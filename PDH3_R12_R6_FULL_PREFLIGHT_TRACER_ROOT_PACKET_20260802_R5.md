# PDH-3 R12 R6 tracer-root preflight packet R5

Status: `FROZEN_FOR_SAME_HASH_GLM_5_2_REVIEW__NO_WORKER_CREATED`

UTC frozen: `2026-08-02T12:39:00Z`

Decision requested: review this exact prospective R6-only RunPod campaign for
safety, tracer correctness, evidence integrity, cost, and teardown. The builder
cannot approve it.

## Authority and phase boundary

- Operator envelope SHA-256:
  `e5fb1b999a84339b780a8c299817c9fa11b0aba38e582db766a2301e6594455b`.
- Kenneth authorized immediate deployment and sequential diagnosed/repaired
  retries.
- This is only the full remote diagnostic preflight: PF-4, Linux smoke, PF-2R,
  PF-5, PF-6, PF-7, PF-8, and a final result review.
- No measured 24-hour branch exists or is authorized.
- Three pre-upload placement attempts maximum, one paid worker at a time, no
  replacement after main upload, no tuning after workload evidence.

## Preserved failure progression

1. Attempt 01, Pod `n3s5q9f8h3i2aj`: smoke receipt was not retrieved before
   teardown. Preserved failure receipt SHA-256
   `7dd5d04724ea3cb31cd80de6c9f39ecaed16ae1190f5de94fa6bfcd5e982d234`.
2. Attempt 02, Pod `vp1qs5vg9e2rg8`: repaired receipt identified a macOS
   `/private/tmp` literal. Preserved receipt SHA-256
   `5315443125efa8bd04fde997f976f2c62584211c00321aa55a8fdf903449213e`.
3. Attempt 03, Pod `em5br6eoyd38r4`: Linux smoke passed all 13 tests, then the
   launcher rejected a nonexistent second tracer library directory. Preserved
   receipt SHA-256
   `8f675181ed651ffd126a86ea23a89136dccffa44496255cc0ec226b15cdf3535`.

All three Pods were deleted with exact-ID 404 and empty active inventory. None
started full-cardinality setup, emitted a measured checkpoint, or started a
24-hour clock.

## Exact prospective repair

Commit: `829b8f29c4e28f9274fca818709f6f790ce95073`.

The extracted Ubuntu `libunwind8` package owns the multiarch library directory
`tracer/usr/lib/x86_64-linux-gnu`. The former host and launcher additionally
required `tracer/lib/x86_64-linux-gnu`, which the extracted packages do not
materialize. The repair:

- sets `LD_LIBRARY_PATH` to exactly the package-owned `/usr/lib` multiarch root;
- requires that one directory to exist and not be a symlink;
- leaves system libc resolution to the loader's normal system paths;
- preserves the exact hash-pinned strace binary and package artifacts;
- changes no workload, cardinality, query, threshold, evidence, network, cost,
  or teardown behavior.

Tests: remote-launcher 3/3 GREEN; bundle-builder 12/12 GREEN; A/B extracted
smokes compiled 35 Python files and ran all 13 test programs GREEN; compile and
`git diff --check` GREEN.

## Bound source and deterministic package

