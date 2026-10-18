from pathlib import Path
import csv,json,hashlib,math,itertools,statistics
from scipy.stats import spearmanr
ROOT=Path('/workspace/shared/architect_sprint'); OUT=Path('/workspace/shared/architect_independent_audit')
manifest=[]
def read(rel):
 p=ROOT/rel;b=p.read_bytes(); rows=list(csv.DictReader(b.decode('utf-8-sig').splitlines())); manifest.append(dict(path=rel,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),rows=len(rows)));return rows
base='icores_2027/runs/local_ablation_20261016/'
r=read(base+'aggregate_B_m630_r1_run.csv'); num=['A','H','V','N','score','rank']; n=lambda row,k:float(row[k]); pair=lambda s:tuple(map(lambda x:int(x[1:]),s.split(',')))
ids=sorted(set(sum([list(pair(x['pair'])) for x in r],[]))); pairs={pair(x['pair']) for x in r}
checks={'rows':len(r),'unique_pairs':len(pairs),'unique_building_ids':ids,'complete_combination_universe':pairs==set(itertools.combinations(ids,2)),'missing_numeric':sum(x.get(k,'')=='' for x in r for k in num),'nonfinite_numeric':sum(not math.isfinite(n(x,k)) for x in r for k in num)}
bounds={k:(min(n(x,k) for x in r),max(n(x,k) for x in r)) for k in 'AHVN'}
def norm(x,k):
 lo,hi=bounds[k];return (x-lo)/(hi-lo) if hi-lo>=1e-12 else 0.
def score(row,prefix=''):return .45*norm(n(row,prefix+'A'),'A')+.35*norm(n(row,prefix+'H'),'H')+.15*(1-norm(n(row,prefix+'V'),'V'))+.05*(1-norm(n(row,prefix+'N'),'N'))
calc={x['pair']:score(x) for x in r}; order=sorted(r,key=lambda x:(-calc[x['pair']],pair(x['pair'])))
checks['bounds']=bounds;checks['score_max_error']=max(abs(calc[x['pair']]-n(x,'score')) for x in r);checks['recomputed_score_rank_mismatches']=sum(int(x['rank'])!=i for i,x in enumerate(order,1));checks['exact_score_tied_groups']=len({v for v in calc.values() if list(calc.values()).count(v)>1})
front={x['pair'] for x in r if not any(n(y,'A')>=n(x,'A') and n(y,'V')<=n(x,'V') and (n(y,'A')>n(x,'A') or n(y,'V')<n(x,'V')) for y in r)}
checks['pareto_count']=len(front);checks['pareto_flag_mismatches']=sum((x['pair'] in front)!=(x['is_pareto_front']=='True') for x in r);checks['top10_pareto_count']=len(front & {x['pair'] for x in order[:10]})
for name,rows in [('independent_top10.csv',order[:10]),('independent_pareto.csv',[x for x in order if x['pair'] in front])]:
 with (OUT/name).open('w') as f:w=csv.DictWriter(f,fieldnames=['pair']+num+['is_pareto_front']);w.writeheader();w.writerows({k:x[k] for k in w.fieldnames} for x in rows)
comparisons=[]; ref={x['pair']:x for x in r}
for method,repeat in itertools.product('AB',[1,2,3]):
 rel=base+f'aggregate_{method}_m630_r{repeat}_run.csv'; z=read(rel); zz={x['pair']:x for x in z};comparisons.append(dict(file=rel,unique_pairs=len(zz),same_pair_order=[x['pair'] for x in z]==[x['pair'] for x in r],max_abs={k:max(abs(n(ref[p],k)-n(zz[p],k)) for p in ref) for k in num},pareto_mismatches=sum(ref[p]['is_pareto_front']!=zz[p]['is_pareto_front'] for p in ref)))
co=read('icores_2027/runs/statistics_20261016/comparison_values.csv');agreements=[]; cohortsets={}
for name in ['curated23','heldout20']:
 z=[x for x in co if x['comparison_set']==name];cohortsets[name]={x['pair_key'] for x in z}
 for metric in ['A','H','score']:
  a=[n(x,'two_d_'+metric) for x in z];b=[n(x,'hb_'+metric) for x in z];agreements.append(dict(cohort=name,metric=metric,n=len(z),rho=float(spearmanr(a,b).statistic),mae=statistics.mean(abs(x-y) for x,y in zip(a,b)),exact_equal=sum(x==y for x,y in zip(a,b))))
