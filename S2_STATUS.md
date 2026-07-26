# S2 Status

- `STATUS`: `S2_REPLACEMENT_PREFLIGHT`
- `BLOCKER`: `REPLACEMENT_PREFLIGHT_OPEN`
- `LAST_GREEN_GATE`: `CK_P7_RECOVERY_GREEN`
- `TARGET_GATE`: `CK_S2_RECOVERY_SOAK_GREEN`
- `LOCAL_SMOKE`: `R3_GREEN`
- `LIFECYCLE_GUARD`: `REMOTE_TEARDOWN_GREEN`
- `RUNPOD_WORKER_CREATED`: `YES_THEN_DELETED`
- `POD_ID`: `btdc8bhvws6cbs`
- `CAMPAIGN_READY`: `NO`
- `TEST_START_UTC`: `NOT_STARTED`
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
