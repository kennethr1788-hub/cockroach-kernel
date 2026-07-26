# P8 Same-Hash Judge Packet R1

## Decision requested

Decide whether the evidence below closes `CK_P8_GOLDEN_GREEN` under the current
R1 plan and correction layer. Review only; do not author code, propose patches,
use tools, browse, deploy, or direct the builder. Return `GREEN` only if every
proposal has an evidence-backed promotion or rejection, replay is deterministic
and frozen-set-bound, policy mutation is atomic and explicit, rollback is exact,
and the non-claims are honest.

## Identity

- Parent gate: `CK_S2_RECOVERY_SOAK_GREEN`
- Implementation commit: `a17f60303ebbc1446871f9cac11c7b82f89ffd83`
- Plan SHA-256:
  `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- Correction-layer SHA-256:
  `de531da8eaa9a39a2b39ee85206a6fdb348279fe042d55f67b22d3f6b88e11a7`
- P8 contract SHA-256:
  `efaeeb1d391253c19ee9125fc465d76e88ffba709389a258ed6640a36f399fb4`
- Scope: local, synthetic, standard-library authority code plus an already
  checksum-verified local CockroachDB v26.2.3 binary.

## Frozen contract

P8 records successful and failed synthetic incidents, accepts bounded
reflection proposals as untrusted input, replays every proposal against one
frozen incident set, and produces exactly one evidence-backed outcome for each
proposal: `PROMOTE` or `REJECT`. Reflection never writes policy directly and no
artifact claims foundation-model retraining.

Policy, incident, and proposal records are strict canonical UTF-8 JSON with
fixed schemas, 64 KiB caps, stable IDs, and SHA-256 binding. A proposal binds
one exact base-policy hash and one complete candidate policy. Stale bases,
unknown fields, unsupported schemas, invalid thresholds, safety weakening, and
no-op proposals reject before replay.

The incident set contains both expected successes and expected failures and is
frozen by the hash of its canonically sorted member hashes. Replay uses no
model, clock, randomness, network, or free-text rationale. The candidate policy
must reproduce the expected verdict and stable reason for every incident while
preserving fixed safety invariants: ordinary quorum at least 3, critical quorum
at least 4 and no lower than ordinary, and correlation limit between 2 and 4.

A promoted proposal produces a golden validation pair binding proposal, base
policy, candidate policy, incident set, replay result, and promotion receipt.
A rejected proposal produces a reason receipt with the same available exact
bindings. Promotion plus its receipt commits in one SERIALIZABLE transaction.
An invalid receipt aborts all candidate writes. Duplicate completed promotion
is idempotent. Explicit rollback restores only the exact previous policy bound
by the promotion receipt and records a rollback receipt in one transaction.

Kill line: silent mutation, unreceipted proposal, regression acceptance,
stale-base promotion, safety weakening, nondeterminism, partial promotion,
rollback mismatch, private-data egress, residue, or judge failure blocks P8.

## Implementation and hashes

`p8-golden/golden.py`
`e7cefb237a9238d92b6d0afb0ec9b1a69fa458570a40441d049dc17f760d75b6`

- strict validators for policy, incident, incident set, and proposal;
- pure `evaluate` authority function with fixed failure ordering;
- `replay_proposal` returns a promotion or rejection receipt for every
  serializable proposal input and binds replay to sorted incident IDs/hashes;
- `build_rollback_receipt` requires exact current and prior policy hashes.

`p8-golden/migrations/001_golden.sql`
`363117ff656ed08105e629ab9a2794a665270d909f85f111a32183b0c898026c`

- policy states restricted to `GOLDEN|SUPERSEDED`;
- proposal outcomes restricted to `PROMOTE|REJECT`;
- unique policy/proposal/promotion/receipt identities;
- 32-byte hash constraints;
- explicit incident-set, promotion, and rollback tables with foreign keys.

`p8-golden/run_integration.py`
`44fd21652694ba067cc1727d64ddfd686b3c63141e92dc44eb56a01e5a345f58`

- starts two independent temporary single-node CockroachDB roots with HOME
  redirected to an empty trial-local directory;
- applies the migration, persists the frozen incident set and every proposal;
- injects an invalid one-byte receipt hash inside the promotion transaction;
- proves the failed transaction leaves no candidate policy, safe proposal, or
  promotion row;
- commits the valid promotion, repeats it idempotently, explicitly rolls back,
  repeats rollback to force a primary-key conflict, and proves the conflict
  leaves the prior policy golden;
- drops the database, terminates the child process, and removes the root.

Test and fixture hashes are recorded in `P8_EVIDENCE_MANIFEST.md`. Principal
test hash:
`14419628d991da71ce04ce475c42454da169a133f3c676f52181b521c3091f19`.

## Frozen incidents and proposal outcomes

Incident set SHA-256:
`dd1d02820c5daaaa58f46a5507fd09aae12c5eb5deebac2601679d47ce751512`.

The set has nine incidents: two expected promotions (ordinary and critical)
and seven expected refusals (ordinary quorum, critical quorum, correlated
outputs, policy veto, tamper, unsafe input, and consumed-warrant replay).

Eight proposals were evaluated:

1. safe correlation tightening: `PROMOTE / ALL_INCIDENTS_MATCH`;
2. ordinary quorum weakening: `REJECT / SAFETY_INVARIANT_FAILED`;
3. critical quorum weakening: `REJECT / SAFETY_INVARIANT_FAILED`;
4. correlation limit 5: `REJECT / SAFETY_INVARIANT_FAILED`;
5. correlation limit 1: `REJECT / SAFETY_INVARIANT_FAILED`;
6. stale base hash: `REJECT / STALE_BASE_POLICY`;
7. no policy change: `REJECT / NO_POLICY_CHANGE`;
8. ordinary quorum tightening that breaks a frozen success:
   `REJECT / REGRESSION_DETECTED` with replay evidence.

Each fixture proposal is tested to have exactly one outcome receipt, one
64-character receipt hash, the exact proposal hash, and the exact incident-set
hash. Malformed and unsupported-schema inputs also receive rejection receipts.

## Mechanical evidence

- P8 unit tests: 15/15 PASS.
- P3-P8 unit tests: 116/116 PASS.
- Five-repeat deterministic replay: PASS.
- Incident-order independence: PASS.
- Proposal-order independence: PASS.
- Two fresh-root CockroachDB trials: 2/2 PASS, identical semantics.

Identical per-trial state:

```text
after interrupted promotion: 0 candidate policies / 0 safe proposals / 0 promotions
after promotion and duplicate: 1 golden / 8 proposals / 1 promotion
after explicit rollback: policy-p8-v1 golden
after duplicate rollback conflict: policy-p8-v1 still golden
final counts: 2 policies / 1 incident set / 8 proposals / 1 promotion / 1 rollback
```

## Contributor provenance

- Kimi K3/OAuth returned a bounded stale-base fixture; the useful vector was
  already present. Its invalid integer policy-version bytes were rejected.
  Contained/headless write attempts produced no edits and no authority result.
- Vibe returned bounded quorum, correlation, and hash-drift vectors. The missing
  correlation-underflow vector was accepted and added; other vectors already
  existed.
- Devstral `mistral-medium-3-5` returned boundary findings. Duplicate rollback
  replay was accepted and added. Partial-state/idempotency/linkage findings were
  already proven. Treating rejected proposals as teardown orphans was rejected
  because the contract requires preserving rejected alternatives.
- Codex owns authority semantics, integration, reconciliation, and evidence.
- None of these builder lanes may judge this packet.

## Safety, residue, and non-claims

- gitleaks: no leaks.
- detect-secrets findings: synthetic SHA-256 values only; no accepted secret.
- Private-path scan: only the deliberate fake-HOME assignment in the local
  integration runner.
- P8 generated roots, P8 contributor worktrees, and branches: absent.
- No AWS, RunPod, public action, HOME/live-memory mutation, Qdrant, StateV2,
  launchd, client/private data, credential, or P9 surface was used.
- No foundation-model training, autonomous policy learning, or live production
  mutation is claimed. “Reflection” means untrusted bounded proposal data;
  deterministic local replay remains the sole authority.

## Known limitations

- This is synthetic local evidence, not the P9 live AWS/CockroachDB integration
  or a production deployment.
- The database constrains hash lengths and relationships; semantic SHA-256
  recomputation happens in the deterministic application layer and is proven by
  the transaction harness, not a SQL digest constraint.
- Rejected proposals are deliberately retained as audit evidence.
- Exact timestamps are evidence metadata and are not inputs to verdicts.

## Required judge response

Return the lane name, the exact packet SHA-256 supplied with the invocation,
one verdict (`GREEN`, `REVISE`, `BLOCKED`, or `INSUFFICIENT_EVIDENCE`), blockers,
non-blocking risks, evidence gaps, recusal status, and required reruns. Do not
write implementation instructions or code.
