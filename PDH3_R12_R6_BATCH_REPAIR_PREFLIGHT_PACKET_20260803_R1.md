# PDH-3 R12 R6 Batch-Repair Full-Cardinality Preflight Packet R1

- `STATUS`: `FROZEN_FOR_SAME_HASH_GLM_5_2_REVIEW__NO_WORKER_CREATED`
- `UTC_FROZEN`: `2026-08-03T07:30:59Z`
- `DECISION_REQUESTED`: Independently review this exact prospective R6-only RunPod preflight for technical adequacy, evidence integrity, bounded cost, data safety, and guaranteed teardown.
- `BUILDER_SELF_APPROVAL`: `forbidden`
- `MEASURED_24H_AUTHORIZED`: `false`

## Authority and phase boundary

- Operator authorization: `PDH3_R12_R6_BATCH_REPAIR_AUTHORIZATION_ENVELOPE_20260803_R1.md`
- Operator authorization SHA-256: `ba0999c2d2a45592502977bca677d0b68776a94729bcaf6beddbc96fcf42fe3d`
- Authorization permits at most three sequential pre-upload creation attempts, one worker at a time, a maximum successful preflight lifetime of 10 hours, and a `$12.00` aggregate campaign ceiling.
- Replacement authority ends permanently when the main bundle upload begins.
- This packet covers only PF-4, extracted Linux smoke, PF-2R, PF-5, PF-6, PF-7, PF-8, evidence retrieval, teardown, and final independent result review.
- It does not authorize or start the measured 24-hour campaign.

## Preserved failed attempt and independent classification

Campaign `ck-pdh3-r12-preflight-r6-repair6` and Pod `mzbblmsmmppz9u` remain permanently `BLOCKED` under packet SHA-256 `17585b9b4dad64d0f3311c2d42e746bc70ec91b535a74ac93902580901da0d79`.

- Blocked receipt: `PDH3_R12_R6_R6_FULL_PREFLIGHT_BLOCKED_RECEIPT_20260803_R1.md`, SHA-256 `975673a63254fd489a6de15721f3466a42058a7bfa9b8b3ac6df2402d1c861c9`.
- Retrieved evidence archive SHA-256: `071919bdcdd8ea223c8155749fc99ad8046922d276934afd196f03fe084f0058`.
- PF-4 and the 10,000-task rung were GREEN.
- The 50,000-task rung timed out because five table populations were submitted as one 1,800-second SQL command. The timeout was not a RunPod worker failure and did not begin PF-5, PF-6, PF-7, or the 24-hour measurement.
- Database teardown, final evidence retrieval, remote hash comparison, provider deletion, exact-ID 404, and empty active inventory were verified.
- A host lifecycle parser defect retried the valid runpodctl v2.8 `404/not_found` envelope; the local controller was stopped after provider absence was independently proved.
- Independent GLM 5.2 classified the primary harness blocker and lifecycle defect as valid and ruled the old packet non-retryable.

The failed attempt may not be relabeled, omitted, or reused as successful evidence.

## Research and repair decision

Research/repair decision: `PDH3_R12_R6_REPLACEMENT_RESEARCH_AND_REPAIR_DECISION_20260803_R1.md`, SHA-256 `772e84a3c609ba443dfb539a556dc8f6a9b0baad66308bcab7449862667c955b`.

Fresh qualified Grok research was attempted three times. The approved wrapper returned exit `78` each time because the model result was cancelled, malformed, or served by an unapproved model. No Grok output was accepted, and no unqualified route was used. Receipt: `PDH3_R12_R6_REPLACEMENT_GROK_RESEARCH_ATTEMPTS_BLOCKED_20260803_R1.md`, SHA-256 `ed7d99562c138a609b442e77e071c11a5247c58714390ccc5437a03008413cf3`.

The repair is based on retrieved failure evidence, prior disclosed Grok context, and current official CockroachDB guidance for batched bulk inserts, bounded statement timeouts, retry handling, and vector-index maintenance.

Prospective changes:

