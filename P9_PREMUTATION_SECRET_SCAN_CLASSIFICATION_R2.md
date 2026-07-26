# P9 Pre-Mutation Secret Scan Classification R2

- `UTC`: `2026-07-26T19:22:00Z`
- `RESULT`: `GREEN_WITH_CLASSIFIED_FALSE_POSITIVES`
- `P9_CLOUD_SCAN`: `0 findings`
- `NEW_RECEIPT_SCAN`: `0 findings`
- `FULL_REPOSITORY_GITLEAKS_CANDIDATES`: `4`
- `REAL_SECRET_FINDINGS`: `0`

The full-repository scan found four pre-existing candidates. None is a
credential:

1. `P0_STATUS.md`: ordinary prose naming AWS/CockroachDB services.
2. `S1_RETRY_PACKET_R3.md`: a recorded SHA-256 digest.
3. Darwin vendored CockroachDB `THIRD-PARTY-NOTICES.txt`: a 40-character Git
   revision in a package locator.
4. Linux vendored CockroachDB `THIRD-PARTY-NOTICES.txt`: the same package Git
   revision.

The candidate values are not reproduced in this receipt. Classification used
file, line, rule, redacted context, length, and SHA-256 only. No credential,
token, API key, password, cookie, MFA value, payment data, or account identifier
was found.

The first compound shell sequence did not stop on the nonzero full-repository
scanner status and created commit `eb427eb11cffa642e83338105e7c6fa56de43b38`.
This receipt closes that evidence gap before any cloud mutation; history is not
rewritten.