checks['cohort_sizes']={k:len(v) for k,v in cohortsets.items()};checks['cohort_overlap']=sorted(set.intersection(*cohortsets.values()));checks['all_top10_curated']=all(x['pair'] in cohortsets['curated23'] for x in order[:10]);checks['all_pareto_curated']=front <= cohortsets['curated23'];checks['cohort_score_recompute_max_error']={p:max(abs(score(x,p+'_')-n(x,p+'_score')) for x in co) for p in ['two_d','hb']};checks['cohort_shared_V_all']=all(x['two_d_V']==x['hb_V'] for x in co);checks['cohort_N_zero']=all(n(x,p+'_N')==0 for x in co for p in ['two_d','hb'])
runtime=read(base+'ablation_runtime_records.csv'); times=[]
for size in [5,20,60,630]:
 z=[x for x in runtime if int(x['subset_size'])==size and x['warmup']=='False' and x['repeat_id'] in ['1','2','3']]; a=[n(x,'end_to_end_seconds') for x in z if x['method']=='A'];b=[n(x,'end_to_end_seconds') for x in z if x['method']=='B'];times.append(dict(size=size,n_A=len(a),n_B=len(b),median_A=statistics.median(a),median_B=statistics.median(b),ratio_medians=statistics.median(a)/statistics.median(b)))
result=dict(scope='Independent cloud recomputation of archived aggregates only; no new site physics or raw pointwise verification',checks=checks,full630_ab_comparisons=comparisons,cohort_agreement=agreements,runtime_recomputed=times)
(OUT/'independent_results.json').write_text(json.dumps(result,indent=2));(OUT/'input_manifest.json').write_text(json.dumps(manifest,indent=2)); print(json.dumps(result,indent=2))
# Audit against independently archived frozen table and production selection.
u=read('paper_assets/tables/table_03_candidate_universe.csv'); um={x['building_ids']:x for x in u};mapping={'A':'low_area_drop_h3_m2','H':'avg_gain_vs_baseline_h','V':'intervention_volume_m3','N':'new_low_area_h3_m2','score':'score','rank':'rank_2p5d_score'}
checks['frozen_universe_comparison']={k:max(abs(n(x,k)-n(um[x['pair']],v)) for x in r) for k,v in mapping.items()};checks['frozen_reference_hash_matches_embedded']=manifest[-1]['sha256']==r[0]['normalization_source_sha256']
production_order=sorted(r,key=lambda x:(-n(x,'score'),-n(x,'A'),-n(x,'H')));checks['production_rank_mismatches']=sum(int(x['rank'])!=i for i,x in enumerate(production_order,1));checks['production_tie_policy']='score DESC, A DESC, H DESC; no explicit final total-order key; current scores untied'
selected={x['pair'] for x in production_order if n(x,'A')>0};selected=set([x['pair'] for x in production_order if n(x,'A')>0][:10])|front|{'C6,C33','C13,C24','C3,C19','C26,C35'}
checks['selected_23_exact_match']=selected==cohortsets['curated23'];checks['selection_composition']='10 Top10 + 12 nonzero A/V Pareto + 2 historical (C6/C33,C13/C24) + 2 controls (C3/C19,C26/C35) - 3 Top10/Pareto overlap = 23'
checks['cohort_V_max_difference']=max(abs(n(x,'two_d_V')-n(x,'hb_V')) for x in co);checks['cohort_shared_V_with_rounding']=checks['cohort_V_max_difference']<1e-9
cur=read('paper_assets/tables/table_04_curated_hb_verification.csv');curm={x['pair_key']:x for x in cur};checks['curated_hb_values_max_difference']={k:max(abs(n(x,'hb_'+k)-n(curm[x['pair_key']],col)) for x in co if x['comparison_set']=='curated23') for k,col in {'A':'low_area_drop_h3_m2','H':'avg_gain_vs_baseline_h','V':'intervention_volume_m3','N':'new_low_area_h3_m2'}.items()}
trans=read('icores_2027/runs/local_hb_20261016/translation_outcome_comparison.csv');checks['translation_legacy_noncontained']=sum(x['legacy_solid_contained']=='False' for x in trans);checks['translation_contained_corrections']=sum(x['corrected_solid_contained']=='True' and x['corrected_result_reuses_unchanged_legacy']=='False' for x in trans);checks['translation_reused']=[x['case_id'] for x in trans if x['corrected_result_reuses_unchanged_legacy']=='True'];checks['translation_new_low_zero']=all(n(x,'corrected_new_low_area_m2')==0 for x in trans)
checks['top10_design_translation_reviewed']=[x['pair'] for x in order[:10] if x['pair'] in {t['case_id'] for t in trans}];checks['top10_no_translation_evidence']=[x['pair'] for x in order[:10] if x['pair'] not in {t['case_id'] for t in trans}]
# Spot-check source-byte identities of the joined geometry outcomes.
for file,key in [('geometry_recheck.csv','geometry_source_sha256'),('design_translation_recheck.csv','daylight_source_sha256')]:
 rel='icores_2027/runs/local_hb_20261016/'+file;read(rel);checks[file+'_hash_match']=manifest[-1]['sha256']==trans[0][key]
