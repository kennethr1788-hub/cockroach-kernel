# Hardening Gate 2 Live Attempt R1

- `UTC_RECORDED`: `2026-07-27T18:15:36Z`
- `RESULT`: `FAIL_CLOSED`
- `PUBLIC_PROMOTE`: `503 INVALID MEMORY_RECORD_MISSING`
- `PUBLIC_REFUSE`: `503 INVALID MEMORY_RECORD_MISSING`
- `ACTION_TAKEN`: `NONE`
- `PROMOTE_RESPONSE_SHA256`: `3ebf5e963b620a61f18ab926ffdf86ac3f7c90688606c837c9458bfc507b866f`
- `REFUSE_RESPONSE_SHA256`: `3ebf5e963b620a61f18ab926ffdf86ac3f7c90688606c837c9458bfc507b866f`
- `COCKROACH_OWNER_QUERY`: `tasks=0; receipts=0; context_vectors=0; worker_results=0 for the two frozen task IDs`
- `FALSE_PROMOTION`: `no`
- `CREDENTIAL_EXPOSURE`: `no`

The public AWS path reached the deployed Lambda and the read-only CockroachDB
query path returned no matching frozen demo records. The handler emitted the
stable fail-closed response and performed no continuation action. A visible
owner-session count query in the authenticated CockroachDB SQL Shell confirmed
that the prior P9 cleanup had removed both synthetic cases from all four tables
required by the public handler. This failed attempt is preserved unchanged.
