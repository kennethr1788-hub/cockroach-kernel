# S2 Runtime Hash Custody Receipt R1

- `UTC_CREATED`: `2026-07-26T02:58:49Z`
- `SOURCE_COMMIT`: `1247dde65205949afd07f0562aadee4ca249d8e6`
- `AUTHORIZATION_SHA256`: `7661fd8de8284cfd69dfcf584f05e6b0584bb736047e626d594a4595047e486e`
- `TRANSFER_ARCHIVE_SHA256`: `f080f48a7c68271af067b751ca8943ffa5c9d3350be33e3382c81cad46a9f2eb`
- `TRANSFER_MANIFEST_SHA256`: `c3cc695f261bfef6a1ccbd8aa86e688d4f9bcdb06c2361cd50dbcb9ec96cd1c0`
- `TRANSFER_MANIFEST_LINES`: `61`
- `LINUX_RUNTIME_ARCHIVE_SHA256`: `3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`
- `LINUX_RUNTIME_BINARY_SHA256`: `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`
- `LINUX_RUNTIME_BINARY_BYTES`: `326015464`
- `RUN_SOAK_SHA256`: `b4b788b59f7ab95358251623ef89088c4c31c218a431f6d240b7980f9f81d01c`
- `LIFECYCLE_GUARD_SHA256`: `4644aa756f47c3d53b82c239657ce22605d4a9caab3e6a8651c4f459d95c6f0c`

The rebuilt payload contains the same 61 source bytes as R3. The sorted tree
manifest hash is unchanged. The rebuilt tarball excludes macOS extended
attributes, so its container hash is new and explicitly bound here.

Local clean extraction independently reproduced the authoritative Linux binary
hash and removed its temporary extraction root. Runtime comparisons must parse
`S2_RUNTIME_HASHES_R1.json` at command execution time. Recalled, manually typed,
or model-summarized hashes are forbidden as expected values.

Scanner results:

- symlinks: zero;
- absolute/private path patterns: zero;
- gitleaks: zero findings;
- detect-secrets: 32 expected `Hex High Entropy String` findings, all in
  synthetic JSON receipt/hash fields; no credential rule or non-hash secret
  class;
- credential or private-key material: zero.
