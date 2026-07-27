# Hardening Gate 2 AWS Secret Receipt R1

- `UTC_CREATED`: `2026-07-27T17:58:52Z`
- `TARGET_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `SECRET_NAME`: `ck-hardening-demo-db`
- `AWS_REGION`: `us-west-2`
- `CREATE_RESULT`: `HARDENING_GATE2_SECRET_CREATED`
- `METADATA_READBACK`: `pass`
- `ROTATION_ENABLED`: `no`
- `TAGS`: `Project=cockroach-kernel; Gate=hardening-2; ManagedBy=codex`
- `SECRET_VALUE_READ_OR_RECORDED`: `no`
- `CLIPBOARD_BYTES_AFTER_HANDOFF`: `0`
- `PUBLIC_ENDPOINT_EXISTS`: `no`
- `HELPER_SHA256`: `d572645012020ec324c00364a0182dbced9b7b26bd23443c4097eaff69d8f6cd`

The third, final provider-generated credential rotation was copied without
reveal and consumed by `hardening-gate2/create_secret.py --clipboard`. The
helper read the value in-process, supplied the five-field secret JSON only via
AWS CLI stdin, suppressed provider output, and performed metadata-only
readback. The enclosing shell cleared the clipboard unconditionally.

No secret value, credential byte, ARN, account identifier, password, cookie,
OAuth grant, or token was printed, logged, written to a file, committed, or
placed in argv. The two prior failed transport attempts remain preserved as
append-only evidence and did not create a secret.
