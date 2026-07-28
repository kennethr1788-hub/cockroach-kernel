# Hardening Gate 7 — Local Readiness Receipt R2

- `UTC_CREATED`: `2026-07-28T04:12:16Z`
- `PARENT_HEAD`: `cb52a19c842b0ecc264dd6b02c25bb1f7176efdc`
- `EVIDENCE_CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `RUNPOD_RUNNING_INVENTORY_AT_R1`: `[]`
- `RUNPOD_CREATED`: `NO`
- `SPEND_INCURRED`: `NO`
- `REAL_CAMPAIGN_SALT_CREATED`: `NO`
- `REAL_HELD_OUT_VECTORS_GENERATED`: `NO`
- `TARGET_PYTHON`: `3.12.13`

## Added runner evidence

```text
Gate 7 unit and subprocess campaign tests: 4/4 PASS
synthetic fixed-salt failure vectors: 21/21 expected semantics PASS
synthetic fixed-salt valid controls: 7/7 expected semantics PASS
fresh-process campaign executions: 43/43 PASS
fresh temporary root teardown: 43/43 PASS
interruption state after fault: CONSUMED
promotion recorded after interruption: false
replay after interruption: REFUSE / WARRANT_REPLAY
canonical aggregate: GREEN
targeted gitleaks scan: PASS
targeted detect-secrets scan: PASS
```

The fixed salt used by the unit test is public test data and is not the future
measured campaign salt. No measured held-out vector exists yet.

## Runner bindings

- `hardening-gate7/make_vectors.py`:
  `6550ac2957c0e9eedf0f19ae271a4629d6f4e4c30ec9f78ab389be7eee29d6f6`
- `hardening-gate7/run_trial.py`:
  `1a167aafd2b54299d798ed83e02d94cc6fceddcecfc92f635b2ccc3676c09881`
- `hardening-gate7/run_campaign.py`:
  `3fd21973fa611cac9da782eed89bf2c113b5c3f65dbb53726cc7b021fbf761d2`
- `hardening-gate7/test_gate7.py`:
  `bc23a82bbd3fa755b5380b535d0183bddf5b46843ba16f9b5ef2723ebb2a6db8`
- `hardening-gate7/profile_memory.py`:
  `a6d021e5ba4633e682a0e842ab95d64c341475aa81a8c781d063df3262212fc1`

## Offline memory sizing

Python 3.12.13 generated the frozen 46,000-row synthetic input shape:

```text
tasks=2000
events=20000
receipts=4000
vectors=20000
vector_queries=200
end_to_end_calls=12
canonical_input_bytes=11787916
generation_elapsed_ms=868
```

Embedded profile hash:
`6999749effba49ab7c0b94726395528989ccc6c971901eeaf4eb8f0bdd91596b`.
This is input-sizing evidence only, not database-performance evidence.

## Remaining launch blockers

1. The strict live-memory bridge and exact campaign-prefix cleanup harness are
   not implemented or dry-run.
2. Runtime `INSERT` and exact cleanup authority must be read back. The public
   demo identity is intentionally read-only and cannot be used for this load.
   No broader privilege may be inferred from earlier success.
3. Current CockroachDB capacity, topology, and allowed schema must be read back.
4. The AWS session must be refreshed only after campaign-ready and must exceed
   the last live call by at least 15 minutes.
5. Current RunPod image/shape/price, safety deadlines, aggregate spend, transfer
   archive, detached guard, and teardown commands are not frozen.
6. Same-hash GLM and AGY preflight review is not complete.
7. Kenneth has not yet authorized the final frozen Gate 7 spend/lifecycle
   envelope.

## Current outcome

```text
HARDENING_7_PREFLIGHT_OPEN
RUNPOD_CREATION_FORBIDDEN
```

The offline 43-execution runner is ready. The live-memory and paid-lifecycle
surfaces are not ready and must not be improvised on a paid worker.
