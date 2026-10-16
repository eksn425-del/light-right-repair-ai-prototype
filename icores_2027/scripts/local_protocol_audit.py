"""Verify actual archived weather/recipe/grid semantics without publishing raw data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from ladybug.wea import Wea
from shapely.geometry import Point, shape
from shapely.ops import unary_union

from local_hb_replay import CASES, GRID
from geometry_audit import legacy_layers, safe_prism_shades, sha256, write_csv

ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--historical-run',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    old=args.historical_run;out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    protocol=ROOT/'icores_2027/configs/ICORES_PROTOCOL.json'
    geo=old/'canonical_site_v2/canonical_site_v2.geojson'
    features=json.loads(geo.read_text())['features']
    geoms={f['properties']['building_id']:shape(f['geometry']) for f in features}
    union=unary_union(list(geoms.values()))
    buildings=pd.read_csv(old/'canonical_site_v2/canonical_buildings.csv').set_index('building_id')
    grid_path=old/'results_csv/100_HB_Radiance传感点.csv'
    grid=pd.read_csv(grid_path)
    inside=sum(union.contains(Point(r.x,r.y)) for r in grid.itertuples())
    boundary=sum(union.boundary.distance(Point(r.x,r.y))<=1e-7 for r in grid.itertuples())
    code=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    common={'run_id':'local_protocol_20261016','config_hash':sha256(protocol),'code_commit':code,
            'measurement_class':'RECOMPUTED_HISTORICAL_PROTOCOL_SEMANTICS','script_sha256':sha256(Path(__file__))}
    rows=[]
    for scenario,parent in CASES:
        scene=old/parent/scenario
        recipe_path=scene/'direct_sun_hours/__inputs__.json'
        recipe=json.loads(recipe_path.read_text())
        wea_path=scene/'direct_sun_hours'/recipe['wea']
        wea=Wea.from_file(str(wea_path),timestep=2)
        actual_grid=np.loadtxt(scene/f'direct_sun_hours/model/grid/{GRID}.pts')
        selected=set() if scenario=='baseline' else set(scenario.split('_')[:2])
        expected_faces=0
        for bid,geom in geoms.items():
            layers,_=legacy_layers(geom,float(buildings.loc[bid,'height_m']),
                                   'design_stepback' if bid in selected else 'baseline',bid)
            for layer in layers:
                # A safe closed prism has one additional bottom face compared
                # with the legacy roof/exterior-wall emitter; real holes=0.
                expected_faces+=len(safe_prism_shades(layer.identifier,layer.footprint,layer.z0,layer.z1))-1
        hb=json.loads((scene/'inputs'/f'{scenario}.hbjson').read_text())
        actual_faces=len(hb['orphaned_shades'])
        row={**common,'input_hash':sha256(recipe_path),'scenario':scenario,
             'weather_sha256':sha256(wea_path),'executed_recipe_sha256':sha256(recipe_path),
             'actual_historical_cpu_count':recipe['cpu-count'],'timestep_per_hour':recipe['timestep'],
             'north_deg':recipe['north'],'weather_record_count':len(wea.datetimes),
             'timezone_utc_offset_h':wea.location.time_zone,
             'dni_min_w_m2':float(min(wea.direct_normal_irradiance)),
             'dni_max_w_m2':float(max(wea.direct_normal_irradiance)),
             'dhi_min_w_m2':float(min(wea.diffuse_horizontal_irradiance)),
             'dhi_max_w_m2':float(max(wea.diffuse_horizontal_irradiance)),
             'all_grid_normals_up':bool(np.array_equal(actual_grid[:,3:],np.tile([0,0,1],(len(actual_grid),1)))),
             'expected_roof_wall_count':expected_faces,'actual_roof_wall_count':actual_faces,
             'all_expected_faces_present':expected_faces==actual_faces,
             'weather_kind':'constant_DNI_geometry_carrier_not_measured_weather'}
        rows.append(row)
    write_csv(out/'actual_recipe_weather_summary.csv',rows)
    report={**common,'input_hash':sha256(geo),'created_utc':datetime.now(timezone.utc).isoformat(),
            'sensor_count':len(grid),'sensor_source_sha256':sha256(grid_path),
            'receivers_strictly_inside_canonical_union':inside,'receivers_on_boundary_within_tolerance':boundary,
            'canonical_geometry_source':'DXF component bbox union; overlaps and shared IDs; not exact surveyed footprints',
            'geographic_north_status':'frozen north=0 assumption, not a new surveyed true-north verification',
            'weather_semantics_verified':all(r['dni_min_w_m2']==r['dni_max_w_m2']==1000 and r['dhi_min_w_m2']==r['dhi_max_w_m2']==0 for r in rows),
            'all_recipe_timezones_utc_plus8':all(r['timezone_utc_offset_h']==8 for r in rows),
            'all_sample_counts16':all(r['weather_record_count']==16 for r in rows),
            'all_expected_faces_present':all(r['all_expected_faces_present'] for r in rows),
            'raw_payload_uploaded':False}
    (out/'protocol_semantics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    if inside or boundary or not all(report[k] for k in ['weather_semantics_verified','all_recipe_timezones_utc_plus8','all_sample_counts16','all_expected_faces_present']):
        raise ValueError('Actual historical input semantics differ; audit retained')
    print(json.dumps({'status':'PASS','receiver_inside_count':inside,'weather':'constant DNI, not measured','cases':len(rows)}))


if __name__=='__main__':main()
