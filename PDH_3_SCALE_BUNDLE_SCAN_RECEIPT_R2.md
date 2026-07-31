# PDH-3 Credential-Free Bundle Scan Receipt R2

- `UTC_CREATED`: `2026-07-31T03:44:03Z`
- `SUPERSEDES_FOR_REMOTE_USE`: `PDH_3_SCALE_BUNDLE_SCAN_RECEIPT_R1.md`
- `ARCHIVE_SHA256`:
  `d418636e2ec2a6141833dd70ca8dccb1bd18c45b485cb76199a840ab3f731151`
- `ARCHIVE_BYTES`: `142829029`
- `BUNDLE_RECEIPT_FILE_SHA256`:
  `6e50456c702d99e2ed0b356914326a77d488646422a53d5266f2b524c1e4af0e`
- `BUNDLE_RECEIPT_CANONICAL_SHA256`:
  `23713fa16b8225566c5cccf3eb7f484dad35c7b7329da998180d2aff389fe39a`
- `SOURCE_SET_SHA256`:
  `8b6f5b5d9db299f7d8c6483015340d3ac74ac54b342d125ebae373184e481349`
- `MANIFEST_SHA256`:
  `b53cef499c1f0ca558fc63af4295d0f95c4831c8c23fde48717fd59bef02daf8`
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
`69e90995b72d5a05bde5840c42c2b7f6728819551dbe69f650046dfb636baa28`;
the aggregate file SHA-256 is
`16d110e29e9c0a77c8e20f417eea0a3707bc9044491f1d73440bad0304446075`.

No credential, cloud configuration, HOME path, private data, account
identifier, persistent-volume binding, or network-volume binding is present in
the R2 transfer bundle.
