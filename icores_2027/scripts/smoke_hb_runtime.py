"""Synthetic runtime check, never a real-site experiment."""
from pathlib import Path
import json, os, subprocess, sys, hashlib, datetime, time
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'icores_2027/runs/environment_20261016';OUT.mkdir(parents=True,exist_ok=True)
RAD=Path(os.environ.get('ICORES_RADIANCE_ROOT','/workspace/shared/icores-radiance/radiance-6.0.c1700d56cc-Linux/usr/local/radiance'))
os.environ['PATH']=str(RAD/'bin')+os.pathsep+str(Path(sys.executable).parent)+os.pathsep+os.environ['PATH']
os.environ['RAYPATH']='.:'+str(RAD/'lib')
from honeybee_radiance.config import folders
folders.radiance_path=str(RAD)
import honeybee_radiance.properties.model
from honeybee.model import Model
from honeybee.shade import Shade
from honeybee_radiance.sensorgrid import SensorGrid,Sensor
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.pointvector import Point3D
from lbt_recipes.recipe import Recipe
from lbt_recipes.settings import RecipeSettings
work=Path('/tmp/icores_hb_smoke');work.mkdir(exist_ok=True)
model=Model('anonymous_synthetic_runtime',orphaned_shades=[Shade('roof',Face3D([Point3D(-10,-10,1),Point3D(10,-10,1),Point3D(10,10,1),Point3D(-10,10,1)]))])
model.properties.radiance.add_sensor_grid(SensorGrid('synthetic',[Sensor((0,0,0.1),(0,0,1)),Sensor((50,50,0.1),(0,0,1))]))
model.to_hbjson('model',str(work))
wea=work/'smoke.wea';wea.write_text('place synthetic\nlatitude 24.55\nlongitude -118.03\ntime_zone -120\nsite_elevation 10\nweather_data_file_units 1\n12 21 12.25 1000 0\n')
r=Recipe('direct-sun-hours');r.input_value_by_name('model',str(work/'model.hbjson'));r.input_value_by_name('wea',str(wea));r.input_value_by_name('timestep',2);r.input_value_by_name('cpu-count',1)
start=time.perf_counter();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
try:
 result=r.run(RecipeSettings(folder=str(work/'run'),workers=1,reload_old=False),radiance_check=True,queenbee_path=str(Path(sys.executable).parent/'queenbee'),silent=True)
 res=list(Path(result).rglob('synthetic.res'))
 vals=[p.read_text().strip() for p in res]
 driver=json.loads((Path(result)/'direct_sun_hours/__logs__/status.json').read_text())['status']['status']
 verdict='PASS' if driver=='Succeeded' and any([float(x) for x in v.split()]==[0.0,0.5] for v in vals) else 'FAIL' 
 report={'status':verdict,'driver_status':driver,'expected_values_h':[0,0.5],'runtime_patch':'audit/lbt_recipes_timestamp_fix.patch','measurement_class':'SYNTHETIC_RUNTIME_SMOKE','run_id':'environment_20261016','started_utc':started,'wall_seconds':time.perf_counter()-start,'radiance_version':subprocess.check_output(['rtrace','-version'],text=True,stderr=subprocess.STDOUT).strip(),'result_values':vals,'result_file_count':len(res),'real_site_replay':False,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
except Exception as e:report={'status':'FAIL','measurement_class':'SYNTHETIC_RUNTIME_SMOKE','error':str(e),'real_site_replay':False}
(OUT/'hb_smoke_result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
