# Gate 7 Run 5 Public Canary R3 Blocked Receipt

- `STATUS`: `BLOCKED`
- `UTC_CLOSED`: `2026-07-29T20:27:41Z`
- `CAMPAIGN_ID`: `ck-g7r5-public-collision-r3`
- `SOURCE_COMMIT`: `6f70d0a30c12003727d05d76d0fa93608d75ce37`
- `HIDDEN_CAMPAIGN`: `NO`
- `RUNPOD_WORKER_CREATED`: `NO`
- `BLOCKER`: `FROZEN_INSERT_TIME_THRESHOLD_BREACHED_DURING_DROPPED_INDEX_GC_TTL`

## Direct result

R3 used the exact unchanged source, workload, retry count, timeout, scale, and
thresholds. Successful batch time reached `383257 ms`, exceeding the frozen
`300000 ms` insert-time ceiling before vector insertion completed. The
controller received SIGTERM through its reviewed interruption path, stopped
further insertion, and completed all 107 cleanup batches.

The closeout directly proves:

- tasks, events, receipts, and vectors residue: `[0,0,0,0]`;
- cleanup batches: `107/107`;
- cleanup retries: `0`;
- cleanup duration: `985949 ms`;
- external child process after closeout: none;
- RunPod worker created: no;
- hidden seed created: no.

The current table zone inherits `gc.ttlseconds = 4500`. The dropped-index GC
job began at `2026-07-29T19:22:26Z` and remained `waiting for MVCC GC` at
closeout. A new full canary before the GC job becomes terminal would repeat a
known degraded window and is forbidden.

## Canonical evidence

- failure receipt field: `aa8b08e2f218141aa66e0e4b1b358ee694fd6c61ac2b942de8d0c592c56b038b`;
- cleanup receipt field: `4adf958a05614cbee2cdbe69fbb90cb45d010e51773b8ba1ab841110547c6b4b`;
- terminal receipt field: `7d7111b230e47a8aaba30a2de03d0f3e95424ce42fd95ef7b05440df84a3fbc5`;
- failure file SHA-256: `10f55fed3a57b517d7fd0c7ed3eb9ca3d829be85fa312faaf8866aef2fd936fb`;
- cleanup file SHA-256: `df9367f9bede5391ea7bfd423d578224781b60e93ac1ec78095831e3bbf990c7`;
- terminal file SHA-256: `04da799ba9e9e941a945eae62cdde23b0d1995ab9e1889531a9dbb536d5ebb6d`;
- journal SHA-256: `e546b3400eeca3374a006fc56b7582b4059cda9371f59b03b5f20bf4c8cbb4bc`;
- direct residue output SHA-256:
  `58d9fffe639ec31e34a1032bd727a05a5b7d6983881706d28a39c24cd03a31bb`.

## Next safe action

Poll the exact GC job read-only until it becomes terminal. Then run one fresh
unchanged R4 public canary. Do not change product behavior, harness semantics,
retry count, backoff, timeout, workload, scale, or thresholds.
