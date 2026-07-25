# P2 Checkpoint

- `GATE`: `CK_P2_BLOCKED`
- `BLOCKER`: `LOCAL_COCKROACH_RUNTIME_UNAVAILABLE`
- `LAST_GREEN_GATE`: `CK_P1_CONTRACT_GREEN`
- `CURRENT_COMMIT_BEFORE_RECEIPT`: `725c6c6ef6c7c7c14c950dba00a37a07ca47a093`
- `UTC`: `2026-07-25T20:17:15Z`
- `NEXT_ALLOWED_ACTION`: provide or activate an approved local CockroachDB
  runtime, verify it without credential leakage, and rerun P2 from fresh
  temporary roots
- `FORBIDDEN`: install global packages; use a substitute database; contact a
  live cluster; launch AWS/RunPod; continue to P3
