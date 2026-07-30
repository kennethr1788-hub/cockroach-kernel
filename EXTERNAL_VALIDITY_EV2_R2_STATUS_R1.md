# External Validity EV2 Replacement Status R1

- `STATUS`: `LIVE_CONTINUITY_EVIDENCE_GREEN`
- `UTC_CLOSED`: `2026-07-30T11:58:41Z`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `REPAIR_COMMIT`: `2c4f2159589c50b2136a95ae2a026d8db438a74d`
- `PREFLIGHT_PACKET_SHA256`: `42cb7faa0080462928b82744288bd3b57dc5f03e6d77407e8f8d33f01181e310`
- `FINAL_REVIEW_PACKET_SHA256`: `f62463cf1f2cc7ec47f5877d1013dade4e300ab5a6d72dffaf1ee42d7cf3c8a7`
- `EVIDENCE_COMMIT`: `29fb4ee0bddaa6c2be8869bf7cb43f9c6c07709b`
- `EVIDENCE_MANIFEST_SHA256`: `aa66877fba906e6849a25b0408f95146b309e6c5366b7521e2174368cc769bcd`
- `FINAL_RECORD_SHA256`: `e818496aec4ef6182829afb1c542fcfbbaac7549c90d9053ef3aa626278920d1`
- `FINAL_RECEIPT_SHA256`: `80ef97f74c7fd9fdb3ab105f91c1149e56a09469e7d3b83862ccf7b532da9a07`
- `EXECUTIONS`: `24_OF_24_PASS`
- `MATRIX`: `8_FAULTS_X_3_REPETITIONS`
- `SCENARIO_INVARIANTS`: `24_OF_24_PASS`
- `PARTIAL_COMMITS`: `0`
- `DUPLICATE_PROMOTIONS`: `0`
- `FALSE_PROMOTIONS`: `0`
- `REPLAY_ACCEPTANCES`: `0`
- `TEARDOWN`: `PASS`
- `FAULT_LAMBDA_ABSENT_LIVE`: `TRUE`
- `DISPOSABLE_SCHEMA_ABSENT_LIVE`: `TRUE`
- `GITLEAKS`: `ZERO_FINDINGS`
- `SECONDARY_CREDENTIAL_SCAN`: `ZERO_FINDINGS`
- `PRIVATE_PATH_AND_CREDENTIAL_MARKER_SCAN`: `ZERO_FINDINGS`
- `FAILED_R1`: `PRESERVED; 0_OF_24; ZERO_CREDIT`
- `GLM_FINAL`: `GREEN; EXACT_HASH; RECUSAL_CLEAR`
- `AGY_FINAL`: `RECUSAL_REQUIRED; PRESERVED_NOT_COUNTED`
- `CAMPAIGN_ID_REUSE_LIMITATION`: `The replacement output root and preflight hash are unique, but the frozen coordinator retained the internal protocol-family campaign_id ck-ev2-live-continuity-r1.`
- `OVERALL_EXTERNAL_VALIDITY_EVIDENCE_GREEN`: `OPEN_NOT_CLAIMED`
- `NEXT_ALLOWED_ACTION`: `Continue only with the separately authorized EV1 or EV3 protocol; do not resume Gate 9 until the full external-validity program is settled or explicitly narrowed.`

## Supported claim

Across 24 bounded executions using the declared live CockroachDB Cloud and AWS
Lambda path, the frozen product failed closed under the eight tested fault
classes, preserved the declared transactional and linkage invariants, rejected
replay, and completed scoped teardown.

## Unsupported claims

This evidence does not establish regional failover, node-loss survival,
production scale, independent-human use, arbitrary-byte recovery, exact provider
billing, or the overall EV0-through-EV3 external-validity gate.
