# PDH-3 Local Canary Same-Hash Preflight R4

## Decision requested

Authorize or block one replacement no-cost local canary after preserved
Attempt 1. Review only the narrow SQLSTATE retry repair, updated hash bindings,
unchanged safety boundary, and unchanged acceptance criteria. Do not provide
code, patches, implementation plans, tool calls, or deployment direction.

The transport wrapper independently verifies served-model identity. Do not
infer or report model identity. Return one raw JSON object, with no Markdown,
containing exactly:

- `packet_sha256`
- `verdict`: `GREEN`, `NOT_GREEN`, or `BLOCKED`
- `blockers`
- `non_blocking_risks`
- `evidence_required`

## Frozen bindings

- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PLAN_SHA256`: `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- `CONTRACT_SHA256`: `8ee5d0229a238dbba96a2c22268203332a9c20b11550c74a7d093c85612f33c2`
- `CONTROLLER_SHA256`: `ae0611565c8e964f45d9bcde980cfefde19655f8d8493e3ceadbf9cba32ce802`
- `ATTEMPT1_DIAGNOSIS_SHA256`: `2501ba2616d1bb0a4851ffdbc2446e31a56b956e7973889c2c6fd5187ff5fe81`
- `ATTEMPT1_FAILURE_FILE_SHA256`: `1cc88b11dee8352262d4660d06cc9144e47001557f171cb07f91f2d61a70fb34`
- `ATTEMPT1_TEARDOWN_FILE_SHA256`: `9d93f77dec17660e442dc60d25c74c91b5aea8fff15ea619dbc66180116afdd1`
- `STATIC_PARSE`: `GREEN`
- `QUERY_FILE_GENERATION_SMOKE`: `GREEN`
- `RETRY_UNIT_SMOKE`: `GREEN`
- `SECRET_PATTERN_SCAN`: `GREEN`
- `PAID_RESOURCES`: forbidden
- `NETWORK`: loopback CockroachDB only; diagnostics disabled
- `DATA`: synthetic only
- `PRODUCT_MUTATION`: forbidden
- `EXTERNAL_TESTER`: deliberately skipped by Kenneth

## Preserved Attempt 1

Attempt 1 stopped before the measured load stages. Its canonical failure
receipt is preserved. Teardown proves:

- database process stopped;
- both generated loopback ports closed;
- generated root removed.

A bounded fresh-root reproduction applied both P9 migrations and inserted the
same generated data:

- tasks: 2/2 batches passed;
- events: 20/20 batches passed;
- receipts: 4/4 batches passed;
- vectors: batches 1–13 passed;
- vector batch 14 returned exact `SQLSTATE 40001` /
  `RETRY_SERIALIZABLE`;
- no other error class appeared;
- the diagnostic node stopped and its generated root was removed.

The failure is a controller omission: the existing Gate 7 bulk controller
already permits bounded retries for exact `SQLSTATE 40001`, but the first
PDH-3 controller used a generic single-attempt command helper.

## Narrow repair

Only generated insert-batch execution changed:

1. Run the exact generated batch.
2. If it succeeds, continue.
3. If output contains exact `SQLSTATE: 40001` and fewer than three retries have
   occurred for that batch, record a retry, wait exactly 250 ms, and rerun the
   same immutable batch.
4. Any other SQLSTATE, error, timeout, hash mismatch, or fourth `40001` failure
   is terminal.
5. Record retry count by stage and in aggregate.

The retry unit smoke proves:

- one `40001` followed by success produces one recorded retry;
- a non-`40001` SQLSTATE fails immediately with
  `INSERT_BATCH_FAILED:<stage>:<batch>:<output hash>`.

No product code, schema, generated row, workload, concurrency, latency
threshold, evidence contract, claim boundary, or teardown behavior changed.

## Unchanged canary contract

The canary:

1. Runs the frozen 43-execution fresh-process verifier/refusal campaign.
2. Starts one disposable CockroachDB v26.2.3 macOS arm64 node bound to
   loopback in `/private/tmp/ck-pdh3-local-r1.*`, with task-local empty HOME.
3. Applies the real P9 schema and collision-safe vector migration.
4. Seeds 500 tasks, 5,000 events, 1,000 receipts, and 5,000 task-bound vectors.
5. Runs isolated task-bound reads, acknowledged writes, contended updates, and
   replay-idempotency writes at concurrency 10, 50, 100, and 250.
6. Requires exact per-workload histogram accounting, acknowledged-write
   accounting, counter accounting, replay idempotency, zero query errors, p99
   at most 5,000 ms, and pMax at most 10,000 ms.
7. Sends SIGKILL after concurrency 50, restarts the same disposable disk store,
   and requires zero application-row loss.
8. Requires zero wrong-task vector linkage, exact rollback, and zero
   campaign-row residue after dependency-ordered cleanup.
9. Stops the process, proves both ports closed, validates the generated-root
   identity, and deletes only that root.
10. Writes canonical result, teardown, manifest, or failure receipts.

No AWS, Lambda, RunPod, live CockroachDB, credential, package installation,
external model, public action, client data, production data, Qdrant, StateV2,
launchd, or HOME runtime access is permitted.

## Permitted conclusion

GREEN authorizes exactly one replacement local canary. It does not authorize:

- Stage 500;
- paid provisioning;
- PDH-3 GREEN;
- cloud-scale, production, or external-user claims;
- PDH-4 or PDH-5.

Paid execution remains a separate human gate requiring an exact hourly-dollar
ceiling, total-dollar ceiling, maximum paid lifetime, creation-attempt ceiling,
and teardown authorization.
