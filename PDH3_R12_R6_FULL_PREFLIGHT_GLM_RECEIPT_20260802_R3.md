# PDH-3 R12 R6 full preflight independent gate R3

- `STATUS`: `GREEN`
- `TARGET_PACKET`: `PDH3_R12_R6_FULL_PREFLIGHT_DIAGNOSTIC_PACKET_20260802_R3.md`
- `TARGET_PACKET_SHA256`: `938d8c1c34c4ca73986a60b1d18f8c8149c80c20628258dd5d88247d496fda64`
- `JUDGE_ROUTE`: direct `glm-zai`
- `SERVED_MODEL`: `glm-5.2`
- `VALID_RAW`: `PDH3_R12_R6_FULL_PREFLIGHT_GLM_RAW_20260802_R5.txt`
- `VALID_RAW_SHA256`: `58044ecc460ac7e359f73cc0a33ef250cbd87ed7b2a2e1081363c0d358d64cfb`
- `UTC_REVIEWED`: `2026-08-02T12:16:00Z`

The first same-packet response is preserved as invalid because it returned a fabricated target hash:

- `INVALID_RAW`: `PDH3_R12_R6_FULL_PREFLIGHT_GLM_RAW_20260802_R4_INVALID.txt`
- `INVALID_RAW_SHA256`: `9a24c26e46493f3add15f8aabcf46a83f992a0c51af4203a4c936885e9c3d37b`
- `INVALID_REASON`: `TARGET_PACKET_SHA256_MISMATCH`

The packet was not changed between the invalid and valid calls. Only the invocation wrapper supplied the already locally computed target hash and required it to be copied exactly. The valid direct response reported exact served-model identity, the exact target packet hash, `VERDICT: GREEN`, and PASS on boundary, evidence, cost, and lifecycle.
