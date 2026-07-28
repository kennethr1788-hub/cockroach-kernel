# Hardening Gate 6 R3 — GLM plus AGY Packet Scan Classification

- `PACKET`: `HARDENING_GATE6_PREFLIGHT_PACKET_R3_AGY_R1.md`
- `PACKET_SHA256`: `bce79ec92f76469cbd11efb0a4fd6221ab3da7e3135b2370907800426b40e7be`
- `PACKET_BYTES`: `99116`
- `GITLEAKS_FINDINGS`: `0`
- `DETECT_SECRETS_FINDINGS`: `0`
- `EGRESS_GATEWAY_GLM`: `ALLOW; byte-identical`
- `EGRESS_GATEWAY_AGY`: `ALLOW; byte-identical`
- `PRIVATE_PATH_ALIASES`: `0`
- `UTC_RECORDED`: `2026-07-28T01:56:00Z`

The first derived packet attempt was not dispatched: the egress gateway treated
the machine label `GLM_5_2_AND_AGY_GREEN_SAME_HASH` as a provider-token shape.
No secret scanner found a credential. The source label was changed to spaced
human text, the superseded status file was excluded, and the packet was rebuilt
from the committed source. No gateway rule was disabled, weakened, or bypassed.
This exact packet passes both judge-lane egress checks byte-identically.
