# P5 Frozen Contract

- `PHASE`: `P5`
- `PARENT_GATE`: `CK_BUNDLE_A_GREEN`
- `START_COMMIT`: `d93c19ab8691e3ba00b0401160b0ac0c7f669f5a`
- `TARGET_GATE`: `CK_P5_LANES_GREEN`
- `STATUS`: `FROZEN_BEFORE_IMPLEMENTATION`

Implement five advisory lanes: syntax/structure, security/policy,
logic/coherence, contextual fit, and trajectory alignment. Each selects no
more than three hash-pinned inert persona traits. Persist strict canonical
lane manifests and results with task, trajectory, candidate, policy, prompt,
route, served-model, output, retry, timeout, dissent, and receipt linkage.

No lane or persona may use tools, mutate authority, change policy, call another
agent, or decide promotion. Unknown fields, stale hashes, duplicate results,
malformed outputs, trait-limit violations, injection/tool requests, and missing
lanes fail closed.

Required contributors:

- Kimi: manifest loader, lane adapters, schema and fixtures.
- Vibe: timeout/retry/malformed/duplicate/conflict/injection tests.
- Devstral: typed configuration, isolation, provenance, and clean-state boundary review.
- Codex: authority semantics, integration, test replay, evidence, and packet.

Required judge roles after mechanical tests: GLM plus AGY on one sanitized
packet hash. Any non-GREEN result blocks P6.

Kill line: any authority escalation, private-data egress, unknown-field
acceptance, nondeterministic hash, missing provenance, or unavailable required
judge leaves `CK_P5_BLOCKED`.

