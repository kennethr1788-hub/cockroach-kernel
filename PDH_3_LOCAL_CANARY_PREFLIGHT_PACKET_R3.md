# PDH-3 Local Canary Same-Hash Preflight R3

## Decision requested

Authorize or block one no-cost local canary. Review safety, evidence integrity,
threshold sufficiency, teardown, and contract/controller parity. Do not provide
code, patches, implementation plans, tool calls, or deployment direction.

The transport wrapper independently verifies served-model identity. Do not
infer, adopt, or report model identity. Return strict JSON with exactly:

- `packet_sha256`
- `verdict`: `GREEN`, `NOT_GREEN`, or `BLOCKED`
- `blockers`
- `non_blocking_risks`
- `evidence_required`

## Frozen bindings

- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PLAN_SHA256`: `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- `CONTRACT`: `PDH_3_LOCAL_CANARY_PACKET_R1.md`
- `CONTRACT_SHA256`: `9ca617c474476f6d4448aa8c896866543ffcce15a7452fd9ba6dd134e00b7844`
- `CONTROLLER`: `post-dogfood/run_pdh3_local_canary.py`
- `CONTROLLER_SHA256`: `61e6b649dcb263bbefa65c6cee8a0b40698be865d21d744b1879dfab117422de`
- `STATIC_PARSE`: `GREEN`
- `QUERY_FILE_GENERATION_SMOKE`: `GREEN`
- `SECRET_PATTERN_SCAN`: `GREEN`
- `PAID_RESOURCES`: forbidden
- `NETWORK`: loopback CockroachDB only; diagnostics explicitly disabled
- `DATA`: synthetic only
- `PRODUCT_MUTATION`: forbidden
- `EXTERNAL_TESTER`: deliberately skipped by Kenneth

R1 review transport produced no output. The smaller contract-only attempt
returned substantively GREEN but falsely self-reported a different served
model, so it is invalid. R2 embedded the entire 39 KB controller and reached
the verified GLM 5.2 endpoint, but the provider ended at
`finish_reason=length` with empty content. Neither attempt authorizes execution.

## Contract

The canary:

1. Binds the candidate, plan, contract SHA, and controller source hashes.
2. Runs the frozen 43-execution fresh-process verifier/refusal campaign.
3. Starts one disposable CockroachDB v26.2.3 macOS arm64 node bound to
   loopback in `/private/tmp/ck-pdh3-local-r1.*`, with an empty task-local
   `HOME` and diagnostics disabled.
4. Applies the real P9 CockroachDB schema and collision-safe vector migration.
5. Seeds exactly 500 tasks, 5,000 events, 1,000 receipts, and 5,000
   task-bound vectors using the existing deterministic bulk generator.
6. Runs four isolated application workloads at concurrency 10, 50, 100, and
   250:
   - task-bound vector, receipt, stale-projection, and trajectory-link reads;
   - unique acknowledged writes;
   - a shared contended counter update;
   - fixed-key idempotent replay writes.
7. Uses a separate querybench process and histogram for each workload so the
   operation denominator is exact. It compares acknowledged row and counter
   deltas directly to the corresponding workload operation totals.
8. Requires every workload histogram total to equal its querybench total.
9. Sends SIGKILL after concurrency 50, restarts the same disposable disk store,
   and compares all application row counts before and after restart.
10. Requires zero wrong-task vector linkage, exact rollback, dependency-ordered
    campaign cleanup, and zero campaign row residue.
11. Stops the process, verifies both loopback ports are closed, validates the
    generated-root identity, and removes only that generated root.
12. Writes canonical result, teardown, manifest, or fail-closed failure
    receipts outside the deleted temporary root.

No AWS, Lambda, RunPod, live CockroachDB, credential, package installation,
external model, public action, client data, production data, Qdrant, StateV2,
launchd, or HOME runtime access is permitted.

## Frozen acceptance

- Exact concurrency stages: 10, 50, 100, 250.
- Read mix: two measured seconds per stage.
- Acknowledged-write, contended-update, and replay workloads: one measured
  second each per stage.
- At least 500 aggregate operations per stage.
- Zero querybench errors.
- Every workload histogram accounts for its exact operation total.
- Acknowledged-write delta equals acknowledged-write operations.
- Counter delta equals contended-update operations.
- Replay-control row count remains exactly one.
- Per-workload aggregate p99 is at most 5,000 ms.
- Per-workload aggregate pMax is at most 10,000 ms.
- Zero wrong-task vector links.
- Zero application-row loss across SIGKILL/restart.
- Exact seeded row counts before and after load.
- Rollback residue zero.
- Campaign cleanup residue `(0,0,0,0)`.
- Frozen verifier campaign GREEN with zero false promotions, zero mutation
  after refusal, 43 stable reasons, 43 task-root teardowns, and zero residue.
- Database process absent, both ports closed, and generated root absent.

Stage 500 is not authorized. The canary cannot produce PDH-3 GREEN, cloud-scale
evidence, production evidence, external-user evidence, or a provider cost
claim.

## Code-parity facts mechanically inspected

- `find_cockroach()` requires exactly one executable Darwin binary.
- `scrubbed_env()` contains only task-local HOME, locale, deterministic Python
  settings, UTC, a bounded PATH, and disabled Cockroach diagnostics.
- `reserve_port()` binds only `127.0.0.1`.
- `start_database()` binds SQL and HTTP to `127.0.0.1`, uses the verified
  generated store/temp roots, and fails if readiness does not arrive.
- SQL execution passes statements directly to the pinned local CockroachDB
  binary; no network client or cloud adapter is invoked for execution.
- Generated SQL batch SHA-256 values are checked before insertion.
- Querybench exit, output, histogram, row-delta, replay, latency, and error
  checks are fail-closed.
- The crash occurs only after a completed stage; restart compares all four
  application table counts.
- Cleanup uses the generator's dependency-ordered, campaign-prefixed cleanup
  manifest.
- `finally` stops the node, probes both ports, checks the exact generated-root
  parent/prefix, deletes that root, and writes a teardown receipt.
- `main()` writes a controlled failure receipt on every caught execution
  failure without embedding raw command output.

## Evidence required after execution

- Result and teardown receipts bind the reviewed contract and controller
  hashes.
- All mechanical acceptance booleans are true.
- Final manifest hashes bind result and teardown.
- No process, port, or generated root remains.
- A final independent review classifies the evidence.

If preflight is GREEN, only the local canary is authorized. Paid provisioning
still requires a separate exact hourly-dollar ceiling, total-dollar ceiling,
maximum paid lifetime, creation-attempt ceiling, and teardown authorization.
