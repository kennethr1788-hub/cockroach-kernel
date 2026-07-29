# Gate 7 Run 4 Public Canary R1 Blocked Receipt

- `STATUS`: `PUBLIC_CANARY_R1_BLOCKED`
- `UTC_CLOSED`: `2026-07-29T05:15:39Z`
- `CAMPAIGN_ID`: `ck-g7r4-public-cleanup-canary-r1`
- `SOURCE_COMMIT`: `67b3b05d954821c4fd9cfdcbf80eb53b85304366`
- `MEASURED_HIDDEN_CAMPAIGN`: `NO`
- `RUNPOD_WORKER_CREATED`: `NO`

## Result

The public canary passed generation, credential isolation, zero-residue
preclean, 2,000 task inserts, 20,000 event inserts, and 4,000 receipt inserts.
It committed 3,500 of 20,000 vectors before vector batch 15 exceeded the
existing 120-second command timeout. The controller emitted a canonical
BLOCKED terminal. This result is preserved and is not relabeled GREEN.

## Fail-closed cleanup

The immediate cleanup attempt also timed out on its first vector cleanup
batch. After the timed-out server work settled, a separately receipted retry
completed all 35 deterministic cleanup batches in 56,372 ms, recovered two
SQLSTATE `40001` conflicts, and directly proved residue `[0,0,0,0]`.

## Evidence hashes

- failure: `19c57eead5a45fb7c3ee2d53c65bd9ddff2cca9e56306e31342b014111187743`
- initial cleanup: `3327d19304a239376c929baaf9e2c4c7e0c9f60e411be5148bf41a11aa109b56`
- terminal: `601b1ce8c7c5d49c106b4a81c15f1f4ef85d1a65a5fd93f99cc921fb9605a8e8`
- initial journal: `2ea326e7a661fe69838959a8f1ed696d392e7a099708ab3bec1349802e7829a6`
- cleanup recovery receipt: `1f60b42342120cc4e6da4068aa0fab9ec98af4704fdd765a5a6e7c769e22be44`
- cleanup recovery journal: `a7adb08f1a90229594a9f78b7397afbdf28fa78afded5f60a40ff537b1884291`

## Classification

The bounded cleanup design is directly supported on the partial live dataset,
but R1 does not prove cleanup after the full 46,000 records. A new public
canary is required before the Run 4 preflight can be frozen.
