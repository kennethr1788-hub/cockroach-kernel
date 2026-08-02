# PDH-3 R12 Preflight Resource-Boundary Amendment R2

Status: `FROZEN_FOR_INDEPENDENT_REVIEW__NO_RUNPOD_LAUNCH`

Parent plan:
`PDH3_R12_EXTENSIVE_PREFLIGHT_PLAN_20260802_R1.md`

Parent plan SHA-256:
`a1214b4779fe1495de219ed0033421ac810390641cd97742deb61cd3957df3d9`

Parent review receipt SHA-256:
`85bf6292856821ec5fd48e79d5a0a5c3af94222fa9f08d91ad70bc5280cdd413`

Parent checkpoint commit:
`f1b3a4bf40353745e67acf93444fa77c53fa5fed`

## Verified new host evidence

- physical memory: `19,327,352,832` bytes;
- logical CPU count: `11`;
- available bytes on the project filesystem at inspection:
  `9,114,685,440` bytes;
- project-filesystem utilization: `98%`;
- frozen remote worker minimum: `94 GiB` RAM and `250 GB` disposable disk;
- frozen CockroachDB process allocation: three processes, each with `8 GiB`
  cache and `8 GiB` SQL memory, before querybench, observers, logs, Python,
  kernel, and OS reserve.

The local host cannot safely reproduce the frozen target worker. Attempting the
full-cardinality three-process PF-3 workload locally would violate the plan's
own memory, disk, and HOME/runtime safety fuses. A smaller local execution cannot
prove target-scale plan selection, concurrency, storage, or growth.

## Narrow amendment

This amendment replaces only the PF-3 terminal rule. Every other R1 stage,
threshold, workload, claim boundary, and kill line remains unchanged.

PF-3 becomes a resource-classification gate with two valid GREEN branches:

1. `PF3_LOCAL_FULL_CARDINALITY_GREEN`: the local host directly satisfies the
   frozen resource fuses and the complete R1 PF-3 workload passes; or
2. `PF3_LOCAL_RESOURCE_BOUNDARY_GREEN`: direct host measurements prove the
   local host cannot safely run the target workload, no target-scale execution
   is attempted locally, no reduced-scale result is represented as equivalent,
   and PF-5 remains the first and mandatory full-cardinality proof.

The second branch is selected for the currently measured host.

PF-2 remains required at representative cardinality for SQL correctness,
current/indexed plan A/B, result equivalence, regression tests, and plan-parser
validation. PF-2 evidence is diagnostic only.

PF-4 must verify the exact remote hardware, disk, namespace/observer
capabilities, off-Pod checkpoint path, deadlines, price, and lifecycle before
upload. PF-5 must then run the first target-scale 500,000/5,000,000/1,000,000/
250,000 proof. No target-scale conclusion may be issued before PF-5.

## Additional remote start prohibition

If PF-5 cannot seed and reconcile full cardinality, capture target-scale plans,
and export a verified setup receipt within the frozen deadline and teardown
reserve, the worker must be closed out. PF-6 and the measured 24-hour campaign
remain forbidden.

## Judge question

Review whether this amendment correctly treats the Mac's hard resource mismatch
as a safety boundary without weakening target-scale proof. Return:

```text
SERVED_MODEL: <provider-reported model>
TARGET_AMENDMENT_SHA256: <exact hash supplied with request>
VERDICT: GREEN | NOT_GREEN | BLOCKED | JUDGE_UNAVAILABLE
CRITICAL_FINDINGS:
- <finding or NONE>
HIGH_FINDINGS:
- <finding or NONE>
REQUIRED_CORRECTIONS:
- <correction or NONE>
RATIONALE: <concise explanation>
```

GREEN authorizes only the amended preflight execution sequence. It does not
authorize or certify a RunPod campaign.
