# PDH-3 R9 Read-Mix Repair R10

## Preserved failure

Campaign `ck-pdh3-scale-r9-relaunch-r1` is preserved as
`BLOCKED_COMPLETE`. Its full-cardinality setup was GREEN at 500,000 tasks,
5,000,000 trajectory events, 1,000,000 receipts, and 250,000 vectors, with
zero reconciliation mismatches and 0.975 mean ANN recall. The measured clock
never began because the first 500-worker premeasurement read mix exited
nonzero. The worker was deleted and exact-ID plus campaign absence were
proved.

## Mechanism

The read mix contained one campaign-wide trajectory-link aggregation. At
target cardinality, each occurrence joined and counted the complete
five-million-event campaign. Running that scan concurrently at 500 workers
was a pathological query shape rather than a representative task retrieval.
The prior subprocess wrapper also hashed but discarded failed querybench
stdout and stderr, and the campaign teardown deleted the failed epoch root.
Those two evidence defects prevented direct diagnosis from the original run.

## Narrow repair

1. The trajectory-link read is now constrained to one deterministic task while
   retaining the task/event join and campaign binding. It uses the existing
   unique `(task_id, sequence)` access path and does not change product data,
   verdict logic, target cardinality, worker concurrency, duration, faults,
   thresholds, or teardown requirements.
2. Querybench stdout and stderr are atomically retained on success, failure,
   and timeout, with separate hashes in terminal error identifiers.
3. A failed epoch is copied into the immutable raw-evidence tree before local
   teardown.
4. The declared node-fault transition retry accepts the exact observed
   CockroachDB `Unavailable / connection interrupted / error while dialing`
   wording, including when wrapped by `SqlOperationError`. It still refuses
   permanent SQL errors.

## Verification

- Focused PDH-3 unit suite: 63 tests GREEN.
- Syntax and whitespace gates: GREEN.
- Failed-epoch preservation: directly exercised; failed querybench stdout,
  stderr, histograms, and a raw manifest survived teardown.
- The 128 MiB local SQL-memory calibration failed honestly at 250 workers with
  `memory budget exceeded`, proving the diagnostics are now readable.
- Fresh targeted 500-worker read-mix smoke: GREEN for 10 seconds over the real
  schema and 1,000 synthetic tasks / 10,000 events / 2,000 receipts / 1,000
  vectors. It completed 267,477 operations with zero errors, p99 58.7 ms,
  maximum 151.0 ms, histogram count equal to operation count, clean database
  stop, and generated-root removal.
- Targeted receipt SHA-256:
  `430df003e270f6b48939e0d2859ba158f8ba7e63e1995365ec562b2724a6a676`.

## Remaining boundary

This repair evidence is local, reduced-cardinality, and diagnostic. It does
not prove the three target-cardinality 500-worker remote premeasurement epochs
or the 24-hour measured campaign. Those remain worker-local fail-closed gates.

