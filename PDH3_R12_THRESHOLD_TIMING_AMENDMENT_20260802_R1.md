# PDH-3 R12 Threshold-Timing Amendment R1

Status: `FROZEN_DISCLOSURE__NO_WORKER_CREATED`

UTC created: `2026-08-02T06:00:00Z`

Parent plan: `PDH3_R12_EXTENSIVE_PREFLIGHT_PLAN_20260802_R1.md`

Parent plan SHA-256:
`a1214b4779fe1495de219ed0033421ac810390641cd97742deb61cd3957df3d9`

## Sequencing defect

Section 6.5 of the parent plan says disk benchmark thresholds must be frozen
before live inventory is seen. RunPod inventory and pricing were inspected
before the concrete disk thresholds below were written. This amendment does
not claim that the original sequencing requirement was met.

No worker was created, no remote disk benchmark ran, and no remote result was
visible before these thresholds were frozen. The values were derived from the
R11b setup rate, the 250 GB plan ceiling, CockroachDB's documented storage
reserve behavior, and a conservative minimum for sustained setup throughput.
They are prospective and may not be changed after any R12 worker benchmark is
visible.

## Frozen PF-4 thresholds

- Linux `x86_64`;
- at least 16 observed logical CPUs;
- at least 64 GiB observed RAM and at least 4 GiB per observed logical CPU;
- disposable filesystem total bytes at least `240,000,000,000`;
- disposable filesystem available bytes at least `220,000,000,000`;
- initial filesystem-used fraction no greater than `0.10`;
- 2 GiB sequential write throughput at least `75 MiB/s`;
- 8 GiB sustained write throughput, with a 512 MiB `fdatasync` interval, at
  least `75 MiB/s`;
- 200 fsync samples with p99 no greater than `50 ms`;
- 256 random synchronized samples at no less than `50 IOPS`;
- cgroup CPU, memory, I/O, and PID accounting readable;
- `/proc` process-tree inspection readable;
- monotonic clock non-regressing;
- the real unprivileged user/network-namespace observer capability canary
  GREEN;
- every generated benchmark file and directory removed before PF-4 closes.

The implementation that enforces these values is bound in the deterministic
bundle. Any missed threshold is terminal `PF4_CAPABILITY_GATE_FAILED`, followed
by evidence retrieval and worker teardown. Reduced thresholds, a second
benchmark, or a replacement worker are not authorized by this amendment.

## Review question

An independent judge must decide whether preserving the ordering defect and
freezing the prospective thresholds before worker creation is sufficient to
continue honestly. A GREEN verdict authorizes only the packet-bound paid
preflight. It does not erase the defect, certify the worker, authorize a retry,
or authorize the later 24-hour campaign.
