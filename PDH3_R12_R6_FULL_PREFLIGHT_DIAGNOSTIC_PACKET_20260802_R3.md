# PDH-3 R12 R6 full remote preflight diagnostic packet R3

Status: `FROZEN_FOR_SAME_HASH_GLM_5_2_REVIEW__NO_WORKER_CREATED`

UTC frozen: `2026-08-02T12:13:00Z`

Builder: `Codex / Icarus`

Decision requested: determine whether this exact prospective R6-only paid
preflight is bounded, fail-closed, evidence-preserving, and safe to execute.
The builder cannot approve this packet.

## 1. Authority and hard phase boundary

Operator envelope:

- file: `PDH3_R12_R6_AUTHORIZATION_ENVELOPE_20260802_R1.md`;
- SHA-256: `e5fb1b999a84339b780a8c299817c9fa11b0aba38e582db766a2301e6594455b`.

Kenneth subsequently authorized immediate deployment and continuous sequential
retries after diagnosis and repair. This packet keeps the stricter existing
limits: at most three pre-upload creation attempts, exactly one paid worker at
a time, no replacement after main upload, a `$0.99/hour` compute ceiling, and
the `$12.00` aggregate R6 lineage ceiling.

This packet authorizes only:

`PF-4 capability -> extracted-bundle smoke -> PF-2R plan proof -> PF-5 setup ->
PF-6 query matrix -> PF-7 15-minute growth/fault/interruption proof -> PF-8
retrieval and teardown -> result-packet independent review`.

It does not authorize a measured 24-hour campaign. The remote entry point has
no 24-hour branch and every terminal receipt must state
`measured_24h_started: false`. A later 24-hour run requires a separate final
same-hash packet and fresh independent GREEN after R6 closes.

## 2. Preserved failed lifecycle and prospective repair

The prior campaign is immutable failed evidence:

- campaign: `ck-pdh3-r12-preflight-r6-full-r2`;
- Pod: `n3s5q9f8h3i2aj`, deleted;
- failure receipt:
  `PDH3_R12_R6_FULL_PREFLIGHT_ATTEMPT_01_BLOCKED_RECEIPT_20260802_R1.md`;
- failure-receipt SHA-256:
  `7dd5d04724ea3cb31cd80de6c9f39ecaed16ae1190f5de94fa6bfcd5e982d234`;
- terminal blocker: `REMOTE_EXTRACTED_SMOKE_FAILED`;
- full-cardinality setup: not started;
- measured checkpoints: zero;
- 24-hour clock: not started;
- teardown: exact Pod lookup 404 and campaign active inventory empty.

The prior remote smoke wrote a detailed result before returning nonzero, but
the host runner raised before retrieving it and correctly deleted the worker.
Therefore the prior evidence cannot identify the failing Linux check and cannot
be treated as product or durability evidence.

Prospective repair commit:
`fdd576572a5125481e5005c22862d55fc28b9e97`.

The repair:

1. emits a v3 smoke receipt with per-check PASS/FAIL/TIMEOUT state, SHA-256,
   byte counts, and at most 4096 source bytes of bounded UTF-8 diagnostic tail;
2. normalizes smoke subprocess timeouts instead of losing the receipt;
3. retrieves the remote smoke receipt before interpreting command failure;
4. validates the receipt hash, archive binding, diagnostic bound, 13-test
   cardinality, failed-check derivation, and GREEN consistency;
5. writes a host diagnostic receipt before fail-closed teardown;
6. does not change target cardinality, query load, thresholds, topology,
   evidence requirements, or teardown law.

Local direct evidence after the repair:

- `post-dogfood/test_build_pdh3_scale_bundle.py`: 12/12 GREEN;
- `post-dogfood/test_pdh3_r12_r6_config.py`: 4/4 GREEN;
- Python compile gate: GREEN;
- `git diff --check`: GREEN;
- extracted A/B local smokes: each compiled 35 Python files and ran all 13
  bundled tests GREEN;
- unrelated untracked `heap_profiler/` remains excluded and untouched.

## 3. Source and package custody

