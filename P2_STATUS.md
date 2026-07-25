# P2 Disposable CockroachDB Clean Room

**Status:** `CK_P2_OPEN`
**Parent gate:** `CK_P1_CONTRACT_GREEN`
**Started UTC:** 2026-07-25T20:14:09Z
**Scope:** synthetic fixtures and local clean-room scaffolding only

## Required outcomes

- migrations and seed fixtures are reproducible from a clean clone;
- rollback and teardown are explicit and idempotent;
- residue scanning covers generated roots and worktree state;
- no HOME runtime, live memory collection, StateV2 database, launchd job,
  credential, client data, or unrelated repository is reachable;
- a fresh sandbox can be rebuilt without hidden state.

## Forbidden

No AWS or CockroachDB credentials, live cluster mutation, RunPod, network
volume, HOME write, live Qdrant/StateV2 access, launchd mutation, production
data, or public release action.

## Gate

`CK_P2_CLEANROOM_GREEN` remains OPEN until a clean-clone run, rollback,
teardown, residue scan, and independent review are recorded.
