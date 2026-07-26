# S2 Replacement Lifecycle Preflight Exact Judge Packet R1

- `PHASE`: `S2_REPLACEMENT_PREFLIGHT`
- `TARGET_GATE`: authorize one bounded replacement campaign under an
  eight-attempt pre-timer retry envelope
- `IMPLEMENTATION_COMMIT`: `58bf07b8801aad569b0c050d097310af2509d9be`
- `GIT_STATUS_AT_FREEZE`: clean before packet creation
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `REPLACEMENT_AUTHORIZATION_SHA256`: `7661fd8de8284cfd69dfcf584f05e6b0584bb736047e626d594a4595047e486e`
- `CAMPAIGN_ID`: `CK-S2-20260726-ORCHESTRATION-R2`
- `REQUIRED_JUDGES`: GLM and Claude Opus 4.8 over this same exact packet

## Decision

Return GREEN only if this packet provides a bounded, fail-closed basis to
create sequential CPU workers, complete the Linux smoke, start exactly one
21,600-second S2 workload, retrieve evidence, and teardown without touching
unrelated resources. No worker may exist before both judges are validly GREEN
on this packet's exact out-of-band SHA-256.

Judges return findings only. Code, patches, commands, repair plans,
implementation direction, tools, browsing, credentials, deployment, and public
actions are forbidden.

## Preserved parent and prior-attempt evidence

- `CK_P5_LANES_GREEN`, packet
  `985d1aa4fcd8ff8776ba997711aec35afecab1555bcdda5a91cd2de83e326cb8`.
- `CK_P6_QUORUM_GREEN`, packet
  `7c887c71aae6c7dffebd95a1fa793261d6ddf7567c3a30e90b46fe1cceae2c10`.
- `CK_P7_RECOVERY_GREEN`, packet
  `e28eb35f7629fd9b35beeb8c177bc4d307bc4d4b227d92d58c91320fcd78f417`.
- Prior S2 lifecycle-preflight packet R3:
  `f99a5deda6715fe50a186420594d5797820fe263e06e1b9d5c420a91a5abf6b8`,
  independently GREEN from GLM 5.2 and Claude Opus 4.8.
- Prior attempt Pod `btdc8bhvws6cbs` is deleted. Exact-ID lookup was absent,
  S2 inventory was empty, and its lifecycle guard terminated GREEN.
- Prior calculated maximum: `$0.003825`; provider itemization returned `[]`.

The prior worker, archive, manifest, and extracted binary were valid. The
executor manually compared against a stale summarized binary hash and deleted
the worker. This is preserved as `EXECUTOR_USED_STALE_BINARY_HASH_AFTER_UPLOAD`,
not a product/runtime failure. The replacement authorization supersedes the old
no-replacement rule within the limits below.

## Machine-readable hash custody

`S2_RUNTIME_HASHES_R1.json` is canonical JSON, 1,327 bytes, SHA-256
`5cbd3a2174ab19d1a33ab21546e7fc4fe0bbc896cbc75f7b2b32f26823588e7c`.

```json
{"created_utc":"2026-07-26T02:58:49Z","linux_cockroach_archive":{"sha256":"3eca6d7bc6fefa3ba0847e89733fc69f61226c80b8fab0af6578e1be672f27d3","source":"p2-cleanroom/vendor/cockroach-v26.2.3-linux/cockroach-v26.2.3.linux-amd64.tgz"},"linux_cockroach_binary":{"sha256":"97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f","source":"clean extraction of p2-cleanroom/vendor/cockroach-v26.2.3-linux/cockroach-v26.2.3.linux-amd64.tgz"},"replacement_authorization":{"sha256":"7661fd8de8284cfd69dfcf584f05e6b0584bb736047e626d594a4595047e486e","source":"/Users/kennethruedas/Documents/Codex/2026-07-18/read-and-execute-the-prompt-afterlife/COCKROACH_KERNEL_S2_REPLACEMENT_EXECUTION_PROMPT_20260725_R1.md"},"s2_lifecycle_guard":{"sha256":"4644aa756f47c3d53b82c239657ce22605d4a9caab3e6a8651c4f459d95c6f0c","source":"s2-soak/lifecycle_guard.py"},"s2_run_soak":{"sha256":"b4b788b59f7ab95358251623ef89088c4c31c218a431f6d240b7980f9f81d01c","source":"s2-soak/run_soak.py"},"schema_version":"s2-runtime-hashes-v1","transfer_archive":{"sha256":"f080f48a7c68271af067b751ca8943ffa5c9d3350be33e3382c81cad46a9f2eb","source":"/tmp/ck-s2-replacement-r1.tar.gz"},"transfer_manifest":{"line_count":61,"sha256":"c3cc695f261bfef6a1ccbd8aa86e688d4f9bcdb06c2361cd50dbcb9ec96cd1c0","source":"/tmp/ck-s2-replacement-payload-r1.manifest.sha256"}}
```

