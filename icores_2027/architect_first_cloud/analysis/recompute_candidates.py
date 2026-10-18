#!/usr/bin/env python3
"""Recompute archived candidate decisions. Does not run a solar simulator.
Run from any directory: python icores_2027/architect_first_cloud/analysis/recompute_candidates.py
"""
from pathlib import Path
import hashlib, json, itertools, sys, platform, os
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
os.environ.setdefault('MPLCONFIGDIR','/tmp/architect-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
AUDIT=OUT.parent/'audit'
FIG=OUT.parent/'paper'/'figures'
for p in [OUT,AUDIT,FIG]:p.mkdir(parents=True,exist_ok=True)
RUN='cloud_archive_reanalysis_20261018'
SRC='icores_2027/runs/local_ablation_20261016/aggregate_B_m630_r1_run.csv'
FROZEN='paper_assets/tables/table_03_candidate_universe.csv'
COHORT='icores_2027/runs/statistics_20261016/comparison_values.csv'
TRANSLATION='icores_2027/runs/local_hb_20261016/translation_outcome_comparison.csv'
inputs=[]
def read(path):
 p=ROOT/path; inputs.append({'path':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
 return pd.read_csv(p)
d=read(SRC);old=read(FROZEN);co=read(COHORT);tr=read(TRANSLATION)
assert len(d)==630 and d.pair.nunique()==630
ids=sorted(set(','.join(d.pair).split(',')),key=lambda x:int(x[1:]))
assert len(ids)==36 and all(x.startswith('C') and x[1:].isdigit() for x in ids)
assert set(d.pair)=={','.join(x) for x in itertools.combinations(ids,2)}
assert (d.N==0).all()
bounds=json.loads(d.normalization_bounds_json.iloc[0]);assert d.normalization_bounds_json.nunique()==1
for q in ['A','H','V','N']:
 lo,hi=bounds[q];d[q+'_recomputed_norm']=0 if abs(hi-lo)<1e-12 else (d[q]-lo)/(hi-lo)
d['recomputed_score']=.45*d.A_recomputed_norm+.35*d.H_recomputed_norm+.15*(1-d.V_recomputed_norm)+.05*(1-d.N_recomputed_norm)
score_error=float(abs(d.recomputed_score-d.score).max());assert score_error<1e-12
# Historical sort columns preserved. Stable input row order only resolves any remaining
# complete-key tie; no complete-key or exact-score ties occur in this archived dataset.
d=d.sort_values(['recomputed_score','A','H'],ascending=False,kind='stable').reset_index(drop=True)
d['recomputed_rank']=np.arange(1,631);assert (d.recomputed_rank==d['rank']).all()
d['recomputed_pareto']=[not (((d.V<=r.V)&(d.A>=r.A))&((d.V<r.V)|(d.A>r.A))).any() for r in d.itertuples()]
assert (d.recomputed_pareto==d.is_pareto_front).all()
top=d[d.A>0].head(10);pareto=d[d.recomputed_pareto & (d.A>0)]
hist={'C6,C33','C13,C24'};controls={'C3,C19','C26,C35'}
selected=set(top.pair)|set(pareto.pair)|hist|controls
assert len(selected)==23 and len(pareto)==12 and len(set(top.pair)&set(pareto.pair))==3
c23=co[co.comparison_set=='curated23'];c20=co[co.comparison_set!='curated23']
assert set(c23.pair_key)==selected and len(c23)==23 and len(c20)==20 and not (set(c23.pair_key)&set(c20.pair_key))
old=old.set_index('building_ids');tr=tr.set_index('case_id');hb=c23.set_index('pair_key')
checks=[]
for q,oq in [('A','low_area_drop_h3_m2'),('H','avg_gain_vs_baseline_h'),('V','intervention_volume_m3'),('N','new_low_area_h3_m2'),('score','score'),('rank','rank_2p5d_score')]:
 err=float(np.max(abs(d.set_index('pair')[q].sort_index()-old[oq].sort_index())))
 checks.append({'check':'frozen_full630_'+q,'max_absolute_difference':err,'tolerance':1e-10,'pass':err<1e-10,'classification':'CLOUD_RECOMPUTED_FROM_ARCHIVE'})
 assert err<1e-10
for p in sorted((ROOT/'icores_2027/runs/local_ablation_20261016').glob('aggregate_*_m630_r*_run.csv')):
 a=read(str(p.relative_to(ROOT))).set_index('pair').sort_index();b=d.set_index('pair').sort_index()
 for q in ['A','H','V','N','score','rank','is_pareto_front']:assert np.array_equal(a[q],b[q])
 checks.append({'check':'six_run_equivalence_'+p.name,'max_absolute_difference':0,'tolerance':0,'pass':True,'classification':'CLOUD_RECOMPUTED_FROM_ARCHIVE'})
def decision(r):
 o=old.loc[r.pair];t=tr.loc[r.pair] if r.pair in tr.index else None
 status=('CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED' if bool(t.corrected_result_reuses_unchanged_legacy) else 'CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED') if t is not None else 'NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION'
 return {'rank':int(r.recomputed_rank),'building_pair':r.pair,'candidate_id':o.candidate_id,'rule_height_change':str(o.original_heights_m)+' -> '+str(o.modified_heights_m)+' m; pair order','low_sun_area_reduction_m2':r.A,'mean_DSH_gain_h':r.H,'nominal_volume_proxy_m3':r.V,'weighted_score':r.recomputed_score,'Pareto_membership':bool(r.recomputed_pareto),'HB_review_status':'ARCHIVED_RULE_HB_REVIEWED' if r.pair in hb.index else ('ARCHIVED_COVERAGE20_RULE_HB_REVIEWED' if r.pair in set(c20.pair_key) else '2P5D_ONLY'),'HB_rule_low_sun_area_reduction_m2':float(hb.loc[r.pair].hb_A) if r.pair in hb.index else np.nan,'design_translation_status':status,'translated_low_sun_area_reduction_m2':float(t.corrected_low_area_reduction_m2) if t is not None else np.nan,'scientific_caveat':'Rule-level shortlist, not construction-ready; nominal volume is not union demolition quantity; fixed canonical site/grid/time; professional review required','source_file':SRC,'run_id':RUN,'source_run_id':'local_ablation_20261016','classification':'CLOUD_RECOMPUTED_FROM_ARCHIVE'}
allrows=pd.DataFrame([decision(r) for r in d.itertuples()]);allrows.to_csv(OUT/'decision_evidence_matrix.csv',index=False)
allrows[allrows.building_pair.isin(top.pair)].to_csv(OUT/'top10_rule_candidates.csv',index=False)
allrows[allrows.building_pair.isin(pareto.pair)].to_csv(OUT/'pareto_rule_candidates.csv',index=False)
pro=[]
for r in d[d.pair.isin(selected)].itertuples():
 cats=[]
 if r.pair in set(top.pair):cats.append('TOP10')
 if r.pair in set(pareto.pair):cats.append('NONZERO_AV_PARETO')
 if r.pair in hist:cats.append('HISTORICAL_PAIR')
 if r.pair in controls:cats.append('CONTROL_PAIR')
 pro.append({'building_pair':r.pair,'rank':r.recomputed_rank,'selection_reasons':';'.join(cats),'membership_count':len(cats),'HB_candidate_id':hb.loc[r.pair].candidate_id,'source':'research_reproducibility/src/legacy_route_b/route_b_enumerate_2p5d_candidates.py:253-259','classification':'CLOUD_RECOMPUTED_FROM_ARCHIVE'})
pd.DataFrame(pro).to_csv(OUT/'selected_23_provenance.csv',index=False)
stats=[]
for name,g in co.groupby('comparison_set'):
 for metric in ['A','H','score']:
  x,y=g['two_d_'+metric],g['hb_'+metric]
  stats.append({'cohort':name,'n':len(g),'metric':metric,'spearman_rho_average_ties':spearmanr(x,y).statistic,'MAE':abs(x-y).mean(),'max_absolute_error':abs(x-y).max(),'classification':'CLOUD_RECOMPUTED_FROM_ARCHIVE','source':COHORT})
pd.DataFrame(stats).to_csv(OUT/'same_metric_recomputed.csv',index=False)
summary=read('icores_2027/runs/local_ablation_20261016/ablation_summary.csv')
records=read('icores_2027/runs/local_ablation_20261016/ablation_runtime_records.csv')
# Preserve full archived timing table; independent runtime audit accompanies this run.
summary.to_csv(OUT/'historical_runtime_rechecked.csv',index=False)
tr.reset_index().to_csv(OUT/'historical_translation_rechecked.csv',index=False)
pd.DataFrame(checks).to_csv(AUDIT/'RESULT_RECONCILIATION.csv',index=False)
cards=['# 建筑师候选决策卡（2026-10-18云端归档重算）','','这是固定模型下的规则减高候选，不是十个施工设计；实际产权、用途、结构、风貌、成本和许可均未据此核准。全部Top10已有历史规则层HB复核，只有三组有已归档转译核查。','']
for r in allrows.head(10).itertuples():
 cards += [f'## {r.rank}. {r.building_pair.replace(","," / ")}',f'两栋高度按已归档规则由 {r.rule_height_change} 调整，足迹保持不变。2.5D筛选预计低于3小时的低日照面积减少 {r.low_sun_area_reduction_m2:.0f} m²，2031点平均直射时长增加 {r.mean_DSH_gain_h:.6f} 小时；名义减高体积为 {r.nominal_volume_proxy_m3:.2f} m³，它不是实际拆除工程量或报价。',f'历史规则层HB对应改善为 {r.HB_rule_low_sun_area_reduction_m2:.0f} m²。'+(f'已有转译结果核查，转译改善为 {r.translated_low_sun_area_reduction_m2:.0f} m²，状态：'+('原本包含性通过，复用未变结果' if 'REUSED' in r.design_translation_status else '旧几何已修正并历史HB复核')+'。' if pd.notna(r.translated_low_sun_area_reduction_m2) else '没有已归档的该组转译设计核查，需另行建模和验证。')+f' A/V非支配候选：{"是" if r.Pareto_membership else "否"}；仍需建筑师判断功能、权益、结构、风貌与实施可行性。',f'出处：{SRC}；原候选高度：{FROZEN}；HB：{COHORT}；转译：{TRANSLATION}。','']
(OUT/'architect_decision_cards.md').write_text('\n'.join(cards),encoding='utf-8')
(OUT/'selection_policy_frozen.md').write_text('''# Frozen selection policy

Source: research_reproducibility/src/legacy_route_b/route_b_enumerate_2p5d_candidates.py, lines 224–259.
The production preference score is 0.45 nA + 0.35 nH + 0.15 (1-nV) + 0.05 (1-nN), using frozen full630 normalization bounds, with no clipping/refitting. N=0 gives constant +0.05 and no ranking influence.
Production sorts score descending, then A descending, then H descending. No exact score ties occur in this630. This reanalysis uses stable source-row order for any residual complete-key tie; no observed ranking depends on that extension. This is not a newly tuned preference policy.
Top10 filters A>0, then takes the first10. Pareto maximizes A and minimizes nominal V, with one strict improvement required; it is not four-objective Pareto. All12 front members have A>0. Three overlap Top10.
Historical review selection is Top10(10) union nonzero-front(12) union historical pairs C6,C33 and C13,C24(2) union controls C3,C19 and C26,C35(2), giving10+12+2+2-3=23. These controls are candidate pairs, not the no-intervention baseline scenario. The additional frozen20 are disjoint same-site coverage candidates, not random or independent-site samples.
The candidate table joins rule-level HB and translated-design evidence separately. All10 shortlist entries have archived rule HB results, but only3 have archived design-translation checks. Neither establishes construction readiness.
''',encoding='utf-8')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'ps.fonttype':42})
fig,ax=plt.subplots(figsize=(6.3,3.8));ax.scatter(d.V,d.A,s=12,c='#a5b4c4',alpha=.55,label='630 rule candidates')
p=pareto.sort_values('V');ax.plot(p.V,p.A,'o-',c='#087e8b',lw=1,label='12 A/V non-dominated')
ax.scatter(top.V,top.A,s=40,marker='s',facecolor='none',edgecolor='#c14953',label='Top 10 preference shortlist')
for pair in ['C9,C24','C9,C15','C9,C13','C25,C29']:
 r=d[d.pair==pair].iloc[0];ax.annotate(pair.replace(',','/'),(r.V,r.A),xytext=(5,6),textcoords='offset points',fontsize=7)
ax.set(xlabel='Nominal volume-reduction proxy (m³)',ylabel='Low-sun-area reduction A (m²)');ax.grid(alpha=.15);ax.legend(fontsize=7,loc='upper right');fig.tight_layout()
for ext in ['pdf','svg','png']:fig.savefig(FIG/f'candidate_tradeoff.{ext}',dpi=220)
plt.close(fig)
manifest={'run_id':RUN,'source_commit':'5dc805a2962f7f21836b4a4f64a5db3e483958e9','generated_utc':datetime.now(timezone.utc).isoformat(),'classification':'CLOUD_RECOMPUTED_FROM_ARCHIVE','inputs':list({x['path']:x for x in inputs}.values()),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'counts':{'full':630,'eligible_ids':36,'top10':10,'pareto':12,'top10_pareto_overlap':3,'selected23':23,'coverage20':20,'top10_rule_hb_reviewed':10,'top10_translations_checked':3},'score_max_absolute_error':score_error,'exact_score_ties':int(d.score.duplicated().sum()),'new_HB_simulation':'NOT_RUN_MISSING_INPUTS','historical_six_aggregate_byte_identity':len({x['sha256'] for x in inputs if 'aggregate_' in x['path']})==1,'python':sys.version,'platform':platform.platform(),'result_checks':checks}
(OUT/'RECOMPUTATION_CHECKS.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'figure_provenance.json').write_text(json.dumps({'candidate_tradeoff':{'source':SRC,'classification':'CLOUD_RECOMPUTED_FROM_ARCHIVE','run_id':RUN,'script':'analysis/recompute_candidates.py','shows':'630 archived candidate A/V values, frozen top10 and recomputed 12-member front; no site geometry','outputs':{str(p.relative_to(OUT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(FIG.glob('candidate_tradeoff.*'))}}},indent=2),encoding='utf-8')
print(json.dumps(manifest['counts'],indent=2));print('score max error',score_error);print('All candidate/reconciliation assertions PASSED. No physical simulator run.')
