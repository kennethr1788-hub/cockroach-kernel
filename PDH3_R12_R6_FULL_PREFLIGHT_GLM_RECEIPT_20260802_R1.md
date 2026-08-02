# PDH-3 R12 R6 full preflight GLM receipt R1

Status: `GLM_5_2_GREEN`

UTC: `2026-08-02T11:44:00Z`

- target packet: `PDH3_R12_R6_FULL_PREFLIGHT_MIN_VCPU_PACKET_20260802_R1.md`;
- target packet SHA-256:
  `3c8ba8be17590bb248f79c127a348e630199c204b426622fdc6e3dbcc4e2c60a`;
- route: direct `glm-zai`;
- requested and served model: `glm-5.2`;
- fallback disabled: true;
- builder authority: none;
- provider/worker authority: none;
- verdict: `GREEN`;
- critical findings: none;
- high findings: none;
- required corrections: none.

The first GLM response is preserved in
`PDH3_R12_R6_FULL_PREFLIGHT_GLM_RAW_20260802_R1.txt` but is invalid as a
load-bearing receipt because its rationale reversed the packet's stop and
terminate order. No paid mutation occurred from that output.

- invalid first raw-output SHA-256:
  `aa26abaaea98b9b618c7796097dd95fa30fb357d7083a8242dc650efe92b2f5f`.

The second response reviewed the same unchanged packet hash and accurately
states the deadline order: host closeout `21:25Z`, provider stop `21:40Z`,
provider terminate `21:55Z`. The controlling raw output is
`PDH3_R12_R6_FULL_PREFLIGHT_GLM_RAW_20260802_R2.txt`.

- controlling raw-output SHA-256:
  `242ea60ed6e1775a6942c63f140093f79ad80f63fb66b25cd8f46ce882ed3e73`.

This GREEN permits only the first creation request inside the frozen R6
preflight envelope. It is not R6 execution evidence and does not authorize the
24-hour measured campaign.
