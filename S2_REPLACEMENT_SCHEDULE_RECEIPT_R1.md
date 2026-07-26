# S2 Replacement Schedule Receipt R1

- `CAMPAIGN_ID`: `CK-S2-20260726-ORCHESTRATION-R2`
- `SCHEDULE_JSON_SHA256`: `dc766db950cd39fe81bc0bd6c39b63be07c72ade677b88f7ae7a489eaaea2e39`
- `ATTEMPT_PREFIX`: `ck-s2-20260726-r2-`
- `FIRST_CREATE_NOT_BEFORE`: `2026-07-26T03:20:00Z`
- `FINAL_CREATE_DEADLINE`: `2026-07-26T04:40:00Z`
- `CAMPAIGN_READY_DEADLINE`: `2026-07-26T04:50:00Z`
- `MAX_ATTEMPTS`: `8`
- `MAX_SIMULTANEOUS_WORKERS`: `1`
- `MAX_SUCCESSFUL_PAID_LIFETIME_SECONDS`: `28800`
- `MAX_ACTIVE_RATE_USD_PER_HOUR`: `0.085`
- `MAX_AGGREGATE_S2_EXPOSURE_USD`: `2.00`

Each attempt has a distinct ten-minute creation slot and exact provider-native
stop/terminate timestamps. Termination is at most eight hours after the start
of its creation slot; stop is ten minutes earlier. A later attempt receives its
own later deadlines and never inherits a stale prior-attempt deadline.

The first creation attempt begins only after GLM and Claude are GREEN over the
same replacement-preflight packet hash. Missed slots are not shifted. If the
active attempt cannot reach `CAMPAIGN_READY` by the frozen deadline, S2 blocks.
