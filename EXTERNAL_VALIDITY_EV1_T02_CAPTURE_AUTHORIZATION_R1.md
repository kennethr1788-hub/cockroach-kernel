# EV1-T02 Capture Authorization R1

- `STATUS`: `CAPTURE_AUTHORIZED; EXECUTION_NOT_STARTED`
- `TASK_ID`: `EV1-T02`
- `UTC_RECORDED`: `2026-07-30T16:39:22Z`
- `TASK_COMMIT`: `769321ec9828948afdacc7856321495c0ffd40a6`
- `WORK_RECEIPT_FILE_SHA256`: `48a5856158cc43884cfd1d500adb0121f207b5b1d05a172e759eab8de78571d9`
- `WORK_RECEIPT_INTERNAL_SHA256`: `a97a025c62baedbad53bdcda6baf668e603e755845613fb3c8d9e9e9d7cc1b91`
- `CAPTURE_STARTED_AT_RECEIPT`: `FALSE`
- `DELETION_STARTED_AT_RECEIPT`: `FALSE`
- `RECOVERY_STARTED_AT_RECEIPT`: `FALSE`

## Kenneth's exact declaration

> I, Kenneth, explicitly declare the exact current EV1-T02
> state—committed scripts/run-storage-contract.mjs at task commit
> 769321ec9828948afdacc7856321495c0ffd40a6, modified package.json, and
> untracked scripts/storage-contract-cases.cjs—permitted for capture, guarded
> disposable-workspace deletion, and fresh-process recovery under the frozen
> EV1 protocol.

This authorization binds only the three declared work units and the exact task
commit above. It does not authorize source drift, product-candidate changes,
rerunning T01, modifying HOME runtime, external publication, or deletion before
the T02 runner and dependency topology pass their frozen independent preflight.
