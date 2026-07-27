# S3 Release-Soak Contract R1

- `STATE`: `PREFLIGHT_FROZEN_NOT_GREEN`
- `PARENT_GATE`: `CK_P9_INTEGRATION_GREEN`
- `PARENT_COMMIT`: `fc296743dd97699a78a4777c8affcd47930f92e6`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `THRESHOLDS_SHA256`: `14c4768ad450d34e5e44a5b8e5f5a602ef2b92fb5d0228b336f79b9d7e4bb006`
- `RESOURCE_ALLOWLIST_SHA256`: `a1993801ce17c4f4a5894720fcfab5cd96715f3f9b0ce03b3919430ea837e3aa`
- `UTC_FROZEN`: `2026-07-26T23:12:11Z`

## Architecture

The disposable RunPod worker is credential-free. It generates only canonical
synthetic `RUN_PROMOTE` and `RUN_REFUSE` requests, runs deterministic local
verification and adversarial/recovery checks, measures resources, and consumes
canonical result receipts. It contains no AWS or CockroachDB client.

The detached host coordinator holds the existing short-lived authenticated
sessions and maps the two operation enums to one frozen P9 implementation path.
Worker fields cannot select SQL, shell, URL, ARN, path, command, destination,
or credentials. Requests and results are strictly field-checked, size-bounded,
sequence-bound, parent-hash-bound, and call-ceiling-bound.

## Frozen workload

- production duration: exactly `43,200` seconds;
- checkpoints: exactly `144` at 300 seconds;
- safety replays: exactly `48` at 900 seconds;
- hourly summaries and cloud exchanges: exactly `12` at 3,600 seconds;
- local CockroachDB: loopback-only Linux runtime;
- production attempts: exactly one;
- coordinator timeout: 300 seconds per exchange;
- worker cloud credentials and cloud clients: zero.

`S3_THRESHOLDS_R1.json` is frozen before production and controls all latency,
growth, retry, correctness, invocation, and cost gates. Thresholds may not be
relaxed after S3 results exist.

## RunPod envelope

- accepted CPU shapes: exactly `2 vCPU / 4 GiB RAM` at no more than
  `$0.06/hour` compute, or exactly `2 vCPU / 8 GiB RAM` at no more than
  `$0.08/hour` compute;
- current smallest sufficient accepted shape: exactly `2 vCPU / 4 GiB RAM`;
- 20 GiB disposable container disk expected price: `$0.004/hour`;
- maximum active rate: `$0.10/hour`;
- maximum successful paid lifetime: 14 hours;
- expected maximum successful-worker exposure: `$1.176`;
- maximum aggregate exposure: `$3.00`;
- image: `runpod/base:1.0.2-ubuntu2204`;
- official template: `runpod-ubuntu-2204` / `Runpod Ubuntu 22.04`;
- image index digest: `sha256:ffe1c3b1ec997f7eaaef8561c2a701792c79ece19754d528222a14ee25d24cb0`;
- linux/amd64 manifest digest: `sha256:27b844c0606ec6e5550fa90bc6647c4b41cf4ee53a44781bd3dbff8ca1beb297`;
- GPU, persistent/network volume, retained IP, and snapshot: zero;
- attempts: at most eight sequential pre-start attempts in 90 minutes;
- simultaneous workers: at most one;
- provider-native `--stop-after` and `--terminate-after`: mandatory;
- detached exact-ID lifecycle guard and separate coordinator guard: mandatory.

Current authenticated UI and CLI inventory were checked at
`2026-07-26T23:06:51Z`. S3-scoped inventory was empty. The UI showed the
2-vCPU/8-GiB CPU class at `$0.08/hour`, and attempt A01 later returned the
outer-authorization-compatible 2-vCPU/4-GiB CPU class at `$0.06/hour`.
The completed six-hour S2 production run measured peak RSS of `836284416`
bytes, below both the S3 frozen RSS ceiling of `1610612736` bytes and 4 GiB of
worker RAM. Both explicitly authorized shapes are therefore sufficient without
relaxing a workload threshold. The provider does not expose image digest
readback on Pod creation; the creation request, current registry digest, and
post-start runtime image evidence must therefore all be preserved.

## Retry and kill law

Only pre-production infrastructure failures listed in the authorization prompt
are retryable. Every attempt is torn down and proved absent before another is
created. No replacement is allowed after upload plus production start.

Kill immediately on credential/private-data exposure, worker auth material,
unknown price, packet or hash drift, undeclared egress, wrong worker/image/
shape/volume/GPU/deadline, nondeterminism, false acceptance, missing evidence,
threshold breach, guard failure, unproved teardown, or a non-GREEN judge.

No RunPod worker may be created until GLM and exact Claude Opus 4.8 both return
GREEN over one byte-identical sanitized preflight packet hash.
