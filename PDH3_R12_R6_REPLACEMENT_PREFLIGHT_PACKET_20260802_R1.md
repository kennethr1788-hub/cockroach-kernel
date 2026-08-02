# PDH-3 R12 R6 replacement paid-preflight packet R1

Status: `FROZEN_FOR_EXACT_HASH_GLM_5_2_REVIEW__NO_WORKER_CREATED`

UTC frozen: `2026-08-02T09:05:00Z`

Builder: `Codex / Icarus`

Decision requested: authorize or block one replacement R6 paid-preflight
worker. This packet cannot authorize the later 24-hour campaign.

## 1. Authority, scope, and last verified state

The operator authorized exactly one replacement attempt after failure analysis,
repair, a new packet, and direct GLM review:

- authorization receipt:
  `PDH3_R12_R6_REPLACEMENT_AUTHORIZATION_20260802_R1.md`;
- receipt SHA-256:
  `5b5564a3c5474ca8f95267ca4e37044e431e4b3eb1ee4f5cbbfc43891c756f00`;
- unchanged outer envelope:
  `PDH3_R12_R6_AUTHORIZATION_ENVELOPE_20260802_R1.md`;
- envelope SHA-256:
  `e5fb1b999a84339b780a8c299817c9fa11b0aba38e582db766a2301e6594455b`.

The replacement is limited to:

- one Secure Cloud L40S worker;
- one creation attempt;
- `$0.99/hour` maximum compute rate;
- `$12.00` aggregate R6 paid-preflight ceiling;
- 250 GB disposable container disk;
- zero persistent or network volume;
- synthetic and sanitized project payload only;
- maximum successful paid-preflight lifetime below ten hours;
- mandatory retrieval, deletion, exact-ID absence, and empty-inventory proof.

It does not authorize a 24-hour measured campaign, product changes, threshold
changes, credentials inside the worker, public release, or submission.

Last implementation commit: `618bc82eed309e157855e997383cd9e79687e4ce`.
The branch `evidence/external-validity-r1` was pushed to that commit before this
packet was frozen. The only unrelated untracked path is `heap_profiler/`; it is
excluded from this packet, payload, and execution.

## 2. Preserved failed attempt and verified mechanisms

Attempt 01 remains immutable failed evidence:

- receipt: `PDH3_R12_R6_ATTEMPT_01_BLOCKED_RECEIPT_20260802_R1.md`;
- receipt SHA-256:
  `e2ae42217f730f4e50d26ad7586beaba12fa26043d6cecdd2423b012f9a549e3`;
- Pod ID: `qv3ve5s5i9eil1`, verified deleted;
- final active Pod inventory: `[]`;
- returned shape: 16 vCPU, 188 GiB RAM, Secure Cloud L40S, 250 GB,
  `$0.99/hour`;
- main bundle uploaded: `false`;
- 24-hour measured clock started: `false`;
- lifecycle result: `TEARDOWN_GREEN`.

PF-4 passed CPU, RAM, disk, write throughput, fsync, random I/O,
process-tree, monotonic-clock, and residue checks. It failed because:

1. `pdh3_r12_network_observer.py` was transferred without its import-time
   dependency `run_pdh3_traced.py`;
2. the probe required cgroup-v2 root files that this provider container did
   not expose and had no cgroup-v1 or procfs accounting fallback;
3. observer stdout/stderr were hash-recorded but not retrieved, preventing
   direct provider-side diagnosis.

No evidence supports a credential leak. The failed worker was deleted and
inventory reconciled empty.

## 3. Prospective repair and non-regression boundary

The complete amendment is bound as:

- `PDH3_R12_R6_PLATFORM_COMPATIBILITY_AMENDMENT_20260802_R1.md`;
- SHA-256:
  `1425e6e4182ccef0db975161d9d6518eeb0e46ad3f792b6e9ff56212c93505a4`.

The repaired PF-4 now:

1. transfers and remotely hashes the observer, `run_pdh3_traced.py`, the
   capability probe, pinned strace DEB, and pinned libunwind8 DEB;
