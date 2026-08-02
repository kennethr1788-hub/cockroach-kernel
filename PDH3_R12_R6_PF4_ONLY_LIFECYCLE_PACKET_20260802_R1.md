# PDH-3 R12 R6 PF-4-only lifecycle packet R1

Status: `FROZEN_FOR_EXACT_HASH_GLM_5_2_REVIEW__NO_WORKER_CREATED`

UTC frozen: `2026-08-02T09:54:00Z`

Builder: `Codex / Icarus`

Decision requested: determine whether this one-attempt PF-4-only provider
lifecycle is sufficiently bounded, fail-closed, evidence-preserving, and safe
to execute. This packet cannot self-approve and cannot authorize PF-2R through
PF-7 or a measured 24-hour campaign.

## 1. Exact authority and phase boundary

- authorization receipt:
  `PDH3_R12_R6_PF4_ONLY_AUTHORIZATION_20260802_R1.md`;
- authorization receipt SHA-256:
  `c55b77a8392082321e6d0b08a48085b5ff8e8be66775cb5a9e4dfbadd69c437b`;
- operator statement: `I authorize a new pf 4`;
- one paid worker creation attempt only;
- successful workload workers: at most one;
- provider: RunPod;
- cloud: Secure Cloud;
- accelerator: one NVIDIA L40S;
- image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- container disk: 250 GB disposable;
- persistent volume: zero;
- network volume: zero;
- main target-scale bundle upload: forbidden;
- PF-2R through PF-7: forbidden;
- measured 24-hour campaign start: forbidden;
- mandatory delete after PF-4 success or failure.

The earlier worker `zby5qthlswc7cy` remains immutable failed evidence. It was
deleted, exact-ID lookup was absent, and campaign inventory was empty. No old
worker, deadline, judge result, or configuration is reused as execution
authority.

## 2. Current policy, provider, price, and spend snapshot

Current policy was reread from:

`/Users/kennethruedas/master-vault/reference/runpod-policy.md`

The controlling 2026-07-25 supersession requires the cheapest sufficient
current hardware unless the operator names a GPU, plus a frozen price,
lifecycle, deadline, and teardown. The operator previously selected Secure
Cloud L40S for this campaign family; this packet does not substitute hardware.

Provider snapshot at `2026-08-02T09:52:00Z`:

- active Pod inventory: `[]`;
- `NVIDIA L40S`: available, Secure Cloud, stock `Low`, 48 GiB VRAM;
- account balance: `$85.4330684207`;
- existing provider spend: `$0.002/hour`, below the controller's `$0.01/hour`
  unrelated-spend stop threshold;
- account spend limit: `$140`;
- current official L40S price: `$0.99/hour`;
- current official container storage price: `$0.10/GB/month`.

The official price source is `https://www.runpod.io/pricing`. Live inventory,
account state, returned shape, and returned price are rechecked immediately
before and after creation. Stock or price drift stops the attempt.

## 3. Fresh campaign and exact deadlines

- campaign ID: `ck-pdh3-r12-preflight-r6-pf4-aff-r1`;
- maximum attempts: 1;
- launch window opens: `2026-08-02T10:05:00Z`;
- launch window closes: `2026-08-02T10:50:00Z`;
- provider-native stop deadline: `2026-08-02T13:05:00Z`;
- provider-native terminate deadline: `2026-08-02T13:20:00Z`;
- maximum successful paid lifetime: 3 hours 15 minutes;
- detached exact-ID lifecycle guard heartbeat: 30 seconds;
- no retry or replacement after any worker is created.

The worker is deleted immediately after PF-4 finishes; the stop and terminate
deadlines are independent last-resort limits, not an idle-time allowance.

## 4. Mechanical cost ceiling

```text
compute_rate = $0.99/hour
container_storage_rate = 250 GB * $0.10/GB-month / 720 hours
                       = $0.0347222222/hour
maximum_active_rate = $1.0247222222/hour
maximum_paid_lifetime = 3.25 hours
mechanical_maximum = $3.3303472222
frozen_aggregate_ceiling = $12.00
```

