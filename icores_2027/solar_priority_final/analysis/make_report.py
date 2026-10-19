import os
os.environ["MPLCONFIGDIR"]="/tmp/solar-mpl"
os.environ["XDG_CACHE_HOME"]="/tmp/solar-cache"
from pathlib import Path
import pandas as pd,numpy as np,json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=Path(__file__).resolve().parents[1];R=B/'results';F=B/'figures';F.mkdir(exist_ok=True)
e=pd.read_csv(R/'shortlist_evaluation.csv');s=pd.read_csv(R/'shortlists_evidence.csv');lp=pd.read_csv(R/'continuous_worst_regret.csv');counts=pd.read_csv(R/'threshold_counts.csv');con=json.loads((R/'CONCLUSIONS.json').read_text());contexts=list(counts.context)
plt.rcParams.update({'pdf.fonttype':42,'font.size':9});fig,axs=plt.subplots(1,2,figsize=(10,3.7));labs=['ordered','solar70','solar80'];x=np.arange(3)
for i,label in enumerate(['historical10','robust10','protected_coverage10']):
 q=e[(e.split=='test')&(e['set']==label)].set_index('context').loc[labs];axs[0].bar(x+(i-1)*.24,q.top10_recovery,.24,label=label);axs[1].bar(x+(i-1)*.24,q.winner_coverage,.24,label=label)
for ax,title in zip(axs,['Preference-specific Top-10 recovery','Best-candidate identity coverage']):ax.set_xticks(x,labs);ax.set_ylim(0,1.06);ax.set_title(title);ax.grid(axis='y',alpha=.2)
axs[0].legend(fontsize=7,loc='lower left');fig.tight_layout()
for ext in ['pdf','png']:fig.savefig(F/f'coverage_tradeoff.{ext}',dpi=200)
plt.close(fig);fig,axs=plt.subplots(1,3,figsize=(10,3.3));q=e[(e.split=='test')&(e['set']=='protected_coverage10')].set_index('context');h=e[(e.split=='test')&(e['set']=='historical10')].set_index('context')
for ax,m in zip(axs,['A','H','V']):ax.bar(np.arange(3),q.loc[labs,'list_'+m+'_mean']/h.loc[labs,'list_'+m+'_mean']);ax.axhline(1,color='black',ls='--');ax.set_xticks(np.arange(3),labs);ax.set_title('List mean '+m+' / historical');ax.set_ylim(0,1.4)
fig.tight_layout()
for ext in ['pdf','png']:fig.savefig(F/f'solar_benefit_tradeoff.{ext}',dpi=200)
plt.close(fig)
def md(df):
 def fmt(v):return f'{v:.6f}' if isinstance(v,float) else str(v).replace('|','/')
 return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+'\n'.join('| '+' | '.join(fmt(v) for v in row)+' |' for row in df.itertuples(index=False,name=None))
