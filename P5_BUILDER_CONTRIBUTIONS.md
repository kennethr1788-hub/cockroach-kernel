# P5 Builder Contributions

- `UTC_UPDATED`: `2026-07-26T00:07:48Z`
- `PHASE`: `P5`
- `AUTHORITY_OWNER`: Codex
- `STATUS`: implementation candidate; not a GREEN gate

## Kimi

- Route: official managed OAuth, `kimi-code/k3`
- CLI version: `0.27.0`
- Binary SHA-256: `550bca0ba6e474f4e0faeadfae03a9294c7c25688670f38ff488ab8cf176d817`
- Scope: isolated `p5-kimi` worktree; `p5-lanes/` only
- Contribution: manifest/result schemas, fixture generator, canonical fixtures,
  deterministic advisory aggregation, and 13 focused tests
- Original focused result: 13/13 passing
- Accepted with Codex changes: explicit persona source-file hashes, stricter
  manifest provenance, strict prompt/output schemas, output injection scan,
  and CockroachDB persistence/integration proof
- Limitation: Kimi did not decide authority or P5 acceptance.

## Devstral

- Wrapper: `14.0.0`
- Wrapper SHA-256: `7fba7da72e8899633e0a916ad6ac792d3bade1c36bc003f32c29f1e76f0678f3`
- Requested/served model: `mistral-medium-3-5`
- Scope: one sanitized no-tool boundary review
- First attempt: blocked, empty final provider text, exit `45`
- Second attempt: exit `0`, exact model match
- Raw accepted boundary output:

```text
TYPED_CONFIGURATION: Accepts only canonical JSON with strict schema enforcement; rejects unknown fields and malformed structures.
ISOLATION: Lanes are inert (no tools, mutations, or external calls); deterministic aggregation prevents cross-lane interference.
PROVENANCE: Mandatory provenance tracking for all outputs; rejects missing or tampered lineage.
CLEAN_STATE: Immutable hash-pinned traits; rejects stale hashes, duplicates, or injection attempts.
LIMITATIONS: Fixed to five lanes (1–3 traits each); no dynamic scaling, promotion, or policy overrides.
```

The output was advisory only and did not supply code or acceptance authority.

## Vibe

- CLI version: `2.21.0`
- Binary SHA-256: `49eda5eccca6991033113b0cf30ea7b740078d222d4a74a97d667db14e3da4a4`
- Route: native bounded `plan` agent with only `read_file` and `grep`
- Scope: isolated synthetic worktree; no edits or external tools
- First attempt: stopped at one-turn bound without a final contribution
- Second attempt: exit `0`; proposed ten bounded adversarial vectors
- Accepted findings: retry and timeout upper bounds were absent; explicit
  boundary/type tests were missing; prompt/output injection and dissent linkage
  deserved separate coverage.
- Rejected as factually incorrect: the claim that integer types were not
  enforced; the implementation already rejected non-integer values. Separate
  boolean-confusion tests were added because Python booleans are integers.
- Codex-integrated result: bounded retry/timeout enforcement and seven
  adversarial tests in `test_manifest_adversarial.py`.

## Codex integration evidence

- Focused unit and adversarial tests: 20/20 passing
- Two fresh-root CockroachDB trials: 5 manifests, 5 results, 5 advisory
  verdicts; duplicate output rejected; database result hashes matched fixture
  hashes; aggregate hash stable at
  `9e95250c7f7c9328f04c5b3d7b4b8694e0606885cb3e62005de086b2f5b99aaa`.
- No P5 judge has run yet; this file cannot close the gate.
