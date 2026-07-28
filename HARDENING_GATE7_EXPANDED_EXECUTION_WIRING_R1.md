# Hardening Gate 7 Expanded Execution Wiring R1

## Authority and stop boundary

- Candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- Scored rows: exactly `84`
- Live track: exactly `3,600` seconds, `60` checkpoints, `12` safety replays,
  `12` cloud exchanges, plus the separately counted 46,000-row bulk track.
- One successful CPU worker; no GPU, persistent volume, network volume, model,
  client data, private memory, or worker credential.
- No hidden seed and no worker creation before same-hash GLM and AGY preflight
  GREEN.
- Stop after Gate 7. Gate 8, S3-R2, release, and submission are forbidden.

This file freezes commands and parameter derivation. Exact Pod ID, SSH endpoint,
creation UTC, stop UTC, and terminate UTC are attempt receipts instantiated from
this contract immediately before each provider request. Instantiation does not
change benchmark semantics or thresholds.

## Frozen provider envelope

The parsed authority is
`HARDENING_GATE7_EXPANDED_RUNPOD_SCHEDULE_R1.json`.

For every attempt:

1. verify `/tmp/runpodctl-v2.7.2-darwin-arm64` has SHA-256
   `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`;
2. require `pod list` to contain no active worker with prefix
   `ck-g7r2-20260728-`;
3. compute `stop_after = attempt_creation_utc + 390 minutes` and
   `terminate_after = attempt_creation_utc + 420 minutes`;
4. write and fsync the exact attempt request, name, and timestamps before the
   create command;
5. create with this command shape:

```text
/tmp/runpodctl-v2.7.2-darwin-arm64 pod create
  --compute-type cpu
  --template-id runpod-ubuntu-2204
  --container-disk-in-gb 20
  --volume-in-gb 0
  --ports 22/tcp
  --ssh
  --name <ATTEMPT_NAME>
  --stop-after <STOP_RFC3339>
  --terminate-after <TERMINATE_RFC3339>
  --output json
```

The returned worker is accepted only when `pod get <POD_ID>
--include-machine --include-network-volume` proves CPU=2, RAM=4 or 8 GiB,
GPU=0, image=`runpod/base:1.0.2-ubuntu2204`, container disk no more than 20
GiB, no volume, compute rate no more than $0.10/hour, and total rate no more
than $0.12/hour. Any mismatch is deleted before upload. The retry window is 120
minutes and aggregate possible spend must remain below $5.00.

The only stop/delete and post-check commands are:

```text
/tmp/runpodctl-v2.7.2-darwin-arm64 pod stop <EXACT_POD_ID>
/tmp/runpodctl-v2.7.2-darwin-arm64 pod delete <EXACT_POD_ID>
/tmp/runpodctl-v2.7.2-darwin-arm64 pod get <EXACT_POD_ID>
/tmp/runpodctl-v2.7.2-darwin-arm64 pod list
```

Deletion is GREEN only when exact-ID lookup is absent and active inventory is
`[]`. A failed deletion blocks every retry.

## Lifecycle guard

Before upload, start the detached exact-ID guard from
`s2-soak/lifecycle_guard.py` under a unique Screen session and `caffeinate`.
Bind exact Pod ID, expected Pod name, verified CLI path/hash, stop epoch,
delete epoch, state file, hash-chained event log, and stop marker. The already
frozen local proof must remain GREEN. Provider-native stop/terminate deadlines
are an independent fuse, not a substitute for the guard.

## Transfer

Upload only the deterministic archive created by
`hardening-gate7/build_expanded_bundle.py`. Before upload require the transfer
manifest, `rg`, gitleaks 8.30.1, and detect-secrets 1.5.0 to be GREEN. After
upload verify the archive SHA-256 before extraction and verify every
`PAYLOAD_TREE.json` entry after extraction. Never upload the repository,
`.s3-runtime`, `.hardening-runtime`, evidence history, credentials, OAuth
artifacts, browser state, or HOME content.

## Remote identities and isolation

Create two unprivileged local identities inside the disposable worker:

- `ckoracle`: owns the hidden seed, generator output, sealed oracle, and final
  scorer input;
- `ckrunner`: receives only input files, runner source, and an empty HOME.

Both must have UID/EUID nonzero and effective capabilities zero. `ckrunner`
executes the hidden track through `hardening-gate6/seccomp_exec.py`, which sets
`no_new_privs`, installs the inherited network-denial seccomp filter, rejects
inherited sockets, and records `/proc` attestation. The canary must prove
socket creation fails with `EPERM` and child exec still succeeds.

`ckrunner` must not have search/read permission on the `ckoracle` root. Root
copies only `generated/inputs` and `input-manifest.json` to the runner root,
then records the copied tree hash. The sealed oracle and master seed remain
mode `0600` under a mode `0700` `ckoracle` root.

## Campaign-ready smoke

Before hidden generation:

1. verify Python and CockroachDB archive/binary hashes;
2. verify unprivileged identities and zero capabilities;
3. run the seccomp network canary;
4. run one known non-measured PROMOTE canary and one known non-measured INVALID
   canary;
