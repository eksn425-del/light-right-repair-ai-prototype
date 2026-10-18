from pathlib import Path
import pandas as pd, shutil
p=Path(__file__).resolve().parent;r=p.parent/'results'
def table(name,caption,label,cols,head,rows,foot=''):
 (p/name).write_text('\\begin{table}[tbp]\\caption{'+caption+'}\\label{'+label+'}\\centering\n\\small\n\\begin{tabular}{'+cols+'}\\toprule\n'+head+r'\\\midrule'+'\n'+'\n'.join(' & '.join(row)+r'\\' for row in rows)+'\n\\bottomrule\\end{tabular}\n'+foot+'\n\\end{table}\n')
e=pd.read_csv(r/'shortlist_evaluation.csv');d=e[e.split.eq('test')]
rows=[]
for sp in ['full','ordered','local']:
 for s in ['historical10','AV10','AHV10','robust10']:
  x=d[(d.space==sp)&(d.set==s)].iloc[0]
  rows.append([sp,{'historical10':'Historical10','robust10':'Robust10'}.get(s,s),*[f'{x[k]:.6f}' for k in ['regret_mean','regret_p95']],f'{x.winner_coverage:.5f}',f'{x.top10_recovery:.5f}'])
table('evaluation_table.tex','Independent test evaluation, 20,000 weights per space and ten candidates per set. Recovery is the mean fraction of each preference-specific top ten retained.','tab:evaluation','llrrrr','Space & Set & Mean regret & 95th pct. & Winner & Recovery',rows)
a=pd.read_csv(r/'continuous_worst_regret.csv');rows=[]
for s in ['historical10','AV10','AHV10','robust10','AV_full','AHV_full']:
 x=a[(a.space=='full')&(a.set==s)].iloc[0]; rows.append([s.replace('_',' '),str(int(d[d.set==s].iloc[0]['k'])),f'{x.continuous_worst_regret:.6f}',f'{x.grid_max:.6f}','0','0'])
table('audit_table.tex','Continuous fixed-set worst regret, with full-space grid maxima. All candidate-specific linear programs succeeded. Full fronts are unequal-budget references.','tab:audit','lrrrrr','Set & Size & Full LP & Full grid & Ordered LP & Local LP',rows)
z=pd.read_csv(r/'shortlists_evidence.csv');rows=[]
for s,fn,lab,caption in [('historical10','historical_table.tex','tab:historical','Historical top ten in immutable score order. All have archived rule-level Honeybee review. C indicates a corrected translated design; U an unchanged contained result reused; -- missing translation.'),('robust10','robust_table.tex','tab:robust','Robust10 in greedy addition order. HB denotes archived rule review (Y) or missing review (--); translation C means an archived contained correction and -- means missing verification. Historical rank is retained for comparison.')]:
 rows=[]
 for _,x in z[z.set==s].iterrows():
  tr='C' if 'CORRECTION' in x.design_translation_status else ('U' if 'UNCHANGED' in x.design_translation_status else '--')
  if s=='historical10':rows.append([str(x.position),x.pair.replace(',','/'),f'{x.A:.0f}',f'{x.H:.5f}',f'{x.V:.1f}',f'{x.historical_score:.5f}',tr])
  else:rows.append([str(x.position),x.pair.replace(',','/'),str(x.historical_rank),f'{x.A:.0f}',f'{x.H:.5f}',f'{x.V:.1f}','Y' if x.HB_cohort!='MISSING' else '--',tr])
 table(fn,caption,lab,'rlrrrrc' if s=='historical10' else 'rlrrrrcc',r'Rank & Pair & $A$ (m$^2$) & $H$ (h) & $V$ (m$^3$) & $S$ & Trans.' if s=='historical10' else r'Step & Pair & Hist. & $A$ & $H$ (h) & $V$ (m$^3$) & HB & Trans.',rows)
(p/'candidate_tables.tex').write_text('\\input{historical_table.tex}\n\\input{robust_table.tex}\n')
b=pd.read_csv(r/'all630_rank_acceptability.csv');rows=[]
for pair in ['C9,C24','C9,C15','C12,C24','C25,C29','C24,C35','C13,C15']:
 for sp in ['full','ordered','local']:
  x=b[(b.pair==pair)&(b.space==sp)&(b.split=='test')].iloc[0]
  rows.append([pair.replace(',','/'),sp,f'{x.winner_acceptability:.4f}',f'{x.top10_acceptability:.4f}',f'{x.average_rank:.2f}',str(x.worst_observed_rank)])
table('rank_table.tex','Selected rank statistics from all 630 candidates on independent test weights. Worst means worst observed rank, not a continuous bound. Acceptability is conditional on the declared weight distribution.','tab:ranks','llrrrr','Pair & Space & Winner & Top ten & Mean rank & Worst',rows)
x=e[(e.space=='full')&(e.split=='replication')];h=x[x.set=='historical10'].iloc[0];q=x[x.set=='robust10'].iloc[0]
(p/'replication_text.tex').write_text(f'Independent full-space replication gives mean regret {h.regret_mean:.6f} for Historical10 and {q.regret_mean:.6f} for Robust10, with winner coverage {h.winner_coverage:.5f} and {q.winner_coverage:.5f}, respectively. The paired robust-minus-historical mean regret difference on the test split is $-0.010705$, with a conditional Monte Carlo 95\\% interval $[-0.011132,-0.010279]$; replication gives $-0.011296$ and $[-0.011736,-0.010855]$. Ordered and local replication retain zero regret for both sets. Thus the prespecified criterion of no larger mean and 95th-percentile regret in every space, with a strict improvement somewhere, is met. This is improvement in the full space and equality in the other two, not strict improvement everywhere.\n')
for f in ['acceptability_heatmap.pdf','continuous_regret.pdf','regret_comparison.pdf']:
 shutil.copy2(p.parent/'figures'/f,p/'figures'/f)