Any returned compute rate above `$0.99/hour`, active-rate uncertainty, unknown
price, or projected aggregate charge above `$12.00` blocks before upload.

## 5. Candidate, implementation, and control-plane bindings

- branch: `evidence/external-validity-r1`;
- PF-4-only implementation commit:
  `7219df502461e1bce06ad9707be1fb44294632c2`;
- prior CPU-affinity packet:
  `PDH3_R12_R6_CPU_AFFINITY_PREFLIGHT_PACKET_20260802_R1.md`;
- prior CPU-affinity packet SHA-256:
  `0c3039d1e502b77c18c7985a1f91c9437c4474e63d2fe4007684b062cc3cddf4`;
- CPU-affinity amendment SHA-256:
  `eb66d5f8632686c015f79c45215b234fc362863f43fc515af87d6bab4c356e55`;
- prior independent GLM result: design GREEN only, paid PF-4 still required.

| Bound file | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_r6_pf4_only.py` | `82bd65a88f530b611f249ea959d995eeb9aca02e227c68c1622127eac9eaabaf` |
| `post-dogfood/test_pdh3_r12_r6_pf4_only.py` | `62edcc1faffc57b805d631309a444a7855b74868527a03b2018a59c23e366bab` |
| `post-dogfood/pdh3_r12_cpu_affinity.py` | `87de9fb5d02fb1eee468601058086e34dfd4a553765b312672f59584e61dd707` |
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `672d6205f510a5972f683688f0146f4f955daf88599a70c7ce9cf1e4eb7b8ae0` |
| `post-dogfood/pdh3_r12_r6_run_pf4.py` | `a01f93e9994ece2e4eadd5bd3c4b7b7121ae971973955ccd21ae153b28c1fc81` |
| `post-dogfood/pdh3_r12_remote_capability.py` | `ee271da20d92a1251e2804287dbcfd585c5441b4f1f61cf21bc5e62fd6d96d0d` |
| `post-dogfood/pdh3_r12_lifecycle_launch.py` | `23db1b1dfb3e41bced1c7b82220f46b43f0ffc4e4a2b871b69ca70687acbe2a1` |
| `s2-soak/lifecycle_guard.py` | `70c12ea1ae19f69a43fb38100d90bda8f5e0a41ae30d2b6c509b331933a9e14d` |
| `post-dogfood/pdh3_r12_r6_config.py` | `fc6d37821157165b87f4fe48344bfa06fff7ffc3f5f4ec14f906ee0a18400068` |

Focused local verification passed 25 tests covering PF-4-only teardown, affinity
math and readback, launch shape validation, and remote capability behavior.
`py_compile` and `git diff --check` also passed. Local tests do not claim real
provider or Linux-affinity evidence.

The unrelated untracked `heap_profiler/` directory is user-owned and excluded
from all source, payload, packet, and evidence bindings.

## 6. Fresh payload and package-integrity evidence

Payload root:
`.pdh3-runtime/r12-preflight/pf4-affinity-20260802-r1/`

- archive: `pdh3-r12-bundle.tgz`;
- archive bytes: `143989825`;
- archive SHA-256:
  `1f5cdf99e09c9010a9f0544947a0920c0004357f3bcf2f2c2a02ffe1da6b85df`;
- bundle-receipt file SHA-256:
  `62d8e20a6f37fec45605e3db50a3e4a5458e9476beb2058cb99bfdb55d63e1a4`;
- embedded receipt SHA-256:
  `6c829e7e3cd0a7e8bf767d98ea1ef382ee0451dacb8773d58162cd3bec330c9c`;
- manifest SHA-256:
  `d8ff6e6a35878e5f31ffbe009f6069e1d051251a5128fc4090d86f2e6fd68020`;
- host-only bindings SHA-256:
  `513451bd3881f619ab894d170051c0c150b7073c307370d5a43d336fd14e8274`;
- package smoke receipt SHA-256:
  `7bf5541e53b6e4e57909ec986277ba0f969fb68eb1cab7f310d1217670422035`;
- smoke verdict: GREEN;
- compiled Python files: 35;
- bundled tests: 13, all GREEN.

The main archive is bound for integrity checking by the host configuration,
but the PF-4-only controller does not upload it. PF-4 transfers only the narrow
capability probe defined by the bound controller.

## 7. Credential, data, and egress boundary

The RunPod API credential remains host-only. It may be read from the existing
operator-authorized local RunPod configuration solely by the local launcher and
injected into the controller process environment. It is never printed,
persisted, hashed, logged, committed, copied into the archive, sent over SSH,
or transferred to the worker.

The worker receives synthetic capability-probe material only. Private data,
client data, HOME runtime state, Qdrant, StateV2, launchd, production data, and
unrelated repositories are forbidden. Any unexpected secret or private-path
match is terminal.

## 8. PF-4 evidence and success contract

Before PF-4 runs, the launcher must prove:

1. current active provider inventory is empty;
2. Secure Cloud L40S availability;
3. returned image, GPU, cloud, vCPU, RAM, disk, volumes, name, rate, and
   deadlines match the packet;
4. detached lifecycle guard binds the exact Pod ID and campaign;
5. SSH host key and connection metadata are pinned;
6. an effective-CPU plan satisfies 4 GiB per effective CPU.

PF-4 must then prove on the real Linux worker:

1. `sched_setaffinity` succeeds;
2. exact `sched_getaffinity` readback matches the deterministic plan;
3. the observer and descendant capability path inherit the exact mask;
4. minimal disk I/O, network observation, resource accounting, and residue
   checks are GREEN;
5. raw streams and canonical receipts are retrieved before deletion.

After PF-4 success or failure, the controller must delete the worker and prove:

- exact Pod-ID lookup absent;
- campaign-scoped active inventory empty;
- lifecycle terminal event `TEARDOWN_GREEN`;
- no main bundle upload;
- no measured 24-hour start.

The controller may emit `PF4_ONLY_GREEN` only when the host PF-4 receipt is
`PF4_GREEN` and teardown is proved. Final gate status still requires a fresh
independent review of the retrieved same-hash evidence; the builder does not
self-green.

## 9. Kill lines

Stop and delete without main upload on any:

- packet, source, payload, CLI, image, shape, price, or deadline mismatch;
- active inventory not empty;
- lifecycle guard bind or heartbeat failure;
- Linux affinity unavailable, denied, ignored, or read back incorrectly;
- insufficient vCPU, RAM, VRAM, disk, or 4-GiB/effective-CPU ratio;
- unexpected network, secret, private path, or credential behavior;
- missing, invalid, or hash-mismatched evidence;
- inability to retrieve evidence before deletion;
- inability to prove exact-ID absence and empty campaign inventory;
- cost uncertainty or projected ceiling breach.

No retry, substitution, threshold weakening, post-result tuning, or later-phase
continuation is permitted by this packet.

## 10. Independent judge contract

GLM 5.2 receives this exact sanitized packet only. It has no shell, file-write,
repository, browser, provider, credential, worker-launch, implementation, or
approval authority.

It must return exactly this line-oriented result, once per field:

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: <exact packet SHA-256>
VERDICT: GREEN|NOT_GREEN|JUDGE_UNAVAILABLE
BLOCKERS:
- none | <blocker>
NON_BLOCKING_RISKS:
- <risk or none>
EVIDENCE_REQUIRED:
- <evidence or none>
```

`GREEN` means only that this PF-4-only lifecycle may create its one bounded
worker. It does not prove PF-4 passed and does not authorize PF-2R through PF-7
or a 24-hour campaign. Any mixed hash, malformed verdict, tool request,
implementation direction, or self-approval invalidates the review.
