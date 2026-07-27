# Hardening Gate 2 Secret Handoff Attempt R2

- `UTC_RECORDED`: `2026-07-27T17:56:40Z`
- `RESULT`: `FAILED_BEFORE_SECRET_CREATION`
- `FAILURE_CLASS`: `AWS_CLI_INPUT_JSON_STDIN_PARSE_FAILURE`
- `AWS_IDENTITY_PROBE`: `pass`
- `AWS_SECRETS_LIST_PROBE`: `pass`
- `AWS_SECRET_AFTER_ATTEMPT`: `absent`
- `CLIPBOARD_AFTER_ATTEMPT_BYTES`: `0`
- `CREDENTIAL_PRINTED_OR_LOGGED`: `no`
- `AWS_PUBLIC_ENDPOINT_EXISTS`: `no`

The explicit `--clipboard` reader accepted the provider-generated credential,
but the project-local AWS CLI rejected `--cli-input-json file:///dev/stdin`
with its output suppressed by the helper. A subsequent dummy-only schema probe
reproduced `Invalid JSON received`; direct AWS identity and Secrets Manager list
probes both passed. A metadata-only readback confirmed
`ck-hardening-demo-db` remained absent.

The credential was never printed, logged, written, or placed in argv, and the
clipboard was cleared unconditionally. The repair keeps all secret bytes on
stdin but changes transport to the command's dedicated
`--secret-string file:///dev/stdin` parameter. The secret name, description,
and three fixed tags remain non-secret argv values.
