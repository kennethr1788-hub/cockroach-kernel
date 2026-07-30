# EV1-T01 GLM Result Audit Receipt R2

- `STATUS`: `GREEN`
- `UTC_RECORDED`: `2026-07-30T15:28:57Z`
- `BASE_EVIDENCE_PACKET_SHA256`: `6e5f1c1edc0d3bb8438120ea824557a75071bc55807da376c336c6f3b4cfa533`
- `OUTPUT_AMENDMENT_SHA256`: `d55a9eaa7984e7b07988ba54dc5bec5f40a210d52e17034b2febb6bf46f8e258`
- `COMPOSED_INPUT_SHA256`: `989a2e866dd9464dcc82d039d199b45085b254e263e2254503a6f9cc058d56b9`
- `RAW_OUTPUT_FILE_SHA256`: `cad2fd579204f06fe924be490c87a8a205a3447a331bc0fddfb00a5e5722e7aa`
- `TRANSPORT_EXIT`: `0`
- `TRANSPORT_SERVED_MODEL`: `glm-5.2`
- `VERDICT`: `GREEN`
- `RECUSAL`: `CLEAR`
- `BYTE_EXACT_RECOVERY`: `SUPPORTED`
- `FULL_ACCEPTANCE_FAILED`: `SUPPORTED`
- `INFRASTRUCTURE_INVALID_NON_SCORING`: `SUPPORTED`
- `BLOCKERS`: `NONE`
- `COUNTED`: `TRUE`

The R2 result is valid because direct wrapper transport verified `glm-5.2`, the
generated output made no competing identity claim, all required fields were
present, and the verdict preserved the conservative claim ceiling. R1 remains
preserved as invalid and is not counted.
