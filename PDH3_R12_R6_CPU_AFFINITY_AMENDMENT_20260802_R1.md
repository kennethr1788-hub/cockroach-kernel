# PDH-3 R12 R6 prospective CPU-affinity amendment R1

Status: `PROSPECTIVE_LOCAL_CANDIDATE__NO_PAID_WORKER_AUTHORIZED`

UTC frozen: `2026-08-02T09:35:32Z`

Implementation commit: `8465880b3753e700217231c59ad43f3362ecdd6d`

## 1. Failure being corrected

The prior replacement worker returned 32 vCPU and 125 GiB. The frozen gate
required at least 4 GiB for every returned vCPU, so it correctly rejected the
shape because 125 is less than 128. No main bundle was uploaded and no measured
clock began. The worker was deleted and its attempt remains failed evidence.

The provider control surface used by this campaign does not select an exact
vCPU/RAM pair before creation. Therefore a packet that merely asks again for an
L40S cannot prospectively guarantee a 128-GiB response.

## 2. Selected repair

Retain the 4-GiB-per-effective-vCPU invariant. Derive one deterministic cap:

```text
memory_bound_vcpus = floor(provider_memory_gib / 4)
effective_vcpu_limit = min(provider_vcpus, memory_bound_vcpus)
```

The provider shape is rejected before upload unless:

- provider vCPU is at least 16;
- provider memory is at least 94 GiB;
- the derived effective limit is at least 16;
- Secure Cloud, one L40S, exact image, 250-GB disposable disk, zero persistent
  volume, and the frozen rate ceiling all pass the existing readback gate.

Examples:

| Provider readback | Derived limit | Result |
|---|---:|---|
| 32 vCPU / 125 GiB | 31 | eligible for Linux affinity proof |
| 16 vCPU / 188 GiB | 16 | eligible; no cap reduction needed |
| any vCPU / 93 GiB | n/a | rejected before upload |
| 15 vCPU / any memory | n/a | rejected before upload |

The cap is not a metadata label. The Linux kernel affinity mask must be applied
and read back exactly before the relevant workload is allowed to continue.

## 3. Enforcement and inheritance chain

1. Host readback derives and hash-binds the plan before any upload.
2. PF-4 transfers the affinity module with the minimal probe payload.
3. PF-4 applies `sched_setaffinity` to its process before resource measurement,
   then reads the mask back exactly. The measured resource check still applies
   the 4-GiB-per-effective-vCPU invariant.
4. The remote launcher independently recomputes the plan from provider
   readback, applies the exact mask before forking, and verifies the detached
   observer process by PID.
5. The observer launches the preflight runner. The runner verifies its own
   mask and three environment bindings before creating output roots.
6. After the three local CockroachDB processes start, the runner verifies the
   exact mask of every live node PID and publishes a hashed checkpoint.
7. After the scheduled kill/restart/reconciliation cycle, the runner verifies
   every current CockroachDB PID again, including the newly restarted node.
8. Any missing Linux API, insufficient source CPU set, apply/readback mismatch,
   environment mismatch, dead process, or child-mask mismatch is terminal.

The packet relies on Linux process-affinity inheritance for descendants, but
does not falsely claim that every transient query child has been individually
sampled. It directly verifies the launcher descendant, the runner, all three
CockroachDB children, and the restarted CockroachDB child. Actual RunPod/Linux
evidence remains required before this prospective mechanism can become a
hardware GREEN gate.

## 4. Preserved workload and evidence contract

This amendment does not change:

- 500,000 tasks, 5,000,000 events, 1,000,000 receipts, or 250,000 vectors;
- the 27-query mix or literal c500 stages;
- p99 5,000-ms or maximum 10,000-ms latency limits;
- setup, growth, network, database, or other evidence limits;
- exact-count, idempotency, vector-quality, plan, or query-result checks;
- the same-host process fault and reconciliation semantics;
- retrieval-before-delete, exact-ID absence, or empty-inventory requirements;
- the prohibition on the 24-hour measured branch during R6 preflight.

It changes only the prospective interpretation of provider CPU capacity from
raw returned vCPU to a kernel-enforced effective CPU set that preserves the
existing memory ratio.

## 5. Fail-closed boundary

The following are hard blockers:

- `PROVIDER_SHAPE_INSUFFICIENT`;
- `EFFECTIVE_VCPU_LIMIT_INSUFFICIENT`;
- `LINUX_AFFINITY_REQUIRED` or `AFFINITY_API_UNAVAILABLE`;
- `AFFINITY_SOURCE_TOO_SMALL` or `AFFINITY_APPLY_MISMATCH`;
- `EFFECTIVE_VCPU_PLAN_MISMATCH` or `EFFECTIVE_VCPU_BINDING_MISMATCH`;
- `DETACHED_PROCESS_AFFINITY_MISMATCH`;
- `COCKROACH_NODE_AFFINITY_MISMATCH` or incomplete child coverage.

No fallback to raw vCPU, a label-only cap, shell `taskset`, reduced memory
ratio, threshold relaxation, or post-failure reinterpretation is allowed.

## 6. Evidence classification

Current local evidence proves deterministic plan derivation, fail-closed
application/readback logic under injected Linux interfaces, source/argument
binding, package completeness, compilation, and extracted smoke behavior.

It does not prove that a future RunPod container exposes or permits the Linux
affinity API. That must be proven on the paid worker during PF-4 before main
bundle upload. A GLM GREEN on this amendment is design/preflight approval only,
not RunPod execution evidence.
