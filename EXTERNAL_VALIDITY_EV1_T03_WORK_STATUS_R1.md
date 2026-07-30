# EV1-T03 Work Status R1

- `STATUS`: `EV1_T03_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED`
- `TASK_ID`: `EV1-T03`
- `TASK_START_UTC`: `2026-07-30T17:22:37Z`
- `WORK_RECORDED_UTC`: `2026-07-30T17:27:35Z`
- `BACKLOG_SHA256`: `6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `SOURCE_COMMIT`: `1a92380a9edf12337f80b3c42ba098a7c1724664`
- `SOURCE_MANIFEST_SHA256`: `d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706`
- `PREPARATION_FILE_SHA256`: `9454933b309121e7a8e4557dca0f7e444a90870fbc386f8bf58c426b5c46904a`
- `PREPARATION_RECEIPT_SHA256`: `595b420b43988da1179e386d23dd34dbffd5aa97233ba1f1edc1ba266ec5dedc`
- `TASK_COMMIT`: `b18edb6f9b2b1c126e38c6fe218a167fe7ac7ca4`
- `WORK_RECEIPT_FILE_SHA256`: `a79ca9fca84602471b0640c31adbe5dc0feadbb3d6981fce43f7919c56492f5d`
- `WORK_RECEIPT_SHA256`: `3afe529af6f359cbe412e4e16a01ce4eb2a79392cff7e533901c7b9f08f04488`
- `CAPTURE_STARTED`: `FALSE`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`

## Exact task state

- committed: `scripts/run-recipe-invariants.mjs`
- modified tracked: `package.json`
- untracked: `scripts/recipe-invariant-cases.cjs`
- aggregate declared bytes: `8691`
- private-marker matches: `0`

## Offline acceptance

- typecheck: `PASS`, log SHA-256 `7ad5370190f3f13153e8329d717ccdfec065241392cd850b68579e68731ca022`
- production build: `PASS`, log SHA-256 `7dadde573ac0a6cc8e8f5fb07ac27b09dda55162be2f1071e8b991e9f626078c`
- recipe invariants: `PASS`, log SHA-256 `907a86f674596dea4f981f07fb8d083bface8ca6d69cd7f71253f92b985c6d80`
- five deterministic repeats: `PASS`, one identical log SHA-256 `907a86f674596dea4f981f07fb8d083bface8ca6d69cd7f71253f92b985c6d80`
- temporary test residue: `0`

The seven deterministic cases exercise monotonic version labels, exclusive
favorite and dial-in pointers, state-preserving cross-group rejection for both
pointer types, single-version Quick Brew cascade cleanup, and whole-group Quick
Brew cascade cleanup. No product-candidate file was changed.

The next protocol step is Kenneth's exact capture declaration. Capture,
guarded deletion, recovery, and any task verdict remain forbidden until that
human-only declaration is recorded and the task-specific execution preflight
passes.
