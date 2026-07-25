# Cockroach Kernel S1 Retry-Envelope Packet R3

- `GATE`: `CK_S1_RETRY_PREFLIGHT_PENDING_JUDGE`
- `LAST_GREEN_GATE`: `CK_P4_VERIFIER_GREEN`
- `CURRENT_COMMIT`: `974a7a785cb10af6ea8d2b481ddc2a77751099f1`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `PREVIOUS_S1_PACKET_SHA256`: `8aa3a3b7da4371ffec5569466f230c8052c7eb9bfe2593678728df3abe91149a`
- `P4_PACKET_SHA256`: `0bc2c11084a144bfafde92dae29561ed5810c7b969690e77aa9137c9855b6c43`
- `CAMPAIGN_ID`: `CK-S1-20260725-FOUNDATION-R3`
- `FROZEN_UTC`: `2026-07-25T21:37:17Z`

## Operator authorization

Kenneth explicitly authorized a bounded S1 RunPod retry envelope without
routine confirmation. This supersedes only the prior second-worker/no-third-
worker attempt restriction. It does not waive price, security, evidence,
judge, billing, teardown, or the stop-after-S1 boundary.

The envelope permits at most eight creation attempts during a 45-minute window
beginning with the first create call, one extant S1 worker at a time, one
successful workload worker, and at most $0.30 aggregate charge. Every failed
worker must be deleted and absence-verified before another attempt. No
replacement is allowed after payload upload or workload execution begins.

## Prior lifecycle and billing

Prior Pod `48bqdill8w3vt0` was deleted without upload or workload execution.
Name-scoped running and all-status inventories are `[]`; Pod get returns
provider 404. The bounded Pod billing query still returns `[]`, so the exact
prior charge remains delayed and is not fabricated. This uncertainty is far
below the $0.30 envelope based on the recorded roughly 14-second lifecycle,
but exact aggregate billing remains mandatory for final GREEN.

## Measured workload

- CUDA dependency: none;
- P3 unit tests: 5 passed;
- P4 unit tests: 6 passed;
- direct S1 driver resource profile: approximately 690,241,536 bytes maximum
  RSS on macOS, below 4 GB;
- direct short profile exercised the S1 process but is not duration or gate
  evidence because its deliberately short duration cannot meet the production
  checkpoint schedule;
- P3 integration convenience harness currently selects the packaged Linux
  binary before the macOS binary and fails locally with `Exec format error`;
  this is recorded as a non-S1 harness defect and is not concealed or used as
  S1 evidence;
- workload driver and remote Linux runtime are unchanged from the previously
  reviewed S1 contract.

Both authorized worker shapes exceed measured S1 memory demand:

| Shape | Maximum compute | Console evidence |
|---|---:|---|
| 2 vCPU / 4 GB | $0.06/hour | previously returned by provider |
| 2 vCPU / 8 GB | $0.08/hour | authenticated console current quote |

Authenticated console storage is $0.0002/GB-hour. A 20 GB container adds
$0.004/hour. Maximum active rate is therefore $0.084/hour, under the authorized
$0.085/hour ceiling.

## Immutable runtime and payload

- RunPodCTL: `/tmp/runpodctl-v2.7.2-darwin-arm64`;
- RunPodCTL version: `2.7.2-309512b`;
- RunPodCTL SHA-256:
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`;
- official template: `runpod-ubuntu-2204`;
- exact image: `runpod/base:1.0.2-ubuntu2204`;
- transfer archive: `/tmp/ck-s1-20260725-foundation-r3.tar.gz`;
- transfer archive bytes: `144438442`;
- transfer SHA-256:
  `a81a51ba39b5bb66553b388187219c8a16d5eea4a02b693d9b032c71cd519dbe`;
- Linux CockroachDB archive SHA-256:
  `3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`;
- Linux CockroachDB binary SHA-256:
  `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`;
- soak driver SHA-256:
  `cdd8ad61610895fd3b3a86ab3fe03e516bb976c833eb6539c03fe82b418fa628`;
- migration SHA-256:
  `f28a8ffa1ed3163b3d31f319b1c1351dd057070235a7cc2c15bbdc27ec9491ac`;
- payload contents: Git-tracked `s1-soak`, `p3-ledger`, and `p4-verifier`
  files plus only the checksum-verified Linux runtime archive;
- private-path scan: no findings;
- gitleaks report SHA-256:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`,
  no leaks;
