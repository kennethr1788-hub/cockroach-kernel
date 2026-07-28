# Hardening Gate 7 — Bounded Live-Memory Workload R1

- `STATUS`: `COUNTS_FROZEN_IMPLEMENTATION_OPEN`
- `PURPOSE`: `MEASURE_COCKROACHDB_MEMORY_BEHAVIOR_NOT_UNIVERSAL_SCALE`
- `CREDENTIAL_SURFACE`: `REVIEWED_LOCAL_CONTROL_ONLY`
- `RUNPOD_CREDENTIALS`: `ZERO`
- `PRODUCT_CANDIDATE_CHANGE`: `NO`
- `OFFLINE_PROFILE_SHA256`: `6999749effba49ab7c0b94726395528989ccc6c971901eeaf4eb8f0bdd91596b`
- `OFFLINE_PROFILE_FILE_SHA256`: `916f902d8ab05c550f1daf4cd4c6c12b853fc9ba6a69c89769a12b4cbc1be17e`
- `OFFLINE_PROFILE_SCOPE`: `INPUT_SIZING_ONLY_NOT_DATABASE_PERFORMANCE`

## Exact workload

The workload is operation-count based, not an arbitrary soak duration:

```text
task_groups=2000
trajectory_events_per_task=10
trajectory_events_total=20000
receipts_per_task=2
receipts_total=4000
context_vectors_per_task=10
context_vectors_total=20000
task_bound_vector_queries=200
end_to_end_aws_lambda_calls=12
end_to_end_promote_calls=6
end_to_end_refuse_calls=6
credential_free_request_streams=4
```

The direct storage-load rows and the twelve end-to-end calls are reported
separately. Direct SQL loading is not relabeled as an end-to-end product call.
The existing AWS/CockroachDB path must still complete all twelve bounded calls.

## Why this size

Gate 6 showed the offline deterministic runner is inexpensive. S3 produced 11
successful live calls with median coordinator latency of 9,504 ms, 99 verified
CockroachDB operations, and zero backlog before the twelfth call failed closed
on expired AWS authentication. The Gate 7 workload therefore spends its new
evidence budget on a larger retained memory population rather than another
long idle timer.

Two thousand task groups and twenty thousand vectors are large enough to expose
batching, index-plan, growth, cleanup, and task-bound retrieval defects while
remaining safely below the existing 512 MiB database-growth ceiling when the
preflight estimate is correct. The twelve full-path calls remain within the
existing reviewed protocol and cost envelope.

The Python 3.12.13 offline sizing profile generated 46,000 synthetic storage
rows with 11,787,916 canonical input bytes in 868 ms. This supports the payload
and evidence ceilings only. It does not predict CockroachDB latency, index use,
database growth, or cloud cost; those remain measured outputs of the live run.

## Required measurements

- inserted and retained row counts by table;
- duplicate and conflicting-duplicate result;
- one bounded SQLSTATE `40001` retry probe;
- top-1 and top-8 task-bound vector recall over 200 frozen queries;
- p50, p95, and p99 batch-write latency;
- p50, p95, and p99 vector-retrieval latency;
- `EXPLAIN` evidence for the declared vector and linkage indexes;
- changefeed initial and restart cursor continuity;
- client/coordinator restart at the halfway cursor and exact resumption;
- one transaction rollback batch with zero committed rows;
- database bytes before load, after load, and after exact cleanup;
- evidence bytes by class;
- actual cluster topology and actual concurrency;
- runtime grants, audit view, and observability evidence;
- exact campaign-prefix cleanup with zero residual campaign rows.

## Hard correctness thresholds

```text
wrong_task_vector_returned=0
expected_exact_target_missing_from_top_1=0
expected_target_missing_from_top_8=0
duplicate_conflict_silently_accepted=0
retry_probe_unresolved=0
changefeed_restart_mismatch=0
rollback_rows_committed=0
restart_cursor_gap_or_duplicate=0
end_to_end_call_failures=0
end_to_end_false_promotions=0
cleanup_residue_rows=0
database_growth_bytes_max=536870912
evidence_growth_bytes_max=67108864
```

Latency values are measurements, not retroactively chosen pass criteria. The
final report must disclose them and compare them with the prior S3 range.

## Execution architecture

The RunPod worker remains credential-free. It owns the frozen workload order,
canonical requests, local Gate 7 verifier trials, checkpoints, and receipt
validation. A strict local bridge maps only enumerated workload operations to
parameterized CockroachDB actions and the fixed Lambda function. Worker fields
cannot select SQL text, paths, URLs, ARNs, shell commands, credentials, or an
arbitrary row count.

The storage load uses campaign-prefixed synthetic IDs. It may insert and delete
only those IDs. It may not alter schemas, roles, grants, cluster settings,
unrelated rows, or production data.

## Readiness still required

- implement and test the bounded load generator and strict bridge schema;
- prove every SQL statement is parameterized or generated only from fixed
  enumerations and bounded integers;
- dry-run the exact row-count and cleanup manifests locally;
- freeze the offline sizing receipt;
- verify CockroachDB capacity and the current AWS session window immediately
  before measured execution;
- independently review the complete same-hash Gate 7 preflight packet.

This document does not authorize a worker, cloud mutation, or spend.