The rebuilt tree has the same 61-file manifest hash as R3. The new tarball
omits macOS extended attributes and therefore has a new container hash. A clean
local extraction reproduced binary SHA-256
`97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`
and 326,015,464 bytes, then removed the extraction root.

Every expected local/remote verification value must be parsed from this exact
JSON at command construction. Manually typed, recalled, chat-derived, or
model-summarized expected hashes are forbidden.

If a pre-timer comparison fails, setup stops but the worker may remain for at
most ten diagnostic minutes inside its rate/deadline envelope. The executor
must reparse the JSON and recompute local archive, local extraction, remote
archive, and remote binary hashes. If bytes agree and only the command's value
was wrong, preserve `EXECUTOR_COMMAND_CONSTRUCTION_ERROR`, repair only command
construction, and continue on the same worker. A genuine byte mismatch blocks
after retrieval and teardown.

## Transfer and scanners

- Archive: `/tmp/ck-s2-replacement-r1.tar.gz`
- Archive bytes: `144469491`
- Archive SHA-256:
  `f080f48a7c68271af067b751ca8943ffa5c9d3350be33e3382c81cad46a9f2eb`
- Manifest: `/tmp/ck-s2-replacement-payload-r1.manifest.sha256`
- Manifest lines: `61`
- Manifest SHA-256:
  `c3cc695f261bfef6a1ccbd8aa86e688d4f9bcdb06c2361cd50dbcb9ec96cd1c0`
- Symlinks: `0`
- Private/absolute path patterns: `0`
- Gitleaks: `0`
- Detect-secrets: 32 `Hex High Entropy String` findings, all expected
  64-character synthetic receipt/hash fields in JSON fixtures; no credential,
  private-key, provider-key, or non-hash secret class.

The transfer contains only hash-bound P3-P7 source, migrations, synthetic
fixtures, S2 workload/README, and the verified Linux CockroachDB archive. It
contains no lifecycle credential, HOME state, live memory, Qdrant, StateV2,
launchd, cron, AWS, CockroachDB Cloud credential, production/client data,
unrelated source, persistent volume, or public action.

## Worker and spend envelope

- CPU only, zero GPUs.
- Official template: `runpod-ubuntu-2204`.
- Exact image: `runpod/base:1.0.2-ubuntu2204`.
- Container disk: at most 20 GB.
- Persistent/network volume: zero.
- Maximum simultaneous S2 workers: one.
- Accepted shapes: exactly 2 vCPU/4 GiB at <=$0.06/hour compute or exactly
  2 vCPU/8 GiB at <=$0.08/hour compute.
- Maximum active rate including disposable storage: `$0.085/hour`.
- Maximum aggregate S2 exposure including prior attempt: `$2.00`.
- Maximum replacement attempts: eight.
- Maximum successful-worker paid lifetime: 28,800 seconds.
- Maximum six-hour workload attempts: one.

The CLI does not expose a pre-create CPU quote. Creation response plus exact-ID
lookup are authoritative. Any returned shape/rate/image/disk/volume/GPU/name or
deadline mismatch is deleted before upload.

Verified RunPod CLI:

