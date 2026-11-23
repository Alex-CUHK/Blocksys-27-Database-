"""Bounded, dependency-free TASK00/01 runner. No paid or full-chain scans."""
import argparse,csv,datetime as dt,hashlib,json,os,platform,random,shutil,sqlite3,subprocess,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CHAINS={'ETH':1,'ARB':42161,'OP':10,'SCROLL':534352}
DISK_LIMIT_GB=5
PERIODS={'P1':('2025-05-01','2025-11-01'),'P2':('2025-11-01','2026-05-01'),'P3':('2026-05-01','2026-11-01')}
def stamp(s): 
    value=dt.datetime.fromisoformat(s)
    if value.tzinfo is None:value=value.replace(tzinfo=dt.timezone.utc)
    return int(value.timestamp())
def size(): return sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
def guard(limit=None):
    limit=DISK_LIMIT_GB if limit is None else min(limit,DISK_LIMIT_GB)
    if limit<=0 or size()>=limit*10**9 or shutil.disk_usage(ROOT).free<3*10**9: raise RuntimeError('STOP: disk budget/reserve')
def write(name,obj):
    guard(); p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
def csvwrite(name,rows,fields):
    guard()
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def doctor():
    try: memory=subprocess.check_output(['sysctl','-n','hw.memsize'],stderr=subprocess.DEVNULL,text=True).strip()
    except (OSError,subprocess.SubprocessError): memory='UNAVAILABLE: OS permission'
    try: commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,stderr=subprocess.DEVNULL,text=True).strip()
    except (OSError,subprocess.SubprocessError): commit='UNAVAILABLE: no commit'
    obj=dict(status='REAL',python=platform.python_version(),system=platform.platform(),machine=platform.machine(),cpu_count=os.cpu_count(),memory_bytes=memory,free_bytes=shutil.disk_usage(ROOT).free,project_bytes=size(),git_commit=commit,seed=20261115,prng='Python random.MT19937',rpc_configured={k:bool(os.getenv(k+'_RPC_URL')) for k in CHAINS},export_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    write('environment.json',obj);return obj
class RPC:
    def __init__(self,url,budget=10): self.url=url;self.remaining=budget;self.calls=0
    def call(self,method,params):
        for attempt in range(3):
            if self.remaining<=0: raise RuntimeError('REQUEST_BUDGET_EXHAUSTED')
            guard(); self.remaining-=1;self.calls+=1
            request=urllib.request.Request(self.url,json.dumps(dict(jsonrpc='2.0',id=self.calls,method=method,params=params)).encode(),{'Content-Type':'application/json'})
            try:
                with urllib.request.urlopen(request,timeout=12) as response:
                    raw=response.read(2_000_001)
                if len(raw)>2_000_000: raise RuntimeError('RESPONSE_SIZE_LIMIT')
                result=json.loads(raw)
                if 'error' in result: raise RuntimeError('RPC_ERROR_'+str(result['error'].get('code','UNKNOWN')))
                if result.get('result') is None: raise RuntimeError('RPC_NULL')
                return result['result']
            except urllib.error.HTTPError as e:
                if e.code==429 and attempt<2: time.sleep(0.5*2**attempt);continue
                raise RuntimeError('HTTP_'+str(e.code)) from None
            except (urllib.error.URLError,TimeoutError,OSError): raise RuntimeError('NETWORK_UNAVAILABLE') from None
        raise RuntimeError('RETRY_EXHAUSTED')
    def block(self,n): return self.call('eth_getBlockByNumber',[hex(n),False])
def lower_bound(fetch,tip,target):
    lo,hi=0,tip+1
    while lo<hi:
        mid=(lo+hi)//2
        if int(fetch(mid)['timestamp'],16)<target:lo=mid+1
        else:hi=mid
    return lo

def sources(args):
    rows=[];remaining=args.max_requests
    for chain,cid in CHAINS.items():
        row=dict(chain=chain,chain_id=cid,status='BLOCKED',provider='environment:'+chain+'_RPC_URL',history_2025='UNAVAILABLE',history_2026='UNAVAILABLE',trace='NOT_PROBED: requires reviewed Pilot',requests=0,reason='RPC_NOT_CONFIGURED',rate='1 sequential request; bounded retries',quota='UNKNOWN',paid='UNKNOWN: explicit free-tier confirmation required')
        url=os.getenv(chain+'_RPC_URL')
        if url and not args.dry_run and args.confirm_free:
            rpc=RPC(url,remaining)
            try:
                if int(rpc.call('eth_chainId',[]),16)!=cid: raise RuntimeError('CHAIN_ID_MISMATCH')
                tip=int(rpc.call('eth_blockNumber',[]),16);cache={}
                def fetch(n):
                    if n not in cache:cache[n]=rpc.block(n)
                    return cache[n]
                for year in (2025,2026):
                    n=lower_bound(fetch,tip,stamp(f'{year}-06-01'))
                    if n>tip: raise RuntimeError('HISTORY_NOT_AVAILABLE')
                    block=fetch(n)
                    if dt.datetime.fromtimestamp(int(block['timestamp'],16),dt.timezone.utc).year!=year:raise RuntimeError('HISTORY_YEAR_MISMATCH')
                    row['history_'+str(year)]='REAL:'+str(n)+':'+block['hash']
                row.update(status='PARTIAL',reason='HOUR_POPULATION_NOT_VERIFIED')
            except (RuntimeError,ValueError,KeyError):
                import sys
                e=sys.exc_info()[1];row['reason']=str(e) if isinstance(e,RuntimeError) else 'MALFORMED_RPC'
            row['requests']=rpc.calls;remaining=rpc.remaining
        elif url:row['reason']='DRY_RUN' if args.dry_run else 'FREE_TIER_NOT_CONFIRMED'
        rows.append(row)
    csvwrite('outputs/source_capability_matrix.csv',rows,list(rows[0]));return {'status':'BLOCKED','sources':rows}
def coverage():
    rows=[]
    for c in CHAINS:
        for p,(a,b) in PERIODS.items():rows.append(dict(chain=c,period=p,valid_hours=0,total_hours=(stamp(b)-stamp(a))//3600,missing_range=a+'/'+b,status='UNAVAILABLE'))
    csvwrite('outputs/activity_coverage.csv',rows,list(rows[0]));return rows

def fixture():
    guard();db=sqlite3.connect(ROOT/'data/synthetic.sqlite')
    db.execute('CREATE TABLE IF NOT EXISTS hour_activity(chain_id INTEGER,hour INTEGER,block_count INTEGER,tx_count INTEGER,sum_gas_used INTEGER,coverage REAL,quality TEXT,source TEXT,PRIMARY KEY(chain_id,hour))')
    for c,cid in CHAINS.items():
        rng=random.Random(int.from_bytes(hashlib.sha256(f'20261115:{cid}'.encode()).digest(),'big'))
        for a,b in PERIODS.values():
            # Deliberately incomplete fixture: never a real percentile population.
            for h in range(48):db.execute('INSERT OR IGNORE INTO hour_activity VALUES(?,?,?,?,?,?,?,?)',(cid,stamp(a)+3600*h,10,rng.randrange(20,100),rng.randrange(10000,100000),1,'SYNTHETIC','synthetic-v1'))
    db.commit();n=db.execute('SELECT count(*) FROM hour_activity').fetchone()[0];db.close();return dict(status='SYNTHETIC',hours=n,real_windows=0)
def report():
    coverage()
    text='''# Stage audit
TASK00 implemented; TASK01 PARTIAL. TASK02–09 NOT STARTED.
REAL sampled windows: 0. Every chain × P1/P2/P3 × High/Normal/Low has 0 completed windows (36 cells).
No reliable complete hourly population acquired; formal percentiles and Pilot are BLOCKED.
Synthetic fixtures are isolated in data/synthetic.sqlite and must never enter mainnet sampling.
No trace, State Root reconstruction, RTL, hardware acceleration or Connection Matrix has been performed.

Next: supply a demonstrably free RPC endpoint per chain and a provenance-bearing historical hourly export for all 12 populations. Review licensing, coverage, field semantics and protocol changes before ingestion. RPC headers alone do not establish historical state/tracing access.
'''
    (ROOT/'outputs/pilot_report.md').write_text(text)
    write('outputs/artifact_hashes.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p.suffix in ('.py','.csv','.md','.yaml')})
    return {'status':'BLOCKED','real_windows':0}
def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['doctor','check-sources','fixture','pilot','full-sample','validate','report','trace-small']);p.add_argument('--dry-run',action='store_true');p.add_argument('--resume',action='store_true');p.add_argument('--confirm-free',action='store_true',help='Operator confirms configured endpoints consume no paid resources');p.add_argument('--max-requests',type=int,default=10);p.add_argument('--disk-limit-gb',type=float,default=5);a=p.parse_args()
    global DISK_LIMIT_GB
    DISK_LIMIT_GB=min(5,a.disk_limit_gb)
    guard()
    if a.max_requests<0:p.error('max-requests must be nonnegative')
    if a.command=='doctor':out=doctor()
    elif a.command=='check-sources':out=sources(a)
    elif a.command=='fixture':out={'status':'SYNTHETIC','action':'would create fixture'} if a.dry_run else fixture()
    elif a.command=='report':out=report()
    else:out={'status':'BLOCKED','reason':'TASK01 hourly population audit incomplete; Pilot review and protocol freeze required before expansion','real_windows':0}
    with (ROOT/'logs/experiment.log').open('a') as f:f.write(json.dumps(dict(utc=dt.datetime.now(dt.timezone.utc).isoformat(),command=a.command,args=vars(a),result=out))+'\n')
    print(json.dumps(out,indent=2))
    return 2 if out.get('status')=='BLOCKED' else 0
if __name__=='__main__':raise SystemExit(main())
