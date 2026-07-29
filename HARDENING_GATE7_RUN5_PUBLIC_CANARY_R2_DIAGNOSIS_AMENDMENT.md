# Gate 7 Run 5 Public Canary R2 Diagnosis Amendment

- `STATUS`: `R2_REMAINS_BLOCKED; UNCHANGED_R3_RETRY_ALLOWED`
- `UTC_CREATED`: `2026-07-29T19:58:12Z`
- `PARENT_RECEIPT`: `HARDENING_GATE7_RUN5_PUBLIC_CANARY_R2_BLOCKED_RECEIPT.md`
- `PRODUCT_CHANGE`: `NONE`
- `HARNESS_CHANGE`: `NONE`
- `THRESHOLD_OR_RETRY_CHANGE`: `NONE`

## Corrected diagnosis

The R2 closeout correctly preserved the SQLSTATE `40001` failure and zero-residue
cleanup, but its proposed condition that the observed schema-change GC job must
leave the active job set before retry was too strict.

The direct job record is:

- type: `SCHEMA CHANGE GC`;
- description: GC for the dropped obsolete digest-constraint index;
- running status: `waiting for MVCC GC`;
- fraction complete: `0`.

CockroachDB's official `SHOW JOBS` documentation states that garbage-collection
jobs for dropped indexes execute after the GC TTL and cannot be canceled. A job
waiting for MVCC GC can therefore remain visible without representing an active
index backfill. The official transaction-retry documentation independently
classifies SQLSTATE `40001` as a client-retryable serialization conflict.

Sources:

- https://www.cockroachlabs.com/docs/stable/show-jobs
- https://www.cockroachlabs.com/docs/stable/transaction-retry-error-reference

## Next safe action

Run one fresh R3 public canary with the exact unchanged source, workload, retry
count, backoff, timeout, thresholds, and scale. Preserve R1 and R2 permanently.
If R3 fails semantically, leaks residue, or exposes a new repeated structural
failure, stop for a new bounded diagnosis rather than looping.
