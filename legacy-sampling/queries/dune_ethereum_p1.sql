-- UNEXECUTED v1. Preflight DESCRIBE ethereum.blocks and ethereum.transactions.
-- Verify UTC timestamp semantics and export permissions before execution.
-- Aggregate blocks separately: joining blocks to transactions would multiply gas.
WITH b AS (
 SELECT date_trunc('hour',time) hour_utc,
 count(*) block_count, count(DISTINCT number) distinct_blocks,
 count(DISTINCT hash) distinct_hashes,
 sum(CAST(gas_used AS DECIMAL(38,0))) sum_gas_used,
 min(number) first_block, max(number) last_block,
 count_if(gas_used IS NULL) null_gas
 FROM ethereum.blocks
 WHERE time >= TIMESTAMP '2025-05-01 00:00:00'
 AND time < TIMESTAMP '2025-11-01 00:00:00'
 GROUP BY 1
), t AS (
 SELECT date_trunc('hour',block_time) hour_utc,
 count(*) tx_count, count(DISTINCT hash) distinct_transactions
 FROM ethereum.transactions
 WHERE block_time >= TIMESTAMP '2025-05-01 00:00:00'
 AND block_time < TIMESTAMP '2025-11-01 00:00:00'
 GROUP BY 1
)
SELECT 1 chain_id, coalesce(b.hour_utc,t.hour_utc) hour_utc,
 b.block_count,b.distinct_blocks,b.distinct_hashes,b.sum_gas_used,
 t.tx_count,t.distinct_transactions,b.first_block,b.last_block,b.null_gas
FROM b FULL OUTER JOIN t ON b.hour_utc=t.hour_utc
ORDER BY 2;
-- Do not coalesce missing counts to zero: investigate absent transaction hours.
-- No success filter: reverted and system/deposit transactions need explicit semantics.
