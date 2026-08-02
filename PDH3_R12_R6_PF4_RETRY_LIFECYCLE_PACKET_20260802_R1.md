# PDH-3 R12 R6 PF-4 replacement retry lifecycle packet R1

Status: `FROZEN_FOR_EXACT_HASH_GLM_5_2_REVIEW__NO_WORKER_CREATED`

UTC frozen: `2026-08-02T10:36:00Z`

Builder: `Codex / Icarus`

Decision requested: determine whether this repaired, datacenter-bound,
PF-4-only replacement campaign is sufficiently bounded, fail-closed,
evidence-preserving, and safe to execute. This packet cannot self-approve and
does not authorize main-bundle upload, PF-2R through PF-7, or the measured
24-hour campaign.

## 1. Exact authority and bounded interpretation

- authorization receipt:
  `PDH3_R12_R6_PF4_RETRY_AUTHORIZATION_20260802_R1.md`;
- authorization SHA-256:
  `4fa410bfcd2e7307b79e7ffca2747b10ad50d0cfff320119ce73e44045a5fe1f`;
- exact operator statement is preserved in that receipt;
- at most three additional sequential worker-creation attempts;
- never more than one paid worker at a time;
- stop retries permanently when one worker completes PF-4 successfully;
- delete every failed or successful worker and prove exact-ID absence plus
  empty campaign inventory before another attempt or campaign closeout;
- provider/capacity failure may be retried without code changes only while this
  packet remains exact;
- any deterministic implementation, contract, threshold, or evidence defect
  requires a local repair, new packet hash, and fresh same-hash GLM 5.2 GREEN;
- three consecutive occurrences of the same failure stop blind retries;
- aggregate campaign cost ceiling remains `$12.00`.

The phrase `continuous retries` is not interpreted as unbounded spending or an
infinite retry loop. The mechanical three-attempt ceiling, cost ceiling,
one-worker invariant, mandatory teardown, and same-failure stop are controlling.

## 2. Preserved failed evidence and causal repair

The preceding PF-4 worker `7g0k4sfm35r1gh` is immutable failed evidence:

- provider shape: 16 vCPU / 188 GiB / Secure L40S / `US-NC-1` / `$0.99/hour`;
- provider readback SHA-256:
  `3c15ec36b12727c0d3193173d96e47c0c02d186dbbb61a94121476ff38c5ff77`;
- real affinity application/readback: 16 CPUs, GREEN;
- real cgroup v1 quota: 13 effective CPUs;
- frozen minimum: 16 effective CPUs;
- PF-4 capability receipt SHA-256:
  `c997d72a57f02cc1e03f6c86d1348c573e94431fd742880017ea7eb3fc51047d`;
- PF-4 terminal receipt SHA-256:
  `738b40cb1e1e6d7af8583cf64a4713962b176368206c27170cbbf95e767a9038`;
- final closeout receipt SHA-256:
  `d1449a9891804042975f69b02d249ff1a6c9e9e8bc7988d253a0470938bede72`;
- attempt blocker receipt SHA-256:
  `64250201dea64e60d27372c44e71361624b3e29cf62bf691ade505932a6f7578`;
- independent result review SHA-256:
  `0238009bb038830b52e97bd9567734ba1fe57c2f1db3c794ec0305308b6fde70`;
- teardown: `TEARDOWN_GREEN`, exact ID absent, campaign inventory `[]`.

The repair does not weaken the 16-effective-CPU threshold. It constrains the
provider scheduler to `US-MO-1`, the datacenter returned by two preserved L40S
workers with 32 vCPU / 125 GiB:

| Historical worker | Readback SHA-256 | Datacenter | vCPU | RAM GiB |
|---|---|---:|---:|---:|
| `5ommwuqsbffrl0` | `17c8757f6512c6f82fec3c0e9c66c45f6b57b8fd4b1a6aff19d5d09d7318f212` | `US-MO-1` | 32 | 125 |
| `zby5qthlswc7cy` | `5c85273ad6134a44b4da6c0f73ec47e14f24085fb3e59b09c01770ae3df8e931` | `US-MO-1` | 32 | 125 |

This is scheduling evidence, not PF-4 evidence. The returned worker must match
`US-MO-1`, and the real Linux cgroup probe must still prove at least 16
effective CPUs. A 32-vCPU / 125-GiB worker receives a prospective deterministic
31-CPU affinity cap to preserve at least 4 GiB per effective CPU; the real
cgroup limit remains authoritative and may still block.

