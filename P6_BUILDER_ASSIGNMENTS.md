# P6 Builder Assignments

All inputs are synthetic and non-sensitive. No builder may access credentials,
HOME runtime, live memory, client data, deployment, AWS, RunPod, or later
phases.

- Kimi owns the bounded proposal for `p6-quorum/state_machine.py`, fixtures,
  and focused tests in an isolated worktree.
- Vibe performs a bounded read-only adversarial review of the accepted P6
  candidate; Codex implements accepted fault vectors with `apply_patch`.
- Devstral performs one sanitized no-tool boundary review; it receives the
  contract only, never paths, raw private data, or repository access.
- Codex owns all authoritative semantics, review, integration, CockroachDB
  transaction proof, evidence, and judge packet.

Every contribution must record route, model, scope, output, accepted/rejected
findings, tests, and limitations.
