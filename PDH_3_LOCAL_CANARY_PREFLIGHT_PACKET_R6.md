# PDH-3 Local Canary Corrected Preflight Packet R6

## Decision requested

Act only as an independent, non-authoring GLM 5.2 judge. Determine whether the
corrected local canary may execute. Do not write code or propose product
features.

Return raw JSON only:

```json
{
  "verdict": "GREEN|NOT_GREEN|INSUFFICIENT_EVIDENCE",
  "packet_sha256": "<exact supplied packet hash>",
  "controller_sha256": "<exact controller hash below>",
  "blocking_findings": [],
  "non_blocking_risks": [],
  "required_evidence_after_execution": []
}
```

`GREEN` means the measurement repair is technically sound, bounded,
fail-closed, does not weaken database-to-client accounting, and is safe to run
under the declared local boundary.

## Frozen identities

- `PRODUCT_CANDIDATE`:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PLAN_SHA256`:
  `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- `CONTROLLER_SHA256`:
  `3371a2952c29c649a5940da4eaf5dfa724b5f7d524e17b110460cb6365169fc1`
- `CONTRACT_SHA256`:
  `f48f65aa447e10c84164e053f4cbd4d101bad2175a7f54b51878f4a6f5de1026`
- `ATTEMPT_3_DIAGNOSIS_SHA256`:
  `68c6052da33faf0150e3aa523f4568e57d94c425b5f6ff3ca54de67907dc1465`
- `CALIBRATION_SHA256`:
  `8592a77f7018d147daae06ebaad16f9e2969f295637925990444921f9b9d72f0`

The controller, contract, diagnosis, and calibration are frozen. A later
change invalidates this preflight.

## Boundary

- No paid resource.
- No AWS, Lambda, RunPod, live CockroachDB, external tester, or public action.
- Loopback-only single-node CockroachDB v26.2.3.
- Synthetic data only.
- Generated `/private/tmp/ck-pdh3-local-r1.*` root only.
- Empty task-local HOME passed only to child processes.
- Product candidate and product behavior remain unchanged.
- HOME runtime, credentials, Qdrant, StateV2, launchd, client data, production
  data, and unrelated repositories are forbidden.
- Any mismatch, error, threshold breach, or teardown failure is terminal.
- Maximum successful conclusion: `PDH_3_LOCAL_CANARY_GREEN`.
- Production-shaped/cloud-scale GREEN is forbidden from this run.

## Preserved failed evidence

Attempt 3 stopped at concurrency 10 because:

- QueryBench summary: 1,857 acknowledged writes.
- Database delta: 1,867 acknowledged-write rows.
- QueryBench summary: 351 contended updates.
- Database delta: 355 counter increments.
- Query errors: zero.
- Histogram-to-summary equality: true.
- Total reported operations: 92,149.
- Maximum workload p99: 41.9 ms.
- Maximum latency: 48.2 ms.
- Database stopped, ports closed, and generated root removed.

The attempt remains `BLOCKED` and is not relabeled.

## Root cause and rejected alternatives

Duration-bounded concurrent mutations did not share one final accounting
boundary: committed database effects exceeded QueryBench's final reported
interval.

`--num-runs` was tested and rejected because a nominal 200-operation probe did
not terminate after more than 30 seconds.

QueryBench's `--max-ops` is a concurrent soft cap. At concurrency 10, two
fresh-root probes showed that a soft cap of 200 produced 209 writes and a soft
cap of 100 produced 109 updates. In every probe:

- QueryBench summary equaled histogram count;
- database-side effect equaled the same observed count;
- errors were zero;
- process and generated root teardown completed.

## Corrected measurement rule

The corrected controller freezes a minimum and permits only the concurrency
overshoot already issued by QueryBench:

```text
minimum <= observed operations <= minimum + concurrency - 1
```

This is not approximate accounting. A mutating workload passes only if:

```text
QueryBench summary == QueryBench histogram == database-side effect
```

The exact frozen per-stage bounds are:

- acknowledged writes: 2,000 through `2,000 + concurrency - 1`;
- contended updates: 1,000 through `1,000 + concurrency - 1`;
- replay operations: 1,000 through `1,000 + concurrency - 1`.

The read workload remains duration-bounded because it has no database mutation
to reconcile.

