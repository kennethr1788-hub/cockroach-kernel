# PDH-3 Local Canary Packet R1

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

## Frozen controller

`post-dogfood/run_pdh3_local_canary.py`:

1. Binds the candidate, plan, and this packet's externally supplied SHA-256.
2. Uses the existing verified CockroachDB v26.2.3 macOS arm64 binary.
3. Runs the frozen 43-execution fresh-process verifier/refusal campaign.
4. Creates one loopback-only CockroachDB single-node process in a generated
   `/private/tmp/ck-pdh3-local-r1.*` root with an empty task-local `HOME`.
5. Applies the exact P9 application migrations.
6. Generates and inserts:
   - 500 tasks;
   - 5,000 trajectory events;
   - 1,000 receipts;
   - 5,000 task-bound vectors.
   Only exact `SQLSTATE 40001` insert failures may be retried, at most three
   times per batch with fixed 250 ms backoff. Every other insert error is
   terminal, and retry counts are recorded by stage.
7. Runs four separately accounted real application-schema workloads at
   concurrency 10, 50, 100, and 250: task-bound reads, acknowledged writes,
   contended updates, and replay-idempotency writes.
8. Accounts for acknowledged writes and contended counter increments against
   each isolated workload's operation total and histogram total. They are not
   mixed into one unlabeled querybench histogram.
9. Requires idempotent replay, zero wrong-task vector linkage, zero query
   errors, exact row counts, and exact rollback.
10. Sends SIGKILL after the concurrency-50 stage, restarts from the same
    disposable store, and verifies that acknowledged state and application row
    counts survive.
11. Executes the generated dependency-ordered cleanup manifest and requires
    zero campaign residue.
12. Stops the node, proves both loopback ports are closed, and removes only the
    verified generated root.

No credential acquisition, AWS call, Lambda call, external model call, package
installation, live CockroachDB connection, RunPod worker, or public surface is
permitted.

## Frozen thresholds

- Concurrency stages: exactly `10`, `50`, `100`, `250`.
- Measured duration per stage: two seconds for the application read mix and
  one second each for acknowledged writes, contended updates, and replay.
- Minimum completed operations: 500 per stage.
- Query errors: zero.
- Insert retries: only exact `SQLSTATE 40001`, at most three per batch; all
  retry counts recorded.
- Every isolated workload histogram must account for its exact querybench
  operation total.
- Acknowledged-write row delta must equal the named acknowledged-write
  histogram count.
- Contended counter delta must equal the named contended-update histogram
  count.
- Replay-control rows: exactly one.
- Aggregate p99: at most 5,000 ms per stage.
- Aggregate pMax: at most 10,000 ms per stage.
- Wrong-task vector links: zero.
- Acknowledged application-row loss after crash/restart: zero.
- Rollback residue: zero.
- Campaign data residue after cleanup: zero.
- Verifier false promotions: zero.
- Verifier mutation after refusal: zero.
- Verifier task-root residue: zero.

Stage 500 is not authorized by this canary. It may be included only in a later
paid campaign if stages 10–250 are GREEN and the exact cost/lifecycle packet is
separately authorized.

## Evidence contract

The controller emits canonical JSON:

- `result.json`: source hashes, product/plan/packet binding, row counts, load
  metrics, per-query operation counts, latency, crash/restart evidence,
  verifier results, storage/evidence calibration, limitations, and next gate.
- `stage-c<concurrency>.json`: a canonical receipt written outside the
  disposable root immediately after each stage, before its GREEN decision.
- `teardown.json`: process, port, and generated-root teardown.
- `manifest.json`: hashes binding the final result and teardown.
- `failure.json`: a canonical fail-closed receipt when the canary does not
  reach a result. It binds every emitted stage receipt plus both the internal
  teardown receipt hash and teardown file hash.

Raw querybench logs and generated database state exist only inside the
generated disposable root. The final receipts preserve their hashes and
aggregate metrics but not the disposable rows.

## Fail-closed conditions

Stop and preserve a blocked result on:

- source, packet, candidate, migration, generated-batch, or receipt hash drift;
- any external network, credential, HOME, private, client, or production
  access;
- false verifier result or mutation after refusal;
- wrong-task vector linkage;
- query error or unaccounted operation;
- acknowledged-write or counter loss;
- replay non-idempotency;
- crash/restart data loss;
- rollback or cleanup residue;
- threshold breach;
- database process, loopback port, or generated-root teardown failure.

## Permitted conclusion

If every mechanical threshold passes and an independent GLM 5.2 review of this
exact packet is GREEN, the controller may run. If the resulting evidence also
passes independent review, the only permitted status is:

`PDH_3_LOCAL_CANARY_GREEN`

The next step remains blocked until Kenneth provides a separate exact hourly
rate ceiling, exact total-dollar ceiling, maximum paid lifetime, attempt
ceiling, and teardown authorization for the measured cloud campaign.
