# Gate 7 Run 4 Public Canary R2 Blocked Receipt

- `STATUS`: `PUBLIC_CANARY_R2_BLOCKED`
- `UTC_CLOSED`: `2026-07-29T05:45:01Z`
- `CAMPAIGN_ID`: `ck-g7r4-public-cleanup-canary-r2`
- `SOURCE_COMMIT`: `c8fa8cd9ef8b0c66084b1406d5c48ecac5c95234`
- `MEASURED_HIDDEN_CAMPAIGN`: `NO`
- `RUNPOD_WORKER_CREATED`: `NO`

## Result

R2 completed the full workload at exact counts
`[2000,20000,4000,20000]`, all 80 vector insert batches, 200 vector queries,
and the rollback and duplicate controls. The vector insert path recovered 38
bounded SQLSTATE `40001` conflicts and did not exceed its amended timeout.

The first 2,500-vector cleanup transaction exceeded 120 seconds. The
fail-closed second cleanup deleted most records but another 2,500-vector batch
also exceeded 120 seconds. The controller correctly emitted a canonical
BLOCKED terminal. R2 is not relabeled GREEN.

## Officially aligned recovery proof

A separate append-only recovery used an indexed ordered delete on `vector_id`
with `LIMIT 250`, one `READ COMMITTED` transaction per batch, then the existing
bounded task-key cleanup for dependent tables. All 107 batches passed in
86,681 ms with zero retries and directly proved `[0,0,0,0]` residue.

CockroachDB's official bulk-delete guidance recommends iterative, single-query
transactions filtered and ordered on an indexed column with a `LIMIT`. Its
official vector-index guidance also warns that large vector batches degrade
write performance. The R3 repair applies those mechanisms without changing
the measured record counts or acceptance thresholds.

## Evidence hashes

- failure: `2d597bc5c027420c4cf7b6cd0b61989f3fefdfb01e58666b2d4e318550541ae2`
- initial cleanup: `305566feedc2e89c0b8a4ece06f2802d5f25bb71db78eb85d342d17e98851b9d`
- terminal: `5fd7a94fc8872a156b2e3994152894fcbb745de4285abca2c6e66b4bcc4673ce`
- initial journal: `e800051b8e12ac06325e2e2dcd54330d295c4a8264a45fe9880c7dfd6e30bc64`
- indexed cleanup recovery receipt: `01feb3786728bde9f0c5f8234b7befc4be2ccb7241328b4ef8a7f2d61ed9e383`
- indexed cleanup recovery journal: `52bbf60ec8d3b9fe22b5649656ffd52f43c068d543366b3058d6388c5227e189`

## Sources

- `https://www.cockroachlabs.com/docs/stable/bulk-delete-data`
- `https://www.cockroachlabs.com/docs/stable/read-committed`
- `https://www.cockroachlabs.com/docs/stable/vector-indexes`

