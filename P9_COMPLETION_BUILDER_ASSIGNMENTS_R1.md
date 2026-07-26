# P9 Completion Builder Assignments R1

- `CONTRACT`: `P9_COMPLETION_CONTRACT_R1.md`
- `PARENT_COMMIT`: `10b1a40a48b8d0e2543a532e8e2d9d9de3036c30`
- `STATUS`: `FROZEN`

Every builder receives only sanitized source and the completion contract in an
isolated worktree. No builder receives credentials, browser state, cloud
account identifiers, live connection strings, private data, OAuth material,
judge outputs, deployment authority, live SQL authority, or gate authority.

## Kimi K3

- personas: Athena, Daedalus, Argos Panoptes
- deliverable: fixed operation enum, canonical coordinator/request adapter,
  deterministic two-trial fixtures, and bounded unit tests
- required route: current Kimi OAuth worker playbook

## Vibe

- personas: Mythos, Talos, Themis
- deliverable: reliability/adversarial tests for retry, idempotency, stale and
  out-of-order messages, changefeed restart, coordinator and Lambda faults,
  cadence/growth, injection, and denial-of-wallet
- required route: current isolated Vibe playbook

## Devstral

- personas: Curator, Soteria, Vault-Recall
- deliverable: typed cloud-boundary configuration, least-privilege and
  credential-separation assertions, MCP/changefeed boundary checks, retention,
  cost, teardown, and clean-state tests
- required route: current sanitized Devstral playbook with live sentinel

## Codex reconciliation

- personas: Ariadne, Metis, Harmonia, then Hygeia, Dike, Praxis
- responsibility: authority invariants, parameterized SQL, local verifier
  linkage, builder-diff review, integration, live coordinator, live evidence,
  packets, receipts, and cleanup

No contribution reaches `main` before inspection and mechanical verification.
Accepted and rejected changes, route/version/wrapper/prompt hashes, files,
tests, and limitations are recorded. A missing required builder after bounded
current-playbook retries produces `BUILDER_UNAVAILABLE`.