## Corrected-controller calibration

The exact frozen controller was exercised at concurrency 10 and 50:

| Concurrency | Workload | Min | Max | Summary | Histogram | DB effect |
|---:|---|---:|---:|---:|---:|---:|
| 10 | acknowledged write | 2,000 | 2,009 | 2,009 | 2,009 | 2,009 |
| 10 | contended update | 1,000 | 1,009 | 1,009 | 1,009 | 1,009 |
| 10 | replay | 1,000 | 1,009 | 1,009 | 1,009 | 1 row |
| 50 | acknowledged write | 2,000 | 2,049 | 2,049 | 2,049 | 2,049 |
| 50 | contended update | 1,000 | 1,049 | 1,049 | 1,049 | 1,049 |
| 50 | replay | 1,000 | 1,049 | 1,049 | 1,049 | 1 row |

All six workloads had zero errors. Both database processes stopped and both
generated roots were removed. No calibration process or root remained.

## Load-bearing controller logic

The controller rejects a call unless exactly one boundary is selected:

```python
if (duration_seconds is None) == (minimum_operations is None):
    raise CanaryError("QUERYBENCH_BOUNDARY_INVALID")
```

For fixed operations it records the mechanical interval:

```python
command.append(f"--max-ops={minimum_operations}")
execution_boundary = {
    "mode": "BOUNDED_FIXED_OPERATIONS",
    "duration_seconds": None,
    "minimum_operations": minimum_operations,
    "maximum_operations": minimum_operations + concurrency - 1,
    "querybench_soft_cap": minimum_operations,
}
```

It writes stdout/stderr, requires exit zero, parses the final summary, parses
the histogram, and records hashes for all three raw outputs:

```python
if completed.returncode != 0:
    raise CanaryError(f"QUERYBENCH_FAILED_C{concurrency}_{kind}")
summary = parse_querybench_summary(completed.stdout)
histogram_count = parse_histogram_count(histogram_path)
```

Each stage checks:

```python
"zero_errors": all(workload["summary"]["errors"] == 0 ...),
"histograms_account_for_operations": all(
    workload["histogram_accounts_for_operations"] ...
),
"bounded_operation_targets_respected": all(
    workload["execution_boundary"]["minimum_operations"]
    <= workload["summary"]["operations"]
    <= workload["execution_boundary"]["maximum_operations"]
    for workload in mutating_workloads
),
"acknowledged_writes_exact": (
    ack_after - ack_before
    == workloads["ack_write"]["summary"]["operations"]
),
"contended_updates_exact": (
    counter_after - counter_before
    == workloads["contended_update"]["summary"]["operations"]
),
"replay_idempotent": replay_rows == 1,
"p99_within_limit": p99 <= 5000.0,
"pmax_within_limit": pmax <= 10000.0,
```

The canonical stage receipt is written outside the disposable database root
before its GREEN decision. Any false check raises
`CONCURRENCY_STAGE_NOT_GREEN:<stage>:<failed checks>`.

## Unchanged full-canary requirements

- Concurrency stages: 10, 50, 100, and 250.
- Read-mix duration: two seconds per stage.
- Minimum total operations: 500 per stage.
- Query errors: zero.
- Every workload histogram equals its QueryBench summary.
- p99 at most 5,000 ms; pMax at most 10,000 ms.
- 43 fresh-process verifier/refusal executions.
- False promotions, mutation after refusal, task-root residue: zero.
- 500 tasks, 5,000 events, 1,000 receipts, 5,000 vectors.
- Wrong-task vector links: zero.
- Insert retry only for exact SQLSTATE 40001, at most three per batch.
- SIGKILL/restart after concurrency 50 with zero acknowledged-state loss.
- Rollback residue: zero.
- Campaign cleanup residue: zero.
- Process stopped, both ports closed, generated root removed.
- Canonical result, stages, teardown, failure, and manifest receipts.

## Judge questions

1. Does the bounded soft-cap interval accurately preserve exact accounting
   without accepting missing or unaccounted operations?
2. Does the database equality check prove acknowledged write and contended
   update effects exactly?
3. Is the calibration sufficient to authorize one full local canary while
   preserving fail-closed behavior at concurrency 100 and 250?
4. Is any product, claim, cloud, paid-resource, or external-user boundary
   silently expanded?

