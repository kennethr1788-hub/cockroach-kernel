# PDH-3 R12 R6 full remote preflight packet R1

Status: `FROZEN_FOR_SAME_HASH_GLM_5_2_REVIEW__NO_WORKER_CREATED`

UTC frozen: `2026-08-02T11:40:21Z`

Builder: `Codex / Icarus`

Decision requested: determine whether this exact prospective R6-only paid
preflight is sufficiently bounded, fail-closed, evidence-preserving, and safe
to execute. This packet cannot self-approve.

## 1. Authority and phase boundary

The operator authorization is:

- `PDH3_R12_R6_AUTHORIZATION_ENVELOPE_20260802_R1.md`;
- SHA-256:
  `e5fb1b999a84339b780a8c299817c9fa11b0aba38e582db766a2301e6594455b`.

The operator subsequently authorized continued sequential creation retries,
with diagnosis and repair after failures. This packet retains the stricter
mechanical limit of three creation attempts, one worker at a time, and the
existing `$12.00` aggregate R6 ceiling.

This packet authorizes only a full-cardinality R6 diagnostic preflight:

`PF-4 capability -> PF-2R plan proof -> PF-5 setup -> PF-6 query matrix ->
PF-7 15-minute growth/fault/interruption proof -> PF-8 host retrieval and
teardown -> final independent review`.

It does not authorize the measured 24-hour campaign. The remote preflight
entry point has no measured-24-hour branch and its terminal receipt must state
`measured_24h_started: false`. A later 24-hour campaign requires a new final
packet and fresh independent GREEN after this R6 lifecycle is fully closed.

## 2. Preserved evidence and current source

- branch: `evidence/external-validity-r1`;
- implementation commit:
  `346d3a767705aa9a2b3501f4d69f4854fa3e902c`;
- PF-4 minimum-vCPU proof commit:
  `76968b097cef520805eedc5881a3e3f2ff0f64be`;
- prior PF-4 result: `PDH3_R12_R6_PF4_MIN_VCPU_GREEN`;
- prior successful PF-4 Pod: `luro78hz0upemt`, deleted;
- prior worker: Secure L40S, 32 provider vCPU, 125 GiB RAM, measured
  27 effective cgroup CPUs, exact affinity proof GREEN;
- prior main bundle uploaded: false;
- prior measured 24-hour clock started: false;
- prior exact-ID absent and final inventory `[]`;
- prior final independent result: direct GLM 5.2 GREEN.

The prior PF-4 result proves only that the selected placement and kernel
capability path can work. The new full-preflight worker must independently
repeat PF-4 GREEN on the same worker before main-bundle transfer. Prior PF-4
evidence cannot be substituted for the new worker's capability receipt.

The current repair binds every remote stage to the exact receipt-recorded SSH
configuration under its current runtime. It rejects symlinks and any path
outside that runtime. This corrects the stale fixed-path lookup that would have
looked for `runtime/ssh-config` instead of the actual
`runtime/attempt-NN/ssh-config`.

Current verification:

- 40 focused R6/affinity/capability/launcher/remote-preflight tests GREEN;
- 10 deterministic bundle-builder tests GREEN;
- Python compile gate GREEN;
- `git diff --check` GREEN;
- unrelated untracked `heap_profiler/` is operator-owned, excluded, and must
  not be read, modified, staged, transferred, or committed.

## 3. Bound source and package custody

