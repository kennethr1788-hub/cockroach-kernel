# PDH-3 R12 R6 full preflight Linux-portability packet R4

Status: `FROZEN_FOR_SAME_HASH_GLM_5_2_REVIEW__NO_WORKER_CREATED`

UTC frozen: `2026-08-02T12:27:00Z`

Decision requested: review this exact prospective R6-only RunPod campaign for
safety, evidence integrity, platform correctness, cost, and teardown. The
builder cannot approve it.

## Authority and boundary

- Operator envelope:
  `PDH3_R12_R6_AUTHORIZATION_ENVELOPE_20260802_R1.md`;
  SHA-256 `e5fb1b999a84339b780a8c299817c9fa11b0aba38e582db766a2301e6594455b`.
- Kenneth authorized immediate deployment and sequential retries after each
  diagnosed and repaired failure.
- This packet authorizes only PF-4, Linux extracted smoke, PF-2R, PF-5, PF-6,
  PF-7, PF-8, and final result review.
- It does not contain or authorize any measured 24-hour branch.
- At most three pre-upload creation attempts, one worker at a time; no
  replacement after main upload; no tuning after workload evidence appears.

## Preserved failure chain and exact correction

Attempt 01 (`n3s5q9f8h3i2aj`) proved that the old host controller failed to
retrieve the Linux smoke receipt before teardown. It is preserved in
`PDH3_R12_R6_FULL_PREFLIGHT_ATTEMPT_01_BLOCKED_RECEIPT_20260802_R1.md`,
SHA-256 `7dd5d04724ea3cb31cd80de6c9f39ecaed16ae1190f5de94fa6bfcd5e982d234`.

Attempt 02 (`vp1qs5vg9e2rg8`) proved the repaired receipt path and diagnosed one
failure: `test_pdh3_local_canary.py` hardcoded macOS `/private/tmp`, absent on
Ubuntu. It is preserved in
`PDH3_R12_R6_FULL_PREFLIGHT_ATTEMPT_02_BLOCKED_RECEIPT_20260802_R1.md`,
SHA-256 `5315443125efa8bd04fde997f976f2c62584211c00321aa55a8fdf903449213e`.
Both workers were deleted; exact lookups returned 404; active inventory was
empty; neither reached full-cardinality setup, any checkpoint, or a 24-hour
clock.

Prospective repair commit:
`157d211b42b0010e7f98bc6ebfd3755976721f1d`.

The exact correction introduces one shared generated-root parent:

- Linux: `/tmp`;
- other supported local hosts: `/private/tmp`.

Both the local-canary execution path and its teardown test use that constant.
The guarded prefix remains `ck-pdh3-local-r1.` and teardown still rejects any
root outside the selected parent. No target cardinality, query, threshold,
database behavior, evidence class, network rule, cost rule, or teardown rule
changed.

Direct local verification:

- local canary tests: 15/15 GREEN;
- bundle-builder tests: 12/12 GREEN;
- Python compile and `git diff --check`: GREEN;
- A and B extracted smokes each compiled 35 Python files and ran all 13 tests
  GREEN.

## Hash-bound source and package