| Bound file | SHA-256 |
|---|---|
| `post-dogfood/build_pdh3_scale_bundle.py` | `adddcff23a01c33c41baf427057605af017568a8746fca090e4c753c71f04deb` |
| `post-dogfood/pdh3_r12_r6_config.py` | `c7d773b5fb996cf4cffd371f67cd4f80b5a82664cb5c332924aefa9b8c2b36a1` |
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `eb48522771f329a343620a2bc4c25f28ca3e4db7a85e5bc5791b8638445960e3` |
| `post-dogfood/pdh3_r12_r6_run_pf4.py` | `a0cff6c5f1e89bd5762216e3b407feb35aacf0839df058c5e656cddf31ab2af1` |
| `post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py` | `e453cca2eec2d2967a392da14ece5ad9c67de196141963d953bdca0ee70c703f` |
| `post-dogfood/pdh3_r12_r6_orchestrator.py` | `4d868cf66308e627a6f2ed9e3576f83535b5a6838131784cfcb74fbf07215ccf` |
| `post-dogfood/pdh3_r12_lifecycle_launch.py` | `23db1b1dfb3e41bced1c7b82220f46b43f0ffc4e4a2b871b69ca70687acbe2a1` |
| `s2-soak/lifecycle_guard.py` | `70c12ea1ae19f69a43fb38100d90bda8f5e0a41ae30d2b6c509b331933a9e14d` |
| `post-dogfood/pdh3_r12_preflight_supervisor.py` | `23d5881fbe3620cda46f71b477a2e96d69033f8c22ae667eac218e6116317a26` |
| `post-dogfood/pdh3_r12_remote_preflight.py` | `65c16b701869ab9f4a9e8a774b25c08d19333d6546c766588660c210c3022e44` |
| `post-dogfood/pdh3_r12_remote_launcher.py` | `f5fcc15188f4b7540567c8af30d90d21320bd89450f566c3c6e4921a6e5868f7` |
| `post-dogfood/pdh3_r12_network_observer.py` | `8e6f72c4fa44d56f982697ee3091938f27924a5120846cba96cc6ed1f794f102` |
| `post-dogfood/pdh3_r12_cpu_affinity.py` | `87de9fb5d02fb1eee468601058086e34dfd4a553765b312672f59584e61dd707` |
| `post-dogfood/pdh3_r12_plan_ab.py` | `820661cf5eb80a6b8d787d426187a86ca772f46a47606207a053cd7c9b435b3f` |
| `post-dogfood/pdh3_r12_checkpoint.py` | `cfe0defb82cc6b8d29f6bc986689e17e89ede572fa8df5270a2d30590cf1ca90` |

Fresh deterministic package root:
`.pdh3-runtime/r12-preflight/full-r6-smoke-diagnostic-20260802-r1/`.

- A/B archive SHA-256:
  `333488646b1635f2979373512a4d577c0a28a1272345a065d9904f8cd51d59f8`;
- archive bytes: `143990721`;
- A/B bundle-receipt file SHA-256:
  `ee73ac8e589d30056dd5910d812ed6a1d6b0ded85a07b73cb0b2dd2502905343`;
- embedded receipt SHA-256:
  `ac76db0bddcd19b64ad912803725fa87011cc83e8ff570ffc9d0870f755c56d7`;
- manifest SHA-256:
  `857bc1a9fdf9f003b73dcf3e6905497f6fd053d694e1a9a9632064e0dbe9e731`;
- remote source-set SHA-256:
  `fb727e724929e571cdfdf818f85c73e1b78e3409aa9032debf2fe372f420f49a`;
- host-only bindings SHA-256:
  `f0304bf7fc3a2847a93c6b81b3f2a2abeb34c37ef48ddfd78676a9fed23001d1`;
- host-only source-set SHA-256:
  `30e689e73c6403f36dcc628b18f3f0a4610d49778d2603d04e8c2a2cfdf16d9d`;
- history-manifest SHA-256:
  `72877c307496cd57d910385c8aa898c779d449170f7134478eb5d2a2702cbe1e`;
- archive-verification SHA-256:
  `1f01367f6eee5384cf460f4d002e8e23a505267115d9436bec018df75e7c49e7`.

The A/B smoke receipts differ only because captured test-output hashes can
include generated temporary-root names. They are not claimed byte-identical.
The transfer archives and bundle receipts are byte-identical. Local smokes are
custody/executability evidence only, never target-scale or Linux proof.

## 4. Current provider and worker contract

Provider snapshot:

- file: `PDH3_R12_R6_FULL_PREFLIGHT_PROVIDER_SNAPSHOT_20260802_R2.json`;
- SHA-256:
  `550e1df814c9a7793a2ceb8cf43b5d87e58ce88f9f016bba0f33e5a200b133ca`;
- observed UTC: `2026-08-02T12:12:12Z`;
- active inventory: `[]`;
- Secure Cloud L40S: available;
- balance: `$85.3585483375`;
- current spend: `$0.002/hour`;
- account spend limit: `$140`.

Exact worker request and readback:

- Secure Cloud; exactly one NVIDIA L40S;
- GraphQL minimum 24 vCPU and 94 GiB RAM;
- returned vCPU at least 24, RAM at least 94 GiB, and measured real cgroup
  effective CPUs at least 16;
