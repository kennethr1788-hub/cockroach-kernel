# PDH-3 R12 R6 PF-4 minimum-vCPU GLM receipt R1

Status: `GREEN_FOR_EXACT_PACKET__PF4_LIFECYCLE_ONLY`

UTC reviewed: `2026-08-02T11:03:09Z`

## Frozen target

- packet: `PDH3_R12_R6_PF4_MIN_VCPU_LIFECYCLE_PACKET_20260802_R1.md`;
- packet SHA-256:
  `c1bdd33757c7ca894fc0b15d996f91db703d8d44c82484b106d4bd92348517e6`;
- packet commit:
  `de095d68a40af56ba9dd33624042d9fb3c23b647`.

## Independent lane

- route: direct `glm-zai`;
- requested model: `glm-5.2`;
- exact-model verification: `glm-5.2`;
- fallback: disabled;
- primary retries: zero;
- served model reported by the wrapper: `glm-5.2`;
- role: independent, sanitized, non-authoring judge;
- authority exclusions: no shell, write, repository, credential, browser,
  provider, worker-launch, implementation, or public-action authority.

## Result

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: c1bdd33757c7ca894fc0b15d996f91db703d8d44c82484b106d4bd92348517e6
VERDICT: GREEN
BLOCKERS:
- none
```

The judge recorded only non-blocking risks already closed by the packet's
fail-closed worker readback, cgroup threshold, datacenter allowlist, provider
deadlines, teardown law, and no-blind-retry boundary.

## Raw custody

- raw output: `PDH3_R12_R6_PF4_MIN_VCPU_GLM_RAW_20260802_R1.txt`;
- raw-output SHA-256:
  `d80a27e1807aa4f127270a196ffe41caf634d6c7624914a16019ef9ac9a6184c`.

This receipt permits only the packet-bound minimum-vCPU PF-4 lifecycle. It is
not evidence that PF-4 passed and does not authorize main-bundle upload,
PF-2R through PF-7, or the measured 24-hour campaign.
