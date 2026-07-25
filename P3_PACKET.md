# Cockroach Kernel P3 Frozen Packet

- `GATE`: `CK_P3_PENDING_JUDGE`
- `LAST_GREEN_GATE`: `CK_P2_CLEANROOM_GREEN`
- `CURRENT_COMMIT`: `7519884`
- `PARENT_P2_PACKET_SHA256`: `bcab4869080e7aa65de46a6e1cf55dfb7d67729afc331fdb078c0b17c3fe8b70`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `FROZEN_UTC`: `2026-07-25T20:44:14Z`

## Implementation

- migration: `p3-ledger/migrations/001_ledger.sql`
- deterministic primitives: `p3-ledger/ledger.py`
- unit tests: `p3-ledger/test_ledger.py`
- Cockroach integration harness: `p3-ledger/run_integration.py`

## Migration and source hashes

- `001_ledger.sql`: `f28a8ffa1ed3163b3d31f319b1c1351dd057070235a7cc2c15bbdc27ec9491ac`
- `ledger.py`: `5006bca442fe124b16339f3b8c9d9849e8f0b1500117b77db1685790096d294a`
- `test_ledger.py`: `8c905cbca6df26a14c461dec033f0214b30e179321f2ca48fb956c3188023d0f`
- `run_integration.py`: `265a00c27df0c92eea8300a917f3343a1f0b7a4585c2c878a0630f3cff68e089`

## Contract coverage

The schema covers tasks, trajectory events, causal links, context records,
persona manifests, candidates, evaluator votes, dissent, policy versions,
recovery capsules, one-use warrants, immutable receipts, and evidence budgets.
The Python authority layer enforces canonical JSON, SHA-256 hashes, stable IDs,
unknown-field rejection, schema validation, deterministic verdicts, trajectory
hashing, and nonnegative evidence accounting.

Authoritative transitions are `DECLARE`, `RECORD`, `EVALUATE`, `PROMOTE`,
`REFUSE`, and `INVALID`. The verdict function uses no time, randomness, model,
or network.

## Test evidence

- unit suite: 5 tests, all `OK`;
- integration trials: 2 fresh roots, both ready, migration successful, 2 tables,
  duplicate event rejected, orphan receipt rejected, first warrant consumption
  returned one row, second consumption returned no row, final warrant
  `CONSUMED`, matching event/budget hashes, and clean teardown;
- no surviving CockroachDB process or temporary trial root after tests.

## Boundaries

Synthetic data only. Project-local CockroachDB runtime only. No credentials,
HOME writes, live cloud, AWS, RunPod, Docker, GPU, production data, client data,
or public actions.

## Gate

`CK_P3_LEDGER_GREEN` requires the independent GLM review of this exact packet
and all evidence above. No later phase is authorized by this packet alone.
