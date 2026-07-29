# Gate 7 Run 5 A01 Campaign Ready Receipt R1

- `STATUS`: `CAMPAIGN_READY`
- `UTC_VERIFIED`: `2026-07-29T22:27:26Z`
- `LAST_GREEN_GATE`: `GATE7_RUN5_PREFLIGHT_GREEN`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `ORCHESTRATION_COMMIT_AT_BIND`: `08039cee8a30962d9290c55fa0817119ad2c7bc7`
- `PREFLIGHT_PACKET_SHA256`: `2b1af0712b00b373ae62b53365abc7268399bffc56f7196ba3c71801859cbe02`
- `PREFLIGHT_JUDGE_RECEIPT_FILE_SHA256`: `85e3cfab1e5bece561fab9cf3bc5e519cf16697d528a882b9386dffce12af857`
- `SOURCE_BINDINGS_SHA256`: `bda2ba096003c3adf1622b1187c0d6d16c48c4b660af382403fe0268a3e300bc`
- `ATTEMPT_REQUEST_SHA256`: `96cdf9124bdd2bbbd519c3948e6f4643eafe8b114e33169ea6b175ed81dd16a7`
- `RUNPOD_SCHEDULE_FILE_SHA256`: `656738ef2eba7b7e3afa6dba37cac1f6417d6436889e64f1af3ef236961f6f43`
- `POD_ID`: `9jizvy2igfeipj`
- `POD_NAME`: `ck-g7r5-20260729-a01`
- `POD_STATE`: `RUNNING`
- `POD_SHAPE`: `CPU_2_VCPU_4_GIB_GPU_0`
- `POD_IMAGE`: `runpod/base:1.0.2-ubuntu2204`
- `POD_RATE`: `$0.06/hour`
- `POD_VOLUME`: `none`
- `STOP_EPOCH`: `1785386885`
- `DELETE_EPOCH`: `1785388685`
- `LIVE_CAMPAIGN_ID`: `ck-s3-g7r5-a01`
- `MEASURED_HIDDEN_CAMPAIGN_ID`: `ck-g7r5-20260729-a01-measured`
- `HIDDEN_SEED_EXISTS`: `NO`
- `MEASURED_EXECUTION_STARTED`: `NO`

## Direct readiness evidence

- `LIVE_READINESS_STATUS`: `GREEN`
- `LIVE_READINESS_RECEIPT_SHA256`: `e1324bf81bbf67ac9c2d03b27f18577e5ee5e9d1a2b2abada16c9103836b0ac3`
- `LIVE_READINESS_FILE_SHA256`: `07b22445895ccf8f8d2f17da96ea4118b8e12d0319b820f88a61401cb0a4bbf2`
- `AWS_LOGIN_PROVIDER_STATUS`: `PASS`
- `AWS_SESSION_MARGIN_STATE`: `PENDING_POST_EXCHANGE_PROBE`
- `TRANSFER_ARCHIVE_SHA256`: `f793deee3bf0d85aef51cfed522b32d0e7c0353ae0ecceada128dd49d45cde21`
- `PAYLOAD_TREE_FILE_SHA256`: `f5cd59a214b73d74e1104cdb99412c30adfdc0237db6e1eb8a5ef34679e8b83e`
- `TRANSFER_MANIFEST_FILE_SHA256`: `f2697df034b73a815418d60b219316c613705b252f95230a90b290497a09ff5f`
- `REMOTE_PAYLOAD_FILES_VERIFIED`: `98_OF_98`
- `REMOTE_SYMLINKS`: `0`
- `COCKROACH_ARCHIVE_SHA256`: `3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`
- `COCKROACH_BINARY_SHA256`: `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`
- `SECCOMP_ATTESTATION_FILE_SHA256`: `863fa7dd5720d8638c5cc9446837920a4a0037e373769985790488f45959f6be`
- `PROMOTE_CANARY_OBSERVATION_SHA256`: `f20992d772c901706e949e2a445178bd263c5c48b2a7a2da77c2de025469bbd4`
- `INVALID_CANARY_OBSERVATION_SHA256`: `217a02260f556822ccf61e1456bb3d05cdd94d48d88b6bbfdcc252bd35b8bb0b`
- `RUNNER_UID`: `10002`
- `ORACLE_UID`: `10001`
- `RUNNER_ORACLE_ACCESS`: `DENIED`
- `REMOTE_CLOUD_CREDENTIAL_FILES`: `0`
- `REMOTE_HIDDEN_SEED`: `ABSENT`

The extracted archive was compared remotely against every canonical payload
tree row for path, byte count, mode, and SHA-256. The public non-measured
canaries returned `PROMOTE / MAX_PROVEN_PREFIX` and `INVALID /
AGGREGATE_LIMIT_EXCEEDED`. The seccomp canary bound a nonzero runner identity,
zero effective capabilities, `no_new_privs`, filter mode 2, no inherited
sockets, network socket refusal with `EPERM`, and successful child execution.

## Guard bindings

- `LIFECYCLE_GUARD_PID`: `8823`
- `COORDINATOR_PID`: `14405`
- `BRIDGE_PID`: `14408`
- `COORDINATOR_GUARD_PID`: `14637`
- `PROTOCOL_SHA256`: `20bfeac7bf3923394fa193343c904b67bde3efee62561b530fad6ff96d41178c`
- `RESOURCE_ALLOWLIST_SHA256`: `a1993801ce17c4f4a5894720fcfab5cd96715f3f9b0ce03b3919430ea837e3aa`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- `COORDINATOR_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 11`
- `BRIDGE_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 2`
- `COORDINATOR_GUARD_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 6`
- `LIFECYCLE_GUARD_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 15`
- `STOP_MARKER_PRESENT`: `NO`
- `COMPLETION_MARKER_PRESENT`: `NO`

All four bound processes were alive and all four canonical hash chains were
advancing at verification. The credential-free worker has no host cloud
credential; AWS and CockroachDB access remain on the host. The AWS session
margin is intentionally pending until the required post-exchange probe.

`CAMPAIGN_READY` authorizes exactly one Run 5 hidden seed and one measured
campaign in the frozen Track 1, Track 3, start-gate, Track 2, and closeout
order. Any subsequent identity, hash, isolation, semantic, resource, cleanup,
guard, AWS, CockroachDB, or custody failure blocks Gate 7. No replacement
worker or measured rerun is authorized after this boundary.
