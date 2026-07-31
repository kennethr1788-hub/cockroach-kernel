# PDH-3 Credential-Free Bundle Scan Receipt R6

- `UTC_CREATED`: `2026-07-31T04:27:56Z`
- `REMOTE_EXECUTION_CANDIDATE`: `YES`
- `SUPERSEDES_FOR_REMOTE_USE`: `R1` through `R5`
- `ARCHIVE_SHA256`:
  `debe8bee6eb02293032c697f2d00498f5c04d301bb5c07f9ea113c98040a7f84`
- `ARCHIVE_BYTES`: `143471017`
- `BUNDLE_RECEIPT_FILE_SHA256`:
  `2fd074a30141dde4773a10c72d1d3a423d22398a48e42f612a444b178758cd59`
- `BUNDLE_RECEIPT_CANONICAL_SHA256`:
  `939e541ba5c7eee660262e93dfbac56ebda77b911ffa8e4d5361392d6de78e3c`
- `SOURCE_SET_SHA256`:
  `c685db38ab86baed4e6ebf452a27669635bcbf878bdb1b168ad7e305a3735b56`
- `MANIFEST_SHA256`:
  `145f189a6ca563b4a577a9f97415ee20946f8f2f18de7f0b1f33576a3166bbce`
- `MANIFEST_FILE_COUNT`: `19`
- `ARCHIVE_ENTRIES`: `20`
- `UNSAFE_ARCHIVE_ENTRIES`: `0`
- `UNIT_TESTS`: `14 GREEN`
- `DETECT_SECRETS_RAW_FINDINGS`: `28`
- `DETECT_SECRETS_ACTIONABLE_FINDINGS`: `0`
- `GITLEAKS_RAW_FINDINGS`: `1`
- `GITLEAKS_ACTIONABLE_FINDINGS`: `0`
- `SENSITIVE_RG_ACTIONABLE_FINDINGS`: `0`

The 28 detect-secrets findings are deterministic SHA-256 values in the bundle
manifest and hash-bound campaign contracts. They are evidence identifiers, not
credentials. The one Gitleaks match remains the classified false positive in
the official CockroachDB `THIRD-PARTY-NOTICES.txt`, bound by SHA-256
`af9d8c7290aafeec05409e728cffca8c613936968ae7178b716ee34681812d83`.
The text scan found only source identifiers and third-party notice text; it
found no credential value, private key material, private path, or HOME path.

The extracted source compiles and its manifest matches every extracted file by
path, byte count, and SHA-256. Its verifier smoke is GREEN across 43
executions, 43 correct stable reasons, zero false promotion, zero refusal
mutation, 43 teardowns, and zero residue. Its canonical aggregate SHA-256 is
`d856ac735686e2bca6cbe358502a5f4f7e63e8b044f9b7b1e0d4c3e604f58670`;
the aggregate file SHA-256 is
`8da4caa51744218c30cb13c9366259728889142382f8bdae69daf6459da472f3`.

R6 adds only the hash-bound Ubuntu Noble `strace` and `libunwind8` package
bytes needed for campaign-local extraction. It does not install packages into
the worker image or contact a package registry. It preserves the narrow
`PROCESS_TREE_OBSERVED_ZERO_EXTERNAL_EGRESS` claim and makes no network
namespace, firewall, or packet-denial claim.
