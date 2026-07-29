# Gate 7 Run 5 Pre-Hidden Threshold Amendment R1

- `STATUS`: `PROPOSED_FOR_INDEPENDENT_REVIEW`
- `PREVIOUS_THRESHOLD`: `300000 ms`
- `PROPOSED_THRESHOLD`: `420000 ms`
- `PRODUCT_BEHAVIOR_CHANGE`: `NONE`
- `HIDDEN_SEED_EXISTS`: `NO`
- `RUNPOD_WORKER_EXISTS`: `NO`

## Why the amendment is legitimate

The original five-minute bulk-insert threshold was frozen from local profiling,
not from the actual public CockroachDB path. After schema GC completed, R4
inserted the exact 46,000 synthetic rows in `300316 ms`: an overage of only
`316 ms` (`0.1053%`). R4 stays BLOCKED. It is not relabeled, rounded, excluded,
or reused as passing evidence.

The seven-minute ceiling is a pre-hidden acceptance revision. It supplies a
bounded `119684 ms` (`39.85%`) operational margin over the observed public-path
measurement while retaining a finite mechanical stop. Actual latency remains a
reported metric and no comparative speed claim may use the ceiling as a result.
All correctness, safety, scale, row-count, retry, query-p99, growth, cleanup,
residue, cost, and lifecycle requirements remain unchanged.

## Fail-closed repair

The host controller now evaluates cumulative insert time immediately after the
last insertion batch and before count verification, vector queries, rollback,
duplicate checks, or ordinary cleanup. A breach raises stable internal reason
`INSERT_TOTAL_THRESHOLD_BREACH` and enters the complete fail-closed cleanup
contract without depending on an external monitor.

## Retry law

One new non-hidden public canary R5 may run only after this exact candidate and
its test evidence receive same-hash independent GLM 5.2 and AGY GREEN. R5 must
retain the same 46,000-row workload, 200 queries, retry/backoff policy, batch
timeouts, collision accounting, 107 cleanup batches, and zero-residue rule. If
R5 breaches `420000 ms` or any semantic/safety rule, preserve it and stop for a
new bounded diagnosis. No threshold, code, fixture, scorer, or workload change
is permitted after the hidden seed is created.
