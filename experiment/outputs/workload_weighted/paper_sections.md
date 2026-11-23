# Workload-informed proxy connectivity results

## Workload-Informed Communication Weighting

We used 72 probability-sampled hours from each of Ethereum Mainnet, OP Mainnet, and Arbitrum One. All event supplements were excluded. Per phase, two weekdays and one weekend date were assigned to training and the remaining three dates to testing, using a common split across networks. The fixed seed was 20231116. The 216 source files passed internal checks for chain identity, timestamp bounds, duplicate records, consecutive heights and parent-hash continuity. Independent verification of window boundary completeness remains outside this audit.

## Proxy-Based Matrix Construction

The original eight-module topology and twelve undirected connections were retained. Transaction count, contract-creation count and summed block size were normalized within each chain using training-only 5th and 95th percentiles. Values outside these bounds were clipped to [0,1]. Fixed coefficients in mapping_config.yaml transformed these observations into symmetric dimensionless weights. These are workload-informed proxies, not measured hardware bytes. The configuration specifies every edge's coefficient triplet and functional rationale, and was fixed before optimization.

The primary mapping generated 72 distinct weight vectors for Ethereum, 72 for OP Mainnet, and 70 for Arbitrum One. The two repeated Arbitrum vectors reflect coincident normalized proxy inputs after clipping. The selected planar permutation remained the same as the static baseline optimum in all tested chains and mapping scales. Thus the new observations altered edge weights and costs without requiring a change in the selected planar assignment in this experiment.

## Two-Dimensional and Three-Dimensional Layout Evaluation

We enumerated all 40,320 assignments for each fixed grid, using the original ordered-pair distance convention. For each chain and vertical-cost ratio, placements minimized mean training cost and were frozen before evaluation on 36 held-out dates. The static experiment reproduced costs 44 and 32 for baseline and optimized planar placement, and two-layer costs 21, 30, 38 and 54 at vertical ratios 0.25, 1, 2 and 4. Original static output files were unchanged.

The table reports unweighted held-out sample mean costs under the primary functional mapping. Percentage change is relative to the optimized planar mean. Negative percentages indicate lower two-layer modeled cost.

| Network | Vertical ratio | Baseline 2D | Optimized 2D | Optimized 3D | Change (%) |
|---|---:|---:|---:|---:|---:|
| Ethereum_Mainnet | 0.25 | 71.209 | 51.012 | 33.736 | -33.87 |
| Ethereum_Mainnet | 1 | 71.209 | 51.012 | 48.160 | -5.59 |
| Ethereum_Mainnet | 2 | 71.209 | 51.012 | 61.771 | +21.09 |
| Ethereum_Mainnet | 4 | 71.209 | 51.012 | 88.993 | +74.46 |
| Optimism | 0.25 | 69.165 | 50.524 | 33.613 | -33.47 |
| Optimism | 1 | 69.165 | 50.524 | 48.091 | -4.82 |
| Optimism | 2 | 69.165 | 50.524 | 61.539 | +21.80 |
| Optimism | 4 | 69.165 | 50.524 | 88.435 | +75.04 |
| Arbitrum_One | 0.25 | 67.495 | 49.055 | 32.556 | -33.63 |
| Arbitrum_One | 1 | 67.495 | 49.055 | 46.481 | -5.25 |
| Arbitrum_One | 2 | 67.495 | 49.055 | 59.485 | +21.26 |
| Arbitrum_One | 4 | 67.495 | 49.055 | 85.495 | +74.28 |

## Sensitivity Analysis

The two-layer cost was lower than the optimized planar cost at vertical ratios 0.25 and 1, and higher at 2 and 4. This direction did not reverse across coefficient multipliers 0.5, 1 and 2 on any network. At ratio 1, the held-out reductions ranged from 4.15% to 5.84% across these network and coefficient combinations. At ratio 4, increases ranged from 72.10% to 77.95%. These tests vary mapping magnitude only and do not establish robustness to other edge-feature mappings.

The uniform scaling control preserved the static ranking and relative changes: -34.375%, -6.25%, +18.75%, and +68.75%. This control confirms that simple overall activity scaling changes absolute scores without creating a new relative layout advantage. The independent verifier checked 4,320 saved per-hour scenario records against the original scalar cost function, together with shared date partitions, train-only normalization and matrix constraints.

## Threats to Validity

Real observations determine the proxy inputs, while topology and functional coefficients remain explicit modeling assumptions. Aggregated blocks cannot identify opcodes, cache behavior, trie accesses or physical hardware paths. The proxy matrix is not the execution-trace traffic matrix T. Costs are weighted distances, not execution times, throughput, bandwidth, energy or physical wirelength. No real opcode tracing, RTL simulation, routing or chip measurement was performed. Future tracing and implementation studies are required for calibration. Within-period held-out dates may be temporally dependent, and the fixed daily hour does not represent full-day activity. Per-chain normalization prohibits calibrated absolute cross-chain cost comparisons. The reported means are test-sample summaries, not design-weighted three-year population estimates.

## Files and reproduction

Run `PYTHON=/path/to/python ./reproduce.sh` from this directory, or use the repository root instructions. The default source is `data/raw` and the default interpreter is the repository `.venv/bin/python`. An alternate source root can be passed as the first argument. This report retains the full experimental record, including sensitivity plots subsequently described in prose in the manuscript. The current manuscript is in `manuscript/` and is synchronized separately to Overleaf.
