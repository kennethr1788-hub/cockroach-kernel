# Gate 7 Run 4 Repair Receipt R1

- `STATUS`: `RUN4_REPAIR_LOCALLY_GREEN`
- `UTC_CREATED`: `2026-07-29T05:03:04Z`
- `AUTHORIZATION`: Kenneth stated exactly: `I authorize a rerun`
- `RUN3_BLOCKED_CLOSEOUT_COMMIT`: `da1901ad352f6fc46ce7fe06b1d240c74f29bbe7`
- `RUN3_STATUS`: `IMMUTABLE_BLOCKED_HISTORY`
- `NEXT_GATE`: `FULL_46000_ROW_LIVE_CLEANUP_CANARY`
- `RUNPOD_CREATION`: `FORBIDDEN_UNTIL_LIVE_CANARY_AND_SAME_HASH_GLM_AGY_PREFLIGHT_ARE_GREEN`
- `HIDDEN_SEED`: `ABSENT; RUN3_SEED_AND_INPUTS_FORBIDDEN`

## Evidenced defect being repaired

Run 3 proved exact bulk insert counts `[2000,20000,4000,20000]`, but its
single cleanup transaction exceeded 300 seconds while Track 2 also performed
database-heavy post-trial cleanup. Track 2 then blocked in `POSTTRIAL_CLEANUP`.
No server lock graph was captured; the narrower database lock mechanism is not
claimed.

## Repair

1. `live_bulk_controller.py` replaces the monolithic cleanup with 35
   deterministic, hash-bound batches. Every batch has its own durable
   start/pass/fail/retry journal records and a 120-second bound.
2. Preclean is no longer a mutating cleanup. It is a fail-closed assertion that
   all four campaign-scoped record counts begin at zero.
3. Track 1 evidence must be archived, hashed, transferred, and sealed before
   Track 3 or Track 2 can consume later campaign time.
4. Track 3 must emit a canonical GREEN terminal, PASS cleanup receipt, exact
   counts, and zero residue before the Track 2 start gate can exist.
5. Track 2 cannot overlap Track 3 database work. Its start marker binds the
   Track 1 aggregate/custody and Track 3 result/cleanup/terminal hashes.

## Local proof

- Gate 7 repair suite: `17/17 PASS` in `28.718s`.
- Entire Gate 7 suite: `21/21 PASS` in `35.411s`.
- Deterministic cleanup batches: `35`.
- Mocked full-count semantics: `[2000,20000,4000,20000]`.
- Custody seal/unseal: hash-bound and mode-checked.
- Negative Track 2 gate vectors: blocked Track 3 terminal, nonzero residue,
  and unsealed Track 1 custody all fail closed.

## Source hashes

- `hardening-gate7/live_bulk_controller.py`: `b67669b7de12b736b1511326737b27d842b2d5e695b82477dc6fb6464ba8318a`
- `hardening-gate7/run4_evidence_custody.py`: `025e5c89eba77597e1831de54e9c6ca967a9b09de9a9f711ac369918673cd265`
- `hardening-gate7/run4_track_gate.py`: `584a49e6803611d4b22950ffbe5a64e837965d53b52e430b1fd7e37fb6d6a2e9`
- `hardening-gate7/test_expanded_gate7.py`: `0f132f75905b12e764f40dc70c228c2a38b74484e7b71c7f5935aa7a9249f256`

## Remaining proof

This receipt is source-level and simulated-runtime evidence, not a Gate 7
verdict. Before any RunPod worker exists, a fresh public/non-hidden full
46,000-row CockroachDB canary must directly pass the new 35-batch cleanup and
prove `[0,0,0,0]` residue. A new frozen Run 4 packet must then receive same-hash
GLM 5.2 and AGY GREEN.
