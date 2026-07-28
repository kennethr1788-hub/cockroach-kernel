# Hardening Gate 6 — Billing Receipt R2

- `COST_STATE`: `BILLING_PENDING`
- `POD_ID`: `2sh4lx37f6r73g`
- `PRELAUNCH_COMPUTE_RATE_USD_PER_HOUR`: `0.06`
- `CONTAINER_STORAGE_RATE_USD_PER_GB_MONTH`: `0.10`
- `CONTAINER_DISK_GIB`: `20`
- `TOTAL_ACTIVE_RATE_BOUND_USD_PER_HOUR`: `0.062778`
- `OBSERVED_LIFECYCLE_SECONDS_BOUND`: `341`
- `OBSERVED_LIFECYCLE_COST_BOUND_USD`: `0.0060`
- `CAMPAIGN_AUTHORIZATION_CEILING_USD`: `25.00`
- `BILLING_QUERY_RESULT_COUNT`: `0`
- `BILLING_QUERY_SHA256`: `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- `WORKER_DELETED`: `yes`
- `RUNNING_INVENTORY`: `[]`

The provider had not exposed an exact charge at closeout. The prompt explicitly
allows `BILLING_PENDING` after verified deletion when the prelaunch rate, paid
lifetime, and bounded maximum exposure are recorded. No exact charge is
fabricated. The Gate 6 result is blocked by isolation capability, not billing.