- deterministic affinity plan preserving at least 4 GiB per effective CPU;
- image `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- 250 GB disposable container disk; zero persistent/network volume;
- compute rate at most `$0.99/hour`;
- SSH host key freshly scanned and pinned;
- allowed datacenters exactly `EU-NL-1`, `EUR-IS-2`, `US-IL-1`, `US-MO-1`,
  `US-NC-1`, `US-TX-3`, and `US-TX-4`.

Bound CLI: `/tmp/runpodctl-v2.7.2-darwin-arm64`, version
`2.7.2-309512b`, SHA-256
`a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`.

## 5. Campaign, retry, cost, and deadlines

- campaign: `ck-pdh3-r12-preflight-r6-full-r3`;
- attempt suffixes: `-01`, `-02`, `-03`;
- launch opens: `2026-08-02T12:14:00Z`;
- launch closes: `2026-08-02T12:59:00Z`;
- provider stop: `2026-08-02T21:44:00Z`;
- provider terminate: `2026-08-02T21:59:00Z`;
- host closeout: `2026-08-02T21:29:00Z`;
- at most three creation attempts, one worker at a time;
- no replacement after any PF-4 semantic result or main-upload start;
- every failed pre-upload Pod must be deleted, exact-ID absent, and active
  inventory empty before another creation attempt.

The absolute shared terminate deadline prevents retry multiplication.

- compute rate: `$0.99/hour`;
- disk rate bound: `250 * $0.10 / 720 = $0.0347222222/hour`;
- total active rate bound: `$1.0247222222/hour`;
- new maximum paid window: `9.75 hours`;
- new lifecycle upper bound: `$9.9910416667`;
- preserved prior R6 upper bound before the blocked R2 campaign: `$0.1024722222`;
- blocked R2 worker upper bound: `106.793 seconds`, `$0.030398`;
- aggregate lineage upper bound: `$10.1239118889`;
- operator ceiling: `$12.00`.

Unknown/repriced cost, account-setting change, insufficient balance, unexpected
active inventory, or any upper-bound breach blocks before creation or triggers
immediate teardown.

Retries are only for pre-upload provider/capacity, returned-shape, SSH
metadata, host-key, or readiness failures. Hash, source, smoke, capability,
semantic, secret, egress, evidence, and teardown failures stop for diagnosis
under a new reviewed packet. The repaired remote smoke is therefore both a
gate and a diagnostic; it cannot be bypassed.

## 6. Credential, data, and containment boundary

The RunPod API credential is read only by the authorized host controller and
injected into its environment. It must never enter a URL, request body, argv,
stdout, stderr, receipt, hash, archive, worker, or commit. Raw provider error
bodies are not persisted. Credential exposure is terminal.

Only frozen synthetic data enters the worker. No AWS, CockroachDB Cloud,
GitHub, model, or other private credential is transferred. HOME runtime, live
memory, Qdrant, StateV2, launchd, client/production data, unrelated repos, and
`heap_profiler/` are forbidden.

## 7. Exact proof obligations

The same worker must pass:

1. PF-4 provider/cgroup/affinity, memory ratio, disposable disk, fsync,
   streaming process-tree observation, resource accounting, tracer hash, and
   zero residue.
2. Repaired extracted-bundle Linux smoke: compile 35 Python files and run all
   13 test programs; retrieve and validate the receipt whether GREEN, FAIL, or
   TIMEOUT.
3. PF-2R isolated target-plan/index A/B on synthetic input.
4. PF-5 exact setup: 500,000 tasks, 5,000,000 events, 1,000,000 receipts,
   250,000 vectors; exact reconciliation; vector quality; target-scale
   EXPLAIN/ANALYZE; prohibited full scans absent after index; query-result
   equivalence; resource gates.
5. PF-6 four named query families at literal concurrency 10, 50, 100, 250,
   and 500; one- and three-gateway c500; observer A/B at no more than 10% p99
   overhead; three complete mixed c500 epochs. Every histogram must account for
   every operation, have zero errors, p99 at most 5,000 ms, and maximum at most
   10,000 ms.
6. PF-7 900 seconds literal c500 growth measurement; separate database,
   evidence, and network projections; projected network at most 1 GiB and
   other evidence/database at most 80% of their frozen limits; same-host
   process kill/restart/reconciliation; restarted-node affinity proof;
   off-worker checkpoint retrieval/ack; partial-successor interruption refusal.
7. PF-8 retrieve terminal semantic/network receipts and best-effort archive;
   verify hashes; close local Cockroach roots; delete worker; prove exact-ID
   absence and empty active inventory; leave no paid background process.

Three Cockroach processes share one physical worker and are not independent
failure domains. The network tracer observes and fail-closes on external
network syscalls; it is not a firewall and does not claim prevention.

## 8. Terminal law

Remote success is only `GREEN_PENDING_PF8`. Host success is only
`GREEN_PENDING_FINAL_GLM`. Final R6 GREEN requires a newly frozen result packet
and direct GLM 5.2 GREEN over its exact hash.

Immediate kill and teardown occurs on any source/hash/receipt mismatch, smoke
failure, missing evidence, threshold failure, secret/private exposure,
undeclared egress, cost uncertainty, worker-shape mismatch, process leak,
observer gap, or inability to prove teardown. A non-GREEN run remains failed
evidence and cannot be tuned or relabeled.

## 9. Requested independent verdict format

Return exactly:

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
