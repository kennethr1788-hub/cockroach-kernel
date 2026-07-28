# Gate 7 A03 Measured Start Receipt R1

- `STATUS`: `MEASURED_CAMPAIGN_IN_PROGRESS`
- `UTC_RECORDED`: `2026-07-28T22:08:06Z`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `EXPANDED_PREFLIGHT_PACKET_SHA256`: `4fd89d699dccd0d3e15451fab40435ad2e9b3f7300061ff8791913dc4b7ecf44`
- `AWS_REFRESH_AMENDMENT_PACKET_SHA256`: `e3414df6b9df3a8e1126d494c8f542460cb38cb51386ac8ec9edfca7dd96c68d`
- `CAMPAIGN_READY_RECEIPT`: `HARDENING_GATE7_A03_CAMPAIGN_READY_RECEIPT_R2.md`
- `HIDDEN_CAMPAIGN_ID`: `ck-g7r2-20260728-a03-measured`
- `LIVE_CAMPAIGN_ID`: `ck-s3-g7r2-a03`
- `BULK_CAMPAIGN_ID`: `ck-g7r2-a03-bulk`
- `MEASURED_RERUN_AUTHORIZED`: `NO`

## Hidden campaign result

- `PRE_GENERATION_COMMITMENT_SHA256`: `5644836838eafe60146027b1ed5edd87af57d6f61bc11c3745639fbd6cebd752`
- `PRE_GENERATION_COMMITMENT_FILE_SHA256`: `b7d5d64faf33bdb6a224e9393c73e00dbffde5108871ca61427c4f965c7e2bc6`
- `GENERATION_RECEIPT_SHA256`: `a5370287a235ed6aaa7ad3191cdfb5e3ef8842361313d5e8e3dddb75b62657b0`
- `GENERATION_RECEIPT_FILE_SHA256`: `68de2c226ce1c1d5790646c4bf523f6fff38c1387d1fe4377e8fb0e2472139fe`
- `INPUT_ONLY_COPY_TREE_SHA256`: `baf7577a030260398471e67f5aac71fc0ddeef9c045f27327344a9885a426587`
- `INPUT_MANIFEST_FILE_SHA256`: `ebf10d5e6944cd67c6405e4272d10a8a43bcdaacbef446a7a62f04b936a02a7c`
- `RUNNER_ORACLE_ACCESS`: `DENIED`
- `RUNNER_ORACLE_FILES`: `0`
- `ISOLATION_ATTESTATION_SHA256`: `19363d7a70e277d5c288f51c6a46f4e26beeaa904f1309aa19bb493da250d9b9`
- `ISOLATION_ATTESTATION_FILE_SHA256`: `a5abd879995ca52db0a9840f7a6d296b92bb6604965cc0bccf7f51aab75228a2`
- `RAW_TREE_SHA256`: `e6d04bb4dd206b33d36e7bde753316d3ad538a26db334db7675da5215f225037`
- `RAW_MANIFEST_SHA256`: `7aa98d657ad64ee6fe8fb24a2fb57fee18f3888923787ae32d9a7c92b3ea1d1d`
- `RAW_MANIFEST_FILE_SHA256`: `43617b608f8c035da39e43737a2b9b5356b1bbe2252dbc8063bd0411152f697d`
- `AGGREGATE_SHA256`: `9428ae8cf6ce7857205dc718a3d2cd903463bf3f0331216b932c8e1cd74cfd8e`
- `AGGREGATE_FILE_SHA256`: `2ce59b35a52c6d495fda05665c5bf6413678538d989682965ebe61c09f5128e4`
- `HIDDEN_EXECUTIONS`: `84`
- `HIDDEN_PASS`: `84`
- `BEHAVIOR_FAILURES`: `0`
- `SAFETY_FAILURES`: `0`
- `FALSE_PROMOTIONS`: `0`
- `RESIDUE_COUNT`: `0`
- `HIDDEN_RESULT`: `GREEN_PENDING_RETRIEVAL_AND_INDEPENDENT_RECOMPUTATION`

The first pre-seed launcher invocation referenced the wrong extracted-bundle
directory and exited before Python opened the generator. No output root or seed
existed. The corrected, verified extracted-bundle path was then invoked once;
that is the sole hidden seed and sole measured 84-row campaign.

## Live track start

- `REMOTE_WORKER_PID`: `2330`
- `REMOTE_WORKER_USER`: `ckrunner`
- `REMOTE_WORKER_CREDENTIALS`: `none`
- `REMOTE_WORKER_DURATION_SECONDS`: `3600`
- `REMOTE_CHECKPOINT_SECONDS`: `60`
- `REMOTE_SAFETY_SECONDS`: `300`
- `REMOTE_CLOUD_EXCHANGE_SECONDS`: `300`
- `EXPECTED_CHECKPOINTS`: `60`
- `EXPECTED_SAFETY_REPLAYS`: `12`
- `EXPECTED_CLOUD_EXCHANGES`: `12`
- `COORDINATOR_OBSERVED_AT_RECEIPT`: `1 Lambda call; 9 CockroachDB operations; request 1 complete`
- `COORDINATOR_CEILINGS`: `12 Lambda calls; 108 CockroachDB operations`
- `BULK_WORKLOAD`: `2,000 tasks; 20,000 events; 4,000 receipts; 20,000 vectors; 200 task-bound vector queries; concurrency 4`

The live track and bulk workload run concurrently. `GREEN` is forbidden until
the complete 3,600-second worker evidence, 900-second post-final-exchange AWS
probe, bulk cleanup, retrieval/hash verification, teardown, empty inventory,
independent recomputation, and final same-hash GLM/AGY review all pass.
