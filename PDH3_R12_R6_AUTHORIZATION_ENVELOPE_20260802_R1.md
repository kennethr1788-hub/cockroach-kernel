# PDH-3 R12 R6 Authorization Envelope R1

Status: `PREPARED__HUMAN_AUTHORIZATION_REQUIRED__NO_WORKER_CREATED`

Prepared UTC: `2026-08-02T07:30:48Z`

Current branch: `evidence/external-validity-r1`

Current checkpoint commit:
`9e4f9423c224dfa59c8937bce45a11676ca0d2ae`

Repair implementation commit:
`97fca76bdb246c02ee4e14d1a4f846d4114071e5`

Platform amendment SHA-256:
`6a873f05fcc285fd7229fed8211deca87ac2e39c1a85deced49427fda9251e47`

Independent platform-amendment verdict: `GLM_5_2_GREEN`

Repaired bundle SHA-256:
`69b5923882c459baf93b4a0baec458648adfc56671528dbf2c2623eceff9faaf`

## 1. Requested paid-preflight authority

This envelope requests authority for one repaired R6 paid preflight with no
more than three sequential Secure Cloud L40S creation attempts. It does not
authorize simultaneous workers, a replacement after the main bundle is
uploaded, or a measured 24-hour clock.

Before the first creation request, Icarus must freeze an exact execution packet
containing the current provider inventory and rate, the exact absolute
provider-native stop/terminate deadlines, the immutable campaign/attempt IDs,
the complete attempt ledger, and the deterministic cost bound. Direct GLM 5.2
must return GREEN over that exact packet hash. Any packet change invalidates
the verdict.

## 2. Creation-retry envelope

- maximum creation attempts: `3`;
- maximum simultaneously existing paid workers: `1`;
- maximum successfully running preflight workers: `1`;
- maximum wall-clock creation window: `45 minutes` from attempt 1;
- worker: Secure Cloud `NVIDIA L40S`, one unused GPU;
- image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- rate ceiling: `$0.99/hour` compute;
- container disk: exactly `250 GB`;
- persistent/network volume: `0 GB`;
- maximum successful preflight paid lifetime: `10 hours`;
- aggregate R6 preflight cost ceiling across all attempts: `$12.00`;
- synthetic, sanitized payload only;
- no account/billing-setting changes;
- no other provider or worker class;
- no second worker until exact-ID absence and empty active inventory are
  proven for the prior failed attempt.

A pre-upload retry is allowed only for:

- provider capacity/create failure with no live worker;
- a returned allocation failing the frozen resource envelope;
- image, disk, volume, GPU, cloud, name, or rate mismatch;
- SSH readiness failure before any capability/main-bundle upload.

Every assigned Pod ID receives an append-only lifecycle receipt and must be
deleted before another attempt. A retry is forbidden after any secret/private
data exposure, cost uncertainty, inability to prove deletion, judge failure,
hash mismatch, PF-4 semantic failure, main-bundle upload, or product workload
start.

## 3. Mandatory returned-shape gate

Before the main bundle upload, the returned/cgroup-effective worker must have:

- at least 16 vCPU;
- at least 94 GiB RAM;
- at least 4 GiB RAM per effective vCPU;
- the exact frozen image, disk, zero-volume, Secure Cloud, name, rate, and
  provider deadlines.

The prior 32-vCPU/125-GiB shape is noncompliant and must be deleted before main
bundle upload if returned again.

## 4. PF-4 through PF-7 boundary

Only one shape-compliant worker may receive the minimal PF-4 capability
payload. PF-4 must prove the repaired resource accounting, streaming
process-tree observer, pinned tracer, disk/clock/cgroup/process capabilities,
validated local lifecycle `BOUND`, off-worker round trip, and residue cleanup.

Only PF-4 GREEN permits the deterministic main-bundle upload. PF-2R through
PF-7 then run on that same worker. The 15-minute network-proof growth canary
must project no more than 1 GiB over 24 hours. Every latency, cardinality,
reconciliation, fault, observer, evidence, and teardown gate remains unchanged.

The worker is deleted after preflight success or any terminal failure. GREEN
requires exact-ID absence, empty active inventory, verified evidence retrieval,
and final same-hash independent GLM 5.2 GREEN.

## 5. Prospective final campaign authority

After and only after complete R6 preflight GREEN, Kenneth's requested final
campaign remains a separate packet and worker:

- one successful worker;
- exactly 24 measured hours;
- maximum 28 paid hours;
- maximum aggregate final-campaign cost, including container storage: `$35`;
- 500,000 tasks, 5,000,000 events, 1,000,000 receipts, 250,000 vectors;
- 500-worker workload;
- 24 scheduled same-host process kill/restart/reconciliation cycles;
- exactly 9,976 verifier executions;
- evidence retrieval and hash verification before deletion;
- exact-ID absence and empty inventory after deletion.

The final campaign cannot start from this authorization envelope. It requires
a newly frozen final packet and fresh same-hash independent GLM 5.2 GREEN.

## 6. Operator authorization string

The exact human response that activates only the R6 paid-preflight envelope is:

```text
I authorize the PDH-3 R12 R6 paid-preflight envelope bound to SHA-256 <insert exact envelope SHA-256>: up to three sequential Secure Cloud L40S creation attempts, one worker at a time, no replacement after main-bundle upload, maximum 10-hour successful preflight lifetime, and $12 aggregate R6 cost ceiling. Freeze exact absolute provider deadlines and obtain fresh same-hash GLM 5.2 GREEN before the first creation request. Preserve R5 unchanged. Do not start the 24-hour campaign until R6 preflight is fully GREEN and a separate final packet is independently GREEN.
```
