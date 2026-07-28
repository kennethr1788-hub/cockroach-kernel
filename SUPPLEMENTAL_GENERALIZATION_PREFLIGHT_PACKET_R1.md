# Supplemental Generalization — Independent Preflight Packet R1

## Requested verdict

Return `GREEN` only if this exact packet safely authorizes one disposable CPU
worker campaign and its sequential pre-upload accessibility retries, and the
frozen workload can produce honest supplemental evidence without changing Gate
6 or Gate 7. Otherwise return `NOT_GREEN` with concrete findings. You are a
non-authoring judge with no shell, browser, credential, provider, write, or
implementation authority.

## Parent state and boundary

- Gate 6: `HARDENING_6_RUN1_GREEN`, immutable.
- Gate 6 candidate: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`.
- Implementation commit containing this harness: `0660af705d8151cffaa2b2abe5c2a679e61f605b`.
- This campaign: supplemental private generalization after Gate 6.
- This campaign is not Gate 7 and does not execute the later fresh-context
  black-box evaluation.
- Live provider inventory immediately before packet freeze: `[]`.

## Objective and acceptance

The full contract is `SUPPLEMENTAL_GENERALIZATION_CONTRACT_R1.md`, SHA-256
`0569a92077e9b6a02bd8e6db0f75b8c448e03995b0556b7c5ed8ebb0fa8a4f9ea`.

The campaign runs 108 unique paired executions: three profiles (16 files /
128 KiB, 64 files / 4 MiB, 128 files / 64 MiB), six frozen state/loss classes,
three methods, and two repetitions. Product acceptance is 12/12 exact-manifest
and executable-continuation passes per profile, 108/108 clean teardowns, zero
residue, and zero unsafe acceptance. All failures are retained. The evidence is
labeled synthetic, team-authored, private, non-production-scale, and unsuitable
for population inference.

## Workload and payload binding

- execution manifest SHA-256: `685467a05a7645ee377376e346d2c4c4d379bc11ad60667d0b123ba6c416a989`;
- compact harness SHA-256: `78826a72c12e6f8020f3e80ce669f103aa7d9fc494a13be5ed8dcde5486b8786`;
- campaign runner SHA-256: `023ff457ce3b077bbc904e2546b7f6f6c3efa76534cda5982ad1ac6ba7c7fb3e`;
- frozen comparator SHA-256: `f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec`;
- frozen verifier SHA-256: `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`;
- seccomp launcher SHA-256: `64a4c1d7e68238dbeb4959a8bc52cba0b0aaa5499131a145e0b31d5cb8c52ab3`;
- Restic 0.19.0 Linux binary SHA-256: `ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c`;
- Ubuntu Git package SHA-256: `8794fcf2c4606c445df0db3dc963c8fb852772208bfb12727a12717c03767af7`;
- payload tree file SHA-256: `dca837268541b028677a23844ed3cab7f03e12811533f2d564944c9c8daeea8d`;
- payload archive SHA-256: `a3fe1f0aef6be48bf478d1e635f33c1345343d271a77d3f8fe94c9c601ddfe85`;
- payload archive bytes: `14,222,836`.

The payload is allowlisted and contains only the frozen protocol, compact
manifest/generator/runner, comparator, verifier, seccomp launcher, Restic
binary, and offline Git package. It contains no repository history, AWS or
CockroachDB material, credentials, private data, HOME state, Qdrant, StateV2,
or Gate 7 inputs. `gitleaks 8.30.1` found zero leaks. `detect-secrets 1.5.0`
reported only five expected high-entropy constants: the frozen protocol/tool
hashes and candidate commit. The raw text scan found only the trial-local
random Restic password implementation, which is generated inside each trial,
never transferred as a credential, and deleted with the trial root.

## Local verification

- three unit tests passed;
- manifest validation passed with 108 unique rows;
- payload-tree verification passed for every file;
- representative small complete-loss Git, Restic, and product trials completed;
- representative medium and large product trials completed;
- a representative high-entropy 64-MiB Restic trial completed in 19.30 seconds;
- every local smoke teardown was clean;
- product and Restic restored exact manifests and executable continuation;
- ordinary Git honestly returned unsupported for uncommitted/untracked state.

Local smoke is not measured evidence and is not merged with the remote result.

## Provider envelope

The canonical one-line schedule is
`SUPPLEMENTAL_GENERALIZATION_RUNPOD_SCHEDULE_R1.json`.

- maximum eight sequential creation/readiness attempts;
- one worker at a time and one measured worker total;
- retries end permanently when payload upload begins;
- accepted worker: secure CPU, exactly 2 vCPU, exactly 4 or 8 GiB RAM, zero
  GPU, official `runpod-ubuntu-2204` template, exact
  `runpod/base:1.0.2-ubuntu2204` image, 20-GiB disposable container disk, zero
  persistent/network volume;
- accepted compute price: at most $0.06/hour for 4 GiB or $0.08/hour for 8 GiB;
- accepted total active rate: at most $0.10/hour;
- aggregate exposure ceiling across attempts: $1.00;
- measured workload ceiling: 7,200 seconds;
- paid-lifetime ceiling: 15,600 seconds;
- provider stop fuse: `2026-07-28T08:30:00Z`;
- provider termination fuse: `2026-07-28T08:45:00Z`.

The latest visible official CPU quote was 2 vCPU / 8 GiB at $0.08/hour. The
creation response must expose and match the actual current shape and rate before
upload. Missing/unknown price, price drift, or an ambiguous response requires
immediate deletion and blocks further retry unless the failure is a permitted
pre-upload accessibility class and the aggregate exposure remains bounded.

## Retry and lifecycle law

The operator explicitly authorized the lifecycle and sequential accessibility
retries. Retry is permitted only before upload for provider creation failure,
capacity failure, mismatched returned shape/image/storage, readiness failure,
or SSH accessibility failure. Every assigned Pod ID gets an attempt receipt.
Any existing attempt is stopped/deleted and exact-ID absence plus empty scoped
inventory is proved before the next attempt. Three consecutive identical
failures stop blind retry for diagnosis. No billing settings, account limits,
provider substitution, parallel worker, or post-upload replacement is allowed.

The host uses `/tmp/runpodctl-v2.7.2-darwin-arm64`, version
`2.7.2-309512b`, SHA-256
`a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`.
The detached exact-ID guard is `s2-soak/lifecycle_guard.py`, SHA-256
`4644aa756f47c3d53b82c239657ce22605d4a9caab3e6a8651c4f459d95c6f0c`.
It binds exact Pod ID/name/prefix and CLI hash, writes a hash-chained heartbeat,
performs bounded stop/delete, and requires exact-ID absence and empty scoped
inventory before teardown GREEN. Provider stop/terminate fuses are independent.

## Remote execution boundary

The worker receives only the hash-verified payload. Fixed offline packages are
installed before isolation; then the complete campaign runs as an unprivileged
user with zero effective capabilities under inherited seccomp network denial.
The filter denies sockets and alternate network interfaces and is verified
through `/proc/self/status` plus an `EPERM` socket canary. No model, cloud API,
AWS, CockroachDB, HOME, secret, or unrelated-project access occurs remotely.

On completion or any post-upload failure, logs and evidence are flushed,
archived, hashed, retrieved, and independently rehashed before exact-ID
stop/delete. Final proof requires exact-ID absence, empty campaign running/all
inventory, no local lifecycle/SSH/transfer processes, and bounded cost
reconciliation. Billing may be recorded as pending after verified deletion only
when the exact prelaunch rate, paid lifetime, and maximum bounded cost are all
known; an unknown prelaunch price is never acceptable.

## Stop conditions

Stop on packet/hash drift, judge non-GREEN, payload scan failure, unknown or
unbounded price, wrong worker, failed deletion proof, upload to an unverified
worker, isolation failure, network availability inside measurement, missing or
noncanonical receipt, evidence mismatch, false acceptance, residue, resource
leak, lifecycle-guard failure, secret/private-path exposure, or aggregate spend
uncertainty above $1.00.

## Judge response schema

Return exactly:

```text
VERDICT: GREEN | NOT_GREEN | JUDGE_UNAVAILABLE
PACKET_SHA256: <exact hash supplied by caller>
BLOCKERS: <none or concise list>
RESIDUAL_RISKS: <concise list>
```
