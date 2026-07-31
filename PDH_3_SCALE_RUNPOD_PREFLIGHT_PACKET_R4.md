# PDH-3 Production-Shaped Scale RunPod Preflight Packet R4

## Judge task

Act only as an independent, non-authoring preflight judge. Evaluate whether the
exact bounded campaign below is safe, internally consistent, evidence-capable,
and ready for one paid worker. Do not write code, redesign the product, invoke
tools, request credentials, or treat missing future measured results as a
preflight defect.

Return one JSON object. A single Markdown `json` fence around that object is
accepted only because the current verified GLM wrapper emits that presentation;
the fence is mechanically stripped and the enclosed bytes must parse exactly:

```json
{"verdict":"GREEN|NOT_GREEN|BLOCKED","candidate_immutability":"GREEN|NOT_GREEN","workload_and_thresholds":"GREEN|NOT_GREEN","credential_and_data_boundary":"GREEN|NOT_GREEN","lifecycle_and_cost":"GREEN|NOT_GREEN","evidence_and_teardown":"GREEN|NOT_GREEN","blockers":[],"limitations":[]}
```

`GREEN` is valid only when every named dimension is GREEN and blockers is empty.

## Current authority

- parent evidence commit: `73aab4d46e4e6f424898a5796b5a98d8e4131d3f`
- immutable product candidate:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- active plan SHA-256:
  `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- operator authorization SHA-256: `f4099665a55fc632255eba55f50ead39d4c84f79fd494e6dea8392f91a735c82`
- preflight bindings SHA-256: `5f6ba6c422606b3f8f567e08bbcdf3d1141e4a739689053bbde1ba9ae718945b`
- active paid RunPod inventory before launch: `[]`

The candidate product commit is frozen. This packet introduces only the
campaign controller, validation, bundle builder, tests, receipts, and lifecycle
evidence. It does not modify the product candidate.

## Stated goal and kill line

Goal: obtain one final production-shaped scale/reliability data point for the
frozen product by running a credential-free, synthetic, 24-hour workload
against a three-node local CockroachDB cluster inside one disposable Secure
Cloud L40S worker.

Kill line: stop and delete the worker on any identity, rate, image, disk,
volume, hash, namespace, evidence, checkpoint, latency, growth, determinism,
cross-task isolation, retry, crash-recovery, cleanup, credential, private-data,
or lifecycle mismatch. No replacement is allowed after the measured workload
begins.

## Exact provider and economic envelope

- RunPod Secure Cloud; one `NVIDIA L40S`; one GPU;
- accepted returned host range: exactly 16 vCPU, 94 through 188 GB RAM,
  and 48 GB VRAM;
- exact image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- exposed ports: `22/tcp` only; global networking omitted/disabled;
- 250 GB disposable container disk;
- zero persistent volume and zero network volume;
- official current Secure L40S compute rate ceiling: `$0.99/hour`;
- container disk pricing: `$0.10/GB/month`, approximately `$0.0348/hour`;
- total active-rate ceiling: `$1.10/hour`;
- maximum paid lifetime: 100,800 seconds / 28 hours;
- maximum aggregate campaign charge: `$35.00`;
- conservative 28-hour compute plus container-disk estimate: approximately
  `$28.69`;
- launch window: `2026-07-31T04:00:00Z` through `2026-07-31T05:00:00Z`;
- provider stop-after: `2026-08-01T07:45:00Z`;
- provider terminate-after: `2026-08-01T08:00:00Z`;
- local guard stop epoch: `1785570300`;
- local guard delete epoch: `1785571200`.

The GPU is not used for model inference. The L40S shape was explicitly selected
and authorized for its current Secure Cloud 16-vCPU/94-GB host allocation and
reliability envelope. The workload is CPU, memory, disk, and database bound.

## Creation command and retry law

For each unique attempt name inside the frozen launch window:

```text
/tmp/runpodctl-v2.7.2-darwin-arm64 pod create
  --cloud-type SECURE
  --compute-type GPU
  --gpu-id "NVIDIA L40S"
  --gpu-count 1
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404
  --name <unique ck-pdh3-scale-r1-aNN name>
  --container-disk-in-gb 250
  --volume-in-gb 0
  --ports 22/tcp
  --stop-after 2026-08-01T07:45:00Z
  --terminate-after 2026-08-01T08:00:00Z
  --output json
```

At most eight sequential pre-workload attempts are allowed, with one extant
worker maximum. A failed or mismatched worker must be deleted, followed by
exact-ID absence and empty matching-campaign active inventory, before another
attempt. Three consecutive identical failures stop blind retries. Retry is
allowed only for provider creation/capacity, returned-shape/image/price
mismatch, readiness, SSH, hash-checked transfer, extracted-bundle validation,
or namespace canary failure before measured execution. Any credential/private
data exposure, unbounded price, failed deletion, product/source drift, or
evidence-contract defect ends the campaign. Once measured execution starts,
there is no replacement, restart, extension, or second measured run.

## Worker verification and credential boundary

Before upload, verify exact worker ID/name, Secure Cloud, one L40S, exactly 16
vCPU, RAM between 94 and 188 GB inclusive, one GPU, image, 250 GB container
disk, zero volume/network volume, rate no greater than `$1.10/hour`, and the
frozen stop/terminate request.
Provider deadline readback is recorded if exposed; otherwise retain the exact
creation request/response without claiming readback.

The local exact-ID guard is bound immediately after creation. It hash-pins
runpodctl, checks worker identity on every heartbeat, survives parent-shell
exit, records a hash chain, performs bounded stop/delete retries, and declares
teardown only after exact-ID absence plus empty matching active inventory.

Only the R3 archive and this packet are uploaded. Their hashes are verified
before extraction. No AWS, CockroachDB Cloud, GitHub, package-registry, model,
HOME, client, private, or production credential/data is transferred. SSH is
used only for bounded transfer, start, observation, retrieval, and teardown.
The workload launches in a fresh user/network namespace with loopback enabled
and no external egress. Namespace failure blocks before measured execution.

## Remote canary and measured command

After extraction and hash verification, execute a 60-second reduced canary
through the same controller inside the no-egress namespace. It must prove
three-node startup, seed, workload, 43 verifier executions, one node
crash/restart, exact reconciliation, database drop, closed ports, stopped
processes, and removed generated root.

Only after that canary is GREEN, execute exactly:

```text
PDH3_PACKET_SHA256=<this packet SHA-256>
python3 post-dogfood/run_pdh3_scale_campaign.py
  --binary p2-cleanroom/vendor/cockroach-v26.2.3-linux/cockroach-v26.2.3.linux-amd64/cockroach
  --packet <this exact packet>
  --output /runpod-volume-disabled/ck-pdh3-scale-r1/evidence
  --campaign-id ck-pdh3-scale-r1
  --production
  --duration-seconds 86400
  --checkpoint-seconds 300
  --tasks 500000
  --events-per-task 10
  --receipts-per-task 2
  --vectors 250000
  --max-concurrency 500
  --query-duration-seconds 120
  --seed-batch-tasks 5000
  --setup-timeout-seconds 5400
  --fault-every-checkpoints 12
  --disk-used-fraction-limit 0.70
  --cache 8GiB
  --sql-memory 8GiB
```

The displayed remote path is a disposable container path name only; no RunPod
volume or network volume is attached.

## Workload and direct acceptance thresholds

- three CockroachDB v26.2.3 nodes;
- 500,000 task rows;
- 5,000,000 trajectory-event rows;
- 1,000,000 receipt rows;
- 250,000 task-bound vector rows;
- exactly 9,976 fresh-process verifier executions in 232 batches of 43;
- concurrency stages 10, 50, 100, 250, and 500;
- exactly 288 five-minute checkpoints over 86,400 measured seconds;
- 24 rotating node `SIGKILL`/surviving-query/restart/reconciliation cycles;
- duplicate/idempotency, SQLSTATE 40001 retry, rollback, deterministic verdict,
  quarantine exclusion, stale/malformed/throttled/timeout advice states, and a
  concurrent create/delete cleanup probe;
- zero false promotions, zero cross-task vector links, zero acknowledged write
  loss, zero accepted replays, and zero cleanup residue;
- p99 no greater than 5,000 ms and maximum latency no greater than 10,000 ms;
- database bytes no greater than 100 GiB;
- evidence bytes no greater than 20 GiB;
- container disk occupancy no greater than 70%;
- every canonical checkpoint, journal event, result, manifest, and teardown
  receipt hash-linked and fsynced.

All failures are retained. Results cannot be pooled with prior campaigns and
there is no post-result tuning. A completed command is not success unless every
threshold and teardown check is directly GREEN.

## Closeout

Stop the workload; flush/fsync evidence; archive it; retrieve logs, evidence,
hashes, canary, system inventory, and provider records; verify local hashes
against remote hashes; stop/delete the worker; prove exact-ID absence and empty
campaign active inventory; prove no guard/SSH/transfer/database/watchdog
process remains; reconcile provider billing as available; and write the final
receipt. Exact billing must never be fabricated. A delayed provider billing
record is a disclosed reconciliation limitation, not permission to exceed the
authorized rate/lifetime/cost envelope.

The measured campaign cannot claim GREEN until one final independent GLM
review over the exact frozen final evidence packet is GREEN. This preflight
only authorizes worker creation.

## Evidence already obtained

# PDH-3 Final RunPod Authorization Receipt R1

- `OPERATOR`: Kenneth
- `UTC_RECORDED`: `2026-07-31T03:19:30Z`
- `PROVIDER`: RunPod
- `CLOUD`: Secure Cloud
- `GPU`: NVIDIA L40S
- `MEASURED_WORKLOAD`: 24 hours / 86,400 seconds
- `MAXIMUM_PAID_LIFETIME`: 28 hours / 100,800 seconds
- `AGGREGATE_COST_CEILING_USD`: `$35.00`
- `CURRENT_COMPUTE_RATE_CEILING_USD_HOUR`: `$0.99`
- `TOTAL_ACTIVE_RATE_CEILING_USD_HOUR`: `$1.10`
- `CONTAINER_DISK`: 250 GB disposable
- `PERSISTENT_OR_NETWORK_VOLUME`: none

## Exact operator authorization

> I approve one Secure Cloud L40S RunPod campaign with a 24-hour measured
> workload, 28-hour maximum paid lifetime, and $35 aggregate cost ceiling.

## Scope

This authorization permits:

- local implementation and preflight of the credential-free PDH-3 controller;
- bounded pre-workload creation retries for one verified Secure Cloud L40S;
- one measured workload after the worker and extracted bundle pass;
- provider charges inside the exact ceilings above;
- evidence retrieval, stop, termination, deletion, billing reconciliation,
  and zero-resource inventory verification.

It does not permit:

- AWS, CockroachDB Cloud, GitHub, package-registry, or model credentials in the
  worker;
- persistent/network volumes;
- client, private, or production data;
- a replacement after measured execution begins;
- a different GPU, cloud class, rate, duration, or aggregate spend;
- PDH-4, release, publication, or submission.

The router's paid-resource human gate is satisfied only for this exact
lifecycle. Independent preflight remains mandatory before worker creation.


# PDH-3 Scale Controller Local Smoke Report R1

## Result

`PDH_3_SCALE_LOCAL_SMOKE_GREEN`

- `CAMPAIGN`: `ck-pdh3-scale-local-r4`
- `PRODUCT_CANDIDATE`:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PACKET_SHA256`:
  `c0cd692e3fb630fba54aabf8dcff40125a3d8c8636e0120afe3b7b337f15d49a`
