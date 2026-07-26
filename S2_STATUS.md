# S2 Status

- `STATUS`: `CK_S2_BLOCKED`
- `BLOCKER`: `EXECUTOR_USED_STALE_BINARY_HASH_AFTER_UPLOAD`
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
campaign is authorized without fresh explicit operator authorization.
