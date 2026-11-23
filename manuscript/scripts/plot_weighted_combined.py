"""Replot saved supplementary results as three upper and three lower panels."""
from pathlib import Path
import csv, os
os.environ.setdefault('MPLCONFIGDIR','/tmp/blocksys-weighted-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'figures/weighted_sensitivity_results.csv').open()))
chains=['Ethereum_Mainnet','Optimism','Arbitrum_One']
names=['Ethereum Mainnet','OP Mainnet','Arbitrum One']
plt.rcParams.update({'font.size':9,'axes.titlesize':10,'pdf.fonttype':42})
fig,axs=plt.subplots(2,3,figsize=(10,6.3),sharey=True,layout='constrained')
for col,(chain,name) in enumerate(zip(chains,names)):
 rr=[r for r in rows if r['chain']==chain and r['split']=='test']
 ax=axs[0,col]
 for mode,scale,label,color,style,marker in [('functional',0,'Static A','#555555','-', 'o'),('functional',1,'Functional proxy W','#0072B2','-', 's'),('uniform',1,'Uniform scaling','#D55E00','--','x')]:
  data=sorted([r for r in rr if r['mode']==mode and float(r['scale'])==scale],key=lambda r:float(r['lambda_value']))
  ax.plot([float(r['lambda_value']) for r in data],[float(r['change_percent']) for r in data],label=label,color=color,ls=style,marker=marker,ms=4)
 ax.set(title=f'({chr(97+col)}) {name}',xlabel=r'Vertical cost ratio $\lambda$',xticks=[.25,1,2,4])
 ax=axs[1,col]
 for lam,color in zip([.25,1,2,4],['#0072B2','#009E73','#E69F00','#CC79A7']):
  data=sorted([r for r in rr if r['mode']=='functional' and float(r['lambda_value'])==lam],key=lambda r:float(r['scale']))
  ax.plot([float(r['scale']) for r in data],[float(r['change_percent']) for r in data],'-o',color=color,label=rf'$\lambda={lam:g}$',ms=4)
 ax.set(title=f'({chr(100+col)}) {name}',xlabel='Mapping coefficient scale s',xticks=[0,.5,1,2])
for ax in axs.flat:
 ax.axhline(0,color='black',lw=.6)
 ax.grid(alpha=.18)
 ax.spines[['top','right']].set_visible(False)
for ax in axs[:,0]:ax.set_ylabel('3D cost change vs optimized 2D (%)')
axs[0,0].legend(fontsize=8,loc='upper left')
axs[1,0].legend(fontsize=8,loc='center left',ncol=2)
for ext in ['pdf','png']:fig.savefig(ROOT/f'figures/weighted_combined.{ext}',dpi=180,bbox_inches='tight')
