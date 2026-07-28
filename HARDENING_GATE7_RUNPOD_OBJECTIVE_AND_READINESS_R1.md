# Hardening Gate 7 — RunPod Objective and Readiness R1

- `STATUS`: `DESIGN_FROZEN_EXECUTION_NOT_AUTHORIZED`
- `PARENT_GATE`: `HARDENING_6_RUN1_GREEN`
- `PARENT_CHECKPOINT`: `48414abba6f90094ebd7a1455d0694fb0fe04950`
- `EVIDENCE_CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `TARGET_GATE`: `HARDENING_7_RUN2_GREEN`
- `WORKER_COUNT`: `ONE_PRIMARY_WORKER`
- `CAMPAIGN_CLASS`: `HELD_OUT_FAILURE_AND_BOUNDED_LIVE_MEMORY`
- `PUBLIC_OR_PRODUCTION_CLAIM`: `NONE`
- `RUNPOD_CREATED`: `NO`
- `SPEND_INCURRED`: `NO`

## Stated goal

Determine whether the exact Gate 6 evidence candidate:

1. remains fail-closed on unseen, post-freeze adversarial variants; and
2. preserves correct, deterministic, observable trajectory-memory behavior on
   the actual bounded AWS and CockroachDB path.

The campaign is not intended to prove universal recovery, production scale,
multi-region behavior, public adoption, or arbitrary reconstruction of bytes
that were never captured.

## Measured workload

The primary worker must execute exactly:

- 21 held-out failure trials: three post-freeze variants for each of seven
  classes;
- seven valid held-out controls;
- 15 repeat-determinism executions: five each for representative `PROMOTE`,
  `REFUSE`, and `INVALID` inputs;
- one separately reported bounded live-memory workload through the existing
  AWS/CockroachDB integration.

The seven failure classes are:

1. tampered receipt;
2. replayed or consumed warrant;
3. malformed canonical record;
4. unsupported schema or value;
5. quarantined candidate;
6. missing or incomplete evidence;
7. interruption after one-use consumption but before mutation.

The live-memory workload must record the exact profiled operation count and
concurrency before worker creation. It must measure record, event, receipt, and
vector counts; SQLSTATE `40001` retries; duplicate handling; task-bound vector
recall; p50/p95/p99 write and retrieval latency; changefeed continuity; restart
and rollback; query-plan and index use; database and evidence growth; actual
topology; access-control evidence; and cleanup.

## Successful outcome

`HARDENING_7_RUN2_GREEN` requires all of the following:

```text
false_promotions=0
mutation_after_refusal=0
correct_stable_reason_code=100_percent
representative_determinism=100_percent
canonical_receipt_emitted=100_percent
valid_control_continuation=100_percent
hidden_session_state_dependencies=0
trial_teardown=100_percent
residue=0
output_schema_compliance=100_percent
live_memory_workload_complete=true
retrieved_evidence_hash_match=100_percent
worker_deleted=true
active_inventory_empty=true
glm_final=GREEN
agy_final=GREEN
same_final_packet_hash=true
```

Latency, storage, recall, and growth measurements are reported honestly; they
are not silently converted into pass thresholds after results are seen. Any
predeclared resource ceiling must be frozen before launch.

## Blocking outcome

Any critical failure produces `HARDENING_7_RUN2_BLOCKED`. It cannot be averaged
away, repaired on the measured worker, or omitted from the evidence package.
The exact failed vector, workload operation, receipt, and teardown state must
be preserved.

If the failure reveals a product defect, the measured candidate remains frozen
and the campaign closes blocked. A repair creates a new candidate and requires
a new contract, new held-out salt, fresh preflight review, and fresh operator
authorization.

## Setup-for-success gate

No worker may be created until every item below has direct evidence:

- [x] Gate 6 is GREEN and the private remote matches local `main`.
- [x] The Gate 6 worker inventory is empty.
- [x] The evidence-candidate commit is immutable and identified above.
- [x] A post-candidate held-out generator exists.
- [ ] A Gate 7 runner executes all 43 trials in fresh roots and processes.
- [ ] Seven valid-control fixtures are frozen separately from failure vectors.
- [ ] The interruption class proves consumed-or-invalid state and zero mutation.
- [ ] The runner emits canonical per-trial receipts and a hash-bound aggregate.
- [x] A local dry run passes with known preflight vectors only; held-out vectors
      remain ungenerated and unseen.
- [ ] The live-memory workload is locally profiled and its exact count,
      concurrency, payload ceiling, database-growth ceiling, evidence-growth
      ceiling, and expected paid duration are frozen.
- [ ] The AWS session strategy leaves at least a 15-minute margin after the last
      scheduled live exchange.
- [ ] The CockroachDB cluster identity, database, runtime role, and allowed
      schema are read back without recording credentials.
- [ ] The transfer archive contains synthetic/sanitized data only and passes
      `rg`, `gitleaks`, and `detect-secrets` scans.
- [ ] Worker image, CPU/RAM/disk, current price, maximum aggregate spend,
      maximum paid lifetime, stop/delete commands, provider-native safety
      deadlines, and detached exact-ID guard are frozen.
- [ ] Independent GLM and AGY return GREEN over the same exact preflight packet
      hash.
- [ ] Kenneth provides explicit Gate 7 RunPod lifecycle and spend authorization
      for the frozen envelope.

Until every checkbox is complete, the only valid state is:

```text
HARDENING_7_PREFLIGHT_OPEN
RUNPOD_CREATION_FORBIDDEN
```

## Worker selection and lifecycle

Use one primary CPU worker. Gate 6 proved that 2 vCPU and 4 GiB RAM can execute
the deterministic harness; Gate 7 must profile the live-memory orchestration
before reusing that shape. Select the smallest currently available CPU shape
that exceeds the measured requirement. Do not use a GPU without a measured
CUDA dependency.

The current global `runpodctl` is version `2.6.1` and is not approved for this
campaign. The previously verified temporary binary is version `2.7.2-309512b`
at `/tmp/runpodctl-v2.7.2-darwin-arm64`, SHA-256
`a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`.
It must be reverified immediately before launch or replaced by a freshly
downloaded, sandbox-local, checksum-verified current binary. Do not alter the
global installation.

There is no arbitrary project completion deadline. The paid worker must still
have bounded stop and termination times because an unbounded paid resource is
forbidden. The timer begins only after readiness, transfer-hash verification,
and smoke success. Setup time does not reduce the measured workload.

Retries are creation/readiness retries only. Each failed worker must be deleted
and exact-ID absence plus empty campaign inventory proved before another is
created. No replacement is allowed after measured evidence begins.

## Isolation and data boundary

- synthetic and sanitized inputs only;
- no API keys, OAuth artifacts, browser state, HOME state, client data, private
  memory, Qdrant, StateV2, launchd, or unrelated repository content;
- no credential transfer to RunPod;
- AWS and CockroachDB access remain on the already reviewed local control
  surface or another separately reviewed credential-free bridge;
- worker network behavior must match the frozen design and be denied by
  default outside explicitly required endpoints;
- retrieve and verify all evidence before deletion;
- deletion requires exact-ID absence and empty active inventory.

## Separate replication decision

A second worker is not part of this primary campaign. After a GREEN result, a
fresh second worker may run a smaller 10–20 percent held-out replication sample
to prove cross-instance reproducibility. That requires a separate packet and
authorization. It must not be used to replace failed primary results.

## Kill line

Kill the campaign before launch if local profiling shows the workload does not
test a claim material to the submission, or if the runner cannot distinguish a
product failure from harness, cloud-authentication, or lifecycle failure.

Kill it during execution on any secret/private-data exposure, candidate or
payload hash mismatch, unauthorized egress, price uncertainty, false
promotion, mutation after refusal, evidence-chain break, missing receipt,
resource-ceiling breach, guard failure, or unprovable teardown.
