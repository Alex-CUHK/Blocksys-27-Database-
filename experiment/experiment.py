"""Standard-library architecture-level pilot; no measured EVM performance claims."""
import argparse,csv,gzip,hashlib,itertools,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
NAMES=['dispatch','stack','alu','keccak','memory','state','cache','dram']
EDGES=[('dispatch','stack'),('dispatch','alu'),('dispatch','keccak'),('dispatch','memory'),('dispatch','state'),('stack','alu'),('stack','memory'),('stack','state'),('memory','keccak'),('state','cache'),('cache','dram'),('memory','dram')]
def dump(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def matrix(edges):
 a=[[0]*8 for _ in NAMES]
 for x,y,w in edges:a[NAMES.index(x)][NAMES.index(y)]+=w
 return a
def sample(source):
 result=[];audit=[]
 for chain in ['Ethereum_Mainnet','Optimism','Arbitrum_One']:
  hours=[];count=0
  for f in sorted((source/chain).glob('*.csv.gz')):
   gas=0;rows=0
   with gzip.open(f,'rt') as h:
    for r in csv.DictReader(h):gas+=int(r['gas_used']);rows+=1
   count+=rows
   hours.append((gas,f,rows))
  if not hours:raise ValueError('No source files: '+chain)
  hours.sort()
  for label,q in [('low',.1),('medium',.5),('high',.9)]:
   total,f,n=hours[round(q*(len(hours)-1))]
   with gzip.open(f,'rt') as h: records=list(csv.DictReader(h))
   # Median gas block of selected hour, not an inferred execution trace.
   r=sorted(records,key=lambda r:(int(r['gas_used']),int(r['block_number'])))[len(records)//2]
   result.append(dict(chain=chain,level=label,source=(pathlib.Path('data/raw')/chain/f.name).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),hour_gas=total,block_number=int(r['block_number']),block_hash=r['block_hash'],timestamp=r['timestamp_utc'],tx_count=int(r['tx_count']),status='TRACE_REQUIRED'))
  audit.append(dict(chain=chain,files=len(hours),rows=count))
 dump(ROOT/'outputs/samples.json',result);dump(ROOT/'outputs/source_audit.json',audit)
 return result
def distance(a,b,z_cost):return abs(a[0]-b[0])+abs(a[1]-b[1])+z_cost*abs(a[2]-b[2])
def cost(m,coords,z):return sum(m[i][j]*distance(coords[i],coords[j],z) for i in range(8) for j in range(8))
def optimize(m,slots,z):
 # Exhaustive search gives a global optimum within this tiny fixed-slot model.
 return min(((cost(m,p,z),p) for p in itertools.permutations(slots)),key=lambda v:v[0])
def layout(m):
 flat=[(x,y,0) for y in range(2) for x in range(4)]
 stacked=[(x,y,z) for z in range(2) for y in range(2) for x in range(2)]
 base=cost(m,flat,1);opt,p=optimize(m,flat,1)
 out={'baseline_2d':{'cost':base,'coordinates':dict(zip(NAMES,flat))},'optimized_2d':{'cost':opt,'coordinates':dict(zip(NAMES,p))},'three_dimensional_sensitivity':[]}
 for z in [.25,1,2,4]:
  c,p=optimize(m,stacked,z)
  out['three_dimensional_sensitivity'].append({'vertical_cost':z,'cost':c,'coordinates':dict(zip(NAMES,p))})
 return out
def ingest(path):
 """Accept simulator events only, not opcode counts masquerading as traffic."""
 obj=json.loads(path.read_text())
 if obj.get('provenance') not in ['SIMULATED_FROM_REAL_TRACE','SYNTHETIC']:raise ValueError('Explicit provenance required')
 if not obj.get('architecture_model') or not obj.get('workload_id'):raise ValueError('Model and workload provenance required')
 edges=[]
 for e in obj['events']:
  if e['src'] not in NAMES or e['dst'] not in NAMES:raise ValueError('Unknown module')
  if not isinstance(e['bytes'],int) or isinstance(e['bytes'],bool) or e['bytes']<0:raise ValueError('Invalid byte count')
  edges.append((e['src'],e['dst'],e['bytes']))
 m=matrix(edges)
 return dict(provenance=obj['provenance'],architecture_model=obj['architecture_model'],workload_id=obj['workload_id'],modules=NAMES,directed_bytes=m,total_bytes=sum(map(sum,m)),layout=layout(m))
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=pathlib.Path);p.add_argument('--events',type=pathlib.Path);a=p.parse_args()
 if a.source:sample(a.source)
 topology=matrix([(x,y,1) for x,y in EDGES]+[(y,x,1) for x,y in EDGES])
 dump(ROOT/'outputs/architecture.json',dict(provenance='ASSUMED_ARCHITECTURE_NOT_NETLIST',modules=NAMES,connection_matrix=topology,edge_weight=1,diagonal=0))
 dump(ROOT/'outputs/static_layout.json',dict(provenance='STATIC_TOPOLOGY_MODEL_NOT_EVM_SPEEDUP',results=layout(topology)))
 if a.events:dump(ROOT/'outputs/event_layout.json',ingest(a.events))
if __name__=='__main__':main()
