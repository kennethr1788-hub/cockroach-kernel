# PDH-3 R12 R6 repaired full-cardinality preflight packet R6

- `STATUS`: `FROZEN_FOR_SAME_HASH_GLM_5_2_REVIEW__NO_WORKER_CREATED`
- `UTC_FROZEN`: `2026-08-03T05:36:43Z`
- `DECISION_REQUESTED`: Independently review this exact prospective R6-only paid RunPod preflight for safety, technical adequacy, evidence integrity, bounded cost, and guaranteed teardown.
- `BUILDER_SELF_APPROVAL`: `forbidden`
- `MEASURED_24H_AUTHORIZED`: `false`

## Authority and phase boundary

- Operator authorization: `PDH3_R12_R6_R6_AUTHORIZATION_ENVELOPE_20260803_R1.md`
- Operator authorization SHA-256: `e91d55a970f942338cb6d8c65ee96ebf26f2d433cdc0a07c9829686e16355cd2`
- Authorization permits at most three sequential pre-upload creation attempts, one worker at a time, a maximum successful preflight lifetime of 10 hours, and a `$12.00` aggregate R6 ceiling.
- Replacement authority ends permanently when the main bundle is uploaded to one verified worker.
- This packet covers only PF-4, extracted Linux smoke, PF-2R, PF-5, PF-6, PF-7, PF-8, evidence retrieval, teardown, and final independent result review.
- It does not authorize or start the measured 24-hour campaign.

## Preserved prior failure

R6 R5 remains `BLOCKED`. Pod `r2iqulx4yfyoz8` is deleted and its campaign inventory is empty. Its 10,000-task PF-2R scale was GREEN, but teardown called undefined `file_sha256`, raised `NameError`, prevented the terminal result receipt, and caused the observer to fail closed. The historical failure is bound by:

- R5 packet SHA-256: `6dabda20b7317e93961977423b58130a4356304da1ff40b75d02fdd703701218`
- R5 final evidence SHA-256: `1c5dfdadb2ca52196d352a585f2b24aceec614402af714a6e9ba8ab490d3ad00`
- R5 blocked-and-repair receipt SHA-256: `35a9f270d9d9934d3d12ec757bc62fca35db6921625bfa2f0181e930ca1cbf2a`

R5 may not be relabeled, omitted, or reused as successful evidence.

## Exact repair and local verification

Candidate commit: `01a92a54c2a6323029c0e95b7ee6a988f0cf2788`.

The R5 repair adds a streaming `file_sha256(path)` helper, isolates database-log preservation, and adds regression coverage for that exact teardown path. No workload, cardinality, query matrix, index decision, threshold, product behavior, evidence rule, network rule, cost rule, or teardown requirement changed.

Local headroom receipt: `PDH3_R12_LOCAL_HEADROOM_PREFLIGHT_RECEIPT_20260803_R1.md`, SHA-256 `125b995dd42b51a7e7d7bd88baad5be337f1ac29a25c06f9656841107a7b2ce0`.

- `136/136` PDH-3 regression tests passed.
- 10,000-task Plan A/B: GREEN, exact counts, expected index chosen, no mismatches, no prohibited post-index scan, teardown GREEN.
- 50,000-task Plan A/B: GREEN, exact counts, both prospective indexes chosen, no mismatches, no prohibited post-index scan, teardown GREEN.
- 100,000-task Plan A/B: local macOS arm64 SQL operation hit the frozen 1,800-second timeout and remained BLOCKED; process stopped, generated root removed, log preserved, teardown GREEN.
- The local 100,000-task timeout is a platform-throughput limitation and supplies no target RunPod timing proof.
- No CockroachDB or PDH-3 process, generated root, or paid RunPod worker remained.

## Bound source and deterministic package

