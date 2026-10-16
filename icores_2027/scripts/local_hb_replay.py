"""Audit and replay six real historical HB scenes, retaining raw data locally.

Only aggregate tables, exact input hashes and coded adverse-ray explanations are
written to --public-dir. Complete models, sensors, matrices and solver logs stay
under --private-dir, which is required to lie outside the Git checkout.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from shapely.geometry import shape
from shapely.ops import unary_union

from geometry_audit import (Prism, containment_report, contained_stepback_v2,
                            emitted_prism_layers, legacy_layers, polygon_parts,
                            safe_prism_shades, sha256, write_csv)
from honeybee_radiance.config import folders

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT/'icores_2027/configs/ICORES_PROTOCOL.json'
GRID = 'ground_3m_road_open_space'
CASES = [('baseline','hb_radiance_project_batch'),
         ('C9_C24_design_stepback','hb_radiance_project_final_design'),
         ('C9_C15_design_stepback','hb_radiance_project_final_design'),
         ('C9_C13_design_stepback','hb_radiance_project_final_design'),
         ('C13_C24_design_stepback','hb_radiance_project_batch'),
         ('C6_C33_design_stepback','hb_radiance_project_batch')]


def suns(path):
    text = path.read_text()
    matches = re.findall(r'\w+\s+source\s+(sun\d+)\s+0\s+0\s+4\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)', text)
    return [(name,np.array([float(x),float(y),float(z)]),float(diameter)) for name,x,y,z,diameter in matches]


def model_grid(data):
    grids = data['properties']['radiance']['sensor_grids']
    assert len(grids)==1 and grids[0]['identifier']==GRID
    return np.asarray([sensor['pos'] for sensor in grids[0]['sensors']],dtype=float)


def matrices(scene):
    result = scene/'direct_sun_hours/results'
    visibility = np.loadtxt(result/'direct_sun_hours'/f'{GRID}.ill')
    cumulative = np.loadtxt(result/'cumulative'/f'{GRID}.res')
    if visibility.shape!=(2031,16) or cumulative.shape!=(2031,):
        raise ValueError('Historical matrix dimensions differ')
    if not np.isin(visibility,[0,1]).all() or not np.array_equal(visibility.sum(axis=1)*.5,cumulative):
        raise ValueError('Visibility/cumulative integration mismatch')
    return visibility,cumulative


def meta(args, input_hash, category):
    return dict(run_id=args.run_id,config_hash=sha256(PROTOCOL),code_commit=args.code_commit,
                input_hash=input_hash,measurement_class=category,
                script_sha256=sha256(Path(__file__)))


def trace(scene, sensors, directions, indices, destination):
    octree = scene/'direct_sun_hours/resources/scene_with_suns.oct'
    rays = [' '.join(f'{v:.12g}' for v in [*sensors[i],*directions[j]]) for i,j in indices]
    command = [str(Path(folders.radbin_path)/'rtrace.exe'),'-h','-ab','0','-osLp',str(octree)]
    environment = os.environ.copy()
    environment['RAYPATH']='.;'+str(folders.radlib_path)
    done = subprocess.run(command,input='\n'.join(rays)+'\n',capture_output=True,text=True,
                          env=environment,timeout=60)
    destination.write_text(done.stdout+'\nSTDERR\n'+done.stderr,encoding='utf-8')
    if done.returncode:
        raise RuntimeError('Historical rtrace diagnostic failed; inspect private log')
    lines = done.stdout.strip().splitlines()
    if len(lines)!=len(indices):
        raise ValueError('Ray diagnostic output count differs')
    result=[]
    for line in lines:
        parts=line.split()
        if len(parts)<5:
            raise ValueError('Unexpected surface/distance/point output; inspect private log')
        result.append({'surface':parts[0],'distance_m':float(parts[1]),'point':np.array([float(v) for v in parts[2:5]])})
    return result


def inspect(args):
    old,private,public=args.historical_run,args.private_dir,args.public_dir
    original_sensors=pd.read_csv(old/'results_csv/100_HB_Radiance传感点.csv')
    xyz=original_sensors[['x','y','z']].to_numpy(float)
    buildings=pd.read_csv(old/'canonical_site_v2/canonical_buildings.csv').set_index('building_id')
    geo=json.loads((old/'canonical_site_v2/canonical_site_v2.geojson').read_text())
    geoms={f['properties']['building_id']:shape(f['geometry']) for f in geo['features']}
    overlap_rows=[]
    for a,b in itertools.combinations(geoms,2):
        intersection=geoms[a].intersection(geoms[b]).area
        if intersection>1e-7:
            overlap_rows.append(dict(**meta(args,sha256(old/'canonical_site_v2/canonical_site_v2.geojson'),
                'RECOMPUTED_CANONICAL_FOOTPRINT_AUDIT'),building_1=a,building_2=b,
                intersection_area_m2=intersection,
                identical_footprints=bool(geoms[a].equals(geoms[b])),
                geometry_source='frozen canonical DXF component bbox union; not surveyed exact footprints'))
    write_csv(public/'footprint_overlap_audit.csv',overlap_rows)
    baseline=old/'hb_radiance_project_batch/baseline'
    baseline_matrix,baseline_hours=matrices(baseline)
    baseline_suns=suns(baseline/'direct_sun_hours/resources/sunpath.mtx')
    directions=np.array([sun[1] for sun in baseline_suns])
    hour_labels=np.loadtxt(baseline/'direct_sun_hours/resources/sun-up-hours.txt')
    source_solar=pd.read_csv(old/'results_csv/100_统一太阳时刻表.csv')
    expected=np.array([pd.Timestamp(value).dayofyear*24-24+pd.Timestamp(value).hour+pd.Timestamp(value).minute/60 for value in source_solar.time])
    if len(baseline_suns)!=16 or not np.array_equal(hour_labels,expected):
        raise ValueError('Historical sun/time identifier mapping differs')
    # The actual source IDs encode minute-of-year; verify order independently.
    if any(int(name[3:])!=int(round(hoy*60)) for (name,_,_),hoy in zip(baseline_suns,hour_labels)):
        raise ValueError('Solar source identifiers are not in time-column order')
    base_pts=np.loadtxt(baseline/f'direct_sun_hours/model/grid/{GRID}.pts')[:,:3]
    if not np.allclose(base_pts,xyz,rtol=0,atol=1e-7):
        raise ValueError('Baseline actual Radiance points differ from original ordered IDs/XYZ')
    rows=[];ray_rows=[];source_rows=[];prepared=[]
    solar_rows=[]
    for j,((name,vector,diameter),hoy) in enumerate(zip(baseline_suns,hour_labels)):
        unit=vector/np.linalg.norm(vector)
        altitude=math.degrees(math.asin(unit[2])); azimuth=math.degrees(math.atan2(unit[0],unit[1]))%360
        solar_rows.append(dict(**meta(args,sha256(baseline/'direct_sun_hours/resources/sunpath.mtx'),'RECOMPUTED_HISTORICAL_SOLAR_MAPPING'),
            sample_index=j,time_local=source_solar.time.iloc[j],hour_of_year=float(hoy),source_id=name,
            hb_elevation_deg=altitude,hb_azimuth_deg=azimuth,pvlib_elevation_deg=float(source_solar.altitude_deg.iloc[j]),
            pvlib_azimuth_deg=float(source_solar.azimuth_deg.iloc[j]),elevation_difference_deg=altitude-source_solar.altitude_deg.iloc[j],
            azimuth_difference_deg=azimuth-source_solar.azimuth_deg.iloc[j],sun_diameter_deg=diameter,
            duration_weight_h=.5,measurement_note='Actual historical solver sunpath, not regenerated solar'))
    for scenario,parent in CASES:
        scene=old/parent/scenario
        model_path=scene/'inputs'/f'{scenario}.hbjson'
        recipe_path=scene/'inputs'/f'{scenario}_inputs.json'
        data=json.loads(model_path.read_text())
        recipe=json.loads(recipe_path.read_text())
        wea=Path(recipe['wea'])
        if not wea.is_file():
            wea=next((scene/'inputs').glob('*.wea'))
        matrix,hours=matrices(scene)
        pts=np.loadtxt(scene/f'direct_sun_hours/model/grid/{GRID}.pts')[:,:3]
        positions=model_grid(data)
        sensor_error=max(float(np.max(np.abs(pts-xyz))),float(np.max(np.abs(positions-xyz))))
        if sensor_error>1e-7:
            raise ValueError('HB scene sensor order/XYZ differs from canonical identity table')
        sunpath=scene/'direct_sun_hours/resources/sunpath.mtx'
        sun_equal=sha256(sunpath)==sha256(baseline/'direct_sun_hours/resources/sunpath.mtx')
        times_equal=np.array_equal(np.loadtxt(scene/'direct_sun_hours/resources/sun-up-hours.txt'),hour_labels)
        if not sun_equal or not times_equal:
            raise ValueError('Shared historical HB vectors or sample columns differ')
        pair=[] if scenario=='baseline' else scenario.split('_')[:2]
        selected=set(pair)
        # Exact original Shade dictionaries are compared with current production
        # regeneration, excluding irrelevant model/display metadata.
        from geometry_audit import load_legacy_functions
        ns=load_legacy_functions(['building_shades','prism_shades','face','clean_id','reduced_height'])
        regenerated,_=ns['building_shades'](buildings.reset_index(),geoms,{'pair':','.join(pair),'scenario':scenario,'model_type':'design_stepback' if pair else 'baseline'})
        recorded={s['identifier']:s['geometry'] for s in data['orphaned_shades']}
        # JSON converts Honeybee tuples into lists; normalize representation,
        # without rounding coordinates or weakening the equality requirement.
        rebuilt=json.loads(json.dumps({s.identifier:s.to_dict()['geometry'] for s in regenerated}))
        if recorded!=rebuilt:
            raise ValueError('Actual historical HB faces do not match canonical production regeneration')
        adverse=np.argwhere((baseline_matrix==1)&(matrix==0))
        net_worsened=np.where(hours<baseline_hours)[0]
        base_low=baseline_hours<3; now_low=hours<3
        row=dict(**meta(args,sha256(model_path),'RECOMPUTED_HISTORICAL_REAL_OUTPUT'),scenario=scenario,
                 sensor_id_and_xyz_match=True,sensor_max_abs_error_m=sensor_error,
                 temporal_columns_match=True,sun_vectors_match_baseline=True,regenerated_faces_match=True,
                 model_face_count=len(recorded),model_holes_total=sum(len(p.interiors) for g in geoms.values() for p in polygon_parts(g)),
                 sensor_count=2031,sample_count=16,max_hours=8.,mean_hours=float(hours.mean()),
                 low_area_h3_m2=float(now_low.sum()*9),low_area_drop_h3_m2=float((base_low.sum()-now_low.sum())*9),
                 new_low_area_h3_m2=float(((~base_low)&now_low).sum()*9),
                 mean_gain_h=float((hours-baseline_hours).mean()),worsened_point_count=len(net_worsened),
                 adverse_ray_event_count=len(adverse),replay_status='HISTORICAL_INPUTS_MAPPED_NEW_RUN_PENDING')
        rows.append(row)
        for label,path in [('model',model_path),('recipe',recipe_path),('wea',wea),('sunpath',sunpath),
                           ('visibility',scene/f'direct_sun_hours/results/direct_sun_hours/{GRID}.ill'),
                           ('cumulative',scene/f'direct_sun_hours/results/cumulative/{GRID}.res'),
                           ('actual_grid',scene/f'direct_sun_hours/model/grid/{GRID}.pts')]:
            source_rows.append(dict(**meta(args,sha256(path),'MEASURED_LOCAL_FILE_IDENTITY'),scenario=scenario,
                                    artifact_role=label,sha256=sha256(path),bytes=path.stat().st_size,raw_uploaded=False))
        if len(adverse):
            base_hits=trace(baseline,xyz,directions,adverse,private/f'{scenario}_baseline_ray_trace.txt')
            hits=trace(scene,xyz,directions,adverse,private/f'{scenario}_modified_ray_trace.txt')
            for (i,j),basehit,hit in zip(adverse,base_hits,hits):
                bid=hit['surface'].split('_')[0]
                x,y,z=hit['point']
                outside=not geoms[bid].buffer(1e-7).covers(__import__('shapely').geometry.Point(x,y)) if bid in geoms else None
                base_is_sun=basehit['surface'].startswith('sun')
                cause='LEGACY_ADDED_OUTSIDE_GEOMETRY_CONFIRMED' if base_is_sun and outside else 'UNRESOLVED'
                ray_rows.append(dict(**meta(args,sha256(model_path),'MEASURED_HISTORICAL_RTRACE'),scenario=scenario,
                    sensor_id=original_sensors.grid_id.iloc[i],sample_index=int(j),time_local=source_solar.time.iloc[j],
                    baseline_surface=basehit['surface'],modified_surface=hit['surface'],blocking_building=bid,
                    intersection_z_m=float(z),intersection_outside_original_footprint=outside,
                    baseline_hit_sun=base_is_sun,cause=cause,visibility_before=1,visibility_after=0,
                    coordinate_data_uploaded=False))
        replay_folder=private/'hb_replay'/scenario
        inputs=replay_folder/'inputs'; inputs.mkdir(parents=True,exist_ok=True)
        output_model=inputs/f'{scenario}.hbjson';shutil.copy2(model_path,output_model)
        output_wea=inputs/'historical.wea';shutil.copy2(wea,output_wea)
        output_recipe={**recipe,'model':str(output_model),'wea':str(output_wea),'cpu-count':1}
        recipe_file=inputs/'recipe.json';recipe_file.write_text(json.dumps(output_recipe),encoding='utf-8')
        prepared.append({'scenario':scenario,'model_type':'legacy_replay','recipe':str(recipe_file),
                         'folder':str(replay_folder),'source_scene':str(scene)})
        if pair:
            changed=False;safe_faces=[]
            for bid in pair:
                layers=contained_stepback_v2(geoms[bid],float(buildings.loc[bid,'height_m']),bid)
                original_layers=legacy_layers(geoms[bid],float(buildings.loc[bid,'height_m']),building_id=bid)[0]
                containment=containment_report(original_layers,layers)
                changed=changed or containment['actual_removed_volume_m3']>1e-7
                for layer in layers:
                    safe_faces.extend(safe_prism_shades(layer.identifier,layer.footprint,layer.z0,layer.z1))
            if changed:
                corrected=json.loads(json.dumps(data))
                corrected['identifier']=scenario+'_contained_v2'
                retained=[s for s in data['orphaned_shades'] if not any(s['identifier'].startswith(bid+'_p') for bid in pair)]
                corrected['orphaned_shades']=retained+[s.to_dict() for s in safe_faces]
                corrected_name=scenario.replace('design_stepback','contained_stepback_v2')
                folder=private/'hb_replay'/corrected_name;inp=folder/'inputs';inp.mkdir(parents=True,exist_ok=True)
                model_file=inp/'model.hbjson';model_file.write_text(json.dumps(corrected),encoding='utf-8')
                w=inp/'historical.wea';shutil.copy2(wea,w)
                rp={**recipe,'model':str(model_file),'wea':str(w),'cpu-count':1}
                recipe_file=inp/'recipe.json';recipe_file.write_text(json.dumps(rp),encoding='utf-8')
                prepared.append({'scenario':corrected_name,'model_type':'contained_v2','recipe':str(recipe_file),
                                 'folder':str(folder),'source_scene':str(scene)})
    write_csv(public/'historical_scene_mapping.csv',rows)
    write_csv(public/'historical_input_hashes.csv',source_rows)
    write_csv(public/'historical_solar_mapping.csv',solar_rows)
    write_csv(public/'adverse_ray_explanation.csv',ray_rows)
    (private/'hb_execution_plan.json').write_text(json.dumps(prepared,indent=2),encoding='utf-8')
    print(json.dumps({'status':'HISTORICAL_REAL_INSPECTED','scenes':len(rows),'adverse_events':len(ray_rows),
                      'explained_events':sum(r['cause']!='UNRESOLVED' for r in ray_rows),
                      'new_hb_scenes_prepared':len(prepared),'raw_files_uploaded':False}))


def run(args):
    plan=json.loads((args.private_dir/'hb_execution_plan.json').read_text())
    records=[];results=[];baseline_hours=None
    for item in plan:
        folder=Path(item['folder']);log=folder/'solver.log'
        executable=shutil.which('lbt-recipes')
        if executable is None:
            raise RuntimeError('lbt-recipes executable is unavailable')
        command=[executable,'run','direct-sun-hours',item['recipe'],'-p',str(folder),'-w','1','-d',str(folder/'debug')]
        started=datetime.now(timezone.utc).isoformat();timer=time.perf_counter()
        with log.open('w',encoding='utf-8') as handle:
            done=subprocess.run(command,stdout=handle,stderr=subprocess.STDOUT,timeout=1800)
        elapsed=time.perf_counter()-timer
        record=dict(**meta(args,sha256(Path(item['recipe'])),'MEASURED_LOCAL_HB_REPLAY'),scenario=item['scenario'],
                    model_type=item['model_type'],started_utc=started,ended_utc=datetime.now(timezone.utc).isoformat(),
                    wall_seconds=elapsed,workers=1,exit_code=done.returncode,status='PASS' if not done.returncode else 'FAIL')
        records.append(record);write_csv(args.public_dir/'hb_runtime_records.csv',records)
        if done.returncode:
            print(json.dumps({'status':'FAIL','scenario':item['scenario'],'private_log_retained':True}),flush=True)
            return 2
        matrix,hours=matrices(folder)
        if item['scenario']=='baseline':
            baseline_hours=hours
        if baseline_hours is None:
            raise ValueError('Baseline must be measured first')
        old_matrix,old_hours=matrices(Path(item['source_scene']))
        old_suns=suns(Path(item['source_scene'])/'direct_sun_hours/resources/sunpath.mtx')
        new_suns=suns(folder/'direct_sun_hours/resources/sunpath.mtx')
        actual_pts=np.loadtxt(folder/f'direct_sun_hours/model/grid/{GRID}.pts')
        source_pts=np.loadtxt(Path(item['source_scene'])/f'direct_sun_hours/model/grid/{GRID}.pts')
        sensor_match=bool(np.array_equal(actual_pts,source_pts))
        sun_match=bool(len(new_suns)==len(old_suns) and all(
            a[0]==b[0] and np.array_equal(a[1],b[1]) and a[2]==b[2]
            for a,b in zip(old_suns,new_suns)))
        hours_match=bool(np.array_equal(
            np.loadtxt(folder/'direct_sun_hours/resources/sun-up-hours.txt'),
            np.loadtxt(Path(item['source_scene'])/'direct_sun_hours/resources/sun-up-hours.txt')))
        if not(sensor_match and sun_match and hours_match):
            raise ValueError('Controlled HB replay changed sensor, solar or time inputs')
        old_new_equal=bool(np.array_equal(matrix,old_matrix))
        containment_pass=(not np.any(matrix<baseline_matrix)) if item['model_type']=='contained_v2' else None
        if item['scenario']=='baseline':
            baseline_matrix=matrix
        results.append(dict(**meta(args,sha256(Path(item['recipe'])),'MEASURED_LOCAL_HB_REPLAY'),scenario=item['scenario'],
            model_type=item['model_type'],sensor_count=len(hours),sample_count=matrix.shape[1],
            mean_hours=float(hours.mean()),mean_gain_h=float((hours-baseline_hours).mean()),
            low_area_h3_m2=float((hours<3).sum()*9),low_area_drop_h3_m2=float(((baseline_hours<3).sum()-(hours<3).sum())*9),
            new_low_area_h3_m2=float(((baseline_hours>=3)&(hours<3)).sum()*9),
            worsened_point_count=int((hours<baseline_hours).sum()),
            max_abs_change_from_historical_hours=float(np.max(np.abs(hours-old_hours))),
            historical_matrix_exact_match=old_new_equal,
            sensor_and_direction_exact_match=sensor_match,solar_sources_exact_match=sun_match,
            time_columns_exact_match=hours_match,
            contained_visibility_monotonic=containment_pass,
            status='MEASURED'))
        write_csv(args.public_dir/'design_translation_recheck.csv',results)
        print(json.dumps({'scenario':item['scenario'],'status':'PASS','seconds':round(elapsed,2)}),flush=True)
        if (item['model_type']=='legacy_replay' and not old_new_equal) or containment_pass is False:
            raise ValueError('Historical reproducibility or contained visibility invariant failed; evidence retained')
    return 0


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--historical-run',type=Path,required=True)
    parser.add_argument('--private-dir',type=Path,required=True)
    parser.add_argument('--public-dir',type=Path,required=True)
    parser.add_argument('--phase',choices=['inspect','run'],required=True)
    parser.add_argument('--run-id',default='local_hb_20261016')
    parser.add_argument('--code-commit',required=True)
    args=parser.parse_args()
    args.private_dir=args.private_dir.resolve();args.public_dir=args.public_dir.resolve()
    if args.private_dir==ROOT or ROOT in args.private_dir.parents:
        raise ValueError('Private HB directory cannot be inside the checkout')
    args.private_dir.mkdir(parents=True,exist_ok=True);args.public_dir.mkdir(parents=True,exist_ok=True)
    return inspect(args) if args.phase=='inspect' else run(args)


if __name__=='__main__':
    raise SystemExit(main())