| Host-control file | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_r6_config.py` | `11833c3436cdd13357b57dc77efdda235be8ab38d3e7c3ada30ea287c9ed7307` |
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `eb48522771f329a343620a2bc4c25f28ca3e4db7a85e5bc5791b8638445960e3` |
| `post-dogfood/pdh3_r12_r6_run_pf4.py` | `a0cff6c5f1e89bd5762216e3b407feb35aacf0839df058c5e656cddf31ab2af1` |
| `post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py` | `e07e59a3a69fdcb151e4cabcf4d220462d35acff4c1f00d05032bc6eab17739e` |
| `post-dogfood/pdh3_r12_r6_orchestrator.py` | `4d868cf66308e627a6f2ed9e3576f83535b5a6838131784cfcb74fbf07215ccf` |
| `post-dogfood/pdh3_r12_lifecycle_launch.py` | `23db1b1dfb3e41bced1c7b82220f46b43f0ffc4e4a2b871b69ca70687acbe2a1` |
| `s2-soak/lifecycle_guard.py` | `70c12ea1ae19f69a43fb38100d90bda8f5e0a41ae30d2b6c509b331933a9e14d` |
| `post-dogfood/pdh3_r12_preflight_supervisor.py` | `23d5881fbe3620cda46f71b477a2e96d69033f8c22ae667eac218e6116317a26` |

| Remote-workload file | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_remote_preflight.py` | `65c16b701869ab9f4a9e8a774b25c08d19333d6546c766588660c210c3022e44` |
| `post-dogfood/pdh3_r12_remote_launcher.py` | `f5fcc15188f4b7540567c8af30d90d21320bd89450f566c3c6e4921a6e5868f7` |
| `post-dogfood/pdh3_r12_network_observer.py` | `8e6f72c4fa44d56f982697ee3091938f27924a5120846cba96cc6ed1f794f102` |
| `post-dogfood/pdh3_r12_cpu_affinity.py` | `87de9fb5d02fb1eee468601058086e34dfd4a553765b312672f59584e61dd707` |
| `post-dogfood/pdh3_r12_plan_ab.py` | `820661cf5eb80a6b8d787d426187a86ca772f46a47606207a053cd7c9b435b3f` |
| `post-dogfood/pdh3_r12_checkpoint.py` | `cfe0defb82cc6b8d29f6bc986689e17e89ede572fa8df5270a2d30590cf1ca90` |

Fresh A/B deterministic package root:
`.pdh3-runtime/r12-preflight/full-r6-minvcpu-20260802-r1/`.

- A/B archive SHA-256:
  `018ed0af97b7e533ad6fdec316db006c1990628dcab2a94c42980c199cbfa2ae`;
- archive bytes: `143989823`;
- A/B bundle-receipt file SHA-256:
  `25679606a45223b08f3a99e69094669f3fa0087ca0600562b80b7dc0c73574fc`;
- embedded receipt SHA-256:
  `0552ccfb649f7396d7d2fdca2d736ca64ecde25a2707f5800c3d135f5a2bba7a`;
- manifest SHA-256:
  `6dfe226a4986981df860f3e41aa42f713ab372aebf4b95537cac8487893e38f1`;
- remote source-set SHA-256:
  `1f00bc9490445e688482f1c7699580da2f604e967298ee6276fbcbfb07605728`;
- host-only bindings SHA-256:
  `e86f83c5f170d04263420f81f98f272b8cb2f0d2e971997889f7371614a57086`;
- host-only source-set SHA-256:
  `a1dbd8ddfef4621b3a462120ccf955ba4c11e4e4a17f48d323219f6b033653fc`;
- archive verification SHA-256:
  `0319c0ce772685dc45761a3b08c4baa7b1056eb14ea8dac4fc4a54c13c4c4df2`;
- extracted A and B smoke: GREEN, 35 Python files compiled and 13 bundled
  test modules GREEN.

These package smokes prove deterministic custody and executable integrity,
not target-scale or remote performance.

## 4. Current provider state and worker contract

Authenticated read-only provider snapshot:

- file: `PDH3_R12_R6_FULL_PREFLIGHT_PROVIDER_SNAPSHOT_20260802_R1.json`;
- SHA-256:
  `93bfbc06601ad3ee40b46062792c1b0e461942ce35ff1ff582c6c02988a37539`;