| File | SHA-256 |
|---|---|
| `post-dogfood/build_pdh3_scale_bundle.py` | `adddcff23a01c33c41baf427057605af017568a8746fca090e4c753c71f04deb` |
| `post-dogfood/pdh3_r12_r6_config.py` | `c7d773b5fb996cf4cffd371f67cd4f80b5a82664cb5c332924aefa9b8c2b36a1` |
| `post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py` | `e453cca2eec2d2967a392da14ece5ad9c67de196141963d953bdca0ee70c703f` |
| `post-dogfood/run_pdh3_local_canary.py` | `b44ea37e3fd6f2a8cf7ba4a41eb9467877dddb61ec3f3670bd6e84078ff9a38f` |
| `post-dogfood/test_pdh3_local_canary.py` | `ea286981c216302c7c3ca861402675d7a500b57a02d26906c983b4a5c0078bf3` |
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `eb48522771f329a343620a2bc4c25f28ca3e4db7a85e5bc5791b8638445960e3` |
| `post-dogfood/pdh3_r12_r6_run_pf4.py` | `a0cff6c5f1e89bd5762216e3b407feb35aacf0839df058c5e656cddf31ab2af1` |
| `post-dogfood/pdh3_r12_r6_orchestrator.py` | `4d868cf66308e627a6f2ed9e3576f83535b5a6838131784cfcb74fbf07215ccf` |
| `post-dogfood/pdh3_r12_lifecycle_launch.py` | `23db1b1dfb3e41bced1c7b82220f46b43f0ffc4e4a2b871b69ca70687acbe2a1` |
| `s2-soak/lifecycle_guard.py` | `70c12ea1ae19f69a43fb38100d90bda8f5e0a41ae30d2b6c509b331933a9e14d` |
| `post-dogfood/pdh3_r12_remote_preflight.py` | `65c16b701869ab9f4a9e8a774b25c08d19333d6546c766588660c210c3022e44` |
| `post-dogfood/pdh3_r12_remote_launcher.py` | `f5fcc15188f4b7540567c8af30d90d21320bd89450f566c3c6e4921a6e5868f7` |
| `post-dogfood/pdh3_r12_network_observer.py` | `8e6f72c4fa44d56f982697ee3091938f27924a5120846cba96cc6ed1f794f102` |

Fresh deterministic package root:
`.pdh3-runtime/r12-preflight/full-r6-linux-portable-20260802-r1/`.

- A/B archive SHA-256:
  `27b12ba16c3bfbda3400cda8d8bdd35b6f89fa95cae8e0fb051fb39082722ef8`;
- archive bytes: `143990873`;
- A/B bundle-receipt file SHA-256:
  `4e55c4a58c29d652dfbd8586315a1a94d9fc3bea2ebd9be0a2746082cf6cfb69`;
- embedded receipt SHA-256:
  `12f0cd7c745dd8d2d14628b294ce0715a1c0d7d73aed9b914161c80e51ba0390`;
- manifest SHA-256:
  `9af92772342a802671e155577a9f89641e3fc1ef4235d027496696a7df28642a`;
- remote source-set SHA-256:
  `92aa26d6cd0bcf94e7d972b75ea7a2b531dc835837c2c915d9fd0fc830a75985`;
- host bindings SHA-256:
  `f0304bf7fc3a2847a93c6b81b3f2a2abeb34c37ef48ddfd78676a9fed23001d1`;
- host source-set SHA-256:
  `30e689e73c6403f36dcc628b18f3f0a4610d49778d2603d04e8c2a2cfdf16d9d`;
- history manifest SHA-256:
  `72877c307496cd57d910385c8aa898c779d449170f7134478eb5d2a2702cbe1e`;
- archive verification SHA-256:
  `fc5a5f7e9c602398cd0cbea147469a18ab77235d37376a0cff89f6239a0890da`.

A/B archives and bundle receipts are byte-identical. Smoke receipts are not
required to be byte-identical because captured test-output hashes can contain
generated local roots. Local smoke is custody evidence, not remote proof.

## Provider, worker, deadlines, and spend

Provider snapshot:
`PDH3_R12_R6_FULL_PREFLIGHT_PROVIDER_SNAPSHOT_20260802_R3.json`, SHA-256
`ef7b0857ae312d98a93ea6268160cbeb703416932c4c010e041a9bedcb755217`.
At `2026-08-02T12:26:02Z`: active inventory `[]`, L40S Secure Cloud
available, balance `$85.3379271875`, current spend `$0.002/hour`, account limit
`$140`.

Worker contract:

