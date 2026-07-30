# EV1 Preflight R1 Blocked Receipt

- `STATUS`: `EV1_PREFLIGHT_R1_BLOCKED`
- `BLOCKER`: `SOURCE_PRIVATE_PATH_MARKER`
- `SOURCE_LABEL`: `brew-ledger`
- `SOURCE_COMMIT`: `1a92380a9edf12337f80b3c42ba098a7c1724664`
- `AFFECTED_TRACKED_FILE`: `CLAUDE.md`
- `PRIVATE_PATH_LINE_COUNT`: `2`
- `CREDENTIAL_MARKER_COUNT`: `0`
- `OTHER_SOURCE_MARKER_COUNT`: `0`
- `MEASURED_TASKS_STARTED`: `0`
- `MEASURED_CLOCK_STARTED`: `FALSE`
- `WORKSPACE_DELETION_PERFORMED`: `FALSE`
- `PRODUCT_CANDIDATE_CHANGED`: `FALSE`
- `R1_BACKLOG_SHA256`: `34ffed70e3d52cde2e94e5f3b66dd96cdac1f2aa7de757b11bf6580bb5e536e4`
- `R2_BACKLOG_CANDIDATE_SHA256`: `6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5`

The first local unit run stopped at source binding before the full mechanical
preflight or either external judge. No private-path value is copied into this
receipt. The marker is confined to a non-application instruction file.

## Narrow correction

- Exclude only `CLAUDE.md` from the Brew Ledger disposable export.
- Bind the remaining 76 tracked files by canonical manifest SHA-256
  `d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706`.
- Preserve all 12 tasks, their order, acceptance checks, state mixes, human-edit
  flags, and expected-invalid cases unchanged.
- Require fresh Kenneth confirmation over the R2 candidate hash before rerunning
  preflight.
