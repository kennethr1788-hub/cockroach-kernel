# PDH-3 R12 R6 platform compatibility amendment R1

Status: `PROSPECTIVE_REPAIR__NO_PROVIDER_AUTHORITY_BY_ITSELF`

This amendment responds to the preserved R6 attempt-01 failure in
`PDH3_R12_R6_ATTEMPT_01_BLOCKED_RECEIPT_20260802_R1.md`. It changes only the
preflight evidence harness. It does not change the product candidate, target
cardinality, query mix, latency thresholds, fault schedule, evidence caps,
teardown requirements, or 24-hour campaign gate.

## 1. Verified failure mechanisms

R6 attempt 01 returned the required 16-vCPU/188-GiB Secure Cloud L40S shape and
passed CPU, RAM, disk, write-throughput, fsync, random-I/O, process-tree,
monotonic-clock, and residue checks. It failed before the main bundle upload.

Three harness defects were verified:

1. PF-4 transferred `pdh3_r12_network_observer.py` without its import-time
   dependency `run_pdh3_traced.py`. The observer imports that adjacent file at
   module load, so the minimal PF-4 payload was incomplete.
2. PF-4 required five cgroup-v2 files directly under `/sys/fs/cgroup`. The
   returned Secure Cloud container exposed none of those root files. The probe
   did not discover cgroup v1 or the already available procfs/process-tree
   accounting interface.
3. The capability receipt retained only hashes of observer stdout and stderr.
   The host teardown path did not retrieve those raw streams, preventing direct
   diagnosis of a provider-side observer failure.

The first two defects caused the semantic non-GREEN result. The third defect
reduced diagnostic evidence but did not mislabel the attempt as successful.

## 2. Repair contract

### 2.1 Complete minimal observer payload

PF-4 now transfers and independently hashes all five minimal components before
execution:

- `pdh3_r12_network_observer.py`;
- `run_pdh3_traced.py`;
- `pdh3_r12_remote_capability.py`;
- the pinned Ubuntu Noble strace DEB; and
- the pinned Ubuntu Noble libunwind8 DEB.

The isolated two-file observer import canary must pass before a paid launch.
Remote SHA-256 verification remains mandatory before executing the observer.

### 2.2 Portable resource-accounting backend

The preflight chooses exactly one directly observed backend in this order:

1. complete cgroup v2: `cpu.stat`, `memory.current`, `memory.events`,
   `io.stat`, and `pids.current`;
2. complete cgroup v1: CPU, memory usage and limit, block-I/O, and PID
   controller files; or
3. procfs process-tree accounting bound to the provider-returned allocation:
   `/proc/self/status`, `/proc/self/io`, `/proc/stat`, `/proc/meminfo`,
   `/proc/net/dev`, scheduler affinity, the existing per-node process metrics,
   and the provider's verified vCPU/RAM shape.

The procfs backend does **not** claim cgroup isolation. Its scope is explicitly
`PROCESS_TREE_PLUS_PROVIDER_ALLOCATION`. Provider allocation remains a hard
upper bound in the capability calculation. Cgroup isolation may be claimed
only when the selected backend is `CGROUP_V1` or `CGROUP_V2`.

The main PF-2R-through-PF-7 resource sampler uses the same backend selection on
every sample. A missing backend or unreadable bounded file is terminal.

This is a mechanism correction, not a threshold reduction. The declared
minimum remains 16 effective vCPU, 64 GiB effective RAM, at least 4 GiB per
effective vCPU, 240 billion total disposable-disk bytes, and 220 billion free
bytes, plus the existing I/O and latency requirements.

### 2.3 Raw observer failure custody

The capability process writes observer stdout and stderr to exclusive,
fsynced files capped at 1 MiB each. The host retrieves both streams before
interpreting the capability receipt. Their local hashes must equal the hashes
embedded in the canonical receipt. On any failure, the host best-effort
retrieves the capability receipt and both raw streams before deleting the Pod.

Failure to retrieve, hash, or reconcile either stream is terminal. The worker
is still deleted, exact-ID absence is proved, and active campaign inventory
must be empty.

