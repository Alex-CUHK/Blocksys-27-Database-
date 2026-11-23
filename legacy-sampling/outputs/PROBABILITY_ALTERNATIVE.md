# Probability sampling alternative: PROPOSED_NOT_APPROVED
Historical design assessment, November 15, 2026. This is separate from the current 72-date study. It neither changes the historical protocol nor generates samples.

When complete hourly populations are unavailable, construct a finite frame of all calendar hours in each chain-period population, draw uniformly and independently with replacement, and retrieve every real block in each selected hour. Each draw has probability 1/N. Cached repeated hours save reads, but their multiplicities must remain in the ECDF. Workloads are fixed population values, while randomness comes from independent index draws. Historical serial dependence does not invalidate that sampling mechanism.

The DKW inequality for one population is P(sup_x |F_n(x)-F(x)| > epsilon) <= 2 exp(-2n epsilon^2). A union bound over twelve populations gives simultaneous confidence of at least 95% when n >= ln(24/0.05)/(2 epsilon^2). scripts/evaluate_probability_alternative.py computes:

| Absolute CDF error | Draws per population | Draws across 12 populations |
|---|---:|---:|
| 5 percentage points | 1,235 | 14,820 |
| 2.5 percentage points | 4,940 | 59,280 |
| 1 percentage point | 30,869 | 370,428 |

These are percentile-rank errors, not relative gas errors or mean errors. For p=0.95, empirical quantiles at p plus or minus epsilon bound the population quantile, with endpoint clipping and generalized inverse CDF handling for ties. At epsilon=0.05 the upper endpoint reaches 1, giving a weak tail bound. Coincident thresholds do not establish exact High-group membership.

P1 contains 4,416 hours. Expected unique sampled hours at the three budgets are approximately 1,077, 2,973, and 4,412. High precision therefore approaches a census and may cost more than server-side aggregation. Repeated draws are not distinct event clusters, and blocks within one hour are not independent replicate hours.

Conditions:
- Every selected hour must be complete. Dropping unreadable hours or replacing them can introduce load-dependent missingness and invalidate the bound.
- The frame contains all calendar hours. Excluding unknown anomalous hours requires a separately defined estimand and proof.
- DKW does not guarantee eight windows per group with 24-hour separation and isolated training, validation, and test events. Subsequent filtering changes selection probabilities.
- Calibration must not use test-window feedback. Register event isolation, seed derivation, and budgets before protocol revision.
- Without a gas upper bound, these CDF guarantees do not imply a distribution-free error bound for mean gas.

Complete SQL aggregation remains the preferred historical route. This alternative quantifies error-cost tradeoffs and does not establish the original exact population 95th-percentile selection of 288 windows.

References: Massart (1990), The Tight Constant in the Dvoretzky-Kiefer-Wolfowitz Inequality, https://doi.org/10.1214/aop/1176990746. Supplementary research: https://arxiv.org/abs/2403.16651.
