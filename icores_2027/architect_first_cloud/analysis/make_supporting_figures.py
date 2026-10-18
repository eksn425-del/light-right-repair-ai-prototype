from pathlib import Path
import os,json,hashlib
os.environ.setdefault('MPLCONFIGDIR','/tmp/architect-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/architect-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[3]; O=Path(__file__).resolve().parent.parent; F=O/'paper/figures'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42})
S='icores_2027/runs/local_ablation_20261016/ablation_summary.csv';d=pd.read_csv(ROOT/S)
fig,ax=plt.subplots(figsize=(6.2,3.2));x=np.arange(len(d));ax.bar(x-.18,d.A_median_end_to_end_seconds,.36,label='A: repeat ray intersections');ax.bar(x+.18,d.B_median_end_to_end_seconds,.36,label='B: reuse blockers (incl. precompute)');ax.set(yscale='log',ylabel='Median elapsed time (s, log scale)',xlabel='Number of rule candidates',xticks=x,xticklabels=d.subset_size);ax.legend(fontsize=7);ax.grid(axis='y',alpha=.15);fig.tight_layout();fig.savefig(F/'runtime_publication.pdf');plt.close(fig)
S2='icores_2027/runs/statistics_20261016/comparison_values.csv';d=pd.read_csv(ROOT/S2);fig,axes=plt.subplots(1,2,figsize=(6.3,3.1),sharex=True,sharey=True)
for ax,(name,g) in zip(axes,d.groupby('comparison_set')):
 ax.scatter(g.two_d_A,g.hb_A,c='#087e8b',s=23);ax.plot([0,410],[0,410],':',c='gray');ax.set(title=name+' (n='+str(len(g))+')',xlabel='2.5D area reduction (m²)');ax.grid(alpha=.15)
axes[0].set_ylabel('HB area reduction (m²)');fig.tight_layout();fig.savefig(F/'agreement_publication.pdf');plt.close(fig)
S3='icores_2027/runs/local_hb_20261016/translation_outcome_comparison.csv';d=pd.read_csv(ROOT/S3);fig,axes=plt.subplots(2,1,figsize=(6.3,4.4),sharex=True);x=np.arange(len(d))
for ax,old,new,label in [(axes[0],'legacy_low_area_reduction_m2','corrected_low_area_reduction_m2','Area reduction (m²)'),(axes[1],'legacy_worsened_point_count','corrected_worsened_point_count','Worsened points')]:
 ax.bar(x-.18,d[old],.36,label='Legacy translated geometry',color='#ba6a63');ax.bar(x+.18,d[new],.36,label='Contained result (C9/C13 reused)',color='#087e8b');ax.set(ylabel=label);ax.grid(axis='y',alpha=.15)
axes[0].legend(fontsize=7);axes[1].set(xticks=x,xticklabels=d.case_id.str.replace(',','/'),yticks=[0,1,2,3,4]);fig.tight_layout();fig.savefig(F/'translation_publication.pdf');plt.close(fig)

p=O/'analysis/figure_provenance.json';m=json.loads(p.read_text())
for name,src in [('runtime_publication',S),('agreement_publication',S2),('translation_publication',S3)]:
 m[name]={'classification':'CLOUD_RECOMPUTED_FROM_ARCHIVE','source':src,'source_sha256':hashlib.sha256((ROOT/src).read_bytes()).hexdigest(),'script':'analysis/make_supporting_figures.py','output_sha256':hashlib.sha256((F/(name+'.pdf')).read_bytes()).hexdigest(),'new_physical_simulation':False}
p.write_text(json.dumps(m,indent=2))
print('Rendered three vector figures from historical aggregate evidence.')
