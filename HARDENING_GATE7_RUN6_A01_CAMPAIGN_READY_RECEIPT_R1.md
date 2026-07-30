# Gate 7 Run 6 A01 Campaign Ready Receipt R1

- `STATUS`: `CAMPAIGN_READY`
- `UTC_VERIFIED`: `2026-07-30T04:47:29Z`
- `LAST_GREEN_GATE`: `GATE7_RUN6_PREFLIGHT_GREEN`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `ORCHESTRATION_COMMIT_AT_BIND`: `03bab25178c46a905a9d4a30a6ad0570bc204885`
- `PREFLIGHT_PACKET_SHA256`: `49deb473ad40c892ee8cf396843e1a20f1486bb81d1af634c3895f22b7c01007`
- `PREFLIGHT_JUDGE_RECEIPT_FILE_SHA256`: `28ff6099498b52f06959dc38326626da41617379e441a3b845937f863ad89eb9`
- `SOURCE_BINDINGS_SHA256`: `44afd2b2d15626642ed22eec525e039ea8f305f243797cd686c12c16b3a52cc9`
- `SOURCE_BINDINGS_FILE_SHA256`: `267f6870295f60a0f3fe68a06cb8a6f0172a70d91f312f7b07c1a23bf7f46332`
- `ATTEMPT_REQUEST_SHA256`: `4b6a9fbd8950ed0546c869035d65c9750caf5e005dcb8d2c52489c908df31b25`
- `RUNPOD_SCHEDULE_FILE_SHA256`: `216d819c89a0b71c977ca968da81acd85bf3240e5f3264be7f3995ea5aad156d`
- `POD_ID`: `71rhohlh4fb02f`
- `POD_NAME`: `ck-g7r6-20260730-a01`
- `POD_STATE`: `RUNNING`
- `POD_SHAPE`: `CPU_2_VCPU_4_GIB_GPU_0`
- `POD_IMAGE`: `runpod/base:1.0.2-ubuntu2204`
- `POD_RATE`: `$0.06/hour`
- `POD_CONTAINER_DISK_GIB`: `20`
- `POD_VOLUME`: `none`
- `STOP_EPOCH`: `1785409316`
- `DELETE_EPOCH`: `1785411116`
- `COORDINATOR_DEADLINE_EPOCH`: `1785408116`
- `FINAL_CLOUD_EXCHANGE_DEADLINE_EPOCH`: `1785406316`
- `LIVE_CAMPAIGN_ID`: `ck-s3-g7r6-a01`
- `MEASURED_HIDDEN_CAMPAIGN_ID`: `ck-g7r6-20260730-a01-measured`
- `HIDDEN_SEED_EXISTS`: `NO`
- `MEASURED_EXECUTION_STARTED`: `NO`
- `CREATION_RETRIES_ENDED`: `YES_AT_UPLOAD`
- `REPLACEMENT_AUTHORITY_REMAINING`: `NONE`

## Direct readiness evidence

