# P6 Frozen Contract

- `PHASE`: `P6`
- `PARENT_GATE`: `CK_P5_LANES_GREEN`
- `START_COMMIT`: `2951cf9b9f2ffb24ac683f3437192131a93bfdd5`
- `TARGET_GATE`: `CK_P6_QUORUM_GREEN`
- `STATUS`: `FROZEN_BEFORE_IMPLEMENTATION`

Implement a typed Thinker → Worker → Verifier workflow in which model and
persona outputs remain untrusted evidence. Every handoff binds exact task,
input-state, trajectory, policy, lane-output, candidate, schema, parent
handoff, and parent-receipt hashes. Unknown fields, stale linkage, replay, and
duplicate transitions fail closed.

Deterministic authority rules:

- ordinary actions require 3 independent approvals from five lanes;
- critical recovery actions require 4 independent approvals from five lanes;
- three approvals can never silently satisfy a critical action;
- split/tie, missing quorum, timeout, and failed-lane states refuse;
- duplicate evaluator votes are invalid;
- four or more materially correlated output hashes refuse;
- explicit policy veto overrides any model consensus;
- all dissent is retained in deterministic lane order;
- reason codes and canonical hashes are deterministic;
- the authoritative transition and immutable receipt commit atomically in a
  retry-safe CockroachDB serializable transaction.

Required vectors: ordinary approval, critical approval, three approvals on a
critical action, four correlated approvals, unanimous unsafe consensus under
policy veto, split vote, tie, timeout, failed lane, missing quorum, duplicate
vote, stale handoff, evaluator replay, interrupted commit, transaction retry,
rollback, and five-repeat determinism.

Required contributors:

- Kimi: typed state machine, schemas, fixtures, and non-authoritative plumbing.
- Vibe: quorum, dissent, timeout, failure, replay, correlation, and transaction
  fault vectors.
- Devstral: typed handoff/configuration boundaries, restart fixtures, and
  clean-state acceptance checks.
- Codex: quorum semantics, policy-veto and transition authority, integration,
  transaction proof, evidence, and packet.

Required judges after mechanical evidence: GLM plus Claude on one exact packet
hash. Neither builder nor model output can close the gate.

Kill line: any false quorum, critical-to-ordinary fallback, correlation bypass,
policy-veto bypass, replay acceptance, non-atomic transition, missing dissent,
private-data egress, or required-judge failure leaves `CK_P6_BLOCKED`.
