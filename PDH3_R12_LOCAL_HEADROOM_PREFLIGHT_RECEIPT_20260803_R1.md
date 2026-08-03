# PDH-3 R12 Local Headroom Preflight Receipt R1

- `STATUS`: `LOCAL_REPRESENTATIVE_SCALE_GREEN__100K_LOCAL_THROUGHPUT_BLOCKED__TEARDOWN_GREEN`
- `UTC_CREATED`: `2026-08-03T05:05:53Z`
- `CURRENT_COMMIT`: `25962737c5c7661a43c0862da9b76eed0ae4bb3f`
- `LAST_GREEN_GATE`: `PDH_3_LOCAL_CANARY_GREEN`
- `PLAN_SHA256`: `a1214b4779fe1495de219ed0033421ac810390641cd97742deb61cd3957df3d9`
- `PAID_WORKER_CREATED`: `false`
- `MEASURED_24H_STARTED`: `false`
- `ACTIVE_RUNPOD_INVENTORY`: `empty when checked before this receipt`

## Objective

Revalidate the repaired R6 candidate locally after disk reclamation without weakening the workload, thresholds, evidence rules, or teardown contract. This receipt is local preflight evidence only. It does not prove target RunPod timing and does not authorize a paid lifecycle.

## Regression suite

- Command: `python3 -m unittest discover -s post-dogfood -p 'test_pdh3*.py' -v`
- Result: `PASS`
- Tests: `136`
- Failures: `0`
- Errors: `0`
- Duration: `5.837 seconds`

## Representative Plan A/B scales

### 10,000 tasks

- Result: `GREEN`
- Exact counts: `[10000, 10000, 20000, 10000, 10000]`
- Selected index: `receipts_task_id_idx`
- Mismatched results: `[]`
- Prohibited post-index scans: `[]`
- Receipt file SHA-256: `c0b7daeca5b3ac3b130a8ffc23b70854dfbcb66ff3801ad010d9dfa97d3056ed`
- Teardown file SHA-256: `bc6286518a3caf1b504bf651f82e45e45f069f7c3caa1147071fa4e331bad33c`
- Process stopped: `true`
- Generated root removed: `true`

### 50,000 tasks

- Result: `GREEN`
- Exact counts: `[50000, 50000, 100000, 50000, 50000]`
- Selected indexes: `receipts_task_id_idx`, `projection_events_source_key_idx`
- Mismatched results: `[]`
- Prohibited post-index scans: `[]`
- Receipt file SHA-256: `b849c01273d440237dfd82416dd86c0b00f37a5bcc9e4b20d91f3f378afc1db3`
- Teardown file SHA-256: `bab048b6fb64132608a78137a0314bfeb389fe13a7650e5d9405955027b54061`
- Process stopped: `true`
- Generated root removed: `true`

### 100,000 tasks

- Result: `BLOCKED`
- Exact error: `PDH3_R12_PF2_BLOCKED:PlanABError:SQL_TIMEOUT:2af88219c4e26b7f9314bc7737975ce578297c7e9f2be9e036e77895b669a9cd`
- Mechanism: one SQL operation exhausted the frozen local 1,800-second timeout on macOS arm64.
- Interpretation: local throughput evidence is insufficient at this scale. This is not target RunPod timing evidence and cannot be promoted to GREEN.
- Failure stderr SHA-256: `28baa4d3d94ecdf4bdc0fd55ffea15dc24c61f92eab7c1bb36521e79ba6607cf`
- Teardown file SHA-256: `26f1837c91cda5397345a89869291a9d5511201d8fb8a5e5ac25e9961e546ca1`
- Preserved database-log SHA-256: `c1be4098f122c13aaa2bbac8a219f7330bd39fcae848a6560a1322a90f2b886b`
- Process stopped: `true`
- Generated root removed: `true`

## Deterministic bundle rebuild

Two independent builds under `.pdh3-runtime/r12-preflight/r6-r6-restart-20260803-r1/` produced:

- Archive bytes: `143990837`
- A archive SHA-256: `52619301a9aa0b88e5c2e3e52d668e6485ae105eb1c0f86405d681a5945be7a6`
- B archive SHA-256: `52619301a9aa0b88e5c2e3e52d668e6485ae105eb1c0f86405d681a5945be7a6`
- A bundle-receipt file SHA-256: `6026c4dd95c699fbc1110c60609f3e249834a6cc7c7a8e7cd5c33e42e4a41c7c`
- B bundle-receipt file SHA-256: `6026c4dd95c699fbc1110c60609f3e249834a6cc7c7a8e7cd5c33e42e4a41c7c`
- Manifest SHA-256: `4567fc0f2b6352a314536fe9bcbe15fd65c9509f798e67780f3fe37c8a303799`
- Remote source-set SHA-256: `668a35cd1b8120218e54bcc7b383345a4a8d671815e0ababd431a6df534d1a15`
- Host-only source-set SHA-256: `5a72f431cf7ee5775fa7e5168ff81f904a81b58bce9c2b19874b2ec679c451c7`
- Embedded attempt-history manifest SHA-256: `72877c307496cd57d910385c8aa898c779d449170f7134478eb5d2a2702cbe1e`
- Synthetic-only manifest: `true`
- Credential-free manifest: `true`
- Transferred host control plane: `false`

Both extracted bundles passed all `141` smoke tests. The smoke-receipt file hashes differ only because unittest runtime durations are recorded:

- A smoke-receipt file SHA-256: `c00faea1fa0732783f2fea1a3a8475c3d02f723edc2cf06f51b6aa739413e81d`
- B smoke-receipt file SHA-256: `537e99711bd3b65d39008ab2ed21e1b03c8ce7a217049748a71e59122e39f2af`

## Residue and safety

- Remaining Cockroach or PDH-3 workload process after teardown: `none`
- Remaining generated scale root: `none`
- Active paid RunPod worker created by this pass: `none`
- Operator-owned untracked `heap_profiler/`: `not read, staged, modified, or committed`
- Free local disk at final check: approximately `136 GiB`

## Decision

The repaired teardown and deterministic package path are locally ready for a new frozen remote-preflight packet. The 10k and 50k representative rungs are GREEN. The 100k local rung remains honestly BLOCKED on platform throughput and therefore supplies no target-scale timing claim.

The next allowed path is:

1. obtain a fresh exact paid-lifecycle and spend authorization;
2. refresh live RunPod inventory, compatible worker properties, and price;
3. freeze absolute lifecycle deadlines and one new immutable packet;
4. obtain independent GLM 5.2 GREEN over that exact packet hash;
5. only then create a paid worker for the bounded full-cardinality preflight.

The 24-hour measured campaign remains forbidden until the remote preflight completes GREEN and a separately frozen final campaign packet receives independent GREEN.
