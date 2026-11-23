# Workload-informed weighted connectivity methodology

This experiment links real blockchain observations to assumed hardware edge weights. It does not recover hardware traffic from block aggregates. The original experiment and its output files remain unchanged.

## Data and integrity

Use the common calendar's 72 probability_sample dates for each chain, excluding every event supplement. Inspect chain metadata inside every gzip CSV. Sum tx_count, contract_creation_tx_count, block_size_bytes and gas_used. Record block count, date, phase, source path and SHA256. Check duplicates, ordering, timestamp bounds, consecutive heights, and internal parent hashes. Missing required values fail the run. Reserved execution fields retain their original missing status and are not substituted by zeros. The audit reports their nonempty counts. Internal continuity does not independently establish that the source omitted no blocks at the window boundaries, and hashes verify file identity rather than blockchain authenticity.

## Shared date split and normalization

Using seed 20231116, within each phase randomly select two weekdays and one weekend date for testing. The other two weekdays and one weekend date are training observations. All three chains share the same 36 training and 36 test dates. This is a stratified within-period holdout, not a forecast evaluation. Nearby dates may remain dependent.

For each chain and feature, fit the 5th and 95th percentiles on training observations only using NumPy's linear interpolation. Transform x to clip((x-p05)/(p95-p05),0,1). If the training bounds are equal, assign 0.5 to that feature for every observation, including test data. This neutral constant supplies no within-feature ordering. Parameters are saved in normalization.json. Hourly gas ranks are descriptive metadata only and are not used to fit proxy normalization or select layouts.

## Fixed topology and coefficients

Retain the original eight modules and twelve undirected edges. The editable mapping_config.yaml is JSON-compatible YAML 1.2 and can be read without an extra YAML dependency. It records the coefficient triplet and engineering rationale for each edge. Coefficients express binary feature inclusion, not fitted physical parameters.

For every original edge, W_ij=1+s*(alpha_ij*X_tx+beta_ij*X_create+gamma_ij*X_bytes). All nonedges and diagonal entries remain zero. W is symmetric and dimensionless. s=1 is the prespecified main experiment. s=0, 0.5 and 2 are sensitivity controls. The mapping was fixed before results and was not selected to favor 3D.

The uniform control gives every edge the same per-hour factor 1+mean(X_tx,X_create,X_bytes). Its costs are positive scalar multiples of static costs, so rankings and relative layout costs must be preserved. The implementation verifies this over all permutations at the training-average weights for both geometries and every tested vertical ratio.

## Optimization and reporting

Enumerate 40,320 labeled permutations on a 4x2 planar grid and a 2x2x2 grid. Precompute each original edge's planar and vertical distances. Multiply undirected edge distances by two to retain the original ordered-pair counting convention. The distance-vector implementation is checked against the original scalar cost function.

For each chain, mapping scale and vertical ratio, minimize mean TRAINING cost. This is equivalent to optimizing the mean training weight vector because cost is linear in weights. Freeze the selected planar and two-layer assignments before evaluating test dates. Each vertical ratio is a separate hardware-cost scenario with its own training-selected two-layer layout. No test observation gets its own optimized layout.

Report baseline planar cost, frozen optimized planar cost and frozen optimized two-layer cost for each date. Aggregate with unweighted test-hour means, consistent with a held-out sample experiment rather than a population estimate. Percentage change is 100*(mean two-layer cost / mean optimized planar cost - 1). Negative values indicate lower modeled cost. It is not the mean of hourly percentage changes and is not speedup. Equal-slot total resource assumptions and the zero diagonal are unchanged.

## Reproduction and provenance

Run reproduce.sh. Source checks and matrix checks fail closed. The run records source hashes, configuration hash, script hash, package versions, normalization parameters and selected permutations. The representative matrix heatmap uses the earliest held-out date, without selection by performance. Static output hashes are checked before and after execution.

## Fixed edge mapping

| Edge | alpha (Tx) | beta (Creation) | gamma (Bytes) | Assumption |
|---|---:|---:|---:|---|
| dispatch--stack | 1 | 0 | 0 | Transaction count proxies instruction dispatch and operand handling. |
| dispatch--alu | 1 | 0 | 0 | Transaction count proxies general execution activity, not opcode count. |
| dispatch--keccak | 0 | 1 | 0 | Creation count proxies deployment-associated hashing demand, not measured Keccak calls. |
| dispatch--memory | 1 | 0 | 1 | Transaction activity and block data scale proxy execution-memory demand. |
| dispatch--state | 1 | 1 | 0 | Transactions and deployments proxy potential state work. |
| stack--alu | 1 | 0 | 0 | Transaction activity proxies operand exchange. |
| stack--memory | 1 | 0 | 1 | Execution activity and data scale proxy memory operand movement. |
| stack--state | 1 | 1 | 0 | Transactions and deployments proxy state addressing activity. |
| memory--keccak | 0 | 1 | 1 | Deployment and data scale proxy hash-input movement. |
| state--cache | 1 | 1 | 0 | State requests proxy cache demand without claiming hit rates. |
| cache--dram | 0 | 0 | 1 | Block bytes proxy potential data movement, not measured cache misses. |
| memory--dram | 0 | 0 | 1 | Block bytes proxy potential external data movement, not DRAM traffic. |
