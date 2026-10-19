#!/usr/bin/env python3
"""Prospectively frozen solar-priority archive decision analysis; no physical simulation."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib,time,sys,platform,itertools
import numpy as np,pandas as pd,scipy
from scipy.optimize import linprog
from scipy.optimize._highspy._core import HIGHS_VERSION_MAJOR,HIGHS_VERSION_MINOR,HIGHS_VERSION_PATCH
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'icores_2027/solar_priority_final';OUT=BASE/'results';P=json.loads((BASE/'protocol/preregistered_protocol.json').read_text());T=time.time()
FREEZE=os.environ.get('SOLAR_PROTOCOL_FREEZE_COMMIT','')
assert len(FREEZE)==40,'Require actual pre-execution remote protocol commit'
OUT.mkdir(exist_ok=True)
for f in ['weights','rank_memberships','scenario_metrics']: (OUT/f).mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(d,n):pd.DataFrame(d).to_csv(OUT/n,index=False)
def log(x):print(x,flush=True)
for x in P['inputs']:assert sha(ROOT/x['path'])==x['sha256'],x['path']
d=pd.read_csv(ROOT/P['inputs'][0]['path']);key=lambda p:tuple(int(s[1:]) for s in p.split(','));d=d.iloc[sorted(range(len(d)),key=lambda i:key(d.pair.iloc[i]))].reset_index(drop=True);ids=d.pair.to_numpy();n=len(d);ix={p:i for i,p in enumerate(ids)}
assert n==630 and d.pair.nunique()==630 and (d.N==0).all();assert np.isfinite(d[['A','H','V','N']]).all().all()
assert d.normalization_bounds_json.nunique()==1
bounds=json.loads(d.normalization_bounds_json.iloc[0]);X=np.column_stack([(d.A-bounds['A'][0])/(bounds['A'][1]-bounds['A'][0]),(d.H-bounds['H'][0])/(bounds['H'][1]-bounds['H'][0]),1-(d.V-bounds['V'][0])/(bounds['V'][1]-bounds['V'][0])]);assert X.min()>=-1e-12 and X.max()<=1+1e-12
assert np.max(np.abs(.45*X[:,0]+.35*X[:,1]+.15*X[:,2]+.05-d.score.to_numpy()))<1e-12
prior=pd.read_csv(ROOT/'icores_2027/preference_robust/results/shortlists_evidence.csv');orig={name:np.array([ix[p] for p in prior[prior['set']==name].pair]) for name in ['historical10','robust10','AV10','AHV10']};order=np.argsort(d['rank'].to_numpy(),kind='stable')
hb=pd.read_csv(ROOT/'icores_2027/runs/statistics_20261016/comparison_values.csv').set_index('pair_key');ev=pd.read_csv(ROOT/'icores_2027/architect_first_cloud/analysis/decision_evidence_matrix.csv').set_index('building_pair')
W={};sampling=[]
for space,spec in P['sampling']['spaces'].items():
 for split in P['sampling']['splits']:
  seed=spec['seeds'][split];rng=np.random.Generator(np.random.PCG64(seed));kept=[];cnt=0;prop=0
  if space=='ordered':w=-np.sort(-rng.dirichlet(np.ones(3),size=20000),axis=1);cnt=prop=20000
  else:
   while cnt<20000:
    z=rng.dirichlet(np.ones(3),size=100000);prop+=len(z);z=z[z[:,2]<=({'solar70':.3,'solar80':.2}[space])];cnt+=len(z);kept.append(z)
   w=np.vstack(kept)[:20000]
  W[space,split]=w;np.savez_compressed(OUT/'weights'/f'{space}_{split}.npz',weights=w);sampling.append(dict(space=space,split=split,seed=seed,proposals=prop,accepted_before_truncation=cnt,kept=len(w)))
save(sampling,'sampling_diagnostics.csv')
def front(e,cols):
 Y=np.column_stack(cols)[e];return e[np.array([not np.any(np.all(Y>=y,axis=1)&np.any(Y>y,axis=1)) for y in Y])]
def stats_ranks(w,e):
 u=w@X[e].T;ro=np.argsort(-u,axis=1,kind='stable');top=e[ro[:,:10]];win=e[ro[:,0]];rk=np.empty_like(ro);rk[np.arange(len(w))[:,None],ro]=np.arange(1,len(e)+1);return u,top,win,rk

def select(e,top,win,rk,protected=False):
 cnt=np.bincount(top.ravel(),minlength=n);wc=np.bincount(win,minlength=n);mean={j:rk[:,k].mean() for k,j in enumerate(e)};rank=sorted(e,key=lambda j:(-cnt[j],-wc[j],mean[j],j));required=sorted(set(win)) if protected else []
 if len(required)>10:return None
 return np.array(required+[j for j in rank if j not in required][:10-len(required)])
rows=[];short=[];rankrows=[];stability=[];selectiontrace=[];counts=[];originalviol=[];scenario_jaccard=[];paired=[];sets_by={};elig_by={};tie=[]
for ctx in P['contexts']:
 name=ctx['name'];space=ctx['space'];e=np.arange(n) if ctx['A_min'] is None else np.flatnonzero(d.A.to_numpy()>=ctx['A_min']);elig_by[name]=e
 counts.append(dict(context=name,A_min=ctx['A_min'],eligible_count=len(e),excluded_count=n-len(e),feasible_k10=len(e)>=10))
 for label,s in orig.items():originalviol.append(dict(context=name,set=label,original_count=10,eligible_members=int(np.isin(s,e).sum()),ineligible_members=int((~np.isin(s,e)).sum()),ineligible_pairs=';'.join(ids[s[~np.isin(s,e)]])))
 if len(e)<10:continue
 if ctx['A_min'] is None:sets={k:v.copy() for k,v in orig.items()}
 else:
  eo=[j for j in order if j in set(e)];r=[j for j in orig['robust10'] if j in set(e)];sets={'historical10':np.array(eo[:10]),'robust10':np.array((r+[j for j in eo if j not in r])[:10])}
  for label,cols in [('AV10',[d.A,-d.V]),('AHV10',[d.A,d.H,-d.V])]:
   f=set(front(e,cols));sets[label]=np.array(([j for j in eo if j in f]+[j for j in eo if j not in f])[:10])
 u,top,win,rk=stats_ranks(W[space,'train'],e)
 for label,protected in [('coverage10',False),('protected_coverage10',True)]:
  s=select(e,top,win,rk,protected)
  if s is not None:sets[label]=s
  selectiontrace.append(dict(context=name,method=label,distinct_training_winners=len(set(win)),required_winner_pairs=';'.join(ids[sorted(set(win))]) if protected else '',feasible=s is not None,training_recovery=float(np.isin(top,s).sum(axis=1).mean()/10) if s is not None else None))
  blocks=[]
  for block in range(10):
   sl=slice(block*2000,(block+1)*2000);bs=select(e,top[sl],win[sl],rk[sl],protected);blocks.append(bs)
   stability.append(dict(context=name,method=label,comparison='block_to_full',block_a=block,block_b=-1,feasible=bs is not None and s is not None,jaccard=len(set(bs)&set(s))/len(set(bs)|set(s)) if bs is not None and s is not None else None,pairs=';'.join(ids[bs]) if bs is not None else ''))
  for a,b in itertools.combinations(range(10),2):
   aa,bb=blocks[a],blocks[b];stability.append(dict(context=name,method=label,comparison='block_pair',block_a=a,block_b=b,feasible=aa is not None and bb is not None,jaccard=len(set(aa)&set(bb))/len(set(aa)|set(bb)) if aa is not None and bb is not None else None,pairs=''))
 sets_by[name]=sets
 for label,s in sets.items():
  assert len(s)==10 and len(set(s))==10 and set(s)<=set(e)
  for pos,j in enumerate(s,1):
   p=ids[j];short.append(dict(context=name,set=label,adapted_baseline=ctx['A_min'] is not None and label in orig,position=pos,pair=p,historical_rank=int(d['rank'].iloc[j]),A=d.A.iloc[j],H=d.H.iloc[j],V=d.V.iloc[j],N=d.N.iloc[j],HB_cohort=hb.loc[p,'comparison_set'] if p in hb.index else 'MISSING',hb_A=hb.loc[p,'hb_A'] if p in hb.index else np.nan,hb_H=hb.loc[p,'hb_H'] if p in hb.index else np.nan,HB_review_status=ev.loc[p,'HB_review_status'],translation_status=ev.loc[p,'design_translation_status']))
 for split in P['sampling']['splits']:
  w=W[space,split];u,top,win,rk=stats_ranks(w,e);best=u.max(axis=1);fullbest=(w@X.T).max(axis=1);np.savez_compressed(OUT/'rank_memberships'/f'{name}_{split}.npz',eligible_indices=e,top10_indices=top,winner_indices=win)
  cnt=np.bincount(top.ravel(),minlength=n);wc=np.bincount(win,minlength=n)
  for k,j in enumerate(e):rankrows.append(dict(context=name,split=split,pair=ids[j],top10_count=int(cnt[j]),top10_acceptability=cnt[j]/len(w),winner_count=int(wc[j]),winner_acceptability=wc[j]/len(w),mean_rank=rk[:,k].mean(),worst_observed_rank=int(rk[:,k].max())))
  su_sorted=np.sort(u,axis=1)[:,::-1];tie.append(dict(context=name,split=split,winner_exact_ties=int(np.sum(su_sorted[:,0]==su_sorted[:,1])),boundary_exact_ties=int(np.sum(su_sorted[:,9]==su_sorted[:,10])) if len(e)>10 else 0))
  hcnt=np.isin(top,sets['historical10']).sum(axis=1);jac=hcnt/(20-hcnt);scenario_jaccard.append(dict(context=name,split=split,mean_jaccard=jac.mean(),min_jaccard=jac.min(),median_jaccard=np.median(jac)))
  arrays={}
  for label,s in sets.items():
   sorted_s=np.sort(s);us=w@X[sorted_s].T;chosen=sorted_s[np.argmax(us,axis=1)];su=us.max(axis=1);reg=np.maximum(0,best-su);recovery=np.isin(top,s).sum(axis=1)/10;cov=np.isin(win,s);ucov=reg<=1e-12;arrays[label]=(reg,recovery,ucov)
   r=dict(context=name,space=space,split=split,set=label,n=len(w),k=10,eligible_count=len(e),regret_mean=reg.mean(),regret_p50=np.median(reg),regret_p95=np.quantile(reg,.95),regret_max=reg.max(),winner_coverage=cov.mean(),utility_winner_coverage=ucov.mean(),top10_recovery=recovery.mean(),any_top10_coverage=(recovery>0).mean(),best_utility_mean=su.mean(),full_universe_regret_mean=(fullbest-su).mean(),full_universe_regret_max=(fullbest-su).max(),filter_opportunity_loss_mean=(fullbest-best).mean(),filter_opportunity_loss_max=(fullbest-best).max())
   for q in ['A','H','V']:
    for typ,vals in [('list',d[q].to_numpy()[s]),('chosen',d[q].to_numpy()[chosen])]:
     for metric,value in [('min',vals.min()),('q25',np.quantile(vals,.25)),('median',np.median(vals)),('mean',vals.mean()),('q75',np.quantile(vals,.75)),('max',vals.max())]:r[f'{typ}_{q}_{metric}']=value
   r['rule_HB_count']=sum(ids[j] in hb.index for j in s);r['translation_checked_count']=sum(str(ev.loc[ids[j],'design_translation_status']).startswith('CONTAINED') or str(ev.loc[ids[j],'design_translation_status']).startswith('UNCHANGED') for j in s)
   rows.append(r)
   save(dict(scenario=np.arange(len(w)),best_utility=su,regret=reg,winner_covered=cov,utility_winner_covered=ucov,top10_recovery=recovery,selected_pair=ids[chosen],selected_A=d.A.to_numpy()[chosen],selected_H=d.H.to_numpy()[chosen],selected_V=d.V.to_numpy()[chosen],full_universe_regret=fullbest-su),f'scenario_metrics/{name}_{split}_{label}.csv.gz')
  for label in ['coverage10','protected_coverage10']:
   if label not in arrays:continue
   for metric,k in [('regret',0),('recovery',1),('utility_coverage',2)]:
    delta=arrays[label][k].astype(float)-arrays['historical10'][k].astype(float);se=delta.std(ddof=1)/np.sqrt(len(delta));paired.append(dict(context=name,split=split,method=label,metric=metric,mean_difference=delta.mean(),mc_se=se,mc95_low=delta.mean()-1.959963984540054*se,mc95_high=delta.mean()+1.959963984540054*se))
 log('Evaluated '+name+' '+str({k:list(ids[s]) for k,s in sets.items()}))
for a,nm in [(rows,'shortlist_evaluation.csv'),(short,'shortlists_evidence.csv'),(counts,'threshold_counts.csv'),(originalviol,'original_list_threshold_violations.csv'),(rankrows,'candidate_acceptability.csv'),(stability,'selection_stability.csv'),(selectiontrace,'selection_trace.csv'),(paired,'paired_differences.csv'),(scenario_jaccard,'scenario_top10_stability.csv'),(tie,'tie_diagnostics.csv')]:save(a,nm)
# Additional prespecified diagnostics, never used for selection.
rdf=pd.DataFrame(rankrows);diff=[]
for name in sets_by:
 a=rdf.query('context==@name and split=="test"').set_index('pair');b=rdf.query('context==@name and split=="replication"').set_index('pair')
 for pair in a.index:diff.append(dict(context=name,pair=pair,top10_acceptability_rep_minus_test=b.loc[pair,'top10_acceptability']-a.loc[pair,'top10_acceptability'],winner_acceptability_rep_minus_test=b.loc[pair,'winner_acceptability']-a.loc[pair,'winner_acceptability']))
save(diff,'acceptability_replication_differences.csv')
sdf=pd.DataFrame(stability);freq=[]
for (name,method),g in sdf.query('comparison=="block_to_full"').groupby(['context','method']):
 feasible=g[g.feasible];occ={pair:0 for pair in ids}
 for pairs in feasible.pairs:
  for pair in pairs.split(';'):occ[pair]+=1
 for pair,count in occ.items():freq.append(dict(context=name,method=method,pair=pair,selected_blocks=count,feasible_blocks=len(feasible),selection_frequency=count/len(feasible) if len(feasible) else None))
save(freq,'block_membership_frequency.csv')
# Boundaries are evaluation only, never selection.
grid=np.array([(i/100,j/100,(100-i-j)/100) for i in range(101) for j in range(101-i)]);lp_rows=[];lp_summary=[];gridrows=[];cache={}
for ctx in P['contexts']:
 name=ctx['name'];space=ctx['space'];e=elig_by[name]
 if name not in sets_by:continue
 g=grid[(grid[:,0]>=grid[:,1]-1e-12)&(grid[:,1]>=grid[:,2]-1e-12)] if space=='ordered' else grid[grid[:,2]<=({'solar70':.3,'solar80':.2}[space])+1e-12]
 gu,gt,gw,gr=stats_ranks(g,e);gb=gu.max(axis=1);np.savez_compressed(OUT/'rank_memberships'/f'{name}_grid.npz',weights=g,eligible_indices=e,top10_indices=gt,winner_indices=gw)
 for label,s in sets_by[name].items():
  rg=gb-(g@X[s].T).max(axis=1);gridrows.append(dict(context=name,set=label,n=len(g),regret_mean=rg.mean(),regret_max=rg.max(),top10_recovery=np.isin(gt,s).sum(axis=1).mean()/10,winner_coverage=np.isin(gw,s).mean()))
  ck=(space,tuple(e),tuple(sorted(s)))
  if ck not in cache:
   rr=[]
   for j in e:
    au=np.column_stack((X[s]-X[j],np.ones(len(s))));bu=np.zeros(len(s))
    if space=='ordered':au=np.vstack([au,[-1,1,0,0],[0,-1,1,0]]);bu=np.r_[bu,0,0]
    else:au=np.vstack([au,[0,0,1,0]]);bu=np.r_[bu,{'solar70':.3,'solar80':.2}[space]]
    sol=linprog([0,0,0,-1],A_ub=au,b_ub=bu,A_eq=[[1,1,1,0]],b_eq=[1],bounds=[(0,1)]*3+[(None,None)],method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});row=dict(candidate=ids[j],success=sol.success,status=sol.status)
    if sol.success:
     w=sol.x[:3];own=float(X[j]@w-(X[s]@w).max());res=max(0,float(np.max(au@sol.x-bu)),float(abs(w.sum()-1)),float(-w.min()),float(w.max()-1));assert res<=1e-8 and abs(own-sol.x[3])<=1e-8
     row.update(raw_objective=sol.x[3],wA=w[0],wH=w[1],wV=w[2],own_objective=own,global_witness_regret=float((X[e]@w).max()-(X[s]@w).max()),residual=res)
    rr.append(row)
   cache[ck]=rr
  rr=cache[ck];lp_rows.extend([dict(context=name,set=label,**r) for r in rr]);ok=all(x['success'] for x in rr)
  if ok:
   mx=max(rr,key=lambda a:a['raw_objective']);assert abs(mx['raw_objective']-mx['global_witness_regret'])<=1e-8;obs=max(r['regret_max'] for r in rows if r['context']==name and r['set']==label);assert mx['raw_objective']>=max(obs,rg.max())-1e-8
   lp_summary.append(dict(context=name,set=label,all_success=True,lp_count=len(e),continuous_worst_regret=max(0,mx['raw_objective']),raw_objective=mx['raw_objective'],wA=mx['wA'],wH=mx['wH'],wV=mx['wV'],witness_candidate=mx['candidate']))
  else:lp_summary.append(dict(context=name,set=label,all_success=False,lp_count=len(e)))
 log('LP complete '+name)
save(lp_rows,'continuous_lp_candidates.csv.gz');save(lp_summary,'continuous_worst_regret.csv');save(gridrows,'grid_evaluation.csv')
# Apply prospectively declared replacement guards, including failures.
evdf=pd.DataFrame(rows);pdf=pd.DataFrame(paired);ldf=pd.DataFrame(lp_summary);claims=[]
for ctx in P['contexts']:
 name=ctx['name'];method='protected_coverage10'
 if name not in sets_by or method not in sets_by[name]:claims.append(dict(context=name,supported_replacement=False,reason='infeasible'));continue
 checks={}
 for split in ['test','replication']:
  a=evdf.query('context==@name and split==@split').set_index('set');h=a.loc['historical10'];v=a.loc[method];ci=pdf.query('context==@name and split==@split and method==@method and metric=="recovery"').iloc[0]
  checks[split+'_recovery_gain_ge_002']=bool(v.top10_recovery-h.top10_recovery>=.02);checks[split+'_recovery_MC_lower_positive']=bool(ci.mc95_low>0);checks[split+'_winner_no_loss']=bool(v.utility_winner_coverage>=h.utility_winner_coverage-1e-4);checks[split+'_mean_regret_no_loss']=bool(v.regret_mean<=h.regret_mean+1e-8)
  for q in ['A','H']:checks[split+'_mean_'+q+'_guard']=bool(v['list_'+q+'_mean']>=.95*h['list_'+q+'_mean'])
 l=ldf.query('context==@name').set_index('set');checks['continuous_regret_no_loss']=bool(l.loc[method,'all_success'] and l.loc['historical10','all_success'] and l.loc[method,'continuous_worst_regret']<=l.loc['historical10','continuous_worst_regret']+1e-8);claims.append(dict(context=name,supported_replacement=all(checks.values()),checks=checks))
(OUT/'CONCLUSIONS.json').write_text(json.dumps(claims,indent=2))
save(d[['pair','A','H','V','N','rank','score']],'all630_archived_metrics.csv')
manifest={'freeze_commit':FREEZE,'protocol_sha256':sha(BASE/'protocol/preregistered_protocol.json'),'script_sha256':sha(Path(__file__)),'runtime_seconds':time.time()-T,'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'highs':'.'.join(map(str,[HIGHS_VERSION_MAJOR,HIGHS_VERSION_MINOR,HIGHS_VERSION_PATCH])),'platform':platform.platform(),'inputs':P['inputs'],'outputs':[{'path':str(f.relative_to(BASE)),'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted(OUT.rglob('*')) if f.is_file()],'new_physical_simulation':False}
(BASE/'RUN_MANIFEST.json').write_text(json.dumps(manifest,indent=2));log(json.dumps(claims));log('Complete '+str(time.time()-T)+' seconds')
