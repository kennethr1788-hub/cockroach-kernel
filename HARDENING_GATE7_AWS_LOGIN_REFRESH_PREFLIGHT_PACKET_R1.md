# Hardening Gate 7 AWS Login Refresh Preflight Packet R1
## Decision requested
GLM and AGY are independent, non-authoring, tool-disabled judges. Review only whether this narrow host-orchestration correction may replace the false static access-credential expiry check before A03 becomes CAMPAIGN_READY. Do not write code, direct implementation, predict the campaign outcome, or treat this preflight as measured evidence.
Return GREEN only if the correction preserves the frozen product candidate, 84-case semantics, live-track thresholds, credential separation, and fail-closed behavior, and if the real post-exchange 900-second provider probe is at least as strong as the intended session-margin gate.
## Bindings
- `PACKET_VERSION`: `gate7-aws-login-refresh-preflight-r1`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `ORCHESTRATION_HEAD`: `e970b4d76b7d9801a0d43ba2e5ed10450cb01d22`
- `PRIOR_PACKET_SHA256`: `4fd89d699dccd0d3e15451fab40435ad2e9b3f7300061ff8791913dc4b7ecf44`
- `PRIOR_JUDGES`: `GLM_5_2_GREEN; AGY_GEMINI_3_1_PRO_HIGH_GREEN; SAME_HASH; RECUSAL_CLEAR`
- `REMOTE_BUNDLE_SHA256`: `b95c6b8e20ec30473676b8f2dbe7e128fdb78bfd33a72105131c51bf45634eb0`
- `REMOTE_BUNDLE_FILES`: `87_OF_87_EXACT`
- `POD_ID`: `xvxonfa5ck8wpq`
- `HIDDEN_SEED_EXISTS`: `NO`
- `MEASURED_EXECUTION_STARTED`: `NO`
- `AWS_PRIMARY_DOC`: `https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html`
- `AWS_SDK_DOC`: `https://docs.aws.amazon.com/sdkref/latest/guide/feature-login-credentials.html`
## Candidate path classification
The candidate commit remains immutable. Paths changed after it include prior harness/evidence work. This amendment changes only the four `s3-soak` host orchestration/test files embedded below; the already accepted remote payload contains only `s3-soak/protocol.py` and `s3-soak/worker.py`, neither changed.
```text
BLACK_BOX_R4_PUBLIC_CANARY_R1_STATUS.md
BLACK_BOX_R4_PUBLIC_CANARY_R2_EVIDENCE_MANIFEST.md
BLACK_BOX_R4_PUBLIC_CANARY_R2_GLM_AUDIT_ATTEMPT1_INVALID.md
BLACK_BOX_R4_PUBLIC_CANARY_R2_GLM_AUDIT_ATTEMPT2_INVALID.md
BLACK_BOX_R4_PUBLIC_CANARY_R2_GLM_AUDIT_FINAL.md
BLACK_BOX_R4_PUBLIC_CANARY_R2_JUDGE_PACKET.md
BLACK_BOX_R4_PUBLIC_CANARY_R2_REPORT.md
FRESH_CONTEXT_BLACK_BOX_GLM_AUDIT_INSTRUCTIONS_R3.md
FRESH_CONTEXT_BLACK_BOX_GLM_AUDIT_RAW_R3.txt
FRESH_CONTEXT_BLACK_BOX_GLM_AUDIT_RECEIPT_R3.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_CAMPAIGN_AUTHORIZATION_R1.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_CAMPAIGN_AUTHORIZATION_R2.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_CAMPAIGN_EVIDENCE_MANIFEST_R3.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_CAMPAIGN_RAW_R3.txt
FRESH_CONTEXT_BLACK_BOX_HIDDEN_CAMPAIGN_REPORT_R3.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_INSTRUCTIONS_R1.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_INSTRUCTIONS_R2.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_INSTRUCTIONS_R3.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_RAW_R1.txt
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_RAW_R2.txt
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_RAW_R3.txt
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_RAW_R3_ATTEMPT1.txt
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_RECEIPT_R1.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_RECEIPT_R2.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_RECEIPT_R3.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_GLM_RECEIPT_R3_ATTEMPT1.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_PACKET_R1.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_PACKET_R2.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_EXECUTION_PACKET_R3.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_FINAL_GLM_INSTRUCTIONS_R3.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_FINAL_GLM_RAW_R3.txt
FRESH_CONTEXT_BLACK_BOX_HIDDEN_FINAL_GLM_RECEIPT_R3.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_FINAL_PACKET_R3.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_ROUTE_AMENDMENT_R2.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_ROUTE_AUTHORIZATION_REQUIRED_R2.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_ROUTE_PREFLIGHT_R1.md
FRESH_CONTEXT_BLACK_BOX_HIDDEN_ROUTE_PREFLIGHT_R2.md
FRESH_CONTEXT_BLACK_BOX_PLAN_R3.md
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_EGRESS_BLOCKER_R3.md
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_GLM_INSTRUCTIONS_R3.md
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_GLM_INSTRUCTIONS_R3B.md
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_GLM_RAW_R3B.txt
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_GLM_RECEIPT_R3B.md
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_PACKET_R3.md
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_PACKET_R3B.md
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_RAW_R3.json
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_REPORT_R3.md
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_SCAN_R3.txt
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_STATUS_R3.md
FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_TEST_R3.txt
FRESH_CONTEXT_BLACK_BOX_R4_HIDDEN_EVIDENCE_MANIFEST_R1.md
FRESH_CONTEXT_BLACK_BOX_R4_HIDDEN_FINAL_GLM_RECEIPT_R1.md
FRESH_CONTEXT_BLACK_BOX_R4_HIDDEN_FINAL_JUDGE_PACKET_R1.md
FRESH_CONTEXT_BLACK_BOX_R4_HIDDEN_PLAN_R1.md
FRESH_CONTEXT_BLACK_BOX_R4_HIDDEN_PREFLIGHT_GLM_RECEIPT_R1.md
FRESH_CONTEXT_BLACK_BOX_R4_HIDDEN_PREFLIGHT_PACKET_R1.md
FRESH_CONTEXT_BLACK_BOX_R4_HIDDEN_REPORT_R1.md
FRESH_CONTEXT_BLACK_BOX_R4_PUBLIC_CANARY_PLAN.md
FRESH_CONTEXT_BLACK_BOX_R4_PUBLIC_CANARY_PLAN_R2.md
FRESH_CONTEXT_BLACK_BOX_SURFACE_PROBE_R3.json
HARDENING_GATE7_A03_CAMPAIGN_READY_PRECHECK_RECEIPT_R1.md
HARDENING_GATE7_ATTEMPT_A01_RECEIPT_R1.md
HARDENING_GATE7_ATTEMPT_A01_REQUEST_R1.json
HARDENING_GATE7_ATTEMPT_A02_RECEIPT_R1.md
HARDENING_GATE7_ATTEMPT_A02_REQUEST_R1.json
HARDENING_GATE7_ATTEMPT_A03_REQUEST_R1.json
HARDENING_GATE7_AWS_LOGIN_REFRESH_AMENDMENT_R1.md
HARDENING_GATE7_AWS_LOGIN_REFRESH_CLOUD_ADAPTER_REVIEW_R1.md
HARDENING_GATE7_AWS_LOGIN_REFRESH_PREFLIGHT_PACKET_R1.md
HARDENING_GATE7_AWS_LOGIN_REFRESH_TEST_RECEIPT_R1.md
HARDENING_GATE7_BUNDLE_REPAIR_AUTHORIZATION_RECEIPT_R1.md
HARDENING_GATE7_CANDIDATE_CONTINUITY_RECEIPT_R1.md
HARDENING_GATE7_CONTINUITY_AGY_RAW_R1.txt
HARDENING_GATE7_CONTINUITY_GLM_RAW_R1.txt
HARDENING_GATE7_CONTINUITY_JUDGE_RECEIPT_R1.md
HARDENING_GATE7_CONTINUITY_PACKET_R1.md
HARDENING_GATE7_CONTINUITY_TESTS_RAW_R1.txt
HARDENING_GATE7_EXPANDED_EXECUTION_WIRING_R1.md
HARDENING_GATE7_EXPANDED_LOCAL_PREFLIGHT_RECEIPT_R1.json
HARDENING_GATE7_EXPANDED_LOCAL_PREFLIGHT_RECEIPT_R2.json
HARDENING_GATE7_EXPANDED_PREFLIGHT_JUDGE_RECEIPT_R1.md
HARDENING_GATE7_EXPANDED_PREFLIGHT_PACKET_R1.md
HARDENING_GATE7_EXPANDED_PREFLIGHT_PACKET_R2.md
HARDENING_GATE7_EXPANDED_RUNPOD_SCHEDULE_R1.json
HARDENING_GATE7_EXPANDED_SOURCE_BINDINGS_R1.json
HARDENING_GATE7_EXPANDED_SOURCE_BINDINGS_R2.json
HARDENING_GATE7_EXPANDED_STATUS_R1.md
HARDENING_GATE7_EXPANDED_THRESHOLDS_R1.json
HARDENING_GATE7_LIVE_READINESS_RECEIPT_R1.json
HARDENING_GATE7_REPAIRED_PREFLIGHT_JUDGE_RECEIPT_R2.md
RESUME_STATE.md
SCENARIO_SURFACE_R3_CANDIDATE_RECEIPT.md
SCENARIO_SURFACE_R3_CLEAN_CLONE_RAW.txt
SCENARIO_SURFACE_R3_CLEAN_CLONE_REPORT.md
evidence/black-box-r3/bb-r3-a359b8048a36/FINAL_SUMMARY.json
evidence/black-box-r3/bb-r3-a359b8048a36/SEED_COMMITMENT.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-01.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-02.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-03.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-04.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-05.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-06.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-07.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-08.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-09.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-10.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-11.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-12.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-13.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-14.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-15.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-16.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-17.json
evidence/black-box-r3/bb-r3-a359b8048a36/run-18.json
evidence/black-box-r4-hidden/R4_EXECUTION_LOCK.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/CAMPAIGN_CLOSEOUT.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/FINAL_SUMMARY.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/SEED_COMMITMENT.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/SEED_REVEAL.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-01.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-02.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-03.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-04.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-05.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-06.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-07.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-08.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-09.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-10.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-11.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-12.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-13.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-14.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-15.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-16.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-17.json
evidence/black-box-r4-hidden/bb-r4-0d77b0fc92ea/run-18.json
evidence/black-box-r4-public-canary/r4-public-canary-r1/public-01.json
evidence/black-box-r4-public-canary/r4-public-canary-r1/public-02.json
evidence/black-box-r4-public-canary/r4-public-canary-r2/FINAL_SUMMARY.json
evidence/black-box-r4-public-canary/r4-public-canary-r2/public-01.json
evidence/black-box-r4-public-canary/r4-public-canary-r2/public-02.json
evidence/black-box-r4-public-canary/r4-public-canary-r2/public-03.json
fresh-context-black-box/build_hidden_execution_packet.py
fresh-context-black-box/build_hidden_final_packet.py
fresh-context-black-box/r3_actor.sb
fresh-context-black-box/r3_actor_response.schema.json
fresh-context-black-box/r3_canary.py
fresh-context-black-box/r3_hidden_campaign.py
fresh-context-black-box/r3_preflight.py
fresh-context-black-box/r4_action_response_r2.schema.json
fresh-context-black-box/r4_hidden_actor_response.schema.json
fresh-context-black-box/r4_hidden_campaign.py
fresh-context-black-box/r4_public_canary.py
fresh-context-black-box/r4_public_canary_r2.py
fresh-context-black-box/r4_typed_actor_response.schema.json
fresh-context-black-box/test_r3_hidden_campaign.py
fresh-context-black-box/test_r3_preflight.py
fresh-context-black-box/test_r4_hidden_campaign.py
fresh-context-black-box/test_r4_public_canary.py
fresh-context-black-box/test_r4_public_canary_r2.py
hardening-gate7/build_aws_refresh_amendment_packet.py
hardening-gate7/build_expanded_bundle.py
hardening-gate7/build_expanded_preflight_packet.py
hardening-gate7/expanded_contract.py
hardening-gate7/freeze_expanded_preflight.py
hardening-gate7/generate_expanded_inputs.py
hardening-gate7/live_bulk_controller.py
hardening-gate7/preflight_live_check.py
hardening-gate7/prepare_hidden_campaign.py
hardening-gate7/run_expanded_campaign.py
hardening-gate7/run_expanded_case.py
hardening-gate7/score_expanded_campaign.py
hardening-gate7/surface_cases.py
hardening-gate7/test_expanded_gate7.py
s3-soak/cloud_adapter.py
s3-soak/hardening.py
s3-soak/host_coordinator.py
s3-soak/test_hardening.py
```
## Required judge output
GLM returns exactly one JSON object with keys: `lane`, `model_identity`, `packet_sha256`, `verdict` (`GREEN|NOT_GREEN|RECUSAL_REQUIRED`), `recusal_clear` (boolean), `blocking_findings` (array), `non_blocking_risks` (array), and `summary`. AGY returns its wrapper-native validated fields: `PACKET_SHA256`, `AGY_VERDICT`, `BLOCKERS`, `NON_BLOCKING_RISKS`, `EVIDENCE_GAPS`, `RECUSAL_CHECK`, and `REQUIRED_RERUNS`. The out-of-band packet SHA-256 supplied by the caller must be copied exactly. Any implementation direction, tool request, or identity adoption invalidates the lane.

