# Hardening Gate 6 R3 — Preflight Judge Receipt R1 (Superseded)

- `PACKET_SHA256`: `49068ab24f16b51120b447514bd928e527d02428a8343ae10443f8a83041613b`
- `GLM_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RAW_SHA256`: `37883d1a021f7aec5c110c6bcfccf325f8488a5e7407c1a916bdb83c4cea5591`
- `CLAUDE_MODEL`: `claude-opus-4-8`
- `CLAUDE_VERDICT`: `GREEN`
- `CLAUDE_RECUSAL`: `CLEAR`
- `CLAUDE_RAW_SHA256`: `93f1a3aed80ea98f20e8f3ad082c5c9ebbbd7357bbe1b628a1df94aa96f801b6`
- `STATUS`: `SUPERSEDED_BY_BUILDER_HARDENING`

Both required judges returned GREEN over the exact R1 packet. Claude also
identified non-blocking residuals involving the x32 syscall-number form and
socket descriptors 0/1/2. The builder independently treated those mechanisms
as worth closing before provider creation. The R1 GREEN therefore authorizes
nothing after the source changes. A complete new packet and complete same-hash
GLM/Claude review are mandatory.
