"""Recompute manuscript tables from audited probability-sample hourly aggregates."""
from pathlib import Path
import json,re
import numpy as np
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'figures/hourly_data.json').read_text());p=root/'samplepaper.tex';s=p.read_text()
chains=[('Ethereum_Mainnet','Ethereum'),('Optimism','OP Mainnet'),('Arbitrum_One','Arbitrum One')]
report={}
t1=r'''\begin{table}[t]
\caption{Probability-sample coverage, excluding event supplements. Failed denotes the total failed-transaction count. Failure share is the pooled failed count divided by all transactions.}\label{tab:sample}
\centering\footnotesize
\setlength{\tabcolsep}{2pt}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrrr@{}}
\toprule Network & Hours & Blocks & Transactions & Failed & \shortstack{Failure\\share (\%)} \\\midrule
'''
t2=r'''\begin{table}[t]
\caption{Hourly statistics recomputed from 72 probability dates per network. SD is the sample standard deviation. IQR is the 75th minus the 25th percentile, using linear interpolation. All entries are counts per hour.}\label{tab:hourly}
\centering\footnotesize
\setlength{\tabcolsep}{2pt}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrrrr@{}}
\toprule Network & Metric & Mean & SD & Median & IQR \\\midrule
'''
for chain,name in chains:
 r=[x for x in rows if x['chain']==chain];assert len(r)==72
 totals={k:sum(x[k] for x in r) for k in ['blocks','tx_count','failed_tx_count']}
 frac=100*totals['failed_tx_count']/totals['tx_count'];report[chain]={'totals':totals,'pooled_failure_percent':frac,'hourly':{}}
 t1+=f"{name} & 72 & {totals['blocks']:,} & {totals['tx_count']:,} & {totals['failed_tx_count']:,} & {frac:.2f}"+r' \\'+'\n'
 for j,(key,label) in enumerate([('blocks','Blocks'),('tx_count','Tx'),('failed_tx_count','Failed tx')]):
  v=np.array([x[key] for x in r],dtype=float);q1,q3=np.percentile(v,[25,75]);vals=[v.mean(),v.std(ddof=1),np.median(v),q3-q1]
  report[chain]['hourly'][key]=dict(zip(['mean','sd','median','iqr'],[float(x) for x in vals]))
  prefix=r'\multirow{3}{*}{'+name+'}' if j==0 else ''
  t2+=prefix+' & '+label+' & '+' & '.join('0' if x==0 else f'{x:,.2f}' for x in vals)+r' \\'+'\n'
 t2+=r'\addlinespace'+'\n'
for label,t in [('sample',t1),('hourly',t2)]:
 t+=r'''\bottomrule
\end{tabular*}
\end{table}'''
 pattern=r'\\begin\{table\}\[t\]\n\\caption\{[^\n]*?\\label\{tab:'+label+r'\}.*?\\end\{table\}'
 s,n=re.subn(pattern,lambda _:t,s,flags=re.S);assert n==1,n
p.write_text(s);(root/'figures/descriptive_table_values.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
