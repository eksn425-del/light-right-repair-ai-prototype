import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np,pandas as pd,json,hashlib,itertools
B=Path(__file__).resolve().parents[1];R=B.parents[1];O=B/'results'
P=json.loads((B/'protocol/preregistered_protocol.json').read_text());M=json.loads((B/'RUN_MANIFEST.json').read_text());checks={}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for a in P['inputs']:assert digest(R/a['path'])==a['sha256']
for a in M['outputs']:assert digest(B/a['path'])==a['sha256']
assert digest(B/'analysis/run_analysis.py')==M['script_sha256']
checks['input_hashes']=len(P['inputs']);checks['output_hashes']=len(M['outputs'])
d=pd.read_csv(R/P['inputs'][0]['path']);k=lambda p:tuple(int(s[1:]) for s in p.split(','));d=d.iloc[sorted(range(len(d)),key=lambda j:k(d.pair.iloc[j]))].reset_index(drop=True);ids=d.pair.tolist();ix={p:j for j,p in enumerate(ids)};bo=json.loads(d.normalization_bounds_json.iloc[0]);X=np.array([[(r.A-bo['A'][0])/(bo['A'][1]-bo['A'][0]),(r.H-bo['H'][0])/(bo['H'][1]-bo['H'][0]),1-(r.V-bo['V'][0])/(bo['V'][1]-bo['V'][0])] for r in d.itertuples()]);assert len(d)==630 and (d.N==0).all()
short=pd.read_csv(O/'shortlists_evidence.csv');summary=pd.read_csv(O/'shortlist_evaluation.csv');acc=pd.read_csv(O/'candidate_acceptability.csv');prior=pd.read_csv(R/'icores_2027/preference_robust/results/shortlists_evidence.csv');orig={s:[ix[p] for p in g.pair] for s,g in prior.groupby('set')}
ws={}
for space,spec in P['sampling']['spaces'].items():
 for split,seed in spec['seeds'].items():
  rng=np.random.default_rng(seed)
  if space=='ordered': expected=np.sort(rng.dirichlet([1.,1.,1.],20000),axis=1)[:,::-1]
  else:
   parts=[];nn=0
   while nn<20000:
    w=rng.dirichlet([1.,1.,1.],100000);w=w[w[:,2]<=({'solar70':.3,'solar80':.2}[space])];parts.append(w);nn+=len(w)
   expected=np.concatenate(parts)[:20000]
  actual=np.load(O/'weights'/f'{space}_{split}.npz')['weights'];assert np.array_equal(expected,actual);ws[space,split]=actual