## FILE: HARDENING_GATE7_AWS_LOGIN_REFRESH_AMENDMENT_R1.md
- `BYTES`: `3546`
- `SHA256`: `e850eb88c2f10c587de340a7379ed8b3c165641f197930e0de17e06010f67d35`
```text
# Hardening Gate 7 AWS Login Refresh Amendment R1

## Classification

- `SCOPE`: `GATE7_HOST_ORCHESTRATION_ONLY`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PRODUCT_MUTATION`: `NO`
- `REMOTE_PAYLOAD_MUTATION`: `NO`
- `BENCHMARK_SEMANTICS_MUTATION`: `NO`
- `THRESHOLD_RELAXATION`: `NO`
- `MEASURED_EXECUTION_STARTED`: `NO`
- `HIDDEN_SEED_EXISTS`: `NO`
- `PRIOR_PACKET_SHA256`: `4fd89d699dccd0d3e15451fab40435ad2e9b3f7300061ff8791913dc4b7ecf44`
- `AUTHORITY`: `The Gate 7 authorization permits a provider/lifecycle orchestration correction before hidden generation when it leaves product and benchmark behavior unchanged and receives fresh same-hash GLM/AGY GREEN.`

## Defect

The static session gate treated the expiration of one AWS access credential as
the expiration of the entire `aws login` session. The installed AWS CLI issues
15-minute access credentials but automatically refreshes them while the login
refresh token remains valid. Repeated human login cannot make one rotating
access credential span the one-hour track, so the old check tests the wrong
object.

