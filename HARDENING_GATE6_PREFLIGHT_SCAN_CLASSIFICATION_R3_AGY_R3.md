# Hardening Gate 6 R3 — Tool-Corrected Packet Scan

- `PACKET`: `HARDENING_GATE6_PREFLIGHT_PACKET_R3_AGY_R3.md`
- `PACKET_SHA256`: `feae49cac213118fb78fcfdb7d72c2d1df7f75293916a6db8d9274212b78187b`
- `PACKET_BYTES`: `102866`
- `GITLEAKS_FINDINGS`: `0`
- `DETECT_SECRETS_FINDINGS`: `0`
- `EGRESS_GATEWAY_GLM`: `ALLOW; byte-identical`
- `EGRESS_GATEWAY_AGY`: `ALLOW; byte-identical`
- `UTC_RECORDED`: `2026-07-28T02:13:00Z`

This revision changes the R3 tool-provenance path binding and execution wiring,
preserves the prior judge history as receipts without embedding raw historical
judge voices, and requires both independent lanes to rerun from scratch.
