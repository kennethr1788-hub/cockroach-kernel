# Hardening Gate 6 — Lifecycle Receipt R2

- `POD_ID`: `2sh4lx37f6r73g`
- `GUARD_BOUND_UTC`: `2026-07-28T00:50:23Z`
- `GUARD_TEARDOWN_GREEN_UTC`: `2026-07-28T00:55:30Z`
- `GUARD_DURATION_SECONDS`: `307.5`
- `GUARD_EVENT_COUNT`: `11`
- `GUARD_CHAIN_VALID`: `yes`
- `GUARD_LOG_SHA256`: `13585292459d2afc26b596e3c547f8880cfe1aaee5b06bf6916cc3c29de77636`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- `STOP_RESPONSE_SHA256`: `6550314b1e6f49b9736f829ced32bb1bb96460a456fa448cec8e3659eefcea8b`
- `DELETE_RESPONSE_SHA256`: `c13542fafba249af98f2c537d285bc75407fc72cd199eb5e81acbe356365547a`
- `EXACT_ID_ABSENT`: `yes`
- `CAMPAIGN_RUNNING_INVENTORY`: `[]`
- `CAMPAIGN_ACTIVE_ALL_STATUS_INVENTORY`: `[]`
- `GUARD_SCREEN_PROCESS_REMAINS`: `no`
- `SSH_OR_TRANSFER_PROCESS_REMAINS`: `no`

The detached local guard bound the exact Pod ID and expected attempt name,
emitted an advancing hash chain, observed manual stop/delete, independently
confirmed exact-ID absence plus empty active campaign inventory, emitted
`TEARDOWN_GREEN`, and exited. Provider-native stop and terminate fuses were also
present in the creation request but were not needed.
