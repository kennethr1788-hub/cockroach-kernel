# Hardening Gate 7 Run 5 — Immutable Blocked Closeout

- `STATUS`: `GATE7_RUN5_BLOCKED`
- `BLOCKER`: `TRACK2_COORDINATOR_BLOCKED_BEFORE_REQUEST_11_RESULT`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `ORCHESTRATION_HEAD_AT_FAILURE`: `d13da10d14778d3a2fa3d3a9197f813da1f107a8`
- `PREFLIGHT_PACKET_SHA256`: `2b1af0712b00b373ae62b53365abc7268399bffc56f7196ba3c71801859cbe02`
- `PLAN_SHA256`: `0f58b51c07d25d4643b98524e53f171d6e9c0d667c46e0718b07f40f27c1d7e7`
- `POD_ID`: `9jizvy2igfeipj`
- `POD_NAME`: `ck-g7r5-20260729-a01`
- `UTC_CLOSED`: `2026-07-29T23:52:40Z`

## Direct failure

The credential-free worker transferred request 11 to the host at
`2026-07-29T23:47:55Z`. The host coordinator then emitted
`COORDINATOR_BLOCKED` before creating `call-0011` evidence or returning a
result. Its stable error hash is
`a0fe27d29e544bb052dbc74dd324e9f0ab0cbfd9b7985c5fa3610ae782fafa85`.

There is no stage failure receipt for request 11. The preserved request and
current live configuration validate, and a later read-only AWS identity probe
passes, but those facts do not reveal the historical exception. The cause is
therefore `UNCLASSIFIED_PRE_CALL_COORDINATOR_FAILURE`. It is not attributed to
AWS, CockroachDB, RunPod, or operator action without direct evidence.

The coordinator guard observed the blocked terminal event, wrote the stop
marker, stopped and deleted the exact worker, and the separate lifecycle guard
recorded `TEARDOWN_GREEN`. Exact-ID lookup is absent and campaign inventory is
empty. One orphaned bridge process group survived the guard's first shutdown
attempt; it was terminated by exact PID and a subsequent campaign process scan
was empty.

## Valid preserved sub-results

- Track 1 aggregate: `84/84 PASS`, zero safety failures. Its aggregate and
  custody receipts are preserved. The sealed raw archive remained on the
  worker and was not retrieved before fail-closed deletion.
- Track 3: exact counts `2,000 / 20,000 / 4,000 / 20,000`, 200 vector queries,
  26 serialization retries, cleanup `107/107`, residue `0/0/0/0`, and GREEN
  terminal/result/cleanup receipts.
- Track 2 host boundary: ten complete Lambda/CockroachDB exchanges, 10 Lambda
  invocations, 90 CockroachDB operations, ten custody receipts, 11 request
  files, and ten result files.
- Lifecycle: exact Pod ID absent, campaign inventory `[]`, no campaign process,
  no Screen session, and lifecycle terminal `TEARDOWN_GREEN`.

These are valid sub-results only. They cannot be averaged into Gate 7 GREEN.

## Conjunctive blockers

1. Track 2 did not complete the required 12 exchanges.
2. No worker final receipt exists.
3. The remote Track 2 checkpoint, safety, summary, and foundation evidence was
   not retrieved before deletion.
4. The required post-final-exchange 900-second AWS identity margin probe did
   not occur.
5. The Track 1 raw archive was not retrieved and cannot be independently
   unsealed or rescored locally.
6. The frozen contract forbids a replacement worker after hidden execution and
   upload; no retry was attempted.

## Closeout state

- `RUNPOD_EXACT_ID`: `ABSENT`
- `RUNPOD_CAMPAIGN_INVENTORY`: `[]`
- `LIFECYCLE_TERMINAL`: `TEARDOWN_GREEN`
- `CAMPAIGN_PROCESSES`: `NONE`
- `SCREEN_SESSIONS`: `NONE`
- `REMOTE_EVIDENCE_RECOVERY`: `IMPOSSIBLE_AFTER_VERIFIED_DELETE`
- `GATE7`: `BLOCKED`
- `GATE8`: `FORBIDDEN`

Next safe action is a separately frozen replacement-campaign contract that
explicitly resolves whether a post-hidden infrastructure failure may be rerun,
preserves Run 5 as immutable failed evidence, and receives fresh same-hash GLM
5.2 plus AGY review before any worker creation. A general pre-hidden retry
authorization does not silently override the frozen post-hidden no-replacement
rule.
