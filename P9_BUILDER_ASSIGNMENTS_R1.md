# P9 Offline Builder Assignments R1

All assignments are local, synthetic, sanitized, isolated, and non-authoritative.
No builder receives credentials, browser state, live account identifiers, raw
private data, judge outputs, or deployment authority.

## Kimi K3

- Persona lens: Athena + Daedalus + Argos Panoptes.
- Allowed outcome: propose implementation in an isolated worktree for the
  standard-library Lambda handler, strict request/response records, deterministic
  context-vector helper, local transport mocks, and migration scaffolding.
- Forbidden: credentials, cloud calls, deployment, live SQL, authority verdicts,
  contract edits, packet edits, judge work, HOME writes.

## Vibe

- Persona lens: Mythos + Talos + Themis.
- Allowed outcome: reliability and adversarial tests in an isolated worktree for
  40001 retries, idempotency, duplicate/stale results, timeout/throttle faults,
  changefeed lag/restart, MCP injection/write refusal, denial-of-wallet, and
  evidence growth.
- Forbidden: credentials, cloud calls, deployment, production data, authority
  changes, contract edits, packet edits, judge work, HOME writes.

## Devstral

- Persona lens: Curator + Soteria + Vault-Recall.
- Allowed outcome: typed configuration, exact IAM/SQL matrices, project-local CA
  path contract, local service mocks, clean-root setup, cost/retention/rollback/
  teardown artifacts, and configuration tests in an isolated worktree.
- Forbidden: credentials, account identifiers, cloud calls, deployment, live
  SQL, arbitrary egress, contract edits, packet edits, judge work, HOME writes.

## Codex reconciliation

- Persona lens: Ariadne + Metis + Harmonia for architecture, then Hygeia + Dike
  + Praxis for final local health, rules, and judgeability checks.
- Codex owns deterministic authority, transaction boundaries, response
  validation, builder diff reconciliation, accepted/rejected contribution
  ledger, mechanical tests, evidence, and packet assembly.
- Builder output is untrusted and cannot enter `main` until separately inspected
  and mechanically verified.

## Gate

These assignments become dispatchable only after their files and this contract
are committed and hashed. Their work can produce `P9_OFFLINE_RUNWAY_READY` only.

