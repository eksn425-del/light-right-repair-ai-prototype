"""Delivery integrity checks, not acceptance of blocked scientific conclusions."""
from pathlib import Path
import csv,json,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]/'icores_2027'
PROVENANCE={'run_id','config_hash','code_commit','input_hash','measurement_class'}

def test_all_new_csvs_have_provenance():
 for path in ROOT.rglob('*.csv'):
  with path.open(encoding='utf-8-sig') as f: fields=csv.DictReader(f).fieldnames
  assert fields and PROVENANCE.issubset(fields),str(path)

def test_historical_timings_not_measured_in_new_run():
 rows=list(csv.DictReader((ROOT/'paper_support/PAPER_NUMBERS_ICORES.csv').open()))
 for r in rows:
  if r['metric'].startswith('historical_'):
   assert r['status'].startswith('REUSED_FROZEN')
   assert r['run_id']=='baseline_20260909_clean'
 r=next(r for r in rows if r['metric']=='real_matched_ablation_speedup')
 if r['value']:
  measured=ROOT/'runs/local_ablation_20261016/ablation_summary.csv'
  full=next(x for x in csv.DictReader(measured.open()) if x['subset_size']=='630')
  assert full['completed_matched_repetitions']=='3' and full['all_equal']=='True'
  assert float(r['value'])==float(full['measured_speedup'])
  assert r['measurement_class']=='MEASURED_REAL_SITE'
 else:
  assert r['status']=='BLOCKED'

def test_frozen_aggregate_figure_is_genuine_vector():
 p=ROOT/'paper_support/figures/same_metric_area_agreement.svg'
 tree=ET.parse(p)
 assert not any(e.tag.endswith('image') for e in tree.iter())
 assert any(e.tag.endswith('path') for e in tree.iter())
 manifest=json.loads((ROOT/'paper_support/FIGURE_MANIFEST.json').read_text())
 for filename,digest in manifest['files'].items():
  assert hashlib.sha256((p.parent/filename).read_bytes()).hexdigest()==digest

def test_actual_runtime_smoke_not_real_scene_claim():
 d=json.loads((ROOT/'runs/environment_20261016/hb_smoke_result.json').read_text())
 assert d['status']=='PASS' and d['driver_status']=='Succeeded'
 assert d['real_site_replay'] is False
 assert d['measurement_class']=='SYNTHETIC_RUNTIME_SMOKE'
 assert [float(v) for v in d['result_values'][0].split()]==[0.0,0.5]

def test_readiness_requires_real_gates_and_author_gates_remain_false():
 s=json.loads((ROOT/'STATUS.json').read_text())
 if s['evidence_ready_for_web_review']:
  gate=json.loads((ROOT/'runs/local_quality_20261016/experiment_gate_report.json').read_text())
  assert gate['all_experiment_gates_passed'] and all(gate['checks'].values())
  assert all(s['tasks'][key]=='PASS' for key in ['G0','G1','G2','G3','G4','G5','G6'])
  assert s['EVIDENCE_READY_FOR_WEB_REVIEW'] is True
 assert s['author_approved'] is False and s['submitted'] is False
 assert s['manuscript_draft_ready'] is False

def test_restricted_payloads_not_in_deliverables():
 forbidden={'.obj','.skp','.cad','.dxf','.wea','.res','.ill','.hbjson','.epw'}
 assert not [str(p) for p in ROOT.rglob('*') if p.suffix.lower() in forbidden]
