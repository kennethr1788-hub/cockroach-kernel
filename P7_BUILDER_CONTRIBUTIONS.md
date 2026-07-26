# P7 Builder Contributions

- `UTC_UPDATED`: `2026-07-26T01:23:38Z`
- `IMPLEMENTATION_COMMIT`: `08de647c4f910cdd22905980511702bd20eeffb1`
- `DATA_CLASS`: synthetic and non-sensitive only

## Kimi

- Route requested: the current official OAuth `kimi-code/k3` headless route in
  an isolated worktree.
- The managed `kimi-codex-worker` preflight rejected stale effort metadata and
  made no project or HOME mutation.
- One direct OAuth attempt ran for the bounded 600-second window, exited `142`,
  and produced an incomplete worktree proposal. It did not close any gate.
- Accepted after Codex review: the strict record/fixture direction and the
  initial fresh-context adapter structure.
- Rejected/replaced: the incomplete test rewrite, any implied authority, and
  every unverified or inconsistent fragment. Codex rewrote the integrated
  tests and retained authority over selection, warrants, filesystem loss, SQL,
  integration, and evidence.
- Kimi version: `0.27.0`.
- Kimi binary SHA-256:
  `550bca0ba6e474f4e0faeadfae03a9294c7c25688670f38ff488ab8cf176d817`.
- Headless wrapper SHA-256:
  `fa900e8233648e712d972b96b7b818b02d81ad74183f94521204e863c1fdd95f`.

## Devstral

- Scope: sanitized, no-tool boundary review; no repository, HOME, credential,
  network, deletion, promotion, or judge authority.
- The exact served-model sentinel passed for `mistral-medium-3-5`.
- The first high-reasoning attempt returned an empty final response and exit
  `45`; it was rejected.
- The bounded no-reasoning retry returned five usable boundary observations:
  normalized path controls; pre-write manifest/hash checks; owned teardown;
  empty active state; and fail-closed one-use warrants.
- Codex independently implemented and tested those boundaries.
- Wrapper SHA-256:
  `7fba7da72e8899633e0a916ad6ac792d3bade1c36bc003f32c29f1e76f0678f3`.

## Vibe

- Version: `2.21.0`.
- Binary SHA-256:
  `49eda5eccca6991033113b0cf30ea7b740078d222d4a74a97d667db14e3da4a4`.
- Scope: read-only adversarial review of the accepted candidate; no edits or
  commands.
- It independently classified all eleven declared P7 vectors as covered and
  found one concrete gap: malformed context dictionaries could surface a raw
  `KeyError` instead of a stable refusal.
- Codex accepted that finding, added fail-closed `validate_context`, and added
  a regression test. No Vibe-authored code entered the implementation.

## Codex

- Authored and owns the integrated strict canonical records, file-byte
  bindings, deterministic maximum-prefix selector, one-use warrant behavior,
  guarded declared-loss harness, CockroachDB schema and serializable state
  transitions, fresh-context byte verification, tests, evidence, and packet.
- Reviewed every external contribution as untrusted; accepted findings are
  represented only through Codex-owned implementation and tests.
- Final mechanical result before packet freeze: 29/29 unit tests and two of
  two fresh-root CockroachDB integration trials passed.

No contributor was used as a judge. Claude and AGY have not authored or shaped
this implementation and remain eligible for the P7 gate.
