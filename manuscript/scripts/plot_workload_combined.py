"""Combine existing distributions and per-chain scatters into a 2-by-3 figure."""
import os,json
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/blocksys-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1];out=root/'figures'
rows=json.loads((out/'hourly_data.json').read_text())
chains=['Ethereum_Mainnet','Optimism','Arbitrum_One'];names=['Ethereum Mainnet','OP Mainnet','Arbitrum One'];colors=['#0072B2','#D55E00','#009E73']
data=[[r for r in rows if r['chain']==chain] for chain in chains]
assert all(len(r)==72 for r in data)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,axs=plt.subplots(2,3,figsize=(9,6),layout='constrained')
for ax,key,label,scale,title in zip(axs[0],['tx_count','failure_rate','block_size_bytes'],['Transactions/hour (thousands)','Failed transactions (%)','Block bytes/hour (MB)'],[1000,1,1e6],['(a) Transaction volume','(b) Failure fraction','(c) Block volume']):
 for rr,name,color in zip(data,names,colors):
  v=np.sort([r[key]/scale for r in rr]);ax.step(v,np.arange(1,73)/72,where='post',label=name,color=color,lw=1.5)
 ax.set(xlabel=label,ylabel='Cumulative probability',title=title,ylim=(0,1.04));ax.grid(alpha=.15)
axs[0,0].legend(fontsize=7,loc='lower right')
for ax,rr,name,letter in zip(axs[1],data,names,['d','e','f']):
 for level,color in zip([1,2,3],colors):
  group=[r for r in rr if r['load']==level];assert len(group)==24
  ax.scatter([r['tx_count']/1000 for r in group],[r['failure_rate'] for r in group],c=color,label=['Low','Medium','High'][level-1],s=24,alpha=.75,edgecolors='white',linewidths=.3)
 ax.set(title=f'({letter}) {name}',xlabel='Transactions/hour (thousands)',ylabel='Failed transactions (%)',ylim=(-1,32));ax.grid(alpha=.15)
axs[1,2].legend(fontsize=8,loc='upper left')
fig.savefig(out/'workload_combined.pdf',bbox_inches='tight');fig.savefig(out/'workload_combined.png',dpi=180,bbox_inches='tight')
print('Six panels generated from unchanged 216 chain-hour observations.')