## 3. Provider, worker, data, and phase boundary

- provider: RunPod;
- cloud: Secure Cloud;
- accelerator: exactly one NVIDIA L40S;
- datacenter allowlist: exactly `US-MO-1`;
- image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- compute price ceiling: `$0.99/hour`;
- container disk: 250 GB disposable;
- persistent volume: zero;
- network volume: zero;
- main target-scale bundle upload: forbidden;
- PF-2R through PF-7: forbidden;
- measured 24-hour clock: forbidden;
- worker replacement after any main-bundle upload: forbidden by construction;
- synthetic narrow capability-probe material only.

Current policy was reread from
`/Users/kennethruedas/master-vault/reference/runpod-policy.md` and the current
RunPod playbook. The launcher rechecks account state, active inventory,
returned worker properties, price, and campaign identity immediately before
and after every creation. Unknown or drifted price, non-empty starting
inventory, or a mismatched worker causes fail-closed teardown.

## 4. Fresh campaign, deadlines, and cost

- campaign ID: `ck-pdh3-r12-r6-pf4-usmo-r1`;
- maximum attempts: 3;
- launch window opens: `2026-08-02T10:48:00Z`;
- launch window closes: `2026-08-02T11:33:00Z`;
- provider-native stop deadline shared by all attempts:
  `2026-08-02T13:33:00Z`;
- provider-native terminate deadline shared by all attempts:
  `2026-08-02T13:48:00Z`;
- maximum aggregate active campaign window: 3 hours;
- maximum final safety window to provider termination: 3 hours 15 minutes;
- lifecycle guard heartbeat: 30 seconds.

The worker is deleted immediately after PF-4 success or failure. Deadlines are
last-resort provider controls, not idle-time permission. Because all attempts
share one absolute deadline and only one worker may exist, retry count cannot
multiply maximum paid lifetime.

```text
compute_rate = $0.99/hour
container_storage_rate = 250 GB * $0.10/GB-month / 720 hours
                       = $0.0347222222/hour
maximum_active_rate = $1.0247222222/hour
maximum safety-window exposure = 3.25 hours
mechanical maximum = $3.3303472222
aggregate campaign ceiling = $12.00
```

Any known or estimated aggregate cost reaching the ceiling, or uncertainty
that could conceal a ceiling breach, is terminal.

## 5. Implementation and package bindings

- branch: `evidence/external-validity-r1`;
- implementation commit:
  `e9a9465f528c3034e7ffdd0b14f07a7a783474c9`;
- focused verification: 28 tests GREEN;
- `py_compile`: GREEN;
- `git diff --check`: GREEN;
- unrelated untracked `heap_profiler/`: user-owned and excluded.

