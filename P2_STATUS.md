# P2 Disposable CockroachDB Clean Room

**Status:** `CK_P2_CLEANROOM_GREEN`
**Parent gate:** `CK_P1_CONTRACT_GREEN`
**Started UTC:** 2026-07-25T20:14:09Z
**Trial completion UTC:** 2026-07-25T20:35:33Z
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

## Preflight and trial result

The pinned official arm64 runtime was downloaded into the project-local vendor
directory and its published checksum verified. No global installation or live
cluster was used. Two sequential fresh-root localhost trials completed with
matching migration, seed, rollback, process, and residue results.

## Gate

`CK_P2_CLEANROOM_GREEN` is issued from the independent GLM `GREEN` receipt in
`P2_JUDGE_RECEIPT.md`. No P3 work is included in this gate.
