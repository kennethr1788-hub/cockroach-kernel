# Hardening Gate 6 — Exact Execution Wiring R2

- `STATUS`: `FROZEN_BEFORE_RUNPOD_CREATION`
- `EXECUTION_REVISION`: `R2`
- `CAMPAIGN_ID`: `ck-gate6-20260727-run1-r2`
- `RUNPODCTL`: `/tmp/runpodctl-v2.7.2-darwin-arm64`
- `RUNPODCTL_VERSION`: `2.7.2-309512b`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- `PAYLOAD_SHA256`: `d9b98d5c66596501f2f46a7e87f54994518325b1acacca1768561652772cf283`
- `UTC_FROZEN`: `2026-07-28T00:28:00Z`

Values selected from `HARDENING_GATE6_RUNPOD_SCHEDULE_R2.json` are fixed
before each attempt. Provider-returned Pod ID, host, port, and private identity
path are validated and used only in the host process. Private identity bytes
and secret-bearing provider fields are never read, copied, logged, or included
in evidence.

## Creation

```text
/tmp/runpodctl-v2.7.2-darwin-arm64 pod create
  --compute-type cpu
  --template-id runpod-ubuntu-2204
  --image runpod/base:1.0.2-ubuntu2204
  --name <FROZEN_ATTEMPT_NAME>
  --container-disk-in-gb 20
  --volume-in-gb 0
  --ports 22/tcp
  --ssh
  --stop-after 2026-07-28T07:50:00Z
  --terminate-after 2026-07-28T08:05:00Z
  --output json
```

The sanitized response must prove CPU-only, two vCPU, 4 or 8 GiB RAM, zero
GPU, zero volume, exact image, 20-GiB container disk, matching name, and no more
than `$0.08/hour` compute or `$0.10/hour` including conservative storage.

## Detached exact-ID lifecycle guard

```text
/usr/bin/screen -dmS <ATTEMPT_SCOPED_SESSION>
  /usr/bin/caffeinate -dimsu
  /usr/bin/python3 s2-soak/lifecycle_guard.py
  --runpodctl /tmp/runpodctl-v2.7.2-darwin-arm64
  --runpodctl-sha256 a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037
  --pod-id <EXACT_PROVIDER_POD_ID>
  --pod-name <FROZEN_ATTEMPT_NAME>
  --campaign-prefix ck-gate6-20260727-r2-
  --stop-epoch 1785225000
  --delete-epoch 1785225900
  --heartbeat-seconds 30
  --log <ATTEMPT_LOCAL_ROOT>/lifecycle.ndjson
```

The guard must emit an advancing valid hash chain before upload. Provider-native
stop and terminate settings remain independent last-resort fuses.

## SSH boundary and upload

Obtain SSH metadata from authenticated `runpodctl ssh info <POD_ID>`. Validate
the host and decimal port, perform two independent ED25519 `ssh-keyscan` calls,
require byte equality, and install the result as an attempt-local `0600`
known-hosts file. Every subsequent SSH/SCP call uses the exact provider-reported
identity path, `IdentitiesOnly=yes`, `StrictHostKeyChecking=yes`, and the
attempt-local known-hosts file. This is disclosed trust-on-first-use, not
provider-signed host identity.

Upload only the scanner-clean payload archive. Before extraction, remote
SHA-256 must equal:

```text
d9b98d5c66596501f2f46a7e87f54994518325b1acacca1768561652772cf283
```

Payload upload permanently ends creation retries.

## Remote setup and hash wall

Run as root only for fixed disposable-worker setup:

```text
mkdir -p /workspace/ck-gate6-20260727-run1-r2/bundle
tar -xzf /workspace/ck-gate6-r2-payload.tar.gz
  -C /workspace/ck-gate6-20260727-run1-r2/bundle
cd /workspace/ck-gate6-20260727-run1-r2/bundle
sha256sum -c PAYLOAD_TREE.sha256
dpkg -i runtime/git_2.34.1-1ubuntu1.17_amd64.deb
chmod 0755 runtime/restic
id gate6 || useradd --create-home --uid 10001 --shell /bin/bash gate6
mkdir -p /workspace/ck-gate6-20260727-run1-r2/smoke
mkdir -p /workspace/ck-gate6-20260727-run1-r2/measured-parent
chown -R gate6:gate6 /workspace/ck-gate6-20260727-run1-r2
```

No apt update, package-resolution network call, model call, cloud login, or
credential transfer is permitted. `dpkg -i` consumes only the hash-bound local
package. Failure is a non-retryable post-upload blocker.

Before measurement, require exact output and byte hashes:

```text
/usr/bin/python3 --version
/usr/bin/git --version
/workspace/ck-gate6-20260727-run1-r2/bundle/runtime/restic version
sha256sum /usr/bin/python3 /usr/bin/git
  /workspace/ck-gate6-20260727-run1-r2/bundle/runtime/restic
  /workspace/ck-gate6-20260727-run1-r2/bundle/p4-verifier/verifier.py
```

The values must match `HARDENING_GATE6_LINUX_TOOL_PROVENANCE_R2.json` exactly.

## Unprivileged network-denial proof

Run as host user `gate6` with an empty environment except fixed PATH:

```text
env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin
  unshare --user --map-root-user --net --mount-proc
  /usr/bin/python3 -c <FIXED_SOCKET_PROBE>
```

The fixed probe attempts one outbound TCP connection to `1.1.1.1:53` and exits
zero only when the connection raises `OSError`. Any nonzero result, inability
to create the namespace, or host-root execution blocks measurement.

## Non-measured remote smoke

Run one `complete-loss`, repetition 1, product trial under the exact unshare
prefix with `--evidence-mode PREFLIGHT`, campaign ID
`ck-gate6-20260727-run1-r2-smoke`, the exact candidate commit, and a fresh
output. Validate canonical bytes, cleanup, zero residue, expected tool
provenance, and the preflight-only limitation labels. Never merge this receipt
with measured evidence.

## Measured command

Run the orchestrator as host user `gate6` under an empty environment:

```text
env -i
  PATH=/usr/bin:/bin:/usr/sbin:/sbin
  /usr/bin/python3 bundle/hardening-gate6/run_campaign.py
  --manifest bundle/HARDENING_GATE6_EXECUTION_MANIFEST_R2.json
  --output-root measured-parent/campaign
  --comparative bundle/hardening-gate5/comparative.py
  --tools bundle/HARDENING_GATE6_LINUX_TOOL_PROVENANCE_R2.json
  --git /usr/bin/git
  --restic /workspace/ck-gate6-20260727-run1-r2/bundle/runtime/restic
  --python /usr/bin/python3
```

The orchestrator creates every measured row under the exact `unshare` wrapper,
validates the untouched candidate receipt, fsyncs a hash-chained checkpoint,
and stops on the first integrity failure. Periodically copy the checkpoint file
to local custody without modifying the remote source.

## Retrieval and teardown

After the runner exits, freeze a remote SHA-256 tree manifest, archive the
measured directory, retrieve both, verify the local archive/tree, and retain
raw stdout/stderr. Then stop and delete the exact Pod, prove exact-ID 404/absent,
and require fresh campaign-scoped running and all-status inventories to be
empty. Stop every attempt-local Screen/caffeinate/SSH/SCP process and verify no
paid or background process remains.

An exact provider charge may be `BILLING_PENDING` after verified deletion when
the exact prelaunch rate, paid lifetime, and bounded maximum remain recorded.
Unknown prelaunch price or unbounded exposure is never allowed.
