# Hardening Gate 7 AWS Login Refresh Preflight Packet R1
## Decision requested
GLM and AGY are independent, non-authoring, tool-disabled judges. Review only whether this narrow host-orchestration correction may replace the false static access-credential expiry check before A03 becomes CAMPAIGN_READY. Do not write code, direct implementation, predict the campaign outcome, or treat this preflight as measured evidence.
Return GREEN only if the correction preserves the frozen product candidate, 84-case semantics, live-track thresholds, credential separation, and fail-closed behavior, and if the real post-exchange 900-second provider probe is at least as strong as the intended session-margin gate.
## Bindings
- `PACKET_VERSION`: `gate7-aws-login-refresh-preflight-r1`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `ORCHESTRATION_HEAD`: `0a1683cbc46f4ca0290d6a66770ab26e4c6174eb`
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
HARDENING_GATE7_AWS_LOGIN_REFRESH_CODE_REVIEW_R1.md
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

## FILE: HARDENING_GATE7_AWS_LOGIN_REFRESH_CODE_REVIEW_R1.md
- `BYTES`: `2756`
- `SHA256`: `57b9fe31b32728296e090dbd47a69598ebe28d37c0641d27aefff4daa48f79c0`
```text
# Gate 7 AWS Login Refresh Code Review R1

## Exact source bindings

- `s3-soak/hardening.py`: `9f985eaa36a3ab50e3ebc9c12f088cd3c616ecad4e50a349658c437e45d53934`
- `s3-soak/cloud_adapter.py`: `e1a7a99c11744244312462a8127d1234bc0179b867f1d106c549feca7507a8ca`
- `s3-soak/host_coordinator.py`: `b4c258189c2619815c81fed52732071db49404e30350e2c37057b438d1234fb1`
- `s3-soak/test_hardening.py`: `b23e9b2550da9466d0136b8a7c30aca98c8c3b4226f96c65a2ef5992fbd96612`

These are host-side Gate 7 orchestration and tests. The frozen remote payload
contains only `s3-soak/protocol.py` and `s3-soak/worker.py`; neither changed.

## Receipt primitives

The new pending-window primitive rejects non-integer, past, undersized-margin,
and malformed-hash inputs. Its receipt declares that no future expiry is being
claimed and stays pending until the post-exchange provider probe exists.

The new postcheck primitive requires integer last-exchange/probe/margin/latency
values, a margin of at least 900 seconds, and two 64-character SHA-256 values.
It returns PASS only when the probe epoch is at or after the last exchange plus
the full margin. An early probe returns BLOCKED with a stable reason code.

## Coordinator state machine

The legacy fixed-expiration mode remains available. Live execution selects
exactly one mode: legacy fixed expiration or the explicit AWS-login automatic
refresh mode. Selecting both or neither fails before the coordinator starts.

In automatic-refresh mode the coordinator:

1. proves the login provider and installed refresh contract;
2. writes the pending session receipt;
3. executes the unchanged twelve-request loop with the unchanged Lambda and
   Cockroach operation ceilings;
4. records the wall-clock epoch immediately after each committed result;
5. after result twelve, waits until the final recorded epoch plus 900 seconds;
6. emits hash-chained heartbeats while waiting and continues enforcing the
   stop signal and absolute lifecycle deadline;
7. performs one sanitized read-only identity probe;
8. validates and fsyncs the final postcheck receipt;
9. emits a hash-chained margin-verified event; and
10. only then proceeds to the pre-existing completion-marker and GREEN path.

A failed provider proof, refresh, identity probe, time check, stop check, or
deadline check enters the existing coordinator BLOCKED path. It cannot be
averaged away or relabeled as product success.

## Tests

The complete `s3-soak` suite passed 17/17. The new test proves an 899-second
probe is BLOCKED and an exact 900-second probe is PASS. Existing tests continue
to cover sanitized external failures, expiry-mode rejection, sequence/order,
hash linkage, atomic evidence, coordinator completion waiting, bridge staging,
and exact local shutdown.

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
