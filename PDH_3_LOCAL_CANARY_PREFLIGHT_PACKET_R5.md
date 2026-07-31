# PDH-3 Local Canary Same-Hash Preflight R5

## Decision requested

Authorize or block one replacement no-cost local canary after preserved
Attempts 1 and 2. Review the stage-receipt observability repair, updated hashes,
and unchanged run contract. Do not provide code, patches, implementation plans,
tool calls, or deployment direction.

The transport wrapper independently verifies served-model identity. Return one
raw JSON object, with no Markdown, containing exactly `packet_sha256`,
`verdict`, `blockers`, `non_blocking_risks`, and `evidence_required`.

## Frozen bindings

- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PLAN_SHA256`: `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- `CONTRACT_SHA256`: `bedae518f472b286654353b48f3eb608bfd699c1715df8b42fb66b0a54ef027f`
- `CONTROLLER_SHA256`: `85349ab6e04a85d0c83ad173a1977bab4efcee031c32cf2d47419263b888e75d`
- `ATTEMPT1_DIAGNOSIS_SHA256`: `2501ba2616d1bb0a4851ffdbc2446e31a56b956e7973889c2c6fd5187ff5fe81`
- `ATTEMPT2_DIAGNOSIS_SHA256`: `16e57045a5692f6f8b9db0d726b1465e3fed5759229f7f505d5de3f732b464f0`
- `ATTEMPT2_FAILURE_FILE_SHA256`: `5115c2043de97e12d7bf90d7a8d95d500d3085f54c7f3368958c56412d961435`
- `ATTEMPT2_TEARDOWN_FILE_SHA256`: `f794f21859370f658d6ebe152bacdd5b382a65c9b4ce4c09f60f1ce464f57326`
- `STATIC_PARSE`: `GREEN`
- `STAGE_RECEIPT_STATIC_CHECK`: `GREEN`
- `PAID_RESOURCES`: forbidden
- `NETWORK`: loopback CockroachDB only; diagnostics disabled
- `DATA`: synthetic only
- `PRODUCT_MUTATION`: forbidden
- `EXTERNAL_TESTER`: deliberately skipped by Kenneth

## Preserved history

Attempt 1 stopped on vector insert batch 14 after exact `SQLSTATE 40001`.
Its process, ports, and generated root were cleanly torn down. A bounded
diagnostic reproduced the serialization retry. The R4-reviewed repair retries
only exact `40001`, at most three times per immutable batch with fixed 250 ms
backoff, and records all retry counts.

Attempt 2 reached concurrency stage 10 and classified it non-GREEN. Its process,
ports, and generated root were cleanly torn down. The only surviving failure
receipt says `CONCURRENCY_STAGE_NOT_GREEN:10`; the detailed stage metrics were
inside the disposable root and were destroyed by correct teardown. Therefore
the exact failed acceptance check is unknown and must not be guessed.

## Narrow R5 repair

No execution behavior changes. The controller now:

1. Writes `stage-c<concurrency>.json` outside the disposable root immediately
   after a stage returns and before deciding whether the stage is GREEN.
2. Binds candidate and current contract hash into the stage receipt.
3. Includes complete per-workload summaries, histogram counts, row/counter
   deltas, replay count, latency maxima, acceptance booleans, and an internal
   receipt hash.
4. On a non-GREEN stage, enumerates the false acceptance checks in the
   controlled failure class.
5. Binds every stage receipt file hash into the final manifest or failure
   receipt.
6. Correctly distinguishes the teardown receipt's internal hash from the
   teardown file SHA-256 in the failure receipt.

This changes only evidence visibility. Product code, schema, data, insert
retry policy, workload, concurrency, duration, thresholds, crash/restart,
cleanup, teardown, and claims remain unchanged.

## Unchanged acceptance

- Frozen 43-execution verifier campaign GREEN.
- Synthetic counts: 500 tasks, 5,000 events, 1,000 receipts, 5,000 vectors.
- Concurrency stages: 10, 50, 100, 250.
- Four isolated workloads per stage: task-bound read mix, acknowledged writes,
  contended updates, and replay-idempotency writes.
- Zero query errors.
- Exact histogram/operation accounting.
- Exact acknowledged-write and counter deltas.
- Replay row exactly one.
- Per-workload p99 at most 5,000 ms and pMax at most 10,000 ms.
- Zero wrong-task vector links.
- Zero row loss across SIGKILL/restart after stage 50.
- Exact rollback and zero campaign-row residue.
- Process absent, ports closed, generated root absent.

## Authority boundary

GREEN authorizes one replacement local run only. It does not authorize paid
resources, Stage 500, PDH-3 GREEN, PDH-4, PDH-5, public actions, or cloud,
production, or external-user claims. Paid execution remains separately blocked
on exact hourly and total dollar ceilings, maximum paid lifetime, creation
attempt ceiling, and teardown authorization.
