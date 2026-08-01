# PDH-3 R8 ANN Proof Repair R9

- UTC completed: `2026-08-01T16:45:36Z`
- Parent failure: `FULL_CARDINALITY_SETUP_NOT_GREEN`
- Failed campaign: `ck-pdh3-scale-r8-relaunch-r8`
- Failed Pod: `klu635c1c1js3g` (deleted; campaign inventory empty)
- Measured 24-hour clock started: `false`

## Verified failure mechanism

R8 inserted and exactly reconciled 500,000 tasks, 5,000,000 events,
1,000,000 receipts, and 250,000 task-bound vectors. The setup gate then tried
to enumerate all 250,000 vectors through `context_vectors_vector_idx` and
required the approximate-nearest-neighbor result set to equal table
cardinality. CockroachDB vector indexes are ANN indexes: they search selected
partitions and do not promise complete table enumeration. R8 therefore failed
on an invalid proof, not on missing or corrupt vector rows.

The R8 failure, archive, logs, lifecycle record, and teardown proof remain
unchanged as failed evidence.

## Minimal correction

The repaired gate separates two claims:

1. Exact vector custody remains the existing full-cardinality base-table
   reconciliation. It verifies expected count, missing rows, content
   mismatches, task/event linkage, vector value, and digest.
2. Vector-index fitness is proved with eight deterministic, population-spanning
   probes. Each probe compares a forced ANN-index top-10 query at beam size 128
   against an exact primary-index top-10 baseline. Every result must contain ten
   unique well-formed IDs and the probe's exact self-match. Each probe must
   achieve recall at least 0.80 and mean recall must be at least 0.90.

All queries share the setup deadline and receive a maximum 120-second child
timeout. Invalid output, duplicate IDs, missing self-match, low recall, index
metadata failure, or deadline exhaustion blocks setup before measurement.

## Local verification

- Unit/preflight suite: `123/123 GREEN`
- Isolated three-node smoke: `GREEN`
- Dataset: 600 tasks, 1,800 events, 600 receipts, 501 vectors
- Exact mismatch counts: all zero
- ANN probes: 8
- Minimum probe recall: `0.90`
- Mean recall: `0.925`
- Measured duration: `60.000337416` seconds
- Fault cycles: 1
- Teardown: nodes stopped, ports closed, generated root removed

Evidence:

- `.pdh3-runtime/r9-vector-quality-local-smoke-20260801/evidence/setup.json`: `5221a67a2b80a78a757fb07347943e335737a1a1a173d1e6b46e741cfa800552`
- `.pdh3-runtime/r9-vector-quality-local-smoke-20260801/evidence/result.json`: `74159a5e7e90f17b27261f724f30419fbae678a2f018dda25f179230faaa3676`
- `.pdh3-runtime/r9-vector-quality-local-smoke-20260801/evidence/teardown.json`: `fe32b050de7a71b13ea9b5bc51904673cde86019f0f8cd61a17397aa2c49dfe4`

## Repaired source bindings

- `post-dogfood/run_pdh3_scale_campaign.py`: `a2ef071149827fc7913303769a7a7fa3f571e9a7a716b892c9da510d1244bf49`
- `post-dogfood/test_pdh3_scale_campaign.py`: `7f9bb1794bebadaffd28421c73679a5ee1199ffb456c594e6d7498752daa0278`
- `post-dogfood/pdh3_scale_contract.py`: `8d5fbf6d94d99abd0ac42177db1c83bf6a1d1830f537045691de7029b602c9c0`
- `post-dogfood/build_pdh3_scale_preflight_packet_r8.py`: `8066e7e539d4cc5013366c4068c20e0e917741e7174de10bcffee3b63294afab`
- `post-dogfood/test_build_pdh3_scale_preflight_packet_r8.py`: `9790a9cded155a2ecb4675d14c12066f1c9dcaaed757303389b321b7d924a8df`
- `post-dogfood/test_pdh3_scale_contract.py`: `3ba0564a123de56ddc7deeb0ff4bb3353792b8c89e0610cab7e7e031b3c0d4aa`

## Cost boundary

The replacement lifecycle remains individually capped at `$35.00`. The
cumulative conservative ceiling is minimally raised from `$36.00` to `$38.00`
to retain R8's bounded setup-only paid interval and the newly authorized
replacement honestly. Exact charge availability is not asserted.

## Next gate

Freeze a fresh same-hash packet and bundle containing this repair and R8's
immutable failed evidence. Launch only after GLM and AGY both return GREEN on
the exact packet hash and fresh provider inventory, pricing, lifecycle, and
teardown bindings pass.
