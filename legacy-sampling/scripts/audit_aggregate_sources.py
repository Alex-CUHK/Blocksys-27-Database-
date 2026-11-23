"""Audit downloaded public source evidence without treating it as sampling data."""
import csv,datetime as dt,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from workload import ROOT,PERIODS,stamp,guard
root=ROOT/'data/source_audit';guard();rows=[]
for chain in ['ethereum','arbitrum','optimism','scroll']:
 p=root/(chain+'_throughput.json');obj=json.loads(p.read_text());points=obj['details']['timeseries']['hourly']['data'];ts=[x[0]//1000 for x in points]
 for period,(start,end) in PERIODS.items():
  valid={t for t in ts if stamp(start)<=t<stamp(end)}
  rows.append(dict(chain=chain,period=period,hours_present=len(valid),hours_expected=(stamp(end)-stamp(start))//3600,first_available=dt.datetime.fromtimestamp(min(ts),dt.timezone.utc).isoformat(),last_available=dt.datetime.fromtimestamp(max(ts),dt.timezone.utc).isoformat(),status='BLOCKED',reason='NO_RESEARCH_WINDOW_HOURS' if not valid else 'SEMANTICS_AND_COMPLETENESS_UNVERIFIED',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source=f'https://api.growthepie.com/v1/metrics/chains/{chain}/throughput.json'))
with (ROOT/'outputs/aggregate_source_coverage.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
p=root/'sqd_arbitrum_10blocks.jsonl';blocks=[json.loads(x)['header'] for x in p.read_text().splitlines()]
assert [x['number'] for x in blocks]==list(range(342607969,342607979))
assert all(x['timestamp']<=y['timestamp'] for x,y in zip(blocks,blocks[1:]))
# Measured one-year block difference, extrapolated to 549 days; estimate only.
n=(468748168-342607969)*549/365
estimate=dict(status='PARTIAL',observed_blocks=len(blocks),observed_bytes=p.stat().st_size,estimated_arbitrum_blocks_549_days=n,estimated_minimal_transfer_bytes=n*p.stat().st_size/len(blocks),basis='2025-06-01 to 2026-06-01 observed boundary block difference; extrapolation, NOT exact full-window count',excludes='transactions, hashes, provenance overhead, retries, other chains',sample_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
(ROOT/'outputs/aggregate_scan_estimate.json').write_text(json.dumps(estimate,indent=2))
with (ROOT/'logs/experiment.log').open('a') as f:f.write(json.dumps(dict(command='audit_aggregate_sources',utc=dt.datetime.now(dt.timezone.utc).isoformat(),result=estimate,covered_hours=sum(x['hours_present'] for x in rows)))+'\n')
print(json.dumps(estimate,indent=2))
