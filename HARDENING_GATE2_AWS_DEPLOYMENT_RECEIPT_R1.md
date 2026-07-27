# Hardening Gate 2 AWS Deployment Receipt R1

- `UTC_RECORDED`: `2026-07-27T18:08:46Z`
- `STATUS`: `DEPLOYED_CONFIGURATION_GREEN_BEHAVIOR_PENDING`
- `LAST_GREEN_GATE`: `HARDENING_1_CLI_GREEN`
- `DEPLOYMENT_COMMIT_PARENT`: `b71f6097d28af11441a6d6ecfd7e7d01ac77c06f`
- `PUBLIC_ENDPOINT`: `https://6rhijj3d37.execute-api.us-west-2.amazonaws.com`
- `HTTP_API_ID`: `6rhijj3d37`
- `DEPLOYMENT_RESULT_SHA256`: `037006d44221a417ee78151a562077feeec2c64e108b4604ffe6b896e6091e8b`
- `BUNDLE_SHA256`: `1fbcaf5b79a648653a26669b224d78f50239380c0318506c01a5a2df21df3f58`
- `INLINE_POLICY_SHA256`: `0a75ccef22af990001a8f786999c0cf1fc7a52a8ceca9cd3dd48d185e86215b2`
- `SECRET_VALUE_READ`: `no`
- `RUNPOD_ACTIVE`: `no`

Direct AWS readback verified one Python 3.12 Lambda with 256 MiB memory and
an eight-second timeout; one HTTP API with exactly `GET /demo/promote` and
`GET /demo/refuse`; a default-stage rate target of 0.05 requests/second and
burst 2; one-day Lambda log retention; exactly two declared alarms; and an
inline role policy containing only `logs:CreateLogStream`,
`logs:PutLogEvents`, and `secretsmanager:GetSecretValue` on the exact project
resources. The function configuration contains only the project secret name,
not credential bytes.

This receipt proves resource configuration, not functional behavior, database
queries, public access, cost, or the final independent gate.
