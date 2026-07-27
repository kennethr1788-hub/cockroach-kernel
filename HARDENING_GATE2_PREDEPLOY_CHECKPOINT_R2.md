# Hardening Gate 2 Pre-Deployment Checkpoint R2

- `UTC_RECORDED`: `2026-07-27T18:05:04Z`
- `STATUS`: `DEPLOYMENT_READY_NOT_GREEN`
- `LAST_GREEN_GATE`: `HARDENING_1_CLI_GREEN`
- `PARENT_COMMIT`: `406c91a509d92db73afa8c4bfb0b9235f2dcf57c`
- `PROMPT_SHA256`: `93d641dd5c21c0042fe5be5d0cdaa45b90e217c6662b6241c4f8214b30c65ab4`
- `AUTHORIZATION_PACKET_SHA256`: `4189d411ae296bcac93e1ef55bf1fe774dbb9d2c1c0debca1a198c3374d87ea7`
- `BUNDLE_SHA256`: `1fbcaf5b79a648653a26669b224d78f50239380c0318506c01a5a2df21df3f58`
- `DEPLOY_HARNESS_SHA256`: `6cff71df2f4ebedcc36804b5afad46922d8a5de060ee676416086274fb2651ef`
- `RESOURCE_CONTRACT_SHA256`: `fb08161fea56f314c61106b1758263601823a1d4bb52ffa69be8de9534bc4e7a`
- `TRUST_POLICY_SHA256`: `b9cc71a38c80e687ad1946218fb689594cfb66a3deb9437944c40e670a4a8633`
- `AWS_AUTH`: `ACTIVE_VERIFIED`
- `EXPECTED_SECRET`: `PRESENT_METADATA_ONLY`
- `LAMBDA`: `ABSENT`
- `IAM_ROLE`: `ABSENT`
- `HTTP_API`: `ABSENT`
- `LOG_GROUP`: `ABSENT`
- `ALARMS`: `ABSENT`
- `RUNPOD_ACTIVE`: `no`

The deploy harness creates only the exact frozen Gate 2 resources, never reads
the secret value, verifies the complete resource configuration, and removes
all resources it created if deployment fails. The previously authorized
project secret remains outside rollback ownership. This is a pre-mutation
checkpoint, not evidence that the public demo works.
