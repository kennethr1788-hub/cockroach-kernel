# PDH-3 Replacement Campaign Relaunch Readiness Checklist R8

This is a fail-closed execution checklist for the replacement 24-hour campaign.
`GREEN` requires direct local evidence plus identical-packet independent review.
Remote premeasurement items remain `REMOTE_GATE` until one verified worker exists;
they are not inferred from reduced tests.

## Candidate and provenance

- [x] `R8-01` Fresh packet and archive bind the exact repaired bytes; no R7
  source hash, expired launch timestamp, or stale judge result is reused.
- [x] `R8-02` Attempts 01 through 07 and the Attempt 07 retrieved failure archive
  are hash-bound as preserved failed evidence, with no secret-bearing raw payload
  copied into the judge packet.
- [x] `R8-03` Production arguments bind the exact 24-hour contract and reject a
  bounded local `store_size` or any reduced-scale override.

## Setup and target-scale premeasurement gates

- [x] `R8-04` Seed retry is limited to timeouts and SQLSTATE `40001`; every
  uncertain timeout reconciles to `ZERO` or `EXACT`, while `MISMATCH` blocks.
- [x] `R8-05` Explicit primary-key conflict targets cannot conceal mismatched
  rows, and full-cardinality mismatch queries return zero.
- [x] `R8-06` Vector-index deferral, recreation, backfill completion, metadata,
  and forced-index queryability are all directly proved.
- [x] `R8-07` One setup deadline covers seed, reconciliation, index recreation,
  and setup receipt finalization, with an enforced tail reserve.
- [ ] `R8-08` **REMOTE_GATE** — the real RunPod shape completes 500,000 tasks, 5,000,000 events,
  1,000,000 receipts, and 250,000 vectors within 5,400 seconds with margin.
- [x] `R8-09` Generated read queries are six-digit IDs and directly hit nonzero
  seeded vector and receipt rows.
- [ ] `R8-10` **REMOTE_GATE** — before the official clock, three 300-second epochs run at
  concurrency 500 with three rotating node faults; trace projection remains at
  or below 80 percent of the 2 GiB cap; all control tables are then reset and
  their exact clean state is proved.

## Measured execution integrity

- [x] `R8-11` Every epoch has one shared monotonic 300-second deadline; no
  individual subprocess or SQL operation can consume the entire remaining
  epoch, and the checkpoint snapshot is taken at the boundary within tolerance.
- [x] `R8-12` The exact schedule is 288 checkpoints, 232 verifier batches,
  9,976 verifier executions, and exactly 24 rotating node-kill cycles.
- [x] `R8-13` Every fault proves the old PID was live, exited from `SIGKILL`, the
  replacement PID differs, all three nodes become SQL-ready, and static plus
  cumulative acknowledged-write/counter/replay state is unchanged or advances
  exactly as declared.
- [x] `R8-14` Raw querybench logs/histograms and all 9,976 unique verifier
  receipts/manifests remain in the evidence archive and reconstruct mechanically.
- [x] `R8-15` Database, evidence, disk, RSS, file-descriptor, process, node-live,
  and trace-growth thresholds are measured at each checkpoint.
- [x] `R8-16` The syscall observer scans one PID-prefixed process-tree stream in
  O(new data), emits atomic progress, fails closed on observer/cap errors, and
  records no external or unparseable destination.

## Terminal-state and lifecycle integrity

- [x] `R8-17` Cluster partial-start failure tears down every started node and can
  never produce vacuous teardown success.
- [x] `R8-18` `result.json` and `MEASURED_CAMPAIGN_GREEN` are impossible before
  database drop, node stop, port closure, generated-root removal, and final
  evidence validation; result and failure are mutually exclusive.
- [x] `R8-19` The tracked supervisor distinguishes GREEN pending final review,
  blocked completion, absent result, partial archive, transport failure, and
  unproved teardown; retrieval is atomic and deletion remains in `finally`.
- [x] `R8-20` The exact-ID guard uses bounded provider calls, retries transient
  stop/delete failures through its deadline, and requires exact 404 plus empty
  campaign inventory before teardown GREEN.

