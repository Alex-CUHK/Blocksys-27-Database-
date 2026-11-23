"""Real-observation proxy weighting with fixed topology and held-out date evaluation."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/blocksys-weighted-mpl')
import argparse,csv,gzip,json,hashlib,itertools,random,datetime,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import experiment as old
ROOT=Path(__file__).resolve().parent
CHAINS=['Ethereum_Mainnet','Optimism','Arbitrum_One']
FEATURES=['tx_count','contract_creation_tx_count','block_size_bytes']
RESERVED=['sload_count','sstore_count','committed_storage_changes','trie_node_reads','trie_node_writes','keccak_count','trie_dependency_depth','rtl_comm_bytes']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def csvout(p,rows):
 with p.open('w',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(source,out):
 out.mkdir(parents=True,exist_ok=True);cfg=json.loads((out/'mapping_config.yaml').read_text());config_hash=sha(out/'mapping_config.yaml')
 original={str(p):sha(p) for p in (ROOT/'outputs').glob('*') if p.is_file()}
 A=np.array(json.loads((ROOT/'outputs/architecture.json').read_text())['connection_matrix']);N=old.NAMES
 assert [tuple(e['pair']) for e in cfg['edges']]==old.EDGES
 # Execute original functions without invoking their file-writing main entry point.
 baseline=old.layout(A.tolist());expected=[21,30,38,54]
 assert baseline['baseline_2d']['cost']==44 and baseline['optimized_2d']['cost']==32
 assert [x['cost'] for x in baseline['three_dimensional_sensitivity']]==expected
 dump(out/'static_reproduction.json',baseline)
 calendar=list(csv.DictReader((source/'sampling_calendar.csv').open()));cal=[r for r in calendar if r['role']=='probability_sample'];assert len(cal)==72 and len({r['date'] for r in cal})==72
 rng=random.Random(cfg['seed']);test=set()
 for phase in range(1,13):
  for stratum,n in [('weekday',2),('weekend',1)]:
   group=sorted(r['date'] for r in cal if int(r['phase'])==phase and r['stratum']==stratum);assert len(group)==2*n
   test.update(rng.sample(group,n))
 audit=[];hours=[]
 for chain in CHAINS:
  for c in cal:
   date=c['date'];f=source/chain/(date+'.csv.gz');nums=set();hashes=set();last=None;n=0;errors=[];sums={k:0 for k in FEATURES+['gas_used']};reserved={k:0 for k in RESERVED};first=None;lastts=None
   lower=int(datetime.datetime.fromisoformat(date+'T12:00:00+00:00').timestamp());prevts=None
   with gzip.open(f,'rt') as h:
    reader=csv.DictReader(h)
    for r in reader:
     n+=1;num=int(r['block_number']);ts=int(r['timestamp_unix'])
     if r['chain']!=chain:errors.append('chain_mismatch')
     if not lower<=ts<lower+3600:errors.append('time_boundary')
     if num in nums or r['block_hash'] in hashes:errors.append('duplicate')
     if last is not None:
      if num!=last[0]+1:errors.append('height_gap_or_order')
      if r['parent_hash']!=last[1]:errors.append('parent_mismatch')
      if ts<prevts:errors.append('time_order')
     for k in sums:
      if r[k]=='':errors.append('missing_'+k)
      else:sums[k]+=int(r[k])
     for k in reserved:reserved[k]+=int(bool(r.get(k,'')))
     nums.add(num);hashes.add(r['block_hash']);last=(num,r['block_hash']);prevts=ts;lastts=ts
     if first is None:first=ts
   if not n:errors.append('empty')
   audit.append(dict(chain=chain,date=date,phase=c['phase'],blocks=n,status='FAIL' if errors else 'PASS',errors='|'.join(sorted(set(errors))),first_timestamp=first,last_timestamp=lastts,sha256=sha(f),source=str(f.relative_to(source)),reserved_nonempty=json.dumps(reserved),boundary_completeness='Internal continuity only, no external boundary-block verification'))
   hours.append(dict(chain=chain,date=date,phase=int(c['phase']),stratum=c['stratum'],split='test' if date in test else 'train',blocks=n,source=str(f.relative_to(source)),sha256=sha(f),**sums))
  print('Audited',chain,flush=True)
 csvout(out/'data_audit.csv',audit)
 if any(r['status']!='PASS' for r in audit):raise RuntimeError('Data audit failed, see data_audit.csv')
 for chain in CHAINS:
  for phase in range(1,13):
   group=sorted([r for r in hours if r['chain']==chain and r['phase']==phase],key=lambda r:(r['gas_used'],r['date']))
   for i,r in enumerate(group):r['load_group']=i//2+1
 coeff=np.array([e['coefficients'] for e in cfg['edges']],dtype=float);pairs=[(N.index(a),N.index(b)) for a,b in old.EDGES]
 params={}
 for chain in CHAINS:
  rr=[r for r in hours if r['chain']==chain];train=np.array([[r[k] for k in FEATURES] for r in rr if r['split']=='train']);lo,hi=np.quantile(train,cfg['normalization']['quantiles'],axis=0)
  params[chain]=dict(features=FEATURES,lower=lo.tolist(),upper=hi.tolist(),constant_value=.5)
  for r in rr:
   x=np.array([r[k] for k in FEATURES]);den=hi-lo;v=np.full(3,.5);np.divide(x-lo,den,out=v,where=den!=0);v=np.clip(v,0,1)
   for k,val in zip(['X_tx','X_create','X_bytes'],v):r[k]=float(val)
 dump(out/'normalization.json',params);csvout(out/'hourly_workloads.csv',hours)
 perms=np.array(list(itertools.permutations(range(8))));flat=np.array([(x,y,0) for y in range(2) for x in range(4)]);stack=np.array([(x,y,z) for z in range(2) for y in range(2) for x in range(2)])
 def dv(slots):
  c=slots[perms];return np.array([2*np.abs(c[:,i,:2]-c[:,j,:2]).sum(axis=1) for i,j in pairs]).T,np.array([2*np.abs(c[:,i,2]-c[:,j,2]) for i,j in pairs]).T
 D,_=dv(flat);H,V=dv(stack);assert D.shape==(40320,12)
 # Check vectorization against original scalar implementation at nontrivial weights.
 samplew=np.arange(1,13,dtype=float);m=np.zeros((8,8))
 for (i,j),v in zip(pairs,samplew):m[i,j]=m[j,i]=v
 for k in [0,123,40319]:assert np.isclose(D[k]@samplew,old.cost(m,flat[perms[k]],1))
 matrices=[];matrixrows=[];results=[];summary=[];layouts=[];checks=[]
 for chain in CHAINS:
  rr=[r for r in hours if r['chain']==chain];X=np.array([[r[k] for k in ['X_tx','X_create','X_bytes']] for r in rr]);train=np.array([r['split']=='train' for r in rr]);inc=X@coeff.T
  for r,w in zip(rr,1+inc):
   mat=np.zeros((8,8))
   for (i,j),value in zip(pairs,w):mat[i,j]=mat[j,i]=value
   assert np.array_equal(mat,mat.T) and np.all(mat[A==0]==0) and np.all(mat>=0)
   matrices.append(dict(chain=chain,date=r['date'],split=r['split'],source=r['source'],sha256=r['sha256'],units='dimensionless proxy',matrix=mat.tolist()))
   matrixrows.append(dict(chain=chain,date=r['date'],**{f'W_{i}_{j}':mat[i,j] for i in range(8) for j in range(8)}))
  assert np.ptp(inc,axis=0).max()>0
  static2=int((D@np.ones(12)).argmin())
  for mode,scale in [('functional',v) for v in cfg['scales']]+[('uniform',1)]:
   weights=1+scale*inc if mode=='functional' else np.repeat((1+X.mean(axis=1))[:,None],12,axis=1)
   avg=weights[train].mean(axis=0);idx2=int((D@avg).argmin());c2=weights@D[idx2];cb=weights@D[0]
   if mode=='uniform':
    assert np.allclose((D@avg)/(avg[0]),D@np.ones(12))
   for lam in cfg['lambdas']:
    dist=H+lam*V;idx3=int((dist@avg).argmin());c3=weights@dist[idx3]
    if mode=='uniform':assert np.allclose((dist@avg)/avg[0],dist@np.ones(12))
    layouts.append(dict(chain=chain,mode=mode,scale=scale,lambda_value=lam,planar_assignment=perms[idx2].tolist(),two_layer_assignment=perms[idx3].tolist(),train_dates=[r['date'] for r in rr if r['split']=='train']))
    for k,r in enumerate(rr):results.append(dict(chain=chain,date=r['date'],phase=r['phase'],split=r['split'],mode=mode,scale=scale,lambda_value=lam,baseline_2d=float(cb[k]),optimized_2d=float(c2[k]),optimized_3d=float(c3[k]),change_percent=float(100*(c3[k]/c2[k]-1))))
    for split,mask in [('train',train),('test',~train)]:
     summary.append(dict(chain=chain,mode=mode,scale=scale,lambda_value=lam,split=split,hours=int(mask.sum()),baseline_2d=float(cb[mask].mean()),optimized_2d=float(c2[mask].mean()),optimized_3d=float(c3[mask].mean()),change_percent=float(100*(c3[mask].mean()/c2[mask].mean()-1)),planar_assignment_changed=bool(idx2!=static2)))
  checks.append(dict(chain=chain,distinct_edge_weight_vectors=len(np.unique(1+inc,axis=0)),uniform_scaling_preserves_all_cost_orderings=True))
 csvout(out/'weighted_matrices.csv',matrixrows);dump(out/'weighted_matrices.json',dict(modules=N,config_sha256=config_hash,observations=matrices));csvout(out/'layout_results.csv',results);csvout(out/'sensitivity_results.csv',summary);dump(out/'trained_layouts.json',layouts);dump(out/'checks.json',checks)
 # Figures use held-out means, with consistent zero-based axes where appropriate.
 fig,ax=plt.subplots(figsize=(8,5),layout='constrained');pos=np.array([(0,2),(1,1),(2,2),(3,2),(3,0),(1,-1),(2,-2),(4,-1)])
 for i,j in pairs:ax.plot(*pos[[i,j]].T,color='#aaaaaa',zorder=1)
 ax.scatter(*pos.T,s=1400,color='#deedf5',edgecolor='#226688',zorder=2)
 for name,(x,y) in zip(N,pos):ax.text(x,y,name,ha='center',va='center',fontsize=9)
 ax.set_axis_off();ax.set_title('Assumed topology: eight modules and twelve connections')
 def save(fig,name):fig.savefig(out/(name+'.pdf'),bbox_inches='tight');fig.savefig(out/(name+'.png'),dpi=150,bbox_inches='tight');plt.close(fig)
 save(fig,'figure1_topology')
 # First test date is chosen by calendar order, never by layout benefit.
 rep=[next(x for x in matrices if x['chain']==c and x['date']==min(test)) for c in CHAINS]
 fig,axs=plt.subplots(1,4,figsize=(12,3.4),layout='constrained');maxw=max(np.max(x['matrix']) for x in rep)
 for ax,mat,title in zip(axs,[A]+[np.array(x['matrix']) for x in rep],['Static A']+[c.replace('_',' ')+'\n'+min(test) for c in CHAINS]):
  im=ax.imshow(mat,vmin=0,vmax=maxw,cmap='Blues');ax.set_xticks(range(8),N,rotation=90,fontsize=6);ax.set_yticks(range(8),N,fontsize=6);ax.set_title(title,fontsize=9)
 fig.colorbar(im,ax=axs,label='Dimensionless connection weight',shrink=.7);save(fig,'figure2_matrices')
 fig,axs=plt.subplots(1,3,figsize=(10,3.5),layout='constrained',sharey=True)
 for ax,c in zip(axs,CHAINS):
  for mode,scale,label in [('functional',0,'Static A'),('functional',1,'Functional proxy W'),('uniform',1,'Uniform scaling')]:
   rr=[r for r in summary if r['chain']==c and r['split']=='test' and r['mode']==mode and r['scale']==scale];ax.plot([r['lambda_value'] for r in rr],[r['change_percent'] for r in rr],marker='o',label=label)
  ax.axhline(0,color='black',lw=.7);ax.set(title=c.replace('_',' '),xlabel='Vertical cost ratio');ax.set_xticks(cfg['lambdas']);ax.grid(alpha=.2)
 axs[0].set_ylabel('3D cost change vs optimized 2D (%)');axs[-1].legend(fontsize=7);save(fig,'figure3_costs')
 fig,axs=plt.subplots(1,3,figsize=(10,3.5),layout='constrained',sharey=True)
 for ax,c in zip(axs,CHAINS):
  for lam in cfg['lambdas']:
   rr=[r for r in summary if r['chain']==c and r['split']=='test' and r['mode']=='functional' and r['lambda_value']==lam];ax.plot([r['scale'] for r in rr],[r['change_percent'] for r in rr],'-o',label=f'lambda={lam}')
  ax.axhline(0,color='black',lw=.7);ax.set(title=c.replace('_',' '),xlabel='Mapping coefficient scale');ax.grid(alpha=.2)
 axs[0].set_ylabel('3D cost change vs optimized 2D (%)');axs[-1].legend(fontsize=7);save(fig,'figure4_sensitivity')
 assert original=={str(p):sha(p) for p in (ROOT/'outputs').glob('*') if p.is_file()}
 dump(out/'run_manifest.json',dict(source=str(source.resolve()),config_sha256=config_hash,script_sha256=sha(Path(__file__)),calendar_sha256=sha(source/'sampling_calendar.csv'),old_outputs_unchanged=True,python=sys.version,numpy=np.__version__,matplotlib=matplotlib.__version__,training_dates=36,test_dates=36))
 print('Completed weighted experiment',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,default=ROOT/'outputs/workload_weighted');a=p.parse_args();run(a.source,a.output)
