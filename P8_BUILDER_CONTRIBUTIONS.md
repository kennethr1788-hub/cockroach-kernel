# P8 Builder Contributions

- `UTC_UPDATED`: `2026-07-26T10:49:32Z`
- `PHASE`: `P8`
- `AUTHORITY_OWNER`: `Codex`
- `STATUS`: `IMPLEMENTATION_CANDIDATE_NOT_A_GATE`

## Kimi K3

- Binary: Kimi Code `0.27.0`
- Binary SHA-256:
  `550bca0ba6e474f4e0faeadfae03a9294c7c25688670f38ff488ab8cf176d817`
- Route: managed Kimi Code OAuth, requested `kimi-code/k3`.
- Contained-worker attempt: failed closed with
  `managed K3 max-effort contract missing`; no files changed.
- Headless worktree attempt: timed out, then bounded retries were terminated;
  no files changed.
- Direct bounded OAuth attempt: exit 0 and returned a stale-base proposal
  fixture. The stale-base vector was accepted as useful and was already
  represented by `proposal-stale.json`. The returned candidate policy used an
  invalid integer schema version, so those bytes were rejected rather than
  copied.
- Authority: none. Kimi did not edit authoritative code or decide P8.

## Vibe

- Version: `2.21.0`
- Binary SHA-256:
  `49eda5eccca6991033113b0cf30ea7b740078d222d4a74a97d667db14e3da4a4`
- Route: isolated `plan` agent, synthetic prompt, no edit authority.
- File-review attempts: exhausted bounded turn/token limits without a usable
  final result; no files changed.
- Final no-file adversarial pass: exit 0 and returned five vectors covering
  ordinary/critical quorum underflow, correlation lower/upper bounds, and
  frozen-set hash drift.
- Accepted correction: add explicit correlation-limit-underflow fixture and
  test. The other vectors were already directly covered.
- Authority: none. Vibe did not decide P8.

## Devstral

- Wrapper: `14.0.0`
- Wrapper SHA-256:
  `7fba7da72e8899633e0a916ad6ac792d3bade1c36bc003f32c29f1e76f0678f3`
- Requested and served model: `mistral-medium-3-5` (sentinel exit 0).
- Scope: sanitized one-turn, no tools, no paths, no raw code.
- First high-reasoning call: failed closed with empty final provider text,
  exit 45.
- Second call: exit 0 and returned five boundary findings.
- Accepted correction: explicitly replay duplicate rollback and prove the
  conflicting receipt aborts atomically while the restored prior policy remains
  golden.
- Already covered: interrupted promotion leaves zero partial state; duplicate
  completed promotion is idempotent; rollback receipt binds prior/current
  policy hashes.
- Rejected finding: rejected reflection proposals are not teardown orphans;
  they are required immutable incident/reflection evidence.
- Authority: none. Devstral did not decide P8.

## Codex reconciliation

- Added the strict policy/incident/proposal schemas and pure authority function.
- Added total outcome receipts, a hash-bound golden validation pair, and exact
  rollback receipts.
- Added the CockroachDB schema and two fresh-root SERIALIZABLE transaction
  trials.
- Added the Vibe correlation-underflow vector and the Devstral duplicate
  rollback proof.
- Final focused unit result: `15/15 PASS`.
- Final inherited-plus-P8 unit result: `116/116 PASS`.
- Final fresh-root integration result: `2/2 PASS` with identical semantics.

No contributor output in this file closes P8. The same-hash independent judge
workflow remains mandatory.
