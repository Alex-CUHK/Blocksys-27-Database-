"""Exhaustive training-only placement sweep, scored on held-out proxy matrices."""
import os,csv,json,itertools,hashlib
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/blocksys-weighted-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];O=R/'figures'
data=json.loads((O/'weighted_matrix_inputs.json').read_text());names=data['modules']
chains=['Ethereum_Mainnet','Optimism','Arbitrum_One'];labels=['Ethereum','OP Mainnet','Arbitrum One'];colors=['#0072B2','#D55E00','#009E73']
perms=np.array(list(itertools.permutations(range(8))))
flat=np.array([(x,y,0) for y in range(2) for x in range(4)])
stack=np.array([(x,y,z) for z in range(2) for y in range(2) for x in range(2)])
pairs=[(i,j) for i in range(8) for j in range(i+1,8) if any(m['matrix'][i][j] for m in data['observations'])]
def distances(slots):
 c=slots[perms]
 return (np.array([2*np.abs(c[:,i,:2]-c[:,j,:2]).sum(axis=1) for i,j in pairs]).T,np.array([2*np.abs(c[:,i,2]-c[:,j,2]) for i,j in pairs]).T)
D,_=distances(flat);H,V=distances(stack)
ratios=np.linspace(0,4,161);report=[];summary=[]
for chain in chains:
 obs=[m for m in data['observations'] if m['chain']==chain]
 train=np.mean([m['matrix'] for m in obs if m['split']=='train'],axis=0)
 test=np.array([m['matrix'] for m in obs if m['split']=='test'])
 vtrain=np.array([train[i,j] for i,j in pairs]);vtest=np.array([[m[i,j] for i,j in pairs] for m in test]);avg=vtest.mean(axis=0)
 i2=int((D@vtrain).argmin());base=float(D[0]@avg);opt=float(D[i2]@avg)
 th=H@vtrain;tv=V@vtrain;ids=np.array([int((th+r*tv).argmin()) for r in ratios])
 hs=H[ids]@avg;vs=V[ids]@avg;cost=hs+ratios*vs
 records=[dict(lambda_value=float(r),cost=float(c),horizontal=float(h),vertical=float(r*v),change_percent=float(100*(c/opt-1)),permutation=perms[k].tolist()) for r,c,h,v,k in zip(ratios,cost,hs,vs,ids)]
 k1=ids[40];hour2=vtest@D[i2];hour3=vtest@(H[k1]+V[k1])
 rec=dict(chain=chain,baseline_2d=base,optimized_2d=opt,train_mean_matrix=train.tolist(),test_dates=[m['date'] for m in obs if m['split']=='test'],hourly_cost_ratio_lambda1=(hour2/hour3).tolist(),sweep=records)
 report.append(rec)
 with (O/f'{chain}_training_mean_matrix.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['module']+names)
  for n,row in zip(names,train):w.writerow([n]+list(row))
 c1=records[40]['cost'];c025=records[10]['cost']
 summary.append(dict(network=chain,baseline_2d=base,optimized_2d=opt,two_layer_lambda1=c1,planar_reduction_percent=100*(1-opt/base),three_d_reduction_vs_opt_percent=100*(1-c1/opt),three_d_reduction_vs_baseline_percent=100*(1-c1/base),cost_ratio_opt_to_3d_lambda1=opt/c1,cost_ratio_opt_to_3d_lambda025=opt/c025))
 # Compare regenerated sweep anchors to the existing independently verified experiment.
 saved=list(csv.DictReader((O/'weighted_sensitivity_results.csv').open()))
 for r in saved:
  if r['chain']==chain and r['mode']=='functional' and float(r['scale'])==1 and r['split']=='test':
   k=round(float(r['lambda_value'])/.025)
   assert np.isclose(records[k]['cost'],float(r['optimized_3d']))
   assert np.isclose(opt,float(r['optimized_2d']))
(O/'weighted_layout_sweep.json').write_text(json.dumps(dict(input_sha256=hashlib.sha256((O/'weighted_matrix_inputs.json').read_bytes()).hexdigest(),placements=40320,results=report,summary=summary),indent=2)+'\n')
with (O/'weighted_layout_summary.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,axs=plt.subplots(2,2,figsize=(9,7),layout='constrained')
ax=axs[0,0]
for d,label,color in zip(report,labels,colors):
 ax.plot(ratios,[v['cost'] for v in d['sweep']],color=color,label=label)
 ax.axhline(d['optimized_2d'],color=color,ls='--',lw=.9)
 ax.axhline(d['baseline_2d'],color=color,ls=':',lw=.9)
ax.set(title='(a) Mean test cost of trained placements',xlabel=r'Vertical cost ratio $\lambda$',ylabel='Dimensionless weighted cost')
ax.legend(fontsize=7,loc='upper left');ax.text(.98,.03,'Solid: two-layer\nDashed: optimized 2D\nDotted: baseline 2D',transform=ax.transAxes,ha='right',fontsize=7)
ax=axs[0,1]
for d,label,color in zip(report,labels,colors):ax.plot(ratios,[-v['change_percent'] for v in d['sweep']],color=color,label=label)
ax.axhline(0,color='black',lw=.7);ax.set(title='(b) Reduction relative to optimized 2D',xlabel=r'Vertical cost ratio $\lambda$',ylabel='Mean cost reduction (%)');ax.legend(fontsize=7)
ax=axs[1,0];xx=np.arange(4);width=.23
for j,(d,label,color) in enumerate(zip(report,labels,colors)):
 rr=[d['sweep'][k] for k in [10,40,80,160]];x=xx+(j-1)*width
 h=np.array([v['horizontal'] for v in rr]);v=np.array([v['vertical'] for v in rr])
 ax.bar(x,h,width,color=color,label=label)
 ax.bar(x,v,width,bottom=h,color=color,alpha=.35,hatch='///',edgecolor=color)
ax.set(title='(c) Two-layer cost components on test hours',xticks=xx,xticklabels=['0.25','1','2','4'],xlabel=r'Vertical cost ratio $\lambda$',ylabel='Mean weighted cost')
ax.set_ylim(0,110)
ax.legend(fontsize=7,loc='upper left');ax.text(.98,.98,'Solid: planar\nHatched: vertical',transform=ax.transAxes,ha='right',va='top',fontsize=7)
ax=axs[1,1]
for d,label,color in zip(report,labels,colors):
 vals=np.sort(d['hourly_cost_ratio_lambda1']);ax.step(vals,np.arange(1,37)/36,where='post',color=color,label=label)
ax.axvline(1,color='black',ls='--',lw=.7);ax.set(title=r'(d) Held-out hourly cost ratios at $\lambda=1$',xlabel='Optimized 2D cost / two-layer cost',ylabel='Empirical cumulative probability');ax.legend(fontsize=7,loc='lower right')
for ax in axs.flat:ax.grid(alpha=.16);ax.set_axisbelow(True)
for ext in ['png','pdf']:fig.savefig(O/f'weighted_layout_cost.{ext}',dpi=180,bbox_inches='tight')
print(json.dumps(summary,indent=2))
