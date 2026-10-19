from pathlib import Path
import pandas as pd,numpy as np,json,hashlib
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent.parent; o=p/'paper';r=p/'results';(o/'figures').mkdir(exist_ok=True)
e=pd.read_csv(r/'shortlist_evaluation.csv'); lp=pd.read_csv(r/'continuous_worst_regret.csv');ev=pd.read_csv(r/'shortlists_evidence.csv');pdiff=pd.read_csv(r/'paired_differences.csv');st=pd.read_csv(r/'selection_stability.csv')
cs=['ordered','solar70','solar80','A90_solar70','A180_solar70','A270_solar70']; labels=['Ordered','Solar70','Solar80','A90','A180','A270'];ms=['historical10','robust10','AV10','AHV10','coverage10','protected_coverage10'];ml=['Historical','Prior robust','AV','AHV','Coverage','Protected']
def table(name,caption,label,cols,header,rows):
 s='\\begin{table}[tbp]\\centering\\small\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\\toprule\n'+header+'\\\\\\midrule\n'+'\n'.join(' & '.join(row)+'\\\\' for row in rows)+'\n\\bottomrule\\end{tabular}\\end{table}\n';(o/name).write_text(s)
for k,sub in enumerate([cs[:3],cs[3:]],1):
 rows=[]
 for c in sub:
  for m,l in zip(ms,ml):
   a=e[(e.context==c)&(e['set']==m)&(e.split=='test')].iloc[0];v=lp[(lp.context==c)&(lp['set']==m)].iloc[0]
   rows.append([labels[cs.index(c)],l,f'{a.top10_recovery:.5f}',f'{a.utility_winner_coverage:.4f}',f'{a.regret_mean:.6f}',f'{v.continuous_worst_regret:.6f}'])
 table(f'comparison{k}.tex',('Independent test comparison on all 630 candidates.' if k==1 else 'Layered comparison within each filtered universe. Baselines are explicitly adapted; conditional regrets are not full-universe losses.')+' All lists contain exactly ten candidates. The final column is the continuous fixed-set maximum, not the largest sampled test loss.','tab:comparison'+str(k),'llrrrr','Context & List & Recovery & Winner & Mean $R$ & Cont. max $R$',rows)
rows=[]
for c,l in zip(cs,labels):
 a=e[(e.context==c)&(e['set']=='protected_coverage10')&(e.split=='test')].iloc[0];h=e[(e.context==c)&(e['set']=='historical10')&(e.split=='test')].iloc[0]
 dt=pdiff[(pdiff.context==c)&(pdiff.method=='protected_coverage10')&(pdiff.split=='test')&(pdiff.metric=='recovery')].iloc[0];dr=pdiff[(pdiff.context==c)&(pdiff.method=='protected_coverage10')&(pdiff.split=='replication')&(pdiff.metric=='recovery')].iloc[0]
 rows.append([l,f'{dt.mean_difference:.5f}',f'[{dt.mc95_low:.5f}, {dt.mc95_high:.5f}]',f'{dr.mean_difference:.5f}',f'{100*(a.list_A_mean/h.list_A_mean-1):+.2f}\\%',f'{100*(a.list_H_mean/h.list_H_mean-1):+.2f}\\%'])
table('gate_table.tex','Protected minus historical recovery, with paired test Monte Carlo intervals, replication gains and raw list-mean sunlight changes. The frozen replacement threshold is a gain of at least 0.02 in both independent splits.','tab:gates','lrrrrr','Context & Test gain & Test 95\\% MC & Repeat gain & $A$ change & $H$ change',rows)
rows=[]
for c,l in zip(cs,labels):
 a=e[(e.context==c)&(e['set']=='protected_coverage10')&(e.split=='test')].iloc[0];q=st[(st.context==c)&(st.method=='protected_coverage10')&(st.comparison=='block_to_full')]
 rows.append([l,f'{a.list_A_mean:.1f}',f'{a.list_H_mean:.5f}',f'{a.list_V_mean:.1f}',f'{int(a.rule_HB_count)}/10',f'{int(a.translation_checked_count)}/10',f'{q.jaccard.mean():.3f}',f'{q.jaccard.min():.3f}'])
table('evidence_table.tex','Protected-list raw means, archived evidence coverage and training-block membership stability. HB denotes rule-level Honeybee review; translation is a separate geometry evidence stage.','tab:evidence','lrrrrrrr','Context & $A$ & $H$ & $V$ & HB & Trans. & $J$ mean & $J$ min',rows)
rows=[]
for _,a in ev[(ev.context=='solar70')&(ev['set']=='protected_coverage10')].iterrows():
 rows.append([a['pair'].replace(',','/'),str(a.historical_rank),f'{a.A:.0f}',f'{a.H:.5f}',f'{a.V:.1f}','Yes' if a.HB_review_status=='ARCHIVED_RULE_HB_REVIEWED' else 'Missing','Yes' if a.translation_status!='NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION' else 'Missing'])
table('shortlist_table.tex','Illustrative Solar70 protected list, not a newly approved replacement. Membership differs from Historical10 by C24/C35 replacing C9/C27. Position follows the selection record, not a final architectural recommendation.','tab:shortlist','lrrrrll','Pair & Old rank & $A$ & $H$ & $V$ & Rule HB & Trans.',rows)
plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'ps.fonttype':42})
fig,axs=plt.subplots(1,2,figsize=(8.3,3.3),layout='constrained')
x=np.arange(6);g=[];gr=[]
for c in cs:
 for target,split in [(g,'test'),(gr,'replication')]:
  q=e[(e.context==c)&(e.split==split)].set_index('set');target.append(100*(q.loc['protected_coverage10','top10_recovery']-q.loc['historical10','top10_recovery']))
axs[0].bar(x-.18,g,.36,label='Test');axs[0].bar(x+.18,gr,.36,label='Replication');axs[0].axhline(2,color='black',ls='--',label='Frozen threshold');axs[0].set_xticks(x,labels,rotation=35);axs[0].set_ylabel('Recovery gain (percentage points)');axs[0].legend(fontsize=7)
for m,l in [('historical10','Historical'),('protected_coverage10','Protected')]:
 vals=[e[(e.context==c)&(e.split=='test')&(e['set']==m)].iloc[0].utility_winner_coverage*100 for c in cs];axs[1].plot(x,vals,'o-',label=l)
axs[1].set_xticks(x,labels,rotation=35);axs[1].set_ylim(80,102);axs[1].set_ylabel('Test winner coverage (%)');axs[1].legend(fontsize=8)
fig.savefig(o/'figures/recovery_and_winners.pdf');fig.savefig(o/'figures/recovery_and_winners.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7,3),layout='constrained')
for i,(m,l) in enumerate([('historical10','Historical'),('robust10','Prior robust'),('protected_coverage10','Protected')]):
 v=[e[(e.context==c)&(e.split=='test')&(e['set']==m)].iloc[0].list_A_mean for c in cs];ax.bar(x+(i-1)*.25,v,.25,label=l)
ax.set_xticks(x,labels);ax.set_ylabel('Mean shortlist A benefit (m²)');ax.legend(ncol=3,fontsize=8);fig.savefig(o/'figures/solar_benefit.pdf');fig.savefig(o/'figures/solar_benefit.png',dpi=180);plt.close(fig)
