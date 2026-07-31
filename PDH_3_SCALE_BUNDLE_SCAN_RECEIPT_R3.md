# PDH-3 Credential-Free Bundle Scan Receipt R3

- `UTC_CREATED`: `2026-07-31T03:46:20Z`
- `REMOTE_EXECUTION_CANDIDATE`: `YES`
- `SUPERSEDES_FOR_REMOTE_USE`:
  `PDH_3_SCALE_BUNDLE_SCAN_RECEIPT_R1.md`,
  `PDH_3_SCALE_BUNDLE_SCAN_RECEIPT_R2.md`
- `ARCHIVE_SHA256`:
  `bc3844047bfbe455fc86d32c2088ddefcd180d91130b57f42f99c2d021b12529`
- `ARCHIVE_BYTES`: `142828968`
- `BUNDLE_RECEIPT_FILE_SHA256`:
  `d1ec79f583233126b0237c1855a5e31084a77ab9bda373cc5795f020f73c7eef`
- `BUNDLE_RECEIPT_CANONICAL_SHA256`:
  `d7324476701792256cd4755675c2cecccf6516c6a099dba4eccfd3d367e5a661`
- `SOURCE_SET_SHA256`:
  `3c4cad585798ab3eef81e7d2130d2ff13518d5ff841a7ddb591b9e63b25868b2`
- `MANIFEST_SHA256`:
  `499723cca5456bee1696bb24ba61865faaf28769b44a9fe8cf90951b5c072191`
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
43 correct stable reasons, zero false promotion, zero refusal mutation, 43
teardowns, and zero residue. The canonical aggregate hash recorded inside that
evidence is
`7d113ddcaf051ae35ff91b9cdc706da3529a7c0b748cb974ec0fb258c51a66fb`;
the aggregate file SHA-256 is
`4f696717bfec2d2cf85766804ef41c829066fc0fe406e2778614a33559ab6e9b`.

The R3 contract additionally pins the exact image
`runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`, the only exposed port
`22/tcp`, and disabled global networking. No credential, cloud
configuration, HOME path, private data, account identifier,
persistent-volume binding, or network-volume binding is present in the R3
transfer bundle.
