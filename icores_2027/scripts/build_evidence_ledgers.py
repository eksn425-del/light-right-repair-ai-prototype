"""Derive ICORES ledgers and vector charts from newly recomputed frozen aggregates."""
import csv,json,hashlib
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]; I=ROOT/'icores_2027'; OUT=I/'paper_support';OUT.mkdir(exist_ok=True)
s=json.loads((I/'runs/statistics_20261016/summary.json').read_text());prov={k:s[k] for k in ['run_id','config_hash','code_commit','input_hash','measurement_class']}
rows=[]
def add(metric,value,unit,source,status='RECOMPUTED',notes=''):
 rows.append(dict(metric=metric,value=value,unit=unit,source=source,status=status,notes=notes,**prov))
for a in s['statistics']:
 for key in ['spearman_rho','mae','max_absolute_error','exact_equal_count']:
  add(a['comparison_set']+'_'+a['comparison']+'_'+key,a[key],a['unit'] if 'error' in key or key=='mae' else 'dimensionless', 'runs/statistics_20261016/same_metric_agreement.csv',notes='Frozen aggregates reprocessed; not a new Honeybee scene.')
for key in ['size','N_min','N_max','N_base_score_constant']:add('candidate_'+key,s['universe'][key],'count' if key=='size' else 'dimensionless','runs/statistics_20261016/summary.json')
add('weighted_day_duration',s['time_weather']['sum_sample_weights_h'],'h','runs/statistics_20261016/summary.json',notes='16*0.5; actual HB binary correspondence blocked.')
add('historical_2p5d_end_to_end_median',55.39783389999866,'s','research_reproducibility/results_public/runtime_summary_v2.json','REUSED_FROZEN','Different Windows hardware; not this cloud run.')
add('historical_HB_per_scene_median',51.106736,'s','research_reproducibility/results_public/runtime_summary_v2.json','REUSED_FROZEN','53 scenes; mixed initial2 vs later4 workers.')
add('historical_HB_630_serial_equivalent',32197.24368,'s','research_reproducibility/results_public/runtime_summary_v2.json','REUSED_FROZEN_EXTRAPOLATED','Not measured all630HB; never use for new matched speedup.')
add('real_matched_ablation_speedup','','ratio','audit/MISSING_INPUTS.md','BLOCKED','No real-input matched measurement exists.')
for r in rows:
 if r['status'].startswith('REUSED'): r['measurement_class']='REUSED_FROZEN' if 'EXTRAPOLATED' not in r['status'] else 'REUSED_FROZEN_EXTRAPOLATED';r['run_id']='baseline_20260909_clean';r['code_commit']='6b64fe43451e2e0330930a5677cbe3432307282b';r['config_hash']='HISTORICAL_NOT_REHASHED';r['input_hash']='HISTORICAL_NOT_REHASHED'
 if r['status']=='BLOCKED':r['measurement_class']='NOT_RUN';r['input_hash']='MISSING'
pd.DataFrame(rows).to_csv(OUT/'PAPER_NUMBERS_ICORES.csv',index=False)
corrections=[
 ('C01','Curated rho .883399 versus heldout .997668 shows improvement','Use same metric/cohort comparisons; old unlike-metric statistic retained but not compared as model improvement','CORRECTED','G4'),
 ('C02','N penalty effective in this universe','N min=max=0; normalized0; contribution .05 constant; N-only weight change cannot change order','CORRECTED','G4'),
 ('C03','MAE .45m2 means subcell spatial precision','Candidate-aggregate mean:19 exact, one9m2 error; cell area9m2','CORRECTED','G4'),
 ('C04','Composite rho1 validates all four independent criteria or100%accuracy','Shared V, constant N, same-site coverage sample; sample-internal ranking only','CORRECTED','G4'),
 ('C05','20 independently random or population representative samples','Pre-frozen coverage sample held out from curated review; archived timestamps report chronology, hash only verifies bytes','CORRECTED','G4'),
 ('C06','08:15–15:45 is7.5h integration','16 weighted half-hour slots sum8h; midpoint-bin interpretation pending actual recipe/binaries','PARTIALLY_CORRECTED','G4'),
 ('C07','WEA represents measured weather','Constant DNI1000/DHI0 geometry/DSH carrier, not real-weather validation','CORRECTED_CODE_SEMANTICS','G4'),
 ('C08','Four adverse points are genuine design side effects','Keep historical result but withhold causal interpretation until real containment/ray audit; synthetic source counterexamples are separate','UNRESOLVED','G2'),
 ('C09','Legacy removed volume always equals translated actual removal','Target rule volume is not union-integrated actual volume; report separate values after real geometry audit','UNRESOLVED','G2'),
 ('C10','New matched algorithm speedup exists','No real A/B result yet; old cross-solver and cross-machine costs cannot supply it','BLOCKED','G3'),
 ('C11','Top5 recall is invariant or model improved to1','Old source-order .8 versus natural-pair1 is tie-rule sensitivity; tie-inclusive boundary6vs7','CORRECTED','G4'),
 ('C12','Production handles nighttime correctly','Production function counts skipped nighttime blockers as visible; confirmed latent defect, saved16slot solar table all above horizon','CORRECTED_COVERAGE_DEFECT','G4'),
 ('C13','p=0 is exact','Numerical scipy zero is underflow/limiting implementation value, never mathematical probability0','CORRECTED','G4')]
