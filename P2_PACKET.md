# Cockroach Kernel P2 Frozen Packet

- `GATE`: `CK_P2_BLOCKED`
- `BLOCKER`: `LOCAL_COCKROACH_RUNTIME_UNAVAILABLE`
- `LAST_GREEN_GATE`: `CK_P1_CONTRACT_GREEN`
- `PARENT_COMMIT`: `725c6c6ef6c7c7c14c950dba00a37a07ca47a093`
- `MIGRATION_SHA256`: `383d8dce1590b2309dc56017fe468a91098b9b5b38a1fe6e3cae7d1f30e961be`
- `FIXTURE_SHA256`: `a49612a43cd4c2cd303783dec1bc9d217587c9bf9d368abc997e2764eb282172`
- `FROZEN_UTC`: `2026-07-25T20:18:14Z`

## Scope

Synthetic local clean-room bootstrap, migration, seed, rollback, teardown, and
residue scanning under `p2-cleanroom/`. No credentials, live cluster, AWS,
RunPod, HOME, production data, or external volume.

## Required evidence

Two fresh-root clean-clone trials must agree on migration, seed, rollback,
teardown, and residue results. Both are `NOT_RUN` because the required local
CockroachDB executable is absent. No substitute runtime was used.

## Evidence files

- `P2_STATUS.md`
- `P2_CLEANROOM_RECEIPT.md`
- `P2_EVIDENCE_MANIFEST.md`
- `P2_CHECKPOINT.md`
