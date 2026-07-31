# PDH-3 Credential-Free Bundle Scan Receipt R7

- `UTC_CREATED`: `2026-07-31T04:38:36Z`
- `REMOTE_EXECUTION_CANDIDATE`: `YES`
- `SUPERSEDES_FOR_REMOTE_USE`: `R1` through `R6`
- `ARCHIVE_SHA256`:
  `b457a288d519da82a622ad705cd6106ffbecf2dd47b536b5af2dc2983c587868`
- `ARCHIVE_BYTES`: `143471437`
- `BUNDLE_RECEIPT_FILE_SHA256`:
  `6b99d25161eab1c6c0eeb6972b2d863b4ad1492c78534e4625bb5b2c86dcd4d5`
- `BUNDLE_RECEIPT_CANONICAL_SHA256`:
  `b0d6d8a140390340dc2a95abc2c8e0b0612306432046b1a5bf24aceba8d44bb8`
- `SOURCE_SET_SHA256`:
  `e9b8cb1fcfcd683baa3a7ebd9fa35864dfd408c187ce60b566a8bdac39bbbe03`
- `MANIFEST_SHA256`:
  `e47a1fa41cb97e105fbcb32a6a4f58f2d797cec13be37683a88ad5b196ecff8e`
- `MANIFEST_FILE_COUNT`: `19`
- `ARCHIVE_ENTRIES`: `20`
- `UNSAFE_ARCHIVE_ENTRIES`: `0`
- `UNIT_TESTS`: `16 GREEN`
- `DETECT_SECRETS_RAW_FINDINGS`: `28`
- `DETECT_SECRETS_ACTIONABLE_FINDINGS`: `0`
- `GITLEAKS_RAW_FINDINGS`: `1`
- `GITLEAKS_ACTIONABLE_FINDINGS`: `0`
- `SENSITIVE_RG_ACTIONABLE_FINDINGS`: `0`

The 28 detect-secrets findings are deterministic SHA-256 evidence values. The
one Gitleaks match is the previously classified string in the official
CockroachDB `THIRD-PARTY-NOTICES.txt`, SHA-256
`af9d8c7290aafeec05409e728cffca8c613936968ae7178b716ee34681812d83`.
No credential value, private key material, private path, or HOME path was
accepted.

The extracted source compiles and its manifest matches every file. Its
verifier smoke is GREEN across 43 executions, with zero false promotion, zero
refusal mutation, 43 teardowns, and zero residue. Its canonical aggregate
SHA-256 is
`0b2c274403b7b1f8e3619b6503fa492c90758d2cb326a4a89eccbb8e3b4e7272`;
the aggregate file SHA-256 is
`f4bc65095a78a4249450dba9a0de430b9449f7d592a1e9c6eb091969a47c4d63`.

R7 adds two tested classifications: destinationless `sendto` on a connected
socket is permitted because every preceding connect is traced from pre-exec,
while explicit external sendto destinations remain blocked. It retains the
observation-only claim and does not claim a namespace, firewall, or packet
denial.
