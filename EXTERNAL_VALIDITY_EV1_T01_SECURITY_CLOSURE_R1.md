# EV1-T01 Security Closure R1

- `STATUS`: `EV1_T01_SECURITY_GATE_CLOSED_WITH_REVOKED_ENVIRONMENT_RESIDUAL`
- `UTC_CLOSED`: `2026-07-30T14:18:59Z`
- `OPERATOR_CONFIRMATION`: `Kenneth confirmed the affected credential was rotated.`
- `RECORDED_PARENT_PROCESS_TERMINATED`: `TRUE`
- `RECORDED_CHILD_PROCESS_TERMINATED`: `TRUE`
- `RECORDED_PROCESS_IDS_ABSENT`: `TRUE`
- `PROCESS_COMMAND_LINES_WITH_VARIABLE_NAME`: `48`
- `PROCESS_ENVIRONMENT_VALUES_READ_OR_RECORDED`: `FALSE`
- `RESIDUAL_CLASSIFICATION`: `INHERITED_REVOKED_VALUE_BY_OPERATOR_ATTESTATION`
- `PROVIDER_REVOCATION_INDEPENDENTLY_VERIFIED`: `FALSE`
- `EV1_TASK_ENVIRONMENT_ALLOWLISTED`: `TRUE`
- `EV1_TASK_ENVIRONMENT_CONTAINS_AFFECTED_VARIABLE`: `FALSE`
- `EV1_TASK_PROCESS_ACTIVE`: `FALSE`
- `T01_PRE_HUMAN_STATE_UNCHANGED`: `TRUE`
- `HUMAN_EDIT_PERFORMED`: `FALSE`
- `CAPTURE_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`

Kenneth explicitly confirmed rotation of the exposed credential. Codex then
terminated only the recorded unrelated `npm exec serve` parent and its child and
verified both process IDs were absent.

The host process table still exposes the affected variable name in 48 inherited
process environments. No value was read or recorded during closure. Those
inherited values are treated as revoked only because Kenneth provided the
human-owned rotation attestation; provider-side revocation is not independently
verifiable by Codex.

EV1-T01 may proceed because its subprocess environment is constructed from an
explicit allowlist and excludes the affected variable. The residual host
environment must not be described as scrubbed. A later host/app restart is
recommended, but it is not part of the measured task and must not be claimed as
completed.