- detect-secrets report SHA-256:
  `8f0ca0520169e4402e604f74bd32368daf71e93c976aa96c929835fe27a89f39`,
  zero files with findings.

## Lifecycle bounds

- first-create deadline: `2026-07-25T22:05:00Z`;
- 45-minute retry window hard end: `2026-07-25T22:50:00Z`;
- successful workload-start deadline: `2026-07-25T22:55:00Z`;
- workload duration: at most 3,600 seconds;
- checkpoint interval: 60 seconds;
- required canonical checkpoints: at least 61;
- provider auto-stop: `2026-07-26T00:05:00Z`;
- provider auto-terminate: `2026-07-26T00:10:00Z`;
- maximum compute rate: $0.08/hour;
- maximum active rate: $0.085/hour;
- maximum aggregate campaign charge: $0.30;
- container disk: at most 20 GB;
- persistent/network volume: 0 GB / none;
- GPU count: zero;
- synthetic input only.

Attempt names are immutable:
`ck-s1-20260725-r3-a01` through `ck-s1-20260725-r3-a08`.

Create-command family, with the attempt name substituted exactly:

```text
/tmp/runpodctl-v2.7.2-darwin-arm64 pod create --compute-type cpu --template-id runpod-ubuntu-2204 --container-disk-in-gb 20 --volume-in-gb 0 --name <attempt-name> --stop-after 2026-07-26T00:05:00Z --terminate-after 2026-07-26T00:10:00Z --output json
```

## Verification and retry law

Before upload, accept only CPU, exactly 2 vCPU, exactly 4 or 8 GB RAM, the
corresponding compute ceiling, at most $0.085/hour total, exact image, at most
20 GB container disk, zero volume, zero GPUs, exact name, and frozen deadlines.

Retry only transient creation/capacity failure, pre-upload worker mismatch, or
pre-upload readiness/SSH failure. For each retry: write a receipt, delete any
worker, prove scoped absence, query billing, confirm cost headroom, and use the
frozen 15/30/60/120/180-second bounded backoff. Stop on the eighth attempt or
the 45-minute hard end.

Never retry a secret/private-data exposure, undeclared egress, hash mismatch,
price or aggregate-cost breach, teardown uncertainty, judge failure, policy
conflict, billing/account challenge, evidence-contract defect, or forbidden
HOME/Qdrant/StateV2/launchd/client/unrelated-project access.

## Workload and evidence contract

After one worker passes verification, retries end permanently. Upload only the
frozen archive, verify its hash, extract, verify the runtime archive and binary,
then run:

```text
python3 s1-soak/run_soak.py --cockroach-bin runtime/cockroach-v26.2.3.linux-amd64/cockroach --output-root /workspace/ck-s1-r3-output --duration-seconds 3600 --checkpoint-seconds 60 --database-growth-limit-bytes 268435456 --evidence-growth-limit-bytes 67108864
```

Every checkpoint must prove SQLSTATE 40001 retry handling, duplicate-receipt
idempotency, restart recovery, five-repeat deterministic verdicts, real
quarantine exclusion, rollback, separate byte classes, and process/resource
state. Runtime residue must be empty. Missing checkpoints, false acceptance,
nondeterminism, failed recovery/rollback, growth breach, hash mismatch, or
process leak stops the run.

## Closeout and kill line

Retrieve and hash-verify all evidence; stop and delete the worker; prove
Pod-scoped and campaign-scoped absence; prove no local SSH/transfer/watchdog or
remote paid process remains; reconcile every attempt's exact charge; scan
residue and secrets; freeze a final packet; obtain a fresh independent GLM
verdict. Exact billing and final independent GREEN are mandatory for S1 GREEN.

Kill line: any policy, price, image, hash, data-boundary, checkpoint,
determinism, quarantine, retry, recovery, rollback, growth, process, cost,
judge, or teardown contradiction blocks S1 and ends the campaign. Do not
continue to P5.
