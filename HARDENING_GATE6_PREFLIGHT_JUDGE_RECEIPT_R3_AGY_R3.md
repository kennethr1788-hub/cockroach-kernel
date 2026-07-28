# Hardening Gate 6 R3 — Tool-Corrected Same-Hash Preflight Receipt

- `STATUS`: `PREFLIGHT_GREEN`
- `PACKET_SHA256`: `feae49cac213118fb78fcfdb7d72c2d1df7f75293916a6db8d9274212b78187b`
- `GLM_SERVED_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RECUSAL`: `clear`
- `GLM_RAW_SHA256`: `a580068e2060d5b134f5af16d32d8fa67d2ffbf51ec748787e76dbad3f28bd0d`
- `AGY_MODEL`: `Gemini 3.1 Pro (High)`
- `AGY_VERDICT`: `GREEN`
- `AGY_RECUSAL`: `clear`
- `AGY_RAW_SHA256`: `b10bde6d835b07bc350ce7c588fafbaa44e5365d26bf4b7a1a4750818bf71847`
- `CLAUDE`: `RECUSAL_REQUIRED_PRESERVED_NOT_COUNTED`
- `RUNPOD_CREATED`: `no`
- `MEASURED_EXECUTIONS`: `0`
- `UTC_RECORDED`: `2026-07-28T02:15:22Z`

Both independent lanes reviewed the exact tool-corrected packet and bound the
same digest. This is the controlling R3 preflight. It authorizes sequential
creation attempts and only the pre-payload capability canary. The full payload
may be uploaded only after a live canary passes every frozen isolation check.
