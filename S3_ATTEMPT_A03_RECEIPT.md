# S3 Attempt A03 Receipt

- `ATTEMPT`: `3_OF_8`
- `POD_ID`: `g3zio18kbi23nl`
- `POD_NAME`: `ck-s3-20260727-r1-a03`
- `CREATED_UTC`: `2026-07-27T01:53:19.075Z`
- `RESULT`: `PREPRODUCTION_AUTH_BLOCKED`
- `RETURNED_SHAPE`: `2_VCPU_4_GIB_CPU`
- `RETURNED_COMPUTE_RATE_USD_PER_HOUR`: `$0.06`
- `WORKER_ARCHIVE_UPLOADED`: `YES_CREDENTIAL_FREE_HASH_VERIFIED`
- `WORKER_ARCHIVE_SHA256`: `c0f0514c09d63da833361ec34ef2cbc2f0e96c210fca043cbc7d3c33a8e703d4`
- `REMOTE_TREE_FILES_VERIFIED`: `73`
- `HOST_COORDINATOR_STARTED`: `NO`
- `CLOUD_OPERATION_STARTED`: `NO`
- `PRODUCTION_STARTED`: `NO`
- `AWS_AUTH_PROBE`: `SESSION_EXPIRED`
- `STOPPED_AND_DELETED_UTC`: `2026-07-27T02:02:47Z`
- `EXACT_ID_LOOKUP_AFTER_DELETE`: `404_ABSENT`
- `S3_SCOPED_INVENTORY_AFTER_DELETE`: `[]`
- `LIFECYCLE_FINAL_EVENT`: `TEARDOWN_GREEN`
- `LIFECYCLE_LOG_SHA256`: `a0ba29eb1971915ad9ddab9a7e306cde3bc77964d86fd0d143e068a203bdcf43`
- `REMOTE_TREE_VERIFY_SHA256`: `1aba3cbbea192154691cde863b37ca21bbd5f68d739480a53f974580de98239f`
- `CALCULATED_MAXIMUM_USD`: `$0.010100`
- `CUMULATIVE_CALCULATED_MAXIMUM_USD`: `$0.013989`
- `RETRY_CLASSIFICATION`: `LOGIN_GATE_NON_RETRYABLE_UNTIL_HUMAN_STATE_CHANGES`

A03 matched the R10 worker envelope. Its exact-ID lifecycle guard emitted an
advancing, valid hash chain. Two SSH host-key scans were byte-identical, strict
host checking passed, the scanner-clean credential-free worker archive matched
its local and remote SHA-256, and 73 extracted files passed the frozen tree
manifest.

Before starting the host coordinator, the bounded AWS identity probe was run
using the project-local AWS config and login-cache directory. AWS explicitly
reported that the session had expired and required `aws login`. The contract
classifies login as an external human gate. No coordinator, bridge, Lambda,
CockroachDB operation, smoke, or production process started.

A03 was stopped and deleted. Exact-ID lookup returned 404, S3-scoped inventory
was empty, no S3 background process remained, the local attempt evidence secret
scan passed, and the exact-ID guard independently ended at sequence 17 with
`TEARDOWN_GREEN`.