Primary AWS documentation:

- `https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html`
- `https://docs.aws.amazon.com/sdkref/latest/guide/feature-login-credentials.html`

The installed `aws login help` output independently states that temporary
credentials are refreshed automatically while the refresh token remains valid.
No credential or token bytes were placed in evidence or sent to any judge.

## Narrow correction

The host coordinator retains the legacy static-expiration mode and adds one
explicit `--aws-login-auto-refresh` mode. That mode:

1. proves the configured `ck-s3` provider type is `login`;
2. proves the installed AWS CLI advertises automatic refresh;
3. records only hashes and stable metadata, never credential bytes;
4. makes no future-expiration claim at campaign start;
5. runs all twelve frozen Lambda/Cockroach exchanges under the existing strict
   ceilings;
6. records the actual wall-clock epoch of the final cloud exchange;
7. waits the full frozen 900-second post-exchange margin using heartbeat and
   deadline checks;
8. performs one sanitized, read-only `sts get-caller-identity` probe after that
   margin; and
9. blocks the coordinator unless that post-margin probe succeeds.

This is stronger than projecting a future expiry: the margin is established by
a real provider call after the required interval. The post-margin probe is not
a Lambda invocation, is not a scored row, and does not change the 3,600-second
remote workload. It is an orchestration closeout check.

## Preserved boundaries

- exactly 84 hidden scored executions;
- exactly one 3,600-second live worker track;
- exactly 12 Lambda calls and 108 CockroachDB operations;
- unchanged 46,000-row synthetic bulk workload;
- unchanged one-worker, rate, disk, volume, network, and teardown ceilings;
- no credential or cloud client on RunPod;
- no hidden seed before `CAMPAIGN_READY`;
- no measured rerun, replacement, tuning, threshold change, or product edit;
- final GLM/AGY same-hash review remains mandatory.

## Kill line

Stop before hidden generation if either independent judge rejects this
amendment, the active provider is not `login`, the installed CLI lacks the
automatic-refresh contract, AWS/Cockroach readiness is not GREEN, or any A03
hash/isolation/lifecycle prerequisite drifts. During execution, a failed
refresh or post-margin identity probe blocks Gate 7 and triggers evidence
preservation plus teardown.

```

## FILE: HARDENING_GATE7_AWS_LOGIN_REFRESH_TEST_RECEIPT_R1.md
- `BYTES`: `1439`
- `SHA256`: `7b270a37e79ffa4459ffea0640146c96d8bd31b88e41b3482d5ea9b18a60480d`
```text
# Hardening Gate 7 AWS Login Refresh Test Receipt R1

- `UTC_RECORDED`: `2026-07-28T21:53:10Z`
- `BASE_COMMIT`: `eea91cc3595f4868b83efb650f20fcf7d7e8c863`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PY_COMPILE`: `PASS; 4_FILES`
- `S3_SOAK_TESTS`: `PASS; 17_OF_17`
- `NEW_MARGIN_TEST`: `PASS; EARLY_PROBE_BLOCKED; EXACT_900_SECOND_PROBE_PASS`
- `LIVE_PROVIDER_PROOF`: `PASS`
- `LIVE_PROVIDER`: `login`
- `AUTOMATIC_REFRESH_CONTRACT_OBSERVED`: `YES`
- `PROVIDER_PROOF_RECEIPT_SHA256`: `e44715c2505fe6f6382e8d4521bf6c2ab53d692e3f16db7d576fe14903ff38d7`
- `PROVIDER_PROOF_FILE_SHA256`: `17f2652aea37572c762795dd2797283f9be48e07b4e738cbe054b20d0de2aff9`
- `POST_REFRESH_LIVE_READINESS`: `GREEN; AWS_AUTHENTICATED; COCKROACH_REACHABLE; CREDENTIAL_BYTES_RECORDED_FALSE`
- `POST_REFRESH_LIVE_READINESS_RECEIPT_SHA256`: `7dba1517728342f15e65fa8f6e9635f3f425a7f16d2f2e7f3c3b940bc0dae55b`
- `POST_REFRESH_LIVE_READINESS_FILE_SHA256`: `7f5190d82cdd6bdaf4ad31e9883179c3ec0509905ff1b36e16feb572ab492234`
- `HIDDEN_SEED_EXISTS`: `NO`
- `MEASURED_EXECUTION_STARTED`: `NO`

The initial root-level unittest invocation was invalid because it omitted the
`s3-soak` import path. It produced no mutation. The canonical discovery command
then passed all 17 tests. The live provider proof made no Lambda call and no
CockroachDB mutation; it inspected only sanitized provider metadata and the
installed CLI's public help/version surfaces.

```

