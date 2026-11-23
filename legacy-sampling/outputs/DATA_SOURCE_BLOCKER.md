# Historical source-access blocker
Historical status from November 15, 2026, preceding the current SQD dataset. BLOCKED, with zero real sampled windows under the earlier protocol. Eight RPC boundary probes across four chains do not establish population coverage.

## Observations at that time
1. growthepie throughput JSON provided 335 hourly points per network, from November 1, 2026, 08:00 UTC through November 15, 2026, 06:00 UTC. The historical study window ended at November 1, 00:00 UTC, so all twelve chain-period populations had zero overlapping hours. Daily data cannot reconstruct hourly data. Raw responses, source URLs, and hashes were retained.
2. SQD Portal returned ten consecutive historical Arbitrum blocks, heights 342607969 through 342607978. Number, timestamp, and gasUsed occupied 753 bytes. This anonymous probe included repeated timestamps, omitted transaction counts, and had not completed RPC gas cross-validation. It was not a candidate sampled hour.
3. Extrapolating observed boundary-height differences over 549 days estimated 189.7 million Arbitrum blocks. At 75.3 bytes per minimal response block, transfer was approximately 14.29 GB for one chain, before transaction counts, hashes, other chains, and retries. This was a rough transfer estimate, not an exact population count. Streaming reduces disk use but does not remove transfer and quota costs.

The SQD documentation then described public access as development or bounded evaluation. It listed a planned Public allowance near 50 MB/month and 0.1 MB/s while noting that billing had not started and existing limits remained effective. Planned allowances were not treated as observed enforcement or permission for a full anonymous backfill. Source: https://docs.sqd.dev/en/portal/pricing.md

The historical task required a cost assessment and authorization before expensive scanning. No large backfill, account creation, or paid query was performed.

## Options recorded at the time
Prefer an existing Dune, Allium, or research-platform export or authorized account, aggregating to 52,704 hourly rows on the server. Paid queries require a confirmed budget. Alternatively, authorize transfer and time budgets for a free streaming backfill after checking current terms and quotas, retaining the local 5 GB cap and 3 GB system reserve. Changes to periods or load metrics require an explicit protocol revision.

Reproduction: python3 scripts/audit_aggregate_sources.py
Artifacts: aggregate_source_coverage.csv, aggregate_scan_estimate.json, and data/source_audit/.