## Proof and authorization boundary

- [x] `R8-21` Unit, fake-clock, extracted-bundle, real local CockroachDB smoke,
  residue, secret, compile, and diff checks are all GREEN without being mislabeled
  as target-scale evidence.
- [x] `R8-22` GLM and AGY independently return GREEN over one identical sanitized
  packet hash; neither judge authors or modifies the candidate.
- [x] `R8-23` **PRECREATE_RECHECK** — current RunPod inventory, L40S offer, image, rate, aggregate-spend
  headroom, runpodctl hash, fresh stop/terminate deadlines, and zero extant paid
  resources are reverified immediately before creation.

## Relaunch rule

The worker may be created only after every local item is checked and both
independent preflight verdicts are GREEN. `R8-08` and `R8-10` are worker-local
premeasurement gates: if either fails, the official 24-hour measured clock does
not begin, all evidence is retrieved, and the worker is deleted. A reduced local
test cannot check either item.

## Frozen evidence ledger

- Final identical judge packet: `PDH_3_SCALE_RUNPOD_PREFLIGHT_PACKET_R8.md` —
  SHA-256 `3615d8606e5678946634f6166c5bdd41e34fbdb21266d39f3396e2c3f11b6d95`,
  204,069 bytes.
- Canonical bindings: `PDH_3_SCALE_RUNPOD_PREFLIGHT_BINDINGS_R8.json` —
  internal SHA-256 `403b24b6e7080ad56e5ef2f57f51074aebd0b2d4ccffad6a2878bfa9e01388c9`;
  source-set SHA-256 `0dfa7de63297d27640ab8308c5fd4067e21985c6724b23b822c470894290ce6f`.
- Transfer archive: `.pdh3-runtime/r8-preflight-final/pdh3-scale-bundle-r8.tgz` —
  SHA-256 `41f35db9e23e008670295755eb5e40d11dc407b0820bb29c88d804e2f3505ecc`.
- Exact-source Python 3.12 matrix:
  `.pdh3-runtime/r8-preflight-final/local-evidence/python312-tests-r5/matrix-receipt.json` —
  8 suites, 125 tests, GREEN, receipt SHA-256
  `5ae64dd2d208587674918510acbff6cef3b112628b5d329b3cb7d68a23e4b4b0`.
- Local evidence manifest:
  `.pdh3-runtime/r8-preflight-final/local-test-manifest-r8-r6.json` — GREEN,
  manifest SHA-256 `0bab4634e59ed7ce2bff82d19de117e1a116821ea6045521835df56d27e16e6e`.
- Isolated smoke contract: `PDH_3_R8_LOCAL_SMOKE_PACKET_R6.md` — SHA-256
  `f74b01ee9a6d855b48377cbda6a92fdefb5754c6f5063aa4f0dcd47748724a33`;
  observed GREEN result and teardown are bound by the local evidence manifest.
- Fresh provider evidence:
  `.pdh3-runtime/r8-preflight-final/provider-r5/runpod-active-receipt-r8.json`
  and `runpod-gpu-pricing-receipt-r8.json`, observed `2026-07-31T19:11:20Z`.
- GLM receipt:
  `.pdh3-runtime/r8-preflight-final/judges-r8/GLM_JUDGE_RECEIPT.json` — GREEN,
  receipt SHA-256 `25570a685a3a275b30c816a18e91e7f8fdd19e8089c2a322ba47d030fbb1ea8f`.
- AGY receipt:
  `.pdh3-runtime/r8-preflight-final/judges-r8/AGY_JUDGE_RECEIPT.json` — GREEN,
  receipt SHA-256 `566dcab8f1f845bc28100dae7c9c81d7627041cc67fb654a5eef860f7d34bb9f`.
- R8-23 is checked only as a proven preflight mechanism and current empty-state
  observation. The same inventory, offer, rate, tool hash, and lifecycle checks
  must run again immediately before paid worker creation; a stale observation
  cannot authorize creation.