- observed UTC: `2026-08-02T11:34:12Z`;
- active Pod inventory: `[]`;
- Secure Cloud `NVIDIA L40S`: available;
- balance: `$85.3828843819`;
- existing spend rate: `$0.002/hour`;
- account spend limit: `$140`;
- bound CLI: `/tmp/runpodctl-v2.7.2-darwin-arm64`, version
  `2.7.2-309512b`, SHA-256
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`.

Exact request and readback contract:

- RunPod Secure Cloud;
- exactly one NVIDIA L40S;
- GraphQL `minVcpuCount: 24`, `minMemoryInGb: 94`;
- returned provider vCPU at least 24 and RAM at least 94 GiB;
- measured real cgroup effective CPUs at least 16;
- deterministic affinity cap preserving at least 4 GiB per effective CPU;
- image `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- 250 GB disposable container disk;
- zero persistent/network volume;
- compute rate at most `$0.99/hour`;
- exact campaign name and provider-native deadlines;
- SSH host key freshly scanned and pinned;
- one worker at a time.

Allowed L40S datacenters are exactly `EU-NL-1`, `EUR-IS-2`, `US-IL-1`,
`US-MO-1`, `US-NC-1`, `US-TX-3`, and `US-TX-4`. The scheduler may place
within that set; post-create readback rejects every other location or shape.

## 5. Campaign, retry law, deadlines, and cost

- campaign ID: `ck-pdh3-r12-preflight-r6-full-r1`;
- attempt names end in `-01`, `-02`, and `-03`;
- launch opens: `2026-08-02T12:10:00Z`;
- launch closes: `2026-08-02T12:55:00Z`;
- provider-native stop: `2026-08-02T21:40:00Z`;
- provider-native terminate: `2026-08-02T21:55:00Z`;
- host closeout deadline: `2026-08-02T21:25:00Z`;
- maximum creation attempts: 3;
- maximum simultaneously existing workers: 1;
- no replacement after any PF-4 semantic result;
- no replacement after main-bundle transfer begins;
- every assigned Pod ID must be deleted and proven absent before a pre-upload
  provider/capacity retry.

The absolute shared terminate deadline prevents retry multiplication.

- compute rate: `$0.99/hour`;
- disposable disk rate bound:
  `250 * $0.10 / 720 = $0.0347222222/hour`;
- total active rate bound: `$1.0247222222/hour`;
- new maximum paid window: `9.75 hours`;
- new lifecycle upper bound: `$9.9910416667`;
- prior R6 worker active-time upper bound: `360 seconds`;
- prior R6 cost upper bound: `$0.1024722222`;
- aggregate R6 lineage upper bound: `$10.0935138889`;
- operator ceiling: `$12.00`.

Unknown price, cost uncertainty, billing-setting change, insufficient balance,
unexpected active inventory, or any path that can exceed the ceiling blocks
before creation or triggers immediate teardown.

Retries are permitted only before a PF-4 semantic result or main upload, and
only for provider creation/capacity, returned-shape, SSH metadata, host-key, or
readiness failures. Each failure must have a receipt and complete teardown.
Deterministic source, hash, capability, semantic, secret, egress, evidence, or
teardown failures stop the campaign for diagnosis and a new reviewed packet.

## 6. Credential, data, and containment boundary

The operator-authorized RunPod API credential is read only by the local host
controller and injected into its environment. The GraphQL request uses the
credential only in the HTTPS Bearer header. It is never placed in a URL,
request body, argv, output, hash, receipt, archive, worker, or commit. Raw
provider error bodies are not persisted. Credential exposure is terminal.

The workload uses only the frozen synthetic data generated by the package. It
must not read or write HOME runtime, live memory, Qdrant, StateV2, launchd,
client data, production data, unrelated repositories, credentials, or the
untracked `heap_profiler/` directory. The worker receives no AWS, CockroachDB
Cloud, GitHub, package-registry, or other private credential.

## 7. Exact preflight proof

