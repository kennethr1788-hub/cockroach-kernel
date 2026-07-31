# PDH-3 Corrected Local Canary Report R1

## Result

`PDH_3_LOCAL_CANARY_GREEN`

- `PRODUCT_CANDIDATE`:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PLAN_SHA256`:
  `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- `CONTROLLER_SHA256`:
  `3371a2952c29c649a5940da4eaf5dfa724b5f7d524e17b110460cb6365169fc1`
- `CONTRACT_SHA256`:
  `f48f65aa447e10c84164e053f4cbd4d101bad2175a7f54b51878f4a6f5de1026`
- `RESULT_RECEIPT_SHA256`:
  `ec230f0a3284c85d99cf9e6ca0a33c9fd928dd3b7c61b1916c49d71ebbf46a67`
- `FINAL_REVIEW_PACKET_SHA256`:
  `1e802282b5153913eeb6f7eac3f6f3444133794c439fd2cddb8d6fc0c70d1ef8`
- `FINAL_GLM_RAW_FILE_SHA256`:
  `0c699fdb29ff1d20c787ce13d90a2b4b4addaf5208932568014ba160b6188962`
- `FINAL_JUDGE`: `GLM 5.2`
- `FINAL_JUDGE_VERDICT`: `GREEN`
- `UTC_VERIFIED`: `2026-07-31T02:49:50Z`

This is a local single-node synthetic calibration. It is not production,
cloud-scale, external-user, or paid-resource evidence.

## Corrected accounting

Attempts 1–3 remain preserved as failed evidence. Attempt 3 proved that
duration-bounded concurrent mutations could commit outside QueryBench's final
reported interval. The corrected controller uses a bounded operation interval
and still requires exact equality:

```text
QueryBench summary == histogram count == database-side effect
```

At concurrency 10, 50, 100, and 250, every mutating workload stayed within
`minimum ... minimum + concurrency - 1`, every exact equality passed, and every
workload reported zero errors.

## Measured evidence

- Total measured operations: 178,264.
- Aggregate measured throughput: 6,830.038 operations/second.
- Maximum p99: 973.1 ms.
- Maximum latency: 973.1 ms.
- Synthetic application rows:
  - 500 tasks;
  - 5,000 trajectory events;
  - 1,000 receipts;
  - 5,000 task-bound vectors.
- Wrong-task vector links: zero.
- Exact SQLSTATE 40001 serialization retries: four across vector batches.
- Verifier/refusal executions: 43.
- Correct stable reasons: 43.
- False promotions: zero.
- Mutation after refusal: zero.
- Verifier residue: zero.
- SIGKILL/restart after concurrency 50: GREEN.
- Rollback residue: zero.
- Campaign cleanup residue: `[0, 0, 0, 0]`.

## Teardown

- Database process stopped.
- Both loopback ports closed.
- Generated canary root removed.
- Post-run process scan found no canary or CockroachDB process.
- Post-run root scan found no canary root.

## Independent review

The preflight packet was independently GREEN under verified GLM 5.2. One
fenced response was preserved as invalid-format evidence; only the strict
raw-JSON response authorized execution.

The final evidence packet was independently reviewed by verified GLM 5.2 over
the exact packet hash. It returned:

- `verdict`: `GREEN`
- `blocking_findings`: `[]`
- `non_blocking_risks`: `[]`
- `permitted_status`: `PDH_3_LOCAL_CANARY_GREEN`

## Remaining gate

Full `PDH_3_PRODUCTION_SHAPED_SCALE_GREEN` is not established. Any paid cloud
campaign remains blocked until Kenneth separately authorizes:

- exact hourly-dollar ceiling;
- exact total-dollar ceiling;
- maximum paid lifetime;
- creation-attempt ceiling;
- exact teardown authority.

PDH-2 remains deliberately skipped. No external-user claim is permitted.
