# P6 Evidence Manifest

- `PHASE`: `P6`
- `TARGET_GATE`: `CK_P6_QUORUM_GREEN`
- `PARENT_GATE`: `CK_P5_LANES_GREEN`
- `UNIT_TESTS`: `41/41 PASS`
- `FRESH_COCKROACH_TRIALS`: `2/2 PASS`
- `TRIAL_COUNTS`: `2 handoffs / 5 votes / 1 transition / 1 receipt`
- `INTERRUPTED_COMMIT`: rejected; `0 transitions / 0 receipts`
- `ROLLBACK`: passed; `0 transitions`
- `TRANSACTION_RETRY`: passed; exactly one transition and one receipt
- `LINKAGE`: decision and receipt hashes present in the joined database rows
- `DETERMINISM`: five-repeat decision semantics and byte-identical fixture
  regeneration passed
- `RESIDUE`: no `p6-db-*` root, symlink, database process, or socket remained
- `GITLEAKS`: no leaks found
- `DETECT_SECRETS`: empty result set
- `JUDGES`: GLM GREEN and Claude GREEN on R3 packet SHA-256
  `7c887c71aae6c7dffebd95a1fa793261d6ddf7567c3a30e90b46fe1cceae2c10`

## Primary evidence

- `P6_CONTRACT.md`
- `P6_BUILDER_ASSIGNMENTS.md`
- `P6_PERSONA_SOURCE_RECEIPT.md`
- `P6_BUILDER_CONTRIBUTIONS.md`
- `p6-quorum/state_machine.py`
- `p6-quorum/migrations/001_quorum.sql`
- `p6-quorum/make_fixtures.py`
- `p6-quorum/test_state_machine.py`
- `p6-quorum/run_integration.py`
- `p6-quorum/fixtures/`

## Exact commands

```text
(cd p6-quorum && PYTHONWARNINGS=error python3 -m unittest -q)
python3 p6-quorum/run_integration.py
gitleaks detect --no-git --source p6-quorum --no-banner --redact --exit-code 1
detect-secrets scan p6-quorum
```

No P7, S2, AWS, RunPod, HOME runtime, live memory, client data, or public
surface was touched.
