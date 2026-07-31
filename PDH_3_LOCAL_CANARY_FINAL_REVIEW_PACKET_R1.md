# PDH-3 Corrected Local Canary Final Review Packet R1

## Decision requested

Act only as independent, non-authoring GLM 5.2 final judge. Determine whether
the exact corrected local canary evidence supports
`PDH_3_LOCAL_CANARY_GREEN`.

Return raw JSON only:

```json
{
  "verdict": "GREEN|NOT_GREEN|INSUFFICIENT_EVIDENCE",
  "packet_sha256": "<exact supplied review-packet hash>",
  "result_sha256": "ec230f0a3284c85d99cf9e6ca0a33c9fd928dd3b7c61b1916c49d71ebbf46a67",
  "blocking_findings": [],
  "non_blocking_risks": [],
  "permitted_status": "PDH_3_LOCAL_CANARY_GREEN|PDH_3_LOCAL_CANARY_BLOCKED"
}
```

Do not authorize cloud-scale, production, external-user, or paid-resource
claims.

## Frozen authority

- `PRODUCT_CANDIDATE`:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PLAN_SHA256`:
  `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- `CONTROLLER_SHA256`:
  `3371a2952c29c649a5940da4eaf5dfa724b5f7d524e17b110460cb6365169fc1`
- `CONTRACT_SHA256`:
  `f48f65aa447e10c84164e053f4cbd4d101bad2175a7f54b51878f4a6f5de1026`
- `PREFLIGHT_PACKET_SHA256`:
  `a320f9b291ca5da8e404fa5fcfe3ab64da3dc87904e8ff8a1e2186036ba3f11e`
- `PREFLIGHT_GLM_RAW_FILE_SHA256`:
  `da96a853ff89abafbec099e2825c93e3b29ff384f99eabfa95b0bc0b2dcc616a`
- `PREFLIGHT_GLM_SERVED_MODEL`: `glm-5.2`
- `PREFLIGHT_VERDICT`: `GREEN`

The earlier fenced output is preserved separately as invalid-format evidence.
Only the strict raw-JSON preflight authorized execution.

## Mechanical result

- `ATTEMPT`: `evidence/pdh3-local-canary-r4`
- `STATUS`: `GREEN`
- `RESULT_RECEIPT_SHA256`:
  `ec230f0a3284c85d99cf9e6ca0a33c9fd928dd3b7c61b1916c49d71ebbf46a67`
- `RESULT_FILE_SHA256`:
  `d0452239a271cab1f447f79e4ede7678d64a0f2121af11d60b8f33cf5573cd5a`
- `MANIFEST_RECEIPT_SHA256`:
  `87c75b8a279c2102e0608e6586bc1365f615bab3fb3e861d5c1551835b39fd4f`
- `MANIFEST_FILE_SHA256`:
  `347abdbe3c71c5c8dab4828aa86372364b14fe0bfe286b3f7343ee0afdeebf70`
- `TEARDOWN_RECEIPT_SHA256`:
  `6553a9c8aeadbf73d98857ee3fda55af1e2b94edbf065456bbdb885b59551e83`
- `TEARDOWN_FILE_SHA256`:
  `76179bc9ca6cad9f948082889fe74832a20dbde8a855755b3507fedba50387a8`

Canonical recomputation passed for the result, manifest, all stage receipts,
and teardown receipt. Every manifest file hash matched the corresponding file.
The stage payloads embedded in `result.json` matched the independent stage
receipts exactly.

## Stage evidence

| C | Total ops | Ack summary/DB | Update summary/DB | Replay ops/rows | p99 ms | pMax ms | Errors |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 43,501 | 2,009 / 2,009 | 1,009 / 1,009 | 1,009 / 1 | 41.9 | 46.1 | 0 |
| 50 | 45,934 | 2,049 / 2,049 | 1,049 / 1,049 | 1,049 / 1 | 209.7 | 218.1 | 0 |
| 100 | 45,435 | 2,099 / 2,099 | 1,099 / 1,099 | 1,099 / 1 | 385.9 | 385.9 | 0 |
| 250 | 43,394 | 2,249 / 2,249 | 1,249 / 1,249 | 1,249 / 1 | 973.1 | 973.1 | 0 |