- one Secure Cloud NVIDIA L40S, compute at most `$0.99/hour`;
- minimum 24 provider vCPU and 94 GiB RAM;
- at least 16 measured cgroup CPUs and at least 4 GiB/effective CPU;
- exact image `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- 250 GB disposable container disk; zero persistent/network volume;
- SSH key and host key pinned locally;
- placement only in `EU-NL-1`, `EUR-IS-2`, `US-IL-1`, `US-MO-1`,
  `US-NC-1`, `US-TX-3`, or `US-TX-4`;
- CLI `/tmp/runpodctl-v2.7.2-darwin-arm64`, SHA-256
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`.

Campaign:

- ID `ck-pdh3-r12-preflight-r6-full-r4`;
- launch `2026-08-02T12:28:00Z` through `2026-08-02T13:13:00Z`;
- provider stop `2026-08-02T21:58:00Z`;
- provider terminate `2026-08-02T22:13:00Z`;
- host closeout `2026-08-02T21:43:00Z`;
- shared absolute deadline across all pre-upload placement attempts.

Cost:

- active rate bound `$1.0247222222/hour` including disk;
- new maximum 9.75-hour lifecycle `$9.9910416667`;
- preserved prior R6 lineage upper bound `$0.1622`;
- total prospective lineage upper bound `$10.1532416667`;
- operator ceiling `$12.00`.

Unknown price, repricing, account-setting change, insufficient balance,
unexpected active inventory, or possible ceiling breach blocks before create
or triggers immediate teardown.

## Credentials, data, proof, and terminal law

The RunPod key remains host-process-only and must never enter URL, argv,
request body, output, receipt, archive, worker, or commit. Only frozen
synthetic data enters the worker. AWS, CockroachDB Cloud, GitHub, model and
other private credentials are forbidden, as are HOME runtime, Qdrant,
StateV2, launchd, client/production data, unrelated repos, and the operator's
untracked `heap_profiler/`.

The same worker must pass:

1. PF-4 capability, cgroup/affinity, storage, tracer, process observer, and
   residue checks.
2. Linux extracted smoke: 35 compiled files and all 13 tests; its hash-bound
   receipt is retrieved and validated on PASS, FAIL, or TIMEOUT.
3. PF-2R target-scale index/plan A/B.
4. PF-5 exact 500,000 tasks, 5,000,000 events, 1,000,000 receipts, and
   250,000 vectors, reconciliation, vector quality, EXPLAIN/ANALYZE, no
   prohibited full scan, query equivalence, and resource gates.
5. PF-6 four named families at literal concurrency 10/50/100/250/500,
   one-/three-gateway c500, observer A/B at no more than 10% p99 overhead,
   and three mixed c500 epochs; zero errors, complete accounting, p99 at most
   5,000 ms, maximum at most 10,000 ms.
6. PF-7 900 seconds literal c500, separated DB/evidence/network projections,
   network at most 1 GiB, other growth at most 80% of limits, same-host process
   kill/restart/reconciliation, restarted affinity, off-worker checkpoints,
   and partial-successor refusal.
7. PF-8 retrieve/hash evidence, close roots, delete worker, prove exact-ID 404,
   active inventory empty, and no paid/background process.

Three database processes are one physical failure domain. The network tracer
is detection plus fail-closed termination, not a firewall.

Remote success is only `GREEN_PENDING_PF8`; host success only
`GREEN_PENDING_FINAL_GLM`. Final R6 GREEN requires a fresh result packet and
direct exact-model GLM 5.2 GREEN. Any mismatch, smoke failure, threshold
failure, missing evidence, observer gap, secret/egress event, cost uncertainty,
or teardown uncertainty immediately blocks and tears down. No failed run may
be relabeled or tuned into success.

## Verdict format

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: <exact SHA-256>
VERDICT: GREEN | NOT_GREEN | BLOCKED | JUDGE_UNAVAILABLE
BOUNDARY_CHECK: PASS | FAIL
EVIDENCE_CHECK: PASS | FAIL
COST_CHECK: PASS | FAIL
LIFECYCLE_CHECK: PASS | FAIL
FINDINGS:
- <finding or NONE>
```