checks['weights_recreated']=180000
scenarios=0;selects=0;blockschecked=0
for c in P['contexts']:
 name=c['name'];e=np.arange(630) if c['A_min'] is None else np.where(d.A.to_numpy()>=c['A_min'])[0];ss=short[short.context==name];methods={s:np.array([ix[p] for p in g.pair]) for s,g in ss.groupby('set')}
 if len(e)<10:assert not methods;continue
 for s in methods.values():assert len(set(s))==10 and set(s)<=set(e)
 # Independently construct fair comparator IDs.
 rankorder=sorted(e,key=lambda j:d['rank'].iloc[j])
 if c['A_min'] is None:
  for label in ['historical10','robust10','AV10','AHV10']:assert np.array_equal(methods[label],orig[label])
 else:
  assert list(methods['historical10'])==rankorder[:10]
  retained=[j for j in orig['robust10'] if j in e];assert list(methods['robust10'])==(retained+[j for j in rankorder if j not in retained])[:10]
  for lab,cols in [('AV10',['A','V']),('AHV10',['A','H','V'])]:
   obj=d[cols].to_numpy().copy();obj[:,-1]*=-1
   front=[j for j in e if not any(np.all(obj[l]>=obj[j]) and np.any(obj[l]>obj[j]) for l in e)]
   assert list(methods[lab])==([j for j in rankorder if j in front]+[j for j in rankorder if j not in front])[:10]
 for split in ['train','test','replication']:
  w=ws[c['space'],split];u=w@X[e].T;ordering=np.argsort(-u,axis=1,kind='stable');top=e[ordering[:,:10]];winner=e[ordering[:,0]];ranks=np.argsort(ordering,axis=1)+1
  stored=np.load(O/'rank_memberships'/f'{name}_{split}.npz');assert np.array_equal(top,stored['top10_indices']);assert np.array_equal(winner,stored['winner_indices'])
  # Python scalar ranking avoids relying only on same vectorized sorting code.
  for z in [0,1,17,103,999,19999]:
   rank=sorted(e,key=lambda j:(-sum(w[z,q]*X[j,q] for q in range(3)),j));assert list(top[z])==rank[:10]
  aa=acc[(acc.context==name)&(acc.split==split)].set_index('pair').loc[[ids[j] for j in e]]
  ct=np.bincount(top.ravel(),minlength=630);wc=np.bincount(winner,minlength=630)
  assert np.array_equal(aa.top10_count,ct[e]);assert np.array_equal(aa.winner_count,wc[e]);assert np.allclose(aa.mean_rank,ranks.mean(axis=0));assert np.array_equal(aa.worst_observed_rank,ranks.max(axis=0))
  if split=='train':
   def expected_selection(positions,protect):
    counts=np.bincount(top[positions].ravel(),minlength=630);wins=np.bincount(winner[positions],minlength=630);mr=ranks[positions].mean(axis=0);pos={j:t for t,j in enumerate(e)};req=set(winner[positions]) if protect else set()
    if len(req)>10:return None
    ordered=sorted(e,key=lambda j:(-counts[j],-wins[j],mr[pos[j]],j));return sorted(req)+[j for j in ordered if j not in req][:10-len(req)]
   stab=pd.read_csv(O/'selection_stability.csv')
   for label,protect in [('coverage10',False),('protected_coverage10',True)]:
    exp=expected_selection(np.arange(20000),protect)
    if exp is None:assert label not in methods
    else:assert list(methods[label])==exp
    selects+=1
    for block in range(10):
     ex=expected_selection(np.arange(block*2000,(block+1)*2000),protect);row=stab[(stab.context==name)&(stab.method==label)&(stab.comparison=='block_to_full')&(stab.block_a==block)].iloc[0]
     if ex is not None:assert row.pairs==';'.join(ids[j] for j in ex)
     blockschecked+=1
  for label,s in methods.items():
   f=pd.read_csv(O/'scenario_metrics'/f'{name}_{split}_{label}.csv.gz');su=(w@X[s].T).max(axis=1);reg=u.max(axis=1)-su;rec=np.isin(top,s).sum(axis=1)/10
   assert np.allclose(reg,f.regret,atol=1e-14);assert np.allclose(rec,f.top10_recovery);assert np.array_equal(np.isin(winner,s),f.winner_covered)
   assert np.allclose((w@X.T).max(axis=1)-su,f.full_universe_regret,atol=1e-14)
   row=summary[(summary.context==name)&(summary.split==split)&(summary['set']==label)].iloc[0]
   for key,val in [('regret_mean',reg.mean()),('regret_p95',np.quantile(reg,.95)),('regret_max',reg.max()),('top10_recovery',rec.mean()),('winner_coverage',np.isin(winner,s).mean())]:assert np.isclose(row[key],val,atol=1e-14)
   for q in ['A','H','V']:assert np.isclose(row['list_'+q+'_mean'],d[q].to_numpy()[s].mean())
   scenarios+=len(w)
checks.update(all_scenario_set_rows=scenarios,all_main_selections=selects,all_training_block_selections=blockschecked)
lps=pd.read_csv(O/'continuous_lp_candidates.csv.gz');largest=0
for (ctx,label),g in lps.groupby(['context','set']):
 c=next(z for z in P['contexts'] if z['name']==ctx);e=np.arange(630) if c['A_min'] is None else np.where(d.A.to_numpy()>=c['A_min'])[0];s=np.array([ix[p] for p in short[(short.context==ctx)&(short['set']==label)].pair]);assert g.success.all();w=g[['wA','wH','wV']].to_numpy();assert np.allclose(w.sum(axis=1),1,atol=1e-9) and w.min()>=-1e-9
 if c['space']=='ordered':assert np.all(w[:,0]>=w[:,1]-1e-9) and np.all(w[:,1]>=w[:,2]-1e-9)
 else:assert np.all(w[:,2]<=({'solar70':.3,'solar80':.2}[c['space']])+1e-9)
 j=[ix[p] for p in g.candidate];own=(w*X[j]).sum(axis=1)-(w@X[s].T).max(axis=1);err=np.max(np.abs(own-g.raw_objective));largest=max(largest,float(err));assert err<1e-8
