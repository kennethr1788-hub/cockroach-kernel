# PDH-3 R12 Paid Remote Preflight Packet R5

Status: `FROZEN_FOR_SAME_HASH_GLM_REVIEW__NO_WORKER_CREATED`

UTC frozen: `2026-08-02T06:54:00Z`

Builder: `Codex / Icarus`

Independent judge: `direct glm-zai route, served model required to be glm-5.2`

## 1. Authorization and terminal boundary

Kenneth authorized all R12 pre-staging, one replacement RunPod preflight, and
the later 24-hour campaign. This packet
interprets that authority narrowly as exactly one paid Secure Cloud worker and
one creation attempt for PF-4 through PF-8. It does not authorize creation
retries, replacement after any creation response, a second simultaneous worker,
or starting the final 24-hour measured campaign before this preflight and its
final independent review are GREEN.

R4 attempted creation once at `2026-08-02T06:47:49Z`; RunPod returned
`This machine does not have the resources to deploy your pod`, assigned no Pod
ID, created no worker, and left active inventory empty. R4 is preserved as
failed capacity evidence and its single creation attempt is consumed. Kenneth
then explicitly authorized one new RunPod run and the 24-hour campaign. R5
mechanically reselects the next-cheapest currently available Secure Cloud worker
that meets the frozen CPU/RAM floor. No R4 output is overwritten or reclassified.

The 24-hour authority is prospective. After R5 preflight GREEN, Codex may freeze
and independently review one final 24-hour campaign packet without another
routine confirmation, provided it remains one worker at a time, one measured
campaign, no post-upload replacement, no production/client/private data, at most
28 paid hours, and at most `$35.00` aggregate final-campaign cost. Any price,
worker, evidence, or lifecycle requirement outside that envelope requires a new
human gate.

Successful completion may set only:

`PDH3_R12_PREFLIGHT_GREEN__24H_PACKET_FREEZE_AUTHORIZED`

Any non-GREEN stage, missing evidence, expired window, cost uncertainty,
capability mismatch, or teardown uncertainty sets:

`PDH3_R12_PREFLIGHT_BLOCKED`

## 2. Bound documents and source

- plan SHA-256:
  `a1214b4779fe1495de219ed0033421ac810390641cd97742deb61cd3957df3d9`
- resource amendment R2 SHA-256:
  `4bf4e47b79a66c672208cbd90f18ad31ff4f23400e833c728a189507dbb0e0b9`
- PF-2 resource amendment R3 SHA-256:
  `0068c17d1c2e515181f209848bd383da08c33893b1e0fb738acefab49070a41e`
- threshold-timing amendment R1: bound by its file SHA-256 recorded in the
  request and judge receipt;
- implementation commit:
  `063444ca484bb26b037713c722ed2fd7ba63dd04`
- frozen product candidate:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- bundle bytes: `143,981,919`;
- deterministic bundle SHA-256:
  `5f0fcd166717b122ac170cbc3f0b8a1b5b6567af85a78ed30291406ca7856332`
- bundle verification SHA-256:
  `1ae40e6439c7eda2efa8b7a746dbe0f3af2e64518b34c32f61b428b202f6d9b4`
- source-set SHA-256:
  `63ad4959f7d35a4dbd29d502e27c4305eec879fa53ba23d72ec095a9c4578b57`
- manifest SHA-256:
  `62538021561021cf339ee6de835ddddda11a0f405c9100031a5318c44daff435`
- bundle receipt SHA-256:
  `a80371dafb417609094042a74529211e73ec81ed552301bfbf36f9a86f2e3714`
- extracted smoke SHA-256:
  `e893e44ab71b8f4fe4910be3513dba5824946fb4d965026c105e3ab7bd0d4004`
- attempt-history manifest SHA-256:
  `72877c307496cd57d910385c8aa898c779d449170f7134478eb5d2a2702cbe1e`
- CockroachDB v26.2.3 Linux binary SHA-256:
  `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`
- RunPodCTL version: `2.7.2-309512b`;
- RunPodCTL SHA-256:
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- R4 blocked receipt SHA-256:
  `bf76393e2ec7ab83af5ddff51491ef1a5a338f1e396ca64f3a1963cce6599cf4`;
- R4 closeout commit:
  `104b01a6e6329d91b5c9d516a1effe5b8ab9c45d`;

Two independent bundle builds produced the same archive bytes and both
extracted smoke runs passed. The untracked `heap_profiler/` directory is
operator-owned, excluded from the source manifest, and must remain untouched.

## 3. Local gate state

