# EV1-T02 Mechanical Result R1

- `STATUS`: `MECHANICAL_TASK_COMPLETE_OPERATOR_OBSERVATION_REQUIRED`
- `TASK_ID`: `EV1-T02`
- `UTC_RECORDED`: `2026-07-30T16:56:22Z`
- `EXECUTION_RECEIPT_FILE_SHA256`: `40a5b3c7342060b739ae2a60f3108dd6cbe65422f7bf5d72a7eb785c8db9204d`
- `EXECUTION_RECEIPT_SHA256`: `fe18b5b10cb4d2174ff8fefc3b9dfd606bc59470a356aca93fad880cd4f846cf`
- `PRODUCT_VERDICT`: `PROMOTE`
- `PRODUCT_REASON`: `MAX_PROVEN_PREFIX`
- `CAMPAIGN_TEARDOWN_PENDING`: `TRUE`

## Direct mechanical result

The one authorized execution completed without a retry:

- the exact disposable original workspace was deleted;
- the outside kill canary survived;
- the original workspace is absent with zero reported residue bytes;
- a fresh successor was created without `.git` history;
- 75 source-bound baseline files were recreated;
- dependencies were cloned into the successor's own `node_modules` ancestry;
- all three declared work units were restored byte-exact;
- the unchanged product returned `PROMOTE / MAX_PROVEN_PREFIX`;
- `npm run typecheck`, `npm run build`, and
  `npm run test:storage-contract` all exited zero;
- the storage-contract result retained its pre-loss deterministic log SHA-256;
- post-loss task restatement words and manual interventions were both zero;
- false promotions, false refusals, invalid outcomes, unsafe mutations,
  unauthorized path accesses, and task-process residue were all recorded as
  zero.

Measured invocation-to-productive-continuation time was 108,812,375 monotonic
nanoseconds. Invocation-to-full-acceptance time was 15,850,416,542 monotonic
nanoseconds.

## Restored work hashes

| Path | SHA-256 |
|---|---|
| `package.json` | `b66777767e93866256960f1bf03ace59a26b55c1c880a6a54ca8c74516379d10` |
| `scripts/run-storage-contract.mjs` | `92148e576b4a1415d6b5a23169d384b6262de3b8878b5dfbcabae6ca56f6e65c` |
| `scripts/storage-contract-cases.cjs` | `e402403a667ec1c4d889bddb181f34d2c98890ddb3b1bf8a823b0cc13584dc25` |

This is mechanical evidence, not a completed EV1 task classification. Kenneth's
two immediate operator observations remain required. The successor and custody
state remain preserved under the bounded temporary campaign root; teardown and
final independent review have not started.
