# PDH-3 R12 R6 Replacement Research and Repair Decision

- `STATUS`: `LOCAL_REPAIR_CANDIDATE_GREEN`
- `UTC_FROZEN`: `2026-08-03T07:25:21Z`
- `PARENT_FAILURE_PACKET_SHA256`: `d186345e47e3a984790da9e96c73e8f9c8f8c4e268287efe506d3b667854cb05`
- `PARENT_BLOCKED_RECEIPT_SHA256`: `975673a63254fd489a6de15721f3466a42058a7bfa9b8b3ac6df2402d1c861c9`
- `PARENT_POD_ID`: `mzbblmsmmppz9u`
- `PARENT_POD_STATE`: `deleted; exact lookup 404; active inventory empty`
- `MEASURED_24H_STARTED`: `false`

## Verified failure synthesis

The paid worker, RunPod hardware, Linux extraction, PF-4 capability gate, and 10,000-task Plan A/B rung were not the primary failure. The 50,000-task rung submitted task, event, receipt, vector, and projection population as one combined `cockroach sql --execute` operation. That command exceeded 1,800 seconds and yielded only the combined statement hash, so the harness could neither localize the slow table nor reconcile an uncertain partial completion. The database process and generated root were torn down, the remote evidence archive was retrieved with matching hashes, and the Pod was deleted.

The independent GLM failure-classification review agreed that this was a load-bearing harness defect and that the old packet was not retryable. A second defect existed in the host lifecycle guard: runpodctl v2.8 returned a numeric HTTP `status:404` plus symbolic `code:not_found`, but the parser incorrectly required every status/code field to be the integer `404`. Provider deletion was independently verified; the local controller had to be terminated after it continued retrying the valid absence response.

## Research basis

Fresh qualified Grok research was attempted three times and failed closed; no Grok content was accepted. The technical repair uses the retrieved raw evidence and these official sources:

1. CockroachDB vector-index documentation: vector indexes are maintained during writes; adding an index to a non-empty table performs a backfill and blocks writes during that backfill. Therefore PF-2 retains the pre-created online vector index instead of adding a new drop/recreate risk. Source: `https://www.cockroachlabs.com/docs/stable/vector-indexes`.
2. CockroachDB SQL performance guidance: use multi-row inserts for bulk loading, determine batch sizes experimentally, keep bulk inserts outside explicit transactions, and break large inserts into smaller batches when long transactions threaten deadlines. Source: `https://www.cockroachlabs.com/docs/v26.2/performance-best-practices-overview`.
3. CockroachDB transaction-retry guidance: SQLSTATE `40001` requires bounded client retry when it is not automatically retried. Source: `https://www.cockroachlabs.com/docs/stable/transaction-retry-error-reference`.
4. CockroachDB session-variable documentation: `statement_timeout` cancels a statement that exceeds its bound. Source: `https://www.cockroachlabs.com/docs/stable/session-variables`.

## Minimal prospective repair

1. PF-2 now reuses the production campaign's proven 5,000-task, per-table, `ON CONFLICT DO NOTHING` seed path for tasks, one event per task, the primary receipt, and vectors.
2. PF-2's intentional one-event/two-receipt shape is preserved by a separate, 5,000-task secondary-receipt batch. The second receipt is linked to event zero exactly as in the original PF-2 contract.
3. Projection rows use a separate 5,000-task batch path.
4. Every primary table, secondary-receipt batch, projection batch, and vector row is content-reconciled against deterministic expected values. `ON CONFLICT DO NOTHING` cannot conceal a mismatched row: any missing or differing field returns `MISMATCH` and blocks the rung.
5. Each SQL operation is capped at 60 seconds during seed/reconciliation. Every scale has one 3,600-second monotonic deadline, a 900-second seed tail reserve, and a 600-second post-seed reserve. Counts, metadata capture, query plans, statistics, and index DDL share the same scale deadline.
6. PF-2 proves visible vector-index metadata plus exact deterministic vector content. ANN quality remains in full-cardinality PF-5; it is not converted into a scale-sensitive 50,000-row PF-2 gate.
7. The lifecycle parser now requires at least one numeric 404 status, rejects any conflicting numeric status, permits a symbolic provider code only as auxiliary data, and still requires a Pod-specific absence message.
8. No product migration, production workload cardinality, concurrency, latency threshold, evidence threshold, fault schedule, RunPod shape, or 24-hour contract changed.

## Current-source local acceptance

The exact repaired source ran one canonical sequence over three fresh generated roots:

| Rung | Exact counts `(tasks, events, receipts, vectors, projections)` | Result | Receipt hash | File SHA-256 |
|---|---:|---|---|---|
| 10,000 | `(10000, 10000, 20000, 10000, 10000)` | GREEN | `fe262567cb06455a1a6c72a7853054c1f42fd50e2d59a74f9bfb3b9f86c2074a` | `466fa3ec025cfe84ce0b1789d46fb26119e1fec19b2709f42e1fa1894fc8bd8e` |
| 50,000 | `(50000, 50000, 100000, 50000, 50000)` | GREEN | `bc4b1512841165553d04ae36bdc4e2d7320a198c8ea6e313805a311bd3cfe739` | `8f7179b34fddbbd1cd7a541f22009007a2726d252663ccb7e74670ffda4e67e5` |
| 100,000 | `(100000, 100000, 200000, 100000, 100000)` | GREEN | `9106e950d7a01c3d41aaadd46a08088d60a82f75b94decdf397c535b6b1786c5` | `b3c1caa6a06771d8e505d8ad27233bc4f24fd051d88a74f34531db877caeb691` |

All rungs produced zero result mismatches and zero prohibited post-index full scans. All database processes stopped and all generated roots were removed. The aggregate `PF2_RESULT.json` is GREEN with receipt hash `c7e155a3e7187d38daa3e120611db596bf774e5a283ac67935522e619f3db966` and file SHA-256 `55eecf4f731bfeec7875b007f3baa9c1cf2bc1b5e1254ee7ac28b80e05454da0`.

The complete bundled regression plus lifecycle suite passed 160 tests across 14 programs. No paid worker was created during repair validation.

## Source bindings

| File | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_plan_ab.py` | `2d0cb19930e553e172ae3c92c1f745722cd2659a5689dff329b99d2db105a277` |
| `post-dogfood/test_pdh3_r12_plan_ab.py` | `a98185b9f53f6ae708ad0eb60bbd6ebf2fc6be22663e2777258aa9e32bf79ea7` |
| `s2-soak/lifecycle_guard.py` | `51258c2d983a6d0764485ff67ecd5e662085331758a2ce1d41813ea79652a5c6` |
| `s2-soak/test_lifecycle_guard.py` | `a59810dfa3c57a90b220163505fc03a499a7fa16a55443eb1f59cbce1260ab1e` |

## Go/no-go boundary

This artifact authorizes packet construction only. A replacement paid preflight remains `NO_GO` until the deterministic transfer bundle and extracted-bundle smoke are GREEN, current RunPod price/inventory fit the operator envelope, absolute deadlines are frozen, all source and evidence hashes are bound into one packet, and independent GLM 5.2 returns GREEN over that exact packet hash.

