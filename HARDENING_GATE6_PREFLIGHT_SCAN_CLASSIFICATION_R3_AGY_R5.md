# Hardening Gate 6 R3 — Attempt-03 Packet Scan Classification

- `PACKET`: `HARDENING_GATE6_PREFLIGHT_PACKET_R3_AGY_R5.md`
- `PACKET_SHA256`: `0e047e3abfd69cc5660c88a283eb8595e869dee575eadaa34409b74dfec5f468`
- `PACKET_BYTES`: `114626`
- `GITLEAKS_FINDINGS`: `0`
- `DETECT_SECRETS_FINDINGS`: `9`
- `DETECT_SECRETS_CLASSIFICATION`: `EXPECTED_SHA256_AND_IMAGE_DIGEST_ECHOES_ONLY`
- `CREDENTIAL_OR_TOKEN_FINDINGS`: `0`
- `PACKET_ALLOWLIST`: `24 explicitly named repository files only`
- `EXCLUDED`: `all ignored runtime directories, AWS login caches, credentials, raw historical judge outputs, unrelated evidence trees`
- `GLM_EGRESS`: `sanitized packet bytes only`
- `AGY_EGRESS`: `sanitized packet bytes only`
- `UTC_RECORDED`: `2026-07-28T02:49:00Z`

The nine entropy findings occur only in the embedded Linux tool-provenance JSON
and source constants that intentionally bind SHA-256 values and OCI image
digests. Gitleaks found no secret pattern. No credential-bearing runtime path is
embedded or eligible for judge egress.
