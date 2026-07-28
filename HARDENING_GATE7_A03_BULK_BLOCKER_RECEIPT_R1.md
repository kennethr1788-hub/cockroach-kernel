# Gate 7 A03 Bulk Workload Blocker Receipt R1

- `STATUS`: `BLOCKED_PRESERVED`
- `UTC_DETECTED`: `2026-07-28T22:09:00Z`
- `CAMPAIGN_ID`: `ck-g7r2-a03-bulk`
- `WORKLOAD_RERUN`: `FORBIDDEN`
- `RESULT_RECEIPT_EXISTS`: `NO`
- `CONTROLLER_PROCESS_AFTER_EXIT`: `ABSENT`
- `SCREEN_SESSION_AFTER_EXIT`: `ABSENT`
- `CAPTURED_EXCEPTION_TEXT`: `UNAVAILABLE`
- `EVIDENCE_CAPTURE_DEFECT`: `controller stdout/stderr was not redirected to a durable file`
- `STABLE_BLOCKER`: `BULK_RESULT_MISSING_AFTER_PARTIAL_INSERT`

## Frozen generated workload

- `TASK_SQL_SHA256`: `a7d6481e35e302c20c109b63259908cd15cb6226c6a0bde78220d0d5d5d2c67c`
- `EVENT_SQL_SHA256`: `48077bec4ee9fc189fccaef82a8f4dbda414f1fbbb2dc36f5a3b4fef92aa2f00`
- `RECEIPT_SQL_SHA256`: `13276de9f1a8fe1dc002a816ffcefb7a66b47e42f2b26014ce1358e5e745438a`
- `VECTOR_SQL_SHA256`: `92004fb4001b2c20275037bf8cb94f0db86c11f09678834167d66278141a9354`
- `QUERY_SPECS_SHA256`: `0128c36190ed72a5910d641b3a2984aa481b0bf6e6eec70d1642945d11496947`
- `MANIFEST_FILE_SHA256`: `1c995191b772a1aa28d874ea9ab373b3b107d17917e72140e522ea8b5e63d0a7`
- `CLEANUP_SQL_SHA256`: `0bd89e72c8513af2de2b28cb53c99782841abfdebb88a46c1160f061333076b5`

## Direct live-state diagnosis

The first post-exit read-only count query observed:

- `tasks`: `2000`
- `trajectory_events`: `20000`
- `receipts`: `4000`
- `context_vectors`: `0`

This directly proves that the controller completed the task, event, and receipt
insert stages and exited before completing the vector stage and before emitting
its required result receipt. Because the exact exception output was not durably
captured, this receipt does not invent a more specific cause.

## Mandatory cleanup

The already frozen dependency-ordered cleanup SQL was executed once solely to
remove synthetic campaign residue; it did not rerun or resume the measured
workload.

- `CLEANUP_OUTPUT_SHA256`: `fafe1c7608a31b52c76fb0a35c28411480b530d4b05e2e905e5553eaaf520229`
- `CLEANUP_LATENCY_MS`: `4515`
- `POST_CLEANUP_TASKS`: `0`
- `POST_CLEANUP_EVENTS`: `0`
- `POST_CLEANUP_RECEIPTS`: `0`
- `POST_CLEANUP_VECTORS`: `0`
- `RESIDUE_OUTPUT_SHA256`: `58d9fffe639ec31e34a1032bd727a05a5b7d6983881706d28a39c24cd03a31bb`
- `RESIDUE_QUERY_LATENCY_MS`: `1150`
- `CLEANUP_STATUS`: `GREEN`

The independent 3,600-second worker remains active and guarded so its evidence
can complete and be preserved. This blocker prevents Gate 7 from becoming GREEN
under the current one-run law, regardless of the worker result. No hidden,
bulk, or worker rerun is authorized.
