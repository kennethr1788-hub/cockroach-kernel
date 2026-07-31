# PDH-3 Prior Attempt Cost Envelope R8

- `STATUS`: `CONSERVATIVE_UPPER_BOUND_NOT_PROVIDER_INVOICE`
- `ATTEMPTS`: `01` through `07`
- `COMPUTE_RATE_CEILING_USD_HOUR`: `0.99`
- `DISPOSABLE_DISK_GB`: `250`
- `DISK_RATE_USD_GB_30_DAY_MONTH`: `0.10`
- `TOTAL_ACTIVE_RATE_UPPER_USD_HOUR`: `1.0247222222222223`
- `PRIOR_ACTIVE_SECONDS_UPPER`: `5684`
- `PRIOR_COST_UPPER_USD`: `1.6179225308641976`
- `REPLACEMENT_28_HOUR_COST_UPPER_USD`: `28.692222222222224`
- `AGGREGATE_COST_UPPER_USD`: `30.310144753086423`
- `AUTHORIZED_AGGREGATE_CEILING_USD`: `35.00`
- `MINIMUM_REMAINING_HEADROOM_USD`: `4.689855246913577`

This is deliberately not an exact provider charge. It is a conservative
evidence-bound upper envelope used only to prove that one full 28-hour
replacement lifecycle can remain below Kenneth's existing `$35` aggregate
authorization. Exact billing must still be preserved if the provider exposes
it.

## Conservative interval law

For Attempts 01 through 06, each paid interval ends at the next attempt's
creation time, not at an optimistic local deletion timestamp. The receipts
prove the earlier exact Pod ID was absent and matching active inventory was
empty before its replacement was created. Attempt 07 ends at the independently
recorded `TEARDOWN_GREEN` event. This intentionally overcounts inactive time.

| Attempt | Conservative UTC interval | Upper seconds |
|---|---|---:|
| 01 | `2026-07-31T04:00:06Z` to `2026-07-31T04:05:25Z` | 319 |
| 02 | `2026-07-31T04:05:25Z` to `2026-07-31T04:16:28Z` | 663 |
| 03 | `2026-07-31T04:16:28Z` to `2026-07-31T04:30:53Z` | 865 |
| 04 | `2026-07-31T04:30:53Z` to `2026-07-31T04:40:25Z` | 572 |
| 05 | `2026-07-31T04:40:25Z` to `2026-07-31T04:41:08Z` | 43 |
| 06 | `2026-07-31T04:41:08Z` to `2026-07-31T04:41:46Z` | 38 |
| 07 | `2026-07-31T04:41:46Z` to `2026-07-31T05:34:50Z` | 3,184 |

## Source bindings

| Evidence | SHA-256 |
|---|---|
| `PDH_3_SCALE_RUNPOD_ATTEMPT_01_RECEIPT.md` | `e31d2571e3272cb732a1af8dd8b3233a7e9f0c69d74352b0228c46e9bab2b1b7` |
| `PDH_3_SCALE_RUNPOD_ATTEMPT_02_RECEIPT.md` | `a9e42fae48705f7c43f1bfc4f0924ebeb57973964a71385d68d45d8238b79250` |
| `PDH_3_SCALE_RUNPOD_ATTEMPT_03_RECEIPT.md` | `6c8d8ec91292e06ba2146db95d307f93463c2d0c5b3dd0578b5704790daee759` |
| `PDH_3_SCALE_RUNPOD_ATTEMPT_04_RECEIPT.md` | `32814ae7a2e4492e62fc5b734c4ac3540b100cd1a149da0f14f930cf5792863b` |
| `PDH_3_SCALE_RUNPOD_ATTEMPTS_05_06_RECEIPT.md` | `6c34afea3d932c10e901d8054acf221a17e1cf2349897da41608dc5131ac10b7` |
| `PDH_3_SCALE_CAMPAIGN_RUNNING_RECEIPT_R1.md` | `546250cdd201121dd8ba6741b36a437f7eff9777a2899154465cd878939f6734` |
| `.pdh3-runtime/preflight-r7/attempt-07-lifecycle-guard.ndjson` | `b873ec11a6c8d408d4d14357843858a7b1bdc5fedc4c2de203e695faf5008ddf` |
| `.pdh3-runtime/preflight-r7/attempt-07-final-retrieval/final-state.json` | `5562f9861524dead0cb564f6d37a6c6a197dfa182caa3339325dcc1cbf0a7317` |
| `.pdh3-runtime/preflight-r7/attempt-07-final-retrieval/final-evidence.tgz` | `b13fc07d1ef8fcac358647b5fdd06925a7f0e3b5cb166303e813ced81c91e6e2` |

## Arithmetic

`TOTAL_ACTIVE_RATE_UPPER = 0.99 + (250 * 0.10 / (30 * 24))`

`PRIOR_COST_UPPER = 5684 / 3600 * TOTAL_ACTIVE_RATE_UPPER`

`REPLACEMENT_COST_UPPER = 28 * TOTAL_ACTIVE_RATE_UPPER`

`AGGREGATE_COST_UPPER = PRIOR_COST_UPPER + REPLACEMENT_COST_UPPER`

`MINIMUM_REMAINING_HEADROOM = 35 - AGGREGATE_COST_UPPER`
