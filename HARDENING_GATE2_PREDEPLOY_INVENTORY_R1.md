# Hardening Gate 2 Pre-Deployment Inventory R1

- `UTC_RECORDED`: `2026-07-27T17:31:36Z`
- `AWS_PROFILE`: `ck-s3`
- `REGION`: `us-west-2`
- `AWS_AUTH`: `GREEN`
- `LAMBDA_ck-hardening-demo`: `ABSENT`
- `IAM_ROLE_ck-hardening-demo`: `ABSENT`
- `SECRET_ck-hardening-demo-db`: `ABSENT`
- `API_GATEWAY_NAME_ck-hardening-demo_COUNT`: `0`
- `LOG_GROUP_/aws/lambda/ck-hardening-demo_COUNT`: `0`
- `CLOUDWATCH_ALARM_PREFIX_ck-hardening-demo_COUNT`: `0`
- `RUNPOD_ACTIVE_COUNT`: `0`
- `AWS_MUTATIONS`: `0`
- `COCKROACHDB_MUTATIONS`: `0`

The exact project resource namespace was empty before deployment. Existing
unrelated AWS, CockroachDB, and RunPod resources were not enumerated into this
receipt and are outside the mutation boundary.
