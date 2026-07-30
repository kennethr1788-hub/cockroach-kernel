# EV1-T04 Work Status R1

- `STATUS`: `EV1_T04_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED`
- `TASK_ID`: `EV1-T04`
- `TASK_START_UTC`: `2026-07-30T17:54:06Z`
- `WORK_RECORDED_UTC`: `2026-07-30T18:01:01Z`
- `BACKLOG_SHA256`: `6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `SOURCE_COMMIT`: `1a92380a9edf12337f80b3c42ba098a7c1724664`
- `SOURCE_MANIFEST_SHA256`: `d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706`
- `PREPARATION_FILE_SHA256`: `27ce9f904902d6d322776504bc79d9b4f8dddc968820c305bf996b6f323e0809`
- `PREPARATION_RECEIPT_SHA256`: `f38d933177ee6674d082cea1a175673fa4ae94d3444206123788d76e2c32b3bd`
- `TASK_COMMIT`: `c27bb9b9023a5b8ce4f5fb7cfa8fdf9d157b3502`
- `WORK_RECEIPT_FILE_SHA256`: `85c06807367cc77150569e423d54e07374959b8a7dd58f016f8abf3b3081d7fd`
- `WORK_RECEIPT_SHA256`: `11ca3d8872f6207eabd9e7f520cee4638644880d7faab907d467766ad5a2d8f2`
- `CAPTURE_STARTED`: `FALSE`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`

## Exact task state

- committed: `scripts/run-dashboard-date.mjs`, `src/lib/dashboardDate.ts`
- modified tracked: `package.json`, `src/app/page.tsx`
- untracked: `scripts/dashboard-date-cases.cjs`
- aggregate declared bytes: `18798`
- private-marker matches: `0`

## Offline acceptance

- Pacific dashboard-date cases: `PASS`, log SHA-256 `6a49b3300432981db63192f716d657b1c0be0e349741eca2abda50a6c5f0a518`
- UTC dashboard-date cases: `PASS`, log SHA-256 `89dca994eb91dabf30dc51461087037c89841ac0319ae55cb100b736120cb40c`
- typecheck: `PASS`, log SHA-256 `7ad5370190f3f13153e8329d717ccdfec065241392cd850b68579e68731ca022`
- production build: `PASS`, log SHA-256 `15e394e44bc876e5566f92abb1f10f35138b101f632520040cc96c013f7a41ad`
- five deterministic repeats per timezone: `PASS`
- temporary test residue: `0`

The pure helper takes an explicit reference instant, excludes invalid timestamps,
uses a stable tie-break, and contains zero implicit wall-clock reads. The fixed
late-Pacific brew remains on the reference instant's local calendar day under
both declared process timezones. No product-candidate file was changed.

The next protocol step is Kenneth's exact capture declaration. Capture, guarded
deletion, recovery, and any task verdict remain forbidden until that human-only
declaration is recorded and the task-specific execution preflight passes.
