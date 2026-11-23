> Historical planning archive (November 15, 2026). Its four-network protocol, blocked status, and synthetic fixtures are separate from the current three-network probability sample and weighted layout experiment. Start with the repository root README.

# EVM historical workload sampling — stage 00/01

This delivery implements environment checks, bounded opt-in free RPC capability auditing, isolated synthetic fixtures, and offline tests. **Real Pilot: BLOCKED; 0/36 windows. Full sampling: not implemented or approved.** Remaining tasks 02–09 require verified hourly populations. CLI placeholder commands fail closed with exit code 2; they do not claim to implement sampling.

Python 3.11+, standard library runtime; no Docker, nodes, large downloads, paid API calls, or dependency installation needed. Run from this directory:

```sh
python3 src/workload.py doctor
python3 -m unittest discover -s tests -v
python3 src/workload.py fixture --resume
python3 src/workload.py check-sources --dry-run
python3 src/workload.py report
```

`check-sources` reads ETH_RPC_URL, ARB_RPC_URL, OP_RPC_URL, SCROLL_RPC_URL. No URLs or keys are logged. `.env.example` is documentation only; shell variables must be exported. `--confirm-free` is an operator assertion that configured endpoints have no paid consumption. Without it, no RPC requests occur. `--max-requests` is a global attempt budget, including retries, not a per-chain budget; 10 is intentionally insufficient for full binary searches. A bounded audit can use 250 requests after free-tier verification. Historical probes locate June 1 in 2025 and 2026 by timestamps, never guessed heights. Trace is deferred until Pilot review. Rate/quota/coverage remain unverified.

All commands accept --dry-run, --resume, --max-requests, --disk-limit-gb. Dry-run prevents network and fixture creation but may write audit metadata. Resume is idempotent for fixture inserts; other stage commands are repeatable audits, not collection resumptions. Responses are capped at 2 MB, timeout 12 seconds, 429 retries bounded by request budget. Disk checks enforce 5 GB project budget and 3 GB free reserve (decimal GB). No long-lived raw trace is stored.

Protocol: four chains, three UTC half-open periods, hourly gas sum as **within-chain** ranking proxy, never Trie operation counts. Intended quantiles High ≥95%, Normal 40–60%, Low 5–25%; missing hours never become zero. Seed 20261115. Intended 288 windows (4/2/2 train/validation/test), 36-window Train-only Pilot; five-minute slices, date/event cluster isolation and ≥24h dispersion. These future selection rules are not yet executed or frozen. Runtime version and Git commit availability recorded in environment.json. No RTL or chip interconnect simulation.

Fixtures contain only 48 hours per period per chain, marked SYNTHETIC in every row and stored separately. They cannot establish population percentiles. No sampling manifests or Parquet files are fabricated. Tests cover only implemented functions; stage 09 statistical QA remains outstanding.

Historical public endpoint audit (system curl transport, no keys):
```sh
python3 src/history_audit.py --dry-run
python3 src/history_audit.py --resume --max-requests 280
```
Stores only lightweight REAL headers in data/history_audit.sqlite, per-boundary results in outputs/historical_rpc_audit.csv, and attempts in experiment.log. Binary search tolerates a pruned historical prefix but requires a readable adjacent predecessor and matching parent hash before accepting the boundary; an unreadable predecessor fails closed. Cache is provider-specific and boundary headers are re-fetched for consistency. This probes June 1 of two years, not population coverage or trace support. This standalone audit uses the default 5 GB guard; workload.py's custom CLI disk limit does not apply to this script.
