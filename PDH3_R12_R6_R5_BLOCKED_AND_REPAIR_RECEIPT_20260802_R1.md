# PDH-3 R12 R6 R5 Blocked and Repair Receipt

- `STATUS`: `R6_R5_BLOCKED_REPAIR_LOCALLY_VERIFIED`
- `UTC_REVIEWED`: `2026-08-02T13:02:00Z`
- `PACKET_SHA256`: `6dabda20b7317e93961977423b58130a4356304da1ff40b75d02fdd703701218`
- `POD_ID`: `r2iqulx4yfyoz8`
- `POD_TEARDOWN`: `GREEN; exact worker absent; campaign inventory empty`
- `MEASURED_24H_STARTED`: `false`
- `HOST_TERMINAL_SHA256`: `6dbe551863d8cb77effe66022026eab73eace49c7b84548e1a0cee51fb2f392c`
- `FINAL_EVIDENCE_SHA256`: `1c5dfdadb2ca52196d352a585f2b24aceec614402af714a6e9ba8ab490d3ad00`

## Verified failure chain

1. Linux extracted-bundle smoke passed with 35 Python files and 13 test files.
2. The remote worker launched with the exact 35-CPU affinity cap.
3. The 10,000-task PF2R scale produced exact counts, observed the expected pre-index full scans, selected the two prospective indexes, eliminated prohibited post-index full scans, preserved result equivalence, and wrote a GREEN scale receipt with SHA-256 `877dcb3448d92a5d937a9cd7e65cb83d827f2d8b7d30ad6b4d0999780b05996e`.
4. During the scale trial's `finally` teardown, `post-dogfood/pdh3_r12_plan_ab.py` called undefined symbol `file_sha256` while hashing the copied CockroachDB log.
5. Python raised `NameError`; the observer recorded child exit `1`, no network-policy violations, and a fail-closed `PROCESS_TREE_OBSERVATION_BLOCKED` verdict.
6. Because the remote runner never wrote `output/result.json`, the host reported `TERMINAL_RECEIPT_RETRIEVAL_FAILED`, retrieved best-effort evidence, deleted the worker, and wrote a BLOCKED terminal receipt.

The failure is an evidence/teardown helper defect after a successful 10,000-task plan trial. It is not evidence that the full R6 preflight passed, and R5 remains permanently BLOCKED.

## Minimal repair

- Added a streaming `file_sha256(path)` helper.
- Isolated database-log preservation in `preserve_database_log(...)`.
- Added a regression test that copies and hashes a synthetic CockroachDB log through that exact helper.
- No product behavior, workload scale, query matrix, thresholds, index decision, lifecycle boundary, or 24-hour claim changed.

## Local repair evidence

- Full 13-file extracted-bundle test surface: `141` tests, all PASS.
- Deterministic candidate archives A and B: byte-identical SHA-256 `52619301a9aa0b88e5c2e3e52d668e6485ae105eb1c0f86405d681a5945be7a6`.
- Deterministic bundle receipt SHA-256: `9fcf6d0a2964c67c8eeb4383eab0b1d2052393a6c8cb2c5a25afc1f0d03f9824`.
- Extracted-bundle smoke: GREEN; 35 Python files; 13 test files; zero failed checks; internal smoke SHA-256 `e9ff978ed566f07f29b6c4f9fa582972c595af1367f69dd485be8d7f8d9ddee9`; receipt-file SHA-256 `e975b62a60b061fa7af9cde871e7388c54399a444a1a4c38b7416c7e0b555689`.
- Disposable local 10,000-task attempt reached the repaired teardown path but CockroachDB correctly refused the index backfill because the host had only about 1.8 GiB free, below its 5% store-reserve requirement.
- That infrastructure-invalid local attempt still proved the repaired teardown: process stopped, generated root removed, copied log hash matched, teardown GREEN.
- Local teardown record SHA-256: `6c279df6fdce46732de1b605747ac584b3955cd51d2efa17ce4f405bcf794fea`.
- Copied database log SHA-256: `d6f4495384b055831f7e930ec47e2257446b1a38c12ffa0891f09fa2b3877699`.
- No CockroachDB process or listener remained.

## Remaining gate

The repair is not remote R6 evidence. Before another paid worker, freeze a new packet over the repaired commit and deterministic archive, obtain exact same-hash independent GLM 5.2 GREEN, and obtain replacement-lifecycle authority that prospectively supersedes R5's post-upload no-replacement marker. Do not start the 24-hour campaign.
