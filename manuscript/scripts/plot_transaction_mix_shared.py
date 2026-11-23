"""One common axis, three stacked bars per phase, from audited hourly aggregates."""
import os,json,csv
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/blocksys-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];rows=json.loads((R/'figures/hourly_data.json').read_text())
chains=['Ethereum_Mainnet','Optimism','Arbitrum_One'];types=['0','1','2','3','other'];colors=['#1f77b4','#cc79a7','#209c79','#e69f00','#808080']
fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
records=[]
for j,chain in enumerate(chains):
 phase=np.arange(1,13);x=phase+(j-1)*.26;bottom=np.zeros(12)
 for t,color in zip(types,colors):
  vals=[]
  for p in phase:
   rr=[r for r in rows if r['chain']==chain and r['phase']==int(p)]
   assert len(rr)==6
   n=sum(r['tx_count'] for r in rr);v=100*sum(r[f'tx_type_{t}_count'] for r in rr)/n;vals.append(v)
   records.append(dict(chain=chain,phase=int(p),type=t,share_percent=v))
  ax.bar(x,vals,width=.235,bottom=bottom,color=color,label=('Type '+t) if j==0 else None)
  bottom+=vals
 assert np.allclose(bottom,100)
 for xx in x:ax.text(xx,-3,['E','O','A'][j],ha='center',va='top',fontsize=7)
ax.set(xlim=(.45,12.55),ylim=(0,100),xticks=range(1,13),ylabel='Transaction share (%)',xlabel='Three month phase')
ax.tick_params(axis='x',pad=17,length=0)
ax.legend(loc='upper center',bbox_to_anchor=(.5,1.16),ncol=5,frameon=False,fontsize=9)
ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True);ax.spines[['top','right']].set_visible(False)
for ext in ['pdf','png']:fig.savefig(R/f'figures/transaction_mix.{ext}',dpi=180,bbox_inches='tight')
with (R/'figures/transaction_mix_shared.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
print('Verified 36 phase/network groups each sum to 100 percent, 216 source hours.')
