# Gate 7 Run 4 Public Canary R3 Green Receipt

- `STATUS`: `RUN4_PUBLIC_FULL_CANARY_GREEN`
- `UTC_CLOSED`: `2026-07-29T05:54:30Z`
- `CAMPAIGN_ID`: `ck-g7r4-public-cleanup-canary-r3`
- `SOURCE_COMMIT`: `5376f6346c3a8ee04b9f675cfe1180a34a3d4c49`
- `MEASURED_HIDDEN_CAMPAIGN`: `NO`
- `RUNPOD_WORKER_CREATED`: `NO`
- `NEXT_GATE`: `RUN4_SAME_HASH_GLM_AGY_PREFLIGHT`

## Direct live result

- tasks: `2,000/2,000`;
- trajectory events: `20,000/20,000`;
- receipts: `4,000/4,000`;
- context vectors: `20,000/20,000`;
- vector queries: `200/200`;
- configured and observed concurrency: `4/4`;
- bounded SQLSTATE `40001` insert recoveries: `20`;
- query latency p99: `924 ms`;
- rollback and duplicate controls: `PASS`;
- indexed ordered cleanup batches: `107/107`;
- cleanup retries: `0`;
- cleanup duration: `206,927 ms`;
- canonical cleanup residue: `[0,0,0,0]`;
- separate direct residue query after closeout: `[0,0,0,0]`;
- terminal validation: `GREEN`.

The result is synthetic public calibration evidence. It is not hidden RunPod
evidence and cannot substitute for the separately authorized measured Run 4
campaign.

## Canonical linkage

- result SHA-256 field: `2d55b50048173a4eea5a077e86022f59894cbf0b6ed5bc0ecde166bd3fd9a2ba`;
- cleanup receipt SHA-256 field: `4530b15e1fd9df522b4133d11768ae1f0dc3f5df876497738f75ebf292243c07`;
- terminal receipt SHA-256 field: `04d61876c04b5b77c448d032df9c952b3a92a8267e414a4cf96fb45f7e2151d4`;
- journal records: `660`;
- cleanup PASS journal events: `107`.

## File hashes

- result file: `be6ac46ca74ceb791931dccdc00107805202e8117048d37f1617691ffd8cd560`;
- cleanup file: `e876c07bdcac3bb1531b4435a5a1cc0c724f0140e49acdcc4ddcc429ed85398c`;
- terminal file: `29562a420c9348c7fcb49a341ae2494b506aec390cf5e20ff232f7c6a9a59b98`;
- journal file: `04df9c4bc54fbdde8a33bb9b2c4edd0fa86f8f7a27246c572b1a631f3870114d`;
- generated manifest: `85cec1ef2c08ae3f6eb4d5251d1d8ed76c52959d882d6f1bfc95e7c19a0732e4`;
- cleanup manifest: `8d253ee5fc1c7afffcc212ad571328e15163d2d51065ba1661d9591a02074be5`.

## Bound source

- live controller: `a4aac833a58274de10a4a044704f318698169194b5e0430eee134e9afb2e3017`;
- Gate 7 tests: `e4ec423c4208605180ffb467044ed0699a93572af99ff016825a2e7979122a42`;
- Track 1 custody: `025e5c89eba77597e1831de54e9c6ca967a9b09de9a9f711ac369918673cd265`;
- Track 2 start gate: `584a49e6803611d4b22950ffbe5a64e837965d53b52e430b1fd7e37fb6d6a2e9`;
- Run 4 schedule: `d111dcbe5a060075ab90972fc28a866735327b9f115174f05e23f789c11b8b1d`.

## Gate boundary

No hidden seed exists. No paid worker exists. Run 3 remains immutable and
blocked. The next action is to freeze one sanitized Run 4 packet and require
same-hash GLM 5.2 and AGY GREEN before any worker creation.

