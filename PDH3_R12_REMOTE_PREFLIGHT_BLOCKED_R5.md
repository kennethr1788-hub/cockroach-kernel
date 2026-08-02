# PDH-3 R12 remote preflight blocked receipt R5

Status: `PDH3_R12_PREFLIGHT_BLOCKED`

- blocker: `PF4_CAPABILITY_GATE_FAILED`
- failure stage: `PF4_CAPABILITY`
- last GREEN gate: `R12_R5_SAME_HASH_GLM_GREEN`
- packet SHA-256: `3d35c77a21d629c922ef137d08c9640c92fa84bce25da7ec806d6dcf538da17a`
- threshold amendment SHA-256: `012716a1a377a938bc8ca20b84631b6450f407c635748929d91db59ff675e2e1`
- implementation commit at attempt: `de584382611daa2376a1c59cd12655ed1268d79c`
- provider Pod ID: `5ommwuqsbffrl0`
- provider Pod name: `ck-pdh3-r12-preflight-r5-01`
- worker create UTC: `2026-08-02T06:58:41Z`
- worker deletion request UTC: `2026-08-02T06:59:21Z`
- closeout verification UTC: `2026-08-02T07:00:41Z`
- returned worker: Secure Cloud L40S, 32 vCPU, 125 GB RAM, 250 GB
  disposable container disk, zero persistent/network volume, `$0.99/hour`
- worker created: `true`
- SSH and PF4 upload began: `true`
- main project bundle upload began: `false`
- product workload execution began: `false`
- final 24-hour measured campaign began: `false`
- worker deleted: `true`
- exact Pod lookup after deletion: structured provider `404 pod not found`
- active provider inventory after failure: `[]`
- local orchestrator, SSH, transfer, lifecycle-guard, and workload processes
  remaining: `0`
- exact attributable provider charge: `unavailable`; the observed worker lifetime
  was approximately 40 seconds at the returned `$0.99/hour` rate, but this is
  not represented as a provider invoice
- sanitized provider readback after closeout: balance `85.466193353`, account
  spend rate `$0.002/hour`, spend limit `140`; the readback does not attribute
  a charge to this attempt
- retries authorized by R5: `0`

## PF4 observations

The remote capability harness passed the disk-total, disk-available,
disk-used-fraction, sequential-write, sustained-write, fsync, random-sync,
cgroup-file, process-tree, monotonic-clock, and residue checks. It failed two
declared checks:

1. `ram`: the probe used host-wide `os.cpu_count() == 256` and host-wide
   `/proc/meminfo` instead of the container's effective cgroup CPU and memory
   limits. This created a false requirement of roughly 1 TiB for a provider
   allocation independently verified as 32 vCPU and 125 GB RAM. Correcting the
   host leak does not make this R5 allocation compliant: `125 / 32 == 3.90625`
   GiB per provider-returned vCPU, below the frozen `4 GiB` ratio. A future
   worker must pass both provider-shape and effective-cgroup accounting; the
   repair may not cap or relabel the returned 32-vCPU allocation as 16 vCPU.
2. `network_namespace`: the exact unprivileged user/network/PID namespace probe
   exited `2`. The wrapper retained only hashes of the child output, so the
   provider-side rejection mechanism was not directly preserved.

A third independent lifecycle defect was discovered during closeout. The local
detached guard was spawned with a scrubbed environment that omitted the already
authorized host-local RunPod credential. It emitted four `BIND_RETRY` events and
terminated `GUARD_BLOCKED:BIND_DEADLINE_EXCEEDED`. The launcher accepted only
PPID detachment and log-file existence instead of requiring a validated `BOUND`
event. Provider-native stop and terminate deadlines remained present, and the
foreground orchestrator deleted the worker immediately after PF4 failed.

These are harness defects. They are not evidence that the product workload
passed or failed, because the main bundle was never uploaded and the product
workload never ran.

## Evidence hashes

- create response SHA-256: `9e14f46ce2842bd5efae8ddca92e6c35378cf3e65ba37560bf12d3eb8ebf1089`
- empty create stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- detailed Pod receipt SHA-256: `17c8757f6512c6f82fec3c0e9c66c45f6b57b8fd4b1a6aff19d5d09d7318f212`
- PF4 failure receipt SHA-256: `21a5d439a8fab2f43daba86d1a8a9df91deb874abe2d62472823fe605e1ad893`
- PF4 capability record embedded receipt SHA-256: `6221e6df764ba5072728bcdfb30f9d33be4329b3efa1caf9b0344b8b08247229`
- orchestrator blocked receipt SHA-256: `b4522cd51e5d8417652ad98445e466e9b8b70d792db41709aacb8174af9fd32d`
- delete response SHA-256: `b93a3a0376507489872a968a511eaaa5c808bbb7cb507386f4034662b0ffb089`
- lifecycle guard chain SHA-256: `17ab42da1bbd2a8adfee04b1405882f45ae23d5ca229376eca92c65a52012142`
- lifecycle guard process log SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

## Resume boundary

The R5 single worker attempt is consumed. No automatic retry is permitted.
Before another paid worker may be created, repair and locally test all three
harness defects, freeze a new packet, and obtain a fresh independent same-hash
GREEN verdict. A fresh operator authorization must then name the replacement
preflight worker envelope. The separately authorized 24-hour measured campaign
remains gated behind a fully GREEN replacement preflight and a new final
same-hash campaign packet; it may not start from the R5 packet or evidence.