- `RESULT_SHA256`:
  `14895d952dec265a3348b9a5320fc4e48a7931dfce10a3a1efad3c0ed64f2688`
- `EVIDENCE_MANIFEST_SHA256`:
  `19feefd9ce5d8371a1a3af3b44b6fee7aa45951b5576e81231c15c2e40b80f00`
- `TEARDOWN_RECEIPT_SHA256`:
  `41c8ec39e13a46bc13e774b2559e29e1f5a32f621fb9faa305b1498e1ec133a0`

## Measured behavior

- three CockroachDB v26.2.3 nodes on isolated loopback ports;
- 60.001039084 measured seconds;
- 25,455 measured operations;
- 43 fresh-process verifier executions;
- one rotating-node `SIGKILL`, surviving-node query, restart, and exact-count
  reconciliation;
- 100 tasks, 300 trajectory events, 100 receipts, and 50 task-bound vectors;
- zero cross-task vector links;
- five synthetic dependency-advice outcome states;
- one concurrent create/delete cleanup probe with zero residue;
- maximum p99 218.1 ms and maximum observed latency 453.0 ms;
- every final green check true.

## Failed attempts preserved

- R1 and R2 exposed that CockroachDB's `sha256` SQL result required explicit
  hex decoding into `BYTES`.
- R3 exposed that a remote-container disk-occupancy ceiling cannot be
  interpreted against unrelated existing Mac host occupancy.
- R4 preserves the remote production ceiling at exactly 70% while recording,
  but not misclassifying, pre-existing local host disk occupancy.

No failed attempt was pooled into the R4 pass.

## Teardown

- database dropped;
- three database processes stopped;
- all six SQL/HTTP ports closed;
- generated root removed;
- no credential, AWS call, CockroachDB Cloud call, GitHub call, external model
  call, persistent volume, or paid resource used.

This report proves controller-path readiness only. It is not paid cloud,
production-scale, multi-region, or production-traffic evidence.


# PDH-3 Credential-Free Bundle Scan Receipt R4

- `UTC_CREATED`: `2026-07-31T04:03:40Z`
- `REMOTE_EXECUTION_CANDIDATE`: `YES`
- `SUPERSEDES_FOR_REMOTE_USE`: `R1`, `R2`, and `R3`
- `ARCHIVE_SHA256`:
  `072fc945b79dfdb0c85e2edc9406e7a4fb75751f72128a97ab80611c4d092b72`
- `ARCHIVE_BYTES`: `142828959`
- `BUNDLE_RECEIPT_FILE_SHA256`:
  `6931db17780e456096a36f1b926b3cbb6344350dea147d58e22abdbfbb963b3a`
- `BUNDLE_RECEIPT_CANONICAL_SHA256`:
  `6eb05b60a22ba5f15b8101e6b59b86729c24cbb4689454f103adf8215bf99763`
- `SOURCE_SET_SHA256`:
  `448571283fd2f7501e1b65c3baf6f079644d20a2ad00ea606c3d10e127c11a88`
- `MANIFEST_SHA256`:
  `4036903461119d87381c00c18c4df3d985fe2d4a935e7ae17658a55c0ec803df`
- `ARCHIVE_ENTRIES`: `17`
- `UNSAFE_ARCHIVE_ENTRIES`: `0`
- `DETECT_SECRETS_FINDINGS`: `0`
- `ACTIONABLE_RG_FINDINGS`: `0`
- `GITLEAKS_RAW_FINDINGS`: `1`
- `GITLEAKS_ACTIONABLE_FINDINGS`: `0`

The one raw Gitleaks match remains the previously classified
`sourcegraph-access-token` false positive in the official CockroachDB
`THIRD-PARTY-NOTICES.txt`, whose complete SHA-256 is
`af9d8c7290aafeec05409e728cffca8c613936968ae7178b716ee34681812d83`.

The extracted source compiles. Its verifier smoke is GREEN across 43
executions, 43 correct stable reasons, zero false promotion, zero refusal
mutation, 43 teardowns, and zero residue. The canonical aggregate SHA-256 is
`ed0725ecf993e91fa93f03d7cd27f22c1fbd7348070bb1cf60d3cd0f0a2f5081`;
the aggregate file SHA-256 is
`cbf55eaaa5b84e8f59ff3ce62cf49d30621c52e9211d1e633a8a93df68eaa3ca`.

R4 changes only the accepted same-price provider RAM range from exact 94 GB to
94–188 GB. Every other executable source, runtime, image, port, workload,
threshold, credential, storage, rate, duration, and teardown boundary is
unchanged.


# PDH-3 RunPod Attempt 01 Receipt

- `ATTEMPT`: `1`
- `POD_ID`: `xc0teveqftq5dr`
- `POD_NAME`: `ck-pdh3-scale-r1-a01`
- `CREATE_UTC`: `2026-07-31T04:00:06Z`
- `CLASSIFICATION`: `RETURNED_HOST_MEMORY_OUTSIDE_EXACT_R3_CONTRACT`
- `UPLOAD_OCCURRED`: `NO`
- `WORKLOAD_OCCURRED`: `NO`
- `RETURNED_CLOUD/GPU`: `Secure Cloud / NVIDIA L40S`
- `RETURNED_VCPU`: `16`
- `RETURNED_RAM_GB`: `188`
- `RETURNED_GPU_COUNT`: `1`
- `RETURNED_IMAGE`:
  `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`
- `RETURNED_CONTAINER_DISK_GB`: `250`
- `RETURNED_VOLUME_GB`: `0`
- `RETURNED_COMPUTE_RATE_USD_HOUR`: `$0.99`
- `DELETE_RESULT`: `GREEN`
- `EXACT_ID_POST_DELETE`: `404 pod not found`
- `ACTIVE_INVENTORY_POST_DELETE`: `[]`

Attempt 01 satisfied every provider and economic property except the R3
packet's exact `94 GB` RAM assertion. The provider returned `188 GB` at the
same rate. The worker was deleted immediately before SSH readiness, upload,
namespace work, or workload execution.

The raw creation response is retained locally because it contains the
operator's public SSH-key material. It is not copied into this packet.

- `RAW_CREATE_RESPONSE_SHA256`:
  `7f287f989f7d342f2a380ae71688bd01952eba60fa773a534facc19780c5811c`
- `RAW_DELETE_RESPONSE_SHA256`:
  `fe442e5df00f39b43edb79d73c0b535415d0a999a55fd0576fde6f5404b67eef`
- `POST_DELETE_GET_SHA256`:
  `abb343a1a20364080e68a3fa77e863e71c3dc444e3f06cb1467cdf87df479556`
