# P1 Handoff Manifests

These are frozen task manifests, not claims that the workers have run.

| Lane | Scope | Forbidden | Required return |
|---|---|---|---|
| Kimi K3 | Schema, fixtures, canonical serialization, non-authoritative persistence | Authority semantics, credentials, live services | Files, tests, raw output, limitations, SHA-256 |
| Vibe | Retry/idempotency/failure-injection and adversarial evidence harness | Authority edits, deployment, credentials | Executable tests, raw output, evidence manifest, SHA-256 |
| Devstral | CockroachDB/AWS boundary fixtures, Lambda mock, least-privilege and clean-clone contract | Deployment, AWS credentials, live clusters | Contract, config schema, checklist, limitations, SHA-256 |
| Codex | Reconcile handoffs, freeze authority contract, produce judge packet | Self-approval, treating summaries as evidence | Conflict ledger, accepted/rejected items, final packet hash |

All lanes use sanitized synthetic data in separate worktrees.
