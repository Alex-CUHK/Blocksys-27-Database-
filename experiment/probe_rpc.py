"""Bounded public RPC capability probe: three requests, no credentials."""
import concurrent.futures,json,pathlib,subprocess
P=pathlib.Path(__file__).resolve().parent
ENDPOINTS={'Ethereum_Mainnet':'https://ethereum-rpc.publicnode.com','Optimism':'https://optimism-rpc.publicnode.com','Arbitrum_One':'https://arbitrum-one-rpc.publicnode.com'}
def probe(item):
 chain,url=item
 # Invalid block deliberately tests method availability without expensive replay.
 payload={'jsonrpc':'2.0','id':1,'method':'debug_traceBlockByNumber','params':['0x0',{'timeout':'1s','disableStack':True,'disableStorage':True}]}
 try:
  r=subprocess.run(['/usr/bin/curl','--silent','--show-error','--fail','--max-time','12','--max-filesize','100000','-H','Content-Type: application/json','--data-binary',json.dumps(payload),url],capture_output=True,check=True)
  data=r.stdout
  result=json.loads(data) if len(data)<=100000 else {'error':'response size cap'}
 except Exception as e:result={'transport_error':str(e)}
 return {'chain':chain,'endpoint':url,'probe_block':'genesis','result':result,'historical_sample_trace_verified':False}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:out=list(ex.map(probe,ENDPOINTS.items()))
 (P/'outputs/rpc_probe.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