1. PF-2 reuses the production campaign's proven 5,000-task per-table seed path.
2. The original PF-2 shape remains one event and two receipts per task. A separately reconciled second-receipt batch links to event zero; projection rows use a separately reconciled batch.
3. Every seed path is idempotent but content-checked. Missing or mismatched rows block; `ON CONFLICT DO NOTHING` cannot conceal drift.
4. Each seed/reconciliation SQL operation is capped at 60 seconds. Each scale has one 3,600-second monotonic deadline, with 900 seconds reserved after core seed and 600 seconds reserved after reconciliation. Counts, metadata, plan capture, statistics, and DDL share that deadline.
5. The pre-created vector index remains online through seed. PF-2 proves its metadata and exact vector content. Full-cardinality PF-5 retains ANN quality testing.
6. The lifecycle guard requires a numeric 404, rejects conflicting numeric statuses, permits symbolic `not_found` only as auxiliary data, and still requires a Pod-specific absence message.
7. No product migration, cardinality, concurrency, threshold, fault schedule, evidence rule, worker shape, cost ceiling, or public claim changed.

## Exact candidate and local verification

- Candidate commit: `c79267188db620111743bd41e82408d09f447bcc`.
- Canonical PF-2 aggregate file SHA-256: `55eecf4f731bfeec7875b007f3baa9c1cf2bc1b5e1254ee7ac28b80e05454da0`.
- Canonical PF-2 aggregate receipt SHA-256: `c7e155a3e7187d38daa3e120611db596bf774e5a283ac67935522e619f3db966`.

One current-source canonical sequence ran in three fresh generated roots:

| Rung | Exact counts `(tasks, events, receipts, vectors, projections)` | Result receipt | Result |
|---|---:|---|---|
| 10,000 | `(10000, 10000, 20000, 10000, 10000)` | `fe262567cb06455a1a6c72a7853054c1f42fd50e2d59a74f9bfb3b9f86c2074a` | GREEN |
| 50,000 | `(50000, 50000, 100000, 50000, 50000)` | `bc4b1512841165553d04ae36bdc4e2d7320a198c8ea6e313805a311bd3cfe739` | GREEN |
| 100,000 | `(100000, 100000, 200000, 100000, 100000)` | `9106e950d7a01c3d41aaadd46a08088d60a82f75b94decdf397c535b6b1786c5` | GREEN |

All three rungs produced zero result mismatches, zero prohibited post-index full scans, process-stopped GREEN, and generated-root-removed GREEN. The full bundled regression plus lifecycle suite passed 160 tests across 14 programs. Secret scans passed. No paid worker was created during repair validation.

## Bound source and deterministic package

