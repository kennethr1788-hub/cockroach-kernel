# Hardening Gate 6 R3 — Provider Lifecycle Fuse Refresh

- `STATUS`: `FROZEN_BEFORE_PREFLIGHT`
- `UTC_RECORDED`: `2026-07-28T01:49:40Z`
- `CAMPAIGN_ID`: `ck-gate6-20260727-run1-r3`
- `SCHEDULE_SHA256`: `c5311d2e31a2d455b66611fc3277b18628d064abcb449468466ead7f8cede425`
- `MAXIMUM_PAID_LIFETIME_SECONDS`: `28800`
- `PROVIDER_STOP_UTC`: `2026-07-28T09:50:00Z`
- `PROVIDER_TERMINATE_UTC`: `2026-07-28T10:00:00Z`
- `MAXIMUM_ACTIVE_RATE_USD_PER_HOUR`: `0.10`
- `MAXIMUM_AGGREGATE_EXPOSURE_USD`: `25.00`

The prior absolute provider fuses no longer left a safe setup, six-hour
measurement, retrieval, and teardown margin. Before freezing the new GLM plus
AGY packet, the schedule was refreshed to preserve provider-native automatic
stop and termination as last-resort controls. This is not a project or phase
completion deadline. It does not extend measured execution beyond 21,600
seconds, permit an idle worker, widen the worker shape, change the candidate,
authorize parallel workers, or relax exact-ID teardown.

If no worker is created early enough to complete setup, the full measurement,
evidence retrieval, and ordinary teardown before these fuses, the schedule must
be refreshed and independently re-reviewed again. It must never be extended
after payload upload or measurement start.
