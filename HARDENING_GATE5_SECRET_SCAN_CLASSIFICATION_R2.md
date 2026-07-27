# Hardening Gate 5 — Secret Scan Classification R2

- `GITLEAKS_STAGED_SCAN`: `PASS_NO_FINDINGS`
- `DETECT_SECRETS_EXIT`: `0`
- `DETECT_SECRETS_FINDINGS`: `5`
- `CLASSIFICATION`: `UNVERIFIED_HEX_SHA256_VALUES_ONLY`
- `CREDENTIAL_FINDINGS`: `0`
- `PACKET_EGRESS_GUARD`: `PASS_FINAL_PACKET`
- `FINAL_PACKET_SHA256`: `41efeb9270b76a0d4e1f711d5b1ab3270ecd92d32eccce93f07bef8a6ba036c0`
- `UTC_RECORDED`: `2026-07-27T22:57:33Z`

The five heuristic findings are the packet/candidate SHA-256 fields in the raw
GLM and Claude verdicts, the judge packet's example verdict, and the sanitized
smoke summary. All are explicitly labeled hashes. None is a password, token,
key, cookie, OAuth grant, provider credential, or reversible secret.

An earlier packet formatting attempt rendered a scanner label as an assignment,
so the local GLM egress guard blocked it before provider execution. The final
packet replaced assignment-style evidence formatting, was rehashed and
rescanned, and passed the egress guard. The blocked attempt has no verdict or
gate authority.
