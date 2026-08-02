# PDH-3 R12 R6 PF-4-only GLM preflight receipt R1

Status: `PF4_ONLY_LIFECYCLE_PREFLIGHT_GREEN`

UTC reviewed: `2026-08-02T09:55:20Z`

## Exact reviewed packet

- packet: `PDH3_R12_R6_PF4_ONLY_LIFECYCLE_PACKET_20260802_R1.md`;
- packet SHA-256:
  `723d95c459c2ef85ba29486a39c052dd36d69a1ba14976cdc6dabe71ba4367d3`;
- packet-freeze commit:
  `7dffd6013e59f366c37f1e694df09ff658f4a95c`;
- operator-authorization receipt SHA-256:
  `c55b77a8392082321e6d0b08a48085b5ff8e8be66775cb5a9e4dfbadd69c437b`.

## Judge identity and boundary

- route: direct `glm-zai`;
- requested and served model: `glm-5.2`;
- fallback: disabled;
- availability smoke: `READY_GLM_52_DIRECT`;
- raw result: `PDH3_R12_R6_PF4_ONLY_GLM_RAW_20260802_R1.txt`;
- raw result SHA-256:
  `0203439efcac3b4995664e8e82cd434ad8d53c343c7d2556bd8cd1dfd1988999`;
- judge authority: review only; no shell, write, repository, credential,
  browser, provider, implementation, worker-launch, or gate-mutation authority.

## Verdict

- exact packet-hash match: GREEN;
- lifecycle verdict: GREEN;
- blockers: none;
- non-blocking risk: L40S stock was `Low`, so inventory drift must stop
  fail-closed;
- required execution evidence: exact guard binding and heartbeat, real Linux
  affinity readback, exact Pod-ID absence, and lifecycle `TEARDOWN_GREEN`.

This review permits only the one bounded PF-4-only worker described by the
packet. It does not prove PF-4, R6, PF-2R through PF-7, or the 24-hour campaign
GREEN.
