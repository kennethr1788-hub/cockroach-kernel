# P5 Evidence Manifest

- `IMPLEMENTATION_COMMIT`: `5f59a07fdd357e128c07def63775d3f1e987cefb`
- `PACKET_COMMIT`: `b54534e`
- `PACKET_SHA256`: `985d1aa4fcd8ff8776ba997711aec35afecab1555bcdda5a91cd2de83e326cb8`
- `UNIT_AND_ADVERSARIAL_TESTS`: `20/20 PASS`
- `CLEAN_COCKROACH_TRIALS`: `2/2 PASS`
- `PERSISTED_ROWS_PER_TRIAL`: `5 manifests / 5 results / 5 advisory verdicts`
- `DUPLICATE_RESULT`: rejected by database uniqueness and local aggregation
- `AGGREGATE_SHA256`: `9e95250c7f7c9328f04c5b3d7b4b8694e0606885cb3e62005de086b2f5b99aaa`
- `RESIDUE`: no `p5-db-*` temporary root after successful trials
- `JUDGES`: GLM GREEN and AGY GREEN on the exact R2 hash

Primary evidence:

- `P5_CONTRACT.md`
- `P5_PERSONA_SOURCE_RECEIPT.md`
- `P5_BUILDER_CONTRIBUTIONS.md`
- `p5-lanes/manifest.py`
- `p5-lanes/migrations/001_lanes.sql`
- `p5-lanes/run_integration.py`
- `p5-lanes/test_manifest.py`
- `p5-lanes/test_manifest_adversarial.py`
- `p5-lanes/fixtures/`
- `P5_PACKET_R2.md`
- `P5_JUDGE_RECEIPT_R2.md`

Non-claims: P5 is advisory only. It does not close P6, P7, S2, Band B,
release, or submission.
