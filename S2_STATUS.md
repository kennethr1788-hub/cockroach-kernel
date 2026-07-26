# S2 Status

- `STATUS`: `CK_S2_RECOVERY_SOAK_GREEN`
- `BLOCKER`: `NONE`
- `LAST_GREEN_GATE`: `CK_P7_RECOVERY_GREEN`
- `TARGET_GATE`: `CK_S2_RECOVERY_SOAK_GREEN`
- `LOCAL_SMOKE`: `R3_GREEN`
- `PRIOR_LIFECYCLE_GUARD`: `REMOTE_TEARDOWN_GREEN`
- `PRIOR_RUNPOD_WORKER`: `btdc8bhvws6cbs`, deleted
- `PRIOR_CAMPAIGN_READY`: `NO`
- `CURRENT_LIFECYCLE_GUARD`: `TEARDOWN_GREEN`
- `REPLACEMENT_POD_ID`: `m6sj0mkio2yc4y`
- `REPLACEMENT_CAMPAIGN_READY`: `YES`
- `TEST_START_UTC`: `2026-07-26T03:25:32Z`
- `TEST_END_UTC`: `2026-07-26T09:25:37Z`
- `MEASURED_TEST_SECONDS`: `21607.859`
- `PRODUCTION_PID`: `EXITED_CLEANLY`
- `P8_STATUS`: `NOT_STARTED`
- `BAND_B_STATUS`: `OPEN`

GLM and Claude returned valid GREEN on preflight packet R3. Attempt 1 returned
the exact approved worker and the transferred archive and 61-file manifest
matched. The executor then compared the extracted binary to a stale hash from
resumed summary data instead of the authoritative receipt and prematurely
deleted the worker. The authoritative hash and remote hash were identical.
Because upload had begun, retry authority had expired. No replacement or second
campaign was authorized under R3. Kenneth has now supplied explicit replacement
authorization bound to SHA-256
`7661fd8de8284cfd69dfcf584f05e6b0584bb736047e626d594a4595047e486e`.
No new worker may be created until the machine-readable hash-custody record and
replacement packet are frozen and GLM plus Claude return GREEN on the same hash.
Those requirements are now satisfied on packet SHA-256
`b072143dd3ba99250b4abccc171a6640efd644819fd46afb383a007ff6a81a53`.
The authorized replacement completed one uninterrupted 21,600-second campaign
with exact 72/24/6 cadence and all assertions passing. All evidence was
hash-verified locally before exact-ID teardown. Provider lookup is 404, S2
inventory is empty, and the detached guard ended `TEARDOWN_GREEN`. Delayed
billing is recorded as a conservative aggregate `CALCULATED_MAXIMUM` of
`$0.525317756`, below the `$2.00` envelope. GLM 5.2, Claude Opus 4.8, and AGY
returned valid GREEN on final packet SHA-256
`46e1135cd285f0023a12b10bd033808c3f628e577f737f905ef2a27789fdfb9f`.
S2 is GREEN. P8 is not started and Band B remains open.
