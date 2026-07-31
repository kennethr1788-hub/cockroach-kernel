# PDH-3 Local Canary Fixed-Operation Calibration R1

## Scope

This was a no-cost, loopback-only, synthetic calibration against the existing
CockroachDB v26.2.3 macOS arm64 binary. It used fresh generated roots and
deleted each root after stopping the database. It was not a product canary and
cannot produce a product or PDH gate.

## Two-probe result

Both fresh-root probes ran at concurrency 10:

| Workload | Soft cap | QueryBench summary | Histogram | Database effect | Errors |
|---|---:|---:|---:|---:|---:|
| Acknowledged write, probe 1 | 200 | 209 | 209 | 209 rows | 0 |
| Contended update, probe 1 | 100 | 109 | 109 | counter +109 | 0 |
| Acknowledged write, probe 2 | 200 | 209 | 209 | 209 rows | 0 |
| Contended update, probe 2 | 100 | 109 | 109 | counter +109 | 0 |

The result proves that QueryBench's concurrent `--max-ops` is a soft cap in
this binary: as many as `concurrency - 1` already-issued operations may finish.
It also proves that after process completion the QueryBench summary, histogram,
and database-side effects can agree exactly.

`--num-runs` was tested as an alternative. The 200-operation acknowledged-write
probe did not terminate after more than 30 seconds and was stopped. Its
generated root and database process were removed. That mode is rejected.

## Accepted measurement boundary

The corrected canary freezes a minimum operation count and a maximum of
`minimum + concurrency - 1`. It does not accept approximate accounting:

- QueryBench summary must equal histogram count exactly.
- Database-side acknowledged-write delta must equal the summary exactly.
- Database-side contended-update delta must equal the summary exactly.
- Any operation count outside the frozen bounded interval is terminal.

## Corrected-controller calibration

The corrected controller boundary was then exercised at concurrency 10 and 50
using the full frozen per-stage minimums:

| Concurrency | Workload | Frozen minimum | Maximum | Summary | Histogram | Database effect |
|---:|---|---:|---:|---:|---:|---:|
| 10 | Acknowledged write | 2,000 | 2,009 | 2,009 | 2,009 | 2,009 rows |
| 10 | Contended update | 1,000 | 1,009 | 1,009 | 1,009 | counter +1,009 |
| 10 | Replay | 1,000 | 1,009 | 1,009 | 1,009 | 1 row |
| 50 | Acknowledged write | 2,000 | 2,049 | 2,049 | 2,049 | 2,049 rows |
| 50 | Contended update | 1,000 | 1,049 | 1,049 | 1,049 | counter +1,049 |
| 50 | Replay | 1,000 | 1,049 | 1,049 | 1,049 | 1 row |

All six workload executions reported zero errors. Both generated roots were
removed after their database processes stopped. No calibration process or
temporary root remained.
