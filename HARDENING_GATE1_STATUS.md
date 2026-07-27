# Hardening Gate 1 Status

- `STATUS`: `HARDENING_1_CLI_GREEN`
- `UTC_CLOSED`: `2026-07-27T16:42:52Z`
- `PARENT_GATE`: `HARDENING_0_CLOSEOUT_GREEN`
- `IMPLEMENTATION_COMMIT`: `ae3fe17922d9d6dfcb81d69e2080455f597f4cba`
- `PACKET_SHA256`: `0d062768d304b7ea5e4ba64e53c5946717b55302ad2646620e3c522b7905e97c`
- `INDEPENDENT_JUDGE`: `glm-4.7 via glm-zai`
- `INDEPENDENT_JUDGE_VERDICT`: `GREEN`
- `NEXT_ALLOWED_GATE`: `HARDENING_2_AWS_DEMO_GREEN`

The judge-facing CLI is a deterministic, credential-free facade over the
existing replay and verifier. The default path is explicitly labeled
`KEYLESS_LOCAL_REPLAY`.
