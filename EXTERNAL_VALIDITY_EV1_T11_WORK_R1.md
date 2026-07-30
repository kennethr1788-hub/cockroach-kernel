# EV1-T11 Work R1

- `STATUS`: `EV1_T11_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED`
- `TASK_COMMIT`: `36790fe0c7c6badae07ae95e1383a051746f1a8c`
- `COMMITTED`: `scripts/check-release-readiness.mjs`
- `MODIFIED_TRACKED`: `docs/RELEASE.md`
- `UNTRACKED`: `scripts/release-readiness-cases.json`
- `WORK_RECEIPT_FILE_SHA256`: `c8c0ed7b92f3955bb2b88d4a7781b1c990faff5b6732914da32cdc7304639b50`
- `WORK_RECEIPT_SHA256`: `7936cf4a3a2266e2fe2f0f53e5b498e0d869f1ee8b330e6fe0cc4dd72abbf323`
- `PRETTIER`: `GREEN_OFFLINE`
- `DRY_RUN_REPEATS`: `5_BYTE_IDENTICAL`
- `DRY_RUN_OUTPUT_SHA256`: `d858812f994319a318157aa47e66de7a381cea1368216a759ec30096a3db7207`
- `PUBLISH_ACTION`: `REFUSED_ROOT_PRIVATE`
- `ADVERSARIAL_CASES`: `8_OF_8_REJECTED`
- `FULL_TESTS`: `84_FILES_PASS; 1475_TESTS_PASS; 7_SKIP; 0_FAIL`
- `NETWORK_PROCESS_OR_WRITE_SURFACE`: `ABSENT_BY_STATIC_ALLOWLIST`
- `ADVERSARIAL_RESIDUE`: `0`
- `CAPTURE_STARTED`: `NO`
- `DELETION_STARTED`: `NO`
- `RECOVERY_STARTED`: `NO`

The guard validates local SemVer metadata, required repository files, CLI and
test metadata, and `workspace:*` bindings using read-only Node standard-library
surfaces. It accepts only `--offline-dry-run`, emits deterministic canonical
JSON, and never authorizes publication. Missing arguments, publish-like
arguments, non-private metadata, invalid versions, unresolved or inconsistent
workspace bindings, missing binary targets, and missing license evidence all
failed closed.

This is work evidence, not recovery evidence. Kenneth's exact-state declaration
and a fresh task-specific independent execution preflight are required before
capture, guarded deletion, or recovery.
