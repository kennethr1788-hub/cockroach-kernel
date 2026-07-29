# Gate 7 Run 5 Public Canary R2 Blocked Receipt

- `STATUS`: `BLOCKED`
- `UTC_CLOSED`: `2026-07-29T19:55:23Z`
- `CAMPAIGN_ID`: `ck-g7r5-public-collision-r2`
- `SOURCE_COMMIT`: `ce47a893413c8ab1de9bcab65336b296a13dbb9c`
- `HIDDEN_CAMPAIGN`: `NO`
- `RUNPOD_WORKER_CREATED`: `NO`
- `BLOCKER`: `VECTOR_INSERT_SERIALIZATION_RETRY_EXHAUSTED_DURING_SCHEMA_CHANGE_GC`

## Direct result

The canary preserved the repaired collision-safe identity contract, but vector
insert batch 48 exhausted the existing three-retry bound on SQLSTATE `40001`.
The controller stopped before queries, executed all 107 dependency-ordered
cleanup batches, and directly proved residue `[0,0,0,0]`.

A subsequent read-only cluster check found exactly one running
`SCHEMA CHANGE GC` job. No retry may begin while that job remains active. This
receipt does not authorize changing the workload, retry count, backoff,
thresholds, candidate, or hidden protocol.

## Canonical evidence

- failure receipt field: `8452b1307584583a5fc8d8b81845daacc0b9a56fa4dd29e331ba2eee04d3f464`;
- cleanup receipt field: `bddd37323ebd8ab48684dacb67a323105ccb5470ea7c15df1e176802236a0535`;
- terminal receipt field: `5c8565fae5c8885113c6e3bf24e7008b9829728a709dbe2b396a83fb0825266f`;
- failure file SHA-256: `a60ff0f06aa079b13d3ef341d9fa513059e2af9e5f7a0937dd6cf7f5eed158b4`;
- cleanup file SHA-256: `ee2be4c453cf7271007aa957966eb7b495b62968d8e46c7990df0c803a359a19`;
- terminal file SHA-256: `c46fbe1ff8f56604686814b5868322f2916c09812a1da30e1c58f66f17f2a6c5`;
- journal SHA-256: `456e735a6c724799c5cce59f3d0de49c272eae0b4519530be5c36d4d296905a1`;
- cleanup batches: `107/107`;
- cleanup retries: `0`;
- cleanup duration: `193625 ms`;
- residue: `[0,0,0,0]`.

## Next safe action

Poll the running schema-change GC read-only. After the active schema-change job
count reaches zero, rerun the unchanged public canary once under a fresh
campaign ID. Preserve this R2 failure permanently.
