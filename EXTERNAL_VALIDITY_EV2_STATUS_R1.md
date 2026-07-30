# External Validity EV2 Status R1

- `STATUS`: `EXTERNAL_VALIDITY_EV2_BLOCKED`
- `BLOCKER`: `FROZEN_HARNESS_VALIDATOR_INTERFACE_MISMATCH`
- `UTC_CLOSED`: `2026-07-30T11:32:08Z`
- `LAST_GREEN_GATE`: `EXTERNAL_VALIDITY_PREFLIGHT_GREEN_FOR_EV2`
- `CURRENT_COMMIT_AT_START`: `c45aa6adfed3792e23965936121d27556bf6b49a`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PREFLIGHT_PACKET_SHA256`: `41a341d60ab776e8a01f38f6ae142661e54751ef8878083d43f5c822045e55b4`
- `CAMPAIGN_SCRIPT_SHA256`: `da17e97840077f6d16e9692fba7d4900d673fd676203dc2a51d08969f8413a4c`
- `COMPLETED_EXECUTIONS`: `0/24`
- `MEASURED_CREDIT`: `NONE`
- `FAILURE_TYPE`: `TypeError`
- `FAILURE_MESSAGE_SHA256`: `363f7ec94a1260c330fa324f97506d52386cb8f87fc29a81b6b6494f3b91ce91`
- `LOCAL_REPRODUCTION`: `HASH_MATCH`
- `TEARDOWN`: `PASS`
- `FAULT_LAMBDA_ABSENT`: `TRUE`
- `CAMPAIGN_SCHEMA_ABSENT`: `TRUE`
- `MCP_OAUTH`: `LOGGED_OUT_BEFORE_CAMPAIGN`
- `GITLEAKS`: `ZERO_FINDINGS`
- `DETECT_SECRETS`: `ZERO_FINDINGS`
- `PRIVATE_PATH_AND_CREDENTIAL_MARKER_SCAN`: `ZERO_FINDINGS`
- `EVIDENCE_ROOT`: `evidence/external-validity-ev2-live-r1`

## Failure mechanism

Execution 1 successfully reached the retained live AWS Lambda and received a
schema-valid advisory response. The frozen EV2 coordinator then called
`cloud_records.validate_response(response, request)`. The current product
validator has the interface `validate_response(response)`. Python therefore
raised `TypeError` before the execution could emit a chained receipt.

The mismatch was reproduced locally against the preserved execution-01 request
and response. The SHA-256 of the local exception message exactly equals the
campaign's recorded `message_sha256`. This proves a harness compatibility defect;
it does not prove or disprove the intended CockroachDB/AWS continuity claim.

## Contract disposition

The frozen protocol forbids retuning or replacing a measured execution after its
outcome is known. This run remains failed evidence and receives zero measured
credit. It must not be relabeled as infrastructure readiness or silently retried.

## Next safe action

Freeze a new amendment that changes only the obsolete validator call to the
current one-argument product interface, adds a local extracted-response canary
that proves the exact call path, and preserves all other matrix, threshold,
resource, teardown, and no-tuning terms. Obtain fresh same-hash GLM and AGY
preflight on that amendment. A replacement campaign requires separate explicit
operator authorization after the amended preflight is GREEN.

EV1, EV3, Gate 9, public claims, release, video, and submission remain forbidden.
