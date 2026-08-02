# PDH-3 R12 R6 Paid Preflight Packet R1

Status: `FROZEN_FOR_SAME_HASH_GLM_5_2_REVIEW__NO_WORKER_CREATED`

UTC frozen: `2026-08-02T07:55:00Z`

Builder: `Codex / Icarus`

## 1. Authority and strict phase boundary

Operator authorization is bound to:

- `PDH3_R12_R6_AUTHORIZATION_ENVELOPE_20260802_R1.md`
- SHA-256: `e5fb1b999a84339b780a8c299817c9fa11b0aba38e582db766a2301e6594455b`

This packet authorizes only the R6 paid preflight after independent review of
this exact packet hash. It does not authorize a 24-hour measured campaign. A
separate final packet and fresh independent GREEN remain mandatory after R6 is
fully GREEN.

R5 remains immutable failed evidence:

- `PDH3_R12_REMOTE_PREFLIGHT_BLOCKED_R5.md`
- SHA-256: `f36e0980ee37c1944116da378be5e79ca93f99afa43fc5173985340f4680fce7`
- prior Pod: `5ommwuqsbffrl0`, verified deleted;
- prior main-bundle upload: `false`;
- prior 24-hour clock start: `false`.

## 2. Frozen source and repaired bundle

- branch: `evidence/external-validity-r1`;
- implementation commit: `6a2d3c39918a6af6151263894e6a15cf4fd7d8d6`;
- remote branch confirmed at that commit before packet freeze;
- platform repair amendment SHA-256:
  `6a873f05fcc285fd7229fed8211deca87ac2e39c1a85deced49427fda9251e47`;
- platform amendment independent result: `GLM_5_2_GREEN`;
- bundle A/B identical SHA-256:
  `728e4592475f5c18e88e18a02d6230dff27d77316ce6eee599e07a8f01fe9e98`;
- archive bytes: `143984891`;
- bundle A receipt file SHA-256:
  `9651ee128a9b411bb3934dc36e6e2fd1f6c9e87ca80413ef75258c840b4388b1`;
- bundle embedded receipt SHA-256:
  `bd203097b420c145731d651dc88c47b58cd84cb180b97f5370fb8f62bc474187`;
- archive verification SHA-256:
  `c6d4d3387ccca66c303a6381fce4878815c0c57bdd8bc6332ae52f57976e882e`;
- manifest SHA-256:
  `64c22e8b01769293d7dff8cf167814f4c59a4238b78777a1f8d3d532642850f0`;
- remote source-set SHA-256:
  `9d3732bbe1f66f9ceb0c963def125262dc749f2cc2c33cf627357fa1defc8158`;
- host-only source-set SHA-256:
  `4d3be6e87b8bfe83dc9a9aa78673b85d7b2dfe0d2aebf1624001cd4a2c2ed108`;
- host-only bindings SHA-256:
  `79fd504aef943dbd34232639b1885270b2ae176899af7fe0c30e85a69ba5e11f`;
- historical attempt manifest SHA-256:
  `72877c307496cd57d910385c8aa898c779d449170f7134478eb5d2a2702cbe1e`.

Both extracted bundles returned GREEN integrity smoke. This is deterministic
packaging evidence only, not remote or scale evidence.

## 3. Bound host control plane

The following host-only files control paid lifecycle execution and are not
transferred as workload inputs:

| File | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_r6_config.py` | `5aeca1ad6dd71ca3b413d80cf5613794509b08ae93985726f4386dcc2175cc0e` |
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `989823a80f324569db55ca0bca2d04f444a2e5e1d8aa66111ed0a8f5319c2b8b` |
| `post-dogfood/pdh3_r12_r6_run_pf4.py` | `cdfd8f0951b58c6bc2149eaba970cf566bdc068f3f2854d95cebbaf2b01edda7` |
| `post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py` | `fb639f50677ec8d2e853f2436781ad79c736f3a6e47acca30603f83661b9439d` |
| `post-dogfood/pdh3_r12_r6_orchestrator.py` | `4d868cf66308e627a6f2ed9e3576f83535b5a6838131784cfcb74fbf07215ccf` |
| `post-dogfood/pdh3_r12_lifecycle_launch.py` | `23db1b1dfb3e41bced1c7b82220f46b43f0ffc4e4a2b871b69ca70687acbe2a1` |
| `s2-soak/lifecycle_guard.py` | `70c12ea1ae19f69a43fb38100d90bda8f5e0a41ae30d2b6c509b331933a9e14d` |

The remote launcher is transferred and hash-bound inside the archive:

- `post-dogfood/pdh3_r12_remote_launcher.py`:
  `367c6439bbec58a0dabd0325134caefaa96015d4c4c467aa6a90a7aec70e2360`.

Forty-five focused R12 tests are GREEN. The exact R5 32-vCPU/125-GiB shape
is a negative fixture and is rejected without CPU relabeling.

## 4. Current provider evidence and exact worker request

Current authenticated provider checks at `2026-08-02T07:52:36Z`:

- active Pod inventory: `[]`;
- canonical empty-inventory SHA-256:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`;
- Secure Cloud `NVIDIA L40S`: available, stock status `Low`;
- provider-advertised GPU memory: `48 GiB`;
- current account spend rate: `$0.002/hour` from unrelated retained storage;
- current balance: `$85.466193353`;
- current spend limit: `$140`;
- requested compute rate ceiling: `$0.99/hour`;
- container disk: exactly `250 GB`;
- persistent/network volume: `0 GB`;
- image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- CLI: `/tmp/runpodctl-v2.7.2-darwin-arm64`;
- CLI version: `2.7.2-309512b`;
- CLI SHA-256:
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`.

Official provider sources checked before freeze:

- `https://www.runpod.io/pricing`;
- `https://docs.runpod.io/pods/pricing`;
- `https://docs.runpod.io/accounts-billing/billing`.