At every stage:

- all canonical stage checks were true;
- the operation total was within the frozen
  `minimum ... minimum + concurrency - 1` interval;
- each histogram equaled its QueryBench summary exactly;
- acknowledged-write database delta equaled its summary exactly;
- contended-update database delta equaled its summary exactly;
- replay produced exactly one idempotent row;
- every workload reported zero errors;
- p99 and pMax remained below frozen limits.

Stage receipt file hashes:

- `stage-c10.json`:
  `4f007c5a8436b747196c732fee6d76742b2eb3664db529b0f98cac2a03238624`
- `stage-c50.json`:
  `a04be44a95f1963cfdb7655295bc48a3074e225a5209c61d127d3c3f61244017`
- `stage-c100.json`:
  `df321b41f7fca40b27f86d589ac89a189481d8fc0ddfd1206f932da1bd10c05d`
- `stage-c250.json`:
  `1eac5195f19109cc5f39feefa306c9fe282bedd8559d5ac11b69291eff369b72`

## Dataset, verifier, and durability

- Synthetic tasks: 500.
- Synthetic trajectory events: 5,000.
- Synthetic receipts: 1,000.
- Task-bound vectors: 5,000.
- Initial and final application counts: `[500, 5000, 1000, 5000]`.
- Wrong-task vector links: zero.
- Insert batches: 46.
- Exact SQLSTATE 40001 serialization retries: four total, all in vector
  batches; controller permits at most three per individual batch and makes all
  other errors terminal.
- Fresh-process verifier/refusal executions: 43.
- Correct stable reasons: 43.
- False promotions: zero.
- Mutation after refusal: zero.
- Trial teardowns: 43.
- Verifier residue: zero.
- Valid control continuations: 12.

After concurrency 50:

- the database received SIGKILL and returned `-9`;
- application counts before and after restart were identical;
- 4,058 acknowledged rows remained after restart;
- crash/restart result was GREEN.

Rollback residue was zero. Campaign cleanup counts were `[0, 0, 0, 0]`.

## Teardown and containment

- Database process stopped: true.
- Both loopback ports closed: true.
- Generated `/private/tmp/ck-pdh3-local-r1.*` root removed: true.
- Post-run process scan found no canary or CockroachDB process.
- Post-run root scan found no generated canary root.
- Network scope: loopback only.
- Paid resources: false.
- Cloud execution: false.

## Calibration summary

- Measured operations: 178,264.
- Measured workload time: 26.1 seconds.
- Aggregate throughput: 6,830.038 operations/second.
- Database bytes per seeded trajectory: 26,874.692.
- Evidence bytes per measured operation: 0.455358.

These are local calibration values, not production or cloud claims.

## Required limitations

The result explicitly preserves:

- `LOCAL_SINGLE_NODE_ONLY`
- `SYNTHETIC_ONLY`
- `NOT_PRODUCTION`
- `NOT_CLOUD_SCALE`
- `NO_EXTERNAL_TESTER`
- `NO_PAID_EXECUTION_AUTHORIZED`
- `NO_PROVIDER_COST_ESTIMATE_WITHOUT_LIVE_PRICING`

The next gate remains
`SEPARATE_EXACT_OPERATOR_AUTHORIZATION_REQUIRED` for any paid measured cloud
campaign.

## Final questions

1. Do the receipts prove the corrected local canary passed all frozen
   mechanical requirements?
2. Did the correction preserve exact database/client accounting rather than
   weaken it?
3. Is `PDH_3_LOCAL_CANARY_GREEN` the maximum honest conclusion?
4. Is any broader claim unsupported or silently implied?

