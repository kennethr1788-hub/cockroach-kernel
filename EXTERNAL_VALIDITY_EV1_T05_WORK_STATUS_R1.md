# EV1-T05 Work Status R1

- `STATUS`: `EV1_T05_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED`
- `TASK_ID`: `EV1-T05`
- `TASK_START_UTC`: `2026-07-30T18:43:12Z`
- `WORK_RECORDED_UTC`: `2026-07-30T18:47:15Z`
- `BACKLOG_SHA256`: `6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `SOURCE_COMMIT`: `2c088ba8599c75cb02fbd61dfcf259d000729131`
- `SOURCE_MANIFEST_SHA256`: `26e53d4658adac171e17796a07bc09e03d0f19e125aa4d599267200996add79d`
- `DEPENDENCY_LOCK_SHA256`: `7e0238617f56ecd9ab4c99bcc6d41a8a7e4c2635707c19247ddf082b94eacd7a`
- `PREPARATION_FILE_SHA256`: `43836cc3bb9a6f8cfdd730c1c199cbe165a79b8d4afd73c2ebf842eac82c701f`
- `PREPARATION_RECEIPT_SHA256`: `5236b6f4e65195579f54976e1cf76ac4e61be332650f654aa69000d1e49f893a`
- `TASK_COMMIT`: `63f151a50d6e4b28cc2091f22c045d785c0261c1`
- `WORK_RECEIPT_FILE_SHA256`: `417323949ead439e9dd42aa2343fe607edd3a3f6cb25475f8382245b8994cf98`
- `WORK_RECEIPT_SHA256`: `bb312c593c1a1b41ca6b2c4dbce6bdc36b459ae787328d94a6a6451e8d999928`
- `CAPTURE_STARTED`: `FALSE`
- `DELETION_STARTED`: `FALSE`
- `RECOVERY_STARTED`: `FALSE`

## Exact task state

- committed: `lib/signalSchema.ts`, `scripts/run-signal-schema.mjs`
- modified tracked: `lib/signals.ts`, `package.json`
- untracked: `scripts/signal-schema-cases.cjs`
- aggregate declared bytes: `5402`
- private-marker matches: `0`

## Offline acceptance

- strict schema suite: `PASS`, eight adversarial cases plus the actual 12-record dataset, log SHA-256 `229c21d068f1496925f83d8331ccffca76c474f9f516169ff05a3fd808701ae4`
- typecheck: `PASS`, log SHA-256 `8c0af875a1ab948857b68d4f22b66e9bce86deedfdf47d7ba6ea1d528e01bbda`
- production build: `PASS`, log SHA-256 `94e24c8e6c8a0f3e4994e2ae4c842d0605ad5e89feb9a832de07fa9132009226`
- five deterministic schema-suite repetitions: `PASS`, byte-identical log SHA-256 `229c21d068f1496925f83d8331ccffca76c474f9f516169ff05a3fd808701ae4`
- verifier profile: `/usr/bin/sandbox-exec` with `(deny network*)`, SHA-256 `5c358b8d847211333e7ba22df82d84f796b5f30a41a2682209a949d783adbd08`

The runtime loader no longer uses the unchecked `as Signal[]` cast. It parses
the JSON through a strict Zod schema before analysis and rejects duplicate IDs,
invalid sources, malformed or impossible timestamps, whitespace-only titles,
non-array tags, and unknown fields. The actual frozen sample dataset also passes
through the parser.

The source commit had no lockfile. Preparation Attempt 1 froze a 119-entry npm
graph with lifecycle scripts disabled but exposed that Next 16 Turbopack binds
an internal port and is incompatible with the fixed offline profile. R2 reused
that exact lock and cache without network, froze the official webpack build mode
and Next's mandatory TypeScript adaptation into the disposable baseline, and
then passed the complete baseline offline. The earlier unexpected npm HOME log
is preserved and remediated; it is not hidden or counted as a task result.

The next protocol step is Kenneth's exact capture declaration. Capture, guarded
deletion, recovery, and any task verdict remain forbidden until that human-only
declaration is recorded and the task-specific same-packet independent preflight
passes.