5. start the detached lifecycle guard and prove its chain advances;
6. prove the worker contains no credential and no nonallowlisted file; and
7. prove the host coordinator, SSH bridge, and local CockroachDB/AWS controller
   are ready without transferring their credentials.

Only then is `CAMPAIGN_READY` true.

## Hidden input generation and runner

As `ckoracle`, invoke:

```text
/usr/bin/python3 bundle/hardening-gate7/prepare_hidden_campaign.py
  --campaign-id <CAMPAIGN_ID>
  --packet-sha256 <PREFLIGHT_PACKET_SHA256>
  --output-root <ORACLE_ROOT>
```

The script writes and fsyncs the 32-byte CSPRNG seed and pre-generation
commitment before concrete inputs exist. It then deterministically writes all
84 inputs, the separate sealed oracle, and generation receipt. No seed exists
before this command.

After the input-only copy and permission proof, execute as `ckrunner`:

```text
/usr/bin/python3 bundle/hardening-gate6/seccomp_exec.py
  --attestation <RUNNER_ROOT>/isolation-attestation.json
  --
  /usr/bin/python3 bundle/hardening-gate7/run_expanded_campaign.py
  --input-manifest <RUNNER_ROOT>/input-manifest.json
  --input-root <RUNNER_ROOT>/inputs
  --python-bin /usr/bin/python3
  --output-root <RUNNER_ROOT>/raw
  --packet-sha256 <PREFLIGHT_PACKET_SHA256>
  --source-bindings-sha256 <SOURCE_BINDINGS_SHA256>
```

The runner executes exactly once in seed-derived order. Any child failure,
false promotion signal, hash mismatch, residue, or missing receipt stops the
campaign. After all raw observations are immutable, root copies the raw tree
to the `ckoracle` root without modification, verifies source/destination tree
hashes, and the scorer runs as `ckoracle`:

```text
/usr/bin/python3 bundle/hardening-gate7/score_expanded_campaign.py
  --campaign-root <ORACLE_ROOT>/raw
  --oracle <ORACLE_ROOT>/generated/sealed-oracle/oracle.json
  --input-manifest <ORACLE_ROOT>/generated/input-manifest.json
  --output-root <ORACLE_ROOT>/scored
  --require-isolation
```

## Separate one-hour live track

The credential-free remote worker uses the frozen existing S3 protocol:

```text
/usr/bin/python3 bundle/s3-soak/worker.py
  --cockroach-bin <LINUX_COCKROACH_BINARY>
  --output-root <LIVE_OUTPUT_ROOT>
  --bridge-root <REMOTE_BRIDGE_ROOT>
  --campaign-id <CAMPAIGN_ID>-live
  --duration-seconds 3600
  --checkpoint-seconds 60
  --safety-seconds 300
  --hourly-seconds 300
  --coordinator-timeout-seconds 300
  --database-growth-limit-bytes 536870912
  --evidence-growth-limit-bytes 67108864
  --rss-limit-bytes 1610612736
  --open-files-limit 128
```

The worker contains no cloud client and no credential. It emits 12 canonical
requests. The host-side `s3-soak/remote_bridge.py` copies only canonical,
hash-linked request/result records over strict SSH host-key pinning. The
host-side `s3-soak/host_coordinator.py` allows exactly 12 Lambda calls and 108
CockroachDB operations through `.s3-runtime/live-config.json`; raw secrets and
command output are never evidence.

In parallel, the host runs the generated, campaign-prefixed, synthetic-only
bulk workload from `hardening-gate7/live_bulk_controller.py`: 2,000 tasks,
20,000 trajectory events, 4,000 receipts, 20,000 vectors, 200 task-bound vector
queries at configured concurrency four, rollback, duplicate handling, query
plan, topology, latency, and dependency-ordered cleanup. It uses the same
host-only adapter and never sends credentials to RunPod.

An AWS session must be refreshed through the project-local `aws login` command
before `CAMPAIGN_READY` and must retain at least a 15-minute margin after the
last exchange. Expiration is `HUMAN_ACTION_REQUIRED`; it is not a product
failure and cannot be bypassed.

## Retrieval and closeout

Retrieve raw inputs, observations, unscored receipts, scored receipts,
aggregates, seed commitment/reveal, isolation attestation, live telemetry,
foundation evidence, bridge/coordinator logs, lifecycle logs, runtime hashes,
and manifests. Verify remote and local hashes before stopping the worker.

Then stop/delete, prove exact-ID absence and active inventory `[]`, terminate
all SSH/bridge/coordinator/guard children, reconcile known/maximum cost, scan
retrieved evidence, and independently recompute all 84 results locally. Delayed
provider itemization does not block when exact paid lifetime, quoted rate,
mathematical maximum below $5.00, deletion, and empty inventory are proven.

Any measured semantic, safety, evidence, isolation, resource, cleanup, or live
assertion failure is preserved and blocks Gate 7. No replacement worker or
measured rerun is authorized after hidden input generation or measured start.
