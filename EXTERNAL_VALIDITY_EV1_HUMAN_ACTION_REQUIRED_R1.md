# EV1 Human Action Required R1

- `STATUS`: `EV1_R2_SOURCE_BINDING_CONFIRMATION_BLOCKED`
- `LAST_GREEN_GATE`: `LIVE_CONTINUITY_EVIDENCE_GREEN`
- `BACKLOG_CANDIDATE_SHA256`: `34ffed70e3d52cde2e94e5f3b66dd96cdac1f2aa7de757b11bf6580bb5e536e4`
- `R2_BACKLOG_CANDIDATE_SHA256`: `6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5`
- `CURRENT_COMMIT_BEFORE_DRAFT`: `31cc6c7531851fc3075d5fbe0176c013c80df1a9`
- `MEASURED_TASKS_STARTED`: `0`
- `MEASURED_CLOCK_STARTED`: `FALSE`
- `MISSING_FACT`: `Kenneth's confirmation that EV1-T01 through EV1-T04 may use the deterministic 76-file Brew Ledger export that excludes CLAUDE.md and is bound by manifest SHA-256 d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706.`
- `EVIDENCE_REQUIRED`: `Kenneth reviews EXTERNAL_VALIDITY_EV1_BACKLOG_CANDIDATE_R2.md and confirms its exact SHA-256. The R1 confirmation remains preserved but cannot cover the corrected source binding.`
- `NEXT_SAFE_ACTION`: `Hash and present the R2 candidate for Kenneth's review. After exact-hash confirmation, freeze it byte-identically and rerun the full mechanical and same-hash judge preflight.`
- `FORBIDDEN`: `Silently stripping CLAUDE.md under the R1 confirmation; beginning EV1-T01; starting the measured clock; fabricating human edits or observations; changing task order; changing the product candidate; or making public claims.`

R1 authenticity is preserved, but its source-boundary attestation was contradicted
by preflight. R2 changes only the sanitized export binding and requires a fresh
human confirmation before execution.
