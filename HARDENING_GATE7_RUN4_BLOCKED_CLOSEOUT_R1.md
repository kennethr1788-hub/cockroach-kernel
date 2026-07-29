# Gate 7 Run 4 Blocked Closeout R1

- `STATUS`: `HARDENING_7_RUN4_BLOCKED`
- `UTC_CLOSED`: `2026-07-29T07:39:59Z`
- `LAST_GREEN_GATE`: `GATE7_RUN4_PREFLIGHT_GREEN`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PREFLIGHT_PACKET_SHA256`: `e7f4d8723b49f422bf31e0f264d49432c5735054ed7d45fdb48666a78e55a7e4`
- `PREFLIGHT_JUDGES`: `GLM_5_2_GREEN; AGY_GEMINI_3_1_PRO_HIGH_GREEN; SAME_HASH; RECUSAL_CLEAR`
- `RUNPOD_ATTEMPTS`: `1`
- `POD_ID`: `rqmyhz8zsdprfu`
- `POD_STATE`: `DELETED; EXACT_ID_ABSENT; CAMPAIGN_INVENTORY_EMPTY`
- `FINAL_JUDGE_PACKET`: `NOT_REACHED`

## Terminal blocker

Run 4 crossed the hidden-seed and measured-execution boundary. It is immutable
historical evidence and cannot be relabeled, resumed, or tuned.

Track 3 stopped at its pre-database generation stage with the canonical stable
failure `VECTOR_DIGEST_COLLISION`. The controller wrote a hash-bound failure
receipt and `BLOCKED` terminal receipt before acquiring the database credential
or issuing any insert. A fresh read-only campaign-prefix count after closeout
returned `[0,0,0,0]`; its sanitized output SHA-256 is
`58d9fffe639ec31e34a1032bd727a05a5b7d6983881706d28a39c24cd03a31bb`.

The mechanism was reproduced without changing the frozen candidate. The first
duplicate context-vector digest was produced by task/segment pairs `(857,3)`
and `(1716,3)` under the Run 4 bulk namespace. The deterministic 64-dimensional
token-feature projection is many-to-one, while the bulk generator incorrectly
required all 20,000 projected vector digests to be unique. This is a source
contract defect, not a provider, CockroachDB, AWS, RunPod, or timing failure.

## Measured tracks

- `TRACK_1`: `GREEN; 84_OF_84_PASS; ZERO_BEHAVIOR_FAILURES; ZERO_SAFETY_FAILURES; ZERO_FALSE_PROMOTIONS; ZERO_RESIDUE; RETRIEVED; HASH_MATCHED; SEALED`
- `TRACK_1_AGGREGATE_SHA256`: `a12e064d3221db81e589713821b8aea0b13db2dbfa172c2df99f8d1b15c72f17`
- `TRACK_1_ARCHIVE_SHA256`: `a59042e805c4a0ea1376a7edb895ee63650ecce4341bafefca3c549851a6f933`
- `TRACK_1_CUSTODY_RECEIPT_SHA256`: `453b389496e50e654e7cedc8f9f2efddd79677b6ed6ee037822ccda49f8533d2`
- `TRACK_3`: `BLOCKED_BEFORE_DATABASE_ACCESS; VECTOR_DIGEST_COLLISION; ZERO_DATABASE_MUTATION; ZERO_RESIDUE`
- `TRACK_2_START_GATE`: `NOT_REACHED`
- `TRACK_2`: `NOT_STARTED; ZERO_LAMBDA_CALLS; ZERO_LIVE_COCKROACHDB_OPERATIONS`

The valid Track 1 result is preserved as a narrow sub-result. It cannot satisfy
the conjunctive Gate 7 acceptance law after Track 3 failed.

## Teardown and cost

- Worker created: `2026-07-29T07:15:26Z`
- Exact-ID stop/delete completed: `2026-07-29T07:39:22Z`
- Lifecycle guard teardown GREEN: `2026-07-29T07:39:59Z`
- Observed rate: `$0.06/hour`
- Conservative paid lifetime: `1,436 seconds`
- Mathematical maximum: `$0.023934`
- Provider itemization: `PENDING; NOT FABRICATED`
- RunPod exact-ID and campaign inventory: `[]`
- Screen inventory: empty
- Residual coordinator, bridge, guard, SSH, and paid processes: none
- CockroachDB synthetic Run 4 bulk residue: `[0,0,0,0]`

## Preserved evidence

See `HARDENING_GATE7_RUN4_BLOCKED_EVIDENCE_MANIFEST_R1.json`. Runtime artifacts
remain under `.hardening-runtime/gate7-r4/attempt-a01/`. The complete Track 1
archive is mode `0000` and remains sealed until an authorized post-closeout
verification step; its custody receipt records the byte count and SHA-256.

## Next safe action

A future Run 5 requires separate authorization. Before any new worker or hidden
seed, the candidate must replace the impossible global digest-uniqueness
assumption with an honest collision-safe storage/linkage contract, prove all
20,000 generated rows and adversarial collision handling locally, run a public
full-scale canary, freeze new source and packet hashes, and obtain fresh
same-hash GLM 5.2 and AGY GREEN. Run 4 evidence, seed, inputs, and results are
forbidden as tuning data or rerun inputs.
