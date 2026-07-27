# Hardening Gate 4 Secret Scan Classification R1

- `GITLEAKS_FINDINGS_NEW_GATE4_CLOSEOUT_FILES`: `0`
- `DETECT_SECRETS_FINDINGS_NEW_GATE4_CLOSEOUT_FILES`: `3`
- `TRUE_SECRETS`: `0`
- `CLASSIFICATION`: `EXPECTED_PACKET_SHA256_ECHOES`
- `UTC_RECORDED`: `2026-07-27T20:30:50Z`

The three detect-secrets findings are the canonical Gate 4 packet SHA-256
echoed by the two valid raw judge outputs and the preserved invalid GLM attempt:

```text
484686e1c02ef84c82a5433c6365559d1683502f9e92fb39d9a039a4b327429d
```

That value is a public evidence identifier, not a password, API key, token,
credential, cookie, encryption key, or private-data digest. The corresponding
files contain no secret bytes. No suppression was added and the raw judge
outputs remain unchanged.

The scan was scoped to the new Gate 4 closeout files and `RESUME_STATE.md`.
Unrelated runtime directories were not incorporated into or egressed with the
judge packet.

