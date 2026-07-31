# PDH-3 Credential-Free Bundle Scan Receipt R4

- `UTC_CREATED`: `2026-07-31T04:03:40Z`
- `REMOTE_EXECUTION_CANDIDATE`: `YES`
- `SUPERSEDES_FOR_REMOTE_USE`: `R1`, `R2`, and `R3`
- `ARCHIVE_SHA256`:
  `072fc945b79dfdb0c85e2edc9406e7a4fb75751f72128a97ab80611c4d092b72`
- `ARCHIVE_BYTES`: `142828959`
- `BUNDLE_RECEIPT_FILE_SHA256`:
  `6931db17780e456096a36f1b926b3cbb6344350dea147d58e22abdbfbb963b3a`
- `BUNDLE_RECEIPT_CANONICAL_SHA256`:
  `6eb05b60a22ba5f15b8101e6b59b86729c24cbb4689454f103adf8215bf99763`
- `SOURCE_SET_SHA256`:
  `448571283fd2f7501e1b65c3baf6f079644d20a2ad00ea606c3d10e127c11a88`
- `MANIFEST_SHA256`:
  `4036903461119d87381c00c18c4df3d985fe2d4a935e7ae17658a55c0ec803df`
- `ARCHIVE_ENTRIES`: `17`
- `UNSAFE_ARCHIVE_ENTRIES`: `0`
- `DETECT_SECRETS_FINDINGS`: `0`
- `ACTIONABLE_RG_FINDINGS`: `0`
- `GITLEAKS_RAW_FINDINGS`: `1`
- `GITLEAKS_ACTIONABLE_FINDINGS`: `0`

The one raw Gitleaks match remains the previously classified
`sourcegraph-access-token` false positive in the official CockroachDB
`THIRD-PARTY-NOTICES.txt`, whose complete SHA-256 is
`af9d8c7290aafeec05409e728cffca8c613936968ae7178b716ee34681812d83`.

The extracted source compiles. Its verifier smoke is GREEN across 43
executions, 43 correct stable reasons, zero false promotion, zero refusal
mutation, 43 teardowns, and zero residue. The canonical aggregate SHA-256 is
`ed0725ecf993e91fa93f03d7cd27f22c1fbd7348070bb1cf60d3cd0f0a2f5081`;
the aggregate file SHA-256 is
`cbf55eaaa5b84e8f59ff3ce62cf49d30621c52e9211d1e633a8a93df68eaa3ca`.

R4 changes only the accepted same-price provider RAM range from exact 94 GB to
94–188 GB. Every other executable source, runtime, image, port, workload,
threshold, credential, storage, rate, duration, and teardown boundary is
unchanged.