- `POST_DELETE_ACTIVE_INVENTORY_SHA256`:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`

R4 accepts the observed current provider range of 94 through 188 GB only;
it does not relax the GPU, vCPU, image, storage, rate, duration, volume,
credential, evidence, retry, or teardown boundary.


The local smoke used the final controller source but preceded two
contract-only hardenings that pinned production scheduling parameters and the
exact remote image/port boundary. Those hardenings do not alter controller
behavior; they are directly covered by the eight passing unit tests, the
deterministic R3 archive, compile checks, secret scans, and the extracted R3
43-execution verifier smoke.

The detached guard proof is GREEN:

```json
{"bound": true, "detached_session": "ck-s2-guard-proof-31548", "events": 8, "state_absent": true, "status": "GREEN", "teardown": true, "terminal_hash": "88d4a74f9a633ba8e276b0d157a70877d30b3da7cb17e1803f352718d80f303e"}
```

## Canonical bindings

```json
{"authorization_sha256":"f4099665a55fc632255eba55f50ead39d4c84f79fd494e6dea8392f91a735c82","bindings_sha256":"5f6ba6c422606b3f8f567e08bbcdf3d1141e4a739689053bbde1ba9ae718945b","bundle":{"archive_bytes":142828959,"archive_sha256":"072fc945b79dfdb0c85e2edc9406e7a4fb75751f72128a97ab80611c4d092b72","manifest_sha256":"4036903461119d87381c00c18c4df3d985fe2d4a935e7ae17658a55c0ec803df","receipt_sha256":"6eb05b60a22ba5f15b8101e6b59b86729c24cbb4689454f103adf8215bf99763","source_set_sha256":"448571283fd2f7501e1b65c3baf6f079644d20a2ad00ea606c3d10e127c11a88"},"extracted_bundle_smoke":{"aggregate_sha256":"ed0725ecf993e91fa93f03d7cd27f22c1fbd7348070bb1cf60d3cd0f0a2f5081","executions":43,"green":true},"launch_window":{"end":"2026-07-31T05:00:00Z","start":"2026-07-31T04:00:00Z","stop_after":"2026-08-01T07:45:00Z","stop_epoch":1785570300,"terminate_after":"2026-08-01T08:00:00Z","terminate_epoch":1785571200},"lifecycle_guard_proof":{"bound":true,"state_absent":true,"status":"GREEN","teardown":true,"terminal_hash":"88d4a74f9a633ba8e276b0d157a70877d30b3da7cb17e1803f352718d80f303e"},"local_smoke":{"campaign":"ck-pdh3-scale-local-r4","manifest_sha256":"19feefd9ce5d8371a1a3af3b44b6fee7aa45951b5576e81231c15c2e40b80f00","result_sha256":"14895d952dec265a3348b9a5320fc4e48a7931dfce10a3a1efad3c0ed64f2688","teardown_sha256":"41c8ec39e13a46bc13e774b2559e29e1f5a32f621fb9faa305b1498e1ec133a0"},"parent_commit":"73aab4d46e4e6f424898a5796b5a98d8e4131d3f","plan_sha256":"bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24","product_candidate":"1c483b1930e629c9ecb6d73418b9554897dc08ad","provider_state":{"active_inventory":[],"container_disk_usd_gb_month":0.1,"l40s_offer":[{"available":true,"communityCloud":true,"displayName":"L40S","gpuId":"NVIDIA L40S","memoryInGb":48,"secureCloud":true,"stockStatus":"Low"}],"official_secure_l40s_compute_usd_hour":0.99,"official_template":{"category":"NVIDIA","containerDiskInGb":30,"id":"runpod-torch-v280","imageName":"runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404","isPublic":true,"isRunpod":true,"name":"Runpod Pytorch 2.8.0","ports":["8888/http","22/tcp","22/udp"],"portsConfig":[{"name":"SSH","port":"22"},{"name":"Jupyter Notebook","port":"8888"}],"readme":"# PyTorch Environment\n\nReady-to-use PyTorch + Python development environment with JupyterLab and common development tools pre-installed:\n\n- Jupyter Notebook 6.5.5\n- JupyterLab with widgets and extensions\n- Pre-configured workspace directory\n- SSH access\n- NGINX server\n- Development tools\n\n## Ports\n\n| Application | Port | Type |\n| ----------- | ---- | ---- |\n| Jupyter     | 8888 | HTTP |\n| SSH         | 22   | TCP  |\n","volumeInGb":50,"volumeMountPath":"/workspace"}},"receipt_files":[{"bytes":1603,"path":"PDH_3_SCALE_AUTHORIZATION_RECEIPT_R1.md","sha256":"f4099665a55fc632255eba55f50ead39d4c84f79fd494e6dea8392f91a735c82"},{"bytes":1562,"path":"PDH_3_SCALE_LOCAL_SMOKE_PACKET_R1.md","sha256":"c0cd692e3fb630fba54aabf8dcff40125a3d8c8636e0120afe3b7b337f15d49a"},{"bytes":2029,"path":"PDH_3_SCALE_LOCAL_SMOKE_REPORT_R1.md","sha256":"c0c1f10fccd3e1c896f4a5e59aa541ccb51abd9431cf3c83e71c964563a279fa"},{"bytes":1759,"path":"PDH_3_SCALE_BUNDLE_SCAN_RECEIPT_R4.md","sha256":"226218c0b73f01fb9fd24ea181aa5f91c7ae7b48541fd308c1b017146cfe149f"},{"bytes":1721,"path":"PDH_3_SCALE_RUNPOD_ATTEMPT_01_RECEIPT.md","sha256":"e31d2571e3272cb732a1af8dd8b3233a7e9f0c69d74352b0228c46e9bab2b1b7"}],"runpodctl":{"sha256":"a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037","version":"2.7.2-309512b"},"source_files":[{"bytes":4879,"path":"post-dogfood/pdh3_scale_contract.py","sha256":"952f2093ed696b5f62b0cd03a8a0e769c34e3bf6443392483ceaca51f0d93277"},{"bytes":42017,"path":"post-dogfood/run_pdh3_scale_campaign.py","sha256":"de4fd0cba5ac07bb13867fef1b740d77817abf26918b0f0e2e391cfee488e94e"},{"bytes":4726,"path":"post-dogfood/build_pdh3_scale_bundle.py","sha256":"7bb35e100fee7c8b1297e04536f7074e9e24a38a61ca2c8054b9708f1ba0dca9"},{"bytes":7950,"path":"s2-soak/lifecycle_guard.py","sha256":"4644aa756f47c3d53b82c239657ce22605d4a9caab3e6a8651c4f459d95c6f0c"}],"version":"ck-pdh3-scale-preflight-bindings-v1"}
```

## Load-bearing source

### `post-dogfood/pdh3_scale_contract.py`

```python
#!/usr/bin/env python3
"""Frozen constants and validation for the final PDH-3 scale campaign."""
from __future__ import annotations

import hashlib
import json
from typing import Any


VERSION = "ck-pdh3-production-scale-contract-v1"
PRODUCT_CANDIDATE = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
PLAN_SHA256 = "bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24"

MEASURED_SECONDS = 86_400
MAX_PAID_SECONDS = 100_800
CHECKPOINT_SECONDS = 300
REQUIRED_CHECKPOINTS = 288
QUERY_DURATION_SECONDS = 120
SEED_BATCH_TASKS = 5_000
SETUP_TIMEOUT_SECONDS = 5_400
FAULT_EVERY_CHECKPOINTS = 12
NODE_CACHE = "8GiB"
NODE_SQL_MEMORY = "8GiB"

TASKS = 500_000
EVENTS_PER_TASK = 10
RECEIPTS_PER_TASK = 2
VECTORS = 250_000
VERIFIER_EXECUTIONS = 9_976
VERIFIER_BATCH_SIZE = 43
VERIFIER_BATCHES = 232

CONCURRENCY_STAGES = (10, 50, 100, 250, 500)
MAX_CONCURRENCY = 500
P99_LIMIT_MS = 5_000.0
PMAX_LIMIT_MS = 10_000.0
DATABASE_BYTES_LIMIT = 100 * 1024**3
EVIDENCE_BYTES_LIMIT = 20 * 1024**3
DISK_USED_FRACTION_LIMIT = 0.70

RUNPOD = {
    "cloud": "SECURE",
    "gpu_id": "NVIDIA L40S",
    "gpu_count": 1,
    "image": "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
    "ports": ["22/tcp"],
    "global_networking": False,
    "vcpu": 16,
    "ram_gb_min": 94,
    "ram_gb_max": 188,
    "container_disk_gb": 250,
    "volume_gb": 0,
    "network_volume": None,
    "compute_rate_usd_hour_max": 0.99,
    "active_rate_usd_hour_max": 1.10,
    "aggregate_cost_usd_max": 35.00,
    "measured_seconds": MEASURED_SECONDS,
    "paid_seconds_max": MAX_PAID_SECONDS,
}

