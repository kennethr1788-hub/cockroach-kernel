# Hardening Gate 2 Human Authorization Receipt R1

- `UTC_RECORDED`: `2026-07-27T17:31:36Z`
- `TARGET_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `LAST_GREEN_GATE`: `HARDENING_1_CLI_GREEN`
- `EXECUTION_PROMPT_SHA256`: `93d641dd5c21c0042fe5be5d0cdaa45b90e217c6662b6241c4f8214b30c65ab4`
- `AUTHORIZATION_PACKET_SHA256`: `4189d411ae296bcac93e1ef55bf1fe774dbb9d2c1c0debca1a198c3374d87ea7`
- `AWS_AUTHENTICATION`: `ACTIVE_VERIFIED_READ_ONLY_IDENTITY_PROBE`
- `COCKROACHDB_CONTINUITY`: `KENNETH_CONFIRMED_THROUGH_2026-09-15T21:00:00Z`
- `PUBLIC_RESOURCE_MUTATIONS_AT_RECEIPT_FREEZE`: `0`
- `RUNPOD_ACTIVE_COUNT`: `0`

## Kenneth's explicit authorization

Kenneth authorized execution of the complete Hardening Run under the exact
frozen execution prompt. That prompt incorporates his explicit approval of the
bounded Gate 2 public AWS demo, including:

- maximum permitted incremental AWS spend of `$12.00`;
- the documented best-effort throttling and denial-of-wallet residual;
- anonymous access to only `GET /demo/promote` and `GET /demo/refuse`;
- one project-scoped Secrets Manager secret;
- preservation through `2026-09-15T21:00:00Z`;
- no billing-setting change;
- no broader route, service, database authority, or public input.

Kenneth separately confirmed that the `cockroach-kernel` Basic cluster is
authorized and able to remain active through the judging period within the
reviewed resource limits.

Kenneth personally completed the visible project-local AWS login. A subsequent
read-only identity probe using profile `ck-s3` in `us-west-2` succeeded. No
credential, account identifier, token, cookie, password, or MFA value is
stored in this receipt.

Authorization permits execution. It does not prove deployment, behavior,
access, cost, topology, teardown, or Gate 2 GREEN.
