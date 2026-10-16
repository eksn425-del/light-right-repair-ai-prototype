"""Locate and verify author-local historical inputs; publish hashes, never coordinates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as metadata
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pvlib

from matched_ablation import load_real_inputs, sha256_file

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--historical-run', type=Path, required=True)
    parser.add_argument('--private-dir', type=Path, required=True)
    parser.add_argument('--public-dir', type=Path, required=True)
    args = parser.parse_args()
    old = args.historical_run.resolve()
    private = args.private_dir.resolve()
    public = args.public_dir.resolve()
    if private == ROOT or ROOT in private.parents:
        raise ValueError('Private inputs must remain outside the Git checkout')
    private.mkdir(parents=True, exist_ok=True)
    public.mkdir(parents=True, exist_ok=True)
    protocol = json.loads((ROOT/'icores_2027/configs/ICORES_PROTOCOL.json').read_text())
    source_solar = old/'results_csv/100_统一太阳时刻表.csv'
    saved = pd.read_csv(source_solar)
    times = pd.DatetimeIndex(pd.to_datetime(saved.time))
    fresh = pvlib.solarposition.get_solarposition(times, protocol['analysis']['latitude'], protocol['analysis']['longitude'])
    max_alt = float(np.max(np.abs(fresh.apparent_elevation.to_numpy()-saved.altitude_deg.to_numpy())))
    max_az = float(np.max(np.abs(fresh.azimuth.to_numpy()-saved.azimuth_deg.to_numpy())))
    if max(max_alt, max_az) > 1e-8 or not np.allclose(saved.weight_h, .5):
        raise ValueError('Saved pvlib sequence or declared half-hour weights differ')
    norms = np.linalg.norm(saved[['vx','vy','vz']].to_numpy(float), axis=1)
    if not np.allclose(norms, 1, atol=1e-12):
        raise ValueError('Historical vectors are not normalized')
    az = np.radians(saved.azimuth_deg.to_numpy())
    converted = pd.DataFrame({'time':saved.time, 'apparent_elevation_deg':saved.altitude_deg,
                              'azimuth_deg':saved.azimuth_deg, 'dx':np.sin(az), 'dy':np.cos(az),
                              'tan_altitude':np.tan(np.radians(saved.altitude_deg))})
    solar_path = private/'historical_pvlib_solar_schema.csv'
    converted.to_csv(solar_path, index=False)
    paths = {'building_csv':old/'canonical_site_v2/canonical_buildings.csv',
             'geometry_geojson':old/'canonical_site_v2/canonical_site_v2.geojson',
             'sensors_csv':old/'results_csv/100_HB_Radiance传感点.csv', 'solar_csv':solar_path}
    manifest = {'measurement_class':'REAL_SITE','synthetic':False,'site':protocol['site'],
                'source_run':'baseline_20260909_clean','units':'m','north_deg':0,
                'coordinate_frame':'canonical DXF/CSV local metric XY, positive Z up; frozen north=0',
                'private_runtime_authorized':True,'sensor_order_preserved':True,
                'solar_mode':'historical_verified','solar_verified':True,
                'solar_verification_scope':'saved 2.5D pvlib sequence; HB effective vectors audited separately, not asserted identical',
                'inputs':{key:{'path':str(path),'sha256':sha256_file(path)} for key,path in paths.items()}}
    manifest_path = private/'private_manifest.json'
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    buildings, geoms, sensors, solar, input_hash = load_real_inputs(manifest_path, protocol)
    from honeybee_radiance.config import folders
    binaries = {}
    for name in ['rtrace','rcontrib','oconv','gendaymtx']:
        path = Path(folders.radbin_path)/(name+'.exe' if os.name=='nt' else name)
        entry = {'present':path.is_file(), 'sha256':sha256_file(path) if path.is_file() else None}
        if path.is_file() and name == 'rtrace':
            done = subprocess.run([str(path),'-version'],capture_output=True,text=True,timeout=15)
            entry['version']=(done.stdout+done.stderr).strip()
        binaries[name]=entry
    package_names=['numpy','pandas','shapely','pvlib','honeybee-core','honeybee-radiance','ladybug-core','lbt-recipes']
    report = {'status':'REAL_INPUTS_VALIDATED','run_id':'local_inputs_20261016',
              'config_hash':sha256_file(ROOT/'icores_2027/configs/ICORES_PROTOCOL.json'),
              'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'input_hash':input_hash,'measurement_class':'MEASURED_LOCAL_INPUT_AUDIT',
              'checked_utc':datetime.now(timezone.utc).isoformat(), 'platform':platform.platform(),
              'python':platform.python_version(),'logical_cpu_count':os.cpu_count(),
              'versions':{name:metadata.version(name) for name in package_names},'radiance':binaries,
              'building_count':len(buildings),'sensor_count':len(sensors),'sample_count':len(solar),
              'source_files':{key:{'sha256':entry['sha256'],'bytes':paths[key].stat().st_size} for key,entry in manifest['inputs'].items()},
              'historical_solar_source_sha256':sha256_file(source_solar),
              'solar_schema_mapping':{'altitude_deg':'apparent_elevation_deg',
                                      'azimuth_deg':'azimuth_deg; dx=sin(azimuth),dy=cos(azimuth)',
                                      'tan_altitude':'tan(altitude_deg)', 'time':'unchanged timezone-aware local timestamps'},
              'pvlib_reconstruction_max_elevation_error_deg':max_alt,'pvlib_reconstruction_max_azimuth_error_deg':max_az,
              'sensor_order_note':'original CSV read without sorting; later matched against every historical HB sensor grid',
              'historical_HB_effective_solar_match':'AUDITED_SEPARATELY_NOT_INFERRED',
              'raw_files_uploaded':False}
    (public/'local_input_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({key:report[key] for key in ['status','input_hash','building_count','sensor_count','sample_count']},indent=2))


if __name__=='__main__':
    main()
