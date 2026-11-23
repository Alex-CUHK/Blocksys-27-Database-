"""Bounded public endpoint identity probe using system TLS/curl. No secrets."""
import csv,json,subprocess,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
endpoints=[('ETH',1,'https://ethereum-rpc.publicnode.com'),('ARB',42161,'https://arb1.arbitrum.io/rpc'),('OP',10,'https://mainnet.optimism.io'),('SCROLL',534352,'https://rpc.scroll.io')]
rows=[]
for chain,expected,url in endpoints:
 row=dict(chain=chain,expected_id=expected,url=url,observed_id='',status='BLOCKED',error='',utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  r=subprocess.run(['curl','-sS','--max-time','12','--max-filesize','10000',url,'-H','Content-Type: application/json','--data',json.dumps(dict(jsonrpc='2.0',id=1,method='eth_chainId',params=[]))],capture_output=True,text=True,timeout=15)
  if r.returncode:row['error']='CURL_'+str(r.returncode)
  else:
   result=json.loads(r.stdout);row['observed_id']=int(result['result'],16);row['status']='REAL_ID_ONLY' if row['observed_id']==expected else 'CHAIN_ID_MISMATCH'
 except (ValueError,KeyError,subprocess.TimeoutExpired):row['error']='INVALID_OR_TIMEOUT'
 rows.append(row)
with (root/'outputs/public_rpc_identity.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
with (root/'logs/experiment.log').open('a') as f:f.write(json.dumps({'command':'probe_public','results':rows})+'\n')
print(json.dumps(rows,indent=2))
