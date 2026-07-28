# Hardening Gate 6 R3 — Preflight Scan Classification

- `PACKET_SHA256`: `49068ab24f16b51120b447514bd928e527d02428a8343ae10443f8a83041613b`
- `EGRESS_GATEWAY_GLM`: `ALLOW; byte-identical`
- `EGRESS_GATEWAY_CLAUDE_JUDGE`: `ALLOW; byte-identical`
- `GITLEAKS_FINDINGS`: `0`
- `DETECT_SECRETS_CLASS`: `HEX_HIGH_ENTROPY_STRING`
- `DETECT_SECRETS_VERIFIED_SECRETS`: `0`
- `UTC_RECORDED`: `2026-07-28T01:28:50Z`

The six detect-secrets matches are immutable candidate/row SHA-256 substrings
on the single minified 54-row manifest line. They are public integrity hashes,
not credentials, tokens, cookies, account identifiers, key material, or
private data. The local egress gateway independently returned ALLOW with no
hits and no private-path aliases for both required lanes. No scanner rule was
disabled or weakened.