| Component | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_r6_config.py` | `c7d773b5fb996cf4cffd371f67cd4f80b5a82664cb5c332924aefa9b8c2b36a1` |
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `eb48522771f329a343620a2bc4c25f28ca3e4db7a85e5bc5791b8638445960e3` |
| `post-dogfood/pdh3_r12_r6_run_pf4.py` | `a0cff6c5f1e89bd5762216e3b407feb35aacf0839df058c5e656cddf31ab2af1` |
| `post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py` | `d374f52dabe654dfd8fc712cd693ef7723b4717d206efe54b2952d8201c091e5` |
| `post-dogfood/pdh3_r12_r6_orchestrator.py` | `4d868cf66308e627a6f2ed9e3576f83535b5a6838131784cfcb74fbf07215ccf` |
| `post-dogfood/pdh3_r12_plan_ab.py` | `f2cd78d2eb0739ccc86f97d639d97d5e250ffdbd457ae7063a7b8a4acdbf7a8d` |
| `post-dogfood/pdh3_r12_network_observer.py` | `8e6f72c4fa44d56f982697ee3091938f27924a5120846cba96cc6ed1f794f102` |
| `post-dogfood/pdh3_r12_remote_preflight.py` | `65c16b701869ab9f4a9e8a774b25c08d19333d6546c766588660c210c3022e44` |
| `post-dogfood/pdh3_r12_remote_launcher.py` | `52d06c3d4ca14b9f7c746c7da882272545f5ccb5fec19527234fcebe31a52149` |
| `post-dogfood/pdh3_r12_lifecycle_launch.py` | `23db1b1dfb3e41bced1c7b82220f46b43f0ffc4e4a2b871b69ca70687acbe2a1` |
| `s2-soak/lifecycle_guard.py` | `70c12ea1ae19f69a43fb38100d90bda8f5e0a41ae30d2b6c509b331933a9e14d` |
| `PDH3_R12_R6_CPU_AFFINITY_AMENDMENT_20260802_R1.md` | `eb66d5f8632686c015f79c45215b234fc362863f43fc515af87d6bab4c356e55` |

Package root: `.pdh3-runtime/r12-preflight/r6-r6-restart-20260803-r1/a/`.

- Archive bytes: `143990837`
- A/B archive SHA-256: `52619301a9aa0b88e5c2e3e52d668e6485ae105eb1c0f86405d681a5945be7a6`
- A/B bundle-receipt file SHA-256: `6026c4dd95c699fbc1110c60609f3e249834a6cc7c7a8e7cd5c33e42e4a41c7c`
- Embedded receipt SHA-256: `9fcf6d0a2964c67c8eeb4383eab0b1d2052393a6c8cb2c5a25afc1f0d03f9824`
- Manifest SHA-256: `4567fc0f2b6352a314536fe9bcbe15fd65c9509f798e67780f3fe37c8a303799`
- Remote source-set SHA-256: `668a35cd1b8120218e54bcc7b383345a4a8d671815e0ababd431a6df534d1a15`
- Host-only source-set SHA-256: `5a72f431cf7ee5775fa7e5168ff81f904a81b58bce9c2b19874b2ec679c451c7`
- Attempt-history manifest SHA-256: `72877c307496cd57d910385c8aa898c779d449170f7134478eb5d2a2702cbe1e`
- Synthetic-only: `true`
- Credential-free: `true`
- Host control plane transferred: `false`
- Two independent extracted smokes: `141/141` tests PASS in each build.

## Live provider, price, and tool binding

Provider snapshot: `PDH3_R12_R6_FULL_PREFLIGHT_PROVIDER_SNAPSHOT_20260803_R6.json`, SHA-256 `55e885c3852cc278f18ed9c8ec81e9634634da00a96bfd7d6eb76445ca84cf07`.

At `2026-08-03T05:36:43Z`:

- Active Pod inventory: `[]`.
- Account balance: `$85.1639031207`.
- Current unrelated account spend: `$0.002/hour`.
- Secure L40S: available, low stock, `$0.99/hour`, 48 GiB VRAM.
- Available allowed locations: `EU-NL-1`, `EUR-IS-2`, `US-MO-1`, `US-TX-3`, and `US-TX-4`; `US-IL-1` and `US-NC-1` reported no L40S stock but remain harmless allowed fallbacks.
- Official container-disk price: `$0.10/GB/month`.
- Project-local RunPodCTL: version `2.8.0-22dc71f`, SHA-256 `67cc575f518d05258f35c4334422f6f730446b7b88864933ed65a05e990ea1f2`.

The tool is project-local, not a global install. The existing account credential may enter only the local controller process environment; it may not be printed, persisted, logged, committed, transferred, or injected into a Pod.

## Exact worker, cost, and deadlines

- Campaign ID: `ck-pdh3-r12-preflight-r6-repair6`.
- Launch window: `2026-08-03T05:46:06Z` through `2026-08-03T06:31:06Z`.
- Host closeout deadline: `2026-08-03T15:01:06Z`.
- Provider stop deadline: `2026-08-03T15:16:06Z`.
- Provider terminate deadline: `2026-08-03T15:31:06Z`.
- Maximum successful paid lifetime: `9.75 hours`, below the authorized 10-hour ceiling.
- Worker: exactly one Secure Cloud `NVIDIA L40S`, one GPU, at least 24 provider vCPU and 94 GiB RAM, with the frozen effective CPU-affinity plan.
- Image: exactly `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`.
- Container disk: exactly `250 GB`, disposable.
- Persistent or network volume: `0 GB`.
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
6. Main-bundle upload permanently ends replacement authority. Any later failure blocks R6 and tears down the same worker.
7. No workload, packet, source, threshold, evidence rule, or hidden input may change between attempts.

## Remote preflight acceptance contract

The one verified worker must pass:

1. **PF-4:** hardware, cgroup CPU-affinity, memory, disk, Linux runtime, tracer-root construction, network observer, supervisor, and deadline checks.
2. **Linux extracted smoke:** compile 35 Python files and pass all 13 test programs; the smoke receipt is retrieved on every outcome.
3. **PF-2R:** Plan A/B at 10k, 50k, and 100k tasks; exact counts; target-scale `SHOW INDEXES`, `EXPLAIN`, and `EXPLAIN ANALYZE`; prospective receipt and projection indexes; no prohibited post-index full scans; result equivalence; database-log preservation; teardown receipts.
4. **PF-5:** exact full cardinality of 500,000 tasks, 5,000,000 events, 1,000,000 receipts, and 250,000 vectors with reconciliation and ANN recall evidence.
5. **PF-6:** concurrency stages 10, 50, 100, 250, and 500; zero execution errors; named and aggregate histograms; p99 no more than 5,000 ms; max no more than 10,000 ms; gateway/observer comparisons; three complete c500 epochs.
6. **PF-7:** 900-second full-cardinality c500 growth and network proof; network evidence no more than 1 GiB; every other evidence class below 80% of its limit; continuous process/resource observations; process kill, restart, and exact reconciliation; partial-successor refusal; checkpoint completeness.
7. **PF-8:** stop workload, flush/fsync, retrieve all evidence, verify hashes locally, preserve raw failure evidence, stop/delete worker, prove exact-ID absence and empty campaign inventory, and prove no SSH, transfer, supervisor, watchdog, database, or paid background process remains.

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
