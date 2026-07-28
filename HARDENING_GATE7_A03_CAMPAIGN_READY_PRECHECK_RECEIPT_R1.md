# Hardening Gate 7 A03 Campaign-Ready Precheck Receipt R1

- `STATUS`: `HUMAN_ACTION_REQUIRED`
- `STABLE_REASON_CODE`: `AWS_SESSION_REFRESH_REQUIRED`
- `UTC_RECORDED`: `2026-07-28T21:17:29Z`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PREFLIGHT_PACKET_SHA256`: `4fd89d699dccd0d3e15451fab40435ad2e9b3f7300061ff8791913dc4b7ecf44`
- `POD_ID`: `xvxonfa5ck8wpq`
- `POD_NAME`: `ck-g7r2-20260728-a03`
- `POD_STATE`: `RUNNING`
- `TRANSFER_BYTES`: `144520219`
- `TRANSFER_SHA256`: `b95c6b8e20ec30473676b8f2dbe7e128fdb78bfd33a72105131c51bf45634eb0`
- `REMOTE_PAYLOAD_FILES`: `87_OF_87_EXACT`
- `REMOTE_PAYLOAD_TREE_RECEIPT_SHA256`: `a421697ff2c379474950801ce4d449d5a4b92d0b9bcef7809304f5fafcabb25d`
- `REMOTE_PAYLOAD_TREE_FILE_SHA256`: `8adc4bb8e7abc92aa7b4779a63ecac8edab8ab0b95c1ea4858486ddc8577f8a3`
- `REMOTE_SYMLINKS`: `0`
- `RUNTIME_ARCHIVE_SHA256`: `3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`
- `RUNTIME_BINARY_SHA256`: `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`
- `RUNTIME_VERSION`: `v26.2.3`
- `RUNTIME_PLATFORM`: `linux_amd64`
- `ORACLE_UID`: `999`
- `RUNNER_UID`: `998`
- `EFFECTIVE_CAPABILITIES`: `ZERO_BOTH_IDENTITIES`
- `SECCOMP_CANARY`: `GREEN; SOCKET_DENIED_EPERM; EXEC_PASS`
- `ORACLE_READ_AND_SEARCH_FROM_RUNNER`: `DENIED`
- `CAMPAIGN_ROOT_LIST_FROM_RUNNER`: `DENIED`
- `PUBLIC_PROMOTE_CANARY`: `PROMOTE; MAX_PROVEN_PREFIX; SECCOMP_BOUND`
- `PUBLIC_INVALID_CANARY`: `INVALID; AGGREGATE_LIMIT_EXCEEDED; NO_TERMINAL_MUTATION; SECCOMP_BOUND`
- `HIDDEN_SEED_EXISTS`: `NO`
- `AWS_PROBE_STATUS`: `GREEN_AT_2026-07-28T21:14Z`
- `AWS_SESSION_EXPIRATION`: `2026-07-28T21:29:43Z`
- `AWS_SESSION_MARGIN`: `INSUFFICIENT_FOR_3600_SECOND_TRACK_PLUS_900_SECOND_MARGIN`
- `COCKROACH_READINESS`: `GREEN_READ_ONLY`
- `REMOTE_PRECHECK_RECEIPT_SHA256`: `c0774eee011b733fbd6fd6ba6ba2aa7920cd32bc960dbbf1d3883c4bfc13fb43`
- `REMOTE_PRECHECK_FILE_SHA256`: `704a1b1920ea01944a69539c94515cc18d508d29cb200b1eda3992a80ecd670a`
- `LIVE_READINESS_FILE_SHA256`: `94552bb83b29bb103d3516208e59f471f1e1ff95146f39857f91adccbf962b8a`
- `LIFECYCLE_GUARD_CAPTURE`: `ALIVE_ADVANCING; SEQUENCE_459; EVENT_HASH_068f2b44c4607c6e219437f951e7125b4677f691e5d570a1e4b982d6b09a1882`
- `CAMPAIGN_READY`: `NO`
- `MEASURED_EXECUTION_STARTED`: `NO`

The repaired A03 transfer, extraction, exact tree comparison, runtime binding,
unprivileged identity boundary, inherited seccomp boundary, oracle exclusion,
and two known non-measured public canaries are directly GREEN. The worker
contains no hidden campaign seed and no measured execution has begun.

The current AWS login is authenticated but expires too soon to cover the
separate one-hour live track and the required fifteen-minute post-exchange
margin. The only allowed next action is a fresh project-local `aws login`,
followed by a new read-only expiration/readiness check. Hidden generation,
the measured 84-case runner, and the live track remain forbidden until that
check passes and the coordinator/bridge guard set is alive and advancing.