## FILE: HARDENING_GATE7_AWS_LOGIN_REFRESH_CLOUD_ADAPTER_REVIEW_R1.md
- `BYTES`: `1936`
- `SHA256`: `25a2b3ccd489a0a5120e5f8d0e7b2ff5f8ce9f317636a626db631e3d304e5577`
```text
# Gate 7 AWS Login Refresh Cloud Adapter Review R1

- `SOURCE_PATH`: `s3-soak/cloud_adapter.py`
- `SOURCE_STATUS`: `HOST_ONLY; NEVER_TRANSFERRED_TO_RUNPOD`
- `PRODUCT_CANDIDATE_MUTATION`: `NO`
- `NEW_PUBLIC_FUNCTIONS`: `prove_aws_login_provider; probe_aws_identity`
- `RAW_CREDENTIAL_OUTPUT_RECORDED`: `NO`

## `prove_aws_login_provider`

The function resolves the existing strictly validated project-local live
configuration and runs three public/read-only AWS CLI surfaces:

1. `configure list` for profile `ck-s3`, requiring the sanitized provider type
   to resolve to `login`;
2. `login help`, requiring the installed CLI's automatic-refresh statement;
3. the CLI version command.

The returned canonical receipt contains only the fixed profile/region, provider
type, a boolean refresh-contract result, SHA-256 hashes of the three command
outputs, aggregate latency, `credential_bytes_recorded=false`, status, and a
receipt hash. It does not return or persist command output.

## `probe_aws_identity`

The function resolves the same strict configuration and invokes the read-only
STS identity operation for profile `ck-s3` in `us-west-2`. It requires the
decoded response to contain exactly `Account`, `Arn`, and `UserId`. The returned
record contains only the sorted field names, SHA-256 of the complete response,
latency, `credential_bytes_recorded=false`, and status. Account, ARN, user ID,
tokens, keys, and raw output are not returned or persisted.

## Failure semantics

Both functions use the existing bounded external-command runner. A nonzero AWS
exit is converted to the existing sanitized failure class and output hash. A
provider-type mismatch, missing installed refresh contract, or identity schema
mismatch raises a stable host-orchestration error and prevents coordinator
GREEN. No retry, credential export, provider fallback, Lambda call, CockroachDB
mutation, or product mutation is introduced by these functions.

```

## FILE: HARDENING_GATE7_A03_CAMPAIGN_READY_PRECHECK_RECEIPT_R1.md
- `BYTES`: `3030`
- `SHA256`: `b383c11cdf5ea2e9d0990dffc731e0b8e1ed684a84679c7e4cfa55451baf76a3`
```text
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

```

## FILE: HARDENING_GATE7_REPAIRED_PREFLIGHT_JUDGE_RECEIPT_R2.md
- `BYTES`: `1779`
- `SHA256`: `ff0984bca74360785bf818cd3f165778f2c45ccad4385ffc30e06530ae3e7dd3`
```text
# Hardening Gate 7 Repaired Preflight Judge Receipt R2

- `UTC_CREATED`: `2026-07-28T19:28:58Z`
- `PACKET`: `HARDENING_GATE7_EXPANDED_PREFLIGHT_PACKET_R2.md`
- `PACKET_SHA256`: `4fd89d699dccd0d3e15451fab40435ad2e9b3f7300061ff8791913dc4b7ecf44`
- `PACKET_BYTES`: `252919`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `SOURCE_BINDINGS_SHA256`: `49359c601dce27ebfafe6f6cfde8151f09e430e58a443896992ef4ec5d75384a`
- `TRANSFER_ARCHIVE_SHA256`: `b95c6b8e20ec30473676b8f2dbe7e128fdb78bfd33a72105131c51bf45634eb0`
- `GLM_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RECUSAL_CHECK`: `clear`
- `GLM_RAW_SHA256`: `992fac52e9ff60d6cbab0e3e59b8320489ce9374cec29fe0f577d8894e26a581`
- `GLM_STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`
- `AGY_MODEL_BINDING`: `Gemini 3.1 Pro (High); authenticated inventory to exact backend override to provider response`
- `AGY_VERDICT`: `GREEN`
- `AGY_RECUSAL_CHECK`: `clear`
- `AGY_RAW_SHA256`: `1bc3e4db300cdf6c97378fa61b1ed3835ceca3f4f41a93c0bbd1dc2777393290`
- `AGY_STDERR_SHA256`: `704cd697e3c35f59e1936b327608c169e0648d6966e31ac5a99ade7b5816186e`
- `SAME_HASH`: `YES`
- `BLOCKERS`: `NONE`
- `ACTIVE_RUNPOD_INVENTORY`: `[]`
- `HIDDEN_SEED_CREATED`: `NO`
- `MEASURED_CAMPAIGN_STARTED`: `NO`
- `DECISION`: `REPLACEMENT_PROVIDER_READINESS_AUTHORIZED`

Both independent non-authoring judges returned valid GREEN verdicts over the
same repaired packet hash with recusal clear. Their raw outputs are preserved
under `.hardening-runtime/gate7-r2/judges-r2/` and are bound above by SHA-256.
This receipt authorizes only the already operator-approved replacement
provider-readiness lifecycle. It does not predict campaign results or waive
any measurement, evidence, teardown, or final-review gate.

```

## FILE: .hardening-runtime/gate7-r2/aws-login-provider-proof-a03.json
- `BYTES`: `606`
- `SHA256`: `17f2652aea37572c762795dd2797283f9be48e07b4e738cbe054b20d0de2aff9`
```text
{"automatic_refresh_contract_observed":true,"aws_cli_version_output_sha256":"1caed9ec0fd9a055abe408dcabbd1dca29583e09eb5b42a28e3830f3a170dfa8","aws_profile":"ck-s3","aws_region":"us-west-2","configure_list_output_sha256":"e1a7a43fbf63f0827369ed779db57f2c47a8fea82256167ebf6828cc97086fea","credential_bytes_recorded":false,"credential_provider":"login","latency_ms":2938,"login_help_output_sha256":"2f88b8a6666456db321a3087d8ff0bd15b9cf9b91b5a09c413e36380cbf52a4b","receipt_hash":"e44715c2505fe6f6382e8d4521bf6c2ab53d692e3f16db7d576fe14903ff38d7","status":"PASS","version":"s3-aws-login-provider-proof-v1"}

```

## FILE: .hardening-runtime/gate7-r2/live-readiness-after-refresh-a03.json
- `BYTES`: `676`
- `SHA256`: `7f5190d82cdd6bdaf4ad31e9883179c3ec0509905ff1b36e16feb572ab492234`
```text
{"aws_authenticated":true,"aws_identity_fields":["Account","Arn","UserId"],"aws_identity_output_sha256":"2f3d21c2f735725e3923e7d3ff8ba82cced4ceb9df2f7ff4837dc1322a286e5b","aws_latency_ms":476,"aws_profile":"ck-s3","aws_region":"us-west-2","cockroach_host_sha256":"7c6a8cd6aa77cf89ebe905cc35fc8279f01e09e17d46a0089a5e08a13a58e342","cockroach_latency_ms":2978,"cockroach_output_sha256":"804a35024e7d9edb6254a882cb1410d10f023851994a74d71a06ee61c99eeab6","cockroach_reachable":true,"credential_bytes_recorded":false,"read_only":true,"receipt_sha256":"7dba1517728342f15e65fa8f6e9635f3f425a7f16d2f2e7f3c3b940bc0dae55b","status":"GREEN","version":"hardening-gate7-live-readiness-v1"}
```

