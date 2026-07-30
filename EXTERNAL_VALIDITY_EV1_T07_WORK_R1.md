# EV1-T07 Work R1

- `STATUS`: `EV1_T07_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED`
- `TASK_COMMIT`: `f1b13c8a3b6fb2ba2affcdf358ccbc7535b626a9`
- `WORK_RECEIPT_FILE_SHA256`: `6d9e2238c5c10419efdadad8e4435e91afa566a4f0150c441985ae1848f4288a`
- `WORK_RECEIPT_SHA256`: `485aed463767d66080f994ce5e7cb3b3b84eee671627006f07dd475481482e2b`
- `COMMITTED`: `lib/requestLimits.ts; scripts/run-api-limits.mjs`
- `MODIFIED_TRACKED`: `app/api/analyze/route.ts; package.json`
- `UNTRACKED`: `fixtures/oversized-analyze-request.json`
- `OVERSIZED_FIXTURE_BYTES`: `81920`
- `API_LIMIT_CASES`: `7`
- `FIVE_EXECUTION_LOGS_BYTE_IDENTICAL`: `TRUE`
- `TYPECHECK_BUILD`: `PASS`
- `PREDECLARED_CAPTURE_OUTCOME`: `INVALID_OVERSIZED_RECORD`
- `DELETION_AFTER_INVALID`: `FORBIDDEN`

The bounded parser and stable 400 path pass offline. The 80 KiB fixture remains
untracked specifically to trigger the frozen expected-invalid capture outcome.
That outcome is a safety result, not successful continuation.
