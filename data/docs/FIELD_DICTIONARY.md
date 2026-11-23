# Field dictionary
English translation and scope clarification of the supplied source dictionary. The original document mixed earlier chain labels and load-selection rules. This version distinguishes field semantics from those historical planning statements.

Window: November 16, 2023, 00:00 UTC inclusive through November 16, 2026, 00:00 UTC exclusive. Each selected date retains blocks from 12:00 inclusive to 13:00 exclusive. Missing or unparseable fields remain empty, including fields unavailable before a protocol fork. Missing values are not replaced with zero.

Source: SQD Portal https://portal.sqd.dev/datasets/{dataset}/finalized-stream. The collection notes describe GET /timestamps/{unix}/block for the first block with timestamp at least the target, followed by strict timestamp filtering. data_source uses sqd-portal:<dataset>.

| Field | Meaning and convention |
|---|---|
| chain | Network identifier. Delivered directories are Ethereum_Mainnet, Optimism, and Arbitrum_One. The inherited dictionary instead listed Ethereum_Mainnet, Polygon_PoS, and Base. |
| dataset | SQD dataset identifier as retained in each record. The inherited examples ethereum-mainnet, polygon-mainnet, and base-mainnet are not a specification of delivered coverage. |
| block_number | Integer block height |
| timestamp_utc | ISO 8601 UTC timestamp |
| timestamp_unix | Integer Unix seconds, filtered to the selected hour |
| block_hash | Hexadecimal hash with 0x prefix |
| parent_hash | Parent hash for continuity checks |
| state_root | stateRoot |
| transactions_root | transactionsRoot |
| receipts_root | receiptsRoot |
| gas_used | Block gasUsed parsed as an integer |
| gas_limit | Block gasLimit parsed as an integer |
| gas_utilization | gas_used / gas_limit, empty for missing inputs or zero limit |
| base_fee_per_gas | Base fee in wei, empty if missing |
| block_size_bytes | Block size in bytes |
| blob_gas_used | Empty before the relevant fork or when unsupported |
| excess_blob_gas | Same availability rule as blob_gas_used |
| tx_count | Transaction array length |
| tx_gas_used_sum | Sum only when every transaction supplies gasUsed, otherwise empty |
| failed_tx_count | Count with status==0, empty if any transaction lacks status |
| contract_creation_tx_count | Transactions with empty to |
| tx_with_to_count | Transactions with nonempty to |
| tx_type_0_count | Legacy transaction count |
| tx_type_1_count | EIP-2930 transaction count |
| tx_type_2_count | EIP-1559 transaction count |
| tx_type_3_count | Blob transaction count |
| tx_type_other_count | Other or unparseable types, with completeness notes |
| data_source | sqd-portal:<dataset> |
| tx_data_completeness | complete or partial:missing_gasUsed=N,... |

Eight reserved fields remain empty pending traces or hardware measurements: sload_count, sstore_count, committed_storage_changes, trie_node_reads, trie_node_writes, keccak_count, trie_dependency_depth, rtl_comm_bytes.

## Audit and summary files named in the source design
The inherited design described daily_summary.csv (hourly block/transaction/gas totals, size, SHA256, availability, status), hourly_activity.csv, data_integrity_audit.csv, collection_progress.csv, failed_tasks.csv, sampling_manifest.csv, gasused_quintiles_by_phase.csv, and paper_summary.csv. These names describe planned collection artifacts and do not imply every file was supplied. The current experiment publishes data_audit.csv, hourly_workloads.csv, normalization.json, and result manifests.

## Historical selection rules in the inherited dictionary
The earlier dictionary divided the window into twelve phases beginning on the 16th and calculated GasUsed quintiles independently for each chain and phase over collected hours. Levels 1 through 5 represented P0 to P20 through P80 to P100, with left-inclusive/right-exclusive boundaries except the last. It targeted four hours per level using four gas strata and seed 20231116, recording shortfalls. Within each selected hour, it chose the five-minute interval with gas nearest the hour total divided by twelve, breaking ties toward earlier intervals. These rules describe an earlier plan.

The current paper instead ranks six probability hours per phase into low, medium, and high pairs, uses whole hours for proxies, and keeps event dates separate. Both designs concern the fixed UTC hour. Gas accounting differs across networks, so absolute gas is not calibrated cross-network hardware pressure.
