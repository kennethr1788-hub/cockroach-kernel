# S3 Local Preflight Receipt R1

- `STATUS`: `LOCAL_PREFLIGHT_GREEN_PENDING_INDEPENDENT_JUDGES`
- `UTC_RECORDED`: `2026-07-26T23:12:11Z`
- `LAST_AMENDED_UTC`: `2026-07-27T00:35:00Z`
- `AMENDMENT_NOTE`: `CURRENT_R3_FIELDS_ADDED_AFTER_ORIGINAL_EVIDENCE_TIME`
- `P9_CLOUD_REGRESSION_SUBSET`: `113_OF_113_GREEN`
- `P9_PARENT_TOTAL_AT_P9_GATE`: `229_OF_229_GREEN`
- `S3_UNIT_TESTS`: `12_OF_12_GREEN`
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
  `8512d0af41630eee31ba7ebf367eb7ff6eeb23f9b3d884c4dd1a83fe88879b11`;
- normal case: guard exited GREEN without stopping the fake worker;
- stale/failure case: guard emitted a stop marker and deleted the exact fake
  worker;
- bridge-terminal-tail case: a hash-valid terminal `BRIDGE_GREEN` log remained
  static beyond the stale window while the other guarded logs advanced; the
  guard did not misclassify that completed process as stale and reached only
  the deliberately accelerated test deadline.

## Bundle proof

- worker archive: 144,503,519 bytes, SHA-256
  `c0f0514c09d63da833361ec34ef2cbc2f0e96c210fca043cbc7d3c33a8e703d4`;
- worker tree manifest SHA-256:
  `21e068263d0724ce9d9e73293ff4540b09fc44bcfdbada16fea455b49643ddd5`;
- host archive: 56,468 bytes, SHA-256
  `97357e45e8eba6e7763c8f493cb30f228ecb5ad8a552b9c7f71c1e4bc567f8c8`;
- host tree manifest SHA-256:
  `5c736027fb3d33e3f96cb1b6fcd769d7eec2455700c460a3198c7c2cb71a98a5`;
- host `gitleaks`: zero;
- host `detect-secrets`: zero;
- host private-path/key scan: zero;
- worker `gitleaks`: zero;
- worker `detect-secrets`: zero;
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
