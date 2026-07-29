# Hardening Gate 7 Run 3 Local Gate Receipt R1

- `STATUS`: `GATE7_RUN3_LOCAL_REPAIR_GREEN`
- `UTC_CREATED`: `2026-07-29T01:27:26Z`
- `REPAIRED_SOURCE_COMMIT`: `c8383c61cd599d10b02d861aabc764686a81d766`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `NEXT_GATE`: `RUN3_SAME_HASH_GLM_AGY_PREFLIGHT`
- `RUNPOD_CREATION`: `FORBIDDEN_UNTIL_BOTH_PREFLIGHT_JUDGES_GREEN`
- `HIDDEN_SEED`: `ABSENT; CREATION_FORBIDDEN_BEFORE_CAMPAIGN_READY`

## Complete local 46,000-row trial

An isolated project-local CockroachDB v26.2.3 runtime completed the repaired
workload:

- tasks: `2,000/2,000`;
- trajectory events: `20,000/20,000`;
- receipts: `4,000/4,000`;
- vectors: `20,000/20,000`;
- SQL batches: `184/184`;
- recovered SQLSTATE `40001` serialization retries: `22`;
- vector queries: `200/200`;
- observed query p99: `450 ms`;
- result: `GREEN`;
- cleanup: `PASS`;
- final residue: `0,0,0,0`.

The hash-chained journal contains 451 records. Its chain, canonical result,
terminal link, cleanup receipt, and zero-residue state were independently
recomputed locally.

- `RESULT_FILE_SHA256`: `fd0bae539f09440c5bb511a7cdb8c5dbdd7f927f8c1c146d34ac95ce73f364fe`
- `RESULT_SHA256`: `2c3d69f819d83505bf74218cd82398d2ac4933bd6024c636c870c421fc736550`
- `TERMINAL_FILE_SHA256`: `3e858bc41b265d87fd5cf09d95e16bc99c61a69099948ea84c910a577733c047`
- `TERMINAL_RECEIPT_SHA256`: `e574e17eabd03688347cce1360638952462179aaeb4315e6e85e3dbeda3dc0ea`
- `CLEANUP_FILE_SHA256`: `dc275ec836f2ddc000efe922ff3d4a6264dfddcd0282cedb11db940ccee03659`
- `CLEANUP_RECEIPT_SHA256`: `f7c3fe0d9a80b336d0b2c57fb9e0eb5bd44d92de87d93019458851052f2a6d02`
- `JOURNAL_FILE_SHA256`: `4ac029319b9bc920e7c6282da5ce31c876c5aeb9954aa043668ff1ff1ad3c357`
- `JOURNAL_TERMINAL_HASH`: `7115956a3812e9e526871228da961c819236896e798ab95778d3c1972152a19c`

Raw synthetic evidence remains under
`.hardening-runtime/gate7-r3/local-full-r1/`.

## Regression suites

- Gate 7 suite: `18/18 PASS`.
- S3 protocol/hardening suite: `18/18 PASS`.
- Python compilation: `PASS`.
- `git diff --check`: `PASS`.

The tests include exact Run 2 collision reproduction, 20,000 unique repaired
digests, SQLSTATE `40001` bounded retry, non-retryable `23505`, partial insert
cleanup, interrupted controller, missing terminal receipt, helper archive
tamper cases, deterministic generation, and complete campaign invariants.

## Deterministic archive and extracted-bundle proof

Two fresh archive builds were byte-identical:

- `TRANSFER_ARCHIVE_SHA256`: `d0a47c311ad14f16e1bed2df181bb3d6885accf155be7322a67829c201023b28`
- `PAYLOAD_TREE_FILE_SHA256`: `d21bf5c262f30049e29d31ee89d817bc4ee9755f3c76578e30739c90729c36bb`
- `TRANSFER_MANIFEST_FILE_SHA256`: `ec2e0da16a68b965301cde70a5d2eb28054d67ee6af617f0a7ef9549d026361c`

The controller executed from each extracted archive and generated identical
184-batch manifests with 20,000 unique vector digests:

- `GENERATED_MANIFEST_SHA256`: `e54bfcf8845c768775888c123e0986ad40235043be054f2be9ee8d458ae1bf63`

The packaged manifest helper was imported from each extracted archive and
invoked against equivalent isolated local evidence roots. Both outputs were
byte-identical and each matched an independently generated, byte-sorted
`find`/`shasum` comparator:

- `PACKAGED_HELPER_OUTPUT_SHA256`: `11050b4db98ed4c0a6f5c8df5bbc376ca61e41ef2bd1eb9f68b192c7c143f50b`
- files: `2`;
- source bytes: `39,562`;
- self-exclusion: `PASS` because the output resides in the required parent
  directory, outside the evidence root.

The helper's production-path guard remains unchanged. The local invocation
rebound only its regular expression to the exact isolated local root; the
remote extracted-bundle canary must invoke the unchanged packaged CLI under
the frozen `/workspace/ck-s3-*/production` path before `CAMPAIGN_READY`.

## Candidate scans and teardown

- exact `rg` private-path/credential-pattern hits: `0`;
- gitleaks findings: `0`;
- detect-secrets findings: `38`, all reviewed `Hex High Entropy String` values;
- 36 findings are 64-character canonical digests;
- 2 findings are the pinned 40-character product/original commit identifiers;
- credential-type findings: `0`;
- local CockroachDB process: `ABSENT`;
- Screen session: `ABSENT`;
- SQL/listen/HTTP ports `26327/26328/8098`: `CLOSED`;
- HOME, Qdrant, StateV2, launchd, client, private, and production mutation:
  `NONE`.

- `GITLEAKS_REPORT_SHA256`: `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`
- `DETECT_SECRETS_REPORT_SHA256`: `789b5d6458387f714612e95decb4d511ff8837208175c42faaa8204987553a29`

## Gate result

Both Run 2 defects are directly closed locally. Gate 7 remains OPEN. A new
frozen packet and same-hash exact-model GLM 5.2 plus AGY preflight must both
return GREEN before any RunPod worker is created. Run 2 evidence remains
historical and unchanged.
