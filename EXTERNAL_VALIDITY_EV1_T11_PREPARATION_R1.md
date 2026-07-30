# EV1-T11 Preparation R1

- `STATUS`: `EV1_T11_READY_FOR_TASK_WORK`
- `SOURCE`: `PUBLIC_MIT_STEP_REALTIME_CLI`
- `SOURCE_COMMIT`: `ee6862f7d65d24d4de11eda8306d29356873b529`
- `SOURCE_FILES`: `410`
- `SOURCE_MANIFEST_SHA256`: `6f81e7e81ad100b53163a13b11c5e7abcd437fe658f817e34905c02cbe0e7182`
- `DISPOSABLE_BASELINE_COMMIT`: `fadda411374331866368c3ee3edfa02e7f221d03`
- `PREPARATION_RECEIPT_FILE_SHA256`: `3d4e7dc29fb7e8eef17b4ebc13ece6ac9d056d523cb6677067c25a703edd2139`
- `PREPARATION_RECEIPT_SHA256`: `6098fad3ca259498bb35a8753aa6251bc64e125f28fddc554e345ae3b469171b`
- `DEPENDENCY_CANARY`: `R4_GREEN`
- `DEPENDENCY_MANIFEST_SHA256`: `bda7fc8f96d452960e7174cc6b84f05708f763ebf2e10dbdd40a1eca87b06dbe`
- `BASELINE_TESTS`: `84_FILES_PASS; 1475_TESTS_PASS; 7_SKIP; 0_FAIL`
- `NETWORK`: `DENIED_SEATBELT`
- `TASK_SURFACE_BEFORE_WORK`: `ABSENT`
- `PUBLIC_ACTION`: `NONE`

The workspace was exported from the exact public source commit into the
campaign-local disposable root. The requalified dependency runtime was cloned
with byte-identical manifest and declared pnpm links, with no install or
lifecycle script. Baseline Prettier and the full unchanged test suite passed
offline before task work.
