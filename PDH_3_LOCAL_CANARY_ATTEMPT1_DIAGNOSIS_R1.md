# PDH-3 Local Canary Attempt 1 Diagnosis R1

- `STATUS`: `PRESERVED_BLOCKED_ATTEMPT`
- `CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PACKET_SHA256`: `9ca617c474476f6d4448aa8c896866543ffcce15a7452fd9ba6dd134e00b7844`
- `FAILURE_RECEIPT`:
  `evidence/pdh3-local-canary-r1/failure.json`
- `FAILURE_RECEIPT_FILE_SHA256`:
  `1cc88b11dee8352262d4660d06cc9144e47001557f171cb07f91f2d61a70fb34`
- `TEARDOWN_RECEIPT`:
  `evidence/pdh3-local-canary-r1/teardown.json`
- `TEARDOWN_RECEIPT_FILE_SHA256`:
  `9d93f77dec17660e442dc60d25c74c91b5aea8fff15ea619dbc66180116afdd1`
- `PROCESS_RESIDUE`: none
- `PORT_RESIDUE`: none
- `GENERATED_ROOT_RESIDUE`: none

## Bounded reproduction

A fresh local diagnostic applied the same two P9 migrations, created the three
calibration control tables, and inserted the same generated batches.

- tasks: 2/2 batches passed;
- events: 20/20 batches passed;
- receipts: 4/4 batches passed;
- vectors: batches 1–13 passed;
- vector batch 14 returned `SQLSTATE 40001` /
  `RETRY_SERIALIZABLE`;
- CockroachDB reported the transaction restart and rolled the batch back;
- the diagnostic database process stopped and its guarded generated root was
  removed.

## Root cause and repair boundary

The existing Gate 7 bulk controller already treats only `SQLSTATE 40001` as
retryable, with at most three retries and fixed 250 ms backoff. The new PDH-3
local controller used a single-attempt generic command helper and therefore
blocked on the first legitimate serialization retry.

The repair copies only the already-reviewed bounded retry behavior:

- retry only when the exact output contains `SQLSTATE: 40001`;
- at most three retries per generated insert batch;
- fixed 250 ms backoff;
- all other errors remain terminal;
- retry counts are recorded by stage and in aggregate;
- product code, schema, generated rows, thresholds, query workloads, and claim
  boundaries do not change.

Attempt 1 remains failed evidence and cannot be relabeled. A rerun requires a
new contract/controller hash and fresh independent preflight.
