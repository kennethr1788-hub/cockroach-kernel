# Cockroach Kernel S1 Frozen Lifecycle Packet

- `GATE`: `CK_S1_PREFLIGHT_PENDING_JUDGE`
- `LAST_GREEN_GATE`: `CK_P4_VERIFIER_GREEN`
- `CURRENT_COMMIT`: `03fb60a`
- `P4_PACKET_SHA256`: `0bc2c11084a144bfafde92dae29561ed5810c7b969690e77aa9137c9855b6c43`
- `RUNPODCTL_VERSION`: `2.7.2-309512b`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- `CAMPAIGN_ID`: `CK-S1-20260725-FOUNDATION`
- `FROZEN_UTC`: `2026-07-25T21:16:30Z`

## Measured workload and selected capacity

The local P4 unit suite plus P3 integration harness completed without CUDA in
approximately 24 seconds with approximately 543 MB maximum RSS. CUDA is not
required. The mechanically selected class is the smallest visible CPU worker:
2 vCPU and 8 GB RAM.

Authenticated RunPod console inventory observed at `2026-07-25T21:05Z`:

| CPU class | RAM | Quote |
|---|---:|---:|
| 2 vCPU | 8 GB | $0.08/hour |
| 4 vCPU | 16 GB | $0.16/hour |
| 8 vCPU | 32 GB | $0.32/hour |
| 16 vCPU | 64 GB | $0.64/hour |
| 32 vCPU | 128 GB | $1.28/hour |

The console separately quotes container storage at $0.0002/GB-hour. The frozen
20 GB container therefore costs $0.004/hour and the maximum active rate is
$0.084/hour. No persistent or network volume is attached.

## Frozen runtime and payload

- compute: RunPod Secure Cloud CPU, 2 vCPU / 8 GB;
- official template: `runpod-ubuntu-2204`;
- image reported by the official template: `runpod/base:1.0.2-ubuntu2204`;
- container disk: 20 GB;
- persistent/network volume: 0 GB / none;
- public application ports: none;
- SSH: provider access channel only for bounded upload, polling, and retrieval;
- transfer archive: `/tmp/ck-s1-20260725-foundation.tar.gz`;
- transfer archive bytes: `144439419`;
- transfer SHA-256: `ad77ef05e8ad121302fbcdbfa8f95ea4c227ad894285826f80dae6f2c3c069e4`;
- Linux CockroachDB archive SHA-256: `3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`;
- Linux CockroachDB binary SHA-256: `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`;
- soak driver SHA-256: `cdd8ad61610895fd3b3a86ab3fe03e516bb976c833eb6539c03fe82b418fa628`;
- payload: synthetic code, tests, migration, and checksum-verified runtime only;
- secret scans: `rg`, `gitleaks`, and `detect-secrets`, no findings.

## Frozen lifecycle

- launch deadline: `2026-07-25T21:30:00Z`;
- workload-start deadline: `2026-07-25T21:40:00Z`;
- workload duration: at most 3,600 seconds;
- checkpoint interval: 60 seconds;
- expected canonical checkpoints: 61;
- provider auto-stop: `2026-07-25T22:43:00Z`;
- provider auto-terminate: `2026-07-25T22:48:00Z`;
- maximum lifecycle estimate: $0.13;
- owner: Kenneth, executed by the authorized Codex S1 task;
- kill line: any policy, price, image, hash, checkpoint, determinism,
  quarantine, recovery, rollback, disk, evidence, process, data, or teardown
  contradiction terminates the workload and deletes the worker.

Frozen create command:

```text
/tmp/runpodctl-v2.7.2-darwin-arm64 pod create --compute-type cpu --template-id runpod-ubuntu-2204 --container-disk-in-gb 20 --volume-in-gb 0 --name ck-s1-20260725-foundation --stop-after 2026-07-25T22:43:00Z --terminate-after 2026-07-25T22:48:00Z --output json
```

Cleanup commands are `pod stop <pod-id>`, `pod delete <pod-id>`, followed by
`pod list --all --output json` and a pod-scoped billing query. No force,
second-worker, restart, volume, billing-setting, or deadline extension is
permitted.

## Workload and evidence contract

`s1-soak/run_soak.py` uses one loopback CockroachDB process and synthetic data.
Every checkpoint exercises an injected SQLSTATE 40001 retry, duplicate receipt
idempotency, rollback, database stop/start recovery, five-repeat deterministic
ledger and verifier verdicts, and real quarantine exclusion. It atomically
writes and fsyncs separate manifest, telemetry, and receipt records.

Each receipt records UTC, checkpoint, iteration, workload-state hash,
telemetry hash, evidence hash, retry count, duplicate result, restart result,
deterministic result, quarantine result, rollback result, residue result, and
process/resource status. Workload, telemetry, receipts, manifest, and database
bytes are separate.

Frozen thresholds:

- database growth: at most 268,435,456 bytes;
- evidence growth: at most 67,108,864 bytes;
- workload duration: at most 3,600 seconds;
- required checkpoints: at least 61;
- runtime residue after closeout: none;
- private paths, secrets, credentials, production data, HOME/Qdrant/StateV2,
  undeclared egress, or non-synthetic input: zero.

## Preflight evidence and remaining gate

The driver compiles, the P3 and P4 unit suites pass, and a short local exercise
completed the semantic checkpoint and removed its runtime store. The short
exercise was not treated as S1 duration evidence. No RunPod worker exists and
spend remains $0 at packet freeze.

The lifecycle remains blocked until one independent GLM judge returns GREEN on
this exact packet hash. A preflight judge cannot approve the later S1 result;
the completed evidence requires a separate final independent review.