c=[dict(claim_id=id,old_claim=old,corrected_claim=new,status=st,stage=g,**prov) for id,old,new,st,g in corrections]
gpath=I/'runs/geometry_20261016/geometry_manifest.json'
if gpath.exists():
 g=json.loads(gpath.read_text()); gp={k:g[k] for k in prov}
 for x in c:
  if x['stage']=='G2': x.update(gp)
  if x['stage']=='G3': x.update(run_id='geometry_20261016',input_hash='MISSING',measurement_class='NOT_RUN')
 c.append(dict(claim_id='C14',old_claim='Centroid stepback and prism faces are generally safe',corrected_claim='Synthetic production-function counterexamples prove concavity containment failure, lost courtyard boundaries, silent face errors and a height-clamp volume mismatch; real-site occurrence remains unverified',status='CONFIRMED_SYNTHETIC_ONLY',stage='G2',**gp))
pd.DataFrame(c).to_csv(OUT/'CLAIM_CORRECTIONS.csv',index=False)
pd.DataFrame([dict(claim_id=x['claim_id'],claim=x['corrected_claim'],status=x['status'],evidence='paper_support/CLAIM_CORRECTIONS.csv',release_scope='PRIVATE_REVIEW_ONLY',**{k:x[k] for k in prov}) for x in c]).to_csv(OUT/'CLAIMS_LEDGER_ICORES.csv',index=False)
pd.DataFrame([dict(item=x['claim_id'],old=x['old_claim'],new=x['corrected_claim'],reason=x['status'],affected_stage=x['stage'],**{k:x[k] for k in prov}) for x in c]).to_csv(I/'audit/RESULT_DIFF_ICORES.csv',index=False)
f=pd.read_csv(I/'runs/statistics_20261016/comparison_values.csv');figdir=OUT/'figures';figdir.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','pdf.fonttype':42})
fig,ax=plt.subplots(1,2,figsize=(10,4.4))
for a,(name,title) in zip(ax,[('curated23','Curated review (n=23)'),('heldout20','Frozen coverage sample (n=20)')]):
 d=f[f.comparison_set.eq(name)];a.scatter(d.two_d_A,d.hb_A,s=24,alpha=.7);hi=max(d.two_d_A.max(),d.hb_A.max())*1.05;a.plot([0,hi],[0,hi],color='gray',linewidth=1);a.set(xlabel='2.5D low-area reduction (m²)',ylabel='Archived HB low-area reduction (m²)',title=title);a.grid(alpha=.2)
fig.suptitle('Same-metric agreement: recomputed from frozen aggregates',fontsize=11);fig.tight_layout();fig.savefig(figdir/'same_metric_area_agreement.svg');fig.savefig(figdir/'same_metric_area_agreement.pdf');fig.savefig(figdir/'same_metric_area_agreement.png',dpi=160);plt.close(fig)
manifest={'figure':'same_metric_area_agreement','source_table':'runs/statistics_20261016/comparison_values.csv','source_sha256':hashlib.sha256((I/'runs/statistics_20261016/comparison_values.csv').read_bytes()).hexdigest(),'formats':{'svg':'native vector paths and text, no embedded raster','pdf':'vector scatter and lines; text embedded','png':'160dpi raster'},'release_scope':'PRIVATE_REVIEW_ONLY; author approves anonymized release','interpretation':'No new HB simulations; same-site aggregate agreement; does not establish real geometry correctness','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in figdir.glob('same_metric_area_agreement.*')},**prov}
(OUT/'FIGURE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Generated ledgers and vector chart from frozen-aggregate recomputation; readiness unchanged false.')
