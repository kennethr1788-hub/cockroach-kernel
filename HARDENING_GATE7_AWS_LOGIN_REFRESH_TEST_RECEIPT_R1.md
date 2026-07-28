# Hardening Gate 7 AWS Login Refresh Test Receipt R1

- `UTC_RECORDED`: `2026-07-28T21:53:10Z`
- `BASE_COMMIT`: `eea91cc3595f4868b83efb650f20fcf7d7e8c863`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `PY_COMPILE`: `PASS; 4_FILES`
- `S3_SOAK_TESTS`: `PASS; 17_OF_17`
- `NEW_MARGIN_TEST`: `PASS; EARLY_PROBE_BLOCKED; EXACT_900_SECOND_PROBE_PASS`
- `LIVE_PROVIDER_PROOF`: `PASS`
- `LIVE_PROVIDER`: `login`
- `AUTOMATIC_REFRESH_CONTRACT_OBSERVED`: `YES`
- `PROVIDER_PROOF_RECEIPT_SHA256`: `e44715c2505fe6f6382e8d4521bf6c2ab53d692e3f16db7d576fe14903ff38d7`
- `PROVIDER_PROOF_FILE_SHA256`: `17f2652aea37572c762795dd2797283f9be48e07b4e738cbe054b20d0de2aff9`
- `POST_REFRESH_LIVE_READINESS`: `GREEN; AWS_AUTHENTICATED; COCKROACH_REACHABLE; CREDENTIAL_BYTES_RECORDED_FALSE`
- `POST_REFRESH_LIVE_READINESS_RECEIPT_SHA256`: `7dba1517728342f15e65fa8f6e9635f3f425a7f16d2f2e7f3c3b940bc0dae55b`
- `POST_REFRESH_LIVE_READINESS_FILE_SHA256`: `7f5190d82cdd6bdaf4ad31e9883179c3ec0509905ff1b36e16feb572ab492234`
- `HIDDEN_SEED_EXISTS`: `NO`
- `MEASURED_EXECUTION_STARTED`: `NO`

The initial root-level unittest invocation was invalid because it omitted the
`s3-soak` import path. It produced no mutation. The canonical discovery command
then passed all 17 tests. The live provider proof made no Lambda call and no
CockroachDB mutation; it inspected only sanitized provider metadata and the
installed CLI's public help/version surfaces.