The same worker must pass all stages:

1. **PF-4 capability:** provider/cgroup/affinity, memory ratio, disposable
   disk, fsync/sequential/sustained/random-sync storage, streaming process-tree
   observer, resource/process accounting, tracer hash, and zero residue.
2. **PF-2R:** isolated target-plan/index A/B proof on synthetic inputs.
3. **PF-5:** exact setup of 500,000 tasks, 5,000,000 events, 1,000,000
   receipts, and 250,000 vectors; exact reconciliation; vector-index quality;
   target-scale `EXPLAIN`/`EXPLAIN ANALYZE`; prohibited full scans absent after
   index creation; query results byte-equivalent before/after; resource gates.
4. **PF-6:** four named query families at literal concurrency 10, 50, 100,
   250, and 500; one-gateway c500; three-gateway c500; observer-on/off A/B with
   at most 10% p99 overhead; three full mixed c500 epochs. Every histogram must
   account for all operations, have zero errors, p99 at most 5,000 ms, and
   maximum at most 10,000 ms.
5. **PF-7:** 900 seconds of literal c500 growth measurement; separate database,
   evidence, and network projection; projected network at most 1 GiB, other
   evidence at most 80% of its frozen limit, and database at most 80% of its
   frozen limit; same-host process kill/restart/reconciliation; exact affinity
   re-verification on restarted nodes; off-worker checkpoint retrieval and
   acknowledgment; deliberate partial-successor interruption rejection.
6. **PF-8 host closeout:** terminal semantic receipts and network receipt
   retrieved; best-effort full archive retrieved and hash-checked; local
   CockroachDB roots closed; worker deleted; exact ID absent; campaign inventory
   empty; no paid background process remains.

The tracer claim is observation plus fail-closed termination on an observed
external network syscall. It is not a firewall and does not claim prevention.
The three CockroachDB processes share one physical worker and do not represent
three independent failure domains.

## 8. Terminal states and kill lines

Remote success is only `GREEN_PENDING_PF8`, never final GREEN. Host success is
only `GREEN_PENDING_FINAL_GLM`. Final R6 GREEN requires a new frozen result
packet and independent GLM 5.2 GREEN over that exact result-packet hash.

Stop and teardown on:

- any packet, archive, source, receipt, tracer, checkpoint, or result mismatch;
- any secret/private-data exposure or undeclared egress;
- wrong worker, image, cloud, GPU, disk, volume, rate, location, name, or
  deadline;
- fewer than 24 provider vCPUs, 94 GiB RAM, 16 effective CPUs, or 4 GiB per
  effective CPU;
- PF-4 non-GREEN or residue;
- setup, exactness, index, plan, query-equivalence, vector, latency, observer,
  growth, fault, interruption, checkpoint, or teardown failure;
- missing/partial evidence, non-GREEN semantic receipt, absent terminal result,
  archive mismatch, or supervisor ambiguity;
- deadline/cost uncertainty or inability to prove exact-ID absence and empty
  inventory.

No threshold weakening, revealed-input tuning, silent substitution, worker
replacement after upload, evidence suppression, or 24-hour start is allowed.

## 9. Independent judge contract

GLM 5.2 receives only this exact sanitized packet. It is non-authoring and has
no shell, filesystem, repository, credential, browser, provider, worker,
implementation, or approval authority.

Return exactly:

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: <exact hash supplied with request>
VERDICT: GREEN | NOT_GREEN | BLOCKED | JUDGE_UNAVAILABLE
CRITICAL_FINDINGS:
- <finding or NONE>
HIGH_FINDINGS:
- <finding or NONE>
REQUIRED_CORRECTIONS:
- <correction or NONE>
RATIONALE: <concise evidence-based explanation>
```

GREEN means only that this exact R6 paid-preflight design is coherent enough
to issue the first creation request inside the frozen envelope. It is not R6
execution evidence and does not authorize a 24-hour campaign.
