# Hardening Gate 2 Reseed Checkpoint R1

- `UTC_RECORDED`: `2026-07-27T18:15:36Z`
- `STATUS`: `RESEED_READY_NOT_GREEN`
- `PARENT_COMMIT`: `a576bd63d68948a8cb110ba9b804f37905db0d20`
- `PROMOTE_SEED_SHA256`: `c7b9990033b36f3ca04e47233709c88aa7d72d8888bf74f384eb8c6833131d11`
- `PROMOTE_FINALIZE_SHA256`: `a5aac6fef7cff7b3d4fadb4d0f7dd82696a6958bf6df4e167030d224ccbf33a3`
- `REFUSE_SEED_SHA256`: `a6bd2d17e5921bc510cbe041a98b1624e903c98e7fcfe8b94ac7754701bb2344`
- `REFUSE_FINALIZE_SHA256`: `96d7f9d3a5d3a959fa0cfadc8b442fb73ec8eeb8d6d104d8c852a805aaedc627`
- `INPUT_PROVENANCE`: `preserved P9 live evidence at the final P9 implementation commit`
- `TARGET_DATABASE`: `cockroach_kernel`
- `TARGET_SCHEMA`: `ck`
- `TARGET_CASES`: `ck-p9-live-promote-r1; ck-p9-live-refuse-r1`
- `NEW_BEHAVIOR`: `none`
- `NEW_CREDENTIAL_OR_PERMISSION`: `none`

The only allowed repair is reapplying the four exact preserved P9 synthetic
seed/finalization transactions through the already authenticated owner SQL
Shell, then proving exact row counts and hashes before re-running the public
test. No schema, grant, cluster setting, route, verifier, or candidate changes
are permitted.
