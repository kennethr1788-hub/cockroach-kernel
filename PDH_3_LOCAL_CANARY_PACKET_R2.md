# PDH-3 Local Canary Packet R2

## Authority and boundary

- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PLAN_SHA256`: `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- `PARENT_GREEN`: `PDH_1_INFORMATION_BOUNDARY_GREEN`
- `PDH_2`: `DELIBERATELY_SKIPPED_BY_OPERATOR`
- `PAID_RESOURCES`: forbidden
- `NETWORK`: loopback only
- `DATA`: generated synthetic data only
- `PRODUCT_MUTATION`: forbidden
- `PUBLIC_ACTIONS`: forbidden
- `HOME_RUNTIME`, `QDRANT`, `STATEV2`, `LAUNCHD`, `CLIENT_DATA`, `PRODUCTION_DATA`: forbidden

This packet authorizes only a no-cost calibration. It cannot produce
`PDH_3_PRODUCTION_SHAPED_SCALE_GREEN`; it may produce only
`PDH_3_LOCAL_CANARY_GREEN` or a fail-closed local-canary blocker.

## R1 history and R2 repair

All R1 attempts remain append-only failed evidence.

- Attempt 1 exposed an omitted bounded `SQLSTATE 40001` retry.
- Attempt 2 exposed missing persistent per-stage observability.
- Attempt 3 exposed a duration-boundary accounting mismatch: committed
  database effects exceeded QueryBench's final reported interval.

R2 changes only the measurement boundary for mutating workloads. It does not
change the product candidate, schema, query semantics, concurrency stages,
latency limits, error limits, recovery behavior, or public claim.

## Frozen controller

`post-dogfood/run_pdh3_local_canary.py`:

1. Binds the candidate, plan, and this packet's externally supplied SHA-256.
2. Uses the existing verified CockroachDB v26.2.3 macOS arm64 binary.
3. Runs the frozen 43-execution fresh-process verifier/refusal campaign.
4. Creates one loopback-only CockroachDB single-node process in a generated
   `/private/tmp/ck-pdh3-local-r1.*` root with an empty task-local `HOME`.
5. Applies the exact P9 application migrations.
6. Generates and inserts 500 tasks, 5,000 trajectory events, 1,000 receipts,
   and 5,000 task-bound vectors. Only exact `SQLSTATE 40001` insert failures
   may be retried, at most three times per batch with fixed 250 ms backoff.
7. Runs task-bound reads for two seconds at concurrency 10, 50, 100, and 250.
8. At each concurrency stage, starts bounded fixed-operation workloads with
   minimums of:
   - 2,000 acknowledged writes;
   - 1,000 contended updates;
   - 1,000 replay-idempotency operations.
9. Sets QueryBench `--warmup-conns=0` and requires process completion before
   reading database-side counts.
10. QueryBench's concurrent `--max-ops` behavior is treated as a soft cap. Each
    workload may complete no more than `minimum + concurrency - 1` operations.
    Its summary and histogram must agree exactly, and the corresponding
    database-side delta must equal that observed count exactly.
11. Requires idempotent replay, zero wrong-task vector linkage, zero query
    errors, exact row counts, and exact rollback.
12. Sends SIGKILL after concurrency 50, restarts from the same disposable
    store, and verifies acknowledged state and application rows survive.
13. Executes the dependency-ordered cleanup manifest and requires zero
    campaign residue.
14. Stops the node, proves both loopback ports are closed, and removes only the
    verified generated root.

No credential acquisition, AWS call, Lambda call, external model call, package
installation, live CockroachDB connection, RunPod worker, or public surface is
permitted.

## Frozen thresholds

- Concurrency stages: exactly `10`, `50`, `100`, `250`.
- Read-mix duration: exactly two seconds per stage.
- Acknowledged writes: 2,000 through `2,000 + concurrency - 1` per stage.
- Contended updates: 1,000 through `1,000 + concurrency - 1` per stage.
- Replay-idempotency operations: 1,000 through
  `1,000 + concurrency - 1` per stage.
- Minimum completed operations: 500 per stage.
- Query errors: zero.
- Insert retries: only exact `SQLSTATE 40001`, at most three per batch.
- Every workload histogram must equal its QueryBench operation total.
- Every fixed-operation QueryBench total must remain inside its frozen bounded
  interval.
- Acknowledged-write row delta must equal its QueryBench summary exactly.
- Contended counter delta must equal its QueryBench summary exactly.
- Replay-control rows: exactly one.
- Aggregate p99: at most 5,000 ms per stage.
- Aggregate pMax: at most 10,000 ms per stage.
- Wrong-task vector links: zero.
- Acknowledged application-row loss after crash/restart: zero.
- Rollback residue: zero.
- Campaign data residue after cleanup: zero.
- Verifier false promotions, mutation after refusal, and task-root residue:
  zero.

Stage 500 is not authorized. Paid or cloud execution is not authorized.

## Evidence contract

The controller emits canonical JSON:

- `result.json`: source hashes, candidate/plan/packet binding, row counts,
  bounded operation targets, QueryBench counts, database deltas, latency,
  crash/restart evidence, verifier results, limitations, and next gate;
- `stage-c<concurrency>.json`: persisted before its GREEN decision;
- `teardown.json`: process, port, and generated-root teardown;
- `manifest.json`: hashes binding result, stages, and teardown;
- `failure.json`: fail-closed result binding all surviving stage and teardown
  evidence.

Raw QueryBench logs and generated database state remain inside the disposable
root. Final receipts preserve hashes and aggregate metrics only.

## Fail-closed conditions

Stop on source or packet drift, external access, false verifier behavior,
wrong-task vector linkage, any query error, any operation-count or database
delta mismatch, replay non-idempotency, crash/restart data loss, rollback or
cleanup residue, threshold breach, or teardown failure.

## Permitted conclusion

Independent GLM 5.2 preflight must return GREEN over the exact frozen packet
and controller hashes before execution. A GREEN run requires an independent
final review over the exact evidence hashes.

The only permitted successful status is:

`PDH_3_LOCAL_CANARY_GREEN`

The next step remains blocked until Kenneth separately authorizes exact paid
cost and lifecycle limits for any measured cloud campaign.
