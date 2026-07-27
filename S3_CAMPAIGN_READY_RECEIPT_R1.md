# S3 Campaign Ready Receipt R1

- `STATUS`: `S3_CAMPAIGN_READY`
- `ATTEMPT`: `A04_OF_8`
- `POD_ID`: `he6sw2nz0w3jtk`
- `POD_NAME`: `ck-s3-20260727-r1-a04`
- `SHAPE`: `2_VCPU_4_GIB_CPU`
- `COMPUTE_RATE_USD_PER_HOUR`: `$0.06`
- `TOTAL_ACTIVE_RATE_MAX_USD_PER_HOUR`: `$0.064`
- `IMAGE`: `runpod/base:1.0.2-ubuntu2204`
- `CONTAINER_DISK_GIB`: `20`
- `GPU_COUNT`: `0`
- `VOLUME_GIB`: `0`
- `PROVIDER_STOP_SAFETY_FUSE`: `2026-07-27T16:35:00Z`
- `PROVIDER_TERMINATE_SAFETY_FUSE`: `2026-07-27T16:45:00Z`
- `CREATE_RESPONSE_SHA256`: `69ba433f5e73cb5c2c496d7b4466a411a0010b79eab738ec5012e88e62c161dd`
- `WORKER_BUNDLE_SHA256`: `c0f0514c09d63da833361ec34ef2cbc2f0e96c210fca043cbc7d3c33a8e703d4`
- `REMOTE_TREE_VERIFY_SHA256`: `1aba3cbbea192154691cde863b37ca21bbd5f68d739480a53f974580de98239f`
- `REMOTE_MANIFEST_FILES`: `73`
- `HOSTKEY_SCANS`: `BYTE_IDENTICAL_ED25519`
- `HOSTKEY_SCAN_SHA256`: `ecccf4f37006f9d664fe7780ab0596e2687ed15ca878573727c2c148418c89c9`
- `STRICT_SSH`: `GREEN`
- `RUNTIME_ARCHIVE_SHA256`: `3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`
- `RUNTIME_BINARY_SHA256`: `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`
- `RUNTIME_VERSION`: `v26.2.3`
- `RUNTIME_PLATFORM`: `LINUX_AMD64_UBUNTU_22_04`
- `REMOTE_CREDENTIAL_MATERIAL_SCAN`: `ZERO_FINDINGS`
- `LIVE_SMOKE`: `GREEN`
- `LIVE_SMOKE_CLOUD_EXCHANGES`: `3`
- `LIVE_SMOKE_COCKROACH_OPERATIONS`: `27`
- `LIVE_SMOKE_CHECKPOINTS`: `6`
- `LIVE_SMOKE_SAFETY_REPLAYS`: `4`
- `OFFLINE_SMOKE`: `EXPECTED_REFUSAL`
- `OFFLINE_SMOKE_CLOUD_EXCHANGES`: `0`
- `SMOKE_EVIDENCE_SHA256`: `62a6236dd90a848deeb1a01aad23b2b54964f41ae10ac1f50354c53b9f7812d7`
- `LIFECYCLE_GUARD`: `ALIVE_ADVANCING`
- `HOST_COORDINATOR`: `ALIVE_ADVANCING`
- `REMOTE_BRIDGE`: `ALIVE_ADVANCING`
- `COORDINATOR_GUARD`: `ALIVE_ADVANCING`
- `AWS_PROJECT_LOGIN`: `VALID_IMMEDIATELY_BEFORE_READY_FREEZE`
- `RUNPOD_S3_ACTIVE_COUNT`: `1_EXACT_A04`
- `PRIOR_S3_ACTIVE_RESOURCES`: `NONE`
- `PRODUCTION_ATTEMPTS_CONSUMED`: `0`
- `PROJECTED_AGGREGATE_MAXIMUM_USD`: `$1.189989`
- `STOP_MARKER`: `ABSENT`
- `UTC_READY`: `2026-07-27T03:39:08Z`

A04 satisfies the frozen campaign-ready gate. The credential-free worker
archive and all manifest entries match locally and remotely; CockroachDB archive
and binary hashes match the authoritative Linux runtime; strict first-use SSH
pinning passes; the real live coordinator smoke completes three bounded
Lambda/Cockroach exchanges; the separate coordinator-absent smoke returns the
expected refusal with zero cloud calls; and all four detached production guards
are alive with advancing canonical hash chains.

The broad text scan matched only the literal word `keychain` inside the
extracted CockroachDB `THIRD-PARTY-NOTICES.txt`. A narrower credential-material
scan for AWS access-key forms, session/secret environment names, OAuth token
field names, private-key markers, the local operator path, Cockroach Cloud host
names, and `PGPASSWORD` returned zero findings. No credential or cloud client
was transferred to the worker.

The one authorized 43,200-second production attempt may start only from fresh
production roots with the exact frozen command. Creating the production start
receipt consumes retry authority permanently; no replacement production worker
is authorized after that point.
