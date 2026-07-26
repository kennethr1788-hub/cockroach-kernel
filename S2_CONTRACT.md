# S2 Frozen Local and Remote Contract

- `PHASE`: `S2`
- `PARENT_GATE`: `CK_P7_RECOVERY_GREEN`
- `START_COMMIT`: `42170e14fd52056691978c02b8b5759bc67956d5`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `TARGET_GATE`: `CK_S2_RECOVERY_SOAK_GREEN`
- `STATUS`: `FROZEN_BEFORE_REMOTE_EXECUTION`
- `UTC_FROZEN`: `2026-07-26T01:47:35Z`

## Parent evidence

- Bundle A: `CK_BUNDLE_A_GREEN`.
- S1 packet: `46e6a9081c949d586d9ea4812a31e6baf033342bef380bdf4a8ed50e73cf25b1`.
- P5 packet: `985d1aa4fcd8ff8776ba997711aec35afecab1555bcdda5a91cd2de83e326cb8`.
- P6 packet: `7c887c71aae6c7dffebd95a1fa793261d6ddf7567c3a30e90b46fe1cceae2c10`.
- P7 packet: `e28eb35f7629fd9b35beeb8c177bc4d307bc4d4b227d92d58c91320fcd78f417`.

## Workload

The immutable production command must use `--production` with exactly:

- 21,600 seconds actual continuous execution;
- 300-second checkpoints, exactly 72;
- 900-second full safety replays, exactly 24;
- 3,600-second hourly summaries, exactly six;
- separate hash-chained checkpoint, safety-replay, named-event, hourly-summary,
  telemetry, manifest, and final streams.

Every checkpoint executes all five P5 advisory lanes, ordinary and critical P6
quorum plus each refusal vector, SQLSTATE 40001 retry, duplicate receipt,
rollback, deterministic P7 selection/refusal, and real P4 quarantine
exclusion. Every safety replay creates a generated workspace, starts and stops
only its owned child, removes only the declared manifest files, proves absence,
reconstructs exact surviving bytes into a never-before-active successor,
verifies those bytes in fresh context, consumes primary and interrupted
warrants, refuses replay, restarts CockroachDB, and proves durable state.

The workload contains no model client. Persona content is represented only by
the already-frozen, synthetic, hash-bound P5 fixtures. Deterministic local code
and CockroachDB are the sole authority.

## Resource and evidence limits

- CPU only; no CUDA and zero GPUs.
- Selected target: least expensive returned secure CPU worker with at least two
  vCPU and 4 GiB RAM; 2 vCPU / 4 GiB is sufficient from measured local peak.
- Accepted compute rate: at most $0.08/hour; active rate including 20 GB
  disposable container storage: at most $0.085/hour.
- Prompt hard ceiling remains $0.25/hour and $2.00 aggregate. The narrower
  packet ceiling controls this campaign.
- Successful-worker paid lifetime: at most eight hours.
- Container disk: 20 GB; persistent/network volume: none; GPU: zero.
- Database-growth limit: 536,870,912 bytes.
- Evidence-growth limit: 134,217,728 bytes.
- RSS limit: 2,147,483,648 bytes.
- Open-file limit: 512.

## Lifecycle

Use only the checksum-verified RunPod CLI at
`/tmp/runpodctl-v2.7.2-darwin-arm64`, version `2.7.2-309512b`, SHA-256
`a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`.

The worker uses official template `runpod-ubuntu-2204`, image
`runpod/base:1.0.2-ubuntu2204`, 20 GB disposable disk, zero volume, and
provider-native stop/terminate deadlines. A detached host-local exact-ID guard
runs under `screen` plus `caffeinate`, binds the exact ID, name, campaign, CLI
path/hash, stop and delete deadlines, records a hash chain, and refuses to call
teardown GREEN until exact-ID lookup is absent and campaign-active inventory is
empty. No lifecycle credential enters the Pod.

Up to eight sequential pre-upload creation attempts are allowed inside 45
minutes, one S2 worker at a time. Every failed worker must be deleted and proved
absent before retry. Retry authority ends permanently at payload upload. There
is no replacement or second six-hour campaign after upload or timer start.

The current provider account contains unrelated resources, including an active
campaign not owned by S2 and a pre-existing network volume. S2 must not modify,
attach, stop, delete, or count those resources as its own. Every inventory
decision is exact-ID and `ck-s2-20260726-` name scoped.

## Data and network boundary

Transfer only the synthetic scanned bundle containing P3–P7 source, migrations,
fixtures, S2 workload, and the checksum-verified Linux CockroachDB archive.
No API key, account credential, HOME state, live memory, Qdrant, StateV2,
launchd, cron, AWS, Cockroach Cloud, client data, private unrelated source,
persistent volume, or public action may enter the Pod.

CockroachDB binds loopback, diagnostic reporting is disabled by environment and
cluster setting, and production checkpoints fail if the database process owns
an established non-loopback TCP connection. SSH/transfer are lifecycle control
channels, not workload egress.

## Kill line

Any parent-hash drift, preflight-judge failure, price/shape/image/volume/deadline
mismatch, secret/private-path finding, payload/runtime/guard hash mismatch,
missing stream, evidence-chain break, false quorum/recovery/quarantine,
accepted replay, policy-veto bypass, failed rollback/restart/interruption,
undeclared egress, resource/growth breach, guard lapse, cost uncertainty above
the envelope, or teardown uncertainty blocks S2. Do not continue to P8.

Required preflight judges: GLM plus Claude on one exact packet hash. Required
final judges: GLM, Claude, and AGY on one exact final packet hash.
