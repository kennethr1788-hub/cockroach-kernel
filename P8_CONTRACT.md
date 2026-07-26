# P8 Frozen Contract

- `PHASE`: `P8`
- `PARENT_GATE`: `CK_S2_RECOVERY_SOAK_GREEN`
- `START_COMMIT`: `5ccd6c92feae8fbb94754bc7a1ec078459ede70e`
- `TARGET_GATE`: `CK_P8_GOLDEN_GREEN`
- `STATUS`: `FROZEN_BEFORE_IMPLEMENTATION`
- `SCOPE`: `LOCAL_SYNTHETIC_ONLY`

P8 records successful and failed synthetic incidents, accepts bounded
reflection proposals as untrusted input, replays every proposal against one
frozen incident set, and produces exactly one evidence-backed outcome for each
proposal: `PROMOTE` or `REJECT`. Reflection never writes policy directly and
no artifact may claim foundation-model retraining.

## Deterministic authority

- Policy is strict canonical UTF-8 JSON with a fixed schema and SHA-256 binding.
- A proposal identifies one exact base-policy hash and a complete candidate
  policy. Stale bases, unknown fields, unsupported versions, invalid thresholds,
  and no-op proposals reject before replay.
- The incident set contains both successful and failed outcomes and is frozen by
  its canonical set hash. Each incident binds its input, expected verdict, and
  expected stable reason code.
- Replay uses no model, clock, randomness, network, or free-text rationale. A
  proposal promotes only when every frozen incident reproduces its expected
  verdict and reason and the safety invariants remain true.
- Every promoted proposal produces a golden validation pair binding the proposal,
  base policy, candidate policy, incident set, replay result, and promotion
  receipt. Every rejected proposal produces a reason receipt with the same exact
  bindings. No proposal may lack an outcome receipt.
- Promotion and its receipt commit atomically in a retry-safe CockroachDB
  serializable transaction. Duplicate promotion is idempotent. A failed receipt
  write rolls the policy change back.
- Rollback is explicit and hash-bound: it restores only the exact previous
  golden policy named by the promotion receipt and records a rollback receipt.

## Required vectors

- one evidence-backed promoted proposal;
- rejected quorum weakening, critical-threshold weakening, stale-base, no-op,
  malformed, unsupported-schema, and unsafe/correlated-vote proposals;
- explicit successful and failed incidents in the frozen set;
- five-repeat deterministic replay and outcome semantics;
- proposal-order independence;
- atomic promotion/receipt rollback on interruption;
- duplicate promotion idempotency;
- explicit rollback to the previous golden policy;
- two fresh-root CockroachDB integration trials with identical results and clean
  teardown;
- canonical record caps, unknown-field rejection, hash linkage, secret/private
  path scan, and zero generated residue.

## Ownership

- Kimi scope: non-authoritative proposal/incident fixture scaffolding only.
- Vibe scope: adversarial replay, malformed, stale, unsafe, interruption, and
  determinism vectors only.
- Devstral scope: disposable CockroachDB schema, transaction, rollback, teardown,
  and clean-root boundary only.
- Codex owns policy semantics, safety invariants, promotion/rejection authority,
  integration, reconciliation, evidence, and the frozen judge packet.

External builder output, if used, is untrusted and cannot close the gate. An
independent non-authoring judge reviews the exact final packet hash only after
mechanical evidence passes.

## Kill line

Any silent policy mutation, unreceipted proposal, regression acceptance,
stale-base promotion, safety weakening, nondeterminism, non-atomic promotion,
rollback mismatch, private-data egress, residue, or independent-judge failure
leaves `CK_P8_BLOCKED`.

P8 does not authorize AWS, RunPod, HOME/live-memory mutation, public actions,
P9, release, or submission.
