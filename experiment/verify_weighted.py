"""Independent checks of split, normalization, matrices, and saved layout costs."""
import csv,json,datetime
from pathlib import Path
import numpy as np
import experiment as old
P=Path(__file__).resolve().parent/'outputs/workload_weighted'
h=list(csv.DictReader((P/'hourly_workloads.csv').open()));cfg=json.loads((P/'mapping_config.yaml').read_text());params=json.loads((P/'normalization.json').read_text());mat=json.loads((P/'weighted_matrices.json').read_text())['observations'];layouts=json.loads((P/'trained_layouts.json').read_text())
assert len(h)==216 and len(mat)==216
chains=sorted({r['chain'] for r in h});splits=[]
for c in chains:
 rr=[r for r in h if r['chain']==c];splits.append({r['date']:r['split'] for r in rr})
 for phase in range(1,13):
  for split in ['train','test']:
   group=[r for r in rr if int(r['phase'])==phase and r['split']==split]
   assert len(group)==3
   assert sum(datetime.date.fromisoformat(r['date']).weekday()<5 for r in group)==2
 train=np.array([[float(r[k]) for k in params[c]['features']] for r in rr if r['split']=='train'])
 lo,hi=np.quantile(train,[.05,.95],axis=0);assert np.allclose(lo,params[c]['lower']) and np.allclose(hi,params[c]['upper'])
assert splits[0]==splits[1]==splits[2]
A=np.array(old.matrix([(a,b,1) for a,b in old.EDGES]+[(b,a,1) for a,b in old.EDGES]))
for m in mat:
 w=np.array(m['matrix']);assert np.array_equal(w,w.T) and np.all(w[A==0]==0) and np.all(w[A>0]>=1)
byhour={(r['chain'],r['date']):r for r in h};bylayout={(r['chain'],r['mode'],float(r['scale']),float(r['lambda_value'])):r for r in layouts}
flat=[(x,y,0) for y in range(2) for x in range(4)];stack=[(x,y,z) for z in range(2) for y in range(2) for x in range(2)]
res=list(csv.DictReader((P/'layout_results.csv').open()))
for r in res:
 obs=byhour[r['chain'],r['date']];x=np.array([float(obs[k]) for k in ['X_tx','X_create','X_bytes']]);scale=float(r['scale']);w=np.zeros((8,8))
 for e in cfg['edges']:
  i,j=map(old.NAMES.index,e['pair']);v=1+scale*np.dot(e['coefficients'],x) if r['mode']=='functional' else 1+x.mean();w[i,j]=w[j,i]=v
 layout=bylayout[r['chain'],r['mode'],scale,float(r['lambda_value'])]
 for field,coords in [('baseline_2d',flat),('optimized_2d',[flat[i] for i in layout['planar_assignment']]),('optimized_3d',[stack[i] for i in layout['two_layer_assignment']])]:
  assert np.isclose(float(r[field]),old.cost(w,coords,float(r['lambda_value'])))
 if r['split']=='test':assert r['date'] not in layout['train_dates']
 if r['mode']=='uniform':
  expected={.25:-34.375,1:-6.25,2:18.75,4:68.75}[float(r['lambda_value'])];assert np.isclose(float(r['change_percent']),expected)
print('PASS: calendar-stratified split, train-only fit, 216 matrix constraints,',len(res),'scalar cost comparisons, held-out isolation, uniform scaling.')
