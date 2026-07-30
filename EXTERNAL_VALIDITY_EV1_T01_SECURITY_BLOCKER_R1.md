# EV1-T01 Security Blocker R1

- `STATUS`: `EV1_T01_SECURITY_BLOCKED`
- `BLOCKER`: `UNRELATED_PROCESS_CREDENTIAL_VISIBLE_IN_COMMAND_LINE`
- `OBSERVED_UTC`: `2026-07-30T14:11:00Z`
- `EXPOSING_PROCESS`: `npm exec serve --listen 4321 --no-clipboard`
- `EXPOSING_PROCESS_ACTIVE_AT_CHECK`: `TRUE`
- `SECRET_VALUE_RECORDED`: `FALSE`
- `TASK_ARTIFACT_FILES_SCANNED`: `87`
- `TASK_ARTIFACT_CREDENTIAL_MARKERS`: `0`
- `EV1_TASK_PROCESS_ACTIVE`: `FALSE`
- `HUMAN_EDIT_PERFORMED`: `FALSE`
- `CAPTURE_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`
- `DISPOSABLE_ROOT_PRESERVED`: `TRUE`

An unrelated pre-existing local process exposes a credential through its
command-line environment. The value is intentionally omitted from every EV1
artifact. It did not enter the source export, dependency receipt, task
workspace, judge packet, or committed evidence.

## Human action required

Kenneth must revoke or rotate the affected credential and restart or terminate
the exposing process. After Kenneth explicitly confirms remediation, Codex must
verify the process is absent or no credential value is present in its command
line before allowing the EV1-T01 human edit.

Do not type the tagline, capture state, destroy the workspace, invoke recovery,
or record an operator observation while this blocker is open.