- path `/tmp/runpodctl-v2.7.2-darwin-arm64`;
- version `2.7.2-309512b`;
- SHA-256
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`.

Current provider state has no S2 worker. One unrelated running worker and one
unrelated network volume exist. They are exact-ID out of scope and must not be
stopped, attached, counted, or modified.

## Exact attempt schedule

Schedule JSON SHA-256:
`dc766db950cd39fe81bc0bd6c39b63be07c72ade677b88f7ae7a489eaaea2e39`.

| Attempt | Create window UTC | Stop UTC | Terminate UTC |
|---|---|---|---|
| a01 | 03:20–03:30 | 11:10 | 11:20 |
| a02 | 03:30–03:40 | 11:20 | 11:30 |
| a03 | 03:40–03:50 | 11:30 | 11:40 |
| a04 | 03:50–04:00 | 11:40 | 11:50 |
| a05 | 04:00–04:10 | 11:50 | 12:00 |
| a06 | 04:10–04:20 | 12:00 | 12:10 |
| a07 | 04:20–04:30 | 12:10 | 12:20 |
| a08 | 04:30–04:40 | 12:20 | 12:30 |

Date for every table time is `2026-07-26`. Attempt names are
`ck-s2-20260726-r2-a01` through `a08`. `CAMPAIGN_READY` deadline is
`2026-07-26T04:50:00Z`. Missed slots are not shifted.

Provider-native stop and terminate timestamps are preserved in every creation
request. A detached host-local exact-ID guard binds Pod ID, expected name,
campaign prefix, verified CLI path/hash, and deadlines; runs under `screen` and
`caffeinate`; emits a hash chain; rejects mismatch; and requires exact-ID
absence plus empty S2-scoped inventory for teardown GREEN. No lifecycle
credential enters the worker.

## Retry law

Retry authority exists only before the six-hour production process starts.
Every earlier worker must be deleted and proved absent before another exists.
Post-upload replacement is allowed only for transient creation/capacity,
returned-property mismatch, readiness/SSH/transfer, detached-guard,
transfer-interruption, transient extraction/dependency, infrastructure-only
Linux smoke, or mechanically proved executor-command-construction failure.

Payload changes require a new packet and both judges. Genuine byte mismatch,
secret/private exposure, egress, product assertion failure, evidence schema or
chain defect, unknown cost, teardown uncertainty, forbidden state access,
judge failure, or any six-hour workload start/failure is non-retryable.

Every failed attempt receives a lifecycle receipt, retrieval, exact deletion,
exact-ID absence, empty S2 inventory, billing query or calculated maximum,
residue proof, cumulative exposure update, and bounded backoff. Three identical
failures stop blind retry and require local diagnosis plus a new same-hash
GLM/Claude gate for any load-bearing correction.

## Remote smoke and production

After transfer and hash verification, run a 60-second Linux smoke in a unique
smoke root. Production uses a different, fresh root. The smoke exercises Linux
`/proc` RSS/open-file checks, non-loopback socket detection, loopback-only
CockroachDB with diagnostics disabled, all five lanes, quorum/refusal vectors,
transaction/duplicate behavior, recovery/quarantine/replay/interruption,
rollback/restart, evidence streams, and residue cleanup.

Only smoke GREEN plus worker/guard/price/hash evidence creates
`CAMPAIGN_READY`. Retry authority ends when production starts.

Production is immutable:

- exactly 21,600 actual test seconds;
- exactly 72 checkpoints at 300 seconds;
- exactly 24 safety replays at 900 seconds;
- exactly six hourly summaries at 3,600 seconds;
- database growth <=536,870,912 bytes;
- evidence growth <=134,217,728 bytes;
- RSS <=2,147,483,648 bytes;
- open files <=512;
- every P5 lane, P6 approval/refusal, P7 recovery/refusal/replay/interruption,
  retry/duplicate, rollback/restart, deterministic verdict, and real quarantine
  exclusion path exercised;
- separate workload, telemetry, receipt, manifest, and database bytes;
- no private path, secret, or undeclared egress.

There is no restart or replacement after production begins.

## Retrieval and teardown

Flush/fsync and retrieve all raw evidence plus remote manifest/tree hash before
deletion. Verify the complete local tree against remote hashes. Delete the
exact worker, prove exact-ID absence and empty S2-scoped running/all-status
inventory, verify no S2 SSH/transfer/screen/guard/child/database/watchdog,
volume, IP, or paid process remains, and run residue/symlink/private-path/
credential/gitleaks/detect-secrets scans.

Delayed provider billing itemization may be labeled `CALCULATED_MAXIMUM` only
when returned rate, exact timestamps, deterministic upper bound <=$2.00, and no
residual resource are proved. Unknown rate/lifetime/residue remains blocking.

## Final gate boundary

This packet authorizes lifecycle start only. Final S2 GREEN still requires the
full six-hour evidence and GLM, Claude, and AGY valid GREEN over one exact final
packet hash. P8 remains `NOT_STARTED`; Band B remains `OPEN`.

## Required verdict schema

```text
ROLE:
ARTIFACT: S2_REPLACEMENT_PREFLIGHT_PACKET_R1.md
BUILDER_AND_INFLUENCE_DISCLOSURE:
PACKET_SHA256: <exact hash supplied out-of-band>
VERDICT: GREEN | BLOCKED | NOT_GREEN | INSUFFICIENT_EVIDENCE | RECUSAL_REQUIRED
FAILED_CRITERIA:
EVIDENCE:
FAILURE_MECHANISM:
MISSING_PROOF:
NON_BLOCKING_RISKS:
RECUSAL_CHECK:
```
