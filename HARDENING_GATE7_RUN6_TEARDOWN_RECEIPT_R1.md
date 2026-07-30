# Hardening Gate 7 Run 6 — Teardown Receipt R1

- `UTC_STOPPED`: `2026-07-30T06:19:24Z`
- `UTC_TEARDOWN_GREEN`: `2026-07-30T06:19:35Z`
- `POD_ID`: `71rhohlh4fb02f`
- `POD_NAME`: `ck-g7r6-20260730-a01`
- `WORKER_SHAPE`: `CPU; 2 vCPU; 4 GiB RAM; 20 GiB disposable disk; zero GPU; zero persistent/network volume`
- `OBSERVED_COMPUTE_RATE`: `$0.06/hour`
- `OBSERVED_ACTIVE_SECONDS`: `6408.486`
- `MATHEMATICAL_COMPUTE_COST`: `$0.1068081`
- `EXACT_PROVIDER_CHARGE`: `NOT_CLAIMED_BY_THIS RECEIPT`
- `EXACT_ID_GET`: `ABSENT`
- `CAMPAIGN_INVENTORY`: `[]`
- `SCREEN_SESSIONS`: `NONE`
- `CAMPAIGN_PROCESSES`: `NONE`
- `STOP_MARKER`: `ABSENT`
- `LIFECYCLE_TERMINAL`: `TEARDOWN_GREEN`
- `LIFECYCLE_EVENT_HASH`: `776ecd035bd47df0289d8a100a64d115898c81b3bd6916b11d563d0223d4712c`
- `LIFECYCLE_LOG_SHA256`: `3204371f816afec901dbad9a5f58cb9fd10233c6ef6fb9d002fc6b861fcd01b1`

The exact worker was stopped and deleted only after all measured evidence was
retrieved and hash-verified. The detached exact-ID guard independently observed
provider absence, reconciled an empty campaign inventory, emitted
`TEARDOWN_GREEN`, and exited. No replacement worker is authorized or needed.

