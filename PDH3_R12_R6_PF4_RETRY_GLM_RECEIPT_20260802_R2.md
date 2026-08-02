# PDH-3 R12 R6 PF-4 replacement retry GLM receipt R2

Status: `PF4_RETRY_LIFECYCLE_PREFLIGHT_GREEN`

UTC reviewed: `2026-08-02T10:45:00Z`

## Exact reviewed packet

- packet: `PDH3_R12_R6_PF4_RETRY_LIFECYCLE_PACKET_20260802_R1.md`;
- packet SHA-256:
  `5afd8dc0f027211fed6361569da254ebfcfaa60fb6ae4bc8945e07d63d0a2a0a`;
- corrected packet commit:
  `66b61bdec66335f9525c474889e58b9e0144cb60`;
- authorization SHA-256:
  `4fa410bfcd2e7307b79e7ffca2747b10ad50d0cfff320119ce73e44045a5fe1f`.

## Review history and identity

The R1 raw verdict targeted the superseded packet hash
`5df683a09c05fdbc38e61185d4fcd593ade739cb745ac273c62228d3cd2a7c60`
and is stale after the campaign-ID correction. It is preserved but cannot
authorize execution.

- valid route: direct `glm-zai`;
- requested and served model: `glm-5.2`;
- fallback: disabled;
- valid raw result: `PDH3_R12_R6_PF4_RETRY_GLM_RAW_20260802_R2.txt`;
- valid raw result SHA-256:
  `b837ca6555b9914de93ac5ead421e7b98b16526c476be96e8bb7d9ef8a8b19ea`;
- judge authority: review only; no shell, write, repository, credential,
  browser, provider, implementation, worker-launch, or gate-mutation authority.

## Verdict

- exact corrected packet-hash match: GREEN;
- lifecycle verdict: GREEN;
- blockers: none;
- execution still requires real cgroup capability evidence, full teardown, and
  a fresh independent result review.

This review permits only the corrected bounded PF-4 replacement lifecycle. It
does not prove PF-4, PF-2R through PF-7, or the measured 24-hour campaign GREEN.
