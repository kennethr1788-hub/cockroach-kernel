# Hardening Gate 2 Status

- `STATUS`: `HARDENING_2_BLOCKED`
- `BLOCKER`: `LIVE_BEHAVIOR_ACCESS_COST_AND_FINAL_JUDGE_PENDING`
- `LAST_GREEN_GATE`: `HARDENING_1_CLI_GREEN`
- `LOCAL_ADAPTER_COMMIT`: `ea4d3764dc6fd778af98f23788ba9871729cd99e`
- `AWS_SESSION`: `ACTIVE_VERIFIED`
- `PUBLIC_ENDPOINT_EXISTS`: `yes`
- `PUBLIC_ENDPOINT`: `https://6rhijj3d37.execute-api.us-west-2.amazonaws.com`
- `AWS_MUTATIONS_THIS_GATE`: `1 project-scoped secret plus exact role, Lambda, log group, two alarms, HTTP API, integration, two routes, and default stage`
- `COCKROACHDB_MUTATIONS_THIS_GATE`: `1 identity plus 5 exact grants`
- `RUNPOD_ACTIVE`: `no`
- `AUTHORIZATION_PACKET`: `HARDENING_GATE2_PUBLIC_DEMO_AUTHORIZATION_PACKET_R1.md`
- `AUTHORIZATION_PACKET_SHA256`: `4189d411ae296bcac93e1ef55bf1fe774dbb9d2c1c0debca1a198c3374d87ea7`
- `PREFLIGHT_JUDGE`: `GLM_4_7_GREEN`
- `HUMAN_AUTHORIZATION_RECEIPT`: `HARDENING_GATE2_HUMAN_AUTHORIZATION_RECEIPT_R1.md`
- `PREDEPLOY_INVENTORY`: `HARDENING_GATE2_PREDEPLOY_INVENTORY_R1.md`
- `BUNDLE_RECEIPT`: `HARDENING_GATE2_BUNDLE_RECEIPT_R1.md`
- `HUMAN_ACTION`: `HARDENING_GATE2_COCKROACH_IDENTITY_ACTION_R1.md`
- `IDENTITY_RECEIPT`: `HARDENING_GATE2_COCKROACH_IDENTITY_RECEIPT_R1.md`
- `SECRET_RECEIPT`: `HARDENING_GATE2_SECRET_RECEIPT_R1.md`
- `PREDEPLOY_CHECKPOINT`: `HARDENING_GATE2_PREDEPLOY_CHECKPOINT_R2.md`
- `DEPLOY_HARNESS_SHA256`: `6cff71df2f4ebedcc36804b5afad46922d8a5de060ee676416086274fb2651ef`
- `DEPLOYMENT_RECEIPT`: `HARDENING_GATE2_AWS_DEPLOYMENT_RECEIPT_R1.md`
- `DEPLOYMENT_RESULT_SHA256`: `037006d44221a417ee78151a562077feeec2c64e108b4604ffe6b896e6091e8b`
- `LIVE_TEST_HARNESS_SHA256`: `2adfcfd13bd083ed8b4980173ecb570f5a9a69dbd276099acb19b79b32db7c0a`
- `UTC_RECORDED`: `2026-07-27T17:58:52Z`

The local adapter and deterministic Lambda bundle are mechanically green.
Kenneth approved the cost/access packet, confirmed cluster continuity, and
completed AWS login. The dedicated `ck_hardening_demo` identity now exists and
CockroachDB Cloud reported successful execution of exactly USAGE plus four
SELECT grants. The credential was copied without being read or recorded, the
authorized AWS secret exists with metadata-only readback, and the clipboard is
empty. The exact AWS resources are now deployed and their configuration
readback is green. Live behavior, database/query-plan proof, access, cost, and
final independent review remain open. No Gate 2 GREEN claim is made.
