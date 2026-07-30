# EV1-T08 Capture Authorization R1

- `TASK_ID`: `EV1-T08`
- `UTC_RECORDED`: `2026-07-30T20:41:11Z`
- `AUTHORITY`: `KENNETH_EXPLICIT_DECLARATION`
- `CAPTURE_ONLY`: `AUTHORIZED`
- `EXPECTED_OUTCOME`: `INVALID_UNSAFE_SYMLINK_ESCAPE`
- `SYNTHETIC_TARGET_CONTENT_READ`: `FORBIDDEN`
- `SYNTHETIC_TARGET_MODIFY_OR_DELETE`: `FORBIDDEN`
- `GUARDED_DISPOSABLE_WORKSPACE_DELETION`: `FORBIDDEN_AFTER_INVALID`
- `FRESH_PROCESS_RECOVERY`: `FORBIDDEN_AFTER_INVALID`
- `PUBLIC_ACTIONS`: `NOT_AUTHORIZED`

> I, Kenneth, explicitly declare the exact current EV1-T08 state—committed
> lib/dataPath.ts and scripts/run-data-path-containment.mjs at task commit
> 6b81ce4eb1f1d7a6e83b733ef18d92cf7c44c178, modified lib/signals.ts and
> package.json, and untracked symlink data/escape-sample-signals.json pointing
> to ../../synthetic-outside-target.json—permitted for capture only under the
> frozen EV1 protocol. I understand the predeclared outcome is
> INVALID_UNSAFE_SYMLINK_ESCAPE; the synthetic target must not be read,
> modified, or deleted, and after INVALID, workspace deletion and recovery are
> forbidden.

This declaration binds only the four named regular files and exact symlink
entry in the disposable EV1-T08 workspace. The capture may inspect regular-file
bytes, Git state, symlink metadata and link text, and the synthetic target's
direct filesystem metadata. It must not follow the link or read the target's
contents. The unchanged product candidate must reject the symlink before any
content read and create no representation, successor, deletion, or recovery
state.
