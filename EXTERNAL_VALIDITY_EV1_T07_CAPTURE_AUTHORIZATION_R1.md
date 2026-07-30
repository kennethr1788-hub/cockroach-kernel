# EV1-T07 Capture Authorization R1

- `TASK_ID`: `EV1-T07`
- `UTC_RECORDED`: `2026-07-30T20:11:03Z`
- `AUTHORITY`: `KENNETH_EXPLICIT_DECLARATION`
- `CAPTURE`: `AUTHORIZED`
- `EXPECTED_OUTCOME`: `INVALID_OVERSIZED_RECORD`
- `GUARDED_DISPOSABLE_WORKSPACE_DELETION`: `FORBIDDEN_AFTER_INVALID`
- `FRESH_PROCESS_RECOVERY`: `FORBIDDEN_AFTER_INVALID`
- `PUBLIC_ACTIONS`: `NOT_AUTHORIZED`

> I, Kenneth, explicitly declare the exact current EV1-T07 state—committed
> lib/requestLimits.ts and scripts/run-api-limits.mjs at task commit
> f1b13c8a3b6fb2ba2affcdf358ccbc7535b626a9, modified
> app/api/analyze/route.ts and package.json, and untracked exact 80 KiB
> fixtures/oversized-analyze-request.json—permitted for capture under the frozen
> EV1 protocol. I understand the predeclared outcome is
> INVALID_OVERSIZED_RECORD; after that INVALID result, deletion and recovery are
> forbidden and the workspace must remain intact.

This declaration binds only the five named task files in the disposable EV1-T07
workspace. The authorized capture must fail closed at the product candidate's
65,536-byte representation boundary, preserve the oversized fixture and entire
workspace unchanged, create no successor, and perform no recovery.
