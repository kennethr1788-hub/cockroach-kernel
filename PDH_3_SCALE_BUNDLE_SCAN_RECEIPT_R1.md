# PDH-3 Credential-Free Bundle Scan Receipt R1

- `ARCHIVE_SHA256`:
  `fd15b62530c606a3de8c4b5b0875970e21395e4b74758e4650f261b96385d158`
- `ARCHIVE_BYTES`: `142828968`
- `BUNDLE_RECEIPT_SHA256`:
  `8cdb7a0d8751c6f22b0d2867b3163a7feb99a66d2a2bec1cdf78b6269c5ffcd9`
- `SOURCE_SET_SHA256`:
  `4e3b8f629ce0779d7fec2c8d97c92f543abda97a642a3ece7760167e400541d2`
- `ARCHIVE_ENTRIES`: `17`
- `UNSAFE_ARCHIVE_ENTRIES`: `0`
- `DETECT_SECRETS_FINDINGS`: `0`
- `ACTIONABLE_RG_FINDINGS`: `0`
- `GITLEAKS_RAW_FINDINGS`: `1`
- `GITLEAKS_ACTIONABLE_FINDINGS`: `0`

The single raw Gitleaks finding is rule `sourcegraph-access-token` in the
official CockroachDB v26.2.3 `THIRD-PARTY-NOTICES.txt` at line 127752. The
complete notices file is independently bound by SHA-256
`af9d8c7290aafeec05409e728cffca8c613936968ae7178b716ee34681812d83`.
It is license/provenance text, not executable configuration or a credential.
The application/controller source subset has zero findings.

The extracted source compiles. Its 43-execution verifier smoke is GREEN with
zero false promotion, zero refusal mutation, 43 correct stable reasons, 43
teardowns, and zero residue. Its aggregate SHA-256 is
`e432c8e4eb964e396d9043184b21ca463b8bc5eaccf4f55b0af226bff397d93f`.

No credential, cloud configuration, HOME path, private data, or account
identifier is present in the transfer bundle.
