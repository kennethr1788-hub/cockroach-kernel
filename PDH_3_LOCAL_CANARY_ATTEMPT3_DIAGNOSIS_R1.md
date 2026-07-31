# PDH-3 Local Canary Attempt 3 Diagnosis R1

## Preserved result

- `ATTEMPT`: `evidence/pdh3-local-canary-r3`
- `STATUS`: `BLOCKED`
- `FAILURE_CLASS`:
  `CONCURRENCY_STAGE_NOT_GREEN:10:acknowledged_writes_exact,contended_updates_exact`
- `STAGE_RECEIPT_SHA256`:
  `6407d5afeda4c796e97e8bd553969d52632e1a45c6eda24baa82ca1c32f5777d`
- `FAILURE_FILE_SHA256`:
  `87883f20a33847fa4ce4a282c23455ebe53cc8bba25aa86b5282b19ab3ec77cc`
- `TEARDOWN_FILE_SHA256`:
  `b3c8876bb7523eea1c492ca44a68caa7c0b6d2bc795f65c877a1e5ffcafd8cb2`

Attempt 3 remains failed evidence and may not be relabeled.

## Direct evidence

At concurrency 10, QueryBench reported:

- 1,857 acknowledged-write operations while CockroachDB recorded a row delta
  of 1,867;
- 351 contended-update operations while CockroachDB recorded a counter delta
  of 355;
- zero errors;
- exact histogram-to-reported-operation accounting;
- 92,149 total reported operations;
- 41.9 ms maximum workload p99 and 48.2 ms maximum latency.

The database process stopped, both ports closed, and the generated root was
removed.

## Mechanism and correction

The duration-bounded mutating workloads did not provide one common completion
boundary for the database delta and QueryBench's final reported interval.
Committed database effects exceeded the final client-reported interval even
though the client reported zero errors.

The corrected controller does not relax database-to-client equality. It
replaces duration-bounded acknowledged writes, contended updates, and replay
operations with bounded fixed-operation workloads. QueryBench v26.2.3 treats
`--max-ops` as a concurrent soft cap and may complete at most
`concurrency - 1` already-issued operations after reaching that cap. A
mutating workload passes only when:

1. QueryBench exits successfully after at least the frozen minimum and no more
   than `minimum + concurrency - 1` operations;
2. its final summary equals its histogram count exactly;
3. the corresponding database-side delta equals that same observed count
   exactly.

The read workload remains duration-bounded because it has no database mutation
to reconcile. Existing latency, error, replay, crash/restart, cleanup, residue,
and product-candidate gates remain unchanged.

Two fresh-root calibration probes at concurrency 10 each requested a soft cap
of 200 acknowledged writes and 100 contended updates. Both produced exactly
209 and 109 operations respectively, and in both probes the QueryBench
summary, histogram, and database-side effects agreed exactly with zero errors.
The alternative `--num-runs` mode did not terminate and was rejected.
