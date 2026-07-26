# P6 Builder Contributions

- `UTC_UPDATED`: `2026-07-26T00:35:19Z`
- `PHASE`: `P6`
- `AUTHORITY_OWNER`: Codex
- `STATUS`: implementation candidate; not a GREEN gate

## Kimi

- Route: official managed OAuth, `kimi-code/k3`
- Binary SHA-256: `550bca0ba6e474f4e0faeadfae03a9294c7c25688670f38ff488ab8cf176d817`
- Scope: isolated `p6-kimi` worktree; `p6-quorum/` only
- Contribution: strict canonical records, typed Thinker-to-Worker and
  Worker-to-Verifier handoffs, deterministic quorum rules, intent/receipt
  shapes, synthetic fixtures, an in-memory atomic-commit harness, and focused
  tests.
- Original focused result: 38/38 passing.
- Limitation: the proposal did not prove a real CockroachDB transaction and
  did not decide P6 acceptance.

## Devstral

- Wrapper SHA-256: `7fba7da72e8899633e0a916ad6ac792d3bade1c36bc003f32c29f1e76f0678f3`
- Requested/served model: `mistral-medium-3-5`
- Scope: sanitized no-tool boundary review of the frozen contract.
- Accepted findings: handoffs must be exact-schema and hash-bound;
  quorum/veto configuration must be immutable; restart handling must reject
  replay/stale state; duplicate, tie, split, and correlation cases require
  clean-state refusal.
- Rejected finding: treating policy-veto authority as an availability defect.
  The frozen safety contract intentionally requires policy veto to override
  unanimous model consensus.
- Limitation: advisory only; no code, tools, or gate authority.

## Vibe

- CLI version: `2.21.0`
- Binary SHA-256: `49eda5eccca6991033113b0cf30ea7b740078d222d4a74a97d667db14e3da4a4`
- Route: native bounded `plan` agent with only `read_file` and `grep`.
- Scope: read-only review of five P6 files; no edits and no commands.
- Result: nine of ten requested vector classes were directly evidenced.
  The sole gap was a direct negative test for an unknown vote-status enum.
- Accepted correction: `test_unknown_vote_status_rejected` now proves
  `PENDING` fails with `MALFORMED_RECORD`.
- Limitation: advisory only; no implementation or gate authority.

## Codex integration

- Added strict boolean/type/range validation to authority records.
- Added same-task/different-intent conflict refusal to the in-memory harness.
- Added the real CockroachDB schema and two-fresh-root integration harness.
- Proved an invalid receipt aborts the entire transaction (`0 transitions / 0
  receipts`), explicit rollback leaves zero transitions, and retry commits one
  linked transition and receipt.
- Final mechanical result before packet freeze: 41/41 unit tests and two of
  two fresh CockroachDB trials passed.
- Secret scans: gitleaks found no leaks; detect-secrets returned an empty
  result set. No P6 temporary database root or symlink remained.

No contributor result in this file closes P6. GLM and Claude must judge one
exact frozen packet hash.
