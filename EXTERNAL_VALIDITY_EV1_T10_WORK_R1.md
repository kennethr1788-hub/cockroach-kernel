# EV1-T10 Work R1

- `STATUS`: `EV1_T10_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED`
- `TASK_ID`: `EV1-T10`
- `UTC_RECORDED`: `2026-07-30T22:25:13Z`
- `TASK_COMMIT`: `5c671337842dc3ece20aa969f4bdec95eacc4203`
- `COMMITTED`: `scripts/validate-release-notes.mjs`
- `MODIFIED`: `docs/RELEASE.md`
- `UNTRACKED`: `.github/release-notes-template.md`
- `PRETTIER`: `GREEN_OFFLINE`
- `VALIDATOR_REPEATS`: `5_IDENTICAL_GREEN`
- `NEGATIVE_CASES`: `5_OF_5_REJECTED`
- `NEGATIVE_CLASSES`: `MISSING,DUPLICATE,REORDERED,OVERSIZED,SYMLINK`
- `PRIVATE_PACKAGE`: `TRUE`
- `VALIDATOR_NETWORK_OR_PUBLISH_SURFACE`: `FALSE`
- `HUMAN_EDIT_REQUIRED`: `FALSE`
- `PUBLIC_ACTION`: `FALSE`
- `WORK_RECEIPT_FILE_SHA256`: `d07d850130d7a2539c251cce53aa35ff02fbc3a6d3bcc9e5e129b8387a4eb691`
- `WORK_RECEIPT_SHA256`: `b77916c6cbb6b2594b114a718ee34fd9aa745013d5924185e75ab6396c7bce5f`
- `CAPTURE_STARTED`: `FALSE`
- `DELETION_STARTED`: `FALSE`

## Declared hashes

- `.github/release-notes-template.md`:
  `5588692402cabf72e89da0fa6d791d8bfacfbe6d33920e1d3135deb3158053f2`
- `docs/RELEASE.md`:
  `e412093cd49a28724fd9d4c218031d8850961afd4ff6507253228d1bcf07f4b8`
- `scripts/validate-release-notes.mjs`:
  `1320a79ab991e04055ec9f24ee60f25028cec86b10bf8dc8dfab7d1a1dcc17e8`

The bound acceptance command passes without network access. Five repeated
validator runs are byte-identical. Missing, duplicated, reordered, oversized,
and symlinked templates each fail closed. The pre-capture table-format repair
is preserved separately. Exact-state human declaration remains required before
capture or any guarded deletion.