- PF-0 contract/custody freeze: `GREEN`;
- PF-1 implementation/supervisor tests: `GREEN`;
- PF-2 local execution: `PF2_LOCAL_STORAGE_RESERVE_BLOCKED`, preserved;
- PF-2R: mandatory first remote database stage after PF-4;
- PF-3: `PF3_LOCAL_RESOURCE_BOUNDARY_GREEN`; no weaker local result is claimed;
- 32 R12 unit tests and the 10-test bundle suite passed at commit `063444c`;
- extracted bundle compilation covered 33 Python files and 12 test programs;
- no RunPod worker was active at packet freeze.

## 4. Live provider evidence and mechanical selection

Prepacket provider evidence:

- active Pod inventory: `[]`;
- active-inventory SHA-256:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`;
- live GPU inventory reports `NVIDIA L40S` available in Secure
  Cloud;
- live GPU-inventory SHA-256:
  `59e58fcb9ae0e2c1f8ef169dedda834a80b54fe3f823d01910801be29822f48e`;
- official pricing page snapshot SHA-256:
  `168f04ec7db90a391166f2ef6e73c227d260fef237b431509dfca38f5e075ac6`;
- page row: 16 vCPUs, 94 GB RAM, 48 GB VRAM, Secure Cloud `$0.99/hour`.
- sanitized account check: client balance `$85.4792497224`, current provider
  spend `$0.002/hour`, account spend limit `$140`, and low-balance notices
  enabled. No account identifier, email, token, or credential is recorded.
- sanitized account snapshot SHA-256:
  `372bf126a125d618e669b016ec1bd4026534655d8a35184a2a2dc4c6dd236049`.

The RTX 3090 was cheaper but its one R4 creation request failed for provider
capacity. The L40S is the next-cheapest currently visible Secure Cloud offer
whose published 16-vCPU/94-GB pair meets the frozen provider `memoryInGb >= 94`
and CPU requirements. The GPU is unused and creates no product claim.

## 5. Frozen provider envelope

- campaign ID and Pod name: `ck-pdh3-r12-preflight-r5-01`;
- cloud: `SECURE`;
- compute type: `GPU` only because the qualifying worker is sold as a GPU
  worker;
- GPU ID: `NVIDIA L40S`;
- GPU count: `1`, unused by the workload;
- image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- container disk: exactly `250 GB`;
- persistent/network volume: `0 GB`;
- exposed port: `22/tcp` only;
- one worker at a time;
- creation attempts: exactly `1`;
- launch window: `2026-08-02T06:50:00Z` through
  `2026-08-02T07:50:00Z`;
- provider-native stop-after: `2026-08-02T16:35:00Z`;
- provider-native terminate-after: `2026-08-02T16:50:00Z`;
- maximum paid lifetime: `10 hours` from the earliest permitted creation;
- compute-rate ceiling: `$0.99/hour`;
- container-storage allowance: conservatively `$0.40` over the bounded life;
- aggregate new-preflight cost ceiling: `$11.00`;
- no provider billing-setting or account-limit changes.

The deterministic preflight bound is `$0.99/hour × 10 hours + $0.40 =
$10.30`, below the `$11.00` ceiling.

Immediately before creation, inventory and pricing must be fetched again. The
worker may be created only if the inventory is still empty, the exact offer is
available, the official price remains no more than `$0.99/hour`, and the launch
window is open. The returned response must match name, cloud, GPU, image, disk,
zero-volume, and rate before any upload.

The exact creation argv is:

```text
/tmp/runpodctl-v2.7.2-darwin-arm64 pod create --cloud-type SECURE --compute-type GPU --gpu-id NVIDIA L40S --gpu-count 1 --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --name ck-pdh3-r12-preflight-r5-01 --container-disk-in-gb 250 --volume-in-gb 0 --ports 22/tcp --stop-after 2026-08-02T16:35:00Z --terminate-after 2026-08-02T16:50:00Z --output json
```

Shell interpolation is forbidden. Arguments are passed as an array.

## 6. PF-4 pre-upload gate

Immediately after a matching creation response:

1. start the exact-ID detached local lifecycle guard and prove PPID 1 plus an
   advancing hash-chained heartbeat;
2. prove SSH readiness without uploading the main bundle;
3. upload only `pdh3_r12_network_observer.py` and
   `pdh3_r12_remote_capability.py`, verify their remote SHA-256 values, and run
   the frozen capability harness;
4. enforce every value in the threshold-timing amendment;
5. retrieve the canonical capability receipt, verify its local SHA-256, and
   prove the first off-worker round trip;
6. upload nothing else unless PF-4 is GREEN.

Any returned worker property mismatch or PF-4 failure consumes the single
attempt. Retrieve available evidence, delete the worker, prove exact-ID absence
and empty campaign-scoped inventory, and stop. A replacement is forbidden.

## 7. PF-2R through PF-7 on the same worker

Only after PF-4 GREEN:

1. upload the one frozen archive, recheck its SHA-256 remotely, and extract into
   a new generated root;
2. use the archive's own hash-bound verifier in explicit verification mode to
   re-run the bundle member/source verification and all extracted smoke tests;
3. execute only `pdh3_r12_remote_launcher.py`; its allowlisted `PATH` includes
   Ubuntu's `/usr/sbin` and `/sbin` for the pinned namespace tools, while its
   command graph contains no `--production` flag and no 86,400-second measured
   branch;
4. the remote network observer begins before the workload process tree;
5. execute PF-2R, PF-5, PF-6, and PF-7 sequentially exactly as defined in the
   plan and amendments;
6. the local checkpoint supervisor continuously retrieves complete canonical
   checkpoint archives, validates sequence/hash chains, and publishes signed
   acknowledgements back to the worker;
7. preserve all raw failure outputs and classify every terminal branch
   fail-closed;
8. the remote process kills only its own generated campaign process during the
   PF-7 interruption test; it never deletes the worker or accesses provider
   credentials.

PF-5 is the first full-cardinality proof. PF-2R and reduced tests cannot replace
it. PF-6 preserves literal 500-worker concurrency and the original 5s/10s
latency limits. PF-7 runs the 15-minute growth, same-host process-fault, and
off-worker interruption proof. No final 24-hour measured clock can start.

## 8. Host supervision, closeout, and cost law

The host control plane must:

- verify the RunPodCTL hash before every provider action;
- use one exact Pod ID and campaign name;
- retain provider create/get/list/stop/delete stdout and stderr;
- treat transport failure, absent result, partial archive, corrupt archive,
  observer loss, lifecycle-guard loss, and semantic non-GREEN as mutually
  exclusive non-GREEN states;
- retrieve and hash-verify available evidence before deletion;
- delete on success, failure, timeout, or interruption;
- prove exact-ID lookup absence and empty campaign-scoped active inventory;
- verify no local SSH, transfer, lifecycle, supervisor, database, or paid
  process remains;
- record known provider cost and label delayed billing as delayed rather than
  inventing a charge.

Known or delayed provider billing is evidence metadata, not permission to
exceed the `$11.00` deterministic ceiling. The frozen rate and maximum paid
lifetime mathematically bound this run below that ceiling.

## 9. Kill lines

Stop, retrieve, delete, and block on:

- judge verdict other than exact same-packet GREEN from served `glm-5.2`;
- mixed source, amendment, packet, bundle, runtime, or tool hash;
- launch window expiry;
- non-empty initial inventory;
- price, account-credit, worker, image, deadline, disk, volume, or identity
  uncertainty;
- secret, credential, private-path, client-data, production-data, HOME, Qdrant,
  StateV2, launchd, or unrelated-project access;
- undeclared egress;
- failed namespace/observer, hardware, disk, clock, cgroup, process-tree, or
  off-worker retrieval capability;
- any PF-2R, PF-5, PF-6, or PF-7 semantic failure;
- any missing checkpoint, evidence class, raw failure output, or terminal
  receipt;
- any p99 greater than 5 seconds or maximum greater than 10 seconds;
- any cardinality, reconciliation, ANN, regression, concurrency, recovery,
  latency, observer-overhead, or growth failure;
- lifecycle heartbeat loss or unprovable teardown;
- any path that would create a second worker or start a 24-hour campaign.

## 10. Independent review contract

The judge receives this complete sanitized packet, the bound threshold-timing
amendment, and their exact SHA-256 values. The judge has no shell, write,
browser, deployment, credential, coding, or implementation authority.

Return exactly:

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: <exact packet hash>
TARGET_THRESHOLD_AMENDMENT_SHA256: <exact amendment hash>
VERDICT: GREEN | NOT_GREEN | BLOCKED | JUDGE_UNAVAILABLE
CRITICAL_FINDINGS:
- <finding or NONE>
HIGH_FINDINGS:
- <finding or NONE>
REQUIRED_CORRECTIONS:
- <correction or NONE>
RATIONALE: <concise evidence-based explanation>
```

GREEN authorizes only this one bounded paid preflight. It does not certify any
stage, erase the threshold-order disclosure, authorize a retry, or itself
certify/start the final 24-hour campaign. Kenneth's prospective 24-hour
authorization becomes executable only through a newly frozen final packet and
fresh independent same-hash GREEN after this preflight closes GREEN.
