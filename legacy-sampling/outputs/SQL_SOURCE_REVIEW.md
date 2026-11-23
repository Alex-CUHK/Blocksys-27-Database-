# Historical server-side SQL source review
Review date: November 15, 2026. Prices and access statements below are historical observations, not current quotations. The earlier four-chain protocol retained P1/P2/P3, High/Normal/Low groups, and seed 20261115. This differs from the current three-network study.
Status: BLOCKED_ACCESS. Ethereum P1 had not been acquired. No paid queries or account creation occurred.

## Candidates
- Dune: Official block catalogs existed for all four chains. Ethereum fields were checked, while detailed L2 schemas required DESCRIBE. Free access was read-only. The reviewed page displayed Analyst at $65/month with 4,000 credits and Plus at $349/month with 25,000 credits, with an annual-payment toggle. These were not confirmed monthly checkout quotes. API access required a key. Exports were listed at 10 and 2 credits/MB, with additional credits at $0.016 and $0.014. Plus explicitly listed CSV export. Analyst API export permissions needed confirmation. Query costs depended on execution and export size. Catalog presence did not prove complete coverage or an immutable historical snapshot.
- Allium Explorer: Historical SQL was confirmed, but all four raw.blocks schemas, particularly Scroll, had not been verified from public catalogs. Signup advertised 100 Explorer Units, requiring an account. Developer Units were not SQL allowances. Machine-payments SQL submission and status each cost $0.01 in the reviewed material. Results were dynamically priced, and status/results required an API key. This was not a $0.01 total experiment quote. Reorganization handling and repeated batch validation required freezing query runs and export hashes. Earliest/latest timestamps, fields, and time semantics still needed validation.
- BigQuery Blockchain Analytics: Official coverage included Ethereum, Arbitrum, and OP, with Scroll unlisted. Google account/project access was required. The reviewed allowance was 1 TiB/month free, with displayed on-demand excess at $6.25/TiB, subject to region and currency. Dry runs and maximum_bytes_billed should control scanning costs. Export size does not estimate scanned bytes. block_timestamp was monthly partitioned. The old Arbitrum goog-blockchain listing stopped updates on October 31, 2026, requiring the new bigquery-public-data tables. Completeness and revisions still needed empirical checks.
- Bitquery: Official historical coverage listed Ethereum, Arbitrum, and OP, with Scroll unconfirmed. GraphQL aggregation was an alternative to SQL. Account access and current historical-query pricing were unverified. Documented start dates did not establish complete hours.
- growthepie: Real downloads from four networks contained 335 recent hours, all after the target window, giving zero historical overlap. Daily data could not substitute for hourly records.
- SQD: Ten Arbitrum blocks were verified. Complete windows remained unavailable. Public bounded evaluation was possible, but server-side SQL aggregation had not been demonstrated. Transfer estimates were not a statistical population.

## Official sources consulted
- https://dune.com/pricing
- https://docs.dune.com/api-reference/overview/authentication
- https://docs.dune.com/data-catalog/evm/ethereum/raw/blocks
- https://docs.dune.com/data-catalog/evm/arbitrum/raw/blocks
- https://docs.dune.com/data-catalog/evm/optimism/raw/blocks
- https://docs.dune.com/data-catalog/evm/scroll/raw/blocks
- https://docs.dune.com/data-catalog/data-quality
- https://www.allium.so/product/allium-explorer
- https://app.allium.so/join
- https://docs.allium.so/ai/machine-payments/endpoints-pricing
- https://docs.allium.so/guides/reorgs
- https://docs.cloud.google.com/blockchain-analytics/docs/supported-datasets
- https://docs.cloud.google.com/blockchain-analytics/docs/schema
- https://cloud.google.com/bigquery/pricing
- https://docs.bitquery.io/docs/graphql/data-coverage-retention/

## Ethereum P1 acceptance procedure
1. Obtain authorized account access or an existing complete public export. Verify schema, spending cap, UTC semantics, and license before any query. No accounts or payment-signing calls were created during this review.
2. Run the two Ethereum schema-preflight queries, then dune_ethereum_p1.sql. Both were unexecuted drafts, with no server compilation claim.
3. Aggregate blocks and transactions separately before joining to prevent duplicate block gas. Retain failed transactions and distinguish block gas from receipt gas. Preserve missing transaction counts as NULL.
4. Require exactly 4,416 UTC hours from May 1, 2025 inclusive to November 1 exclusive. Duplicate hashes/heights, NULL gas, negative values, or missing hours fail validation. Zero-block hours require independent outage or boundary evidence.
5. Retain SQL SHA256, schema exports, query_id, execution_id, UTC export time, pages, rows, file hashes, license, and actual credits/billing. All result pages must be acquired.
6. Use a fixed seed to cross-check at least three complete hours by RPC enumeration. Compare gas, transaction and block counts, and verify height continuity across hours. Stop on inconsistencies rather than silently patching them.
7. After 24 hours, rerun a small range or check revision indicators and retain differences. Version revised exports and document absent snapshot guarantees.
8. Extend to other periods and networks only after these checks. Steps 1 through 7 had not been executed at review time.

## Exact historical blocker
DUNE_API_KEY, ALLIUM_API_KEY, and GOOGLE_APPLICATION_CREDENTIALS were absent. Only presence was checked. No verified anonymous, free, complete four-chain hourly export was available. Dune was the preferred route pending access, Allium required Scroll schema and results-cost confirmation, and BigQuery required another source for Scroll.