## FILE: s3-soak/hardening.py
- `BYTES`: `13976`
- `SHA256`: `9f985eaa36a3ab50e3ebc9c12f088cd3c616ecad4e50a349658c437e45d53934`
```text
#!/usr/bin/env python3
"""Fail-closed S3 hardening primitives.

This module deliberately stores only stable classifications and hashes of
external-command output.  Raw command output, credentials, and environment
contents are never written to evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import signal
import time
from typing import Any

import protocol


AWS_AUTHENTICATION = "AWS_AUTHENTICATION"
AWS_AUTHORIZATION_OR_THROTTLING = "AWS_AUTHORIZATION_OR_THROTTLING"
COCKROACH_CONNECTIVITY = "COCKROACH_CONNECTIVITY"
UNKNOWN_EXTERNAL_COMMAND = "UNKNOWN_EXTERNAL_COMMAND"
SESSION_MARGIN_SECONDS = 900

_AWS_AUTH_MARKERS = (
    b"expiredtoken", b"expired token", b"token has expired",
    b"unauthorizedssotoken", b"sso session", b"login session",
    b"invalidclienttokenid", b"unrecognizedclientexception",
)
_AWS_AUTHZ_MARKERS = (
    b"accessdenied", b"not authorized", b"unauthorizedoperation",
    b"throttl", b"too many requests", b"requestlimitexceeded",
)
_COCKROACH_CONNECTIVITY_MARKERS = (
    b"connection refused", b"connection reset", b"connection timed out",
    b"no such host", b"could not connect", b"failed to connect",
    b"server closed the connection", b"tls handshake", b"x509:",
    b"certificate", b"dial tcp", b"network is unreachable",
)


@dataclass(frozen=True)
class ExternalCommandFailure(RuntimeError):
    command_family: str
    return_code: int
    output_hash: str
    failure_class: str

    def __str__(self) -> str:
        return f"{self.failure_class}:{self.command_family}:{self.return_code}"


def classify_external_failure(command_family: str, output: bytes) -> str:
    """Classify bounded command output without returning or retaining it."""
    lowered = bytes(output[:1_048_576]).lower()
    if command_family == "aws":
        if any(marker in lowered for marker in _AWS_AUTH_MARKERS):
            return AWS_AUTHENTICATION
        if any(marker in lowered for marker in _AWS_AUTHZ_MARKERS):
            return AWS_AUTHORIZATION_OR_THROTTLING
    if command_family == "cockroach" and any(
            marker in lowered for marker in _COCKROACH_CONNECTIVITY_MARKERS):
        return COCKROACH_CONNECTIVITY
    return UNKNOWN_EXTERNAL_COMMAND


def command_failure(command_family: str, return_code: int,
                    output: bytes) -> ExternalCommandFailure:
    return ExternalCommandFailure(
        command_family=command_family,
        return_code=return_code,
        output_hash=protocol.sha256(output),
        failure_class=classify_external_failure(command_family, output),
    )


def write_atomic(path: Path, value: dict[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink() or (path.exists() and path.is_symlink()):
        raise RuntimeError("EVIDENCE_PATH_UNSAFE")
    raw = protocol.canonical(value) + b"\n"
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def failure_receipt(*, campaign_id: str, sequence: int, stage: str,
                    request_hash: str, failure: ExternalCommandFailure,
                    utc: str | None = None) -> dict[str, Any]:
    core = {
        "version": "s3-stage-failure-v1",
        "campaign_id": campaign_id,
        "sequence": sequence,
        "stage": stage,
        "request_hash": request_hash,
        "failure_class": failure.failure_class,
        "command_family": failure.command_family,
        "return_code": failure.return_code,
        "sanitized_output_sha256": failure.output_hash,
        "raw_output_stored": False,
        "utc": utc or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    return {**core, "receipt_hash": protocol.sha256(core)}


def session_window_receipt(*, expires_epoch: int, final_exchange_epoch: int,
                           margin_seconds: int = SESSION_MARGIN_SECONDS) -> dict[str, Any]:
    if any(isinstance(item, bool) or not isinstance(item, int)
           for item in (expires_epoch, final_exchange_epoch, margin_seconds)):
        raise RuntimeError("AWS_SESSION_WINDOW_INVALID")
    if margin_seconds < SESSION_MARGIN_SECONDS:
        raise RuntimeError("AWS_SESSION_MARGIN_TOO_SMALL")
    required_expiry = final_exchange_epoch + margin_seconds
    status = "PASS" if expires_epoch >= required_expiry else "BLOCKED"
    core = {
        "version": "s3-aws-session-window-v1",
        "expires_epoch": expires_epoch,
        "final_exchange_epoch": final_exchange_epoch,
        "margin_seconds": margin_seconds,
        "required_expiry_epoch": required_expiry,
        "status": status,
        "stable_reason_code": (
            "AWS_SESSION_MARGIN_VERIFIED" if status == "PASS"
            else "AWS_SESSION_MARGIN_INSUFFICIENT"
        ),
    }
    return {**core, "receipt_hash": protocol.sha256(core)}


def validate_session_window(*, expires_epoch: int, final_exchange_epoch: int,
                            margin_seconds: int = SESSION_MARGIN_SECONDS) -> dict[str, Any]:
    receipt = session_window_receipt(
        expires_epoch=expires_epoch,
        final_exchange_epoch=final_exchange_epoch,
        margin_seconds=margin_seconds,
    )
    if receipt["status"] != "PASS":
        raise RuntimeError("AWS_SESSION_MARGIN_INSUFFICIENT")
    return receipt


def login_refresh_pending_receipt(*, final_exchange_deadline_epoch: int,
                                  margin_seconds: int = SESSION_MARGIN_SECONDS,
                                  provider_receipt_hash: str) -> dict[str, Any]:
    """Bind an AWS-login campaign without claiming a false static expiry.

    ``aws login`` rotates its short-term access credentials.  This mode is
    fail-closed: the campaign is not session-GREEN until a second read-only
    identity probe succeeds after the required post-exchange margin.
    """
    if (isinstance(final_exchange_deadline_epoch, bool) or
            not isinstance(final_exchange_deadline_epoch, int) or
            final_exchange_deadline_epoch <= int(time.time())):
        raise RuntimeError("AWS_LOGIN_FINAL_EXCHANGE_DEADLINE_INVALID")
    if (isinstance(margin_seconds, bool) or
            not isinstance(margin_seconds, int) or
            margin_seconds < SESSION_MARGIN_SECONDS):
        raise RuntimeError("AWS_SESSION_MARGIN_TOO_SMALL")
    if (not isinstance(provider_receipt_hash, str) or
            len(provider_receipt_hash) != 64):
        raise RuntimeError("AWS_LOGIN_PROVIDER_RECEIPT_INVALID")
    core = {
        "version": "s3-aws-login-refresh-window-v1",
        "mode": "AWS_LOGIN_AUTO_REFRESH_POSTCHECK",
        "provider_receipt_hash": provider_receipt_hash,
        "final_exchange_deadline_epoch": final_exchange_deadline_epoch,
        "margin_seconds": margin_seconds,
        "future_expiry_claimed": False,
        "status": "PENDING_POST_EXCHANGE_PROBE",
        "stable_reason_code": "AWS_LOGIN_POST_EXCHANGE_PROBE_REQUIRED",
    }
    return {**core, "receipt_hash": protocol.sha256(core)}


def login_refresh_postcheck_receipt(*, provider_receipt_hash: str,
                                    last_exchange_epoch: int,
                                    probe_epoch: int,
                                    margin_seconds: int,
                                    identity_output_sha256: str,
                                    latency_ms: int) -> dict[str, Any]:
    values = (last_exchange_epoch, probe_epoch, margin_seconds, latency_ms)
    if any(isinstance(value, bool) or not isinstance(value, int)
           for value in values):
        raise RuntimeError("AWS_LOGIN_POSTCHECK_VALUE_INVALID")
    if margin_seconds < SESSION_MARGIN_SECONDS or latency_ms < 0:
        raise RuntimeError("AWS_LOGIN_POSTCHECK_VALUE_INVALID")
    if any(not isinstance(value, str) or len(value) != 64 for value in
           (provider_receipt_hash, identity_output_sha256)):
        raise RuntimeError("AWS_LOGIN_POSTCHECK_HASH_INVALID")
    required_probe_epoch = last_exchange_epoch + margin_seconds
    status = "PASS" if probe_epoch >= required_probe_epoch else "BLOCKED"
    core = {
        "version": "s3-aws-login-refresh-postcheck-v1",
        "provider_receipt_hash": provider_receipt_hash,
        "last_exchange_epoch": last_exchange_epoch,
        "probe_epoch": probe_epoch,
        "margin_seconds": margin_seconds,
        "required_probe_epoch": required_probe_epoch,
        "identity_output_sha256": identity_output_sha256,
        "credential_bytes_recorded": False,
        "latency_ms": latency_ms,
        "status": status,
        "stable_reason_code": (
            "AWS_LOGIN_POST_EXCHANGE_MARGIN_VERIFIED" if status == "PASS"
            else "AWS_LOGIN_POST_EXCHANGE_MARGIN_INSUFFICIENT"
        ),
    }
    return {**core, "receipt_hash": protocol.sha256(core)}


def cleanup_trial_exact(trial_root: Path, evidence_root: Path) -> dict[str, Any]:
    """Remove exactly one generated trial root and prove zero path residue."""
    trial = trial_root.resolve(strict=False)
    evidence = evidence_root.resolve()
    if trial.parent != evidence or trial == evidence or trial.is_symlink():
        raise RuntimeError("TRIAL_CLEANUP_SCOPE_INVALID")
    existed = trial.exists()
    if existed:
        shutil.rmtree(trial)
    residue = trial.exists() or trial.is_symlink()
    core = {
        "version": "s3-trial-cleanup-v1",
        "trial_name": trial.name,
        "existed_before_cleanup": existed,
        "residue_entries": 1 if residue else 0,
        "status": "BLOCKED" if residue else "PASS",
        "stable_reason_code": "TRIAL_RESIDUE" if residue else "ZERO_TRIAL_RESIDUE",
    }
    receipt = {**core, "receipt_hash": protocol.sha256(core)}
    if residue:
        raise RuntimeError("TRIAL_RESIDUE")
    return receipt


class CheckpointCustody:
    """Append-only, per-exchange custody outside the disposable trial root."""

    def __init__(self, root: Path, campaign_id: str) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=False)
        self.campaign_id = campaign_id
        self.previous = protocol.GENESIS_HASH
        self.sequence = 0

    def capture(self, request: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        protocol.validate_request(request)
        protocol.validate_result(result, request)
        expected = self.sequence + 1
        if request["campaign_id"] != self.campaign_id or request["sequence"] != expected:
            raise RuntimeError("CUSTODY_SEQUENCE_INVALID")
        core = {
            "version": "s3-checkpoint-custody-v1",
            "campaign_id": self.campaign_id,
            "sequence": expected,
            "previous_receipt_hash": self.previous,
            "request_hash": request["request_hash"],
            "result_hash": result["result_hash"],
            "request_bytes_sha256": protocol.sha256(protocol.canonical(request)),
            "result_bytes_sha256": protocol.sha256(protocol.canonical(result)),
        }
        receipt = {**core, "receipt_hash": protocol.sha256(core)}
        write_atomic(self.root / f"exchange-{expected:04d}.json", receipt)
        self.previous = receipt["receipt_hash"]
        self.sequence = expected
        return receipt


def coordinated_local_shutdown(processes: list[tuple[str, int]],
                               timeout_seconds: float = 5.0) -> dict[str, Any]:
    """Terminate exact local coordinator/bridge PIDs and prove their absence."""
    if timeout_seconds <= 0:
        raise RuntimeError("SHUTDOWN_TIMEOUT_INVALID")
    ordered = []
    for role, pid in processes:
        if role not in {"worker", "bridge", "coordinator"} or pid <= 1 or pid == os.getpid():
            raise RuntimeError("SHUTDOWN_TARGET_INVALID")
        ordered.append((role, pid))
    for _role, pid in ordered:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + timeout_seconds
    remaining: list[tuple[str, int]] = []
    while time.monotonic() < deadline:
        remaining = []
        for role, pid in ordered:
            try:
                waited, _status = os.waitpid(pid, os.WNOHANG)
                if waited == pid:
                    continue
            except ChildProcessError:
                pass
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                continue
            remaining.append((role, pid))
        if not remaining:
            break
        time.sleep(0.05)
    if remaining:
        for _role, pid in remaining:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        time.sleep(0.05)
    live = []
    for role, pid in ordered:
        try:
            waited, _status = os.waitpid(pid, os.WNOHANG)
            if waited == pid:
                continue
        except ChildProcessError:
            pass
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            continue
        live.append(role)
    core = {
        "version": "s3-coordinated-shutdown-v1",
        "requested_roles": [role for role, _pid in ordered],
        "live_roles_after_shutdown": live,
        "status": "PASS" if not live else "BLOCKED",
    }
    receipt = {**core, "receipt_hash": protocol.sha256(core)}
    if live:
        raise RuntimeError("COORDINATED_SHUTDOWN_INCOMPLETE")
    return receipt

```

