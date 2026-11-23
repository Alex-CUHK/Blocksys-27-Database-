# Limitations

Block aggregates expose activity, not opcode counts, trie paths, cache misses or real hardware transfers. Transaction count, creation count and block size are proxies with imperfect and architecture-dependent relationships to module work. Block size includes data that may never traverse the assumed execution paths. Creation count is not a Keccak invocation count. No proxy is a measured byte or cycle count.

The topology, unit coefficients and equal-area slots are assumptions. Global scaling sensitivity tests only the magnitude of the selected mapping, not all possible edge assignments or feature combinations. Positive results cannot validate the chosen mapping. Train-only normalization avoids leakage but is based on 36 hours per chain and clips extremes. Per-chain normalization removes absolute cross-chain scale, so raw costs must not be interpreted as calibrated cross-chain hardware demand.

The held-out set shares the historical period with training, and nearby dates and protocol regimes may remain correlated. No population confidence interval, causal conclusion, or forecasting claim is made. The daily fixed hour does not represent all intraday activity. Supplemental event dates are excluded. Boundary completeness and source authenticity were not checked against independent blockchain nodes.

The experiment models endpoint weighted distances without routing, contention, queues, serialization, capacity constraints, physical wire lengths, TSV area, timing closure, thermal effects or energy calibration. Symmetric proxy weights do not imply symmetric real traffic. No historical EVM replay, opcode trace, RTL simulation, physical routing, or chip energy measurement was performed. Real traces and implementation validation are needed to calibrate the model.
