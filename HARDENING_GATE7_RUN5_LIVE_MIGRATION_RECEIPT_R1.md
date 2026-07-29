# Gate 7 Run 5 Live Migration Receipt R1

- `STATUS`: `GREEN`
- `UTC_APPLIED`: `2026-07-29T19:22:51Z`
- `ORCHESTRATION_COMMIT`: `c122174fe4ddd23af79ff53686e10fc2ca40fbc4`
- `MIGRATION`: `p9-cloud/migrations/003_collision_safe_vector_digest.sql`
- `MIGRATION_SHA256`: `d4696b355525454158818d29c4c8d6f3fa317e549a5bd32fb184eb008119d660`
- `MIGRATION_OUTPUT_SHA256`: `db3307fa16cafbbfb1fc75868bd4d90951beac528d16fd938b98cc62a76ffbcd`
- `MIGRATION_LATENCY_MS`: `6733`
- `OLD_UNIQUE_DIGEST_CONSTRAINT_COUNT_AFTER`: `0`
- `DIGEST_LOOKUP_INDEX_DISTINCT_COUNT_AFTER`: `1`
- `DIGEST_LOOKUP_INDEX_NON_UNIQUE`: `true`
- `DIGEST_LOOKUP_INDEX_KEY_COLUMN`: `vector_digest`
- `DIGEST_LOOKUP_INDEX_IMPLICIT_IDENTITY_COLUMN`: `vector_id`
- `VERIFICATION_OUTPUT_SHA256`: `899583e2c008bceeca45ab7f1180ced540617ad038bac2dc83cc3179da45bd19`
- `CREDENTIAL_BYTES_RECORDED`: `false`
- `CONSOLE_LOGIN_USED`: `false`
- `HOST_ONLY_KEYCHAIN_ADAPTER_USED`: `true`

The project-local host adapter retrieved the CockroachDB credential directly
into the child-process environment, executed the checked-in migration, removed
the environment binding, and zeroed the in-process byte buffer. The credential
was not printed, written to evidence, committed, or transferred to RunPod.

The live `SHOW INDEXES` response reports two index rows because CockroachDB
enumerates the explicit key column and the implicit unique row-identity column.
They are one distinct non-unique index named
`context_vectors_vector_digest_idx`; this receipt does not misstate the raw row
count as the number of indexes.
