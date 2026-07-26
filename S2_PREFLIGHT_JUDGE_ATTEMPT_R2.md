# S2 Preflight Judge Attempt R2

- `UTC_CREATED`: `2026-07-26T01:57:00Z`
- `PACKET`: `S2_PREFLIGHT_PACKET_R2.md`
- `PACKET_SHA256`: `de9da7980f36ce63f305e56d8a301c5fc9722f8421d04ab12b6aff0cd6a89ab5`
- `PACKET_BYTES`: `100825`
- `RESULT`: `LOCAL_EGRESS_BLOCKED_NO_PROVIDER_EXECUTION`
- `RAW_RESULT`: `egress-gateway: blocked glm-zai:glm-5.2 egress: provider token`

The deterministic local gateway matched the metadata field name beginning
with `GLM_` plus a long hash label; no credential or provider material was
present, and no packet content left the machine. The field is renamed without
altering implementation, evidence, authority, or lifecycle semantics. R2
contains no verdict and cannot close or contribute to the preflight gate.
