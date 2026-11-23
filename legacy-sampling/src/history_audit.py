"""Bounded public RPC historical audit. Cache contains only REAL lightweight headers."""
import argparse,csv,datetime as dt,json,sqlite3,subprocess,time
from pathlib import Path
from workload import ROOT,guard,stamp,lower_bound
ENDPOINTS=[('ETH',1,'https://ethereum-rpc.publicnode.com'),('ARB',42161,'https://arb1.arbitrum.io/rpc'),('OP',10,'https://mainnet.optimism.io'),('SCROLL',534352,'https://rpc.scroll.io')]
class PublicRPC:
 def __init__(self,url,budget):self.url=url;self.budget=budget;self.calls=0
 def call(self,method,params):
  for attempt in range(3):
   guard()
   if self.budget[0]<=0:raise RuntimeError('REQUEST_BUDGET_EXHAUSTED')
   self.budget[0]-=1;self.calls+=1
   try:
    p=subprocess.run(['curl','-sS','--max-time','12','--max-filesize','2000000','-w','\n%{http_code}',self.url,'-H','Content-Type: application/json','--data',json.dumps(dict(jsonrpc='2.0',id=self.calls,method=method,params=params))],capture_output=True,text=True,timeout=15)
   except subprocess.TimeoutExpired:raise RuntimeError('TIMEOUT') from None
   if p.returncode:raise RuntimeError('CURL_'+str(p.returncode))
   body,code=p.stdout.rsplit('\n',1)
   if code=='429' and attempt<2:time.sleep(2**attempt);continue
   if code!='200':raise RuntimeError('HTTP_'+code)
   try:obj=json.loads(body)
   except ValueError:raise RuntimeError('INVALID_JSON') from None
   if 'error' in obj:raise RuntimeError('RPC_ERROR_'+str(obj['error'].get('code','UNKNOWN')))
   if obj.get('result') is None:raise RuntimeError('RPC_NULL')
   time.sleep(.1)
   return obj['result']
  raise RuntimeError('RETRIES_EXHAUSTED')
def check_boundary(before,block,target):
 if int(block['timestamp'],16)<target:raise RuntimeError('LOWER_BOUND_INVALID')
 if before:
  if int(before['timestamp'],16)>=target:raise RuntimeError('PREDECESSOR_BOUNDARY_INVALID')
  if before['hash']!=block['parentHash']:raise RuntimeError('PARENT_HASH_MISMATCH')
  if int(before['number'],16)+1!=int(block['number'],16):raise RuntimeError('NUMBER_GAP')
def retained_lower_bound(fetch,tip,target):
 lo,hi=0,tip+1
 while lo<hi:
  mid=(lo+hi)//2
  try:timestamp=int(fetch(mid)['timestamp'],16)
  except RuntimeError as e:
   if str(e)!='RPC_ERROR_4444':raise
   lo=mid+1
   continue
  if timestamp<target:lo=mid+1
  else:hi=mid
 return lo

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--max-requests',type=int,default=280);parser.add_argument('--resume',action='store_true');parser.add_argument('--dry-run',action='store_true');a=parser.parse_args()
 if a.max_requests<0:parser.error('negative request budget')
 guard();budget=[a.max_requests]
 if a.dry_run:print(json.dumps({'status':'DRY_RUN','max_requests':a.max_requests,'endpoints':ENDPOINTS}));return 0
 db=sqlite3.connect(ROOT/'data/history_audit.sqlite')
 db.execute('CREATE TABLE IF NOT EXISTS headers(provider TEXT,number INTEGER,body TEXT,PRIMARY KEY(provider,number))')
 if not a.resume:db.execute('DELETE FROM headers');db.commit()
 rows=[]
 for chain,cid,url in ENDPOINTS:
  rpc=PublicRPC(url,budget)
  def fetch(n,refresh=False):
   old=db.execute('SELECT body FROM headers WHERE provider=? AND number=?',(url,n)).fetchone()
   if old and not refresh:return json.loads(old[0])
   block=rpc.call('eth_getBlockByNumber',[hex(n),False])
   if int(block['number'],16)!=n:raise RuntimeError('BLOCK_NUMBER_MISMATCH')
   light={k:block[k] for k in ['number','hash','parentHash','timestamp','gasUsed','gasLimit','stateRoot']}
   light['transaction_count']=len(block['transactions'])
   if old and json.loads(old[0])['hash']!=light['hash']:raise RuntimeError('REORG_OR_INCONSISTENT_PROVIDER')
   guard();db.execute('INSERT OR REPLACE INTO headers VALUES(?,?,?)',(url,n,json.dumps(light)));db.commit();return light
  try:
   if int(rpc.call('eth_chainId',[]),16)!=cid:raise RuntimeError('CHAIN_ID_MISMATCH')
   tip=int(rpc.call('eth_blockNumber',[]),16)
  except (RuntimeError,ValueError,KeyError) as e:
   for year in [2025,2026]:rows.append(dict(chain=chain,year=year,status='BLOCKED',reason=str(e),number='',timestamp='',hash='',parent_hash='',source=url))
   continue
  for year in [2025,2026]:
   row=dict(chain=chain,year=year,status='BLOCKED',reason='',number='',timestamp='',hash='',parent_hash='',source=url)
   try:
    target=stamp(f'{year}-06-01');n=retained_lower_bound(fetch,tip,target)
    if n>tip:raise RuntimeError('TARGET_AFTER_TIP')
    block=fetch(n,True);before=fetch(n-1,True) if n else None
    check_boundary(before,block,target)
    timestamp=dt.datetime.fromtimestamp(int(block['timestamp'],16),dt.timezone.utc)
    if timestamp.year!=year:raise RuntimeError('YEAR_MISMATCH')
    row.update(status='REAL',number=n,timestamp=timestamp.isoformat(),hash=block['hash'],parent_hash=block['parentHash'])
   except (RuntimeError,ValueError,KeyError) as e:row['reason']=str(e) if isinstance(e,RuntimeError) else 'MALFORMED_RESPONSE'
   rows.append(row)
   print(json.dumps(row),flush=True)
   with (ROOT/'outputs/historical_rpc_audit.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(row));writer.writeheader();writer.writerows(rows)
   with (ROOT/'logs/experiment.log').open('a') as f:f.write(json.dumps(dict(command='history-audit',utc=dt.datetime.now(dt.timezone.utc).isoformat(),result=row,requests_used=a.max_requests-budget[0]))+'\n')
 with (ROOT/'outputs/historical_rpc_audit.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 summary=dict(status='PARTIAL',verified_probes=sum(r['status']=='REAL' for r in rows),target_probes=8,requests=a.max_requests-budget[0],real_sample_windows=0)
 (ROOT/'outputs/history_audit_summary.json').write_text(json.dumps(summary,indent=2));db.close();print(json.dumps(summary));return 0
if __name__=='__main__':raise SystemExit(main())