| Bound file | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_r6_config.py` | `ea2742e02bf4dd6558b60ba6f90c3c5cf10e6a58627c37b4564cfffadfc22e74` |
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `ce679328717fe0a85f6694077e88fa601152cb12825011b068ce89f17baebafd` |
| `post-dogfood/test_pdh3_r12_r6_config.py` | `1dca0b6c3e5b9987f21c1d72961829cb0682a5ebaa34f6b374ec0d4632b8b567` |
| `post-dogfood/test_pdh3_r12_r6_launch_pf4.py` | `1b6f0dfb616b5f71eadfddc2b40385b03b49d80f7f197125b028f590f24eb839` |
| `post-dogfood/pdh3_r12_r6_pf4_only.py` | `82bd65a88f530b611f249ea959d995eeb9aca02e227c68c1622127eac9eaabaf` |
| `post-dogfood/pdh3_r12_cpu_affinity.py` | `87de9fb5d02fb1eee468601058086e34dfd4a553765b312672f59584e61dd707` |
| `post-dogfood/pdh3_r12_remote_capability.py` | `ee271da20d92a1251e2804287dbcfd585c5441b4f1f61cf21bc5e62fd6d96d0d` |
| `s2-soak/lifecycle_guard.py` | `70c12ea1ae19f69a43fb38100d90bda8f5e0a41ae30d2b6c509b331933a9e14d` |

Fresh deterministic package root:
`.pdh3-runtime/r12-preflight/pf4-retry-usmo-20260802-r1/`

- archive bytes: `143989827`;
- archive SHA-256:
  `b9df3cffa961e9ab082df0582d7bf259cf1c90bf162ebb5df0ac37f56566aca3`;
- bundle-receipt file SHA-256:
  `06da44d1c802335825fc78bdb6c7cd7f109f09d4075aa322e1876daa75359c20`;
- embedded receipt SHA-256:
  `15335d407de193a0a3b90148641e14b179e4f3f88b55022ce2421b7ec2e61d0c`;
- manifest SHA-256:
  `a638a4772710eafae0b0d050a801ee92b007d55a6364cc876bce029d76d0762c`;
- source-set SHA-256:
  `1f00bc9490445e688482f1c7699580da2f604e967298ee6276fbcbfb07605728`;
- host-only bindings SHA-256:
  `f545ffc3d6deba573e2a78b3f670115da02466afe20942c3b4f1ca926290d707`;
- smoke-receipt file SHA-256:
  `31e0e3af50b8ca030c9de0f1206eb7afc49c756114a201949a10f3f02b5b37c1`;
- smoke verdict: GREEN; 35 compiled Python files and 13 tests GREEN.

The main archive is bound for integrity but remains forbidden from transfer in
this PF-4-only campaign. PF-4 transfers only the narrow bound capability probe.

## 6. Retry and teardown law

For every attempt:

1. prove current starting inventory empty;
2. create only the exact packet-bound worker in `US-MO-1`;
3. validate name, image, datacenter, cloud, GPU, vCPU, RAM, price, disk,
   volumes, and deadlines before capability-probe transfer;
4. bind the detached lifecycle guard to the exact Pod ID;
5. pin SSH host identity and prove readiness;
6. run PF-4 once;
7. retrieve and hash raw evidence before deletion;
8. delete the worker;
9. prove exact-ID absence, empty campaign inventory, and `TEARDOWN_GREEN`.

Creation, returned-shape, readiness, or transient provider failure may proceed
to the next numeric attempt only after teardown is proved and the exact packet
remains applicable. A PF-4 capability failure returns to local diagnosis; it
must not be blindly retried as a provider failure. Any load-bearing repair
requires a new packet and fresh GLM review.

## 7. Credential and safety boundary

The existing operator-authorized RunPod credential may be read solely from the
local RunPod configuration and injected into the local controller process. It
must not be printed, persisted, logged, committed, hashed, or transferred to a
worker.

No client data, private data, HOME runtime state, Qdrant, StateV2, launchd,
production data, or unrelated repository material may enter the worker. Any
unexpected secret or private-path match is terminal.

## 8. PF-4 pass contract

PF-4 must prove on the real worker:

1. `sched_setaffinity` succeeds;
2. exact `sched_getaffinity` readback matches the deterministic plan;
3. observer and descendant processes inherit the exact mask;
4. real cgroup accounting reports at least 16 effective CPUs;
5. at least 4 GiB RAM exists per effective CPU;
6. disk I/O, fsync, network-observer capability, process/resource accounting,
   and residue checks all pass unchanged thresholds;
7. raw streams and canonical receipts are retrieved before deletion.

The host controller may emit `PF4_ONLY_GREEN` only when the real PF-4 receipt
is `PF4_GREEN` and teardown is proved. Final PF-4 status still requires fresh
independent review of the retrieved exact-hash evidence.

## 9. Kill lines

Stop and teardown on any:

- packet, source, package, CLI, image, datacenter, shape, price, deadline, or
  campaign mismatch;
- non-empty starting inventory or inability to prove prior deletion;
- lifecycle guard bind, heartbeat, retrieval, or teardown failure;
- affinity unavailable, denied, ignored, or read back incorrectly;
- cgroup effective CPUs below 16 or RAM ratio below 4 GiB per effective CPU;
- unexpected network, credential, secret, private-path, or production-data
  behavior;
- missing, invalid, partial, or hash-mismatched evidence;
- aggregate-cost uncertainty or projected ceiling breach;
- repeated identical failure three times.

No threshold weakening, silent hardware substitution, post-result tuning,
main-bundle upload, later preflight, or measured 24-hour start is permitted.

## 10. Independent judge contract

GLM 5.2 receives this exact sanitized packet only. It is a non-authoring judge
with no shell, write, repository, browser, provider, credential, worker-launch,
implementation, or approval authority.

It must return exactly:

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

`GREEN` permits only this repaired PF-4-only lifecycle. It does not prove PF-4
passed and does not authorize PF-2R through PF-7 or a measured 24-hour
campaign. Any mixed hash, malformed verdict, fallback model, tool request,
implementation direction, or self-approval invalidates the review.