# Reproduce within-cohort TopK under declared natural numeric key and legacy source order.
topk=[]
for name in cohortsets:
 z=[x for x in co if x['comparison_set']==name]
 for metric in ['A','score']:
  for k in [3,5,10]:
   for policy in ['natural_pair','source_order','include_boundary_ties']:
    lists=[]
    for prefix in ['two_d_','hb_']:
     field=prefix+metric;s=sorted(z,key=lambda x:(-n(x,field),pair(x['pair_key']) if policy=='natural_pair' else int(x['source_row_order']))); chosen=s[:k] if policy!='include_boundary_ties' else [x for x in s if n(x,field)>=n(s[k-1],field)];lists.append({x['pair_key'] for x in chosen})
    topk.append(dict(cohort=name,metric=metric,k=k,policy=policy,two_d_size=len(lists[0]),hb_size=len(lists[1]),intersection=len(lists[0]&lists[1]),hb_set_recall=len(lists[0]&lists[1])/len(lists[1])))
result['topk']=topk
(OUT/'independent_results.json').write_text(json.dumps(result,indent=2));(OUT/'input_manifest.json').write_text(json.dumps(manifest,indent=2)); print('\nEXTENDED_CHECKS\n'+json.dumps(checks,indent=2))
frozen_rel='project_archive_2026_10_16/research/experiments/baseline_20260909_clean/independent_validation/VALIDATION_SAMPLE_FROZEN.csv'; frozen=read(frozen_rel)
checks['frozen20_sha256']=manifest[-1]['sha256'];checks['frozen20_hash_preserved']=manifest[-1]['sha256']=='ad4abb9b89a263edaecc2cb3553f7832ce0ccb460521ba218e0083e05bcb46b2';checks['frozen20_identity_order_match']=[x['pair_key'] for x in sorted(frozen,key=lambda x:int(x['sample_order']))]==[x['pair_key'] for x in sorted([x for x in co if x['comparison_set']=='heldout20'],key=lambda x:int(x['source_row_order']))]
checks['frozen20_strata']={s:sum(x['stratum']==s for x in frozen) for s in sorted({x['stratum'] for x in frozen})}
blobs=json.loads(Path('/workspace/shared/architect_materialization.json').read_text());blobcheck=[]
for x in blobs:
 p=ROOT/x['path']
 if p.exists():
  b=p.read_bytes(); actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();blobcheck.append(dict(path=x['path'],expected=x['sha'],actual=actual,match=actual==x['sha']))
checks['materialized_blob_count']=len(blobcheck);checks['materialized_blob_mismatches']=[x['path'] for x in blobcheck if not x['match']]
(OUT/'blob_verification.json').write_text(json.dumps(blobcheck,indent=2));(OUT/'independent_results.json').write_text(json.dumps(result,indent=2));(OUT/'input_manifest.json').write_text(json.dumps(manifest,indent=2)); print('\nFROZEN20_AND_BYTES\n'+json.dumps({k:v for k,v in checks.items() if k.startswith(('frozen20','materialized'))},indent=2))
