# Cockroach Kernel P4 Frozen Packet

- `GATE`: `CK_P4_PENDING_JUDGE`
- `LAST_GREEN_GATE`: `CK_P3_LEDGER_GREEN`
- `CURRENT_COMMIT`: `4b8bde6`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `P3_PACKET_SHA256`: `d8cd81f035cb61599be03b907e07cefed23ea5b6eb11d39d5cbfdcf24a227b42`
- `FROZEN_UTC`: `2026-07-25T20:57:19Z`

## Implementation hashes

- `verifier.py`: `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`
- `test_verifier.py`: `788224e9bc90fac3cbeb912fc62862288e4cec8b66b6d21cff471c64f03452bf`

## Contract

The verifier accepts only the frozen p4-v1 record shape, canonical UTF-8 JSON,
SHA-256 payload linkage, stable IDs, declared relative paths, explicit
provenance, and supported schema. It emits only `PROMOTE`, `REFUSE`, or
`INVALID` with stable reason codes. It uses no clock, randomness, model, or
network. Quarantine is separate from active retrieval and `active()` always
excludes quarantined records.

## Test evidence

Six tests pass, covering promotion, malformed/unknown fields, hash mismatch,
unsupported schema, replay, unsafe paths, policy veto, unsupported input,
missing provenance, quarantine exclusion, and five-repeat determinism.

No S1, RunPod, AWS, P5, or later work is included.
