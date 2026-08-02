glm-zai: served by glm-5.2
```text
SERVED_MODEL: glm-5.2
TARGET_AMENDMENT_SHA256: 4bf4e47b79a66c672208cbd90f18ad31ff4f23400e833c728a189507dbb0e0b9
VERDICT: GREEN
CRITICAL_FINDINGS:
- NONE
HIGH_FINDINGS:
- NONE
REQUIRED_CORRECTIONS:
- NONE
RATIONALE: The amendment correctly converts PF-3 from a target-scale execution gate into a resource-classification gate while preserving every target-scale proof obligation. The measured host (≈18 GiB RAM, 9.1 GiB free disk, 11 logical CPUs, 98% filesystem utilization) cannot satisfy the frozen 94 GiB RAM / 250 GB disk worker minimum, and the three-process CockroachDB allocation alone (3×(8 GiB cache + 8 GiB SQL) = 48 GiB) exceeds physical memory before any ancillary load. The chosen PF3_LOCAL_RESOURCE_BOUNDARY_GREEN branch explicitly (a) refuses any local target-scale attempt, (b) forbids representing any reduced-scale run as equivalent, and (c) defers the first full-cardinality 500,000/5,000,000/1,000,000/250,000 proof to PF-5 on verified remote hardware. All other R1 stages, thresholds, workloads, claim boundaries, and kill lines are stated to remain unchanged. PF-2 is correctly demoted to diagnostic-only SQL correctness evidence with no target-scale inference. PF-4 retains hardware/disk/namespace/checkpoint/price/lifecycle verification before upload. The added remote start prohibition closes the loop: if PF-5 cannot seed, capture plans, and export a verified receipt within deadline plus teardown reserve, PF-6 and the 24-hour campaign remain forbidden. The closing clause correctly scopes GREEN to authorize only the amended preflight sequence and explicitly withholds RunPod campaign authorization. No weakening of target-scale proof, no equivalence substitution, and no silent relaxation of safety fuses is present.
```