- `LIVE_READINESS_STATUS`: `GREEN`
- `LIVE_READINESS_RECEIPT_SHA256`: `acff3264e24242e42194cd0f6cca472dbfcbd7483514b6ea01302633fb7d5d26`
- `LIVE_READINESS_FILE_SHA256`: `a80d79d32234e1f589c00015e990d1d87463309d69a4dfc22332297936801050`
- `AWS_LOGIN_PROVIDER_STATUS`: `PASS`
- `AWS_SESSION_MARGIN_STATE`: `PENDING_POST_EXCHANGE_PROBE`
- `COCKROACH_READINESS_STATUS`: `PASS`
- `TRANSFER_ARCHIVE_SHA256`: `77568eea6f33ec574a0a60c969c8a176f3f0c3024e9e5809ccf67438ec3e2890`
- `TRANSFER_ARCHIVE_BYTES`: `144548380`
- `PAYLOAD_TREE_FILE_SHA256`: `fefc5ddf72888cd4ea111f264dd0dd46841d58a586ea05f92b6f40208b26129d`
- `TRANSFER_MANIFEST_FILE_SHA256`: `6a332037fa0447014a91d73656df8e0fd1ef43b822a16872940c0868bc6eaf77`
- `REMOTE_PAYLOAD_FILES_VERIFIED`: `98_OF_98`
- `REMOTE_PAYLOAD_ROWS_SHA256`: `62b6e18088f128fcf3e53f018eab1ac435620f1a0ffd64ad5b89718d19a38136`
- `REMOTE_SYMLINKS`: `0`
- `COCKROACH_ARCHIVE_SHA256`: `3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`
- `COCKROACH_BINARY_SHA256`: `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`
- `SECCOMP_ATTESTATION_SHA256`: `19363d7a70e277d5c288f51c6a46f4e26beeaa904f1309aa19bb493da250d9b9`
- `SECCOMP_ATTESTATION_FILE_SHA256`: `a5abd879995ca52db0a9840f7a6d296b92bb6604965cc0bccf7f51aab75228a2`
- `PROMOTE_CANARY_OBSERVATION_SHA256`: `39a713206fa45be81e2e89b45436632b0891969bec73ffe5a9199be3a49cd48f`
- `INVALID_CANARY_OBSERVATION_SHA256`: `6a1a69f1cd8acc0ecb9147ba63b46dadc42999a356b9ecdf2f412aebaa5e5c60`
- `RUNNER_UID`: `998`
- `ORACLE_UID`: `999`
- `RUNNER_ORACLE_ACCESS`: `DENIED`
- `REMOTE_CLOUD_CREDENTIAL_FILES`: `0`
- `REMOTE_HIDDEN_SEED`: `ABSENT`
- `REMOTE_BRIDGE_FILES_AT_BIND`: `0`
- `SSH_KNOWN_HOSTS_SHA256`: `e97a74f48d9b54b3ae98f3f4ca817a47ba4eea88430a9e28221321298fe89946`

The extracted archive was compared remotely against every canonical payload
tree row for path, byte count, mode, and SHA-256. The public non-measured
canaries returned `PROMOTE / MAX_PROVEN_PREFIX` and `INVALID /
AGGREGATE_LIMIT_EXCEEDED`. The seccomp canary bound UID/EUID `998`, zero
effective capabilities, `no_new_privs=1`, filter mode 2, no inherited sockets,
network socket refusal with `EPERM`, and successful child execution. The
credential-free worker contains no host cloud credential; AWS and CockroachDB
access remain on the host.

## Guard bindings

- `LIFECYCLE_GUARD_PID`: `53394`
- `COORDINATOR_PID`: `56006`
- `BRIDGE_PID`: `56171`
- `COORDINATOR_GUARD_PID`: `56316`
- `PROTOCOL_SHA256`: `20bfeac7bf3923394fa193343c904b67bde3efee62561b530fad6ff96d41178c`
- `RESOURCE_ALLOWLIST_SHA256`: `a1993801ce17c4f4a5894720fcfab5cd96715f3f9b0ce03b3919430ea837e3aa`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- `LIFECYCLE_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 92`
- `COORDINATOR_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 52`
- `BRIDGE_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 30`
- `COORDINATOR_GUARD_LAST_EVENT_AT_VERIFICATION`: `HEARTBEAT sequence 21`
- `STOP_MARKER_PRESENT`: `NO`
- `COMPLETION_MARKER_PRESENT`: `NO`

All four bound processes were alive and all four canonical hash chains were
advancing at verification. The AWS session margin is intentionally pending
until the required post-exchange probe.

## Preserved pre-hidden control-plane events

The following events happened before hidden-input generation and before any
measured execution. They are retained and are not counted as campaign results:

1. A remote setup command failed because shell quoting left an `awk` positional
   parameter unbound; the command was corrected before extraction.
2. The isolated runner initially could not traverse the generated outer root
   at mode `0700`; only that generated outer root was changed to `0755`, while
   the oracle root remained `0700` and runner access remained denied.
3. The local macOS `screen` build rejected the unsupported `-Logfile` option;
   no process or hidden state was created by that attempt.
4. A bounded bridge startup probe remained healthy for seven seconds and was
   terminated by the local timeout before measurement. Its three-record chain
   is preserved at SHA-256
   `1960bd8ad5fee4fe5693412c035403d40216c8bfad4a29d029fb35ac22209e7d`.

`CAMPAIGN_READY` authorizes exactly one new Run 6 hidden seed and one measured
campaign in the frozen Track 1, Track 3, start-gate, Track 2, and closeout
order. Run 5 remains immutable failed evidence and none of its revealed hidden
inputs may be read, tuned against, or reused. Any subsequent identity, hash,
isolation, semantic, resource, cleanup, guard, AWS, CockroachDB, or custody
failure blocks Gate 7. No replacement worker or measured rerun is authorized
after this boundary.
