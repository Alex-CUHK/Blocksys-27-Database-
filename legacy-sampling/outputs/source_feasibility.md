# Source feasibility audit — 2026-11-15

Status: BLOCKED for real populations; PARTIAL source investigation. No paid calls, no full scans. Four configured RPC environment variables are absent. Browser search access works; local RPC POST access remains unverified, not claimed unavailable. OS memory query was denied. No API account or export is available in the workspace.

## Candidate aggregate services
- Dune https://dune.com/pricing : retrieved public pricing describes free view/copy access and paid query capabilities. No export or query was executed; full four-chain hourly coverage and licensing have NOT been validated. Do not equate dashboard visibility with free bulk export.
- Allium https://app.allium.so/join and https://www.allium.so/blog/allium-launches-self-service-for-real-time-developer-apis/ : advertises signup credits and historical datasets. Developer credits do not prove free historical SQL exports. No account created or credits consumed. Four-chain coverage, query cost, historical schema and license are UNVERIFIED.
- RPC headers: chain identity and two historical year probes implemented but not executed without endpoints. Trace support UNKNOWN. Header retention is not archive-state retention.

## Scan cost model (hypothetical, NOT measured block counts)
The interval has 549 days = 47,433,600 seconds, 13,176 hours per chain; four chains need 52,704 verified hourly rows. Header requests are N = end_height - start_height, plus timestamp boundary probes and retries. N cannot be determined without actual endpoint measurements. Illustrative cadence assumptions only: 12 s implies 3,952,800 requests; 2 s implies 23,716,800; 0.25 s implies 189,734,400. These are not asserted historical chain cadences. At one request/s each would take approximately 46, 275, 2196 days. Storage depends on retained row size; streaming hourly aggregates avoids retaining all headers. Monetary price and quotas UNKNOWN, never assumed zero. Full enumeration is not authorized or started.

Preferred next input: 52,704 complete UTC hourly rows, with chain ID, gas sum, tx/block counts, coverage, original source URL, SQL/query version/ID, export UTC and license. Independently cross-check random hours with headers. Missing buckets must not be filled with zeros. Assess duplicates, continuity, source field definitions and protocol versions per period before quantiles.

## Protocol evidence
Scroll official Euclid page https://docs.scroll.io/en/technology/overview/scroll-upgrades/euclid-upgrade/ documents the April 2025 migration from zkTrie to MPT. This supports the requested start date only; it does not establish that any chain implementation stayed constant during all periods. Ethereum/Arbitrum/OP/Scroll per-period upgrade timelines remain to be audited before the main experiment.

## Acceptance gaps
TASK00: runnable standard-library CLI, offline unittest tests and fixture delivered; pytest is not installed, so pytest execution is NOT claimed.
TASK01: source matrix and feasibility delivered; real identity/history/trace probes remain unverified. No trustworthy complete hourly export acquired. Therefore TASK02–06 halted at the explicit source-coverage gate. CLI later-stage commands are fail-closed placeholders, not completed implementations. TASK07–09 not completed.

## Follow-up execution
Public endpoints were selected from Arbitrum chain-info, the official Optimism superchain registry and Scroll developer documentation:
ETH https://eth.llamarpc.com ; ARB https://arb1.arbitrum.io/rpc ; OP https://mainnet.optimism.io ; SCROLL https://rpc.scroll.io . Each received one attempted eth_chainId request in the restricted run and one in the escalated run (8 attempts total). Both runs returned NETWORK_UNAVAILABLE before any verified RPC result. A local diagnostic observed DNS resolution failure; this does not establish provider outage. No mainnet block height, identity or historical availability has been verified.
Sources: https://developer.arbitrum.io/chain-info ; https://github.com/ethereum-optimism/superchain-registry/blob/main/superchain/configs/mainnet/op.toml ; https://docs.scroll.io/en/developers/tooling-deployed-on-scroll . Endpoints used no API key or billing account; service quotas remain UNKNOWN.

Additional source candidates:
- https://docs.growthepie.com/core-concepts/time-granularity-freshness-and-update-cadence documents daily flat exports and optional hourly series; txcount is an hourly example. fundamentals.json covers only 90 days. This is not evidence of complete historical hourly block.gasUsed sums plus block/tx counts. Coverage and matching gas definitions remain unverified.
- https://portal.sqd.dev/ and https://sqd.dev/chains/ advertise historical data and support for the four chains. Public access is described as free at current limits until billing starts. No query submitted, account created, or bulk stream downloaded. Need verify no-key access, requested block fields including tx count, start/end coverage, transfer volume and license before adopting this source. Full bulk enumeration remains gated by cost assessment.

Follow-up QA: 11 unittest tests pass, including UTC offset conversion and persistent custom disk budget. pytest has still not been run. All 36 experiment cells remain at zero REAL windows. Aggregate population acquisition remains BLOCKED.

### Transport correction (later observation supersedes connectivity inference)
System curl outside the sandbox successfully verified Arbitrum=42161, OP=10, Scroll=534352. Ethereum endpoint did not provide a parseable successful identity response; reason remains unresolved. See public_rpc_identity.csv for timestamps and exact public endpoint URLs. Python urllib failures therefore do NOT mean the three successful services are unreachable. Historical headers and hourly populations remain unverified. A separate initial curl Scroll probe also returned 534352. No real sampling windows were collected.

### Ethereum replacement verified
At 2026-11-15T07:23:24.128023+00:00, https://ethereum-rpc.publicnode.com returned eth_chainId=0x1 via system curl. Replaced the failed Llama endpoint in the public probe script and identity CSV. All four public endpoints now have verified chain IDs; historical coverage and trace remain unverified. Official endpoint source: https://ethereum.publicnode.com/ .

## Historical audit completed (8 evidence points)
Four chains each have verified June 1 boundaries in 2025 and 2026, with fresh predecessor and parent-hash checks. First pass used 178 requests; second pass used 100 and stopped at its budget while rechecking Arbitrum. The merged CSV preserves successful first-pass evidence for remaining chains and links each row to its evidence file; it does not claim the retry completed all chains. Ethereum needed search handling for a pruned historical prefix (4444); both requested dates passed. 278 requests total, zero paid resources. Complete hourly populations and trace support still unverified; formal Pilot remains BLOCKED. Sixteen unittest tests passed.

## Aggregate-source gate
See DATA_SOURCE_BLOCKER.md for measured four-chain hourly coverage (zero in study periods), successful bounded SQD ten-block probe, and an estimated 14.29GB minimal Arbitrum transfer. Large-scale enumeration is not started pending the user decision required by the task specification.