text='''# Solar-priority decision analysis: results and failures

No context satisfies the prospectively declared supported-replacement criterion. Preserve the previous manuscript and evidence; do not relax the0.02 recovery requirement after seeing results. New findings support an optional transparent sensitivity revision, not a superior general algorithm claim.

A failed composite criterion is not absence of all value. Total-solar-weight supports admit H-oriented winning choices missed by Historical10; the new lists preserve them. Ordered priorities already retain the best choice. These are different priority definitions.

## Mathematical selection
For scenario Top10 set T(w), Q(S)=E[|S∩T(w)|/10]=sum(i in S)Pr(i in T(w))/10. Linearity makes Q modular. The ten highest training inclusion frequencies exactly maximize empirical Q. ProtectedCoverage10 mandates each distinct training winner before filling remaining slots; >10 mandated winners is explicitly infeasible. Both selectors have identical membership in all six observed contexts, so the protection constraint adds no observed selection advantage. Neither mechanism is new general optimization theory.

180000 sampled weights are divided into three supports and independent train/test/replication splits of20000. A-floor contexts reuse solar70 samples intentionally. Only training determines membership. Ten training blocks provide selection stability. Independent evaluation, grid and LP never reselect.

Ordered means wA>=wH>=wV but remains compensatory. Total-solar70/80 means wA+wH>=.70/.80, permits wA=0 and does not guarantee a physical A floor. A90/180/270 are hard prospective study scenarios, not laws or expert preferences. All normalization remains global and frozen.

## Threshold attrition
'''+md(counts)+'\n\nLayered baseline lists are explicitly eligible adaptations. Original-list violations are separately archived; no list is silently relabeled. Ten slots are compared within the same universe.\n\n## Independent test\n'+md(e.query('split=="test"')[['context','set','top10_recovery','winner_coverage','regret_mean','regret_max','list_A_mean','list_H_mean','list_V_mean','rule_HB_count']])+'\n\n## Independent replication\n'+md(e.query('split=="replication"')[['context','set','top10_recovery','winner_coverage','regret_mean','regret_max']])+'\n\n## Continuous fixed-set audit\n'+md(lp[['context','set','lp_count','all_success','continuous_worst_regret','wA','wH','wV']])+'\n\nThese LPs audit fixed sets under declared supports, not global set optimality or physical accuracy.\n\n## Frozen success/failure guards\n'
for c in con:text+='\n### '+c['context']+'\nSupported replacement: '+str(c['supported_replacement'])+'\n\nFailed guards: '+', '.join(k for k,v in c.get('checks',{}).items() if not v)+'\n'
text+='''
## Negative findings and boundaries
All recovery gains are below the prospectively declared two-percentage-point criterion. Positive paired Monte Carlo intervals do not override this practical threshold. Ordered selection gains mean A but loses enough mean H to fail its95%guard. Solar80 shifts toward H, loses mean A and increases nominal intervention; do not claim more sunlight and less intervention in every sense. A180 also fails its mean-Aguard. At A270 historical, robust-adapted and both new lists coincide; AV/AHV differ. The A270 filter loses all630 opportunities despite zero conditional regret: conditional regret + filter loss = total regret, all separately saved.

Prior full-simplex Robust10 retains winners but recovers fewer preferred Top10 entries and contains low-A/low-volume options. Its original objective differs; it is not retrained in primary contexts. No geometric diversity, actual architect satisfaction or construction readiness has been measured.

N is exactlyzero and excluded from active rank discrimination but retained for geometry-risk interpretation. Rule-level HB review and translated-design checks are separate; missing entries remain missing. Frozen23/20cohorts are unchanged. This is new decision analysis on archived data, not new physical simulation.

## Recommended architect workflow
Clarify whether priority means orderedA/H/V, high total solar importance, or a hard minimumA. Inspect A and H separately, then nominalV without claiming real cost. Keep Historical10 as a defensible initial list under ordered priorities. Offer contextual total-solar lists as alternatives showing H-rich winning opportunities, with the small recovery gains and missingHBexplicit. Request professional simulation and geometric/structural/rights review before design development. Architect makes the final choice.

## Six requested answers
1. Consider the new mechanism to reveal dependence on one unelicited weight vector and preserve several high-ranked alternatives. The data do not justify automatic replacement.
2.45/35/15/5 ranks once. New selection aggregates Top10 membership across declared weight scenarios, optionally protects trainingwinners, and removes constantNfrom discrimination.
3. Actual benefit: total-solar supports restore missed H-oriented best options and modestly improve Top10 recovery; ordered baseline already has zero regret.
4. Failures: gains<2points, some meanA/H reductions, and no new-list advantage after A270; all six replacementgates fail.
5. Methods are established MCDA/SMAA-related acceptability and modular selection. Contribution is the controlled architectural comparison and transparent limits, not invented optimization theory.
6. Retain the supported baseline and offer sensitivity alternatives; architects choose priority interpretation and final designs.
'''
(B/'RESULTS_AND_FAILURES.md').write_text(text)
compare=[]
for ctx in contexts:
 h=s[(s.context==ctx)&(s['set']=='historical10')].sort_values('position');v=s[(s.context==ctx)&(s['set']=='protected_coverage10')].sort_values('position')
 for (_,a),(_,b) in zip(h.iterrows(),v.iterrows()):compare.append({'context':ctx,'position':a.position,**{'old_'+k:a[k] for k in ['pair','A','H','V','HB_cohort','translation_status']},**{'new_'+k:b[k] for k in ['pair','A','H','V','HB_cohort','translation_status']}})
pd.DataFrame(compare).to_csv(R/'old_new_top10_comparison.csv',index=False)
(B/'NEW_OLD_TOP10_COMPARISON.md').write_text('# Old/new ten-slot comparison\n\nSlots are presentation order, not matched designs or inherent merit ranks. Layered historical lists are explicitly eligible adaptations.\n\n'+md(pd.DataFrame(compare)))
figs=[{'path':str(p.relative_to(B)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':'results/shortlist_evaluation.csv','generator':'analysis/make_report.py'} for p in sorted(F.glob('*'))];(B/'FIGURE_MANIFEST.json').write_text(json.dumps(figs,indent=2))
