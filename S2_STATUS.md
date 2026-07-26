# S2 Status

- `STATUS`: `S2_PREFLIGHT_PACKET_READY_JUDGES_PENDING`
- `BLOCKER`: `S2_PREFLIGHT_JUDGES_PENDING`
- `LAST_GREEN_GATE`: `CK_P7_RECOVERY_GREEN`
- `TARGET_GATE`: `CK_S2_RECOVERY_SOAK_GREEN`
- `LOCAL_SMOKE`: `R3_GREEN`
- `LIFECYCLE_GUARD`: `LOCAL_GREEN_REMOTE_NOT_STARTED`
- `RUNPOD_WORKER_CREATED`: `NO`
- `P8_STATUS`: `NOT_STARTED`
- `BAND_B_STATUS`: `OPEN`

The exact transfer bundle, current inventory, returned-shape acceptance
envelope, deadlines, spend contract, and lifecycle proof are frozen. No paid
S2 resource may be created until GLM and Claude return GREEN on the same exact
preflight packet hash.
