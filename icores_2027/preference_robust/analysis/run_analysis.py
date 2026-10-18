#!/usr/bin/env python3
"""Frozen preference-only archive reanalysis. No physical simulation or re-selection."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ.setdefault('MPLCONFIGDIR','/tmp/preference-matplotlib')
from pathlib import Path
import json,hashlib,time,sys,platform,itertools
import numpy as np
import pandas as pd
import scipy
from scipy.optimize._highspy._core import HIGHS_VERSION_MAJOR,HIGHS_VERSION_MINOR,HIGHS_VERSION_PATCH
from scipy.stats import pearsonr,spearmanr
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[3]; BASE=ROOT/'icores_2027/preference_robust'; OUT=BASE/'results'; FIG=BASE/'figures'
for p in [OUT,FIG]:p.mkdir(parents=True,exist_ok=True)
T0=time.time(); FREEZE='cff3e81eebf93a16df6da8a21fe735c1554a5a8f'; P=json.loads((BASE/'protocol/preregistered_protocol.json').read_text())
def log(s):print(s,flush=True)
def save(df,name):df.to_csv(OUT/name,index=False)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[]
def read(p):
 f=ROOT/p; inputs.append({'path':p,'sha256':digest(f),'bytes':f.stat().st_size});return pd.read_csv(f)
for a in P['inputs']:assert digest(ROOT/a['path'])==a['sha256'],a['path']
d=read('icores_2027/runs/local_ablation_20261016/aggregate_B_m630_r1_run.csv')
old=read('icores_2027/architect_first_cloud/analysis/top10_rule_candidates.csv')
ev=read('icores_2027/architect_first_cloud/analysis/decision_evidence_matrix.csv')
hb=read('icores_2027/runs/statistics_20261016/comparison_values.csv')
tr=read('icores_2027/runs/local_hb_20261016/translation_outcome_comparison.csv')
raw=read('paper_assets/tables/table_03_candidate_universe.csv')
key=lambda p:tuple(int(s[1:]) for s in p.split(','))
d=d.iloc[sorted(range(len(d)),key=lambda j:key(d.iloc[j]['pair']))].reset_index(drop=True)
ids=d.pair.to_numpy(); idx={p:i for i,p in enumerate(ids)}; n=len(d)
assert n==630 and d.pair.nunique()==630
buildings=sorted(set(','.join(ids).split(',')),key=lambda s:int(s[1:]));assert len(buildings)==36
assert set(ids)=={','.join(x) for x in itertools.combinations(buildings,2)}
assert np.isfinite(d[['A','H','V','N']].to_numpy()).all() and (d.N==0).all()
assert d.normalization_bounds_json.nunique()==1
bounds=json.loads(d.normalization_bounds_json.iloc[0]); norm={}
for q in ['A','H','V','N']:
 lo,hi=bounds[q];norm[q]=np.zeros(n) if hi==lo else (d[q].to_numpy()-lo)/(hi-lo)
X=np.array([norm['A'],norm['H'],1-norm['V']]).T
assert X.min()>=-1e-12 and X.max()<=1+1e-12
score=.45*norm['A']+.35*norm['H']+.15*(1-norm['V'])+.05*(1-norm['N'])
assert np.max(np.abs(score-d.score.to_numpy()))<1e-12
hist=d.sort_values(['score','A','H'],ascending=False,kind='stable').query('A>0').head(10).pair.to_list()
assert hist==old.building_pair.to_list()
cor={'pearson_A_H':float(pearsonr(d.A,d.H).statistic),'spearman_A_H':float(spearmanr(d.A,d.H).statistic),'N_all_zero':True,'N_unique':[0],'n':n,'normalization_bounds':bounds}
(OUT/'metric_audit.json').write_text(json.dumps(cor,indent=2))
log('Metric audit: '+json.dumps(cor))
# Strict Pareto domination without tolerance; coincident objective vectors retained.
def front(cols):
 Y=np.asarray(cols).T
 return np.array([not np.any(np.all(Y>=Y[i],axis=1)&np.any(Y>Y[i],axis=1)) for i in range(n)])
av=front([d.A,-d.V]); ahv=front([d.A,d.H,-d.V])
order=np.argsort(d['rank'].to_numpy(),kind='stable')
def trunc(mask):
 f=[j for j in order if mask[j]];return np.array((f+[j for j in order if not mask[j]])[:10])
sets={'historical10':np.array([idx[p] for p in hist]),'AV10':trunc(av),'AHV10':trunc(ahv)}
W={}; sampling=[]
for space in P['sampling']['space_order']:
 for split in P['sampling']['splits']:
  seed=P['sampling']['spaces'][space]['seeds'][split];rng=np.random.Generator(np.random.PCG64(seed)); proposals=20000
  if space=='local':
   accepted=[];count=0;proposals=0
   while count<20000:
    a=rng.dirichlet(np.ones(3),size=100000); proposals+=len(a);a=a[np.all(np.abs(a-np.array([9,7,3])/19)<=.1,axis=1)];accepted.append(a);count+=len(a)
   w=np.vstack(accepted)[:20000]
  else:
   w=rng.dirichlet(np.ones(3),size=20000)
   if space=='ordered':w=-np.sort(-w,axis=1)
  W[space,split]=w;sampling.append({'space':space,'split':split,'seed':seed,'kept':len(w),'proposals':proposals,'accepted_before_truncation':count if space=='local' else 20000,'raw_acceptance_rate':count/proposals if space=='local' else 1.0})
(OUT/'weight_samples').mkdir(exist_ok=True)
for (space,split),weights in W.items():np.savez_compressed(OUT/'weight_samples'/f'{space}_{split}.npz',weights=weights)
np.savez_compressed(OUT/'weight_samples.npz',**{f'{a}_{b}':v for (a,b),v in W.items()});save(pd.DataFrame(sampling),'sampling_diagnostics.csv')
train=np.vstack([W[s,'train'] for s in P['sampling']['space_order']]);U=train@X.T;ustar=U.max(axis=1);current=np.zeros(len(U));chosen=[];trace=[]
for k in range(10):
 best=None
 for j in range(n):
  if j in chosen:continue
  r=ustar-np.maximum(current,U[:,j]);obj=(float(r.max()),float(r.mean()),j)
  if best is None or obj<best:best=obj
 j=best[2];chosen.append(j);current=np.maximum(current,U[:,j]);trace.append({'k':k+1,'pair':ids[j],'max_train_regret':best[0],'mean_train_regret':best[1]});log('Greedy '+str(trace[-1]))
sets['robust10']=np.array(chosen);sets['AV_full']=np.flatnonzero(av);sets['AHV_full']=np.flatnonzero(ahv)
save(pd.DataFrame(trace),'greedy_trace.csv');del U
log('Sets: '+json.dumps({k:list(ids[v]) for k,v in sets.items()}))
shortrows=[]
ev=ev.set_index('building_pair');hb=hb.set_index('pair_key');assert len(hb)==43 and hb.index.nunique()==43
for label,js in sets.items():
 for pos,j in enumerate(js,1):
  p=ids[j];row={'set':label,'position':pos,'pair':p,'historical_rank':int(d.iloc[j]['rank']),'A':d.iloc[j].A,'H':d.iloc[j].H,'V':d.iloc[j].V,'N':d.iloc[j].N,'historical_score':score[j],'AV_front':bool(av[j]),'AHV_front':bool(ahv[j]),'HB_review_status':ev.loc[p,'HB_review_status'],'design_translation_status':ev.loc[p,'design_translation_status'],'hb_A':hb.loc[p,'hb_A'] if p in hb.index else np.nan,'hb_H':hb.loc[p,'hb_H'] if p in hb.index else np.nan,'HB_cohort':hb.loc[p,'comparison_set'] if p in hb.index else 'MISSING','candidate_id':ev.loc[p,'candidate_id']};shortrows.append(row)
save(pd.DataFrame(shortrows),'shortlists_evidence.csv')
all_d=d.copy();all_d['AV_front']=av;all_d['AHV_front']=ahv
for name,s in sets.items():all_d[name]=np.isin(np.arange(n),s)
all_d['hb_A']=all_d.pair.map(hb.hb_A);all_d['hb_H']=all_d.pair.map(hb.hb_H);all_d['HB_cohort']=all_d.pair.map(hb.comparison_set).fillna('MISSING')
save(all_d,'all630_metrics_memberships.csv')
def wilson(k,N):
 z=1.959963984540054;p=np.asarray(k)/N;mid=(p+z*z/(2*N))/(1+z*z/N);half=z*np.sqrt(p*(1-p)/N+z*z/(4*N*N))/(1+z*z/N);return mid-half,mid+half
stats=[];summary=[];paired=[];jaccards=[];ties=[];scenario_frames=[];prefix_summary=[]
def summarize(r,u,win,uwin,topany,recovery,space,split,label):
 row={'space':space,'split':split,'set':label,'n':len(r),'k':len(sets[label]) if label in sets else int(label.split('_')[-1]),'regret_mean':r.mean(),'regret_p50':np.quantile(r,.5),'regret_p95':np.quantile(r,.95),'regret_max':r.max(),'regret_mean_mc_se':r.std(ddof=1)/np.sqrt(len(r)),'utility_mean_mc_se':u.std(ddof=1)/np.sqrt(len(u)),'winner_coverage':win.mean(),'utility_winner_coverage':uwin.mean(),'any_top10_coverage':topany.mean(),'top10_recovery':recovery.mean()}
 for q,v in [('mean',u.mean()),('p05',np.quantile(u,.05)),('p50',np.quantile(u,.5)),('p95',np.quantile(u,.95)),('min',u.min()),('max',u.max())]:row['utility_'+q]=v
 for col,a in [('winner_coverage',win),('utility_winner_coverage',uwin),('any_top10_coverage',topany)]:row[col+'_ci_low'],row[col+'_ci_high']=wilson(a.sum(),len(a))
 return row
for space in P['sampling']['space_order']:
 for split in P['sampling']['splits']:
  w=W[space,split];u=w@X.T;m=len(w);rorder=np.argsort(-u,axis=1,kind='stable');ranks=np.empty_like(rorder,dtype=np.uint16);ranks[np.arange(m)[:,None],rorder]=np.arange(1,n+1,dtype=np.uint16);top=rorder[:,:10];best=u.max(axis=1)
  histogram=np.stack([np.bincount(ranks[:,j],minlength=n+1)[1:] for j in range(n)])
  h=pd.DataFrame(histogram,columns=[f'rank_{j}' for j in range(1,n+1)]);h.insert(0,'pair',ids);save(h,f'rank_distribution_{space}_{split}.csv.gz')
  rankfile={'top10_indices':top.astype(np.uint16),'winner_indices':rorder[:,0].astype(np.uint16)};np.savez_compressed(OUT/f'rank_memberships_{space}_{split}.npz',**rankfile)
  for j in range(n):
   wc=int(histogram[j,0]);tc=int(histogram[j,:10].sum());wl,wh=wilson(wc,m);tl,th=wilson(tc,m);stats.append({'space':space,'split':split,'pair':ids[j],'winner_count':wc,'winner_acceptability':wc/m,'winner_ci_low':wl,'winner_ci_high':wh,'top10_count':tc,'top10_acceptability':tc/m,'top10_ci_low':tl,'top10_ci_high':th,'average_rank':ranks[:,j].mean(),'worst_observed_rank':ranks[:,j].max()})
  sortedu=np.take_along_axis(u,rorder[:,:11],axis=1);wgap=sortedu[:,0]-sortedu[:,1];tgap=sortedu[:,9]-sortedu[:,10]
  ties.append({'space':space,'split':split,'winner_exact_ties':int((wgap==0).sum()),'winner_near_ties_1e12':int((wgap<=1e-12).sum()),'top10_boundary_exact_ties':int((tgap==0).sum()),'top10_boundary_near_ties_1e12':int((tgap<=1e-12).sum())})
  intersection=np.isin(top,sets['historical10']).sum(axis=1);jac=intersection/(20-intersection)
  jaccards.append({'space':space,'split':split,'mean':jac.mean(),'p05':np.quantile(jac,.05),'p50':np.quantile(jac,.5),'p95':np.quantile(jac,.95),'min':jac.min(),'max':jac.max()})
  np.savez_compressed(OUT/f'jaccard_{space}_{split}.npz',jaccard_to_historical10=jac)
  regrets={}
  for label,js in sets.items():
   su=u[:,js].max(axis=1);reg=np.maximum(0,best-su);win=np.isin(rorder[:,0],js);uwin=reg<=1e-12;cnt=np.isin(top,js).sum(axis=1);topany=cnt>0;rec=cnt/10;regrets[label]=reg
   summary.append(summarize(reg,su,win,uwin,topany,rec,space,split,label))
   scenario_frames.append(pd.DataFrame({'space':space,'split':split,'scenario':np.arange(m),'set':label,'best_utility':su,'regret':reg,'winner_covered':win,'utility_winner_covered':uwin,'any_top10_covered':topany,'top10_recovered':cnt}))
  for k in range(1,11):
   js=np.array(chosen[:k]);su=u[:,js].max(axis=1);reg=np.maximum(0,best-su);cnt=np.isin(top,js).sum(axis=1)
   prefix_summary.append(summarize(reg,su,np.isin(rorder[:,0],js),reg<=1e-12,cnt>0,cnt/10,space,split,f'prefix_{k}'))
  for baseline in ['historical10','AV10','AHV10']:
   diff=regrets['robust10']-regrets[baseline];se=diff.std(ddof=1)/np.sqrt(m);paired.append({'space':space,'split':split,'comparator':baseline,'mean_regret_difference_robust_minus_comparator':diff.mean(),'mc_se':se,'mc95_low':diff.mean()-1.959963984540054*se,'mc95_high':diff.mean()+1.959963984540054*se})
  log(f'Evaluated {space}/{split}')
stat=pd.DataFrame(stats);save(stat,'all630_rank_acceptability.csv');save(pd.DataFrame(summary),'shortlist_evaluation.csv');save(pd.DataFrame(paired),'paired_regret_differences.csv');save(pd.DataFrame(prefix_summary),'greedy_prefix_evaluation.csv');save(pd.DataFrame(ties),'tie_diagnostics.csv');save(pd.DataFrame(jaccards),'membership_stability.csv');scen=pd.concat(scenario_frames,ignore_index=True);save(scen,'set_scenario_metrics.csv.gz');del scenario_frames
(OUT/'set_scenario_metrics').mkdir(exist_ok=True)
for (space,split,label),g in scen.groupby(['space','split','set']):save(g,f'set_scenario_metrics/{space}_{split}_{label}.csv.gz')
cross=[];crossjac=[]
for split in ['train','test','replication']:
 for a,b in itertools.combinations(P['sampling']['space_order'],2):
  aa=stat[(stat.space==a)&(stat.split==split)].set_index('pair');bb=stat[(stat.space==b)&(stat.split==split)].set_index('pair')
  for p in ids:cross.append({'split':split,'space_a':a,'space_b':b,'pair':p,**{v+'_delta_b_minus_a':float(bb.loc[p,v])-float(aa.loc[p,v]) for v in ['winner_acceptability','top10_acceptability','average_rank','worst_observed_rank']}})
  def most10(x):return set(sorted(ids,key=lambda p:(-x.loc[p,'top10_acceptability'],x.loc[p,'average_rank'],key(p)))[:10])
  sa,sb=most10(aa),most10(bb);crossjac.append({'split':split,'space_a':a,'space_b':b,'top_acceptability_top10_jaccard':len(sa&sb)/len(sa|sb)})
save(pd.DataFrame(cross),'cross_space_candidate_changes.csv');save(pd.DataFrame(crossjac),'cross_space_top_acceptability_jaccard.csv')
mc=[];mcsummary=[]
for space in P['sampling']['space_order']:
 a=stat[(stat.space==space)&(stat.split=='test')].set_index('pair');b=stat[(stat.space==space)&(stat.split=='replication')].set_index('pair')
 for p in ids:mc.append({'space':space,'pair':p,**{c+'_replication_minus_test':b.loc[p,c]-a.loc[p,c] for c in ['winner_acceptability','top10_acceptability','average_rank']}})
 for c in ['winner_acceptability','top10_acceptability']:
  z=np.abs(b[c]-a[c]);mcsummary.append({'space':space,'metric':c,'median_absolute_delta':z.median(),'p95_absolute_delta':z.quantile(.95),'max_absolute_delta':z.max()})
save(pd.DataFrame(mc),'mc_candidate_replication_differences.csv');save(pd.DataFrame(mcsummary),'mc_error_summary.csv')
# Equal-space pooled evaluation is secondary; same fixed sets.
pooled=[]
for (split,label),g in scen.groupby(['split','set']):
 pooled.append(summarize(g.regret.to_numpy(),g.best_utility.to_numpy(),g.winner_covered.to_numpy(),g.utility_winner_covered.to_numpy(),g.any_top10_covered.to_numpy(),g.top10_recovered.to_numpy()/10,'equal_space_pool',split,label))
pooled_df=pd.DataFrame(pooled)
for row in pooled_df.index:
 split=pooled_df.loc[row,'split'];label=pooled_df.loc[row,'set'];g=scen[(scen.split==split)&(scen['set']==label)]
 for source,target in [('regret','regret_mean_mc_se'),('best_utility','utility_mean_mc_se')]:
  pooled_df.loc[row,target]=np.sqrt(sum(z[source].var(ddof=1)/len(z) for _,z in g.groupby('space'))/9)
# Pooled design is stratified rather than IID; marginal Wilson intervals are only reported within spaces.
pooled_df=pooled_df[[c for c in pooled_df if '_ci_' not in c]]
save(pooled_df,'pooled_shortlist_evaluation.csv')
overlap=[]
for label,s in sets.items():
 a=set(s);b=set(sets['historical10']);overlap.append({'set':label,'k':len(s),'historical_intersection':len(a&b),'historical_jaccard':len(a&b)/len(a|b)})
save(pd.DataFrame(overlap),'shortlist_overlap.csv')
# Deterministic stress grid, explicitly held out of selection.
grid=np.array([(i/100,j/100,(100-i-j)/100) for i in range(101) for j in range(101-i)])
gridrows=[];gridsummary=[]
for space in P['sampling']['space_order']:
 g=grid
 if space=='ordered':g=g[(g[:,0]>=g[:,1]-1e-12)&(g[:,1]>=g[:,2]-1e-12)]
 if space=='local':g=g[np.all(np.abs(g-np.array([9,7,3])/19)<=.1+1e-12,axis=1)]
 u=g@X.T;best=u.max(axis=1);rorder=np.argsort(-u,axis=1,kind='stable');top=rorder[:,:10]
 for label,s in sets.items():
  su=u[:,s].max(axis=1);reg=np.maximum(0,best-su);cnt=np.isin(top,s).sum(axis=1)
  gridsummary.append(summarize(reg,su,np.isin(rorder[:,0],s),reg<=1e-12,cnt>0,cnt/10,space,'grid',label))
  gridrows.append(pd.DataFrame({'space':space,'set':label,'wA':g[:,0],'wH':g[:,1],'wV':g[:,2],'best_utility':su,'regret':reg,'winner_index':rorder[:,0],'winner_covered':np.isin(rorder[:,0],s),'utility_winner_covered':reg<=1e-12,'top10_recovered':cnt}))
save(pd.concat(gridrows),'grid_scenario_metrics.csv.gz');grid_summary=pd.DataFrame(gridsummary)
# MC interval columns are deliberately removed for deterministic stress grid.
grid_summary=grid_summary[[c for c in grid_summary if '_mc_' not in c and '_ci_' not in c]];save(grid_summary,'grid_evaluation.csv')
log('Starting fixed-set continuous LP audit')
lprows=[];lpsummary=[];cache={};options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9}
for space in P['sampling']['space_order']:
 for label,s in sets.items():
  ck=(space,tuple(sorted(s)));results=[]
  if ck in cache:
   results=[dict(r,set=label) for r in cache[ck]]
  else:
   wb=[(0,1)]*3 if space!='local' else [(float(c-.1),float(c+.1)) for c in np.array([9,7,3])/19]
   for i in range(n):
    aub=np.column_stack((X[s]-X[i],np.ones(len(s))));bub=np.zeros(len(s))
    if space=='ordered':aub=np.vstack([aub,[-1,1,0,0],[0,-1,1,0]]);bub=np.r_[bub,0,0]
    sol=linprog([0,0,0,-1],A_ub=aub,b_ub=bub,A_eq=[[1,1,1,0]],b_eq=[1],bounds=wb+[(None,None)],method='highs',options=options)
    row={'space':space,'set':label,'candidate':ids[i],'status':sol.status,'success':sol.success,'message':sol.message}
    if sol.success:
     w=sol.x[:3];rawobj=sol.x[3];witness=float((X@w).max()-(X[s]@w).max());own=float(X[i]@w-(X[s]@w).max());res=max(0,float(np.max(aub@sol.x-bub)),float(abs(w.sum()-1)),max(lo-float(v) for v,(lo,hi) in zip(w,wb)),max(float(v)-hi for v,(lo,hi) in zip(w,wb)))
     row.update(raw_objective=rawobj,wA=w[0],wH=w[1],wV=w[2],candidate_witness_objective=own,allcandidate_witness_regret=witness,feasibility_residual=res,objective_residual=abs(rawobj-own));assert res<=1e-8 and abs(rawobj-own)<=1e-8
    results.append(row)
   cache[ck]=results
  lprows+=results;ok=all(r['success'] for r in results)
  if ok:
   winner=max(results,key=lambda x:x['raw_objective']);worst=winner['raw_objective'];witness=winner['allcandidate_witness_regret'];assert abs(worst-witness)<=1e-8 and worst>=-1e-8
   observed=max(x['regret_max'] for x in summary if x['space']==space and x['set']==label);gm=float(grid_summary[(grid_summary.space==space)&(grid_summary['set']==label)].regret_max.iloc[0]);assert worst>=max(observed,gm)-1e-8
   lpsummary.append({'space':space,'set':label,'all_630_lps_success':True,'continuous_worst_regret':max(0,worst),'raw_objective':worst,'wA':winner['wA'],'wH':winner['wH'],'wV':winner['wV'],'witness_candidate':winner['candidate'],'witness_regret':witness,'sample_max_including_train':observed,'grid_max':gm})
  else:lpsummary.append({'space':space,'set':label,'all_630_lps_success':False})
  log('LP '+str(lpsummary[-1]))
save(pd.DataFrame(lprows),'continuous_lp_all_candidates.csv.gz');save(pd.DataFrame(lpsummary),'continuous_worst_regret.csv')
# Figures: saved summaries are authoritative sources.
import matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'ps.fonttype':42})
evaldf=pd.read_csv(OUT/'shortlist_evaluation.csv');lp=pd.read_csv(OUT/'continuous_worst_regret.csv')
fig,axs=plt.subplots(1,3,figsize=(11,3.2))
for ax,space in zip(axs,P['sampling']['space_order']):
 labels=['historical10','AV10','AHV10','robust10'];g=evaldf[(evaldf.space==space)&(evaldf.split=='test')].set_index('set').loc[labels];x=np.arange(4);ax.bar(x-.18,g.regret_mean,.36,label='Mean test regret');ax.bar(x+.18,g.regret_p95,.36,label='95th-percentile test regret');ax.set_xticks(x,labels,rotation=30,ha='right');ax.set_title(space);ax.set_ylabel('Absolute utility regret');ax.grid(axis='y',alpha=.2);ax.set_ylim(0,.15)
 if space!='full':ax.text(.5,.5,'All four sets: zero regret',ha='center',va='center',transform=ax.transAxes)
axs[0].legend(fontsize=7);fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(FIG/f'regret_comparison.{ext}',dpi=220)
plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4));lp[lp['set'].isin(['historical10','AV10','AHV10','robust10'])].pivot(index='space',columns='set',values='continuous_worst_regret').plot.bar(ax=ax);ax.set_ylabel('Continuous worst-case utility regret');ax.set_xlabel('Preference space');ax.tick_params(axis='x',rotation=0);fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(FIG/f'continuous_regret.{ext}',dpi=220)
plt.close(fig)
selected=sorted(set(np.concatenate([sets['historical10'],sets['robust10']])),key=lambda j:float(stat[(stat.space=='full')&(stat.split=='test')&(stat.pair==ids[j])].top10_acceptability.iloc[0]),reverse=True)
heat=stat[(stat.split=='test')&stat.pair.isin(ids[selected])].pivot(index='pair',columns='space',values='top10_acceptability').loc[ids[selected],P['sampling']['space_order']]
fig,ax=plt.subplots(figsize=(5,6));im=ax.imshow(heat,vmin=0,vmax=1,cmap='viridis',aspect='auto');ax.set_yticks(range(len(heat)),heat.index);ax.set_xticks(range(3),heat.columns);fig.colorbar(im,ax=ax,label='Top-10 acceptability');fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(FIG/f'acceptability_heatmap.{ext}',dpi=220)
plt.close(fig)
figure_sources={'regret_comparison':'results/shortlist_evaluation.csv','continuous_regret':'results/continuous_worst_regret.csv','acceptability_heatmap':'results/all630_rank_acceptability.csv'}
(BASE/'figures/PROVENANCE.json').write_text(json.dumps(figure_sources,indent=2))
# Predetermined interpretation rule.
stable=True;strict=False
for sp in P['sampling']['space_order']:
 for split in ['test','replication']:
  a=evaldf[(evaldf.space==sp)&(evaldf.split==split)].set_index('set')
  for c in ['regret_mean','regret_p95']:
   delta=a.loc['robust10',c]-a.loc['historical10',c];stable &= delta<=1e-12;strict |= delta< -1e-12
conclusion={'stable_improvement_rule_met':bool(stable and strict),'claim':'Preference robustness under declared weight distributions only; heuristic shortlist, no global optimality.','wall_seconds':time.time()-T0,'front_sizes':{'AV':int(av.sum()),'AHV':int(ahv.sum())},'robust10_pairs':list(ids[sets['robust10']]),'historical10_pairs':hist,'robust10_reviewed':int(sum(p in hb.index for p in ids[sets['robust10']])),'zero_train_regret_first_prefix':next((a['k'] for a in trace if a['max_train_regret']<=1e-12),None)}
(OUT/'CONCLUSIONS.json').write_text(json.dumps(conclusion,indent=2))
manifest={'freeze_commit':FREEZE,'protocol_sha256':digest(BASE/'protocol/preregistered_protocol.json'),'script_sha256':digest(Path(__file__)),'inputs':inputs,'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'highs':f'{HIGHS_VERSION_MAJOR}.{HIGHS_VERSION_MINOR}.{HIGHS_VERSION_PATCH}','platform':platform.platform(),'wall_seconds':time.time()-T0,'new_physical_simulation':False,'output_files':[{'path':str(f.relative_to(BASE)),'sha256':digest(f),'bytes':f.stat().st_size} for f in sorted(OUT.rglob('*')) if f.is_file()]}
(BASE/'RUN_MANIFEST.json').write_text(json.dumps(manifest,indent=2));log('COMPLETE '+json.dumps(conclusion))
