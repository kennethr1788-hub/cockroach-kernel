# Hardening Gate 6 R3 — Preflight Scan Classification

- `R1_PACKET_SHA256_SUPERSEDED`: `49068ab24f16b51120b447514bd928e527d02428a8343ae10443f8a83041613b`
- `CURRENT_R2_PACKET_SHA256`: `7993cdbf3d76469ba268cb6c4a26742d4726ecfef0b41c1a9e5072a56188650d`
- `EGRESS_GATEWAY_GLM`: `ALLOW; byte-identical`
- `EGRESS_GATEWAY_CLAUDE_JUDGE`: `ALLOW; byte-identical`
- `GITLEAKS_FINDINGS`: `0`
- `DETECT_SECRETS_CLASS`: `HEX_HIGH_ENTROPY_STRING`
- `DETECT_SECRETS_VERIFIED_SECRETS`: `0`
- `UTC_RECORDED`: `2026-07-28T01:37:03Z`

The detect-secrets entropy matches are immutable candidate/row SHA-256
substrings on the minified 54-row manifest line. They are public integrity
hashes, not credentials, tokens, cookies, account identifiers, key material, or
private data. Gitleaks reports zero findings. The local egress gateway returned
ALLOW with byte-identical output, no hits, and no private-path aliases for both
required lanes on R2. No scanner rule was disabled or weakened.
