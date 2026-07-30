# EV1-T08 Work R1

- `STATUS`: `EV1_T08_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED`
- `TASK_COMMIT`: `6b81ce4eb1f1d7a6e83b733ef18d92cf7c44c178`
- `WORK_RECEIPT_FILE_SHA256`: `cd9f6293427dce01e855fcc310327310a6a7719b31814d0741202fac30cabfdf`
- `WORK_RECEIPT_SHA256`: `561e1d4bde9c67dd4f19435f59ee1bd9e68bca89a0e4e59f0d6d21121bb03c1f`
- `COMMITTED`: `lib/dataPath.ts; scripts/run-data-path-containment.mjs`
- `MODIFIED_TRACKED`: `lib/signals.ts; package.json`
- `UNTRACKED_SYMLINK`: `data/escape-sample-signals.json -> ../../synthetic-outside-target.json`
- `CONTAINMENT_CASES`: `IN_ROOT_READ_PASS; OUT_OF_ROOT_SYMLINK_REJECTED_BEFORE_READER_CALL`
- `ESCAPED_READER_CALLS`: `0`
- `FIVE_EXECUTION_LOGS_BYTE_IDENTICAL`: `TRUE`
- `TYPECHECK_BUILD`: `PASS`
- `PREDECLARED_CAPTURE_OUTCOME`: `INVALID_UNSAFE_SYMLINK_ESCAPE`
- `OUTSIDE_TARGET_CONTENT_READ_BY_WORK_RECORDER`: `FALSE`
- `OUTSIDE_TARGET_METADATA_UNCHANGED`: `TRUE`
- `TARGET_READ_MODIFY_DELETE_AFTER_INVALID`: `FORBIDDEN`
- `WORKSPACE_DELETION_AFTER_INVALID`: `FORBIDDEN`

The task validates the real data root and resolved candidate before invoking a
reader. The synthetic escape symlink remains untracked and is intended to
trigger the frozen expected-invalid capture outcome. That outcome is a safety
result, not successful continuation.
