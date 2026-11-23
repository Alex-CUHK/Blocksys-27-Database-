"""Design calculation only. Does NOT sample or change the experiment."""
import csv,math
from pathlib import Path
rows=[]
for eps in [.05,.025,.01]:
 n=math.ceil(math.log(2*12/.05)/(2*eps**2))
 rows.append(dict(simultaneous_confidence=.95,populations=12,cdf_error=eps,draws_per_population=n,total_hour_draws=n*12,expected_unique_P1_hours=4416*(1-(1-1/4416)**n),status='PROPOSED_NOT_APPROVED'))
p=Path(__file__).resolve().parents[1]/'outputs/probability_error_bounds.csv'
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(rows)