checks['lp_witness_rows']=len(lps);checks['max_lp_objective_error']=largest
# Verify paired comparisons and every preregistered adoption flag independently.
paired=pd.read_csv(O/'paired_differences.csv')
for r in paired.itertuples():
 a=pd.read_csv(O/'scenario_metrics'/f'{r.context}_{r.split}_{r.method}.csv.gz');b=pd.read_csv(O/'scenario_metrics'/f'{r.context}_{r.split}_historical10.csv.gz')
 col={'regret':'regret','recovery':'top10_recovery','utility_coverage':'utility_winner_covered'}[r.metric];delta=a[col].astype(float)-b[col].astype(float);se=delta.std(ddof=1)/len(delta)**.5
 assert np.isclose(delta.mean(),r.mean_difference,atol=1e-14) and np.isclose(se,r.mc_se,atol=1e-14)
 assert np.isclose(delta.mean()-1.959963984540054*se,r.mc95_low,atol=1e-14)
claims=json.loads((O/'CONCLUSIONS.json').read_text());lp_summary=pd.read_csv(O/'continuous_worst_regret.csv')
for c in claims:
 name=c['context'];expected={}
 for split in ['test','replication']:
  q=summary[(summary.context==name)&(summary.split==split)].set_index('set');h=q.loc['historical10'];a=q.loc['protected_coverage10'];pp=paired[(paired.context==name)&(paired.split==split)&(paired.method=='protected_coverage10')&(paired.metric=='recovery')].iloc[0]
  expected[split+'_recovery_gain_ge_002']=a.top10_recovery-h.top10_recovery>=.02
  expected[split+'_recovery_MC_lower_positive']=pp.mc95_low>0
  expected[split+'_winner_no_loss']=a.utility_winner_coverage>=h.utility_winner_coverage-1e-4
  expected[split+'_mean_regret_no_loss']=a.regret_mean<=h.regret_mean+1e-8
  for met in ['A','H']:expected[split+'_mean_'+met+'_guard']=a['list_'+met+'_mean']>=.95*h['list_'+met+'_mean']
 q=lp_summary[lp_summary.context==name].set_index('set');expected['continuous_regret_no_loss']=q.loc['protected_coverage10','continuous_worst_regret']<=q.loc['historical10','continuous_worst_regret']+1e-8
 assert all(bool(v)==c['checks'][k] for k,v in expected.items());assert all(expected.values())==c['supported_replacement']
hb=pd.read_csv(R/'icores_2027/runs/statistics_20261016/comparison_values.csv').set_index('pair_key');ev=pd.read_csv(R/'icores_2027/architect_first_cloud/analysis/decision_evidence_matrix.csv').set_index('building_pair')
for row in short.itertuples():
 assert row.translation_status==ev.loc[row.pair,'design_translation_status'];assert row.HB_review_status==ev.loc[row.pair,'HB_review_status']
 if row.pair in hb.index:assert row.HB_cohort==hb.loc[row.pair,'comparison_set'] and np.isclose(row.hb_A,hb.loc[row.pair,'hb_A']) and np.isclose(row.hb_H,hb.loc[row.pair,'hb_H'])
 else:assert row.HB_cohort=='MISSING' and np.isnan(row.hb_A) and np.isnan(row.hb_H)
checks['paired_rows_verified']=len(paired);checks['adoption_decisions_verified']=len(claims);checks['evidence_rows_verified']=len(short)
checks['status']='PASS';checks['manifest_sha256']=digest(B/'RUN_MANIFEST.json');checks['protocol_sha256']=digest(B/'protocol/preregistered_protocol.json');checks['script_sha256']=M['script_sha256']
(B/'qa/independent_check_results.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
