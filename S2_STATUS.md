# S2 Status

- `STATUS`: `S2_CAMPAIGN_READY`
- `BLOCKER`: `NONE_BEFORE_PRODUCTION_START`
- `LAST_GREEN_GATE`: `CK_P7_RECOVERY_GREEN`
- `TARGET_GATE`: `CK_S2_RECOVERY_SOAK_GREEN`
- `LOCAL_SMOKE`: `R3_GREEN`
- `PRIOR_LIFECYCLE_GUARD`: `REMOTE_TEARDOWN_GREEN`
- `PRIOR_RUNPOD_WORKER`: `btdc8bhvws6cbs`, deleted
- `PRIOR_CAMPAIGN_READY`: `NO`
- `CURRENT_LIFECYCLE_GUARD`: `BOUND_AND_HEARTBEATING`
- `REPLACEMENT_POD_ID`: `m6sj0mkio2yc4y`
- `REPLACEMENT_CAMPAIGN_READY`: `YES`
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
Those requirements are now satisfied on packet SHA-256
`b072143dd3ba99250b4abccc171a6640efd644819fd46afb383a007ff6a81a53`.
Attempt 1 matched the frozen worker envelope, guard, transfer, manifest,
runtime, and Linux-smoke gates. The next allowed action is the one authorized
21,600-second production start. No retry is authorized after that process
starts.
