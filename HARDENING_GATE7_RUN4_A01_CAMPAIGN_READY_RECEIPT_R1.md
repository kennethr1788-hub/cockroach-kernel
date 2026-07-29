# Gate 7 Run 4 A01 Campaign Ready Receipt R1

- `STATUS`: `CAMPAIGN_READY`
- `UTC_VERIFIED`: `2026-07-29T07:34:10Z`
- `LAST_GREEN_GATE`: `GATE7_RUN4_PREFLIGHT_GREEN`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PREFLIGHT_PACKET_SHA256`: `e7f4d8723b49f422bf31e0f264d49432c5735054ed7d45fdb48666a78e55a7e4`
- `PREFLIGHT_JUDGE_RECEIPT_FILE_SHA256`: `cce335daed0c8ae0eff6c5a832c92b3d2abed2282e857a5700bf94a1ded7309a`
- `SOURCE_BINDINGS_SHA256`: `3e666f8051df7c968fc3ee052e3d33b6303f7ac51036163e745f516e0e1ca8d3`
- `ATTEMPT_REQUEST_SHA256`: `75954e6b2ecda533ea7b884c268e62c790bb33cddf3f7e16be0f7bc410f4ac69`
- `RUNPOD_SCHEDULE_FILE_SHA256`: `487b29c32884913714186b4e576f25d6c9024e543caff4ab3da0aef1c1aee305`
- `POD_ID`: `rqmyhz8zsdprfu`
- `POD_NAME`: `ck-g7r4-20260729-a01`
- `POD_STATE`: `RUNNING`
- `POD_SHAPE`: `CPU_2_VCPU_4_GIB_GPU_0`
- `POD_IMAGE`: `runpod/base:1.0.2-ubuntu2204`
- `POD_RATE`: `$0.06/hour`
- `POD_VOLUME`: `none`
- `STOP_EPOCH`: `1785332677`
- `DELETE_EPOCH`: `1785334477`
- `LIVE_CAMPAIGN_ID`: `ck-s3-g7r4-a01`
- `MEASURED_HIDDEN_CAMPAIGN_ID`: `ck-g7r4-20260729-a01-measured`
- `HIDDEN_SEED_EXISTS`: `NO`
- `MEASURED_EXECUTION_STARTED`: `NO`

## Direct readiness evidence

- `LIVE_READINESS_STATUS`: `GREEN`
- `LIVE_READINESS_RECEIPT_SHA256`: `fda47558fa46ea38ef3c8668805431dab4d48eefe81f29b113014da603f32689`
- `LIVE_READINESS_FILE_SHA256`: `b87255206a4183768cefca7f0b1633c62c9857fa5ab2a6e297964810237e3fd4`
- `AWS_LOGIN_PROVIDER_STATUS`: `PASS`
- `AWS_LOGIN_PROVIDER_RECEIPT_SHA256`: `fb6607345ead1ec49e7aab7dab5a458b5dfb2e8fe16b59219c568a6a6daee8b8`
- `AWS_LOGIN_PROVIDER_FILE_SHA256`: `ce3eea4957b42581b9ec31f0c2aab3d67c1348675d9748cc3297d2a4d3566b41`
- `AWS_SESSION_MARGIN_STATE`: `PENDING_POST_EXCHANGE_PROBE`
- `AWS_SESSION_MARGIN_RECEIPT_SHA256`: `8f9307ae81d73955542026a8ee020ead664cd4f3185351a8aee34fc6fe378cd9`
- `AWS_SESSION_MARGIN_FILE_SHA256`: `827008479c2c455d75a5a860625da81b1d7a0b8e7d4e2bb6f0c1e46c6b531660`
- `TRANSFER_ARCHIVE_SHA256`: `9d7e2ba2e3c75fcadbf9c8567da536ae5fec1decac44a035c622cebd130381ad`
- `COCKROACH_BINARY_SHA256`: `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`
- `SECCOMP_ATTESTATION_FILE_SHA256`: `a5abd879995ca52db0a9840f7a6d296b92bb6604965cc0bccf7f51aab75228a2`
- `PROMOTE_CANARY_OBSERVATION_SHA256`: `d0d76ac6496114b2e34b7f6abf6f959d1994cf5ddfb53e68c7bac3ee253393d0`
- `INVALID_CANARY_OBSERVATION_SHA256`: `e9a76f6009d25d11a7088f360f312141b8f8d5245277817f481073a2fa737ab3`
- `REMOTE_PAYLOAD_FILES_VERIFIED`: `95_OF_95`
- `REMOTE_SYMLINKS`: `0`
- `RUNNER_ORACLE_ACCESS`: `DENIED`
- `REMOTE_CLOUD_CREDENTIAL_FILES`: `0`
- `REMOTE_HIDDEN_ROOTS`: `ABSENT`

The public non-measured canaries returned `PROMOTE / MAX_PROVEN_PREFIX` and
`INVALID / AGGREGATE_LIMIT_EXCEEDED`. The seccomp canary bound nonzero runner
identity, zero effective capabilities, `no_new_privs`, filter mode 2, zero
inherited sockets, socket refusal with `EPERM`, and successful child exec.

## Guard bindings

- `LIFECYCLE_GUARD_PID`: `29337`
- `COORDINATOR_PID`: `39978`
- `BRIDGE_PID`: `38837`
- `COORDINATOR_GUARD_PID`: `40301`
- `PROTOCOL_SHA256`: `20bfeac7bf3923394fa193343c904b67bde3efee62561b530fad6ff96d41178c`
- `RESOURCE_ALLOWLIST_SHA256`: `a1993801ce17c4f4a5894720fcfab5cd96715f3f9b0ce03b3919430ea837e3aa`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- `COORDINATOR_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 43`
- `BRIDGE_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 12`
- `COORDINATOR_GUARD_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 37`
- `LIFECYCLE_GUARD_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 32`
- `STOP_MARKER_PRESENT`: `NO`
- `COMPLETION_MARKER_PRESENT`: `NO`

All four bound processes were alive and all four canonical hash chains were
advancing at verification. The credential-free worker contains no host cloud
credential. AWS and CockroachDB access remain host-only.

The first coordinator launch exited before writing its canonical coordinator
chain because the AWS CLI provider proof required an explicit region binding.
No hidden seed or measured input existed. The corrected invocation added only
the already frozen `us-west-2` environment binding; it did not change code,
payload, semantics, thresholds, or packet hashes. The successful coordinator
uses the append-only `coordinator-evidence-r2` and `custody-r2` roots so the
failed startup remains distinguishable.

`CAMPAIGN_READY` authorizes exactly one Run 4 hidden seed and one measured
campaign in the frozen Track 1, Track 3, start-gate, Track 2, and closeout
order. Any subsequent identity, hash, isolation, semantic, resource, cleanup,
guard, AWS, CockroachDB, or custody failure blocks Gate 7. No replacement
worker or measured rerun is authorized after hidden-seed creation.
