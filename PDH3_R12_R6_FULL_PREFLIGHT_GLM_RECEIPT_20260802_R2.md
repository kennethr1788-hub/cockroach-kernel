# PDH-3 R12 R6 full preflight GLM receipt R2

Status: `GLM_5_2_GREEN`

UTC: `2026-08-02T11:53:00Z`

- target packet: `PDH3_R12_R6_FULL_PREFLIGHT_MIN_VCPU_PACKET_20260802_R2.md`;
- target packet SHA-256:
  `044a13b0037650edbecce168da7f54e5ad260aafd0c104cd1a3a1056cb9d40d9`;
- route: direct `glm-zai`;
- requested and served model: `glm-5.2`;
- fallback disabled: true;
- verdict: `GREEN`;
- critical findings: none;
- high findings: none;
- required corrections: none;
- builder/provider/worker authority: none.

The first R2-packet transport attempt returned HTTP 200 with empty response
content and `finish_reason=length`. It is preserved as unavailable transport,
not a verdict. The second attempt reviewed the same unchanged packet hash with
a bounded output schema and returned the controlling GREEN.

This GREEN permits only the first creation request inside the R6 diagnostic
preflight envelope. It is not execution evidence and does not authorize the
24-hour campaign.
