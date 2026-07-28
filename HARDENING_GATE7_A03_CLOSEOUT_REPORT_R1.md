# Hardening Gate 7 A03 Closeout Report R1

- `GATE_RESULT`: `HARDENING_7_RUN2_BLOCKED`
- `PRIMARY_BLOCKER`: `BULK_RESULT_MISSING_AFTER_PARTIAL_INSERT`
- `SECONDARY_BLOCKER`: `PACKAGED_EVIDENCE_MANIFEST_HELPER_MISSING`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `POD_ID`: `xvxonfa5ck8wpq`
- `POD_NAME`: `ck-g7r2-20260728-a03`
- `POD_CREATED_UTC`: `2026-07-28T19:30:35.637Z`
- `POD_TEARDOWN_GREEN_UTC`: `2026-07-28T23:27:36Z`
- `PAID_LIFETIME_SECONDS`: `14220.363`
- `QUOTED_RATE_USD_PER_HOUR`: `0.06`
- `MATHEMATICAL_MAXIMUM_COST_USD`: `0.23700605`
- `POD_EXACT_ID_AFTER_DELETE`: `ABSENT`
- `ACTIVE_INVENTORY_AFTER_DELETE`: `[]`
- `CAMPAIGN_ACTIVE_AFTER_DELETE`: `[]`
- `LOCAL_GUARDED_PROCESSES_AFTER_CLOSEOUT`: `none`
- `UTC_CLOSED`: `2026-07-28T23:27:36Z`

## Passed measured evidence

### Hidden expanded benchmark

- exactly one hidden seed and one measured execution;
- 84/84 PASS;
- behavior failures: 0;
- safety failures: 0;
- false promotions: 0;
- mutation after refusal/invalid: 0;
- cleanup green: 84/84;
- residue: 0;
- remote aggregate SHA-256:
  `9428ae8cf6ce7857205dc718a3d2cd903463bf3f0331216b932c8e1cd74cfd8e`;
- local independent rescore aggregate SHA-256:
  `9428ae8cf6ce7857205dc718a3d2cd903463bf3f0331216b932c8e1cd74cfd8e`;
- remote and local aggregate file SHA-256:
  `2ce59b35a52c6d495fda05665c5bf6413678538d989682965ebe61c09f5128e4`.

### One-hour live worker

- status: GREEN;
- measured seconds: 3613.026;
- duration requirement met: true;
- checkpoints: 60/60;
- safety replays: 12/12;
- summaries: 12/12;
- Lambda calls: 12/12;
- CockroachDB operations: 108/108;
- failure: null;
- interrupted: false;
- worker final evidence hash:
  `2f88d04363d10e5d41ab2c9948f01ce64dcc6da2345d29980f950f20bcf18e92`;
- worker final file SHA-256:
  `cb474614743a7b164ead8ce0360a1b6647d3b964b253fdca9e6152c3a5e83eb4`.

### Host/provider controls

- project-local AWS login provider proved before start;
- 900-second read-only post-final-exchange identity probe: PASS;
- AWS margin postcheck receipt hash:
  `955fa82eb1c7dd32cb6520cd085007597a3567b15c3fb3564d37a18174101084`;
- coordinator terminal event: `COORDINATOR_GREEN`;
- bridge terminal event: `BRIDGE_GREEN`;
- coordinator guard terminal event: `COORDINATOR_GUARD_GREEN`;
- lifecycle guard terminal event: `TEARDOWN_GREEN`;
- lifecycle terminal event hash:
  `04fadb53df0c58390f26dc685d25d05f68ca70075be13b83aaa5a492910af8d4`.

### Evidence custody

- production manifest entries verified: 318/318;
- oracle manifest entries verified: 345/345;
- runner manifest entries verified: 255/255;
- production manifest file SHA-256:
  `5321de03ea884e7c17d03c19b7f18fb7808517ef008cc983ef5f9f552f5c4ad2`;
- oracle manifest file SHA-256:
  `e3ae455070020f4f703e7cdea2ff6d8df8a5cad22aa44fcd4e7133a15ffd3ca9`;
- runner manifest file SHA-256:
  `ea9cf82163da786b60a749223c1752684452964de4e14a1b08360d486a911d6f`;
- gitleaks findings: 0;
- private-path/credential exact-pattern hits: 0;
- detect-secrets findings: 162, all `Hex High Entropy String` instances in
  canonical hash receipts; no credential-type finding.

## Blocking findings

### 1. Bulk workload result missing after partial insert

The generated bulk controller exited without a result receipt. A direct
read-only count immediately after exit showed 2,000 tasks, 20,000 trajectory
events, 4,000 receipts, and 0 vectors. This proves the task, event, and receipt
insert stages completed and the vector stage did not. The controller process
and Screen session were absent. Its stdout/stderr had not been redirected to a
durable file, so the exact exception is unavailable and is not fabricated.

The frozen cleanup SQL was executed once solely for residue removal. The
post-cleanup counts were 0/0/0/0. The measured workload was not rerun or
resumed. This is a hard Gate 7 blocker because the contract requires the
separate 46,000-row bulk track and its canonical result receipt.

### 2. Packaged evidence helper missing

The frozen wiring required the transferred
`bundle/s3-soak/freeze_evidence_manifest.py` helper. It was absent from the
accepted worker payload. No post-start payload upload or patch was performed.
For custody only, standard Linux `find`, byte-sorted relative paths, and
`sha256sum` produced deterministic manifests, and every entry verified locally.
Those manifests are explicitly labeled as a fallback and are not represented
as output of the missing packaged helper. This packaging defect independently
prevents the prescribed closeout path from passing.

## Outcome

The hidden benchmark and one-hour live worker provide strong usable evidence,
but Gate 7 cannot be GREEN under the frozen all-or-nothing acceptance law.
Gate 8, S3-R2, release, and submission remain forbidden. A future repair would
require fresh operator authorization because hidden generation and measured
execution already occurred and the current prompt forbids a measured rerun.

