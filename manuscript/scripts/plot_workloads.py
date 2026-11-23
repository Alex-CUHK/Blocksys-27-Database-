"""Rebuild five figures from 72 probability dates, without event supplements."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/blocksys-mpl')
import argparse,csv,gzip,json,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);a=p.parse_args()
out=Path(__file__).resolve().parents[1]/'figures';out.mkdir(exist_ok=True)
cal=[r for r in csv.DictReader((a.source/'sampling_calendar.csv').open()) if r['role']=='probability_sample'];assert len(cal)==72
chains=['Ethereum_Mainnet','Optimism','Arbitrum_One'];names=['Ethereum Mainnet','OP Mainnet','Arbitrum One'];colors=['#0072B2','#D55E00','#009E73'];data=[];manifest=[]
fields=['gas_used','tx_count','failed_tx_count','block_size_bytes','contract_creation_tx_count','base_fee_per_gas']+['tx_type_'+x+'_count' for x in ['0','1','2','3','other']]
for chain in chains:
 rows=[]
 for c in cal:
  f=a.source/chain/(c['date']+'.csv.gz');s={k:0 for k in fields};n=0
  with gzip.open(f,'rt') as h:
   for r in csv.DictReader(h):
    n+=1
    for k in fields:
     assert r[k]!='',(f,k)
     s[k]+=int(r[k])
  assert s['failed_tx_count']<=s['tx_count']
  assert sum(s['tx_type_'+x+'_count'] for x in ['0','1','2','3','other'])==s['tx_count']
  s.update(chain=chain,date=c['date'],phase=int(c['phase']),blocks=n)
  s['base_fee_per_gas']/=n;s['failure_rate']=100*s['failed_tx_count']/s['tx_count'];rows.append(s)
  manifest.append(dict(file=str(f.relative_to(a.source)),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
 for phase in range(1,13):
  group=sorted([r for r in rows if r['phase']==phase],key=lambda r:(r['gas_used'],r['date']));assert len(group)==6
  for i,r in enumerate(group):r['load']=i//2+1
 data.append(rows)
(out/'hourly_data.json').write_text(json.dumps(sum(data,[]),indent=2)+'\n');(out/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
def save(fig,name):
 fig.savefig(out/(name+'.pdf'),bbox_inches='tight');fig.savefig(out/(name+'.png'),dpi=160,bbox_inches='tight');plt.close(fig)
fig,axs=plt.subplots(2,1,figsize=(7,5),sharex=True,layout='constrained')
for rows,name,color in zip(data,names,colors):
 for ax,key,scale in zip(axs,['tx_count','failure_rate'],[1000,1]):
  vals=[np.array([r[key]/scale for r in rows if r['phase']==p]) for p in range(1,13)]
  ax.plot(range(1,13),[np.median(v) for v in vals],'-o',ms=3,label=name,color=color)
  ax.fill_between(range(1,13),[np.percentile(v,25) for v in vals],[np.percentile(v,75) for v in vals],alpha=.12,color=color)
axs[0].set_ylabel('Transactions per hour (thousands)');axs[1].set_ylabel('Failed transactions (%)');axs[1].set_xlabel('Three-month phase (1 = Nov 2023 to Feb 2024)');axs[1].set_xticks(range(1,13));axs[0].legend(fontsize=8,ncol=3);save(fig,'phase_trends')
fig,axs=plt.subplots(1,3,figsize=(8,3),layout='constrained')
for ax,key,label,scale in zip(axs,['tx_count','failure_rate','block_size_bytes'],['Transactions/hour (thousands)','Failed transactions (%)','Block bytes/hour (MB)'],[1000,1,1e6]):
 for rows,name,color in zip(data,names,colors):
  v=np.sort([r[key]/scale for r in rows]);ax.step(v,np.arange(1,73)/72,where='post',label=name,color=color)
 ax.set_xlabel(label);ax.set_ylabel('Empirical cumulative probability');ax.grid(alpha=.15)
axs[0].legend(fontsize=7);save(fig,'hourly_distributions')
fig,axs=plt.subplots(1,3,figsize=(8,3),layout='constrained',sharey=True)
for ax,rows,name in zip(axs,data,names):
 for level,color in zip([1,2,3],colors):
  group=[r for r in rows if r['load']==level];ax.scatter([r['tx_count']/1000 for r in group],[r['failure_rate'] for r in group],c=color,label=['Low','Medium','High'][level-1],s=22,alpha=.7)
 ax.set_title(name);ax.set_xlabel('Transactions/hour (thousands)');ax.grid(alpha=.15)
axs[0].set_ylabel('Failed transactions (%)');axs[-1].legend(fontsize=7);save(fig,'load_failure')
fig,axs=plt.subplots(3,1,figsize=(7,6),layout='constrained',sharex=True)
for ax,rows,name in zip(axs,data,names):
 bottom=np.zeros(12)
 for typ,color in zip(['0','1','2','3','other'],['#0072B2','#CC79A7','#009E73','#E69F00','#777777']):
  v=np.array([100*sum(r['tx_type_'+typ+'_count'] for r in rows if r['phase']==p)/sum(r['tx_count'] for r in rows if r['phase']==p) for p in range(1,13)])
  ax.bar(range(1,13),v,bottom=bottom,label='Type '+typ,color=color);bottom+=v
 ax.set_ylabel('Share (%)');ax.set_title(name,loc='left');ax.set_ylim(0,100)
axs[0].legend(ncol=5,fontsize=7,loc='upper center',bbox_to_anchor=(.5,1.4));axs[-1].set_xticks(range(1,13));axs[-1].set_xlabel('Three-month phase');save(fig,'transaction_mix')
keys=['gas_used','tx_count','failed_tx_count','block_size_bytes','contract_creation_tx_count','base_fee_per_gas'];labels=['Gas','Tx','Failed','Bytes','Create','Fee']
fig,axs=plt.subplots(1,3,figsize=(9,3.4),layout='constrained')
for ax,rows,name in zip(axs,data,names):
 c=np.corrcoef([[r[k] for r in rows] for k in keys]);im=ax.imshow(c,vmin=-1,vmax=1,cmap='RdBu_r')
 ax.set_xticks(range(6),labels,rotation=45,ha='right');ax.set_yticks(range(6),labels);ax.set_title(name)
 for i in range(6):
  for j in range(6):ax.text(j,i,f'{c[i,j]:.2f}',ha='center',va='center',fontsize=6,color='white' if abs(c[i,j])>.65 else 'black')
fig.colorbar(im,ax=axs,shrink=.7,label='Pearson r');save(fig,'correlations')
print('Generated five figures from',sum(len(x) for x in data),'chain-hours')
