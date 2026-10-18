#!/usr/bin/env python3
"""Independent archived-output checks. Does not alter selection or analysis outputs."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib,itertools
import pandas as pd
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[1];O=B/'results'
p=json.loads((B/'protocol/preregistered_protocol.json').read_text())
d=pd.read_csv(R/p['inputs'][0]['path']); key=lambda s:tuple(int(a[1:]) for a in s.split(','));d=d.iloc[sorted(range(len(d)),key=lambda j:key(d.pair.iloc[j]))].reset_index(drop=True)
ids=d.pair.tolist();ix={s:i for i,s in enumerate(ids)};bounds=json.loads(d.normalization_bounds_json[0]);norm={c:(d[c].to_numpy()-bounds[c][0])/(bounds[c][1]-bounds[c][0]) for c in ['A','H','V']};X=np.c_[norm['A'],norm['H'],1-norm['V']]
report={}
report['all_frozen_input_hashes_match']=all(hashlib.sha256((R/a['path']).read_bytes()).hexdigest()==a['sha256'] for a in p['inputs'])
ws=np.load(O/'weight_samples.npz');maxerr=0
for s in ['full','ordered','local']:
 for split in ['train','test','replication']:
  rng=np.random.Generator(np.random.PCG64(p['sampling']['spaces'][s]['seeds'][split]));w=ws[s+'_'+split]
  if s=='local':
   accepted=[]
   while sum(map(len,accepted))<20000:
    a=rng.dirichlet([1.,1.,1.],100000);accepted.append(a[np.max(np.abs(a-np.array(p['sampling']['spaces']['local']['center'])),axis=1)<=.1])
   ref=np.concatenate(accepted)[:20000]
  else:
   ref=rng.dirichlet([1.,1.,1.],20000)
   if s=='ordered':ref=np.sort(ref,axis=1)[:,::-1]
  assert np.array_equal(ref,w),(s,split)
report['all_180000_weights_recreated_exactly']=True
allm=pd.read_csv(O/'all630_metrics_memberships.csv').set_index('pair').loc[ids]
for name,cols in [('AV',['A','V']),('AHV',['A','H','V'])]:
 z=d[cols].to_numpy().copy();z[:,-1]*=-1
 front=np.array([all(not (np.all(t>=row) and np.any(t>row)) for t in z) for row in z])
 assert np.array_equal(front,allm[name+'_front'].to_numpy())
 report[name+'_front_size']=int(front.sum())
st=pd.read_csv(O/'all630_rank_acceptability.csv')
for s in ['full','ordered','local']:
 for split in ['train','test','replication']:
  h=pd.read_csv(O/f'rank_distribution_{s}_{split}.csv.gz').set_index('pair').loc[ids].to_numpy();assert np.all(h.sum(axis=0)==20000) and np.all(h.sum(axis=1)==20000)
  a=st[(st.space==s)&(st.split==split)].set_index('pair').loc[ids]
  assert np.allclose(h[:,0]/20000,a.winner_acceptability,atol=1e-15)
  assert np.allclose(h[:,:10].sum(axis=1)/20000,a.top10_acceptability,atol=1e-15)
  assert np.allclose(h@np.arange(1,631)/20000,a.average_rank,atol=1e-12)
  assert np.array_equal(630-np.argmax(h[:,::-1]>0,axis=1),a.worst_observed_rank)
  rm=np.load(O/f'rank_memberships_{s}_{split}.npz');which=np.linspace(0,19999,61,dtype=int)
  for t in which:
   utilities=X@ws[s+'_'+split][t];order=sorted(range(630),key=lambda j:(-utilities[j],key(ids[j])))
   assert np.array_equal(order[:10],rm['top10_indices'][t])
report['all_rank_histogram_margins_and_statistics_verified']=True
report['independent_python_sort_rank_samples_verified']=549
short=pd.read_csv(O/'shortlists_evidence.csv');ev=pd.read_csv(R/'icores_2027/architect_first_cloud/analysis/decision_evidence_matrix.csv').set_index('building_pair');hb=pd.read_csv(R/'icores_2027/runs/statistics_20261016/comparison_values.csv').set_index('pair_key')
for _,row in short.iterrows():
 assert row.HB_review_status==ev.loc[row.pair,'HB_review_status']
 assert row.design_translation_status==ev.loc[row.pair,'design_translation_status']
 if row.pair in hb.index:assert row.HB_cohort==hb.loc[row.pair,'comparison_set'] and np.isclose(row.hb_A,hb.loc[row.pair,'hb_A'])
 else:assert row.HB_cohort=='MISSING' and np.isnan(row.hb_A) and row.HB_review_status=='2P5D_ONLY'
report['all_shortlist_HB_and_translation_status_joins_verified']=True
# Independently assess first and final greedy choices with all training scenarios; no reselection saved.
t=np.concatenate([ws[s+'_train'] for s in ['full','ordered','local']]);u=t@X.T;best=u.max(axis=1);trace=pd.read_csv(O/'greedy_trace.csv');chosen=[ix[s] for s in trace.pair]
for k in [0,9]:
 current=np.max(u[:,chosen[:k]],axis=1) if k else np.zeros(len(t));objectives=[]
 for j in range(630):
  if j in chosen[:k]:continue
  r=best-np.maximum(current,u[:,j]);objectives.append((float(r.max()),float(r.mean()),key(ids[j]),j))
 winner=min(objectives);assert winner[-1]==chosen[k]
 assert abs(winner[0]-trace.max_train_regret[k])<1e-14
report['greedy_steps_1_and_10_verified_exhaustively']=True
if (O/'continuous_lp_all_candidates.csv.gz').exists():
 lp=pd.read_csv(O/'continuous_lp_all_candidates.csv.gz');assert lp.success.all()
 maxownerr=0.;maxfeas=0.
 for (space,label),g in lp.groupby(['space','set']):
  s=[ix[a] for a in short[short['set']==label].pair];w=g[['wA','wH','wV']].to_numpy();u=w@X.T;su=u[:,s].max(axis=1);own=u[np.arange(len(g)),[ix[a] for a in g.candidate]]-su
  maxownerr=max(maxownerr,float(np.max(np.abs(own-g.raw_objective))));assert np.allclose(own,g.raw_objective,atol=1e-8,rtol=0)
  assert np.allclose(w.sum(axis=1),1,atol=1e-8) and w.min()>=-1e-8
  if space=='ordered':assert np.all(w[:,0]>=w[:,1]-1e-8) and np.all(w[:,1]>=w[:,2]-1e-8)
  if space=='local':assert np.max(np.abs(w-np.array([9,7,3])/19))<=.1+1e-8
  j=int(np.argmax(g.raw_objective.to_numpy()));assert abs(u[j].max()-su[j]-g.raw_objective.iloc[j])<1e-8
 report['all_LP_witness_objectives_and_space_constraints_verified']=len(lp)
 report['maximum_independent_LP_objective_error']=maxownerr
(B/'qa/independent_check_results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
# Verify stored scenario utilities/ranks and summary reductions independently.
sc=pd.read_csv(O/'set_scenario_metrics.csv.gz');summary=pd.read_csv(O/'shortlist_evaluation.csv');paired=pd.read_csv(O/'paired_regret_differences.csv')
for (space,split,label),g in sc.groupby(['space','split','set'],sort=False):
 js=[ix[a] for a in short[short['set']==label].pair];which=np.linspace(0,19999,61,dtype=int);sub=g.set_index('scenario').loc[which];u=ws[space+'_'+split][which]@X.T;best=u.max(axis=1);su=u[:,js].max(axis=1);reg=best-su;order=np.argsort(-u,axis=1,kind='stable');counts=np.isin(order[:,:10],js).sum(axis=1)
 assert np.allclose(sub.regret,reg,atol=1e-14,rtol=0) and np.allclose(sub.best_utility,su,atol=1e-14,rtol=0)
 assert np.array_equal(sub.top10_recovered,counts) and np.array_equal(sub.winner_covered,np.isin(order[:,0],js))
 ss=summary[(summary.space==space)&(summary.split==split)&(summary['set']==label)].iloc[0]
 for col,val in [('regret_mean',g.regret.mean()),('regret_p95',np.quantile(g.regret,.95)),('regret_max',g.regret.max()),('winner_coverage',g.winner_covered.mean()),('top10_recovery',g.top10_recovered.mean()/10)]:assert abs(ss[col]-val)<1e-13,(space,split,label,col)
for (space,split),g in sc.groupby(['space','split']):
 wide=g.pivot(index='scenario',columns='set',values='regret')
 for baseline in ['historical10','AV10','AHV10']:
  diff=wide.robust10-wide[baseline];line=paired[(paired.space==space)&(paired.split==split)&(paired.comparator==baseline)].iloc[0]
  assert abs(line.mean_regret_difference_robust_minus_comparator-diff.mean())<1e-13
  assert abs(line.mc_se-diff.std(ddof=1)/np.sqrt(20000))<1e-13
report['scenario_metrics_independently_verified_samples']=3294
report['all_summary_regret_coverage_and_paired_differences_verified']=True
(B/'qa/independent_check_results.json').write_text(json.dumps(report,indent=2));print('Scenario and summary checks passed.')
cross=pd.read_csv(O/'cross_space_candidate_changes.csv')
lookup=st.set_index(['split','space','pair'])
for _,row in cross.iterrows():
 for metric in ['winner_acceptability','top10_acceptability','average_rank','worst_observed_rank']:
  want=float(lookup.loc[(row.split,row.space_b,row.pair),metric])-float(lookup.loc[(row.split,row.space_a,row.pair),metric])
  assert abs(row[metric+'_delta_b_minus_a']-want)<1e-12,(row.pair,metric)
report['all_cross_space_changes_including_signed_worst_rank_verified']=len(cross)
manifest=json.loads((B/'RUN_MANIFEST.json').read_text())
assert manifest['script_sha256']==hashlib.sha256((B/'analysis/run_analysis.py').read_bytes()).hexdigest()
for f in manifest['output_files']:
 assert hashlib.sha256((B/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
report['final_run_identity']={'manifest_sha256':hashlib.sha256((B/'RUN_MANIFEST.json').read_bytes()).hexdigest(),'analysis_script_sha256':manifest['script_sha256'],'protocol_sha256':manifest['protocol_sha256'],'freeze_commit':manifest['freeze_commit'],'manifest_output_hashes_verified':len(manifest['output_files'])}
(B/'qa/independent_check_results.json').write_text(json.dumps(report,indent=2));print('Cross-space signed deltas and final manifest hashes verified.')
