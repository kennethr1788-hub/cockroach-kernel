# PDH-3 R12 R6 R6 Full-Cardinality Preflight Blocked Receipt

- `STATUS`: `PDH3_R12_R6_R6_FULL_PREFLIGHT_BLOCKED`
- `BLOCKER`: `PF2R_SCALE_50000_COMBINED_SEED_SQL_TIMEOUT`
- `SECONDARY_BLOCKER`: `LIFECYCLE_GUARD_404_ABSENCE_NOT_TERMINAL`
- `UTC_CLOSED`: `2026-08-03T06:31:51Z`
- `CAMPAIGN_ID`: `ck-pdh3-r12-preflight-r6-repair6`
- `POD_ID`: `mzbblmsmmppz9u`
- `PACKET_SHA256`: `17585b9b4dad64d0f3311c2d42e746bc70ec91b535a74ac93902580901da0d79`
- `IMPLEMENTATION_COMMIT`: `01a92a54c2a6323029c0e95b7ee6a988f0cf2788`
- `PACKET_COMMIT`: `8fca8649beda08ea9ea21174e5ff39986191784d`
- `MEASURED_24H_STARTED`: `false`
- `REPLACEMENT_AUTHORITY_AFTER_UPLOAD`: `closed for this packet`
- `POD_TEARDOWN`: `GREEN; delete response true; exact Pod lookup 404; active inventory []`
- `LOCAL_CONTROLLER_TEARDOWN`: `GREEN after operator-scoped SIGTERM; no matching controller processes remain`

## Verified outcome

1. The independently reviewed same-hash packet was GREEN before worker creation.
2. Attempt 01 created one Secure Cloud L40S worker in `EU-NL-1` at `$0.99/hour`, with 32 provider vCPU, 117 GiB RAM, 250 GB disposable container disk, no persistent/network volume, and a verified 29-CPU affinity plan. The effective cgroup CPU count was 27, above the fixed 16-CPU minimum.
3. PF-4 was GREEN. All capability checks passed, including resource accounting, disk, RAM, fsync, sequential and sustained I/O, process-tree availability, affinity, and streaming network-observer capability.
4. The exact bundle SHA-256 `52619301a9aa0b88e5c2e3e52d668e6485ae105eb1c0f86405d681a5945be7a6` passed the extracted Linux smoke: 35 Python files compiled, all 13 test programs passed, and `failed_checks` was empty.
5. The 10,000-task Plan A/B rung was GREEN with exact counts `(10000, 10000, 20000, 10000, 10000)`, both prospective indexes selected, zero prohibited post-index full scans, zero mismatched results, and teardown GREEN.
6. The 50,000-task rung issued one combined SQL command containing all task, trajectory-event, receipt, vector, and projection inserts. That single subprocess exceeded the frozen 1,800-second SQL timeout and raised `SQL_TIMEOUT:3cf7b0a02c010bf7f5af473bd5610bc34403acaa837243d81ff58a60617c0231`.
7. The 50,000-task database process stopped, the generated root was removed, the database log was preserved, and the scale teardown receipt was GREEN.
8. Because the remote child exited `1`, the network observer correctly returned `PROCESS_TREE_OBSERVATION_BLOCKED`. It recorded no network-policy violations, 69 continuous summaries, 101,589 persisted evidence bytes, and a 24-hour evidence projection of 4,479,189 bytes. This is fail-closed evidence, not a network GREEN claim.
9. PF-5, PF-6, and PF-7 did not run. No full-cardinality, c500, fault-cycle, or 24-hour claim is supported.
10. Best-effort final evidence retrieval succeeded and the local archive SHA-256 exactly matched the remote SHA-256.
11. The Pod delete response was `{"deleted":true,"id":"mzbblmsmmppz9u"}`. Fresh exact lookup returned provider `404 not_found`; fresh active inventory was `[]`.
12. The local lifecycle guard did not recognize repeated provider `404 not_found` responses as successful exact-ID absence. It emitted repeated `PROVIDER_RETRY` events and left the local controller and PF2R wrapper running after provider deletion. Both processes were terminated locally after evidence retrieval and independent provider-absence verification; no matching controller process remains.

## Evidence bindings

| Evidence | SHA-256 |
|---|---|
| Retrieved `final-evidence.tgz` | `071919bdcdd8ea223c8155749fc99ad8046922d276934afd196f03fe084f0058` |
| Remote SHA receipt | `99d39dd89701f5c143f78a43d1add2bcb7d5fc0b5fb2fe1074c2191c8c6cae43` |
| Network receipt | `b9e734921574fbdad9e781b59956683cbf0680f11ee2203b4bb91f7256b29eed` |
| Remote child stderr | `0e8a7314676ce081238159d0ba1c2a0753d31b103846954b775824b029f3ea59` |
| 10k Plan A/B receipt file | `2a9dc7e3c84b19b3de795fe35ffc13cccd6b49ddc9ebe930ea10e10bb97e6e09` |
| 10k teardown | `2a0b45a098c7f2c87f9791dcecc8d5a5bdefc0fd66be900e89833dbfbfa8cce0` |
| 50k teardown | `314e09afac30db69a5de243757fd84327ad34bbf9b180d8c14e47c8b7133c0b8` |
| PF-4 host receipt | `8615c65928fba7ca0c9826a783d136e3641220636ad9e78f6304e58de0c467b8` |
| PF-4 capability receipt | `2aad8ee1271ed9c25cb055fe156a66a5a0b23d3265fa05c0327c7ba6c6fe9af3` |
| Extracted smoke receipt | `564acb4ddef6d5cf7b4757a3294a506c8e3d325eb63896dbfac6a3fb8bc447a5` |
| Main-bundle upload marker | `6be036f7aa9b548fba485ba0fe91f43e778bfc90098e1251fab58da8e874e705` |
| Pod delete response | `313c663340820a52ab057daffd3c38a76ed8043b57f6250679daced78432e809` |
| Lifecycle event stream | `b320f4b24d413d4306cef9595ac4ee593a74fd6a998d5dd33cbc36a501fee5fd` |

## Cost reconciliation

- Pre-create balance: `$85.1639031207`.
- Post-delete balance: `$84.5351255783`.
- Observed account-balance delta: `$0.6287775424`.
- The account also reported unrelated current spend of `$0.002/hour`; therefore the balance delta is an account-level reconciliation, not an exact itemized campaign charge.
- Even treating the complete balance delta as campaign spend, it is below the authorized `$12.00` ceiling.

## Classification and next boundary

This attempt is permanently BLOCKED. The primary defect is not the receipt-view index repair; it is the seed harness's decision to place five target-scale table populations into one all-or-nothing 1,800-second SQL subprocess. The secondary defect is a host lifecycle guard that retries provider `404 not_found` after deletion rather than treating verified absence plus empty inventory as teardown completion.

A future campaign requires a new prospective packet and new independent review. It may repair batching, per-table reconciliation/idempotency, bounded per-operation deadlines, setup-budget accounting, and exact-ID absence handling. It may not relabel this attempt, weaken cardinality or thresholds, reuse remote results as hidden evidence, or begin the measured 24-hour campaign.
