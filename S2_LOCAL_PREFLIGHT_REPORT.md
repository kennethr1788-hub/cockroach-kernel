# S2 Local Preflight Report

- `UTC_REPORTED`: `2026-07-26T01:47:35Z`
- `STATUS`: `LOCAL_WORKLOAD_GREEN`
- `REMOTE_STATUS`: `NOT_STARTED`
- `LAST_GREEN_GATE`: `CK_P7_RECOVERY_GREEN`

## Smoke history

- R1 failed closed before any checkpoint because the harness incorrectly
  expected the aggregate selector to repeat a candidate-specific ineligibility
  reason. Final receipt SHA-256:
  `5207cb2443133209129c0a46ce1211d2f37e18366b9986977d75ba55c5fffca8`.
- R2 failed closed before any checkpoint on an unquoted empty JSON SQL literal.
  Final receipt SHA-256:
  `e5d3cb7dba726ba357b635b8fa9f98d4569d89efa68552d4c6b55d2aa3bd90b4`.
- Both defects were corrected without modifying any earlier phase. Both failed
  outputs remain preserved and are not represented as passes.

## R3 successful local smoke

Command schedule: 12 seconds requested, 2-second checkpoints, 3-second safety
replays, and 4-second summaries. This accelerated smoke is not six-hour
evidence; it validates the same code paths and stream mechanics.

- status: GREEN;
- measured end-to-end execution: 44.803 seconds (work exceeded the accelerated
  intervals but all scheduled operations executed; production intervals are
  300/900/3,600 seconds);
- checkpoints: 6/6;
- safety replays: 4/4;
- hourly summaries: 3/3;
- named event receipts: 10;
- runtime residue: empty;
- final evidence hash:
  `e703861f1de757c7d745995d4fe573d431f335574aed98243d4e69ddf013b50e`;
- final JSON SHA-256:
  `7d56d7dad0a4ce7d10a139ca0babcee79149301fc90445f1136ed152740481e5`;
- complete R3 tree digest:
  `a3b67dde6f8226ac46a0bc7a495d0a00bad182fbed9c3eb785c234a72d337eb9`;
- files: 31, total 51,016 bytes;
- every stream sequence, previous-hash link, and receipt hash independently
  recomputed successfully;
- symlink scan: empty.

Local `/usr/bin/time -l` profile:

- maximum RSS: 478,068,736 bytes;
- peak memory footprint: 330,662,392 bytes;
- process exited successfully;
- no swaps;
- 2 vCPU / 4 GiB therefore exceeds measured memory demand by more than eight
  times before the frozen 2 GiB runtime limit.

The source imports only Python standard-library modules plus the local P4–P7
modules. The workload has no HTTP, socket, SDK, model, AWS, Cockroach Cloud, or
RunPod client. On Linux production, it additionally proves the CockroachDB
process owns no established non-loopback TCP socket.

The failed R1/R2 and successful R3 local evidence directories are retained as
raw preflight evidence. They are not included in the remote transfer payload.
