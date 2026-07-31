# PDH-3 Credential-Free Bundle Scan Receipt R5

- `UTC_CREATED`: `2026-07-31T04:14:40Z`
- `REMOTE_EXECUTION_CANDIDATE`: `YES`
- `SUPERSEDES_FOR_REMOTE_USE`: `R1` through `R4`
- `ARCHIVE_SHA256`:
  `1a1690bb090cd91999ad00c555f0d4a1f4cbffea3fa0bacf81d9cabf98ac91e9`
- `ARCHIVE_BYTES`: `142831369`
- `BUNDLE_RECEIPT_FILE_SHA256`:
  `684e8febd9c9ecbdd80c73cf43418279443daf14c72500e147f4a2108a5216e1`
- `BUNDLE_RECEIPT_CANONICAL_SHA256`:
  `7b4588250822dcad523c334d8180c8d8f24707b362d7ccbf127ea9a0060eb72a`
- `SOURCE_SET_SHA256`:
  `a1830ce874c7759f7c6a178c3ef1089f72af0e0802829e3a94ca28e49e7b1900`
- `MANIFEST_SHA256`:
  `d8fefe4c4f18ea6f57d9555a31d3751181d6d1673148899fa33e922f88f96f05`
- `ARCHIVE_ENTRIES`: `18`
- `UNSAFE_ARCHIVE_ENTRIES`: `0`
- `DETECT_SECRETS_FINDINGS`: `0`
- `ACTIONABLE_RG_FINDINGS`: `0`
- `GITLEAKS_RAW_FINDINGS`: `1`
- `GITLEAKS_ACTIONABLE_FINDINGS`: `0`

The one raw Gitleaks match remains the classified false positive in the
official CockroachDB `THIRD-PARTY-NOTICES.txt`, bound by SHA-256
`af9d8c7290aafeec05409e728cffca8c613936968ae7178b716ee34681812d83`.

The extracted source compiles. Its verifier smoke is GREEN across 43
executions, 43 correct stable reasons, zero false promotion, zero refusal
mutation, 43 teardowns, and zero residue. Its canonical aggregate SHA-256 is
`d95d1ef70832952f4c7facc16f3b7978c58794b85c8e8bfbf4f68d16e168c820`;
the aggregate file SHA-256 is
`c10f3a7d20598fccd883c0f70bc06b5411712fec3b359d0a805c53cfc166a0cc`.

R5 adds only the tested process-tree `connect`/`sendto` observer and the honest
observed-zero-egress contract. It makes no network-namespace, firewall, or
packet-denial claim.
