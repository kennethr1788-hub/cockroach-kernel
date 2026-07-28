# Gate 7 AWS Login Refresh Cloud Adapter Review R1

- `SOURCE_PATH`: `s3-soak/cloud_adapter.py`
- `SOURCE_STATUS`: `HOST_ONLY; NEVER_TRANSFERRED_TO_RUNPOD`
- `PRODUCT_CANDIDATE_MUTATION`: `NO`
- `NEW_PUBLIC_FUNCTIONS`: `prove_aws_login_provider; probe_aws_identity`
- `RAW_CREDENTIAL_OUTPUT_RECORDED`: `NO`

## `prove_aws_login_provider`

The function resolves the existing strictly validated project-local live
configuration and runs three public/read-only AWS CLI surfaces:

1. `configure list` for profile `ck-s3`, requiring the sanitized provider type
   to resolve to `login`;
2. `login help`, requiring the installed CLI's automatic-refresh statement;
3. the CLI version command.

The returned canonical receipt contains only the fixed profile/region, provider
type, a boolean refresh-contract result, SHA-256 hashes of the three command
outputs, aggregate latency, `credential_bytes_recorded=false`, status, and a
receipt hash. It does not return or persist command output.

## `probe_aws_identity`

The function resolves the same strict configuration and invokes the read-only
STS identity operation for profile `ck-s3` in `us-west-2`. It requires the
decoded response to contain exactly `Account`, `Arn`, and `UserId`. The returned
record contains only the sorted field names, SHA-256 of the complete response,
latency, `credential_bytes_recorded=false`, and status. Account, ARN, user ID,
tokens, keys, and raw output are not returned or persisted.

## Failure semantics

Both functions use the existing bounded external-command runner. A nonzero AWS
exit is converted to the existing sanitized failure class and output hash. A
provider-type mismatch, missing installed refresh contract, or identity schema
mismatch raises a stable host-orchestration error and prevents coordinator
GREEN. No retry, credential export, provider fallback, Lambda call, CockroachDB
mutation, or product mutation is introduced by these functions.