| File | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py` | `d374f52dabe654dfd8fc712cd693ef7723b4717d206efe54b2952d8201c091e5` |
| `post-dogfood/pdh3_r12_remote_launcher.py` | `52d06c3d4ca14b9f7c746c7da882272545f5ccb5fec19527234fcebe31a52149` |
| `post-dogfood/test_pdh3_r12_remote_launcher.py` | `c01caff32297fcf47a31d2a669341091635dc98394ea8ee5a52ae9282b697790` |
| `post-dogfood/build_pdh3_scale_bundle.py` | `adddcff23a01c33c41baf427057605af017568a8746fca090e4c753c71f04deb` |
| `post-dogfood/pdh3_r12_r6_config.py` | `c7d773b5fb996cf4cffd371f67cd4f80b5a82664cb5c332924aefa9b8c2b36a1` |
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `eb48522771f329a343620a2bc4c25f28ca3e4db7a85e5bc5791b8638445960e3` |
| `post-dogfood/pdh3_r12_r6_run_pf4.py` | `a0cff6c5f1e89bd5762216e3b407feb35aacf0839df058c5e656cddf31ab2af1` |
| `post-dogfood/pdh3_r12_r6_orchestrator.py` | `4d868cf66308e627a6f2ed9e3576f83535b5a6838131784cfcb74fbf07215ccf` |
| `post-dogfood/pdh3_r12_lifecycle_launch.py` | `23db1b1dfb3e41bced1c7b82220f46b43f0ffc4e4a2b871b69ca70687acbe2a1` |
| `s2-soak/lifecycle_guard.py` | `70c12ea1ae19f69a43fb38100d90bda8f5e0a41ae30d2b6c509b331933a9e14d` |
| `post-dogfood/pdh3_r12_remote_preflight.py` | `65c16b701869ab9f4a9e8a774b25c08d19333d6546c766588660c210c3022e44` |
| `post-dogfood/pdh3_r12_network_observer.py` | `8e6f72c4fa44d56f982697ee3091938f27924a5120846cba96cc6ed1f794f102` |

Package root:
`.pdh3-runtime/r12-preflight/full-r6-tracer-lib-20260802-r1/`.

- A/B archive SHA-256:
  `06bbc9567967998bee21e5c5cd42e44b688c52e3ca4b8a0d78577eaad06b9a99`;
- archive bytes `143990825`;
- A/B bundle-receipt file SHA-256:
  `88220991ab7f25663e801450a44490a9c4cc57f2ff64d317b3a61aeb0099b110`;
- embedded receipt SHA-256:
  `0044ec201e5483d3fc87b575516229c0da37e77ca12d618e144f3a49de7fc41c`;
- manifest SHA-256:
  `18d33cce28e65c9415992ba18e4b4e4749114a5d6765760ac4bbfe0eae12902c`;
- remote source-set SHA-256:
  `a7cfb3e35166be0a2735f023a08c860d23fb1fdf4e489ecb401af29af20c3aca`;
- host bindings SHA-256:
  `39c62c13b478166702ba6ebe62ca3a2cb19debb98250454089f73dfed5220e48`;
- host source-set SHA-256:
  `5a72f431cf7ee5775fa7e5168ff81f904a81b58bce9c2b19874b2ec679c451c7`;
- history manifest SHA-256:
  `72877c307496cd57d910385c8aa898c779d449170f7134478eb5d2a2702cbe1e`;
- archive verification SHA-256:
  `107cb8440eacc9db2df4f3f29143202ea5f3ec36af7e0416acb974a9cadc1002`.

A/B archives and receipts are byte-identical. Local smoke is custody evidence,
not remote performance evidence.

## Provider, worker, cost, and deadlines

Snapshot `PDH3_R12_R6_FULL_PREFLIGHT_PROVIDER_SNAPSHOT_20260802_R4.json`,
SHA-256 `2202cb9d3ac4bd3e296475629cd8dcd810d549319e9ffac41d8806a87bb48dcd`:
at `2026-08-02T12:38:20Z`, active inventory `[]`, Secure L40S available,
balance `$85.3180675125`, current spend `$0.002/hour`, account limit `$140`.

- Campaign `ck-pdh3-r12-preflight-r6-full-r5`.
- Launch: `2026-08-02T12:40:00Z` through `2026-08-02T13:25:00Z`.
- Provider stop: `2026-08-02T22:10:00Z`.
- Provider terminate: `2026-08-02T22:25:00Z`.
- Host closeout: `2026-08-02T21:55:00Z`.
- One Secure Cloud L40S, at most `$0.99/hour`, minimum 24 vCPU/94 GiB,
  at least 16 measured cgroup CPUs and 4 GiB/effective CPU.
- Exact image `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`, 250 GB
  disposable disk, zero persistent/network volume, pinned SSH host key.
- Allowed datacenters: `EU-NL-1`, `EUR-IS-2`, `US-IL-1`, `US-MO-1`,
  `US-NC-1`, `US-TX-3`, `US-TX-4`.

Total active rate bound is `$1.0247222222/hour`; new 9.75-hour upper bound is
`$9.9910416667`; preserved lineage upper bound is `$0.1918`; prospective total
is `$10.1828416667`, under the `$12.00` ceiling. Unknown price, repricing,
account-setting change, insufficient balance, unexpected inventory, or ceiling
uncertainty blocks before create or tears down.

## Proof and terminal law

The key remains host-process-only and never enters URL, argv, body, logs,
receipts, hashes, archive, worker, or commit. Only frozen synthetic data is
allowed; all private credentials, HOME runtime, Qdrant, StateV2, launchd,
client/production data, unrelated repos, and `heap_profiler/` are forbidden.

One worker must pass: PF-4 hardware/cgroup/storage/tracer/observer; Linux smoke
(35 files, 13 tests, receipt retrieved on every outcome); PF-2R target plan A/B;
PF-5 exact 500k tasks/5M events/1M receipts/250k vectors and reconciliation;
PF-6 concurrency 10/50/100/250/500 with zero errors, p99 <= 5,000 ms and max
<= 10,000 ms, gateway and observer A/B, three c500 epochs; PF-7 900-second c500
growth, network <= 1 GiB, other growth <= 80% limits, process kill/restart,
affinity, checkpoints, partial-successor refusal; PF-8 evidence retrieval,
hash verification, root closeout, deletion, exact-ID 404, empty inventory, and
no paid/background process.

Three DB processes are one physical failure domain. Network tracing is
detection plus fail-closed termination, not a firewall. Remote success is only
`GREEN_PENDING_PF8`; host success only `GREEN_PENDING_FINAL_GLM`. Final R6
GREEN requires a fresh result packet and exact-model GLM 5.2 GREEN. Any failure,
mismatch, missing evidence, threshold breach, observer gap, secret/egress event,
cost uncertainty, or teardown uncertainty blocks and tears down; no failed run
may be relabeled.

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