2. chooses one observed resource-accounting backend in order: complete
   cgroup v2, complete cgroup v1, or procfs process-tree accounting bound to
   the provider-returned allocation;
3. labels the procfs fallback only as
   `PROCESS_TREE_PLUS_PROVIDER_ALLOCATION`, never cgroup isolation;
4. writes, fsyncs, retrieves, and hash-reconciles capped raw observer stdout
   and stderr before interpreting the PF-4 receipt;
5. performs the same backend selection continuously in PF-2R through PF-7;
6. fails closed on unsupported/unreadable accounting, observer failure,
   missing raw streams, hash mismatch, or residue;
7. uses config schema `ck-pdh3-r12-r6-config-v2`, which rejects any
   `max_attempts` value other than `1` before provider mutation.

The repair does not change target cardinality, query mix, latency thresholds,
fault schedule, evidence caps, cleanup requirements, or product behavior.

Bound repaired source hashes:

| File | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_remote_capability.py` | `f644c0dd05509f762f733f28979f80f63cde87c8a4a2480884cce10e963306bb` |
| `post-dogfood/pdh3_r12_r6_run_pf4.py` | `41b9e6b25929166baac39f7e8993647b0bff7178a790a287f248d89c6eaacbbd` |
| `post-dogfood/pdh3_r12_remote_preflight.py` | `dce066c67ab0c74492bae8be6850a9d78920570f588414cc6118975141bb042c` |
| `post-dogfood/pdh3_r12_network_observer.py` | `8e6f72c4fa44d56f982697ee3091938f27924a5120846cba96cc6ed1f794f102` |
| `post-dogfood/run_pdh3_traced.py` | `87ce2498b1a03d1a0c80e96ef9e966e3a8958788c934e0ce4a63201aec3691e4` |
| `post-dogfood/test_pdh3_r12_remote_capability.py` | `f2d2d8e0b5713efef82c30c8ff3a0724efdfe31c55017b3dd0183fa274315175` |
| `post-dogfood/pdh3_r12_r6_config.py` | `fc6d37821157165b87f4fe48344bfa06fff7ffc3f5f4ec14f906ee0a18400068` |
| `post-dogfood/test_pdh3_r12_r6_config.py` | `6b9b36f9ff571cfb44716ec3f36bcb5dfd3f464615974916c9fb38c1d0992535` |

## 4. Local verification and deterministic payload

Local verification on the committed candidate:

- 49 focused `test_pdh3_r12*.py` tests: GREEN;
- config v2 rejects a three-attempt value: GREEN;
- raw observer-stream persistence/hash tests: GREEN;
- cgroup-v2, cgroup-v1, and procfs/provider-bound selection tests: GREEN;
- isolated observer import using only the two required Python files: GREEN;
- changed Python modules compile: GREEN;
- bundle-builder tests: GREEN;
- `git diff --check`: GREEN.

Two independent bundle builds produced byte-identical archives and receipts:

- archive SHA-256:
  `3152cd00011d1c8c23d873a051b3651407379699ffb9e180a3581f86b44a3418`;
- archive bytes: `143986735`;
- receipt file SHA-256:
  `86caf2b146615799a16e8b2295cd70aa2f4b6fff123a8f9818a61d6f1e33ba0a`;
- embedded receipt SHA-256:
  `ecee83603a2e5436533c2e33f9d919c18949d7a2f63922173578acc2c7fc57d6`;
- manifest SHA-256:
  `4b0c3f7d0770361ce572b80438ec809171a03ef15ca179e02726aa426e905612`;
- remote source-set SHA-256:
  `1f7694000ce2ace147ac6fa630f70b92fcaf8c3d45718351dbc1dd3f142a01da`;
- host-only source-set SHA-256:
  `a36156f5d2fe956fcef942565b3050b94942de6eee9f2dc9f212dd3d39c8ec7f`;
- host-only bindings SHA-256:
  `a8b5c46b39499bb3fd2060c7e7b760ccb5b62113a4f2d14d81391e3b3b86200f`;
- archive verification SHA-256:
  `e44e3ae9e8262be2b9cf7947d0ad33b2d02fdab2ffba1a98ea56aee50206aac7`;
- historical-attempt manifest SHA-256:
  `72877c307496cd57d910385c8aa898c779d449170f7134478eb5d2a2702cbe1e`.

Both extracted copies compiled and passed all 12 bundled smoke tests. Their
path-bearing stderr hashes differ because the extraction roots are different;
therefore the smoke receipt files are not falsely described as byte-identical:

- smoke A file SHA-256:
  `a4d56700a7e37a10115c5675fd725e2632f06cd4323fea7c7311f1e8568eff7a`;
- smoke B file SHA-256:
  `2287f7c95303532b6d81c4b85e096a1b5268e864ba7cf3c40fb516a34de55465`;
- both: `green: true`, 12 tests, compile return code 0;
- both bind archive SHA-256 `3152cd00011d1c8c23d873a051b3651407379699ffb9e180a3581f86b44a3418`.

These are packaging and reduced integrity proofs, not RunPod or scale proofs.

## 5. Current provider and price evidence

Sanitized provider snapshot:

- `PDH3_R12_R6_REPLACEMENT_PROVIDER_SNAPSHOT_20260802_R1.json`;
- SHA-256:
  `b97982209a2a47148180c6f5779af51adbd5a58e171137bdd0b2930cc5e9ae7d`;
- observed UTC: `2026-08-02T09:00:57Z`;
- active Pod inventory: `[]`;
- Secure Cloud L40S: available, stock `Low`, 48 GiB VRAM;
- account balance: `$85.4451900651`;
- current spend: `$0.002/hour` from unrelated retained storage;
- account spend limit: `$140`;
- official Secure Cloud L40S price: `$0.99/hour`;
- container disk price: `$0.10/GB/month`.

Official pricing source: `https://www.runpod.io/pricing`, checked on
`2026-08-02`. RunPod CLI inventory and account state are rechecked before
creation. Returned shape and price are rechecked before any upload. Any drift,
unexpected active Pod, or rate above the ceiling is terminal.