FORBIDDEN_RUNTIME_DEPENDENCIES = (
    "AWS credentials or login",
    "CockroachDB Cloud credentials or login",
    "GitHub credentials or login",
    "package-registry credentials",
    "persistent or network volume",
    "private, client, or production data",
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: bytes | Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def production_contract() -> dict[str, Any]:
    body = {
        "version": VERSION,
        "product_candidate": PRODUCT_CANDIDATE,
        "plan_sha256": PLAN_SHA256,
        "runpod": RUNPOD,
        "workload": {
            "tasks": TASKS,
            "trajectory_events": TASKS * EVENTS_PER_TASK,
            "receipts": TASKS * RECEIPTS_PER_TASK,
            "task_bound_vectors": VECTORS,
            "verifier_executions": VERIFIER_EXECUTIONS,
            "verifier_batches": VERIFIER_BATCHES,
            "concurrency_stages": list(CONCURRENCY_STAGES),
            "checkpoints": REQUIRED_CHECKPOINTS,
            "checkpoint_seconds": CHECKPOINT_SECONDS,
            "query_duration_seconds": QUERY_DURATION_SECONDS,
            "seed_batch_tasks": SEED_BATCH_TASKS,
            "setup_timeout_seconds": SETUP_TIMEOUT_SECONDS,
            "fault_every_checkpoints": FAULT_EVERY_CHECKPOINTS,
            "node_cache": NODE_CACHE,
            "node_sql_memory": NODE_SQL_MEMORY,
        },
        "thresholds": {
            "p99_ms": P99_LIMIT_MS,
            "pmax_ms": PMAX_LIMIT_MS,
            "database_bytes": DATABASE_BYTES_LIMIT,
            "evidence_bytes": EVIDENCE_BYTES_LIMIT,
            "disk_used_fraction": DISK_USED_FRACTION_LIMIT,
            "false_promotions": 0,
            "cross_task_vector_links": 0,
            "acknowledged_write_loss": 0,
            "accepted_replays": 0,
            "residual_paid_resources": 0,
        },
        "forbidden_runtime_dependencies": list(FORBIDDEN_RUNTIME_DEPENDENCIES),
    }
    return {**body, "contract_sha256": digest(body)}


def validate_production_arguments(arguments: dict[str, Any]) -> None:
    expected = {
        "duration_seconds": MEASURED_SECONDS,
        "checkpoint_seconds": CHECKPOINT_SECONDS,
        "tasks": TASKS,
        "events_per_task": EVENTS_PER_TASK,
        "receipts_per_task": RECEIPTS_PER_TASK,
        "vectors": VECTORS,
        "max_concurrency": MAX_CONCURRENCY,
        "disk_used_fraction_limit": DISK_USED_FRACTION_LIMIT,
        "query_duration_seconds": QUERY_DURATION_SECONDS,
        "seed_batch_tasks": SEED_BATCH_TASKS,
        "setup_timeout_seconds": SETUP_TIMEOUT_SECONDS,
        "fault_every_checkpoints": FAULT_EVERY_CHECKPOINTS,
        "cache": NODE_CACHE,
        "sql_memory": NODE_SQL_MEMORY,
    }
    mismatches = {
        key: {"expected": value, "actual": arguments.get(key)}
        for key, value in expected.items()
        if arguments.get(key) != value
    }
    if mismatches:
        raise ValueError("PRODUCTION_ARGUMENT_MISMATCH:" + digest(mismatches))


if __name__ == "__main__":
    print(canonical(production_contract()).decode("utf-8"))

```
### `post-dogfood/run_pdh3_scale_campaign.py`

```python
#!/usr/bin/env python3
"""Credential-free three-node PDH-3 production-shaped scale campaign.

The production mode is hash-bound to the frozen packet and exact 24-hour
contract. A reduced smoke mode exercises the same cluster, query, verifier,
fault, evidence, cleanup, and teardown paths without making scale claims.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from typing import Any

import pdh3_scale_contract as contract


BASE = Path(__file__).resolve().parents[1]
ZERO_HASH = "0" * 64


class CampaignError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: bytes | Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


class ChainLog:
    def __init__(self, path: Path, campaign_id: str) -> None:
        if path.exists():
            raise CampaignError("JOURNAL_ALREADY_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.campaign_id = campaign_id
        self.sequence = 0
        self.previous = ZERO_HASH
        self.started_ns = time.monotonic_ns()

    def emit(self, event: str, details: dict[str, Any]) -> dict[str, Any]:
        self.sequence += 1
        body = {
            "version": "ck-pdh3-scale-journal-v1",
            "campaign_id": self.campaign_id,
            "sequence": self.sequence,
            "event": event,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "elapsed_ns": time.monotonic_ns() - self.started_ns,
            "previous_hash": self.previous,
            "details": details,
        }
        record = {**body, "event_hash": digest(body)}
        with self.path.open("ab") as handle:
            handle.write(canonical(record) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous = record["event_hash"]
        return record


def load_canary_module() -> Any:
    path = BASE / "post-dogfood/run_pdh3_local_canary.py"
    spec = importlib.util.spec_from_file_location("pdh3_local_canary_reuse", path)
    if spec is None or spec.loader is None:
        raise CampaignError("CANARY_MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def reserve_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        return int(handle.getsockname()[1])


def scrubbed_env(fake_home: Path) -> dict[str, str]:
    return {
        "HOME": str(fake_home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "TZ": "UTC",
        "COCKROACH_SKIP_ENABLING_DIAGNOSTIC_REPORTING": "true",
    }


def run(
    command: list[str],
    *,
    env: dict[str, str],
    timeout: int,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        bounded_tail = completed.stdout[-2_000:].decode("utf-8", "replace")
        raise CampaignError(
            "COMMAND_FAILED:"
            + Path(command[0]).name
            + ":"
            + digest(completed.stdout)
            + ":"
            + bounded_tail
        )
    return completed


def sql(
    binary: Path,
    port: int,
    statement: str,
    *,
    env: dict[str, str],
    database: str | None = "cockroach_kernel",
    timeout: int = 300,
) -> bytes:
    command = [
        str(binary),
        "sql",
        "--insecure",
        f"--host=127.0.0.1:{port}",
        "--format=tsv",
    ]
    if database is not None:
        command.append(f"--database={database}")
    command.extend(["--execute", statement])
    return run(command, env=env, timeout=timeout).stdout


def parse_last_integer(raw: bytes) -> int:
    for line in reversed(raw.decode("utf-8", "replace").splitlines()):
        value = line.strip()
        if value.isdigit():
            return int(value)
    raise CampaignError("INTEGER_OUTPUT_MISSING")


def parse_count_tuple(raw: bytes, fields: int) -> tuple[int, ...]:
    for line in reversed(raw.decode("utf-8", "replace").splitlines()):
        values = line.strip().split("\t")
        if len(values) == fields and all(value.isdigit() for value in values):
            return tuple(int(value) for value in values)
    raise CampaignError("COUNT_OUTPUT_INVALID")


def tree_bytes(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


class Node:
    def __init__(
        self,
        index: int,
        sql_port: int,
        http_port: int,
        store: Path,
        log: Path,
    ) -> None:
        self.index = index
        self.sql_port = sql_port
        self.http_port = http_port
        self.store = store
        self.log = log
        self.process: subprocess.Popen[bytes] | None = None
        self.log_handle: Any | None = None


def node_command(
    binary: Path,
    node: Node,
    join: str,
    cache: str,
    sql_memory: str,
) -> list[str]:
    return [
        str(binary),
        "start",
        "--insecure",
        f"--store={node.store}",
        f"--listen-addr=127.0.0.1:{node.sql_port}",
        f"--advertise-addr=127.0.0.1:{node.sql_port}",
        f"--http-addr=127.0.0.1:{node.http_port}",
        f"--join={join}",
        f"--cache={cache}",
        f"--max-sql-memory={sql_memory}",
        "--logtostderr=ERROR",
    ]


def start_node(
    binary: Path,
    node: Node,
    join: str,
    cache: str,
    sql_memory: str,
    env: dict[str, str],
    *,
    append: bool,
) -> None:
    node.store.mkdir(parents=True, exist_ok=True)
    node.log_handle = node.log.open("ab" if append else "xb", buffering=0)
    node.process = subprocess.Popen(
        node_command(binary, node, join, cache, sql_memory),
        env=env,
        cwd=node.store.parent,
        stdin=subprocess.DEVNULL,
        stdout=node.log_handle,
        stderr=subprocess.STDOUT,
    )


def stop_node(node: Node, *, crash: bool) -> int:
    if node.process is None:
        return 0
    process = node.process
    if process.poll() is None:
        process.send_signal(signal.SIGKILL if crash else signal.SIGTERM)
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=15)
    code = int(process.returncode or 0)
    if node.log_handle is not None:
        node.log_handle.close()
    node.process = None
    node.log_handle = None
    return code


def start_cluster(
    binary: Path,
    root: Path,
    env: dict[str, str],
    cache: str,
    sql_memory: str,
) -> tuple[list[Node], str]:
    ports: set[int] = set()
    while len(ports) < 6:
        ports.add(reserve_port())
    values = list(ports)
    nodes = [
        Node(
            index=index,
            sql_port=values[index * 2],
            http_port=values[index * 2 + 1],
            store=root / f"node-{index + 1}/store",
            log=root / f"node-{index + 1}/cockroach.log",
        )
        for index in range(3)
    ]
    join = ",".join(f"127.0.0.1:{node.sql_port}" for node in nodes)
    for node in nodes:
        node.store.parent.mkdir(parents=True)
        start_node(binary, node, join, cache, sql_memory, env, append=False)
    run(
        [
            str(binary),
            "init",
            "--insecure",
            f"--host=127.0.0.1:{nodes[0].sql_port}",
        ],
        env=env,
        timeout=120,
    )
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            if parse_last_integer(
                sql(
                    binary,
                    nodes[0].sql_port,
                    "SELECT 1",
                    env=env,
                    database=None,
                    timeout=10,
                )
            ) == 1:
                return nodes, join
        except (CampaignError, subprocess.TimeoutExpired):
            time.sleep(1)
    raise CampaignError("THREE_NODE_CLUSTER_READINESS_TIMEOUT")


def apply_migrations(binary: Path, port: int, env: dict[str, str]) -> None:
    sql(binary, port, "CREATE DATABASE cockroach_kernel", env=env, database=None)
    for relative in (
        "p9-cloud/migrations/001_cloud.sql",
        "p9-cloud/migrations/003_collision_safe_vector_digest.sql",
    ):
        run(
            [
                str(binary),
                "sql",
                "--insecure",
                f"--host=127.0.0.1:{port}",
                "--database=cockroach_kernel",
                f"--file={BASE / relative}",
            ],
            env=env,
            timeout=600,
        )
    sql(
        binary,
        port,
        "CREATE TABLE ck.pdh3_acknowledged_writes "
        "(ack_id STRING PRIMARY KEY,created_at TIMESTAMPTZ NOT NULL);"
        "CREATE TABLE ck.pdh3_counter "
        "(id STRING PRIMARY KEY,value INT8 NOT NULL);"
        "INSERT INTO ck.pdh3_counter VALUES ('shared',0);"
        "CREATE TABLE ck.pdh3_replay_control "
        "(replay_id STRING PRIMARY KEY);",
        env=env,
    )


def q(value: str) -> str:
    if "\x00" in value:
        raise CampaignError("SQL_LITERAL_INVALID")
    return "'" + value.replace("'", "''") + "'"


def vector_literal() -> str:
    values = ",".join(f"{((index % 17) - 8) / 17:.6f}" for index in range(64))
    return q("[" + values + "]") + "::VECTOR(64)"


def seed_batch_statements(
    campaign_id: str,
    start: int,
    stop: int,
    events_per_task: int,
    receipts_per_task: int,
    vector_stop: int,
) -> list[tuple[str, str]]:
    campaign = q(campaign_id)
    prefix = q(campaign_id + "-task-")
    task_expression = f"{prefix} || lpad(i::STRING,6,'0')"
    event_expression = (
        f"{task_expression} || '-event-' || lpad(s::STRING,2,'0')"
    )
    event_hash = (
        f"decode(sha256(({campaign} || '-event-' || i::STRING || '-' || "
        "s::STRING)::BYTES),'hex')"
    )
    parent_hash = (
        "CASE WHEN s=0 THEN decode('" + ZERO_HASH + "','hex') "
        f"ELSE decode(sha256(({campaign} || '-event-' || i::STRING || '-' || "
        "(s-1)::STRING)::BYTES),'hex') END"
    )
    statements = [
        (
            "tasks",
            "INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash) "
            f"SELECT {task_expression},{campaign},"
            "jsonb_build_object('synthetic',true,'task',i),"
            f"decode(sha256(({campaign} || '-task-hash-' || i::STRING)::BYTES),'hex'),"
            f"decode(sha256(({campaign} || '-state-hash-' || i::STRING)::BYTES),'hex') "
            f"FROM generate_series({start},{stop - 1}) AS g(i)",
        ),
        (
            "events",
            "INSERT INTO ck.trajectory_events"
            "(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash) "
            f"SELECT {event_expression},{task_expression},s,{parent_hash},"
            f"decode(sha256(({campaign} || '-state-hash-' || i::STRING)::BYTES),'hex'),"
            "jsonb_build_object('synthetic',true,'sequence',s),"
            f"{event_hash} FROM generate_series({start},{stop - 1}) AS g(i),"
            f"generate_series(0,{events_per_task - 1}) AS e(s)",
        ),
        (
            "receipts",
            "INSERT INTO ck.receipts"
            "(receipt_hash,task_id,event_hash,status,receipt_json) "
            f"SELECT decode(sha256(({campaign} || '-receipt-' || i::STRING || '-' || "
            f"s::STRING)::BYTES),'hex'),{task_expression},{event_hash},'SEALED',"
            "jsonb_build_object('synthetic',true,'receipt',s) "
            f"FROM generate_series({start},{stop - 1}) AS g(i),"
            f"generate_series(0,{receipts_per_task - 1}) AS e(s)",
        ),
    ]
    limited_stop = min(stop, vector_stop)
    if start < limited_stop:
        statements.append(
            (
                "vectors",
                "INSERT INTO ck.context_vectors"
                "(vector_id,task_id,event_hash,namespace,vector,vector_digest) "
                f"SELECT {task_expression} || '-vector-00',{task_expression},"
                f"decode(sha256(({campaign} || '-event-' || i::STRING || '-0')::BYTES),'hex'),"
                f"{campaign},{vector_literal()},"
                f"decode(sha256(({campaign} || '-vector-constant')::BYTES),'hex') "
                f"FROM generate_series({start},{limited_stop - 1}) AS g(i)",
            )
        )
    return statements


def seed_dataset(
    binary: Path,
    port: int,
    env: dict[str, str],
    journal: ChainLog,
    *,
    campaign_id: str,
    tasks: int,
    events_per_task: int,
    receipts_per_task: int,
    vectors: int,
    batch_tasks: int,
    setup_deadline: float,
) -> dict[str, Any]:
    counts = {"tasks": 0, "events": 0, "receipts": 0, "vectors": 0}
    retries = 0
    statement_hashes: list[str] = []
    for start in range(0, tasks, batch_tasks):
        if time.monotonic() >= setup_deadline:
            raise CampaignError("SETUP_DEADLINE_EXCEEDED")
        stop = min(tasks, start + batch_tasks)
        for stage, statement in seed_batch_statements(
            campaign_id,
            start,
            stop,
            events_per_task,
            receipts_per_task,
            vectors,
        ):
            raw_hash = digest(statement.encode("utf-8"))
            for attempt in range(4):
                try:
                    sql(binary, port, statement, env=env, timeout=900)
                    break
                except CampaignError:
                    if attempt == 3:
                        raise
                    retries += 1
                    time.sleep(0.25 * (attempt + 1))
            rows = stop - start
            if stage == "events":
                rows *= events_per_task
            elif stage == "receipts":
                rows *= receipts_per_task
            elif stage == "vectors":
                rows = max(0, min(stop, vectors) - start)
            counts[stage] += rows
            statement_hashes.append(raw_hash)
        journal.emit(
            "SEED_BATCH",
            {
                "start": start,
                "stop": stop,
                "counts": dict(counts),
                "statement_set_sha256": digest(statement_hashes),
            },
        )
    return {
        "counts": counts,
        "statement_set_sha256": digest(statement_hashes),
        "retries": retries,
    }


def campaign_counts(binary: Path, port: int, env: dict[str, str], campaign: str) -> tuple[int, ...]:
    prefix = campaign + "-task-%"
    return parse_count_tuple(
        sql(
            binary,
            port,
            "SELECT "
            f"(SELECT count(*) FROM ck.tasks WHERE campaign_id={q(campaign)}),"
            f"(SELECT count(*) FROM ck.trajectory_events WHERE task_id LIKE {q(prefix)}),"
            f"(SELECT count(*) FROM ck.receipts WHERE task_id LIKE {q(prefix)}),"
            f"(SELECT count(*) FROM ck.context_vectors WHERE namespace={q(campaign)})",
            env=env,
        ),
        4,
    )


def dependency_matrix(
    binary: Path,
    port: int,
    env: dict[str, str],
    campaign: str,
    epoch: int,
) -> dict[str, Any]:
    task_id = f"{campaign}-task-000000"
    statuses = ("ADVISORY", "TIMEOUT", "THROTTLED", "MALFORMED", "STALE")
    for index, status in enumerate(statuses):
        request_id = f"{campaign}-advice-{epoch:04d}-{index}"
        seed = f"{campaign}:{epoch}:{index}"
        sql(
            binary,
            port,
            "INSERT INTO ck.worker_results"
            "(request_id,task_id,candidate_id,request_hash,response_hash,attempt,"
            "supersedes,status,result_json,result_hash) VALUES ("
            f"{q(request_id)},{q(task_id)},{q('candidate-' + str(index))},"
            f"decode(sha256({q(seed + ':request')}::BYTES),'hex'),"
            f"decode(sha256({q(seed + ':response')}::BYTES),'hex'),1,NULL,{q(status)},"
            f"jsonb_build_object('synthetic',true,'status',{q(status)}),"
            f"decode(sha256({q(seed + ':result')}::BYTES),'hex')) ON CONFLICT DO NOTHING",
            env=env,
        )
    count = parse_last_integer(
        sql(
            binary,
            port,
            f"SELECT count(*) FROM ck.worker_results WHERE request_id LIKE "
            f"{q(campaign + '-advice-' + format(epoch, '04d') + '-%')}",
            env=env,
        )
    )
    if count != len(statuses):
        raise CampaignError("DEPENDENCY_MATRIX_COUNT_MISMATCH")
    return {"statuses": list(statuses), "rows": count}


def cleanup_probe(
    binary: Path,
    port: int,
    env: dict[str, str],
    campaign: str,
    epoch: int,
) -> dict[str, Any]:
    task_id = f"{campaign}-cleanup-{epoch:04d}"
    task_seed = task_id + ":task"
    event_seed = task_id + ":event"
    sql(
        binary,
        port,
        "BEGIN;"
        "INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash)"
        f" VALUES ({q(task_id)},{q(campaign)},'{{\"synthetic\":true}}',"
        f"decode(sha256({q(task_seed)}::BYTES),'hex'),"
        f"decode(sha256({q(task_id + ':state')}::BYTES),'hex'));"
        "INSERT INTO ck.trajectory_events"
        "(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash)"
        f" VALUES ({q(task_id + '-event')},{q(task_id)},0,"
        f"decode('{ZERO_HASH}','hex'),"
        f"decode(sha256({q(task_id + ':state')}::BYTES),'hex'),"
        f"'{{\"synthetic\":true}}',"
        f"decode(sha256({q(event_seed)}::BYTES),'hex'));"
        "COMMIT;"
        f"DELETE FROM ck.trajectory_events WHERE task_id={q(task_id)};"
        f"DELETE FROM ck.tasks WHERE task_id={q(task_id)};",
        env=env,
    )
    residue = parse_last_integer(
        sql(
            binary,
            port,
            f"SELECT count(*) FROM ck.tasks WHERE task_id={q(task_id)}",
            env=env,
        )
    )
    if residue != 0:
        raise CampaignError("CLEANUP_PROBE_RESIDUE")
    return {"task_id_hash": digest(task_id.encode()), "residue": residue}


def process_metrics(nodes: list[Node], root: Path, output: Path) -> dict[str, Any]:
    values = []
    for node in nodes:
        pid = node.process.pid if node.process is not None else None
        rss_kb = None
        descriptors = None
        if pid is not None and Path(f"/proc/{pid}/status").is_file():
            for line in Path(f"/proc/{pid}/status").read_text().splitlines():
                if line.startswith("VmRSS:"):
                    rss_kb = int(line.split()[1])
            descriptors = len(list(Path(f"/proc/{pid}/fd").iterdir()))
        values.append(
            {
                "node": node.index + 1,
                "pid": pid,
                "alive": node.process is not None and node.process.poll() is None,
                "rss_kb": rss_kb,
                "descriptors": descriptors,
            }
        )
    usage = shutil.disk_usage(root)
    return {
        "nodes": values,
        "database_bytes": sum(tree_bytes(node.store) for node in nodes),
        "evidence_bytes": tree_bytes(output),
        "disk_total_bytes": usage.total,
        "disk_used_bytes": usage.used,
        "disk_used_fraction": usage.used / usage.total,
    }


def fault_cycle(
    binary: Path,
    nodes: list[Node],
    node_index: int,
    join: str,
    cache: str,
    sql_memory: str,
    env: dict[str, str],
    campaign: str,
) -> dict[str, Any]:
    target = nodes[node_index]
    surviving = nodes[(node_index + 1) % len(nodes)]
    before = campaign_counts(binary, surviving.sql_port, env, campaign)
    returncode = stop_node(target, crash=True)
    during = campaign_counts(binary, surviving.sql_port, env, campaign)
    start_node(binary, target, join, cache, sql_memory, env, append=True)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            after = campaign_counts(binary, target.sql_port, env, campaign)
            if after == before:
                return {
                    "node": node_index + 1,
                    "signal": "SIGKILL",
                    "returncode": returncode,
                    "before": list(before),
                    "during": list(during),
                    "after": list(after),
                    "green": during == before and after == before,
                }
        except (CampaignError, subprocess.TimeoutExpired):
            time.sleep(1)
    raise CampaignError("FAULT_RESTART_RECONCILIATION_FAILED")


def create_query_files(canary: Any, root: Path, campaign_id: str) -> dict[str, dict[str, Any]]:
    canary.CAMPAIGN_ID = campaign_id
    return canary.build_query_files(root)


def verifier_batch(
    canary: Any,
    root: Path,
    env: dict[str, str],
    campaign_id: str,
) -> dict[str, Any]:
    canary.CAMPAIGN_ID = campaign_id
    result = canary.run_verifier_campaign(root, env)
    if result["measured_executions"] != contract.VERIFIER_BATCH_SIZE:
        raise CampaignError("VERIFIER_BATCH_COUNT_INVALID")
    return result


def result_manifest(output: Path) -> dict[str, Any]:
    files = {
        str(path.relative_to(output)): file_sha256(path)
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }
    body = {
        "version": "ck-pdh3-scale-evidence-manifest-v1",
        "files": files,
        "file_count": len(files),
        "file_set_sha256": digest(files),
    }
    value = {**body, "manifest_sha256": digest(body)}
    atomic_write(output / "manifest.json", canonical(value))
    return value


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if not args.campaign_id.startswith("ck-pdh3-scale-"):
        raise CampaignError("CAMPAIGN_ID_INVALID")
    binary = args.binary.resolve()
    packet = args.packet.resolve()
    output = args.output.resolve()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise CampaignError("COCKROACH_BINARY_INVALID")
    if not packet.is_file():
        raise CampaignError("PACKET_MISSING")
    if output.exists():
        raise CampaignError("OUTPUT_ALREADY_EXISTS")
    output.mkdir(parents=True)
    packet_hash = file_sha256(packet)
    if os.environ.get("PDH3_PACKET_SHA256") != packet_hash:
        raise CampaignError("PACKET_HASH_BINDING_INVALID")
    if args.production:
        contract.validate_production_arguments(vars(args))
    root_parent = Path("/tmp" if sys.platform.startswith("linux") else "/private/tmp")
    root = Path(tempfile.mkdtemp(prefix=args.campaign_id + ".", dir=root_parent))
    fake_home = root / "empty-home"
    fake_home.mkdir()
    env = scrubbed_env(fake_home)
    journal = ChainLog(output / "journal.ndjson", args.campaign_id)
    canary = load_canary_module()
    canary.CANDIDATE = contract.PRODUCT_CANDIDATE
    canary.P99_LIMIT_MS = contract.P99_LIMIT_MS
    canary.PMAX_LIMIT_MS = contract.PMAX_LIMIT_MS
    canary.STAGE_DURATION_SECONDS = args.query_duration_seconds
    nodes: list[Node] = []
    join = ""
    result: dict[str, Any] | None = None
    teardown: dict[str, Any] = {
        "nodes_stopped": False,
        "ports_closed": False,
        "generated_root_removed": False,
        "database_dropped": False,
    }
    try:
        journal.emit(
            "CAMPAIGN_START",
            {
                "production": args.production,
                "packet_sha256": packet_hash,
                "contract_sha256": contract.production_contract()["contract_sha256"],
                "binary_sha256": file_sha256(binary),
                "network": "LOOPBACK_CLUSTER_ONLY",
                "credential_material": False,
            },
        )
        nodes, join = start_cluster(
            binary,
            root,
            env,
            args.cache,
            args.sql_memory,
        )
        gateway = nodes[0].sql_port
        apply_migrations(binary, gateway, env)
        setup_deadline = time.monotonic() + args.setup_timeout_seconds
        seed = seed_dataset(
            binary,
            gateway,
            env,
            journal,
            campaign_id=args.campaign_id,
            tasks=args.tasks,
            events_per_task=args.events_per_task,
            receipts_per_task=args.receipts_per_task,
            vectors=args.vectors,
            batch_tasks=args.seed_batch_tasks,
            setup_deadline=setup_deadline,
        )
        expected_counts = (
            args.tasks,
            args.tasks * args.events_per_task,
            args.tasks * args.receipts_per_task,
            args.vectors,
        )
        if campaign_counts(binary, gateway, env, args.campaign_id) != expected_counts:
            raise CampaignError("SEEDED_COUNTS_MISMATCH")
        wrong_links = parse_last_integer(
            sql(
                binary,
                gateway,
                "SELECT count(*) FROM ck.context_vectors v "
                "JOIN ck.trajectory_events e ON e.event_hash=v.event_hash "
                "WHERE v.task_id != e.task_id",
                env=env,
            )
        )
        if wrong_links:
            raise CampaignError("VECTOR_CROSS_TASK_CONTAMINATION")
        query_files = create_query_files(canary, root, args.campaign_id)
        measured_start_ns = time.monotonic_ns()
        measured_start_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        checkpoints: list[dict[str, Any]] = []
        total_verifier = 0
        total_operations = 0
        max_p99 = 0.0
        max_pmax = 0.0
        fault_count = 0
        required_checkpoints = args.duration_seconds // args.checkpoint_seconds
        for epoch in range(required_checkpoints):
            epoch_start_ns = time.monotonic_ns()
            epoch_root = root / f"epoch-{epoch:04d}"
            epoch_root.mkdir()
            concurrency = min(
                args.max_concurrency,
                contract.CONCURRENCY_STAGES[
                    min(epoch, len(contract.CONCURRENCY_STAGES) - 1)
                ],
            )
            canary.MINIMUM_ACK_WRITE_OPERATIONS = max(2_000, concurrency * 10)
            canary.MINIMUM_CONTENDED_UPDATE_OPERATIONS = max(1_000, concurrency * 5)
            canary.MINIMUM_REPLAY_OPERATIONS = max(1_000, concurrency * 5)
            with ThreadPoolExecutor(max_workers=1) as executor:
                cleanup_future = executor.submit(
                    cleanup_probe,
                    binary,
                    gateway,
                    env,
                    args.campaign_id,
                    epoch,
                )
                stage = canary.run_stage(
                    binary,
                    gateway,
                    query_files,
                    epoch_root,
                    concurrency,
                    env,
                )
                cleanup = cleanup_future.result(timeout=120)
            if not stage["green"]:
                raise CampaignError("CONCURRENCY_STAGE_BLOCKED:" + str(concurrency))
            dependency = dependency_matrix(
                binary, gateway, env, args.campaign_id, epoch
            )
            verifier = None
            if epoch < min(contract.VERIFIER_BATCHES, required_checkpoints):
                verifier = verifier_batch(
                    canary,
                    epoch_root / "verifier",
                    env,
                    f"{args.campaign_id}-v{epoch:04d}",
                )
                total_verifier += verifier["measured_executions"]
            fault = None
            if (epoch + 1) % args.fault_every_checkpoints == 0:
                target = fault_count % 3
                fault = fault_cycle(
                    binary,
                    nodes,
                    target,
                    join,
                    args.cache,
                    args.sql_memory,
                    env,
                    args.campaign_id,
                )
                fault_count += 1
                gateway = nodes[0].sql_port
                if not fault["green"]:
                    raise CampaignError("FAULT_CYCLE_NOT_GREEN")
            counts = campaign_counts(binary, gateway, env, args.campaign_id)
            if counts != expected_counts:
                raise CampaignError("ACKNOWLEDGED_DATASET_DRIFT")
            wrong_links = parse_last_integer(
                sql(
                    binary,
                    gateway,
                    "SELECT count(*) FROM ck.context_vectors v "
                    "JOIN ck.trajectory_events e ON e.event_hash=v.event_hash "
                    "WHERE v.task_id != e.task_id",
                    env=env,
                )
            )
            if wrong_links:
                raise CampaignError("VECTOR_CROSS_TASK_CONTAMINATION")
            resources = process_metrics(nodes, root, output)
            if resources["database_bytes"] > contract.DATABASE_BYTES_LIMIT:
                raise CampaignError("DATABASE_GROWTH_LIMIT")
            if resources["evidence_bytes"] > contract.EVIDENCE_BYTES_LIMIT:
                raise CampaignError("EVIDENCE_GROWTH_LIMIT")
            if resources["disk_used_fraction"] > args.disk_used_fraction_limit:
                raise CampaignError("DISK_USED_FRACTION_LIMIT")
            total_operations += stage["total_operations"]
            max_p99 = max(max_p99, stage["maximum_latency_ms"]["p99"])
            max_pmax = max(max_pmax, stage["maximum_latency_ms"]["max"])
            checkpoint_body = {
                "version": "ck-pdh3-scale-checkpoint-v1",
                "epoch": epoch + 1,
                "concurrency": concurrency,
                "stage": stage,
                "cleanup_probe": cleanup,
                "dependency_matrix": dependency,
                "verifier": verifier,
                "fault": fault,
                "counts": list(counts),
                "wrong_task_vector_links": wrong_links,
                "resources": resources,
                "elapsed_ns": time.monotonic_ns() - measured_start_ns,
            }
            checkpoint = {
                **checkpoint_body,
                "checkpoint_sha256": digest(checkpoint_body),
            }
            atomic_write(
                output / f"checkpoint-{epoch + 1:04d}.json",
                canonical(checkpoint),
            )
            checkpoints.append(
                {
                    "epoch": epoch + 1,
                    "checkpoint_sha256": checkpoint["checkpoint_sha256"],
                }
            )
            journal.emit(
                "CHECKPOINT",
                {
                    "epoch": epoch + 1,
                    "checkpoint_sha256": checkpoint["checkpoint_sha256"],
                    "concurrency": concurrency,
                    "total_operations": total_operations,
                    "total_verifier": total_verifier,
                },
            )
            next_boundary_ns = (
                measured_start_ns + (epoch + 1) * args.checkpoint_seconds * 1_000_000_000
            )
            remaining_ns = next_boundary_ns - time.monotonic_ns()
            if remaining_ns < 0:
                raise CampaignError("CHECKPOINT_INTERVAL_OVERRUN")
            time.sleep(remaining_ns / 1_000_000_000)
            if time.monotonic_ns() - epoch_start_ns > (
                args.checkpoint_seconds * 1_000_000_000 + 2_000_000_000
            ):
                raise CampaignError("CHECKPOINT_SCHEDULE_DRIFT")
        measured_end_ns = time.monotonic_ns()
        measured_seconds = (measured_end_ns - measured_start_ns) / 1_000_000_000
        if args.production and not (args.duration_seconds <= measured_seconds <= args.duration_seconds + 2):
            raise CampaignError("MEASURED_DURATION_INVALID")
        if args.production and total_verifier != contract.VERIFIER_EXECUTIONS:
            raise CampaignError("VERIFIER_EXECUTION_TOTAL_INVALID")
        if max_p99 > contract.P99_LIMIT_MS or max_pmax > contract.PMAX_LIMIT_MS:
            raise CampaignError("LATENCY_THRESHOLD_BREACH")
        final_counts = campaign_counts(binary, gateway, env, args.campaign_id)
        final_wrong_links = parse_last_integer(
            sql(
                binary,
                gateway,
                "SELECT count(*) FROM ck.context_vectors v "
                "JOIN ck.trajectory_events e ON e.event_hash=v.event_hash "
                "WHERE v.task_id != e.task_id",
                env=env,
            )
        )
        result_body = {
            "version": "ck-pdh3-production-scale-result-v1",
            "status": "GREEN",
            "production_mode": args.production,
            "product_candidate": contract.PRODUCT_CANDIDATE,
            "plan_sha256": contract.PLAN_SHA256,
            "packet_sha256": packet_hash,
            "contract_sha256": contract.production_contract()["contract_sha256"],
            "campaign_id": args.campaign_id,
            "synthetic_only": True,
            "credentials_used": False,
            "external_cloud_calls": 0,
            "cluster_topology": "THREE_NODES_ONE_SECURE_RUNPOD_HOST",
            "measured_start_utc": measured_start_utc,
            "measured_end_utc": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            ),
            "measured_seconds": measured_seconds,
            "seed": seed,
            "dataset_counts": list(final_counts),
            "wrong_task_vector_links": final_wrong_links,
            "checkpoints": checkpoints,
            "checkpoint_count": len(checkpoints),
            "total_measured_operations": total_operations,
            "verifier_executions": total_verifier,
            "fault_cycles": fault_count,
            "maximum_p99_ms": max_p99,
            "maximum_latency_ms": max_pmax,
            "journal_terminal_hash_before_result": journal.previous,
            "limitations": [
                "SYNTHETIC_ONLY",
                "SINGLE_RUNPOD_HOST",
                "NOT_MULTI_REGION",
                "NOT_PRODUCTION_TRAFFIC",
                "LAMBDA_FAILURES_ARE_FROZEN_LOCAL_ADVICE_STATES",
                "GPU_NOT_USED_BY_CPU_BOUND_PROTOCOL",
            ],
        }
        required = {
            "checkpoint_count": (
                contract.REQUIRED_CHECKPOINTS if args.production else required_checkpoints
            ),
            "verifier_executions": (
                contract.VERIFIER_EXECUTIONS if args.production else total_verifier
            ),
        }
        result_body["green_checks"] = {
            "checkpoint_count": len(checkpoints) == required["checkpoint_count"],
            "verifier_execution_count": total_verifier == required["verifier_executions"],
            "dataset_counts": final_counts == expected_counts,
            "cross_task_vector_links": final_wrong_links == 0,
            "false_promotions": all(
                (
                    json.loads(
                        (output / f"checkpoint-{index:04d}.json").read_bytes()
                    ).get("verifier") or {}
                ).get("false_promotions", 0)
                == 0
                for index in range(1, len(checkpoints) + 1)
            ),
            "latency": (
                max_p99 <= contract.P99_LIMIT_MS
                and max_pmax <= contract.PMAX_LIMIT_MS
            ),
            "fault_cycles": fault_count >= (required_checkpoints // args.fault_every_checkpoints),
        }
        if not all(result_body["green_checks"].values()):
            raise CampaignError("FINAL_GREEN_CHECK_FAILED")
        result = {**result_body, "result_sha256": digest(result_body)}
        atomic_write(output / "result.json", canonical(result))
        journal.emit("MEASURED_CAMPAIGN_GREEN", {"result_sha256": result["result_sha256"]})
        sql(
            binary,
            gateway,
            "DROP DATABASE cockroach_kernel CASCADE",
            env=env,
            database=None,
            timeout=1800,
        )
        remaining = parse_last_integer(
            sql(
                binary,
                gateway,
                "SELECT count(*) FROM [SHOW DATABASES] "
                "WHERE database_name='cockroach_kernel'",
                env=env,
                database=None,
            )
        )
        if remaining != 0:
            raise CampaignError("DATABASE_DROP_RESIDUE")
        teardown["database_dropped"] = True
        return result
    except BaseException as exc:
        failure_body = {
            "version": "ck-pdh3-scale-failure-v1",
            "campaign_id": args.campaign_id,
            "exception_type": type(exc).__name__,
            "reason": str(exc),
            "journal_prior_hash": journal.previous,
        }
        atomic_write(
            output / "failure.json",
            canonical({**failure_body, "failure_sha256": digest(failure_body)}),
        )
        journal.emit(
            "CAMPAIGN_BLOCKED",
            {"type": type(exc).__name__, "reason": str(exc)},
        )
        raise
    finally:
        for node in nodes:
            stop_node(node, crash=False)
        teardown["nodes_stopped"] = all(
            node.process is None for node in nodes
        )
        open_ports = []
        for node in nodes:
            for port in (node.sql_port, node.http_port):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                    probe.settimeout(0.2)
                    if probe.connect_ex(("127.0.0.1", port)) == 0:
                        open_ports.append(port)
        teardown["ports_closed"] = not open_ports
        verified = root.resolve()
        if verified.parent not in (Path("/tmp"), Path("/private/tmp")):
            raise CampaignError("GENERATED_ROOT_PARENT_INVALID")
        if not verified.name.startswith(args.campaign_id + "."):
            raise CampaignError("GENERATED_ROOT_IDENTITY_INVALID")
        shutil.rmtree(verified)
        teardown["generated_root_removed"] = not verified.exists()
        teardown_body = {
            "version": "ck-pdh3-scale-teardown-v1",
            "campaign_id": args.campaign_id,
            **teardown,
            "open_ports": open_ports,
        }
        atomic_write(
            output / "teardown.json",
            canonical({**teardown_body, "receipt_sha256": digest(teardown_body)}),
        )
        journal.emit("LOCAL_TEARDOWN", teardown)
        result_manifest(output)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--binary", type=Path, required=True)
    value.add_argument("--packet", type=Path, required=True)
    value.add_argument("--output", type=Path, required=True)
    value.add_argument("--campaign-id", required=True)
    value.add_argument("--production", action="store_true")
    value.add_argument("--duration-seconds", type=int, default=60)
    value.add_argument("--checkpoint-seconds", type=int, default=60)
    value.add_argument("--tasks", type=int, default=100)
    value.add_argument("--events-per-task", type=int, default=3)
    value.add_argument("--receipts-per-task", type=int, default=1)
    value.add_argument("--vectors", type=int, default=50)
    value.add_argument("--max-concurrency", type=int, default=10)
    value.add_argument("--query-duration-seconds", type=int, default=2)
    value.add_argument("--seed-batch-tasks", type=int, default=100)
    value.add_argument("--setup-timeout-seconds", type=int, default=600)
    value.add_argument("--fault-every-checkpoints", type=int, default=1)
    value.add_argument("--disk-used-fraction-limit", type=float, default=0.999)
    value.add_argument("--cache", default="128MiB")
    value.add_argument("--sql-memory", default="128MiB")
    return value


def main() -> int:
    args = parser().parse_args()
    if args.duration_seconds < 1 or args.checkpoint_seconds < 1:
        raise CampaignError("DURATION_INVALID")
    if args.duration_seconds % args.checkpoint_seconds:
        raise CampaignError("CHECKPOINT_DIVISIBILITY_INVALID")
    if not 0.1 <= args.disk_used_fraction_limit <= 0.999:
        raise CampaignError("DISK_FRACTION_LIMIT_INVALID")
    if not 1 <= args.receipts_per_task <= args.events_per_task:
        raise CampaignError("RECEIPT_COUNT_INVALID")
    execute(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```
### `post-dogfood/build_pdh3_scale_bundle.py`

```python
#!/usr/bin/env python3
"""Build a deterministic credential-free PDH-3 RunPod transfer bundle."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import tarfile
from typing import Any


BASE = Path(__file__).resolve().parents[1]
FILES = (
    "post-dogfood/pdh3_scale_contract.py",
    "post-dogfood/run_pdh3_scale_campaign.py",
    "post-dogfood/run_pdh3_local_canary.py",
    "hardening-gate7/make_vectors.py",
    "hardening-gate7/run_campaign.py",
    "hardening-gate7/run_trial.py",
    "hardening-gate5/heldout_contract.py",
    "p4-verifier/verifier.py",
    "p7-recovery/records.py",
    "p9-cloud/migrations/001_cloud.sql",
    "p9-cloud/migrations/003_collision_safe_vector_digest.sql",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/cockroach",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/LICENSE",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/THIRD-PARTY-NOTICES.txt",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/lib/libgeos.so",
    "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
    "cockroach-v26.2.3.linux-amd64/lib/libgeos_c.so",
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate_relative(name: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\x00" in name:
        raise ValueError("BUNDLE_PATH_UNSAFE")


def build(output: Path, manifest_path: Path) -> dict[str, Any]:
    if output.exists() or manifest_path.exists():
        raise ValueError("OUTPUT_EXISTS")
    entries: list[dict[str, Any]] = []
    for relative in FILES:
        validate_relative(relative)
        path = BASE / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError("SOURCE_INVALID:" + relative)
        raw = path.read_bytes()
        entries.append(
            {
                "path": relative,
                "bytes": len(raw),
                "sha256": digest(raw),
                "mode": 0o755 if os.access(path, os.X_OK) else 0o644,
            }
        )
    manifest_body = {
        "version": "ck-pdh3-scale-bundle-manifest-v1",
        "credential_free": True,
        "synthetic_only": True,
        "files": entries,
        "file_count": len(entries),
        "source_set_sha256": digest(canonical(entries)),
    }
    manifest = {
        **manifest_body,
        "manifest_sha256": digest(canonical(manifest_body)),
    }
    manifest_raw = canonical(manifest)
    stream = io.BytesIO()
    with gzip.GzipFile(fileobj=stream, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w") as archive:
            for row in entries:
                raw = (BASE / row["path"]).read_bytes()
                info = tarfile.TarInfo(row["path"])
                info.size = len(raw)
                info.mode = row["mode"]
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                archive.addfile(info, io.BytesIO(raw))
            info = tarfile.TarInfo("PDH3_BUNDLE_MANIFEST.json")
            info.size = len(manifest_raw)
            info.mode = 0o644
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            archive.addfile(info, io.BytesIO(manifest_raw))
    archive_raw = stream.getvalue()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(archive_raw)
    receipt_body = {
        "version": "ck-pdh3-scale-bundle-receipt-v1",
        "archive": output.name,
        "archive_bytes": len(archive_raw),
        "archive_sha256": digest(archive_raw),
        "manifest": manifest,
    }
    receipt = {
        **receipt_body,
        "receipt_sha256": digest(canonical(receipt_body)),
    }
    manifest_path.write_bytes(canonical(receipt))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    arguments = parser.parse_args()
    print(
        canonical(build(arguments.output.resolve(), arguments.receipt.resolve())).decode()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```
### `s2-soak/lifecycle_guard.py`

```python
#!/usr/bin/env python3
"""Detached local exact-ID RunPod lifecycle guard.

This process runs on the operator host only. It receives one exact Pod ID,
expected name/campaign prefix, a hash-pinned runpodctl path, and absolute stop
and delete deadlines. It never enters the Pod and never transfers credentials.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


class GuardFailure(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, check=False)


class ChainLog:
    def __init__(self, path: Path) -> None:
        if path.exists():
            raise GuardFailure("LOG_ALREADY_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.previous = "0" * 64
        self.sequence = 0

    def emit(self, event: str, details: Any) -> dict[str, Any]:
        self.sequence += 1
        core = {"schema_version": "s2-guard-v1", "sequence": self.sequence,
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "monotonic_seconds": round(time.monotonic(), 3),
                "previous_hash": self.previous, "event": event,
                "details": details}
        record = {**core, "event_hash": hashlib.sha256(canonical(core)).hexdigest()}
        with self.path.open("ab") as handle:
            handle.write(canonical(record) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous = record["event_hash"]
        return record


def parse_json(result: subprocess.CompletedProcess[str]) -> Any:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise GuardFailure("MALFORMED_PROVIDER_JSON") from exc


def pod_get(cli: Path, pod_id: str) -> tuple[bool, dict[str, Any] | None, str]:
    result = run([str(cli), "pod", "get", pod_id, "--output", "json"])
    if result.returncode != 0:
        lowered = result.stdout.lower()
        if "404" in lowered or "not found" in lowered or "does not exist" in lowered:
            return False, None, result.stdout.strip()
        raise GuardFailure("POD_GET_FAILED:" + result.stdout[-500:])
    value = parse_json(result)
    if not isinstance(value, dict):
        raise GuardFailure("MALFORMED_POD_GET")
    return True, value, result.stdout.strip()


def campaign_active(cli: Path, campaign_prefix: str) -> list[dict[str, Any]]:
    result = run([str(cli), "pod", "list", "--all", "--output", "json"])
    if result.returncode != 0:
        raise GuardFailure("POD_LIST_FAILED:" + result.stdout[-500:])
    value = parse_json(result)
    if not isinstance(value, list):
        raise GuardFailure("MALFORMED_POD_LIST")
    return [item for item in value if isinstance(item, dict)
            and str(item.get("name", "")).startswith(campaign_prefix)
            and str(item.get("desiredStatus", "")).upper() not in
            {"EXITED", "TERMINATED", "DELETED"}]


def verify_identity(value: dict[str, Any], pod_id: str, expected_name: str,
                    campaign_prefix: str) -> None:
    if value.get("id") != pod_id:
        raise GuardFailure("POD_ID_MISMATCH")
    if value.get("name") != expected_name:
        raise GuardFailure("POD_NAME_MISMATCH")
    if not expected_name.startswith(campaign_prefix):
        raise GuardFailure("CAMPAIGN_MISMATCH")


def bounded_action(cli: Path, action: str, pod_id: str,
                   log: ChainLog) -> None:
    delays = (0, 2, 5)
    for attempt, delay in enumerate(delays, 1):
        if delay:
            time.sleep(delay)
        result = run([str(cli), "pod", action, pod_id, "--output", "json"])
        log.emit(action.upper() + "_ATTEMPT",
                 {"attempt": attempt, "exit": result.returncode,
                  "output_hash": hashlib.sha256(result.stdout.encode()).hexdigest()})
        if result.returncode == 0:
            return
        lowered = result.stdout.lower()
        if action == "delete" and ("404" in lowered or "not found" in lowered):
            return
    raise GuardFailure(action.upper() + "_RETRIES_EXHAUSTED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runpodctl", type=Path, required=True)
    parser.add_argument("--runpodctl-sha256", required=True)
    parser.add_argument("--pod-id", required=True)
    parser.add_argument("--pod-name", required=True)
    parser.add_argument("--campaign-prefix", required=True)
    parser.add_argument("--stop-epoch", type=int, required=True)
    parser.add_argument("--delete-epoch", type=int, required=True)
    parser.add_argument("--heartbeat-seconds", type=int, default=30)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    if args.heartbeat_seconds < 1 or args.delete_epoch <= args.stop_epoch:
        raise GuardFailure("INVALID_DEADLINE")
    cli = args.runpodctl.resolve()
    if not cli.is_file() or not os.access(cli, os.X_OK):
        raise GuardFailure("CLI_NOT_EXECUTABLE")
    log = ChainLog(args.log.resolve())
    stopped = False
    try:
        if sha256_file(cli) != args.runpodctl_sha256:
            raise GuardFailure("CLI_HASH_MISMATCH")
        present, value, _ = pod_get(cli, args.pod_id)
        if not present or value is None:
            raise GuardFailure("POD_ABSENT_AT_BIND")
        verify_identity(value, args.pod_id, args.pod_name, args.campaign_prefix)
        log.emit("BOUND", {"pod_id": args.pod_id, "name": args.pod_name,
                           "campaign_prefix": args.campaign_prefix,
                           "cli_sha256": args.runpodctl_sha256,
                           "stop_epoch": args.stop_epoch,
                           "delete_epoch": args.delete_epoch})
        while True:
            if sha256_file(cli) != args.runpodctl_sha256:
                raise GuardFailure("CLI_HASH_MISMATCH")
            present, value, raw = pod_get(cli, args.pod_id)
            if not present:
                active = campaign_active(cli, args.campaign_prefix)
                if active:
                    raise GuardFailure("EXACT_ID_ABSENT_CAMPAIGN_ACTIVE")
                log.emit("TEARDOWN_GREEN", {"exact_id_absent": True,
                                             "campaign_active": []})
                return 0
            assert value is not None
            verify_identity(value, args.pod_id, args.pod_name, args.campaign_prefix)
            now = int(time.time())
            log.emit("HEARTBEAT", {"pod_id": args.pod_id,
                                   "provider_state": value.get("desiredStatus"),
                                   "provider_record_hash": hashlib.sha256(raw.encode()).hexdigest(),
                                   "seconds_to_stop": args.stop_epoch - now,
                                   "seconds_to_delete": args.delete_epoch - now})
            if now >= args.delete_epoch:
                bounded_action(cli, "delete", args.pod_id, log)
            elif now >= args.stop_epoch and not stopped:
                bounded_action(cli, "stop", args.pod_id, log)
                stopped = True
            time.sleep(args.heartbeat_seconds)
    except Exception as exc:
        log.emit("GUARD_BLOCKED", {"type": type(exc).__name__, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

```

## Expected evidence gap

The paid worker, 24-hour result, provider-returned rate/shape, retrieved remote
evidence, teardown, and final audit do not yet exist. That is expected at
preflight. They remain mandatory for the final gate and must not be inferred.
