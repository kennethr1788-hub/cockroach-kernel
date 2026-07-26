# S2 Status

- `STATUS`: `S2_LOCAL_GREEN_PREFLIGHT_PACKET_PENDING`
- `BLOCKER`: `S2_PREFLIGHT_JUDGES_AND_REMOTE_LIFECYCLE_OPEN`
- `LAST_GREEN_GATE`: `CK_P7_RECOVERY_GREEN`
- `TARGET_GATE`: `CK_S2_RECOVERY_SOAK_GREEN`
- `LOCAL_SMOKE`: `R3_GREEN`
- `LIFECYCLE_GUARD`: `LOCAL_GREEN_REMOTE_NOT_STARTED`
- `RUNPOD_WORKER_CREATED`: `NO`
- `P8_STATUS`: `NOT_STARTED`
- `BAND_B_STATUS`: `OPEN`

No paid S2 resource may be created until the exact transfer bundle, current
price/inventory, worker/deadline/spend contract, and lifecycle proof are frozen
and both required preflight judges return GREEN on the same packet hash.
