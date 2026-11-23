"""Exhaustive static-topology sensitivity experiment. No real-trace performance claims."""
import os,json,itertools
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/blocksys-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1];out=root/'figures'
arch=json.loads((out/'layout_architecture.json').read_text());A=np.array(arch['connection_matrix'])
assert np.array_equal(A,A.T) and A.sum()==24 and np.trace(A)==0
perms=np.array(list(itertools.permutations(range(8))));assert len(perms)==40320
flat=np.array([(x,y,0) for y in range(2) for x in range(4)])
stack=np.array([(x,y,z) for z in range(2) for y in range(2) for x in range(2)])
def components(slots):
 c=slots[perms];h=np.zeros(len(c));v=h.copy()
 for i,j in zip(*np.nonzero(A)):
  h+=A[i,j]*np.abs(c[:,i,:2]-c[:,j,:2]).sum(axis=1)
  v+=A[i,j]*np.abs(c[:,i,2]-c[:,j,2])
 return h,v
planar,_=components(flat);h,v=components(stack)
baseline=float(planar[0]);best=float(planar.min());ratios=np.linspace(0,4,161)
costs=h[:,None]+v[:,None]*ratios[None,:];ids=costs.argmin(axis=0);opt=costs[ids,np.arange(len(ratios))]
# Exact crossing of the lower envelope against the planar optimum.
assert (v>0).all()
threshold=float(np.max((best-h)/v))
selected=[.25,1,2,4];records=[]
for r,expected in zip(selected,[21,30,38,54]):
 c=h+r*v;k=int(c.argmin());assert c[k]==expected
 records.append(dict(r=r,cost=float(c[k]),horizontal=float(h[k]),vertical=float(r*v[k]),coordinates={m:stack[perms[k,i]].tolist() for i,m in enumerate(arch['modules'])}))
assert baseline==44 and best==32
report=dict(provenance='ASSUMED_STATIC_ARCHITECTURE_NOT_EVM_PERFORMANCE',placements_per_grid=len(perms),baseline_planar=baseline,optimized_planar=best,exact_model_crossing=threshold,selected=records,sweep=[dict(r=float(r),optimum=float(o),median=float(np.median(costs[:,i])),p10=float(np.percentile(costs[:,i],10)),p90=float(np.percentile(costs[:,i],90))) for i,(r,o) in enumerate(zip(ratios,opt))])
(out/'layout_sensitivity.json').write_text(json.dumps(report,indent=2)+'\n')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,axs=plt.subplots(2,2,figsize=(8.4,6.4),layout='constrained')
ax=axs[0,0];ax.fill_between(ratios,np.percentile(costs,10,axis=0),np.percentile(costs,90,axis=0),color='#e7e7e7',label='Two-layer P10 to P90')
ax.plot(ratios,np.median(costs,axis=0),color='#888888',ls=':',label='Two-layer median')
ax.plot(ratios,opt,color='#D55E00',lw=2,label='Two-layer optimum')
ax.axhline(best,color='#0072B2',ls='--',label='Planar optimum (32)');ax.axhline(baseline,color='#555555',ls='-.',label='Planar baseline (44)')
ax.set(title='(a) Placement sensitivity',xlabel='Vertical cost ratio r',ylabel='Weighted cost');ax.legend(fontsize=7,loc='upper left')
ax=axs[0,1];gain=100*(best-opt)/best;ax.plot(ratios,gain,color='#D55E00',lw=2)
ax.fill_between(ratios,gain,0,where=gain>=0,color='#009E73',alpha=.15);ax.fill_between(ratios,gain,0,where=gain<0,color='#D55E00',alpha=.12)
ax.axhline(0,color='#555555',lw=.8);ax.axvline(threshold,color='#555555',ls='--');ax.annotate(f'Model crossing r = {threshold:g}',(threshold,0),xytext=(1.45,25),arrowprops=dict(arrowstyle='->'),fontsize=8)
ax.set(title='(b) Benefit relative to optimized planar',xlabel='Vertical cost ratio r',ylabel='Cost reduction (%)')
ax=axs[1,0];pos=np.arange(4);hh=[r['horizontal'] for r in records];vv=[r['vertical'] for r in records]
ax.bar(pos,hh,color='#0072B2',label='Planar component H');ax.bar(pos,vv,bottom=hh,color='#E69F00',label='Vertical component rV')
for i,r in enumerate(records):ax.text(i,r['cost']+1,f"{r['cost']:g}",ha='center',fontsize=9)
ax.axhline(best,color='#555555',ls='--',lw=1);ax.set(title='(c) Optimal two-layer cost components',xlabel='Vertical cost ratio r',ylabel='Weighted cost',xticks=pos,xticklabels=selected,ylim=(0,65));ax.legend(fontsize=8)
ax=axs[1,1]
for vals,label,color in [(planar,'Planar','#0072B2'),(h+.25*v,'Two-layer r = 0.25','#009E73'),(h+v,'Two-layer r = 1','#D55E00'),(h+2*v,'Two-layer r = 2','#CC79A7')]:
 u,n=np.unique(vals,return_counts=True);ax.step(u,np.cumsum(n)/len(vals),where='post',label=label,color=color)
ax.set(title='(d) Exhaustive placement distributions',xlabel='Weighted cost',ylabel='Fraction of placements');ax.legend(fontsize=8,loc='lower right')
for ax in axs.flat:ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.savefig(out/'layout_cost.pdf',bbox_inches='tight');fig.savefig(out/'layout_cost.png',dpi=180,bbox_inches='tight')
print('Verified all 40,320 placements per grid. Model crossing:',threshold)
