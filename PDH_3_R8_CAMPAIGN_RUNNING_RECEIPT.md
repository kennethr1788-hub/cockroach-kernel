# PDH-3 R8 campaign running receipt

- `STATUS`: `RUNNING_SETUP_NOT_GREEN`
- `UTC_VERIFIED`: `2026-08-01T11:31:44Z`
- `IMPLEMENTATION_COMMIT`: `dd3739485a906618fb7ba12a1d778adaaf64f7aa`
- `CAMPAIGN_ID`: `ck-pdh3-scale-r8-relaunch-r8`
- `POD_ID`: `klu635c1c1js3g`
- `POD_NAME`: `ck-pdh3-scale-r8-relaunch-r8-01`
- `WORKER`: `Secure Cloud NVIDIA L40S`
- `COMPUTE_RATE_USD_HOUR`: `0.99`
- `PACKET_SHA256`: `6c88b03dacb992cf6841fdffc44740921f1b42229cd6004da1ce26b1e1d108f3`
- `BUNDLE_SHA256`: `0ca257a38ddb49a812ba2252459f3ae900b83aa674f2f2883b709ea599258c15`
- `CONCRETE_COMMANDS_SHA256`: `c44cda0147267d1d3675b3472646c137b7a8160540c448641ee1010b72ba5c4b`
- `REMOTE_LAUNCH_RECEIPT_SHA256`: `976c1b962a33b4506c104c937fef6fe40270d3cc85c1be1f978b13671700c734`
- `GUARD_START_RECEIPT_SHA256`: `5edfc75cc7cb2b56dd830d312689dcb80149292a026201381ba7f8af47a0617e`
- `SUPERVISOR_START_RECEIPT_SHA256`: `6ee78a427ede35c632130cd3ca2b0b5b39a45304055581b63a3e58a3d4da410b`
- `PREFLIGHT_JUDGE_RECEIPT_SHA256`: `5cb15c2a9d5eb440a1c601abcdcb650a7ff0d3ef1602195392833f1f7f22a79f`
- `GLM_PREFLIGHT`: `GREEN`
- `AGY_PREFLIGHT`: `GREEN`
- `MEASURED_CLOCK_STARTED`: `false`
- `LIFECYCLE_GUARD`: `RUNNING_DETACHED_PPID_1`
- `SUPERVISOR`: `RUNNING_DETACHED_PPID_1`
- `PROVIDER_STOP_AFTER`: `2026-08-02T15:08:31Z`
- `PROVIDER_TERMINATE_AFTER`: `2026-08-02T15:23:31Z`
- `PERSISTENT_OR_NETWORK_VOLUME`: `none`

## Creation and transfer custody

The first provider creation call returned a transient provider error and no Pod
identifier. The second call returned the exact bound worker. The initial bundle
transfer was incomplete (`15,928,320` of `143,951,988` bytes); extraction
failed closed and no workload started. The same worker then received the full
archive. Remote SHA-256 matched the frozen local archive before a clean
re-extraction and process launch.

## Current boundary

The traced production-shaped controller is running in setup. This receipt does
not claim full-cardinality setup, premeasurement, the 24-hour measured clock,
campaign success, evidence retrieval, or teardown. Any of those claims require
their later raw receipts and final independent review.
