# EV1-T06 Work R1

- `STATUS`: `EV1_T06_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED`
- `UTC_RECORDED`: `2026-07-30T19:31:48Z`
- `TASK_COMMIT`: `a3e5cd8f7dda19dd04df5904b5671f955a5c7adb`
- `WORK_RECEIPT_FILE_SHA256`: `78cf0fb8f07ee61d86eb37b6970c087df21deac6b22e3f6ba671b5ae9489f602`
- `WORK_RECEIPT_SHA256`: `7a31602588f1e319d70b9bd202e15683862fe7f061786f14e76a1b27e8896780`
- `COMMITTED`: `lib/ranking.ts; scripts/run-stable-ranking.mjs`
- `MODIFIED_TRACKED`: `lib/signals.ts; package.json`
- `UNTRACKED`: `scripts/stable-ranking-cases.cjs`
- `STABLE_RANKING_CASES`: `5`
- `REPEATS_PER_CASE`: `5`
- `FIVE_EXECUTION_LOGS_BYTE_IDENTICAL`: `TRUE`
- `TYPECHECK`: `PASS`
- `PRODUCTION_BUILD`: `PASS`
- `NETWORK`: `DENIED_BY_SEATBELT`
- `PRIVATE_MARKER_MATCHES`: `0`
- `CAPTURE_STARTED`: `FALSE`

The pure comparator orders by relevance score, publication time, and signal ID
without mutating its input. The application integration, deterministic cases,
typecheck, production build, and five byte-identical test repetitions pass.
Capture requires Kenneth's separate exact-state declaration.