CLI binding:

- `/tmp/runpodctl-v2.7.2-darwin-arm64`;
- version `2.7.2-309512b`;
- SHA-256:
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`.

## 6. Campaign, worker request, deadlines, and cost bound

- campaign ID: `ck-pdh3-r12-preflight-r6-replacement-20260802a`;
- sole attempt name:
  `ck-pdh3-r12-preflight-r6-replacement-20260802a-01`;
- launch window start: `2026-08-02T09:15:00Z`;
- launch window end: `2026-08-02T10:00:00Z`;
- host closeout deadline: `2026-08-02T18:30:00Z`;
- provider-native stop deadline: `2026-08-02T18:45:00Z`;
- provider-native terminate deadline: `2026-08-02T19:00:00Z`;
- maximum simultaneous workers: `1`;
- maximum attempts: `1`;
- maximum successful paid lifetime: `9.75 hours`;
- replacement after creation failure: forbidden;
- replacement after any upload: forbidden.

Request:

- cloud: `SECURE`;
- compute: GPU;
- GPU ID: `NVIDIA L40S`;
- count: 1;
- image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- container disk: 250 GB;
- volume: 0 GB;
- port: `22/tcp`;
- provider stop and termination deadlines: exactly as above.

Deterministic upper bound:

- compute: `9.75 * $0.99 = $9.6525`;
- disk hourly bound: `250 * $0.10 / 720 = $0.0347223`;
- disk for 9.75 hours: `$0.338542`;
- total bound: `$9.991042`;
- authorized ceiling: `$12.00`.

The deadlines are denial-of-wallet and teardown fuses, not phase deadlines or
success evidence.

## 7. Credential, lifecycle, and pre-upload gates

The operator separately authorized reading `~/.runpod/config.toml` only to
inject the `apikey` value into the local controller process environment.
The value is never printed, persisted, hashed, logged, transferred, or
committed. The worker receives no RunPod credential.

Before provider mutation the controller must prove:

- exact CLI hash and version;
- exact packet, authorization, amendment, GLM result, archive, and receipt
  hashes;
- config v2 with `max_attempts: 1`;
- launch window open;
- active inventory empty;
- Secure Cloud L40S available;
- sanitized account balance and spend within bounds;
- local detached lifecycle guard can receive its host-only credential.

After creation and before upload it must prove:

- exact campaign/name/image/disk/zero-volume/readback;
- Secure Cloud L40S, one GPU;
- at least 16 vCPU and 94 GiB RAM, at least 4 GiB RAM per vCPU;
- returned compute price no more than `$0.99/hour`;
- SSH readiness under a freshly scanned host key;
- exact-ID detached lifecycle guard is double-forked, bound, heartbeating,
  and armed with exact stop/delete epochs.

Any mismatch causes immediate deletion and final blocked closeout. There is no
second creation attempt under this packet.

## 8. PF-4, main upload, remote preflight, and closeout

PF-4 receives only the five hash-bound minimal artifacts. It must prove:

- a supported directly observed accounting backend;
- all unchanged CPU/RAM/disk/I/O/fsync/process-tree/clock gates;
- extracted strace SHA-256
  `28f957c227012de0b18d1bd7fff2d396cb693ea60ed8013be68de071e84b5001`;
- observer execution under the pinned tracer and library root;
- raw stdout/stderr retrieval and receipt-hash reconciliation;
- observer receipt GREEN;
- PF-4 residue removal.

Only PF-4 GREEN permits main archive upload. Immediately before upload a local
immutable `replacement_forbidden: true` marker is written. The archive,
receipt, and this packet are rehashed after transfer and extraction.

PF-2R through PF-7 retain the frozen full-cardinality setup, three c500
preflight epochs, exactness, latency thresholds, network-proof growth gate,
continuous resource accounting, checkpoint acknowledgment, failure evidence,
and residue checks. No 24-hour measured branch is reachable from this
controller.

On any terminal outcome:

1. stop child workloads;
2. fsync and retrieve available receipts, raw streams, logs, and archives;
3. verify local/remote hashes where artifacts exist;
4. stop/delete the exact worker;
5. prove exact Pod ID absent;
6. prove campaign active inventory empty;
7. prove no SSH, transfer, controller, guard, or paid background process
   remains;
8. preserve a blocked or GREEN result packet without rewriting prior failures.

R6 can become GREEN only after final teardown and a new independent GLM 5.2
GREEN over the exact final result packet. Even that does not start or authorize
the 24-hour campaign.

## 9. Kill lines

Any one of the following is terminal:

- packet, source, archive, receipt, CLI, tracer, or evidence hash mismatch;
- GLM result missing, stale, wrong-model, wrong-hash, or non-GREEN;
- launch window closed;
- unexpected active Pod or current spend;
- unavailable/wrong/repriced worker;
- credential output, persistence, logging, transfer, or commit;
- missing lifecycle heartbeat or uncertain deletion ability;
- unsupported accounting backend or false cgroup-isolation claim;
- observer error, missing raw stream, or stream-hash mismatch;
- threshold, exactness, latency, growth, checkpoint, or residue failure;
- undeclared egress or private/production data;
- incomplete retrieval, partial archive, or ambiguous supervisor state;
- exact-ID absence or empty inventory not proved;
- projected cost above `$12.00`.

## 10. Independent judge contract

You are the direct, non-authoring GLM 5.2 preflight judge. You have no shell,
filesystem-write, credential, browser, deployment, editing, public-action, or
implementation authority. Do not improve the design or write code. Evaluate
whether this exact packet is sufficient to authorize one paid replacement
preflight, not whether the product or future 24-hour claim is complete.

Return exactly one structured result:

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: <exact packet sha256>
VERDICT: GREEN|NOT_GREEN|BLOCKED|JUDGE_UNAVAILABLE
BLOCKERS:
- <none or exact blocker>
NON_BLOCKING_RISKS:
- <risk>
EVIDENCE_REQUIRED:
- <none or exact missing evidence>
```

`GREEN` authorizes only this one replacement paid-preflight worker. It does not
authorize a 24-hour campaign or allow the builder to self-grade final results.
