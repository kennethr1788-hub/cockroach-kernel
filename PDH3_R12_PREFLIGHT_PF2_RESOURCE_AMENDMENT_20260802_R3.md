# PDH-3 R12 PF-2 Resource Amendment R3

Status: `FROZEN_FOR_INDEPENDENT_REVIEW__NO_RUNPOD_LAUNCH`

Parent plan: `PDH3_R12_EXTENSIVE_PREFLIGHT_PLAN_20260802_R1.md`

Parent plan SHA-256:
`a1214b4779fe1495de219ed0033421ac810390641cd97742deb61cd3957df3d9`

Parent resource amendment:
`PDH3_R12_PREFLIGHT_RESOURCE_BOUNDARY_AMENDMENT_20260802_R2.md`

Parent resource-amendment SHA-256:
`4bf4e47b79a66c672208cbd90f18ad31ff4f23400e833c728a189507dbb0e0b9`

Direct local blocker receipt:
`PDH3_R12_PF2_LOCAL_RESOURCE_BLOCKER_RECEIPT_20260802.json`

## Verified new evidence

The PF-2 harness started an isolated disposable CockroachDB v26.2.3 node,
created a fresh 100-task synthetic dataset, and froze all five current receipt
query plans before attempting either candidate index. Each receipt predicate
used `receipts@receipts_pkey` with `spans: FULL SCAN`.

The first bounded correction then failed before completion:

```text
store 1 has insufficient remaining capacity to ingest data
(remaining: 7.0 GiB / 1.5%, min required: 5.0%)
```

The database process was stopped, its generated root was removed, and the
teardown receipt is GREEN. The product migration was not modified. No reduced
result is represented as equivalent and no unrelated data will be deleted to
manufacture local free space.

## Narrow amendment

This amendment changes only the execution surface and ordering of PF-2.

1. The local PF-2 attempt is preserved as
   `PF2_LOCAL_STORAGE_RESERVE_BLOCKED`; it is not PF-2 GREEN.
2. PF-4 remains the first paid stage and must first prove exact hardware,
   price, disk, network-namespace observer, lifecycle guard, and off-Pod
   checkpoint capability.
3. After PF-4 GREEN, the same worker must run `PF-2R` before PF-5:
   - three fresh generated roots at 10,000, 50,000, and 100,000 tasks;
   - current `SHOW INDEXES`, `SHOW STATISTICS`, `EXPLAIN`, and read-only
     `EXPLAIN ANALYZE (DISTSQL)` frozen before correction;
   - the identical 27 read queries at each scale;
   - only the receipt index from the parent plan, plus the smallest
     source-key index only when the frozen current plan proves it necessary;
   - completed schema/statistics jobs;
   - byte-identical results before and after;
   - no receipt or stale-projection full scan after correction;
   - exact count/content reconciliation, regression tests, teardown, and an
     off-Pod verified receipt for every scale.
4. PF-5 remains the first target-cardinality proof and must repeat target-scale
   current/selected plan capture. PF-2R cannot substitute for PF-5.
5. Any PF-2R failure closes the worker under PF-8 teardown rules. PF-5 through
   PF-7 and any 24-hour campaign remain forbidden.

## Unchanged boundaries

Every threshold, workload cardinality, literal-c500 rule, evidence ceiling,
one-worker rule, zero-volume boundary, failure custody rule, and claim boundary
from R1/R2 remains unchanged. No 24-hour campaign is authorized.

## Judge question

Does this amendment preserve the evidentiary strength of PF-2 while respecting
the directly observed local CockroachDB storage reserve, given that PF-2R must
complete before PF-5 and PF-5 must repeat all target-scale plan gates?

Return exactly:

```text
SERVED_MODEL: <provider-reported model>
TARGET_AMENDMENT_SHA256: <exact supplied hash>
VERDICT: GREEN | NOT_GREEN | BLOCKED | JUDGE_UNAVAILABLE
CRITICAL_FINDINGS:
- <finding or NONE>
HIGH_FINDINGS:
- <finding or NONE>
REQUIRED_CORRECTIONS:
- <correction or NONE>
RATIONALE: <concise explanation>
```

GREEN authorizes only the amended preflight staging sequence. It does not
certify PF-2, authorize a RunPod worker, or authorize a 24-hour campaign.
