# Independent GLM 5.2 Contract Audit Instructions

You are the independent, non-authoring judge. Review only the exact contract
bytes appended after these instructions. Do not write code, patches, or an
implementation plan. Do not use tools or claim evidence not present.

## Decision requested

Return whether the R3 contract is safe and complete enough to permit the Codex
builder to implement the scenario-driven public recovery surface. This is a
contract gate, not product evidence or black-box execution approval.

## Proven starting blocker

The old frozen product candidate exposed only `demo` and `inspect`. A public
probe ran two distinct disposable workspaces and received identical canned demo
results. Independent GLM 5.2 confirmed `FROZEN_CLI_NOT_SCENARIO_DRIVEN` and
required a separately authorized product revision, new candidate, revised
plan, and fresh preflight. No hidden seed or actor execution exists.

Bindings:

- old candidate: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- R1 blocker packet SHA-256: `b1be8da1e8787f1d79bdfeed9c5fe4a14248cb686aac2b698ecbd39e823c1767`
- R1 GLM receipt SHA-256: `372846a693754d9e54337c7476baa7ac9536d823ed963b6625dd96e4a79903ab`
- R2 plan SHA-256: `4453424a60e0cb591bde3a7a6da5ceeb7bd752b8cf9dd6abba785b42c61f32cc`

## Review criteria

1. Deterministic binding to external typed inputs rather than a renamed replay.
2. Reuse of existing P7 validation and selection authority without a weaker
   parallel selector.
3. Safe path/root/symlink/executable/size boundaries before mutation.
4. Exact-byte representation validation and no invented uncaptured bytes.
5. Persistent one-use custody, locking, atomic fsync persistence, and
   fail-closed interruption semantics.
6. Zero workspace mutation for refusal, invalid, and no-loss controls.
7. Clear verdict/reason/exit-code and evidence contracts.
8. Test completeness for complete, partial, no-loss, tamper, replay,
   interruption, malformed, unsupported, and unsafe scenarios.
9. Preservation of old evidence, no hidden execution, no cloud/public/Gate 7
   authority, and no runtime dependency expansion.
10. Any ambiguity that could let implementation claim more than it restores.

## Required output

Return exactly this structure:

```text
VERDICT: GREEN | NOT_GREEN | BLOCKED
SERVED_MODEL: glm-5.2
RECUSAL: CLEAR | REQUIRED
BLOCKERS:
- <none or exact blocker>
NON_BLOCKING_RISKS:
- <none or exact risk>
EVIDENCE_REQUIRED_AFTER_IMPLEMENTATION:
- <direct evidence item>
```

GREEN means the contract may be implemented. It does not certify code, allow a
hidden seed, authorize an actor call, or start Gate 7.