| Component | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_r6_config.py` | `c7d773b5fb996cf4cffd371f67cd4f80b5a82664cb5c332924aefa9b8c2b36a1` |
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `eb48522771f329a343620a2bc4c25f28ca3e4db7a85e5bc5791b8638445960e3` |
| `post-dogfood/pdh3_r12_r6_run_pf4.py` | `a0cff6c5f1e89bd5762216e3b407feb35aacf0839df058c5e656cddf31ab2af1` |
| `post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py` | `d374f52dabe654dfd8fc712cd693ef7723b4717d206efe54b2952d8201c091e5` |
| `post-dogfood/pdh3_r12_r6_orchestrator.py` | `4d868cf66308e627a6f2ed9e3576f83535b5a6838131784cfcb74fbf07215ccf` |
| `post-dogfood/pdh3_r12_plan_ab.py` | `2d0cb19930e553e172ae3c92c1f745722cd2659a5689dff329b99d2db105a277` |
| `post-dogfood/pdh3_r12_network_observer.py` | `8e6f72c4fa44d56f982697ee3091938f27924a5120846cba96cc6ed1f794f102` |
| `post-dogfood/pdh3_r12_remote_preflight.py` | `65c16b701869ab9f4a9e8a774b25c08d19333d6546c766588660c210c3022e44` |
| `post-dogfood/pdh3_r12_remote_launcher.py` | `52d06c3d4ca14b9f7c746c7da882272545f5ccb5fec19527234fcebe31a52149` |
| `post-dogfood/pdh3_r12_lifecycle_launch.py` | `23db1b1dfb3e41bced1c7b82220f46b43f0ffc4e4a2b871b69ca70687acbe2a1` |
| `s2-soak/lifecycle_guard.py` | `51258c2d983a6d0764485ff67ecd5e662085331758a2ce1d41813ea79652a5c6` |
| `PDH3_R12_R6_CPU_AFFINITY_AMENDMENT_20260802_R1.md` | `eb66d5f8632686c015f79c45215b234fc362863f43fc515af87d6bab4c356e55` |

Package root: `.pdh3-runtime/r12-preflight/r6-replacement-r2-candidate-20260803-r1/`.

- Archive bytes: `143995062`.
- Archive SHA-256: `15ebf96848b6aed0f860cda92006e8d4b4f5ca2e1b704417b3bc151c8d5e0aa3`.
- Bundle-receipt file SHA-256: `16b14517c6218b2696d8e508c2a3ca4569c14a7cdbec547580f636a84894a225`.
- Embedded receipt SHA-256: `e9ef394a81da8fdb457eb552c4d5015606e8e314803954109ca2caaa7054127d`.
- Manifest SHA-256: `e0774d0ec3e6f9d7931d77f979dba55d533029cb1a9d367ce91a23ab2b6067de`.
- Remote source-set SHA-256: `3c67e7a4ebf32b1d2aeb0f577d907da08d34685b1ccad6e82dc5cf4ad85a2ea4`.
- Host-only binding SHA-256: `5ab1634553bc8b71b9e3f1ae5434383547b9394d5e4b323c98cbe31a91474491`.
- Attempt-history manifest SHA-256: `72877c307496cd57d910385c8aa898c779d449170f7134478eb5d2a2702cbe1e`.
- Extracted-smoke file SHA-256: `d11d0d357d28decbdbfa743b93d9ba53d8b47995d748d540c0d92c6e33983d53`.
- Extracted-smoke receipt SHA-256: `1a34dc3f443e2e3c408a345f78d2178ddf738b98b9b71ce00f0ffa3ac7e574dd`.
- Extracted smoke: 35 Python files compiled; all 13 test programs passed; no failed checks.
- Synthetic-only: `true`; credential-free: `true`; host control plane transferred: `false`.

## Live provider, price, tool, and lifecycle binding

Provider snapshot: `PDH3_R12_R6_BATCH_REPAIR_PROVIDER_SNAPSHOT_20260803_R1.json`, SHA-256 `d8fdc34ed09d174306c807caa76ea3fff90332c122610b6ff00962b99fda8adc`.

At `2026-08-03T07:30:14Z`:

- active Pod inventory was `[]`;
- account balance was `$84.5331811339` and unrelated current spend was `$0.002/hour`;
- Secure Cloud L40S was available at `$0.99/hour`, low stock;
- allowed in-stock locations were `EU-NL-1`, `EUR-IS-2`, `US-IL-1`, `US-MO-1`, and `US-TX-4`;
- project-local RunPodCTL version was `2.8.0-22dc71f`, SHA-256 `67cc575f518d05258f35c4334422f6f730446b7b88864933ed65a05e990ea1f2`;
- both active-only and all-status inventory commands returned valid JSON; active count was zero.

The existing account credential may enter only the local controller process environment. It may not be printed, persisted, logged, committed, transferred, or injected into a Pod.

## Exact worker, cost, and deadlines

- Campaign ID: `ck-pdh3-r12-preflight-r6-batchrepair`.
- Launch window: `2026-08-03T07:40:00Z` through `2026-08-03T08:25:00Z`.
- Host closeout deadline: `2026-08-03T16:55:00Z`.
- Provider stop deadline: `2026-08-03T17:10:00Z`.
- Provider terminate deadline: `2026-08-03T17:25:00Z`.
- Maximum paid lifetime from launch-window open: 9.75 hours, below the authorized 10-hour ceiling.
- Worker: exactly one Secure Cloud `NVIDIA L40S`, one GPU, at least 24 provider vCPU and 94 GiB RAM, with the frozen effective CPU-affinity plan.
- Image: exactly `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`.
- Container disk: exactly 250 GB disposable; persistent/network volume: zero.
- Exposed service: SSH only.
- Compute ceiling: `$0.99/hour`.
- Container-disk rate: `250 * $0.10 / 720 = $0.0347222222/hour`.
- Maximum combined active rate: `$1.0247222222/hour`.
- Maximum 9.75-hour campaign charge: `$9.9910416667`, below `$12.00`.

Unknown pricing, a returned rate above either ceiling, insufficient balance, account-setting change, unexpected existing Pod, or aggregate uncertainty blocks before creation or triggers immediate teardown.

## Retry and upload law

1. At most three sequential creation attempts exist inside the 45-minute launch window.
2. Only provider placement, capacity, readiness, SSH readiness, or pre-upload shape mismatch may consume a retry.
3. Every returned worker is verified before upload: ID/name, Secure Cloud, L40S, GPU count, image, disk, zero volume, provider vCPU/RAM, observed price, datacenter, and deadlines.
4. A failed attempt is deleted and exact-ID absence plus empty campaign inventory is proved before another creation.
5. No more than one paid worker may exist at once.
6. Main-bundle upload permanently ends replacement authority. Any later failure blocks this campaign and tears down the same worker.
7. No workload, packet, source, threshold, evidence rule, or hidden input may change between attempts.

## Remote preflight acceptance contract

The one verified worker must pass:

1. **PF-4:** hardware, cgroup CPU-affinity, memory, disk, Linux runtime, tracer-root construction, network observer, supervisor, absolute deadlines, and lifecycle checks.
2. **Linux extracted smoke:** compile 35 Python files and pass all 13 test programs. Retrieve the smoke receipt on every outcome.
3. **PF-2R:** Plan A/B at 10k, 50k, and 100k tasks; exact counts; bounded, idempotent, content-reconciled batches; target-scale `SHOW INDEXES`, `EXPLAIN`, and `EXPLAIN ANALYZE`; prospective receipt and projection indexes; no prohibited post-index full scans; result equivalence; database-log preservation; teardown receipts.
4. **PF-5:** exact full cardinality of 500,000 tasks, 5,000,000 events, 1,000,000 receipts, and 250,000 vectors with reconciliation and ANN recall evidence.
5. **PF-6:** concurrency stages 10, 50, 100, 250, and 500; zero execution errors; named and aggregate histograms; p99 at most 5,000 ms; max at most 10,000 ms; gateway/observer comparisons; three complete c500 epochs.
6. **PF-7:** 900-second full-cardinality c500 growth and network proof; network evidence at most 1 GiB; every other evidence class below 80% of its limit; continuous process/resource observations; process kill, restart, exact reconciliation; partial-successor refusal; checkpoint completeness.
7. **PF-8:** stop workload; flush/fsync; retrieve all evidence; verify hashes locally; preserve raw failure evidence; stop/delete worker; prove exact-ID absence and empty active inventory; prove no SSH, transfer, supervisor, watchdog, database, or paid background process remains.

Three CockroachDB processes on one worker are one physical failure domain. The network observer provides detection and fail-closed termination, not firewall isolation. Remote success is only `GREEN_PENDING_PF8`; host closeout is only `GREEN_PENDING_FINAL_GLM`. Final R6 GREEN requires a new exact result packet and independent GLM 5.2 GREEN.

## Kill lines

Immediately block and tear down on any source, archive, packet, tool, worker, image, price, deadline, or evidence hash mismatch; secret or private-data exposure; undeclared egress; target-scale exactness failure; prohibited scan; latency or growth breach; missing checkpoint; observer gap; unbounded child operation; process leak; inability to retrieve evidence; lifecycle guard failure; cost uncertainty; or inability to prove deletion.

The operator-owned untracked `heap_profiler/` is forbidden and may not be read, staged, modified, copied, hashed, or committed.

## Required independent verdict format

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: <exact packet SHA-256>
VERDICT: GREEN | NOT_GREEN | BLOCKED | JUDGE_UNAVAILABLE
BOUNDARY_CHECK: PASS | FAIL
EVIDENCE_CHECK: PASS | FAIL
COST_CHECK: PASS | FAIL
LIFECYCLE_CHECK: PASS | FAIL
FINDINGS:
- <finding or NONE>
```
