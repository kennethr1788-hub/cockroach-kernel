# S3 Local Preflight Receipt R1

- `STATUS`: `LOCAL_PREFLIGHT_GREEN_PENDING_INDEPENDENT_JUDGES`
- `UTC_RECORDED`: `2026-07-26T23:12:11Z`
- `P9_REGRESSION_TESTS`: `113_OF_113_GREEN`
- `S3_UNIT_TESTS`: `7_OF_7_GREEN`
- `GIT_DIFF_CHECK`: `GREEN`
- `RUNPOD_S3_SCOPED_INVENTORY`: `[]`

## Fresh-root live proof

| Trial | Status | Cadence | Cloud calls | CRDB operations | Raw aggregate SHA-256 |
|---|---|---:|---:|---:|---|
| r3 | GREEN | 6 / 4 / 2 | 2 | 18 | `1aba25d7540030198d5fce0986ba71577b24fd1be9aa48bca95a2c31940f4649` |
| r4 | GREEN | 6 / 4 / 2 | 2 | 18 | `6ad178c6e49e70d75e455b858b0443fc53c9a2f2cf4226dd346463d2eef5e607` |

`6 / 4 / 2` means checkpoints / safety replays / hourly summaries. Across the
four calls, coordinator latency was 6,677–11,530 ms, Cockroach path latency was
2,362–3,445 ms, Lambda latency was 997–2,474 ms, vector latency was 571–794 ms,
each changefeed restart proof returned two identical request rows, and backlog
was zero. These values are below the already frozen thresholds.

The post-smoke fixed cleanup readback found zero tasks, workers, and
projections. Its bounded receipt hash is
`47b86c80d38bf68ffafa22c7b9cc430b427d384c60a373a6ebde196cb3df49d4`.
No related local coordinator, worker, or database process remained.

## Refusal and guard proof

- forced offline refusal raw aggregate SHA-256:
  `6682a7332fe720df1ee774d5745cbbb0ccf22bee816084cbb78de871a954b656`;
- result: `EXPECTED_REFUSAL:COORDINATOR_UNAVAILABLE`;
- cloud calls: zero;
- updated coordinator-guard proof SHA-256:
  `703075d8f6595cf4067049789350e020ac49da365ea49a4af965666cee894468`;
- normal case: guard exited GREEN without stopping the fake worker;
- stale/failure case: guard emitted a stop marker and deleted the exact fake
  worker.

## Bundle proof

- worker archive: 144,500,645 bytes, SHA-256
  `51df007f8ffc79b164e5b3b6e0e95115e2fc57b8f2efff4de19992eb6c117cd0`;
- host archive: 52,718 bytes, SHA-256
  `c37fd8eb605b469b09950b10959c4edc29bbc998b9fc7925a344fb2964445e4d`;
- host tree manifest SHA-256:
  `401979ae5d02ba9f5ecdaeec5fc936458e75dd356fc2c7af271acbb7dccc9635`;
- host `gitleaks`: zero;
- host `detect-secrets`: zero;
- host private-path/key scan: zero;
- worker `gitleaks`: zero;
- worker `detect-secrets`: 36 classified findings in 27 inherited synthetic
  fixture files, all fixed SHA-256 test values; no credential or auth artifact;
- worker private-path/key scan: zero.

The Linux CockroachDB archive SHA-256 is
`3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3`;
the extracted binary SHA-256 is
`97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`.

## Cloud credential boundary

AWS CLI v2.36.8 was unpacked project-locally from the official signed package;
no global install or HOME AWS configuration was created. The CLI binary
SHA-256 is
`133ba61b0c2669053e62e8ae6bb46ff66faf32fd08c372b78f780cb392c4f46c`.
Its short-lived login cache, CockroachDB CA, live config, and SQL password
lookup remain ignored local runtime material. They are excluded from bundles,
Git, packets, and RunPod. The SQL password is retrieved only into a child
process environment from the existing Keychain entry and is never printed or
stored in an evidence artifact.

No RunPod worker was created during this preflight.
