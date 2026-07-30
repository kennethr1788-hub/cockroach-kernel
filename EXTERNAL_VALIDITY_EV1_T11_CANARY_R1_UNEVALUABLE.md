# EV1-T11 Dependency Canary R1 — Unevaluable

- `STATUS`: `EV1_T11_DEPENDENCY_CANARY_R1_UNEVALUABLE`
- `CLASSIFICATION`: `HARNESS_EVIDENCE_LOSS`
- `TASK_WORK_STARTED`: `NO`
- `PRODUCT_CANDIDATE_CHANGED`: `NO`
- `SOURCE_REPOSITORY_CHANGED`: `NO`
- `SURVIVING_TEMP_ROOT`: `NONE_OBSERVED`
- `SURVIVING_PROCESS`: `NONE_OBSERVED`
- `RESULT_USABLE_AS_EVIDENCE`: `NO`

The first exploratory canary sent the unchanged `pnpm test` output through a
bounded terminal result that was truncated before its exit status could be
retained. Its shell also used `set -e`, so the intended status-recording branch
could not run after a nonzero command. At recovery, no matching temporary root
or Vitest/pnpm process remained. Containment therefore closed, but the test
verdict is unrecoverable and must not be inferred.

The attempt also linked a quarantined `node_modules` tree into the temporary
workspace. Inspection subsequently found 14 workspace-relative symlinks that
are broken at the quarantine location. A corrected canary must copy-on-write
clone the tree into the fresh workspace so those links resolve against the
original topology, retain logs and a canonical receipt outside the temporary
root, and clean up regardless of command exit.
