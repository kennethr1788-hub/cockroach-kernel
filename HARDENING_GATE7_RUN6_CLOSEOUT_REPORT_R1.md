# Hardening Gate 7 Run 6 — Closeout Report R1

## Status before independent review

`RUN6_COMPLETE_EVIDENCE_RETRIEVED_TEARDOWN_GREEN`

This is not builder self-approval. Gate 7 remains pending until GLM 5.2 and AGY
independently return GREEN over one exact final packet hash.

## Results

- Track 1: 84/84 hidden executions PASS; behavior failures 0; safety failures
  0; false promotions 0; mutations after refusal/invalid 0; correct stable
  reasons 84/84; cleanup 84/84; residue 0; tuning events 0. After teardown,
  the sealed archive unsealed with its original SHA-256 and an independent local
  rescore reproduced aggregate SHA-256
  `e0b313d32cc2c9f552f17fe9fbd43d539eb5c84fd3c8fddc7972f5ecafd62694`.
- Track 3: exact rows 2,000 tasks / 20,000 events / 4,000 receipts / 20,000
  vectors; 200 task-bound vector queries; concurrency 4 observed; 24
  serialization retries handled; insert total 234,977 ms; query p99 1,086 ms;
  cleanup 107/107; residue 0/0/0/0; no credential bytes.
- Track 2: 3,613.497 measured seconds; 60 checkpoints; 12 safety replays; 12
  hourly summaries; 12 completed requests; 12 Lambda invocations; 108
  CockroachDB operations; status GREEN; interruption false; failure null;
  runtime residue empty.
- AWS post-exchange margin: PASS after 901 seconds against a 900-second
  requirement; no credential bytes recorded.
- Control plane: `BRIDGE_GREEN`, `COORDINATOR_GREEN`,
  `COORDINATOR_GUARD_GREEN`, and `TEARDOWN_GREEN`; all four hash chains validate.
- Provider closeout: exact Pod ID absent; campaign inventory `[]`; no Screen
  session or campaign process remains.
- Final local regression: Gate 7 24/24, P9 cloud contract 8/8, S3 protocol and
  hardening 19/19.

## Honest limits

The hidden campaign is synthetic, uses the same generator and product
implementation, and is not public-user or statistically independent evidence.
The live workload is bounded and single-region. The product reconstructs only
captured, declared representations and cannot recover arbitrary uncaptured
bytes from nothing. Observed active-time cost is mathematical evidence, not an
exact provider billing receipt.

Runs 3, 4, and 5 remain preserved as failed evidence and are not relabeled.
Run 6 used a new hidden seed and did not tune against or reuse revealed Run 5
inputs.

