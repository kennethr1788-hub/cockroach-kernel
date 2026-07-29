# Gate 7 Run 5 Collision-Safe Repair and Execution Contract R1

## Objective

Repair the invalid global uniqueness assumption for deterministic vector content
digests, prove exact row identity and event linkage remain unique, then execute one
new hidden Gate 7 campaign. If Gate 7 becomes independently GREEN, build and
independently review Gate 8. Stop before Gate 9.

## Preserved historical evidence

Run 4 remains immutable. Its Track 1 evidence is 84/84 GREEN and sealed. Its
Track 3 failure `VECTOR_DIGEST_COLLISION` remains a failure receipt. Track 2 was
never started and its worker was deleted. Run 5 does not reuse Run 4 hidden
inputs, seed, worker, or verdict.

## Repair contract

`vector_digest` is a SHA-256 content digest of the exact canonical vector bytes.
It is intentionally non-unique because the deterministic 64-dimensional
projection is many-to-one. Security and custody bind exact database rows by:

1. unique `vector_id`;
2. unique `(task_id, event_id, namespace)` linkage;
3. exact content digest recorded for every row;
4. manifest accounting for unique digests, total legitimate digest collisions,
   maximum digest multiplicity, unique row IDs, and unique linkages.

The controller must fail on a duplicate row ID or duplicate linkage. It must not
fail merely because two distinct rows have identical canonical content. The live
migration removes only the global digest uniqueness constraint and retains a
non-unique lookup index.

## Required local and public proof before worker creation

- full Gate 7 and P9 contract suites GREEN;
- old-schema to new-schema Cockroach migration proof using two distinct linked
  rows with the same digest;
- fresh 20,000-vector generation with exact identity/linkage accounting;
- full non-hidden live CockroachDB canary after applying migration 003;
- exact 46,000 rows, 200 vector queries, 107 cleanup batches, zero residue;
- deterministic transfer archive, extracted-bundle canaries, secret/private-path
  scans, lifecycle guard, and empty RunPod inventory;
- same-hash GLM 5.2 and AGY preflight GREEN.

## Measured RunPod campaign

Use `HARDENING_GATE7_RUN5_SCHEDULE_R1.json` and the existing expanded thresholds.
Only one worker may exist at a time. Up to eight sequential pre-upload creation
attempts are permitted inside one 120-minute window. Every failed worker must be
deleted and its exact absence plus empty campaign inventory proved before retry.
Three identical failures require bounded diagnosis and a new same-hash preflight.
No replacement is permitted after upload, hidden seed creation, or measured work.

The successful worker runs Track 1, seals its evidence, runs Track 3, passes the
Track 2 start gate, runs Track 2 for at least 3,600 measured seconds, then closes
out. It uses synthetic/sanitized payloads only, no persistent/network volume,
no GPU, no HOME/private/client/production data, and no credential transfer.

## Gate authority

Run 5 is not Gate 7 GREEN until retrieved evidence and teardown are hash-bound
and the exact final packet receives independent same-hash GLM 5.2 and AGY GREEN.
Gate 8 cannot start earlier. Gate 8 is limited to evidence scorecard, canonical
claim-to-evidence manifest, private raw archive, sanitized public subset, and an
architecture diagram reflecting measured boundaries. Gate 8 requires zero
missing artifacts, hash mismatches, unsupported claims, contradictory metrics,
credential/private-path leaks, or replay/live ambiguity and an independent
same-hash review. Gate 9 is out of scope.
