# Hardening Gate 7 Run 4 AWS Refresh Required R1

- `STATUS`: `HUMAN_ACTION_REQUIRED`
- `UTC_RECORDED`: `2026-07-29T06:13:43Z`
- `LAST_GREEN_GATE`: `GATE7_RUN4_PREFLIGHT_GREEN`
- `PREFLIGHT_PACKET_SHA256`: `e7f4d8723b49f422bf31e0f264d49432c5735054ed7d45fdb48666a78e55a7e4`
- `PREFLIGHT_JUDGES`: `GLM_5_2_GREEN; AGY_GREEN; EXACT_SAME_HASH`
- `RUNPOD_ACTIVE_INVENTORY`: `[]`
- `RUNPOD_WORKER_CREATED`: `NO`
- `HIDDEN_SEED_CREATED`: `NO`
- `COCKROACH_READINESS`: `GREEN`
- `AWS_READINESS`: `HUMAN_ACTION_REQUIRED`
- `CREDENTIAL_BYTES_RECORDED`: `false`
- `READINESS_RECEIPT_SHA256`: `279de68954bebc57ff67e58cfecfe2626b5edd6fb8b375674c5c54cc21cf0717`
- `READINESS_FILE_SHA256`: `b69a4cc222abfbf1a80abecf5645691aec282f4b131cd4529a3204196db96b46`

## Closed pre-worker evidence

- two deterministic transfer archives are byte-identical;
- archive SHA-256: `9d7e2ba2e3c75fcadbf9c8567da536ae5fec1decac44a035c622cebd130381ad`;
- archive bytes: `144544975`;
- file count: `95`;
- transfer manifest file SHA-256: `b89e3e407228d01a46d8a8ce1bde4c70665092ce945408e95d4a6bfc1ce12ee2`;
- payload tree file SHA-256: `a68a0b9e521f8a1c0987a4e028c35ed740517947245e4ebf50b38f9232bdea3a`;
- gitleaks findings: `0`;
- detect-secrets findings: `0`;
- extracted generate-only smoke: exact `[2000,20000,4000,20000]`, 200 queries,
  107 cleanup batches, 80 indexed vector batches at 250 rows;
- packaged helper is present and hash-bound; its required `/workspace/...`
  absolute-root execution remains a remote `CAMPAIGN_READY` check.

The AWS identity command exited nonzero after the operator's prior login. The
probe persisted only failure/output hashes and schema-safe metadata. It did not
persist or expose AWS account identity or credentials.

## Exact human action

```bash
cd /Users/kennethruedas/sandbox/cockroach-kernel-build-20260725

AWS_CONFIG_FILE="$PWD/.s3-runtime/aws-auth/config" \
AWS_LOGIN_CACHE_DIRECTORY="$PWD/.s3-runtime/aws-auth/login-cache" \
AWS_SHARED_CREDENTIALS_FILE=/dev/null \
.s3-runtime/aws-expanded-r1/aws-cli.pkg/Payload/aws-cli/aws login \
  --profile ck-s3 \
  --region us-west-2
```

After the operator reports `Done`, rerun the read-only live readiness probe.
Only a new GREEN receipt may resume worker creation. Do not regenerate the
archive, change the packet, create the hidden seed, or create a worker before
that probe passes.