Live inventory, returned worker shape, image, disk, volume, cloud, name, rate,
and authenticated account state are rechecked before and after every creation
attempt. An unavailable or drifted live surface fails closed.

## 5. Immutable campaign, attempts, and absolute provider deadlines

- campaign ID: `ck-pdh3-r12-preflight-r6-20260802a`;
- attempt names:
  - `ck-pdh3-r12-preflight-r6-20260802a-01`;
  - `ck-pdh3-r12-preflight-r6-20260802a-02`;
  - `ck-pdh3-r12-preflight-r6-20260802a-03`;
- launch window start: `2026-08-02T08:15:00Z`;
- launch window end: `2026-08-02T09:00:00Z`;
- provider-native stop deadline: `2026-08-02T17:45:00Z`;
- provider-native terminate deadline: `2026-08-02T18:00:00Z`;
- host closeout deadline: `2026-08-02T17:30:00Z`;
- maximum simultaneously existing workers: `1`;
- maximum attempts: `3`;
- no replacement after minimal PF-4 upload produces a semantic result;
- no replacement after main-bundle upload begins;
- no 24-hour measured branch exists in the R6 launcher.

The provider deadlines are cost and teardown fuses, not evidence that a phase
passed. Every failed assigned Pod ID must be deleted and proven absent, with
campaign inventory empty, before a subsequent creation request.

## 6. Deterministic cost bound

The one-worker-at-a-time rule and shared absolute terminate deadline limit
aggregate paid R6 wall time across all attempts to at most `9.75 hours`.

- compute upper bound: `9.75 * $0.99 = $9.6525`;
- disposable disk rate bound using `$0.10/GB/month`:
  `250 * $0.10 / 720 = $0.0347223/hour`;
- disk upper bound for 9.75 hours: `$0.338542`;
- aggregate deterministic R6 upper bound: `$9.991042`;
- authorized R6 ceiling: `$12.00`.

The controller independently recomputes a conservative attempt-time bound and
stops if a successful remaining lifecycle could exceed `$12`. Price
uncertainty, billing-setting changes, or an unexpected existing active Pod are
terminal blockers.

## 7. Returned-shape and PF-4 gate

Before main-bundle upload, provider and cgroup/affinity evidence must prove:

- at least `16` effective vCPU;
- at least `94 GiB` effective RAM;
- at least `4 GiB` effective RAM per effective vCPU;
- Secure Cloud L40S, one GPU;
- exact image, 250-GB disposable disk, zero volume, name, rate, and deadlines;
- SSH ready with a freshly scanned host key;
- the host-local exact-ID lifecycle guard is double-forked, PPID 1, and has a
  validated hash-chained identity-matching `BOUND` event.

The detached guard requires `RUNPOD_API_KEY` in its host-only process
environment. The current CLI's authenticated config is not extracted, copied,
or committed. If that environment binding is unavailable, worker creation is
forbidden and the result is `HOST_CREDENTIAL_BINDING_REQUIRED`.

Only after a worker passes returned-shape and lifecycle readiness may it receive
the minimal PF-4 payload: observer, capability probe, pinned strace DEB, and
pinned libunwind8 DEB. PF-4 extracts them into a generated remote root, verifies
all hashes, binds exact `LD_LIBRARY_PATH`, runs the capability probe, retrieves
and verifies the canonical receipt off-worker, removes PF-4 residue, and stops
without replacement on any semantic failure.

Tracer bindings:

- strace DEB SHA-256:
  `d588810ae26b06fee6678dc81e5b54f6efcde8e718e4589adb4d11d254b9820b`;
- libunwind8 DEB SHA-256:
  `658977d18976149b75391850ba0ccacaf7bde3201f0284189da50cd634334d17`;
- extracted strace SHA-256:
  `28f957c227012de0b18d1bd7fff2d396cb693ea60ed8013be68de071e84b5001`.

## 8. Main upload, remote preflight, retrieval, and teardown

PF-4 GREEN on the same worker is the sole permission for main-bundle upload.
Immediately before transfer, the host writes an immutable local marker with
`replacement_forbidden: true`. The archive, receipt, and this packet are then
transferred and rehashed remotely. Extracted-bundle smoke must be GREEN.

PF-2R through PF-7 retain the frozen target workload, three c500 preflight
epochs, latency and exactness thresholds, 15-minute network-proof growth gate,
checkpoint export/acknowledgment, and failure preservation. The observer uses
the hash-pinned streaming process-tree tracer and exact extracted library root.
The claim remains observation plus fail-closed termination after an observed
syscall, not a preventive firewall.

Every success or terminal failure performs best-effort evidence retrieval,
remote/local hash comparison where evidence exists, worker deletion, exact-ID
absence verification, and empty campaign inventory verification. Missing
evidence, partial archive, hash mismatch, observer failure, non-GREEN semantic
receipt, teardown uncertainty, or cost uncertainty is `R6_BLOCKED`.

R6 is not fully GREEN until the worker is absent, inventory is empty, every
required receipt is verified, and a final independent GLM 5.2 review over one
new frozen result packet returns GREEN. That later final review still does not
authorize the 24-hour campaign.

## 9. Judge question

Review this exact packet as a non-authoring, no-tools independent gate. Return
exactly:

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
to issue the first creation request within the frozen envelope. It does not
claim R6 evidence exists and does not approve the 24-hour campaign.
