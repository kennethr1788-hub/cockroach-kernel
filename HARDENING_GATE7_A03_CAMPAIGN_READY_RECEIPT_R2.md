# Gate 7 A03 Campaign Ready Receipt R2

- `STATUS`: `CAMPAIGN_READY`
- `UTC_VERIFIED`: `2026-07-28T22:03:48Z`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `EXPANDED_PREFLIGHT_PACKET_SHA256`: `4fd89d699dccd0d3e15451fab40435ad2e9b3f7300061ff8791913dc4b7ecf44`
- `AWS_REFRESH_AMENDMENT_PACKET_SHA256`: `e3414df6b9df3a8e1126d494c8f542460cb38cb51386ac8ec9edfca7dd96c68d`
- `AWS_REFRESH_AMENDMENT_JUDGES`: `GLM_5_2_GREEN; AGY_GEMINI_3_1_PRO_HIGH_GREEN; SAME_HASH; RECUSAL_CLEAR`
- `POD_ID`: `xvxonfa5ck8wpq`
- `POD_NAME`: `ck-g7r2-20260728-a03`
- `POD_SHAPE`: `CPU_2_VCPU_4_GIB_GPU_0`
- `POD_IMAGE`: `runpod/base:1.0.2-ubuntu2204`
- `POD_RATE`: `$0.06/hour`
- `POD_VOLUME`: `none`
- `STOP_EPOCH`: `1785290397`
- `DELETE_EPOCH`: `1785292197`
- `SECONDS_TO_STOP_AT_VERIFICATION`: `14169`
- `SECONDS_TO_DELETE_AT_VERIFICATION`: `15969`
- `LIVE_CAMPAIGN_ID`: `ck-s3-g7r2-a03`
- `MEASURED_HIDDEN_CAMPAIGN_ID`: `ck-g7r2-20260728-a03-measured`
- `HIDDEN_SEED_EXISTS`: `NO`
- `MEASURED_EXECUTION_STARTED`: `NO`

## Direct readiness evidence

- `LIVE_READINESS_STATUS`: `GREEN`
- `LIVE_READINESS_RECEIPT_SHA256`: `9b8b1a33efea502eae525f96e2fcdeb78ff8e0bd92108f2f21bfa90d9dc990a9`
- `LIVE_READINESS_FILE_SHA256`: `16bf5932d739993c783d699c013a584ea4c2044c583847a2793d8423f3fc4d5a`
- `AWS_LOGIN_PROVIDER_STATUS`: `PASS`
- `AWS_LOGIN_PROVIDER_RECEIPT_SHA256`: `454f42cefaa56f533217564e3a7a0792733539e829d93dd8d5c1feb18c10fb1d`
- `AWS_LOGIN_PROVIDER_FILE_SHA256`: `4edfe6183219dc5d501bbaf11548e06cd4fbfe776ba64c4f7e4b07075425f81e`
- `AWS_SESSION_MARGIN_STATE`: `PENDING_POST_EXCHANGE_PROBE`
- `AWS_SESSION_MARGIN_RECEIPT_SHA256`: `463fe973f707d4db56afdc10e448a7e784b7cfd317ce654e85fbdb6513740779`
- `AWS_SESSION_MARGIN_FILE_SHA256`: `874ccc8a2aff7bd3d2d92e195f4ecf6918e93fc6777d8fda2ab25de8189d7634`
- `REMOTE_PRECHECK_RECEIPT_SHA256`: `c0774eee011b733fbd6fd6ba6ba2aa7920cd32bc960dbbf1d3883c4bfc13fb43`
- `REMOTE_PRECHECK_FILE_SHA256`: `704a1b1920ea01944a69539c94515cc18d508d29cb200b1eda3992a80ecd670a`
- `SECCOMP_CANARY_ATTESTATION_SHA256`: `19363d7a70e277d5c288f51c6a46f4e26beeaa904f1309aa19bb493da250d9b9`
- `TRANSFER_ARCHIVE_SHA256`: `b95c6b8e20ec30473676b8f2dbe7e128fdb78bfd33a72105131c51bf45634eb0`
- `REMOTE_PAYLOAD_TREE_RECEIPT_SHA256`: `a421697ff2c379474950801ce4d449d5a4b92d0b9bcef7809304f5fafcabb25d`
- `COCKROACH_BINARY_SHA256`: `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`

## Guard bindings

- `LIFECYCLE_GUARD_PID`: `34224`
- `COORDINATOR_PID`: `65582`
- `BRIDGE_PID`: `65583`
- `COORDINATOR_GUARD_PID`: `65729`
- `PROTOCOL_SHA256`: `20bfeac7bf3923394fa193343c904b67bde3efee62561b530fad6ff96d41178c`
- `RESOURCE_ALLOWLIST_SHA256`: `a1993801ce17c4f4a5894720fcfab5cd96715f3f9b0ce03b3919430ea837e3aa`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- `COORDINATOR_LAST_EVENT`: `HEARTBEAT sequence 10`
- `BRIDGE_LAST_EVENT`: `HEARTBEAT sequence 2`
- `COORDINATOR_GUARD_LAST_EVENT`: `HEARTBEAT sequence 6`
- `LIFECYCLE_GUARD_LAST_EVENT`: `HEARTBEAT sequence 655`

All four bound processes were alive when this receipt was frozen, all four
hash chains were advancing, and no stop marker or completion marker existed.
The credential-free worker contains no cloud credential. The host retains the
project-local AWS login and CockroachDB configuration.

The prior remote precheck correctly remained conditional on the then-missing
human AWS refresh. That human action is now complete and is superseded only for
campaign-readiness by the fresh live readiness receipt and independently GREEN
AWS-login refresh amendment above. The required post-exchange 900-second STS
probe remains an execution-time Gate 7 completion condition; it is not falsely
claimed complete here.

`CAMPAIGN_READY` authorizes one hidden seed generation and one measured
campaign under the frozen 84-row semantics. Any subsequent guard, hash,
identity, isolation, call-ceiling, threshold, or residue failure terminates the
campaign and preserves a blocked result; no measured rerun is authorized.
