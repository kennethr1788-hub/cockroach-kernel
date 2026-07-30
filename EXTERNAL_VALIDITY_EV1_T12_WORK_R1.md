# EV1-T12 Work R1

- `STATUS`: `EV1_T12_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED`
- `TASK_ID`: `EV1-T12`
- `TASK_COMMIT`: `62b3f01f00544ba618a04ea8935908de8b038bb4`
- `WORK_FILE_SHA256`: `c20b9cfffa6a40cfb682a351184e13cb41bf404cc5f09ac630e6cde1db749df4`
- `WORK_RECEIPT_SHA256`: `69cc45764a10433bd9070b982c2378445fd36e095fba511e925cd1026d393359`
- `COMMITTED`: `scripts/build-release-manifest.mjs`
- `MODIFIED`: `docs/RELEASE.md`
- `UNTRACKED`: `scripts/build-release-manifest.test.ts`
- `HUMAN_EDIT_REQUIRED`: `FALSE`
- `SYNTHETIC_BINARY_FIXTURES_ONLY`: `TRUE`
- `NETWORK_OR_PROCESS_CODE_PRESENT`: `FALSE`
- `RELEASE_UPLOAD_SIGNING_REGISTRY_ACTIONS`: `0`
- `PRETTIER`: `GREEN`
- `TARGETED_TESTS`: `8_OF_8_GREEN`
- `DETERMINISM`: `5_OF_5_BYTE_IDENTICAL`
- `MANIFEST_SHA256`: `e59b9f359e2da8c52644e6a7d5558e35c17035e19978c8055daa6110de376057`
- `PRIVATE_MARKER_MATCHES`: `0`
- `TEMPORARY_RESIDUE_PATHS`: `0`
- `CAPTURE_STARTED`: `FALSE`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`

## Declared file hashes

- `docs/RELEASE.md`: `8ea051ff477c04d7becafb53fa970f9973875d67211ea2ae7c390ba4050d1fee`
- `scripts/build-release-manifest.mjs`: `1aa1561692cba73683d00cb0991971e04a6ae9f70101c0b5093ee47eb2d9c40a`
- `scripts/build-release-manifest.test.ts`: `01b0d4eaf0e0794e4b5d5224932a75186613e6f36f667681950255e9f9e69941`

The generator emits canonical platform-sorted SHA-256 manifests, rejects
duplicate platform labels, unsafe paths, symlinks, malformed labels, and
unknown fields, and performs no release or external action. Capture, deletion,
and recovery remain blocked until Kenneth declares this exact state and the
task-specific local and independent pre-execution gates pass.
