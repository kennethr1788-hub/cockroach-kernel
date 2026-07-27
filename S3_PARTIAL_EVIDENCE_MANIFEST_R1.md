# S3 Partial Evidence Manifest R1

- `CLASSIFICATION`: `QUALIFIED_HARDENING_INPUT`
- `S3_RESULT`: `CK_S3_BLOCKED`
- `BLOCKER`: `AWS_AUTH_SESSION_EXPIRED_DURING_EXCHANGE_12`
- `LAST_GREEN_GATE`: `CK_P9_INTEGRATION_GREEN`
- `SOURCE_COMMIT`: `bf0040fd56c8e3b2665f1fb2412b0cee66da5d19`
- `S3_CONTRACT_SHA256`: `7628f6fc18b297f9c756ea4739590598aec47ab39a48d857b4ea35f2643de068`
- `S3_PRODUCTION_START_RECEIPT_SHA256`: `8ae61ad6fdce451a008d372f99b73cef00343babdd30cff832db755169e99a7c`
- `UTC_FROZEN`: `2026-07-27T16:23:59Z`

## Proven results

- canonical requests received: `12`;
- canonical results completed: `11`;
- successful `RUN_PROMOTE` exchanges: `6`;
- successful `RUN_REFUSE` exchanges: `5`;
- successful AWS Lambda invocations: `11`;
- successful CockroachDB operations: `99`;
- coordinator backlog: `0` for every completed exchange;
- coordinator latency: minimum `7897 ms`, median `9504 ms`, mean
  `9465.2 ms`, maximum `10395 ms`;
- RunPod exact-ID teardown: `GREEN`;
- active RunPod inventory after teardown: `[]`;
- canonical chain validation: coordinator, bridge, coordinator guard, and
  lifecycle chains independently parse and validate through their frozen tails.

## Frozen evidence roots

All paths below are relative to `.s3-runtime/attempt-a04/` and remain private
execution evidence. They are not public-package paths.

| Evidence class | Files | Aggregate SHA-256 |
|---|---:|---|
| `production/bridge/requests/*.json` | 12 | `a378e420d85ce80d0cff5aba9a1dd0510c9816d8bf76dd408e4f763a4d4c4cb9` |
| `production/bridge/results/*.json` | 11 | `f26b53e597c18fb133960b28cd116dae05ee6aa4ae9e93f2ed1cea4963d0a2f1` |
| `production/coordinator-evidence/call-*/summary.json` | 11 | `7df846c6e6562aa3bebb330798574648a52031c0036efea757988dc0b23da21e` |

Aggregate hashes are SHA-256 over newline-terminated, lexicographically sorted
`<file-sha256><two spaces><path relative to attempt-a04>` entries.

## Critical custody hashes

| Path relative to `.s3-runtime/attempt-a04/` | SHA-256 |
|---|---|
| `production/coordinator-evidence/coordinator.ndjson` | `a8604ce69def468675d7c01de3d2b424733405e05a9de146b0eb17d11f945b39` |
| `production/bridge.ndjson` | `10505a9cf5575ebf973d618e70b8fad5eabbd92504c5d246bda97d6c0f35de44` |
| `production/coordinator-guard.ndjson` | `0253caf102cfb732331341522fdc829b140dfb6609d5c5e1c49a91190a8c4b87` |
| `lifecycle.ndjson` | `a547caf36736c528185180377dac4fd4cf32e979300b32263639c37f24358549` |
| `production/stop.json` | `b47d5ac5c6f3bda9f516b8174902b94621105bf3b6af849b3ebeaf462efe3334` |

## Chain tails

- coordinator: `7884` records, terminal event `COORDINATOR_BLOCKED` at
  `2026-07-27T14:40:44Z`;
- bridge: `1511` records, frozen at heartbeat sequence `1511` at
  `2026-07-27T16:22:18Z` after the already-deleted worker could no longer
  return result 12;
- coordinator guard: `7798` records, terminal lifecycle action
  `DELETE_ATTEMPT` at `2026-07-27T14:40:48Z`;
- RunPod lifecycle guard: `1199` records, terminal event `TEARDOWN_GREEN` at
  `2026-07-27T14:41:19Z`.

## Explicit limitations

This packet does not prove a twelve-hour S3 pass, result 12, 144 remote
checkpoints, 48 remote safety replays, 12 hourly summaries, final remote
resource measurements, or a retrieved final remote evidence manifest. Those
claims remain forbidden. This packet may support the Hardening Run, comparative
testing, and the public claim that eleven scheduled live exchanges passed
before the system failed closed and deleted its disposable worker.
