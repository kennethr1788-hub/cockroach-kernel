# S2 Production Start Receipt R2

- `CAMPAIGN_ID`: `CK-S2-20260726-ORCHESTRATION-R2`
- `POD_ID`: `m6sj0mkio2yc4y`
- `PRODUCTION_PID`: `1143`
- `START_OBSERVED_UTC`: `2026-07-26T03:25:32Z`
- `OUTPUT_ROOT`: `/workspace/ck-s2-r2-a01-production`
- `STDOUT_PATH`: `/workspace/ck-s2-r2-a01-production.stdout`
- `DURATION_SECONDS`: `21600`
- `CHECKPOINT_SECONDS`: `300`
- `SAFETY_SECONDS`: `900`
- `HOURLY_SECONDS`: `3600`
- `DATABASE_GROWTH_LIMIT_BYTES`: `536870912`
- `EVIDENCE_GROWTH_LIMIT_BYTES`: `134217728`
- `RSS_LIMIT_BYTES`: `2147483648`
- `OPEN_FILES_LIMIT`: `512`
- `RETRY_AUTHORITY`: `EXPIRED`
- `REPLACEMENT_AUTHORITY`: `EXPIRED`
- `SECOND_SIX_HOUR_ATTEMPT`: `FORBIDDEN`

The remote process was observed alive three seconds after launch and its
`/proc` command line matched the immutable production contract. Any failure,
interruption, or incomplete run now blocks S2 and triggers retrieval and
teardown; it cannot be restarted under the current authorization.
