# Hardening Gate 6 — Exact Execution Wiring R3

- `STATUS`: `FROZEN_BEFORE_RUNPOD_CREATION`
- `EXECUTION_REVISION`: `R3`
- `CAMPAIGN_ID`: `ck-gate6-20260727-run1-r3`
- `RUNPODCTL`: `/tmp/runpodctl-v2.7.2-darwin-arm64`
- `RUNPODCTL_VERSION`: `2.7.2-309512b`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- `UTC_FROZEN`: `2026-07-28T01:22:12Z`

## Creation and lifecycle

Create one CPU worker at a time using the exact R3 schedule, official Ubuntu
22.04 CPU template, exact image, 20-GiB container disk, zero volume, SSH, and
provider-native stop/terminate fuses. The response must prove 2 vCPU, 4 or 8
GiB, zero GPU, exact image/name/disk/volume, compute rate within its shape limit,
and total active rate no greater than `$0.10/hour`.

Immediately bind the exact Pod ID and expected name to the hash-pinned detached
local `s2-soak/lifecycle_guard.py`. Require an advancing chain before any
transfer. SSH uses validated provider metadata, two byte-identical ED25519
`ssh-keyscan` results, an attempt-local known-hosts file, `IdentitiesOnly=yes`,
and `StrictHostKeyChecking=yes`. Private identity bytes are never printed,
copied, read into evidence, or committed.

## Capability-only retry stage

Before the benchmark payload, transfer only `hardening-gate6/seccomp_exec.py`
and its SHA-256. Root may create UID 10001 and a canary output directory. Run:

```text
env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin
  runuser -u gate6 --
  /usr/bin/python3 seccomp_exec.py
  --attestation /workspace/ck-gate6-r3-canary/attestation.json
  --canary-only
```

Validate the exact script hash, canonical attestation hash, UID/capability
fields, no inherited socket on any descriptor (including 0/1/2),
`NoNewPrivs=1`, `Seccomp=2`, filter-spec hash, x32 kill branch,
`DENIED_EPERM`, and exec canary. A pre-payload capability/readiness failure may
tear down and consume a sequential retry. Teardown and exact-ID absence are
mandatory before another.

## Payload and setup

After one worker passes the canary, creation retries end. Upload only the
scanner-clean, hash-bound R3 payload, verify its archive and tree hashes, and
extract under `/workspace/ck-gate6-20260727-run1-r3/bundle`. Install only the
included Ubuntu Git package, set the included Restic binary executable, and
chown the campaign root to UID 10001. No apt resolution, cloud login, model
call, credential transfer, persistent volume, or undeclared egress is allowed.

Reverify exact Python, Git, Restic, verifier, runner, and seccomp-launcher
versions and byte hashes. Any post-payload mismatch blocks without replacement.

## Smoke and measured run

Run the non-measured product/complete-loss smoke through the same seccomp
launcher into a fresh output. Then run the R3 orchestrator under a fresh
attestation:

```text
env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin
  runuser -u gate6 --
  /usr/bin/python3 bundle/hardening-gate6/seccomp_exec.py
  --attestation /workspace/ck-gate6-20260727-run1-r3/isolation.json
  --
  /usr/bin/python3 bundle/hardening-gate6/run_campaign_r3.py
  --manifest bundle/HARDENING_GATE6_EXECUTION_MANIFEST_R3.json
  --output-root measured-parent/campaign
  --comparative bundle/hardening-gate5/comparative.py
  --tools bundle/HARDENING_GATE6_LINUX_TOOL_PROVENANCE_R3.json
  --git /usr/bin/git
  --restic /workspace/ck-gate6-20260727-run1-r3/bundle/runtime/restic
  --python /usr/bin/python3.10
```

Retrieve checkpoints during execution where practical. After completion,
freeze the remote evidence tree, retrieve and byte-verify it, then stop/delete
the exact worker and require exact-ID absence plus empty campaign running and
active inventories. Stop all local guard/SSH/transfer processes. Billing may
remain explicitly pending after verified deletion if the exact rate, paid
lifetime, and bounded maximum are preserved; unknown prelaunch price is never
allowed.
