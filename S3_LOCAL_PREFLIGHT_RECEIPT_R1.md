# S3 Local Preflight Receipt R1

- `STATUS`: `LOCAL_PREFLIGHT_GREEN_PENDING_INDEPENDENT_JUDGES`
- `UTC_RECORDED`: `2026-07-26T23:12:11Z`
- `P9_REGRESSION_TESTS`: `113_OF_113_GREEN`
- `S3_UNIT_TESTS`: `9_OF_9_GREEN`
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

- worker archive: 144,500,700 bytes, SHA-256
  `5c33c443e8e4d0e0b8c6c539ddd94c4c291625a73e4c257daec5fc69ae38140f`;
- worker tree manifest SHA-256:
  `c3d7613ce0d06031e2e3a11e692e7c707431328b740a8b92fabc51b96b479793`;
- host archive: 54,288 bytes, SHA-256
  `b1f49a1df501c56a46eec7b35772ef190a1807b3cf40d84b3ece411bccfc3ff5`;
- host tree manifest SHA-256:
  `98b31d0bb095d74e328161688466a63ab9552d52e75b32ee4ea75d4c511fe083`;
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