## FILE: s3-soak/host_coordinator.py
- `BYTES`: `14992`
- `SHA256`: `b4c258189c2619815c81fed52732071db49404e30350e2c37057b438d1234fb1`
```text
#!/usr/bin/env python3
"""Detached S3 host coordinator with strict sequence and call ceilings."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import time
from typing import Any
import re

import cloud_adapter
import hardening
import protocol


class CoordinatorFailure(RuntimeError):
    pass


REQUEST_NAME_RE = re.compile(r"^request-([0-9]{4})\.json$")


def verify_request_directory(requests: Path, expected_sequence: int,
                             processed: set[str]) -> None:
    expected_temporary = f"request-{expected_sequence:04d}.json.tmp"
    for entry in requests.iterdir():
        if entry.is_symlink() or not entry.is_file():
            raise CoordinatorFailure("REQUEST_ENTRY_UNSAFE")
        match = REQUEST_NAME_RE.fullmatch(entry.name)
        if match is None:
            if entry.name == expected_temporary:
                continue
            raise CoordinatorFailure("REQUEST_FILE_UNKNOWN")
        sequence = int(match.group(1))
        if sequence > expected_sequence:
            raise CoordinatorFailure("OUT_OF_ORDER_REQUEST")
        if sequence < expected_sequence:
            prior = protocol.decode_request(entry.read_bytes())
            if prior["sequence"] != sequence or prior["request_hash"] not in processed:
                raise CoordinatorFailure("STALE_REQUEST_MISMATCH")


def write_atomic(path: Path, value: dict[str, Any]) -> None:
    raw = protocol.canonical(value)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


class ChainLog:
    def __init__(self, path: Path, campaign_id: str) -> None:
        if path.exists():
            raise CoordinatorFailure("LOG_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.campaign_id = campaign_id
        self.previous = protocol.GENESIS_HASH
        self.sequence = 0

    def emit(self, event: str, details: Any) -> dict[str, Any]:
        self.sequence += 1
        core = {
            "version": "s3-coordinator-log-v1",
            "campaign_id": self.campaign_id,
            "sequence": self.sequence,
            "previous_hash": self.previous,
            "event": event,
            "details": details,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "monotonic_ns": time.monotonic_ns(),
        }
        record = {**core, "event_hash": protocol.sha256(core)}
        with self.path.open("ab") as handle:
            handle.write(protocol.canonical(record) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous = record["event_hash"]
        return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bridge-root", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--expected-requests", type=int, required=True)
    parser.add_argument("--lambda-call-ceiling", type=int, required=True)
    parser.add_argument("--cockroach-operation-ceiling", type=int, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--mode", choices=("live", "fixture", "offline-refusal"),
                        required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--heartbeat-seconds", type=int, default=5)
    parser.add_argument("--completion-marker", type=Path)
    parser.add_argument("--custody-root", type=Path)
    parser.add_argument("--aws-session-expiry-epoch", type=int)
    parser.add_argument("--final-cloud-exchange-epoch", type=int)
    parser.add_argument("--session-margin-seconds", type=int, default=900)
    parser.add_argument("--aws-login-auto-refresh", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.expected_requests <= protocol.MAX_SEQUENCE:
        raise CoordinatorFailure("EXPECTED_REQUESTS_INVALID")
    if args.mode == "live" and args.config is None:
        raise CoordinatorFailure("LIVE_CONFIG_REQUIRED")
    if args.mode == "live" and any(value is None for value in (
            args.custody_root, args.final_cloud_exchange_epoch)):
        raise CoordinatorFailure("LIVE_CUSTODY_OR_SESSION_GATE_REQUIRED")
    if (args.mode == "live" and
            (args.aws_login_auto_refresh ==
             (args.aws_session_expiry_epoch is not None))):
        raise CoordinatorFailure("LIVE_SESSION_MODE_INVALID")
    if (args.mode == "live" and
            (args.final_cloud_exchange_epoch < int(time.time()) or
             args.final_cloud_exchange_epoch > args.deadline_epoch)):
        raise CoordinatorFailure("FINAL_CLOUD_EXCHANGE_WINDOW_INVALID")
    if args.deadline_epoch <= int(time.time()):
        raise CoordinatorFailure("DEADLINE_INVALID")
    if args.lambda_call_ceiling < args.expected_requests:
        raise CoordinatorFailure("LAMBDA_CEILING_TOO_LOW")
    if args.cockroach_operation_ceiling < args.expected_requests * 9:
        raise CoordinatorFailure("COCKROACH_CEILING_TOO_LOW")

    bridge = args.bridge_root.resolve()
    requests = bridge / "requests"
    results = bridge / "results"
    for path in (requests, results):
        path.mkdir(parents=True, exist_ok=True)
    evidence = args.evidence_root.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    custody = None
    if args.custody_root is not None:
        custody = hardening.CheckpointCustody(
            args.custody_root, args.campaign_id)
    if args.mode == "live":
        assert args.final_cloud_exchange_epoch is not None
        if args.aws_login_auto_refresh:
            provider_receipt = cloud_adapter.prove_aws_login_provider(args.config)
            hardening.write_atomic(
                evidence / "aws-login-provider.json", provider_receipt)
            session_receipt = hardening.login_refresh_pending_receipt(
                final_exchange_deadline_epoch=args.final_cloud_exchange_epoch,
                margin_seconds=args.session_margin_seconds,
                provider_receipt_hash=provider_receipt["receipt_hash"],
            )
        else:
            assert args.aws_session_expiry_epoch is not None
            provider_receipt = None
            session_receipt = hardening.validate_session_window(
                expires_epoch=args.aws_session_expiry_epoch,
                final_exchange_epoch=args.final_cloud_exchange_epoch,
                margin_seconds=args.session_margin_seconds,
            )
        hardening.write_atomic(evidence / "aws-session-window.json", session_receipt)
    log = ChainLog(evidence / "coordinator.ndjson", args.campaign_id)
    processed: set[str] = set()
    expected_sequence = 1
    parent_hash = protocol.GENESIS_HASH
    lambda_calls = 0
    cockroach_operations = 0
    last_exchange_epoch: int | None = None
    stopped = False

    def stop(_signum: int, _frame: Any) -> None:
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    log.emit("COORDINATOR_START", {
        "mode": args.mode,
        "expected_requests": args.expected_requests,
        "lambda_call_ceiling": args.lambda_call_ceiling,
        "cockroach_operation_ceiling": args.cockroach_operation_ceiling,
        "deadline_epoch": args.deadline_epoch,
    })
    last_heartbeat = 0.0
    try:
        while expected_sequence <= args.expected_requests:
            if stopped:
                raise CoordinatorFailure("COORDINATOR_STOPPED")
            if int(time.time()) >= args.deadline_epoch:
                raise CoordinatorFailure("COORDINATOR_DEADLINE")
            now = time.monotonic()
            if now - last_heartbeat >= args.heartbeat_seconds:
                log.emit("HEARTBEAT", {
                    "next_sequence": expected_sequence,
                    "processed": len(processed),
                    "lambda_calls": lambda_calls,
                    "cockroach_operations": cockroach_operations,
                })
                last_heartbeat = now
            verify_request_directory(requests, expected_sequence, processed)
            request_path = requests / f"request-{expected_sequence:04d}.json"
            if not request_path.exists():
                time.sleep(0.1)
                continue
            raw = request_path.read_bytes()
            request = protocol.decode_request(raw)
            if request["campaign_id"] != args.campaign_id:
                raise CoordinatorFailure("CAMPAIGN_MISMATCH")
            if request["sequence"] != expected_sequence:
                raise CoordinatorFailure("OUT_OF_ORDER_REQUEST")
            if request["parent_hash"] != parent_hash:
                raise CoordinatorFailure("PARENT_HASH_MISMATCH")
            if request["request_hash"] in processed:
                raise CoordinatorFailure("DUPLICATE_REQUEST")
            log.emit("REQUEST_ACCEPTED", {
                "sequence": expected_sequence,
                "request_hash": request["request_hash"],
                "operation": request["operation"],
            })
            if args.mode == "offline-refusal":
                log.emit("COORDINATOR_OFFLINE_REFUSAL", {
                    "sequence": expected_sequence,
                    "request_hash": request["request_hash"],
                    "stable_reason_code": "COORDINATOR_UNAVAILABLE",
                })
                return 73
            call_root = evidence / f"call-{expected_sequence:04d}"
            if args.mode == "live":
                metrics, hashes = cloud_adapter.run_live(request, args.config, call_root)
            else:
                metrics, hashes = cloud_adapter.run_fixture(request)
            lambda_calls += int(metrics["lambda_invocations"])
            cockroach_operations += int(metrics["cockroach_operations"])
            if lambda_calls > args.lambda_call_ceiling:
                raise CoordinatorFailure("LAMBDA_CALL_CEILING")
            if cockroach_operations > args.cockroach_operation_ceiling:
                raise CoordinatorFailure("COCKROACH_OPERATION_CEILING")
            result = protocol.make_result(request, metrics, hashes)
            result_path = results / f"result-{expected_sequence:04d}.json"
            write_atomic(result_path, result)
            if custody is not None:
                custody_receipt = custody.capture(request, result)
                log.emit("CHECKPOINT_CUSTODY_COMMITTED", {
                    "sequence": expected_sequence,
                    "receipt_hash": custody_receipt["receipt_hash"],
                })
            log.emit("RESULT_COMMITTED", {
                "sequence": expected_sequence,
                "request_hash": request["request_hash"],
                "result_hash": result["result_hash"],
                "lambda_calls": lambda_calls,
                "cockroach_operations": cockroach_operations,
            })
            last_exchange_epoch = int(time.time())
            processed.add(request["request_hash"])
            parent_hash = request["request_hash"]
            expected_sequence += 1
        if args.mode == "live" and args.aws_login_auto_refresh:
            assert provider_receipt is not None
            assert last_exchange_epoch is not None
            required_probe_epoch = last_exchange_epoch + args.session_margin_seconds
            while int(time.time()) < required_probe_epoch:
                if stopped:
                    raise CoordinatorFailure("COORDINATOR_STOPPED")
                if int(time.time()) >= args.deadline_epoch:
                    raise CoordinatorFailure("AWS_MARGIN_PROBE_DEADLINE")
                now = time.monotonic()
                if now - last_heartbeat >= args.heartbeat_seconds:
                    log.emit("HEARTBEAT", {
                        "next_sequence": expected_sequence,
                        "processed": len(processed),
                        "lambda_calls": lambda_calls,
                        "cockroach_operations": cockroach_operations,
                        "awaiting_aws_margin_probe": True,
                        "remaining_margin_seconds": max(
                            0, required_probe_epoch - int(time.time())),
                    })
                    last_heartbeat = now
                time.sleep(0.2)
            identity_probe = cloud_adapter.probe_aws_identity(args.config)
            postcheck = hardening.login_refresh_postcheck_receipt(
                provider_receipt_hash=provider_receipt["receipt_hash"],
                last_exchange_epoch=last_exchange_epoch,
                probe_epoch=int(time.time()),
                margin_seconds=args.session_margin_seconds,
                identity_output_sha256=identity_probe["identity_output_sha256"],
                latency_ms=identity_probe["latency_ms"],
            )
            if postcheck["status"] != "PASS":
                raise CoordinatorFailure("AWS_LOGIN_POSTCHECK_BLOCKED")
            hardening.write_atomic(
                evidence / "aws-session-margin-postcheck.json", postcheck)
            log.emit("AWS_SESSION_MARGIN_VERIFIED", {
                "postcheck_receipt_hash": postcheck["receipt_hash"],
                "margin_seconds": args.session_margin_seconds,
            })
        if args.completion_marker is not None:
            marker = args.completion_marker.resolve()
            while not marker.exists():
                if stopped:
                    raise CoordinatorFailure("COORDINATOR_STOPPED")
                if int(time.time()) >= args.deadline_epoch:
                    raise CoordinatorFailure("COMPLETION_MARKER_DEADLINE")
                now = time.monotonic()
                if now - last_heartbeat >= args.heartbeat_seconds:
                    log.emit("HEARTBEAT", {
                        "next_sequence": expected_sequence,
                        "processed": len(processed),
                        "lambda_calls": lambda_calls,
                        "cockroach_operations": cockroach_operations,
                        "awaiting_completion_marker": True,
                    })
                    last_heartbeat = now
                time.sleep(0.2)
        log.emit("COORDINATOR_GREEN", {
            "processed": len(processed),
            "lambda_calls": lambda_calls,
            "cockroach_operations": cockroach_operations,
        })
        return 0
    except Exception as exc:
        log.emit("COORDINATOR_BLOCKED", {
            "type": type(exc).__name__,
            "error_hash": protocol.sha256(str(exc).encode("utf-8")),
        })
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

```
