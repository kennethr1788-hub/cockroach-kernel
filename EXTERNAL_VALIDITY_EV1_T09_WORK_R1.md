# EV1-T09 Work R1

- `STATUS`: `EV1_T09_WORK_GREEN_HUMAN_EDIT_REQUIRED`
- `TASK_COMMIT`: `3210c33c2a551f64d8a89270bfbc24d212f9d3ec`
- `COMMITTED`: `scripts/validate-release-policy.mjs`
- `MODIFIED_TRACKED`: `docs/RELEASE.md`
- `UNTRACKED`: `scripts/release-policy-cases.json`
- `PRE_HUMAN_RECORDER_SHA256`: `cfcbc2e0df6af405271f150c783c3a8d7b227be6b048d65b83a39dcf84d1f8a3`
- `PRE_HUMAN_RECEIPT_FILE_SHA256`: `defec3b52f298dabdf2ec419c1c4297371b94c0813dca68ca1fe2e63eab4d3e0`
- `PRE_HUMAN_RECEIPT_SHA256`: `e58c628c112d63ef17e3eebc0c81c33761fc7ab2212df2ba765941f81b881575`
- `PINNED_PNPM`: `10.17.0; b276da51dc8ca5b0d3ee3371695b50fc8b3244b281b091c63a3f082a88dadeb9`
- `PINNED_PRETTIER`: `3.8.1; ac5523cd57e7e9d8eac71caef7e022a8a8489bcdc19ca8a778b7e728ec103b93`
- `PRETTIER_OFFLINE`: `PASS`
- `STRUCTURAL_POLICY_OFFLINE`: `PASS_WITH_FROZEN_HUMAN_PLACEHOLDER`
- `REQUIRED_HUMAN_GATE`: `FAIL_CLOSED; HUMAN_RELEASE_PRINCIPLE_REQUIRED`
- `PRIVATE_PACKAGE_SAFEGUARD`: `PASS`
- `VALIDATOR_NETWORK_OR_PUBLISH_SURFACE`: `ABSENT`
- `DEPENDENCY_ATTEMPT_R1`: `QUARANTINED; NOT_ACCEPTANCE_EVIDENCE`
- `CAPTURE_DELETION_RECOVERY`: `NOT_STARTED`

Everything except the human-owned sentence is mechanically ready. The exact
acceptance command intentionally exits 1 while the frozen marker remains. Codex
must not write, suggest, or substitute the sentence. Kenneth must personally
replace the marker in `docs/RELEASE.md`, visibly save the file, and confirm that
action before the task may be captured.