## 3. Bound repaired sources

| File | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_remote_capability.py` | `f644c0dd05509f762f733f28979f80f63cde87c8a4a2480884cce10e963306bb` |
| `post-dogfood/pdh3_r12_r6_run_pf4.py` | `41b9e6b25929166baac39f7e8993647b0bff7178a790a287f248d89c6eaacbbd` |
| `post-dogfood/pdh3_r12_remote_preflight.py` | `dce066c67ab0c74492bae8be6850a9d78920570f588414cc6118975141bb042c` |
| `post-dogfood/pdh3_r12_network_observer.py` | `8e6f72c4fa44d56f982697ee3091938f27924a5120846cba96cc6ed1f794f102` |
| `post-dogfood/run_pdh3_traced.py` | `87ce2498b1a03d1a0c80e96ef9e966e3a8958788c934e0ce4a63201aec3691e4` |
| `post-dogfood/test_pdh3_r12_remote_capability.py` | `f2d2d8e0b5713efef82c30c8ff3a0724efdfe31c55017b3dd0183fa274315175` |

## 4. Local evidence

- 49 focused `test_pdh3_r12*.py` tests: GREEN;
- command-stream persistence and hash reconciliation test: GREEN;
- synthetic cgroup-v2 selection: GREEN;
- synthetic cgroup-v1 selection: GREEN;
- synthetic procfs/provider-bound fallback selection: GREEN;
- isolated observer import with only the two required Python files: GREEN;
- Python compilation of all changed runtime modules: GREEN;
- main-bundle test: GREEN;
- local provider inventory after the failed attempt: `[]`;
- R6 runtime exact-key scan after closeout: zero matches.

Local tests do not prove the selected RunPod backend or ptrace/strace behavior.
The replacement PF-4 is the smallest paid test that can prove those facts.

## 5. Primary technical sources

- Linux kernel cgroup-v2 interface:
  `https://docs.kernel.org/admin-guide/cgroup-v2.html`;
- Linux kernel cgroup-v1 index:
  `https://docs.kernel.org/6.1/admin-guide/cgroup-v1/index.html`;
- Linux kernel CPU-accounting controller:
  `https://docs.kernel.org/admin-guide/cgroup-v1/cpuacct.html`;
- official RunPod CLI and Pod lifecycle commands:
  `https://github.com/runpod/runpodctl`.

These sources establish that cgroup v1 and v2 expose different file layouts
and that provider Pod lifecycle must be independently managed. They do not
assert which backend a future worker will expose; PF-4 must observe that live.

## 6. Replacement preflight law

The replacement execution packet must bind this amendment, the repaired
source hashes, a deterministic main bundle, current provider inventory and
price, one worker maximum, one immutable campaign ID, a 250-GB disposable
container disk, zero persistent/network volume, a `$0.99/hour` rate ceiling,
a `$12` aggregate ceiling, a maximum ten-hour successful preflight lifetime,
and absolute provider stop/terminate deadlines.

The operator's authorization covers one replacement paid preflight attempt.
No retry after PF-4 or main-bundle upload is permitted. A transient creation or
readiness failure consumes this replacement unless separately reauthorized.

The main bundle may upload only after all PF-4 checks are GREEN, including:

- one supported accounting backend;
- raw observer stdout/stderr retrieval and hash reconciliation;
- a GREEN streaming observer capability receipt;
- exact provider shape, rate, image, disk, and zero-volume readback; and
- a live, identity-bound lifecycle guard.

Any missing artifact, unsupported backend, observer error, hash mismatch,
threshold failure, credential exposure, cost uncertainty, or teardown
uncertainty is `PDH3_R12_R6_BLOCKED`.

## 7. Independent review boundary

This amendment and the resulting paid-preflight packet require one direct,
non-authoring GLM 5.2 review over the exact complete packet hash. The builder
cannot self-approve. `GREEN` authorizes only the bounded replacement preflight;
it does not approve or start the 24-hour campaign.
