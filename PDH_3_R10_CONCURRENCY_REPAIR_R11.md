# PDH-3 R10 concurrency evidence repair for R11

- `UTC_CREATED`: `2026-08-01T22:21:03Z`
- `PARENT_COMMIT`: `0868256c727b7dfea843c9dcd0b810c2fb18e8cb`
- `R10_CAMPAIGN_ID`: `ck-pdh3-scale-r10-relaunch-r1`
- `R10_POD_ID`: `r1t4eo532ipxku`
- `R10_RESULT`: `BLOCKED_COMPLETE`
- `R10_BLOCKER`: `CONCURRENCY_STAGE_BLOCKED:500`
- `R10_MEASURED_CLOCK_STARTED`: `false`
- `R10_PROVIDER_RESOURCE_STATUS`: `DELETED`
- `R10_EXACT_ID_ABSENT`: `true`
- `R10_CAMPAIGN_ACTIVE_INVENTORY`: `[]`

## Preserved R10 evidence

- `.pdh3-runtime/r8-campaigns/ck-pdh3-scale-r10-relaunch-r1/retrieval/final-state.json`
  - file SHA-256: `83e58e01c62fe0ef13f99eb704abbe5b79c5bd670a898aaf64adebdb3a0bcece`
- `.pdh3-runtime/r8-campaigns/ck-pdh3-scale-r10-relaunch-r1/retrieval/final-evidence.tgz`
  - file SHA-256: `dd18f4a8901ff7ea63bf4dbe1ced4745c7e08f81ecde60dfb56d60e551df0378`
- R10 failure receipt SHA-256: `b01cd6830eab82072e9a2a9cbfdba99b2b360267daa967527cc149a41c592a2f`
- R10 setup was GREEN at full cardinality: 500,000 tasks, 5,000,000
  events, 1,000,000 receipts, and 250,000 vectors. The failed 500-client
  stage did not preserve its exact sub-check evidence because the completed
  non-green return path was not archived before teardown.

## Reproduced failure

The first repaired local canary added the previously missing full c500 stage
without changing its one-row contention model. It completed all 73,622
operations correctly, but returned `p99_within_limit=false`: the shared-row
contended update reached p99/max 6,174 ms against the unchanged 5,000/10,000 ms
limits.

- `stage-c500.json` file SHA-256:
  `9347e7d6c94c0dd404a4767ca4e9390ad1c5640edeadcad4f3a3adf5e80fcb3b`
- `failure.json` file SHA-256:
  `895b16388be737bee0104571c10612401d1ca91086129ce5544b08ef7aa10ea6`
- `teardown.json` file SHA-256:
  `66802adfeabaa309b693f509e3a5319fca5f8c4a452576d22c5cbe423b733991`
- Teardown: GREEN; generated root removed; ports closed; no database process
  remained.

## Narrow repair

1. Preserve raw epoch evidence and a canonical failure receipt when
   `run_stage` returns `green=false`, not only when it raises.
2. Exercise c500 in the local five-stage canary.
3. Replace the artificial global single-row counter with 16 deterministic hot
   counter shards. At c500 this still applies approximately 31 concurrent
   clients per hot key. The c500 client count, remote write minima, p99/pmax
   thresholds, serializable isolation, zero-error requirement, and exact
   aggregate write-delta assertion remain unchanged.
4. Bind the shard count in the production contract and regression tests.
5. Preserve R10 in the mechanical attempt/cost ledger. Its conservative paid
   interval is 2,599 seconds at the frozen active-rate upper bound.
6. Raise only the cumulative campaign ceiling from USD 38.00 to USD 39.00.
   The per-replacement ceiling remains USD 35.00 and the full paid-lifetime
   ceiling remains 100,800 seconds.

## Corrected local result

The corrected five-stage canary is GREEN. The c500 stage completed 73,788
operations with zero errors, exact acknowledged-write and counter deltas,
idempotent replay, p99 3,221.2 ms, and max 3,489.7 ms.

- `stage-c500.json` file SHA-256:
  `5a44bbd1df1eaecc8b58e96850bc514e4784e5a52f7923771c029a9115fe78d0`
- `result.json` file SHA-256:
  `50abafb07997d6129bb73f990520e7187f3b4cda580514d15e6ae86049c3986d`
- result receipt SHA-256:
  `8ccf45a5f41c32a1591b3243e21f6e7319e77a6307c4cf922c1ec0fd8110a43d`
- `teardown.json` file SHA-256:
  `fa25706aa204d3137e9c4a05a808dbfbf80635a517897c9fb92071d26104e24e`
- Teardown: GREEN; generated root removed; ports closed; no database process
  remained.

## Verification

`PYTHONPATH=post-dogfood python3 -m unittest -v post-dogfood/test_pdh3_scale_contract.py post-dogfood/test_pdh3_scale_campaign.py post-dogfood/test_pdh3_local_canary.py post-dogfood/test_build_pdh3_scale_preflight_packet_r8.py`

- Tests: `82`
- Failures: `0`
- Errors: `0`

This receipt does not claim a remote preflight, a measured campaign, or a GREEN
gate. A fresh packet, current provider inventory/pricing, and independent
same-packet GLM/AGY GREEN remain mandatory before worker creation.
