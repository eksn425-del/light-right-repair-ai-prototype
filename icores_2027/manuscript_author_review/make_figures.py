from pathlib import Path
import csv,json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'evidence/icores_2027/runs'
plt.rcParams.update({'font.size':9,'axes.titlesize':10,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':8,'pdf.fonttype':42,'ps.fonttype':42,'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
records=[]
def rows(path):return list(csv.DictReader(path.open()))
def finish(fig,name,source,notes):
 fig.savefig(ROOT/'figures'/f'{name}.pdf',metadata={'Title':name,'Author':'','CreationDate':None,'ModDate':None})
 fig.savefig(ROOT/'figures'/f'{name}.svg',metadata={'Date':None,'Creator':'Matplotlib'})
 fig.savefig(ROOT/'figures'/f'{name}.png',dpi=300)
 records.append({'figure':name,'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'script':'make_figures.py','notes':notes,'change':'Publication-size replot of unchanged frozen aggregate source; no new experiment or inferred data.'})
 plt.close(fig)
p=BASE/'local_ablation_20261016/ablation_summary.csv';r=rows(p)
x=np.array([int(a['subset_size']) for a in r]);a=[float(v['A_median_end_to_end_seconds']) for v in r];b=[float(v['B_median_end_to_end_seconds']) for v in r]
f,ax=plt.subplots(figsize=(4.8,3.05),layout='constrained')
ax.plot(x,a,'o-',color='#174b70',label='A: repeated intersection');ax.plot(x,b,'s--',color='#c66b20',label='B: reuse, including precompute')
ax.set_xscale('log');ax.set_yscale('log');ax.set_xticks(x,[str(i) for i in x]);ax.set_xlabel('Number of candidates');ax.set_ylabel('End-to-end runtime (s)');ax.legend(loc='upper left');ax.grid(which='major',alpha=.2);ax.set_ylim(10,50000)
finish(f,'runtime_publication',p,'Three repeats per method and size; medians; both axes logarithmic.')
p=BASE/'statistics_20261016/comparison_values.csv';r=rows(p)
f,axs=plt.subplots(1,2,figsize=(4.8,2.7),layout='constrained',sharex=True,sharey=True)
for ax,c,title in zip(axs,['curated23','heldout20'],['Curated (n = 23)','Coverage (n = 20)']):
 rr=[a for a in r if a['comparison_set']==c];ax.plot([0,410],[0,410],color='.55',lw=.8,zorder=0);ax.scatter([float(v['hb_A']) for v in rr],[float(v['two_d_A']) for v in rr],s=22,facecolors='none',edgecolors='#174b70',linewidths=.9);ax.set_title(title);ax.set_aspect('equal');ax.set_xlim(-15,415);ax.set_ylim(-15,415);ax.set_xticks([0,200,400]);ax.set_yticks([0,200,400]);ax.set_xlabel('Honeybee A (m²)');ax.grid(alpha=.15)
axs[0].set_ylabel('Screening A (m²)')
finish(f,'agreement_publication',p,'Frozen aggregate comparison; overplotted coincident values retained without jitter; identity line only.')
p=BASE/'local_hb_20261016/translation_outcome_comparison.csv';r=rows(p)
f,axs=plt.subplots(2,1,figsize=(4.8,4.1),layout='constrained',sharey=True)
y=np.arange(len(r)); labels=[v['case_id'].replace(',','/')+('*' if v['corrected_result_reuses_unchanged_legacy']=='True' else '') for v in r]
for ax,keys,xlab in zip(axs,[('legacy_low_area_reduction_m2','corrected_low_area_reduction_m2'),('legacy_worsened_point_count','corrected_worsened_point_count')],['Low-sun-area reduction (m²)','Worsened receiving points']):
 aa=np.array([float(v[keys[0]]) for v in r]);bb=np.array([float(v[keys[1]]) for v in r]);ax.barh(y-.17,aa,height=.32,color='#b9cad8',edgecolor='#174b70',label='Historical');ax.barh(y+.17,bb,height=.32,color='#c66b20',label='Contained / unchanged*');ax.set_yticks(y,labels);ax.set_xlabel(xlab);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
 for yy,v in zip(y-.17,aa):ax.text(v+(3 if keys[0].startswith('legacy_low') else .05),yy,f'{v:g}',va='center',fontsize=8)
 for yy,v in zip(y+.17,bb):ax.text(v+(3 if keys[0].startswith('legacy_low') else .05),yy,f'{v:g}',va='center',fontsize=8)
axs[0].invert_yaxis();axs[0].set_xlim(0,400);axs[1].set_xlim(0,4.8);axs[1].set_xticks(range(5));axs[0].legend(loc='lower right',fontsize=7.5)
finish(f,'translation_publication',p,'Four new corrections; *C9/C13 reuses unchanged historical result. Net union-volume reductions are not matched.')
(ROOT/'figures/PUBLICATION_FIGURE_MANIFEST.json').write_text(json.dumps({'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'figures':records},indent=2))
