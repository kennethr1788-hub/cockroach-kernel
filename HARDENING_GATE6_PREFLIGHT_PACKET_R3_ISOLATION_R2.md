# Hardening Gate 6 — Same-Hash Preflight Judge Packet R3-ISOLATION-R2

## Judge contract

This is a non-authoring, sanitized, pre-provider review. Return one structured
verdict only. Do not write code, propose patches, direct implementation,
request tools or credentials, or claim execution. Treat every included byte as
one packet. The externally supplied SHA-256 is canonical.

Required verdict schema:

```json
{"verdict":"GREEN|NOT_GREEN|BLOCKED","candidate_immutability":"GREEN|NOT_GREEN","fairness_and_pairing":"GREEN|NOT_GREEN","runtime_isolation":"GREEN|NOT_GREEN","evidence_and_statistics":"GREEN|NOT_GREEN","lifecycle_and_teardown":"GREEN|NOT_GREEN","blockers":[],"limitations":[],"recusal":"CLEAR|REQUIRED"}
```

GREEN means this exact R3 packet is safe and complete enough to create one CPU
worker at a time, run the pre-payload capability canary, and—only after a
successful canary—execute the frozen 54-row campaign. It does not assert the
seccomp mechanism works on RunPod, predict a favorable product result, or
approve Gate 7.

The R2 namespace failure is real and preserved. R3 makes no network-namespace
claim. Decide whether the proposed unprivileged `no_new_privs` plus inherited
seccomp-BPF boundary is an acceptable, fail-closed replacement for this
offline benchmark. If not, return NOT_GREEN or BLOCKED; do not design a fix.

Control state: parent Gate 5 R2 is independently GREEN; orchestration commit is
`9377acc747d93e16b9e5aa081b696aed20440005`; immutable candidate is `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`; current
RunPod running inventory is empty; no Gate 6 R3 worker, canary, or measured row
exists.

## FILE: HARDENING_GATE6_R3_OPERATOR_AUTHORIZATION_RECEIPT.md

```text
# Hardening Gate 6 R3 — Operator Authorization Receipt

- `STATUS`: `AUTHORIZED`
- `AUTHORIZED_BY`: `Kenneth`
- `AUTHORIZED_SCOPE`: `Gate 6 R3 isolation amendment and sequential RunPod retries`
- `UTC_RECORDED`: `2026-07-28T01:22:12Z`
- `LAST_GREEN_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `GATE7_AUTHORIZED`: `no`

Kenneth explicitly authorized another RunPod retry and future retries for failed
attempts needed to make the Gate 6 run work. This receipt interprets that
authority as sequential, bounded, reviewed Gate 6 campaigns under the current
RunPod policy. It does not authorize parallel workers, an unknown or unbounded
price, a rate above the policy human gate, provider billing or account-setting
changes, persistent/network volumes, credential transfer, candidate changes,
HOME or live-state mutation, Gate 7, release, or submission.

Each paid campaign still requires a frozen worker/rate/lifetime envelope,
provider-native stop and terminate fuses, exact-ID deletion, empty scoped
inventory, and same-hash independent preflight. If the same failure occurs
three consecutive times, blind retries stop for bounded diagnosis and a new
same-hash review. No benchmark-payload replacement is permitted after the
first successful isolation canary and full payload upload.
```

## FILE: HARDENING_GATE6_STATUS_R2.md

```text
# Hardening Gate 6 Status R2

- `STATUS`: `HARDENING_6_RUN1_BLOCKED`
- `EXECUTION_REVISION`: `R2`
- `BLOCKER`: `UNPRIVILEGED_NETWORK_NAMESPACE_UNAVAILABLE`
- `LAST_GREEN_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `ORCHESTRATION_BASE_COMMIT`: `cede131c59097b615b0f6c02926b35b77505b65f`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `PREFLIGHT_PACKET_SHA256`: `f1df04300bd4d865d2c0d2b87bc8c5f607a98f23e7c45d377edc84c31a04346d`
- `PREFLIGHT_JUDGES`: `GLM 5.2 GREEN; CLAUDE OPUS 4.8 GREEN; RECUSAL CLEAR`
- `FINAL_PACKET_SHA256`: `6f3b1d8a3c10244d88feb99a8a39c9ce13ae836abf9c0117617d7adfcac12ede`
- `FINAL_JUDGES`: `GLM 5.2 BLOCKED CONFIRMED; CLAUDE OPUS 4.8 BLOCKED CONFIRMED; RECUSAL CLEAR`
- `MEASURED_EXECUTIONS_COMPLETED`: `0`
- `RUNPOD_ATTEMPTS`: `1`
- `POD_IDS`: `2sh4lx37f6r73g`
- `COST_STATE`: `BILLING_PENDING_BOUNDED_MAX_$0.0060`
- `RUNPOD_RUNNING_INVENTORY`: `[]`
- `UTC_RECORDED`: `2026-07-28T00:58:13Z`

The returned worker matched every reviewed provider property. Payload transfer,
tree verification, offline Git installation, and the exact Python, Git, Restic,
and product-verifier version/hash wall passed. The required host-unprivileged
network namespace then failed before smoke or measurement:

```text
unshare: unshare failed: Operation not permitted
```

The prompt explicitly classifies inability to create the reviewed unprivileged
network namespace as an isolation/capability failure. No alternate isolation,
root execution, in-process socket guard, host firewall change, replacement Pod,
smoke row, or measured row was used. The worker was stopped and deleted; exact
ID absence, empty campaign inventory, the guard teardown chain, and absence of
remaining local campaign processes all passed.

Gate 6 remains blocked. Gate 7 is forbidden.
```

## FILE: HARDENING_GATE6_FINAL_JUDGE_RECEIPT_R2.md

```text
# Hardening Gate 6 — Same-Hash Final Judge Receipt R2

- `PACKET_SHA256`: `6f3b1d8a3c10244d88feb99a8a39c9ce13ae836abf9c0117617d7adfcac12ede`
- `GLM_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `BLOCKED`
- `GLM_RECUSAL`: `CLEAR`
- `GLM_RAW_SHA256`: `5137140d5c200fad93079802c5c0256ef302ed1f808980abbefeb664041f44cc`
- `CLAUDE_MODEL`: `claude-opus-4-8`
- `CLAUDE_VERDICT`: `BLOCKED`
- `CLAUDE_RECUSAL`: `CLEAR`
- `CLAUDE_RAW_SHA256`: `3e3e7fabb2aeb599497acb2f8f6515f50d0cca939ab14c87742d89fd2c893328`
- `TEARDOWN_ASSESSMENT`: `GREEN_FOR_BLOCKED_ATTEMPT`
- `SAFE_TO_STOP_BEFORE_GATE7`: `yes`
- `UTC_RECORDED`: `2026-07-28T01:07:25Z`

Both required independent judges reviewed the exact same final packet and
confirmed that `HARDENING_6_RUN1_BLOCKED` is the only evidence-supported
closeout. The required unprivileged network-denial proof is absent, zero of 54
measured executions ran, and those completion requirements cannot be waived.

Both judges separately confirmed that exact-ID deletion, empty campaign
inventory, guard closure, bounded billing custody, and process cleanup are
sufficient to stop safely. Neither verdict authorizes Gate 7 or a replacement
worker.
```

## FILE: HARDENING_GATE6_PREFLIGHT_JUDGE_RECEIPT_R3_R1.md

```text
# Hardening Gate 6 R3 — Preflight Judge Receipt R1 (Superseded)

- `PACKET_SHA256`: `49068ab24f16b51120b447514bd928e527d02428a8343ae10443f8a83041613b`
- `GLM_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RAW_SHA256`: `37883d1a021f7aec5c110c6bcfccf325f8488a5e7407c1a916bdb83c4cea5591`
- `CLAUDE_MODEL`: `claude-opus-4-8`
- `CLAUDE_VERDICT`: `GREEN`
- `CLAUDE_RECUSAL`: `CLEAR`
- `CLAUDE_RAW_SHA256`: `93f1a3aed80ea98f20e8f3ad082c5c9ebbbd7357bbe1b628a1df94aa96f801b6`
- `STATUS`: `SUPERSEDED_BY_BUILDER_HARDENING`

Both required judges returned GREEN over the exact R1 packet. Claude also
identified non-blocking residuals involving the x32 syscall-number form and
socket descriptors 0/1/2. The builder independently treated those mechanisms
as worth closing before provider creation. The R1 GREEN therefore authorizes
nothing after the source changes. A complete new packet and complete same-hash
GLM/Claude review are mandatory.
```

## FILE: HARDENING_GATE6_ISOLATION_AMENDMENT_R3.md

```text
# Hardening Gate 6 — Isolation and Platform Amendment R3

- `STATUS`: `FROZEN_FOR_INDEPENDENT_PREFLIGHT`
- `EXECUTION_REVISION`: `R3`
- `PARENT_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `PRIOR_BLOCKER`: `UNPRIVILEGED_NETWORK_NAMESPACE_UNAVAILABLE`
- `REPLACEMENT_MECHANISM`: `UNPRIVILEGED_NO_NEW_PRIVS_INHERITED_SECCOMP_BPF`
- `NETWORK_NAMESPACE_CLAIM`: `NOT_MADE`

## Evidence-driven change

R2 directly proved that the reviewed RunPod container rejects
`unshare --user --map-root-user --net --mount-proc` with `Operation not
permitted`. No measured row ran. R3 does not relabel that failure or claim a
namespace exists. It replaces the unavailable namespace with a kernel-enforced
network-denial boundary that an unprivileged process can install without a
capability, host firewall change, privileged container, or provider setting.

The immutable product candidate, six scenarios, three methods, three
repetitions, method rotation, success rules, comparator source, verifier, tool
versions, and 54-row evidence contract do not change. Only Gate 6 execution
infrastructure changes.

## Kernel contract

`hardening-gate6/seccomp_exec.py` must run on Linux x86_64 as UID/EUID 10001
with `CapEff=0`, no inherited socket file descriptor, and an empty fixed
environment. It then:

1. calls `prctl(PR_SET_NO_NEW_PRIVS, 1)`;
2. installs a classic seccomp-BPF filter using
   `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, ...)`;
3. kills a foreign syscall architecture and the x32 ABI syscall-number form;
4. returns `EPERM` for every declared x86_64 socket syscall and for alternate
   kernel paths that could create, submit, or acquire network work (`bpf`,
   `io_uring_*`, `pidfd_getfd`, `setns`, and `unshare`);
5. permits ordinary file, process, Git, Restic, and verifier operations;
6. proves `/proc/self/status` reports `NoNewPrivs=1` and `Seccomp=2`;
7. proves an AF_INET socket creation fails with `EPERM` and `/bin/true` can
   execute;
8. fsyncs a canonical hash-bound attestation; and
9. `exec`s the measured orchestrator without clearing the filter.

Linux seccomp filters and `no_new_privs` are inherited across fork and exec and
cannot be relaxed by the filtered unprivileged process. All 54 method children
therefore execute under the same kernel filter. The R3 runner independently
checks UID, capability state, kernel seccomp state, attestation bytes/hash, and
another real AF_INET denial before the first measured row.

## Pre-upload capability canary

Before any benchmark payload upload, a returned worker may receive only the
hash-bound `seccomp_exec.py` canary. Root may create the disposable UID 10001
and its output directory, then the canary must run as that user with a fixed
empty environment. A valid canary requires:

- exact script SHA-256;
- Linux x86_64;
- UID/EUID 10001 and nonzero;
- `CapEff=0000000000000000`;
- no inherited socket descriptor, including descriptors 0, 1, or 2;
- `NoNewPrivs=1` and `Seccomp=2` after installation;
- filter-spec hash agreement;
- AF_INET creation denied with `EPERM`;
- child exec canary PASS; and
- canonical attestation hash agreement.

Failure before benchmark upload permits teardown and a sequential provider
retry. Three consecutive identical capability failures stop blind retrying for
bounded diagnosis and fresh review. Any mismatch, secret exposure, undeclared
egress, inability to delete, or unknown price is non-retryable.

## Limits and honest claims

This is process-tree network denial, not a network namespace, VM boundary,
container escape defense, host firewall, or proof about unrelated processes.
The remote root setup lane can use the already-open SSH control path; measured
code cannot create or acquire a network socket. The benchmark remains
synthetic, team-authored, `n=3` per class/method, and not population evidence.

Any judge rejection of this replacement mechanism preserves Gate 6 BLOCKED.
No fallback to an in-process monkeypatch, socket shim, root execution, or
unfiltered measurement is allowed.
```

## FILE: HARDENING_GATE6_EXECUTION_PLAN_R3.md

```text
# Hardening Gate 6 — Execution Plan R3

- `TARGET_GATE`: `HARDENING_6_RUN1_GREEN`
- `EXECUTION_REVISION`: `R3`
- `PARENT_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `CAMPAIGN_ID`: `ck-gate6-20260727-run1-r3`
- `MEASURED_EXECUTIONS`: `54`
- `PAIRED_GROUPS`: `18`
- `RUNPOD_WORKERS`: `one successful measured worker; at most eight sequential pre-payload attempts in this campaign`
- `AGY_REQUIRED`: `false`

## Acceptance and kill line

Close GREEN only if all 54 canonical receipts, all 18 equal-information pairs,
raw aggregation, inherited kernel network denial, candidate and tool hashes,
evidence custody, exact-ID teardown, empty campaign inventory, and same-hash
GLM plus Claude final reviews pass. A favorable product score is not itself an
acceptance condition.

Kill before measurement on candidate, contract, tool, script, filter, canary,
payload, price, or lifecycle drift; unequal paired inputs/budgets; inherited
socket state; unavailable kernel seccomp; or a non-GREEN required preflight
judge. Kill during the campaign on any invalid row or receipt, false promotion,
unsafe acceptance, mutation after loss/refusal, nondeterminism, residue,
checkpoint failure, network-denial failure, or inability to guarantee worker
deletion.

## Frozen comparison

`HARDENING_GATE6_EXECUTION_MANIFEST_R3.json` contains each
`(scenario_class, repetition, method)` tuple exactly once. It preserves the
Gate 5 scenario-index rotation and identical candidate/comparator behavior.
Every row uses a fresh process and trial root. The common candidate harness
emits the receipt; Gate 6 only validates, fsyncs a checkpoint, and aggregates.

## Isolation

The exact R3 amendment and reviewed `seccomp_exec.py` control the boundary.
The capability canary runs before the full payload. Once the payload is
uploaded, creation retries permanently end. The successful worker runs one
non-measured smoke and then the 54-row campaign as unprivileged UID 10001 under
the inherited filter. `run_campaign_r3.py` fails closed unless the kernel and
attestation wall is directly present.

## Evidence

Preserve the canary attestation, remote script hash, tool hash wall, non-measured
smoke, 54 raw receipts, 54-event checkpoint chain, 18 paired reports, aggregate,
raw stdout/stderr, remote and retrieved tree manifests, lifecycle chain,
provider responses, billing bounds, exact-ID absence, inventories, and secret/
private-path scans. Evidence labels must distinguish canary, smoke, and measured
rows. Gate 3 human trace remains separate and is never pooled.

## Required independent judges

Before worker creation and after teardown, GLM 5.2 and Claude Opus 4.8 review
the same exact sanitized packet hash as non-authoring judges. They have no
shell, write, credential, deployment, browser, or implementation authority.
Both must return GREEN with recusal clear. The builder never self-approves.

No model, prompt, untrusted content, memory write, agent dispatch, or external
egress occurs inside the measured workload, so a separate Wall-7/AGY lane is
not required for this offline benchmark.
```

## FILE: HARDENING_GATE6_EXECUTION_WIRING_R3.md

```text
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
  --tools bundle/HARDENING_GATE6_LINUX_TOOL_PROVENANCE_R2.json
  --git /usr/bin/git
  --restic /workspace/ck-gate6-20260727-run1-r3/bundle/runtime/restic
  --python /usr/bin/python3
```

Retrieve checkpoints during execution where practical. After completion,
freeze the remote evidence tree, retrieve and byte-verify it, then stop/delete
the exact worker and require exact-ID absence plus empty campaign running and
active inventories. Stop all local guard/SSH/transfer processes. Billing may
remain explicitly pending after verified deletion if the exact rate, paid
lifetime, and bounded maximum are preserved; unknown prelaunch price is never
allowed.
```

## FILE: HARDENING_GATE6_RUNPOD_SCHEDULE_R3.json

```text
{"accepted_active_rate_usd_per_hour_max":"0.10","accepted_compute_rate_usd_per_hour_by_memory_gib":{"4":"0.06","8":"0.08"},"accepted_container_disk_gb":20,"accepted_cpu_count":2,"accepted_gpu_count":0,"accepted_image":"runpod/base:1.0.2-ubuntu2204","accepted_memory_gib_values":[4,8],"accepted_network_volume_gb":0,"accepted_template_id":"runpod-ubuntu-2204","aggregate_runpod_exposure_usd_max":"25.00","attempt_names":["ck-gate6-20260727-r3-a01","ck-gate6-20260727-r3-a02","ck-gate6-20260727-r3-a03","ck-gate6-20260727-r3-a04","ck-gate6-20260727-r3-a05","ck-gate6-20260727-r3-a06","ck-gate6-20260727-r3-a07","ck-gate6-20260727-r3-a08"],"campaign_id":"ck-gate6-20260727-run1-r3","campaign_prefix":"ck-gate6-20260727-r3-","execution_revision":"R3","maximum_creation_attempts":8,"maximum_measured_workers":1,"maximum_measured_workload_seconds":21600,"maximum_paid_lifetime_seconds":25200,"maximum_simultaneous_workers":1,"provider_stop_epoch":1785226500,"provider_stop_utc":"2026-07-28T08:15:00Z","provider_terminate_epoch":1785227400,"provider_terminate_utc":"2026-07-28T08:30:00Z","schema_version":"hardening-gate6-runpod-schedule-v1"}
```

## FILE: HARDENING_GATE6_EXECUTION_MANIFEST_R3.json

```text
{"campaign_id":"ck-gate6-20260727-run1-r3","candidate_commit":"8718fbecc2b145ff36ce8c3ed655e92b5906aeab","evidence_mode":"MEASURED_GATE6","execution_revision":"R3","manifest_sha256":"1e73682e0eb880c95f5826d731cf6c1b6fe1f61e342bfb2d36c7fd1d3600d711","methods":["ordinary-git","git-plus-restic-0.19.0","product"],"recovery_budget_seconds":180,"repetitions":[1,2,3],"rotation_rule":"scenario_index_mod_3_as_frozen_by_gate5_run_smoke","row_count":54,"rows":[{"execution_order":1,"method":"ordinary-git","receipt_name":"001--committed-only--r1--ordinary-git.json","repetition":1,"row_sha256":"479490b37b4214e81be6ad4a2be0cbbcc54378c83e0ecbcc267a6c5cf5de7db9","scenario_class":"committed-only","sequence":1},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"002--committed-only--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"60fc2873fe9c12dbf442abffa0208fe72b3ca6977e6b5cfe68840c4b55b9df53","scenario_class":"committed-only","sequence":2},{"execution_order":3,"method":"product","receipt_name":"003--committed-only--r1--product.json","repetition":1,"row_sha256":"ee7f9359c56172127c45b0f9189d0554b3c0c315e8fa8ecab5650b0b5de09cb0","scenario_class":"committed-only","sequence":3},{"execution_order":1,"method":"ordinary-git","receipt_name":"004--committed-only--r2--ordinary-git.json","repetition":2,"row_sha256":"8d47bcf59febb725847f84ee51b4eab07e4852f9e5e7fdac33f107377c88adb1","scenario_class":"committed-only","sequence":4},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"005--committed-only--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"47c6c30389e2f2ba09918f32fea6cf9694a88f23343e77711088c0c125235e25","scenario_class":"committed-only","sequence":5},{"execution_order":3,"method":"product","receipt_name":"006--committed-only--r2--product.json","repetition":2,"row_sha256":"afd76c4c2d6b181100f43aa144c6cb7e798a438b9c2159cac8d0cbf5f5f368b5","scenario_class":"committed-only","sequence":6},{"execution_order":1,"method":"ordinary-git","receipt_name":"007--committed-only--r3--ordinary-git.json","repetition":3,"row_sha256":"acb6b683e84339d2ce08ac71018781b647705aff0ec764ce14979ef2a83da761","scenario_class":"committed-only","sequence":7},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"008--committed-only--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"d1ef09296bb8d808ef27a8c0d3fcf7a0d6bc94a1560e5b8657e4c5b2be19c57d","scenario_class":"committed-only","sequence":8},{"execution_order":3,"method":"product","receipt_name":"009--committed-only--r3--product.json","repetition":3,"row_sha256":"399da93cc6269c8cbd9d78ac07e05d824c374dc6702b38b63e740a1f8375deed","scenario_class":"committed-only","sequence":9},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"010--committed-plus-uncommitted--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"92ff8ff99830dc29c9770627e48fa7ebfeae876b3d0e06f7ffdf05f0d22c65c0","scenario_class":"committed-plus-uncommitted","sequence":10},{"execution_order":2,"method":"product","receipt_name":"011--committed-plus-uncommitted--r1--product.json","repetition":1,"row_sha256":"b636b3e4f0cfc372dd5074020007d528aa0a7370b90be88e1cac09f1e6f82975","scenario_class":"committed-plus-uncommitted","sequence":11},{"execution_order":3,"method":"ordinary-git","receipt_name":"012--committed-plus-uncommitted--r1--ordinary-git.json","repetition":1,"row_sha256":"8179cff27d9a0114c086150fcc1ac744d041f6aa2680b77e87c9f07b2916061b","scenario_class":"committed-plus-uncommitted","sequence":12},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"013--committed-plus-uncommitted--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"b74e22822cf646da75a796fe5701c7c1d0e72b607cbe4e891db5ae4ff3d1ef67","scenario_class":"committed-plus-uncommitted","sequence":13},{"execution_order":2,"method":"product","receipt_name":"014--committed-plus-uncommitted--r2--product.json","repetition":2,"row_sha256":"7d3882e9786629d33e8246dc659fe3c0d27114ed10ee524a451272b558bdbb7c","scenario_class":"committed-plus-uncommitted","sequence":14},{"execution_order":3,"method":"ordinary-git","receipt_name":"015--committed-plus-uncommitted--r2--ordinary-git.json","repetition":2,"row_sha256":"1fbc00f5c459c0ed31c5f76f77e5a31080dbb4fb62d6a1570ca68b4051e8c37d","scenario_class":"committed-plus-uncommitted","sequence":15},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"016--committed-plus-uncommitted--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"af4271e7f9ab3c8fbc9c8ee78efb720035bcab29d982a1c2f60fd87839327f32","scenario_class":"committed-plus-uncommitted","sequence":16},{"execution_order":2,"method":"product","receipt_name":"017--committed-plus-uncommitted--r3--product.json","repetition":3,"row_sha256":"a7b6673e41c6a2df9bffae62a16fed04a221a122fe3a0295569b364daec1d458","scenario_class":"committed-plus-uncommitted","sequence":17},{"execution_order":3,"method":"ordinary-git","receipt_name":"018--committed-plus-uncommitted--r3--ordinary-git.json","repetition":3,"row_sha256":"3419162323edd35238a259f5b3abc2e184fedeb7380326f1851e7caf591a67a7","scenario_class":"committed-plus-uncommitted","sequence":18},{"execution_order":1,"method":"product","receipt_name":"019--complete-loss--r1--product.json","repetition":1,"row_sha256":"ba29258457f921553e5c9e37180cb11dcf7de13af8be3cbcf836176c9ed5a51f","scenario_class":"complete-loss","sequence":19},{"execution_order":2,"method":"ordinary-git","receipt_name":"020--complete-loss--r1--ordinary-git.json","repetition":1,"row_sha256":"a677b0b8c8be45091483fdb515f612b2d367958beec8ff32e3a4f40825468146","scenario_class":"complete-loss","sequence":20},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"021--complete-loss--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"70f1c8fbe60570b6a6d0bd7b7babc865d5158c136c3e7ece41987161222c6f29","scenario_class":"complete-loss","sequence":21},{"execution_order":1,"method":"product","receipt_name":"022--complete-loss--r2--product.json","repetition":2,"row_sha256":"d2bdc12ad83800c151e6d0d9287b279699c6dd3e6f089df04fd290ff3692583d","scenario_class":"complete-loss","sequence":22},{"execution_order":2,"method":"ordinary-git","receipt_name":"023--complete-loss--r2--ordinary-git.json","repetition":2,"row_sha256":"e585ea98590a2d9d2ad8e4609addda70a390c370531d0f1d64304271016a991a","scenario_class":"complete-loss","sequence":23},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"024--complete-loss--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"728838c0c63d3a341697b06f907e4b48d3296918c9a78a74575f45fda2faf4c4","scenario_class":"complete-loss","sequence":24},{"execution_order":1,"method":"product","receipt_name":"025--complete-loss--r3--product.json","repetition":3,"row_sha256":"6f8e2fcadefbdb9ea598d6d25666cc45e995aedf9f4056474d30fc5676f4cf10","scenario_class":"complete-loss","sequence":25},{"execution_order":2,"method":"ordinary-git","receipt_name":"026--complete-loss--r3--ordinary-git.json","repetition":3,"row_sha256":"e1a48948060bdabbd37a26f9729be2623583ff1c7bfc51d836b119fcabf76013","scenario_class":"complete-loss","sequence":26},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"027--complete-loss--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"2dda42922736885cd6ccd57c6e71469bca9bbf86ffeaddf57704030dd8494ddf","scenario_class":"complete-loss","sequence":27},{"execution_order":1,"method":"ordinary-git","receipt_name":"028--partial-loss--r1--ordinary-git.json","repetition":1,"row_sha256":"006f4bca238a5083b8507cbbf1172c1817eb7491e237ad3c52faa6e8e17488d6","scenario_class":"partial-loss","sequence":28},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"029--partial-loss--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"a51a56a862ec4d840e1d557748784a6410d89776d4311d3494db26e675b0c095","scenario_class":"partial-loss","sequence":29},{"execution_order":3,"method":"product","receipt_name":"030--partial-loss--r1--product.json","repetition":1,"row_sha256":"ebae460545116a1ef6fc21dfa5c555904e865d2bd894f647d65f8a3746d0eabd","scenario_class":"partial-loss","sequence":30},{"execution_order":1,"method":"ordinary-git","receipt_name":"031--partial-loss--r2--ordinary-git.json","repetition":2,"row_sha256":"837c4228f1b8ad0101f7574bf4a418addc0dc258e54a00dfc70a6ef35f11beb7","scenario_class":"partial-loss","sequence":31},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"032--partial-loss--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"3686cdc3f8bd5e67df8548e25a2a3982e7e4695fcec653a6a567f862d0feb1e0","scenario_class":"partial-loss","sequence":32},{"execution_order":3,"method":"product","receipt_name":"033--partial-loss--r2--product.json","repetition":2,"row_sha256":"d283400a25155fd109e6740e8191a9c9a323b04269b242cc83f1727530f21c06","scenario_class":"partial-loss","sequence":33},{"execution_order":1,"method":"ordinary-git","receipt_name":"034--partial-loss--r3--ordinary-git.json","repetition":3,"row_sha256":"2c92f9e71caadc70173d016296ed92d3d7a1fb9235b1e058543e4a8530a6eca0","scenario_class":"partial-loss","sequence":34},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"035--partial-loss--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"e984f5966b6bf073d81a570b2545033110c9ef8a203c34e68a055d139fbab7c8","scenario_class":"partial-loss","sequence":35},{"execution_order":3,"method":"product","receipt_name":"036--partial-loss--r3--product.json","repetition":3,"row_sha256":"553dfb86c022576a83e7e9a58a9c8227de856bf950b9754237457357e4f4b4e7","scenario_class":"partial-loss","sequence":36},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"037--conflicting-stale--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"d62d085394b3c6f4ccc8049e8b7f34f363cfa8d4650bb18e785c74ef7ed8fbea","scenario_class":"conflicting-stale","sequence":37},{"execution_order":2,"method":"product","receipt_name":"038--conflicting-stale--r1--product.json","repetition":1,"row_sha256":"a145eca12e2bf2680b799f9eee7e826dd7881dc94ab9e9806a7e2e950bfe2a67","scenario_class":"conflicting-stale","sequence":38},{"execution_order":3,"method":"ordinary-git","receipt_name":"039--conflicting-stale--r1--ordinary-git.json","repetition":1,"row_sha256":"481cad49bdb19ce7c4cb310f2036975f4d1355099e15bc150b5382cce0c564fd","scenario_class":"conflicting-stale","sequence":39},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"040--conflicting-stale--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"1b7d47e4b862f022fe54e55dbbe265413c18666ceb142225af06741edf773eae","scenario_class":"conflicting-stale","sequence":40},{"execution_order":2,"method":"product","receipt_name":"041--conflicting-stale--r2--product.json","repetition":2,"row_sha256":"934b973395074ea9893acc162bc5cd90ec4c44cc430d538e5c85c4be3790a711","scenario_class":"conflicting-stale","sequence":41},{"execution_order":3,"method":"ordinary-git","receipt_name":"042--conflicting-stale--r2--ordinary-git.json","repetition":2,"row_sha256":"2fe1c1b1c1df27f4a89d30d70b606fedad400c936fa088087cd735509cc026ee","scenario_class":"conflicting-stale","sequence":42},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"043--conflicting-stale--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"f5d239e84920307f76556647842d140c39103361fd8060fa4696656a51a91e45","scenario_class":"conflicting-stale","sequence":43},{"execution_order":2,"method":"product","receipt_name":"044--conflicting-stale--r3--product.json","repetition":3,"row_sha256":"593337ecc8ac8f55cd913ff03038eb9830c435dfe74d1ab4c3d0daf6e60ae0bb","scenario_class":"conflicting-stale","sequence":44},{"execution_order":3,"method":"ordinary-git","receipt_name":"045--conflicting-stale--r3--ordinary-git.json","repetition":3,"row_sha256":"db9e2c5c440360d6a487abd910cb070022da7e7ce27ae641a6aad70e4565e525","scenario_class":"conflicting-stale","sequence":45},{"execution_order":1,"method":"product","receipt_name":"046--clean-control--r1--product.json","repetition":1,"row_sha256":"607df8505b9d959a3463c57591dcebc79e9c3bad47539bdff2f12f9839032957","scenario_class":"clean-control","sequence":46},{"execution_order":2,"method":"ordinary-git","receipt_name":"047--clean-control--r1--ordinary-git.json","repetition":1,"row_sha256":"fa104fd0d608d3ae35b6412285342a1c27d8f82c640200205003078afde8bf5e","scenario_class":"clean-control","sequence":47},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"048--clean-control--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"b3faf6cf0833c91c5243fba32e05812ca24cb7381338e00aa0e65ca201954bfc","scenario_class":"clean-control","sequence":48},{"execution_order":1,"method":"product","receipt_name":"049--clean-control--r2--product.json","repetition":2,"row_sha256":"9816f500f9a04ca77d23f5a1e389faa0d8f03fbe088f2061cc7badd64e5a0b34","scenario_class":"clean-control","sequence":49},{"execution_order":2,"method":"ordinary-git","receipt_name":"050--clean-control--r2--ordinary-git.json","repetition":2,"row_sha256":"3f29a7ffeb7a4021ef47ae086f9f8023d6068e8aaeae7ebb8807fe17e813d2b8","scenario_class":"clean-control","sequence":50},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"051--clean-control--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"ee09e31e3e2fb83cc6723f518278db8ba2965aa5a4c879953b240f8d22af6166","scenario_class":"clean-control","sequence":51},{"execution_order":1,"method":"product","receipt_name":"052--clean-control--r3--product.json","repetition":3,"row_sha256":"c11315bf8ff9252331e1d742f5a4483c35b7448a254c4f2f697afaad81f40227","scenario_class":"clean-control","sequence":52},{"execution_order":2,"method":"ordinary-git","receipt_name":"053--clean-control--r3--ordinary-git.json","repetition":3,"row_sha256":"fde23d5ba2758c22986b5fa394095c319fac97526be4597ebe3ae3c303d16f26","scenario_class":"clean-control","sequence":53},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"054--clean-control--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"da1abe76f65b9e42f2e9939120150abd0cc2c402d2f11cc1e63451e7b068d6c7","scenario_class":"clean-control","sequence":54}],"scenario_classes":["committed-only","committed-plus-uncommitted","complete-loss","partial-loss","conflicting-stale","clean-control"],"version":"hardening-gate6-execution-manifest-v1"}
```

## FILE: HARDENING_GATE6_SOURCE_BINDING_R3.md

```text
# Hardening Gate 6 — Source and Policy Binding R3

- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `COMPARATIVE_SHA256`: `f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec`
- `VERIFIER_SHA256`: `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`
- `GATE4_PROTOCOL_R2_SHA256`: `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`
- `LINUX_TOOL_PROVENANCE_SHA256`: `ce370290c11efe44eccc3d021b6074edc294b5f0ffaebd6e48af5021aac22c05`
- `SECCOMP_LAUNCHER_SHA256`: `64a4c1d7e68238dbeb4959a8bc52cba0b0aaa5499131a145e0b31d5cb8c52ab3`
- `R3_RUNNER_SHA256`: `f86388fe4ee8c677bd8a7699b0595d7b1e1c92bc681eea047643b1d4df2b88a4`
- `R3_MANIFEST_FILE_SHA256`: `a4c7c12c135475b712199916a8257b90543a1dd2b346e15bb6519f1d9ec80d3d`
- `R3_MANIFEST_EMBEDDED_SHA256`: `1e73682e0eb880c95f5826d731cf6c1b6fe1f61e342bfb2d36c7fd1d3600d711`
- `LIFECYCLE_GUARD_SHA256`: `4644aa756f47c3d53b82c239657ce22605d4a9caab3e6a8651c4f459d95c6f0c`
- `RUNPOD_POLICY_SHA256`: `6dfe19f3fd8be6c86f864190f633ec6052ce0276cad94fa76386b73a19031694`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`

`git diff` from the immutable candidate commit across the comparative source,
deterministic verifier, and scenario seeds is empty. R3 adds only orchestration,
isolation, lifecycle, and evidence infrastructure. The product candidate and
comparison semantics are unchanged.
```

## FILE: HARDENING_GATE6_LOCAL_PREFLIGHT_RECEIPT_R3.md

```text
# Hardening Gate 6 — Local Preflight Receipt R3

- `STATUS`: `LOCAL_PREFLIGHT_GREEN_NOT_PROVIDER_EVIDENCE`
- `EXECUTION_REVISION`: `R3`
- `PARENT_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `RUNPOD_WORKERS_CREATED_R3`: `0`
- `RUNPOD_ACTIVE_INVENTORY`: `[]`
- `RUNPOD_COST_STATE_R3`: `EXACT_$0.00`
- `UTC_RECORDED`: `2026-07-28T01:22:12Z`

## Mechanical results

- R2 plus R3 Gate 6 unit tests: `7/7 PASS`.
- Broader project regression: `271/271 PASS` across `24` established test
  files, including the new R3 tests.
- Test-log aggregate SHA-256: `ffce7ff7ba9a80090c365e9c974d941c32b040bf21a548969eaed591be7174db`.
- Exact 54-row R3 manifest validation: `PASS`.
- Manifest embedded SHA-256:
  `1e73682e0eb880c95f5826d731cf6c1b6fe1f61e342bfb2d36c7fd1d3600d711`.
- Manifest file SHA-256:
  `a4c7c12c135475b712199916a8257b90543a1dd2b346e15bb6519f1d9ec80d3d`.
- Python byte compilation: `PASS`.
- x32 ABI kill branch and all-descriptor inherited-socket rejection: `PASS`
  under structural unit tests; live kernel proof remains remote-canary gated.
- `git diff --check`: `PASS`.
- Candidate comparative/verifier/scenario diff from candidate commit: empty.
- Current RunPod running inventory: empty; Gate 6 campaign-scoped active
  inventory: empty.

## Platform limitation

The local host is macOS arm64 and cannot execute the Linux x86_64 seccomp
filter. Local tests validate the BPF instruction structure, foreign-architecture
kill branch, syscall deny coverage, R3 manifest, and fail-closed attestation
wall. Direct kernel proof remains mandatory in the capability-only RunPod
canary before benchmark upload. This receipt is not Linux, RunPod, measured,
network-denial, or Gate 6 completion evidence.
```

## FILE: HARDENING_GATE6_LINUX_TOOL_PROVENANCE_R2.json

```text
{"architecture":"x86_64","execution_revision":"R2","git":{"deb_sha256":"8794fcf2c4606c445df0db3dc963c8fb852772208bfb12727a12717c03767af7","package":"git_2.34.1-1ubuntu1.17_amd64.deb","path":"/usr/bin/git","sha256":"587ef21868c948b883993e23209b86a72a6ddc06aab1545c697ffc31075acd4a","source":"Ubuntu jammy security package","version":"git version 2.34.1"},"image":{"linux_amd64_manifest_digest":"sha256:27b844c0606ec6e5550fa90bc6647c4b41cf4ee53a44781bd3dbff8ca1beb297","name":"runpod/base:1.0.2-ubuntu2204","registry_index_digest":"sha256:ffe1c3b1ec997f7eaaef8561c2a701792c79ece19754d528222a14ee25d24cb0"},"platform":"Linux","product":{"path":"bundle/p4-verifier/verifier.py","sha256":"a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40","version":"p4-deterministic-verifier-v1"},"python":{"path":"/usr/bin/python3","sha256":"d6bca2b84e73c7775a0dd5e6a76899cfe4ee62863d7c8f88513811d1fda23f49","source":"prior direct runtime attestation from the same immutable image digest; mandatory remote byte recheck before measurement","version":"Python 3.10.12"},"restic":{"archive_sha256":"13176fe6d89d4357947a2cd107218ab2873a5f9d8e1ac2d4cd1c8e07e6839c21","path":"/workspace/ck-gate6-20260727-run1-r2/bundle/runtime/restic","sha256":"ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c","source":"official Restic 0.19.0 Linux amd64 release","version":"restic 0.19.0 compiled with go1.26.4 on linux/amd64"},"version":"hardening-gate6-linux-tool-provenance-v1"}
```

## FILE: hardening-gate6/seccomp_exec.py

```text
#!/usr/bin/env python3
"""Install an inherited, fail-closed network-denial seccomp filter and exec.

This launcher is Gate 6 execution infrastructure. It is not product code.  It
must run as an unprivileged Linux x86_64 user with no effective capabilities.
The filter is installed after ``no_new_privs`` and is inherited by every child.
"""
from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
from typing import Any


AUDIT_ARCH_X86_64 = 0xC000003E
BPF_LD = 0x00
BPF_W = 0x00
BPF_ABS = 0x20
BPF_JMP = 0x05
BPF_JEQ = 0x10
BPF_JSET = 0x40
BPF_K = 0x00
BPF_RET = 0x06
SECCOMP_RET_KILL_PROCESS = 0x80000000
SECCOMP_RET_ERRNO = 0x00050000
SECCOMP_RET_ALLOW = 0x7FFF0000
PR_SET_NO_NEW_PRIVS = 38
PR_SET_SECCOMP = 22
SECCOMP_MODE_FILTER = 2
X32_SYSCALL_BIT = 0x40000000

# Linux x86_64. Socket operations are denied directly. The additional entries
# close alternate kernel interfaces that can submit network work or acquire a
# socket descriptor without calling socket(2) in the filtered process.
DENIED_SYSCALLS = {
    "socket": 41,
    "connect": 42,
    "accept": 43,
    "sendto": 44,
    "recvfrom": 45,
    "sendmsg": 46,
    "recvmsg": 47,
    "shutdown": 48,
    "bind": 49,
    "listen": 50,
    "getsockname": 51,
    "getpeername": 52,
    "socketpair": 53,
    "setsockopt": 54,
    "getsockopt": 55,
    "unshare": 272,
    "accept4": 288,
    "recvmmsg": 299,
    "setns": 308,
    "sendmmsg": 307,
    "bpf": 321,
    "io_uring_setup": 425,
    "io_uring_enter": 426,
    "io_uring_register": 427,
    "pidfd_getfd": 438,
}


class SockFilter(ctypes.Structure):
    _fields_ = [
        ("code", ctypes.c_ushort),
        ("jt", ctypes.c_ubyte),
        ("jf", ctypes.c_ubyte),
        ("k", ctypes.c_uint32),
    ]


class SockFprog(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ushort),
        ("filter", ctypes.POINTER(SockFilter)),
    ]


class IsolationError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def proc_status() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key] = value.strip()
    return values


def inherited_socket_fds() -> list[int]:
    found: list[int] = []
    for entry in Path("/proc/self/fd").iterdir():
        try:
            descriptor = int(entry.name)
            target = os.readlink(entry)
        except (OSError, ValueError):
            continue
        if target.startswith("socket:["):
            found.append(descriptor)
    return sorted(found)


def filter_spec() -> dict[str, Any]:
    return {
        "architecture": "x86_64",
        "audit_arch": AUDIT_ARCH_X86_64,
        "default_action": "ALLOW",
        "denied_action": "ERRNO_EPERM",
        "denied_syscalls": dict(sorted(DENIED_SYSCALLS.items())),
        "foreign_arch_action": "KILL_PROCESS",
        "version": "hardening-gate6-seccomp-network-deny-v1",
    }


def build_filter() -> tuple[Any, SockFprog]:
    instructions = [
        SockFilter(BPF_LD | BPF_W | BPF_ABS, 0, 0, 4),
        SockFilter(BPF_JMP | BPF_JEQ | BPF_K, 1, 0, AUDIT_ARCH_X86_64),
        SockFilter(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_KILL_PROCESS),
        SockFilter(BPF_LD | BPF_W | BPF_ABS, 0, 0, 0),
        # x32 uses the same AUDIT_ARCH with bit 30 set on the syscall number.
        # Kill that ABI rather than allowing its differently numbered sockets.
        SockFilter(BPF_JMP | BPF_JSET | BPF_K, 0, 1, X32_SYSCALL_BIT),
        SockFilter(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_KILL_PROCESS),
    ]
    for number in sorted(set(DENIED_SYSCALLS.values())):
        instructions.extend((
            SockFilter(BPF_JMP | BPF_JEQ | BPF_K, 0, 1, number),
            SockFilter(BPF_RET | BPF_K, 0, 0,
                       SECCOMP_RET_ERRNO | errno.EPERM),
        ))
    instructions.append(SockFilter(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_ALLOW))
    array_type = SockFilter * len(instructions)
    filters = array_type(*instructions)
    return filters, SockFprog(len(instructions), filters)


def install_filter() -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                           ctypes.c_ulong, ctypes.c_ulong]
    libc.prctl.restype = ctypes.c_int
    if libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:
        value = ctypes.get_errno()
        raise IsolationError(f"NO_NEW_PRIVS_FAILED:{value}")
    filters, program = build_filter()
    if libc.prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER,
                  ctypes.cast(ctypes.pointer(program), ctypes.c_void_p).value,
                  0, 0) != 0:
        value = ctypes.get_errno()
        raise IsolationError(f"SECCOMP_FILTER_FAILED:{value}")
    # Keep the backing array alive until prctl has copied the filter.
    del filters


def network_probe() -> int:
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError as error:
        if error.errno == errno.EPERM:
            return error.errno
        raise IsolationError(f"NETWORK_PROBE_WRONG_ERRNO:{error.errno}") from error
    raise IsolationError("NETWORK_PROBE_UNEXPECTEDLY_ALLOWED")


def validate_host() -> dict[str, Any]:
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise IsolationError("PLATFORM_MUST_BE_LINUX_X86_64")
    if os.geteuid() == 0 or os.getuid() == 0:
        raise IsolationError("USER_MUST_BE_UNPRIVILEGED")
    status = proc_status()
    if int(status.get("CapEff", "-1"), 16) != 0:
        raise IsolationError("EFFECTIVE_CAPABILITIES_MUST_BE_ZERO")
    sockets = inherited_socket_fds()
    if sockets:
        raise IsolationError("INHERITED_SOCKET_FD_PRESENT")
    return {"cap_eff": status["CapEff"], "inherited_socket_fds": sockets}


def attest(path: Path) -> dict[str, Any]:
    status = proc_status()
    if status.get("NoNewPrivs") != "1" or status.get("Seccomp") != "2":
        raise IsolationError("KERNEL_STATUS_ATTESTATION_FAILED")
    socket_errno = network_probe()
    result = subprocess.run(["/bin/true"], check=False)
    if result.returncode != 0:
        raise IsolationError("EXEC_CANARY_FAILED")
    record: dict[str, Any] = {
        "version": "hardening-gate6-isolation-attestation-v1",
        "uid": os.getuid(),
        "euid": os.geteuid(),
        "gid": os.getgid(),
        "egid": os.getegid(),
        "cap_eff": status["CapEff"],
        "no_new_privs": int(status["NoNewPrivs"]),
        "seccomp_mode": int(status["Seccomp"]),
        "seccomp_filters": int(status.get("Seccomp_filters", "1")),
        "network_socket_probe_errno": socket_errno,
        "network_socket_probe_result": "DENIED_EPERM",
        "exec_canary": "PASS",
        "inherited_socket_fds": inherited_socket_fds(),
        "filter_spec": filter_spec(),
        "filter_spec_sha256": digest(filter_spec()),
    }
    record["attestation_sha256"] = digest(record)
    atomic_write(path, canonical(record))
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attestation", required=True, type=Path)
    parser.add_argument("--canary-only", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    host = validate_host()
    install_filter()
    record = attest(args.attestation.resolve())
    if args.canary_only:
        print(canonical({"status": "GREEN", **host,
                         "attestation_sha256": record["attestation_sha256"]}).decode())
        return 0
    if not args.command:
        raise IsolationError("COMMAND_REQUIRED")
    environment = dict(os.environ)
    environment["CK_GATE6_ISOLATION_ATTESTATION"] = str(args.attestation.resolve())
    environment["CK_GATE6_ISOLATION_ATTESTATION_SHA256"] = record["attestation_sha256"]
    os.execvpe(args.command[0], args.command, environment)
    return 127


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IsolationError as error:
        print(f"ISOLATION_BLOCKED:{error}", file=sys.stderr)
        raise SystemExit(70)
```

## FILE: hardening-gate6/run_campaign_r3.py

```text
#!/usr/bin/env python3
"""Gate 6 R3 seccomp-isolated measured campaign and evidence aggregator."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import socket
import sys


HERE = Path(__file__).resolve().parent


def load_r2():
    path = HERE / "run_campaign.py"
    spec = importlib.util.spec_from_file_location("gate6_campaign_r2_base", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("R2_BASE_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_r2()
R2_VALIDATE_MANIFEST = base.validate_manifest


def file_hash(path: Path) -> str:
    return base.file_hash(path)


def proc_status() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key] = value.strip()
    return values


def validate_isolation() -> dict[str, object]:
    if os.getuid() == 0 or os.geteuid() == 0:
        raise base.CampaignError("HOST_USER_MUST_BE_UNPRIVILEGED")
    status = proc_status()
    if int(status.get("CapEff", "-1"), 16) != 0:
        raise base.CampaignError("EFFECTIVE_CAPABILITIES_NOT_ZERO")
    if status.get("NoNewPrivs") != "1" or status.get("Seccomp") != "2":
        raise base.CampaignError("SECCOMP_KERNEL_STATE_INVALID")
    path_text = os.environ.get("CK_GATE6_ISOLATION_ATTESTATION", "")
    claimed = os.environ.get("CK_GATE6_ISOLATION_ATTESTATION_SHA256", "")
    path = Path(path_text)
    if not path.is_absolute() or not path.is_file() or file_hash(path) != claimed:
        raise base.CampaignError("ISOLATION_ATTESTATION_BINDING_INVALID")
    record = json.loads(path.read_bytes())
    body = {key: value for key, value in record.items()
            if key != "attestation_sha256"}
    if (record.get("attestation_sha256") != base.digest(body) or
            record.get("attestation_sha256") != claimed or
            record.get("uid") == 0 or record.get("euid") == 0 or
            int(record.get("cap_eff", "-1"), 16) != 0 or
            record.get("no_new_privs") != 1 or
            record.get("seccomp_mode") != 2 or
            record.get("network_socket_probe_result") != "DENIED_EPERM" or
            record.get("exec_canary") != "PASS" or
            record.get("inherited_socket_fds") != []):
        raise base.CampaignError("ISOLATION_ATTESTATION_CONTENT_INVALID")
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError as error:
        if error.errno != 1:
            raise base.CampaignError("NETWORK_DENIAL_WRONG_ERRNO") from error
    else:
        raise base.CampaignError("NETWORK_DENIAL_NOT_ENFORCED")
    return record


def validate_manifest_r3(manifest: object):
    if not isinstance(manifest, dict):
        raise base.CampaignError("MANIFEST_TYPE_INVALID")
    if manifest.get("execution_revision") != "R3":
        raise base.CampaignError("MANIFEST_REVISION_INVALID")
    translated = dict(manifest)
    translated["execution_revision"] = "R2"
    translated_body = {key: value for key, value in translated.items()
                       if key != "manifest_sha256"}
    translated["manifest_sha256"] = base.digest(translated_body)
    rows = R2_VALIDATE_MANIFEST(translated)
    original_body = {key: value for key, value in manifest.items()
                     if key != "manifest_sha256"}
    if manifest.get("manifest_sha256") != base.digest(original_body):
        raise base.CampaignError("MANIFEST_HASH_MISMATCH")
    return rows


def main() -> int:
    # The R2 engine remains byte-preserved; only its R2 revision check and
    # unshare wrapper are replaced. Every child inherits this process's filter.
    original_validate = base.validate_manifest
    original_run = base.subprocess.run
    original_aggregate = base.aggregate

    def validate(manifest: object):
        return validate_manifest_r3(manifest)

    def inherited_run(command, *args, **kwargs):
        if isinstance(command, list) and command and str(command[0]).endswith("unshare"):
            command = command[5:]
        return original_run(command, *args, **kwargs)

    def aggregate(receipts, raw_sizes, manifest, final_checkpoint):
        translated = dict(manifest)
        translated["execution_revision"] = "R2"
        translated_body = {key: value for key, value in translated.items()
                           if key != "manifest_sha256"}
        translated["manifest_sha256"] = base.digest(translated_body)
        result = original_aggregate(receipts, raw_sizes, translated,
                                    final_checkpoint)
        result["execution_revision"] = "R3"
        result["campaign_id"] = manifest["campaign_id"]
        result["manifest_sha256"] = manifest["manifest_sha256"]
        result["limitations"].append(
            "KERNEL_SECCOMP_NETWORK_DENIAL_NOT_NETWORK_NAMESPACE"
        )
        result["aggregate_sha256"] = base.digest({
            key: value for key, value in result.items()
            if key != "aggregate_sha256"
        })
        return result

    if "--validate-only" not in sys.argv[1:]:
        validate_isolation()
    base.validate_manifest = validate
    base.subprocess.run = inherited_run
    base.aggregate = aggregate
    original_argv = sys.argv
    try:
        sys.argv = [str(HERE / "run_campaign.py"), *sys.argv[1:]]
        return base.main()
    finally:
        sys.argv = original_argv
        base.validate_manifest = original_validate
        base.subprocess.run = original_run
        base.aggregate = original_aggregate


if __name__ == "__main__":
    raise SystemExit(main())
```

## FILE: hardening-gate6/test_campaign_r3.py

```text
#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


manifest_module = load("gate6_manifest_r3", ROOT / "make_manifest_r3.py")
runner = load("gate6_runner_r3", ROOT / "run_campaign_r3.py")
launcher = load("gate6_seccomp", ROOT / "seccomp_exec.py")


class Gate6R3Tests(unittest.TestCase):
    def test_manifest_is_exactly_54_r3_rows(self):
        manifest = manifest_module.build()
        rows = runner.validate_manifest_r3(manifest)
        self.assertEqual(manifest["execution_revision"], "R3")
        self.assertEqual(len(rows), 54)

    def test_manifest_revision_tamper_fails(self):
        manifest = manifest_module.build()
        manifest["execution_revision"] = "R2"
        with self.assertRaisesRegex(runner.base.CampaignError,
                                    "MANIFEST_REVISION_INVALID"):
            runner.validate_manifest_r3(manifest)

    def test_filter_denies_all_declared_network_paths(self):
        required = {
            "socket", "connect", "accept", "sendto", "recvfrom",
            "sendmsg", "recvmsg", "socketpair", "accept4", "recvmmsg",
            "sendmmsg", "io_uring_setup", "bpf", "pidfd_getfd",
        }
        self.assertTrue(required.issubset(launcher.DENIED_SYSCALLS))
        filters, program = launcher.build_filter()
        self.assertEqual(program.length, 7 + 2 * len(set(
            launcher.DENIED_SYSCALLS.values())))
        self.assertEqual(len(filters), program.length)

    def test_foreign_arch_is_killed_and_default_allows(self):
        filters, _ = launcher.build_filter()
        self.assertEqual(filters[2].k, launcher.SECCOMP_RET_KILL_PROCESS)
        self.assertEqual(filters[4].k, launcher.X32_SYSCALL_BIT)
        self.assertEqual(filters[5].k, launcher.SECCOMP_RET_KILL_PROCESS)
        self.assertEqual(filters[-1].k, launcher.SECCOMP_RET_ALLOW)


if __name__ == "__main__":
    unittest.main()
```

## FILE: hardening-gate6/run_campaign.py

```text
#!/usr/bin/env python3
"""Gate 6 R2 process-isolated measured campaign and evidence aggregator."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import statistics
import subprocess
import sys
import time
from typing import Any


EXPECTED_CANDIDATE = "8718fbecc2b145ff36ce8c3ed655e92b5906aeab"
EXPECTED_PROTOCOL = "a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52"
EXPECTED_RESTIC = "ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c"
SCENARIOS = (
    "committed-only", "committed-plus-uncommitted", "complete-loss",
    "partial-loss", "conflicting-stale", "clean-control",
)
METHODS = ("ordinary-git", "git-plus-restic-0.19.0", "product")
ZERO_HASH = "0" * 64


class CampaignError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else canonical(value)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def file_hash(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load_comparative(path: Path):
    spec = importlib.util.spec_from_file_location("gate6_comparative", path)
    if spec is None or spec.loader is None:
        raise CampaignError("COMPARATIVE_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_manifest(manifest: Any) -> list[dict[str, Any]]:
    if not isinstance(manifest, dict):
        raise CampaignError("MANIFEST_TYPE_INVALID")
    claimed = manifest.get("manifest_sha256")
    body = {key: value for key, value in manifest.items()
            if key != "manifest_sha256"}
    if claimed != digest(body):
        raise CampaignError("MANIFEST_HASH_MISMATCH")
    if (manifest.get("version") != "hardening-gate6-execution-manifest-v1" or
            manifest.get("execution_revision") != "R2" or
            manifest.get("candidate_commit") != EXPECTED_CANDIDATE or
            manifest.get("evidence_mode") != "MEASURED_GATE6" or
            not str(manifest.get("campaign_id", "")).startswith("ck-gate6-") or
            manifest.get("row_count") != 54 or
            tuple(manifest.get("scenario_classes", [])) != SCENARIOS or
            tuple(manifest.get("methods", [])) != METHODS or
            manifest.get("repetitions") != [1, 2, 3] or
            manifest.get("recovery_budget_seconds") != 180):
        raise CampaignError("MANIFEST_CONTROL_INVALID")
    rows = manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != 54:
        raise CampaignError("MANIFEST_ROWS_INVALID")
    combinations: set[tuple[str, int, str]] = set()
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise CampaignError("MANIFEST_ROW_TYPE_INVALID")
        claimed_row = row.get("row_sha256")
        row_body = {key: value for key, value in row.items()
                    if key != "row_sha256"}
        if claimed_row != digest(row_body) or row.get("sequence") != index:
            raise CampaignError("MANIFEST_ROW_HASH_INVALID")
        key = (row.get("scenario_class"), row.get("repetition"),
               row.get("method"))
        if (key[0] not in SCENARIOS or key[1] not in (1, 2, 3) or
                key[2] not in METHODS or key in combinations or
                row.get("execution_order") not in (1, 2, 3) or
                not re.fullmatch(r"[0-9]{3}--[a-z0-9.-]+--r[123]--[a-z0-9.+-]+\.json",
                                 str(row.get("receipt_name", "")))):
            raise CampaignError("MANIFEST_ROW_INVALID")
        combinations.add(key)
    expected = {(scenario, repetition, method)
                for scenario in SCENARIOS for repetition in (1, 2, 3)
                for method in METHODS}
    if combinations != expected:
        raise CampaignError("MANIFEST_COVERAGE_INVALID")
    for scenario_index, scenario in enumerate(SCENARIOS):
        rotation = scenario_index % 3
        expected_order = METHODS[rotation:] + METHODS[:rotation]
        for repetition in (1, 2, 3):
            actual = tuple(row["method"] for row in rows
                           if row["scenario_class"] == scenario and
                           row["repetition"] == repetition)
            if actual != expected_order:
                raise CampaignError("MANIFEST_ROTATION_INVALID")
    return rows


def validate_tools(tools: Any, git: Path, restic: Path, python: Path) -> None:
    expected = {
        "platform": "Linux",
        "architecture": "x86_64",
        "git": {"path": str(git), "sha256": file_hash(git)},
        "restic": {"path": str(restic), "sha256": file_hash(restic)},
        "python": {"path": str(python), "sha256": file_hash(python)},
    }
    for key in ("platform", "architecture"):
        if tools.get(key) != expected[key]:
            raise CampaignError("TOOL_PLATFORM_DRIFT")
    for name in ("git", "restic", "python"):
        item = tools.get(name)
        if not isinstance(item, dict):
            raise CampaignError("TOOL_RECORD_INVALID")
        if item.get("path") != expected[name]["path"] or item.get("sha256") != expected[name]["sha256"]:
            raise CampaignError(f"{name.upper()}_PROVENANCE_DRIFT")
    if tools["restic"].get("sha256") != EXPECTED_RESTIC:
        raise CampaignError("RESTIC_HASH_INVALID")


def append_checkpoint(path: Path, sequence: int, row: dict[str, Any],
                      receipt: dict[str, Any], prior_hash: str) -> str:
    event = {
        "version": "hardening-gate6-checkpoint-v1",
        "sequence": sequence,
        "row_sha256": row["row_sha256"],
        "receipt_sha256": receipt["receipt_sha256"],
        "previous_event_sha256": prior_hash,
    }
    event["event_sha256"] = digest(event)
    raw = canonical(event) + b"\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(descriptor, "ab", closefd=True) as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return event["event_sha256"]


def median(values: list[int | float]) -> int | float:
    return statistics.median(values)


def aggregate(receipts: list[dict[str, Any]], raw_sizes: dict[str, int],
              manifest: dict[str, Any], final_checkpoint: str) -> dict[str, Any]:
    if len(receipts) != 54:
        raise CampaignError("RECEIPT_COUNT_INVALID")
    pairs: list[dict[str, Any]] = []
    pair_match_counts = {name: 0 for name in
                         ("source", "event", "loss", "allowed_information")}
    retention_outcomes = {method: {"wins": 0, "ties": 0, "losses": 0}
                          for method in METHODS}
    for scenario in SCENARIOS:
        for repetition in (1, 2, 3):
            group = [item for item in receipts
                     if item["scenario_class"] == scenario and
                     item["repetition"] == repetition]
            if len(group) != 3 or {item["method"] for item in group} != set(METHODS):
                raise CampaignError("PAIR_COVERAGE_INVALID")
            hash_fields = {
                "source": "source_manifest_sha256",
                "event": "event_stream_sha256",
                "loss": "loss_receipt_sha256",
                "allowed_information": "allowed_information_sha256",
            }
            for label, field in hash_fields.items():
                if len({item[field] for item in group}) != 1:
                    raise CampaignError(f"PAIR_{label.upper()}_HASH_MISMATCH")
                pair_match_counts[label] += 1
            ratios = {item["method"]: item["declared_work_units_retained"] /
                      item["declared_work_units_total"] for item in group}
            best = max(ratios.values())
            winners = {method for method, value in ratios.items() if value == best}
            for method in METHODS:
                if method in winners and len(winners) == 1:
                    retention_outcomes[method]["wins"] += 1
                elif method in winners:
                    retention_outcomes[method]["ties"] += 1
                else:
                    retention_outcomes[method]["losses"] += 1
            pairs.append({
                "scenario_class": scenario,
                "repetition": repetition,
                "hashes": {label: group[0][field]
                           for label, field in hash_fields.items()},
                "methods": {item["method"]: {
                    "receipt_sha256": item["receipt_sha256"],
                    "operation_status": item["operation_status"],
                    "retention_ratio": ratios[item["method"]],
                    "manifest_exact_match": item["manifest_exact_match"],
                    "executable_continuation_pass": item["executable_continuation_pass"],
                    "unsafe_acceptance": item["unsafe_acceptance"],
                } for item in group},
            })
    method_summary: dict[str, Any] = {}
    for method in METHODS:
        items = [item for item in receipts if item["method"] == method]
        ratios = [item["declared_work_units_retained"] /
                  item["declared_work_units_total"] for item in items]
        method_summary[method] = {
            "execution_count": len(items),
            "operation_status_counts": {status: sum(item["operation_status"] == status
                                                     for item in items)
                                         for status in sorted({item["operation_status"]
                                                               for item in items})},
            "manifest_exact_match": [sum(item["manifest_exact_match"] for item in items), len(items)],
            "executable_continuation_pass": [sum(item["executable_continuation_pass"] for item in items), len(items)],
            "unsafe_acceptance": [sum(item["unsafe_acceptance"] for item in items), len(items)],
            "retention_ratio_raw": ratios,
            "retention_ratio_median": median(ratios),
            "retention_ratio_min": min(ratios),
            "retention_ratio_max": max(ratios),
            "recovery_ms_raw": [item["wall_clock_recovery_ms"] for item in items],
            "recovery_ms_median": median([item["wall_clock_recovery_ms"] for item in items]),
            "capture_overhead_ms_raw": [item["capture_overhead_ms"] for item in items],
            "capture_overhead_ms_median": median([item["capture_overhead_ms"] for item in items]),
            "storage_bytes_raw": [item["storage_bytes_pre_loss"] for item in items],
            "storage_bytes_median": median([item["storage_bytes_pre_loss"] for item in items]),
            "canonical_receipt_bytes_raw": [raw_sizes[item["receipt_sha256"]] for item in items],
            "canonical_receipt_bytes_median": median([raw_sizes[item["receipt_sha256"]] for item in items]),
            "retention_pair_outcomes": retention_outcomes[method],
        }
    result: dict[str, Any] = {
        "version": "hardening-gate6-aggregate-v1",
        "execution_revision": "R2",
        "status": "GREEN",
        "campaign_id": manifest["campaign_id"],
        "candidate_commit": EXPECTED_CANDIDATE,
        "manifest_sha256": manifest["manifest_sha256"],
        "measured_executions": len(receipts),
        "unique_combinations": len({(item["scenario_class"], item["repetition"], item["method"])
                                    for item in receipts}),
        "pair_count": len(pairs),
        "pair_hash_match_counts": pair_match_counts,
        "canonical_receipts_valid": sum(1 for _ in receipts),
        "cleanup_pass": sum(item["cleanup_pass"] for item in receipts),
        "residue_bytes": sum(item["residue_bytes_after_teardown"] for item in receipts),
        "unsafe_acceptance_count": sum(item["unsafe_acceptance"] for item in receipts),
        "original_workspace_mutation_count": sum(item["original_workspace_mutated_after_loss"] for item in receipts),
        "final_checkpoint_sha256": final_checkpoint,
        "method_summary": method_summary,
        "pairs": pairs,
        "limitations": [
            "SYNTHETIC_PAIRED_COMPARATIVE", "NOT_LIVE_AWS",
            "NOT_PRODUCT_SCALE", "RUNPOD_GENERIC_COMPUTE",
            "N_EQUALS_THREE_PER_CLASS_METHOD", "NO_POPULATION_INFERENCE",
            "PRODUCT_TEAM_AUTHORED_SCENARIOS_AND_SUCCESS_RULES",
            "RECEIPT_EVIDENCE_BYTES_FIELD_IS_PRE_RECEIPT_AND_ZERO; ACTUAL_CANONICAL_RECEIPT_BYTES_REPORTED_SEPARATELY",
        ],
    }
    if (result["unique_combinations"] != 54 or result["pair_count"] != 18 or
            set(pair_match_counts.values()) != {18} or
            result["canonical_receipts_valid"] != 54 or
            result["cleanup_pass"] != 54 or result["residue_bytes"] != 0 or
            result["unsafe_acceptance_count"] != 0 or
            result["original_workspace_mutation_count"] != 0):
        raise CampaignError("CAMPAIGN_INTEGRITY_INVALID")
    result["aggregate_sha256"] = digest(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--comparative", required=True, type=Path)
    parser.add_argument("--tools", required=True, type=Path)
    parser.add_argument("--git", required=True, type=Path)
    parser.add_argument("--restic", required=True, type=Path)
    parser.add_argument("--python", required=True, type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_bytes())
    rows = validate_manifest(manifest)
    comparative = load_comparative(args.comparative.resolve())
    if comparative.PROTOCOL_SHA256 != EXPECTED_PROTOCOL:
        raise CampaignError("PROTOCOL_HASH_DRIFT")
    if file_hash(args.comparative) != "f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec":
        raise CampaignError("COMPARATIVE_HASH_DRIFT")
    if args.validate_only:
        print(canonical({"status": "GREEN", "rows": len(rows),
                         "manifest_sha256": manifest["manifest_sha256"]}).decode())
        return 0
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise CampaignError("MEASURED_PLATFORM_INVALID")
    if os.geteuid() == 0:
        raise CampaignError("HOST_USER_MUST_BE_UNPRIVILEGED")
    unshare = shutil.which("unshare")
    if unshare is None:
        raise CampaignError("NETWORK_DENY_RUNTIME_MISSING")
    for path in (args.git, args.restic, args.python):
        if not path.resolve().is_file():
            raise CampaignError("TOOL_PATH_INVALID")
    tools = json.loads(args.tools.read_bytes())
    validate_tools(tools, args.git.resolve(), args.restic.resolve(), args.python.resolve())
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=False)
    receipts_root = output / "receipts"
    receipts_root.mkdir()
    checkpoints = output / "checkpoints.ndjson"
    child_env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "CK_GATE5_GIT": str(args.git.resolve()),
        "CK_GATE5_RESTIC": str(args.restic.resolve()),
    }
    receipts: list[dict[str, Any]] = []
    raw_sizes: dict[str, int] = {}
    prior_hash = ZERO_HASH
    started = time.monotonic()
    for row in rows:
        destination = receipts_root / row["receipt_name"]
        command = [
            unshare, "--user", "--map-root-user", "--net", "--mount-proc",
            str(args.python.resolve()), str(args.comparative.resolve()),
            row["scenario_class"], str(row["repetition"]), row["method"],
            str(destination), "--campaign-id", manifest["campaign_id"],
            "--candidate-commit", EXPECTED_CANDIDATE,
            "--execution-order", str(row["execution_order"]),
            "--evidence-mode", "MEASURED_GATE6",
        ]
        result = subprocess.run(command, cwd=args.comparative.resolve().parents[1],
                                env=child_env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, check=False, timeout=240)
        if result.returncode != 0:
            raise CampaignError(f"ROW_EXECUTION_FAILED:{row['sequence']}:{digest(result.stdout)}")
        raw = destination.read_bytes()
        receipt = comparative.validate_receipt(json.loads(raw), raw)
        if (receipt["campaign_id"] != manifest["campaign_id"] or
                receipt["candidate_commit"] != EXPECTED_CANDIDATE or
                receipt["evidence_mode"] != "MEASURED_GATE6" or
                receipt["runtime_platform"] != "Linux" or
                receipt["scenario_class"] != row["scenario_class"] or
                receipt["repetition"] != row["repetition"] or
                receipt["method"] != row["method"] or
                receipt["execution_order"] != row["execution_order"] or
                not receipt["cleanup_pass"] or
                receipt["residue_bytes_after_teardown"] != 0):
            raise CampaignError("RECEIPT_CONTEXT_INVALID")
        for name, item_hash in receipt["tool_binary_sha256"].items():
            if item_hash != tools[name]["sha256"]:
                raise CampaignError(f"RECEIPT_{name.upper()}_PROVENANCE_DRIFT")
            if receipt["tool_versions"][name] != tools[name]["version"]:
                raise CampaignError(f"RECEIPT_{name.upper()}_VERSION_DRIFT")
        receipts.append(receipt)
        raw_sizes[receipt["receipt_sha256"]] = len(raw)
        prior_hash = append_checkpoint(checkpoints, row["sequence"], row,
                                       receipt, prior_hash)
    result = aggregate(receipts, raw_sizes, manifest, prior_hash)
    result["elapsed_seconds"] = time.monotonic() - started
    result["aggregate_sha256"] = digest({key: value for key, value in result.items()
                                         if key != "aggregate_sha256"})
    atomic_write(output / "aggregate.json", result)
    evidence_files = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "evidence-manifest.json":
            evidence_files.append({
                "path": path.relative_to(output).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": file_hash(path),
            })
    evidence_manifest = {
        "version": "hardening-gate6-evidence-manifest-v1",
        "campaign_id": manifest["campaign_id"],
        "candidate_commit": EXPECTED_CANDIDATE,
        "files": evidence_files,
    }
    evidence_manifest["manifest_sha256"] = digest(evidence_manifest)
    atomic_write(output / "evidence-manifest.json", evidence_manifest)
    print(canonical({"status": "GREEN", "measured_executions": 54,
                     "aggregate_sha256": result["aggregate_sha256"],
                     "evidence_manifest_sha256": evidence_manifest["manifest_sha256"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## FILE: s2-soak/lifecycle_guard.py

```text
#!/usr/bin/env python3
"""Detached local exact-ID RunPod lifecycle guard.

This process runs on the operator host only. It receives one exact Pod ID,
expected name/campaign prefix, a hash-pinned runpodctl path, and absolute stop
and delete deadlines. It never enters the Pod and never transfers credentials.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


class GuardFailure(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, check=False)


class ChainLog:
    def __init__(self, path: Path) -> None:
        if path.exists():
            raise GuardFailure("LOG_ALREADY_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.previous = "0" * 64
        self.sequence = 0

    def emit(self, event: str, details: Any) -> dict[str, Any]:
        self.sequence += 1
        core = {"schema_version": "s2-guard-v1", "sequence": self.sequence,
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "monotonic_seconds": round(time.monotonic(), 3),
                "previous_hash": self.previous, "event": event,
                "details": details}
        record = {**core, "event_hash": hashlib.sha256(canonical(core)).hexdigest()}
        with self.path.open("ab") as handle:
            handle.write(canonical(record) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous = record["event_hash"]
        return record


def parse_json(result: subprocess.CompletedProcess[str]) -> Any:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise GuardFailure("MALFORMED_PROVIDER_JSON") from exc


def pod_get(cli: Path, pod_id: str) -> tuple[bool, dict[str, Any] | None, str]:
    result = run([str(cli), "pod", "get", pod_id, "--output", "json"])
    if result.returncode != 0:
        lowered = result.stdout.lower()
        if "404" in lowered or "not found" in lowered or "does not exist" in lowered:
            return False, None, result.stdout.strip()
        raise GuardFailure("POD_GET_FAILED:" + result.stdout[-500:])
    value = parse_json(result)
    if not isinstance(value, dict):
        raise GuardFailure("MALFORMED_POD_GET")
    return True, value, result.stdout.strip()


def campaign_active(cli: Path, campaign_prefix: str) -> list[dict[str, Any]]:
    result = run([str(cli), "pod", "list", "--all", "--output", "json"])
    if result.returncode != 0:
        raise GuardFailure("POD_LIST_FAILED:" + result.stdout[-500:])
    value = parse_json(result)
    if not isinstance(value, list):
        raise GuardFailure("MALFORMED_POD_LIST")
    return [item for item in value if isinstance(item, dict)
            and str(item.get("name", "")).startswith(campaign_prefix)
            and str(item.get("desiredStatus", "")).upper() not in
            {"EXITED", "TERMINATED", "DELETED"}]


def verify_identity(value: dict[str, Any], pod_id: str, expected_name: str,
                    campaign_prefix: str) -> None:
    if value.get("id") != pod_id:
        raise GuardFailure("POD_ID_MISMATCH")
    if value.get("name") != expected_name:
        raise GuardFailure("POD_NAME_MISMATCH")
    if not expected_name.startswith(campaign_prefix):
        raise GuardFailure("CAMPAIGN_MISMATCH")


def bounded_action(cli: Path, action: str, pod_id: str,
                   log: ChainLog) -> None:
    delays = (0, 2, 5)
    for attempt, delay in enumerate(delays, 1):
        if delay:
            time.sleep(delay)
        result = run([str(cli), "pod", action, pod_id, "--output", "json"])
        log.emit(action.upper() + "_ATTEMPT",
                 {"attempt": attempt, "exit": result.returncode,
                  "output_hash": hashlib.sha256(result.stdout.encode()).hexdigest()})
        if result.returncode == 0:
            return
        lowered = result.stdout.lower()
        if action == "delete" and ("404" in lowered or "not found" in lowered):
            return
    raise GuardFailure(action.upper() + "_RETRIES_EXHAUSTED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runpodctl", type=Path, required=True)
    parser.add_argument("--runpodctl-sha256", required=True)
    parser.add_argument("--pod-id", required=True)
    parser.add_argument("--pod-name", required=True)
    parser.add_argument("--campaign-prefix", required=True)
    parser.add_argument("--stop-epoch", type=int, required=True)
    parser.add_argument("--delete-epoch", type=int, required=True)
    parser.add_argument("--heartbeat-seconds", type=int, default=30)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    if args.heartbeat_seconds < 1 or args.delete_epoch <= args.stop_epoch:
        raise GuardFailure("INVALID_DEADLINE")
    cli = args.runpodctl.resolve()
    if not cli.is_file() or not os.access(cli, os.X_OK):
        raise GuardFailure("CLI_NOT_EXECUTABLE")
    log = ChainLog(args.log.resolve())
    stopped = False
    try:
        if sha256_file(cli) != args.runpodctl_sha256:
            raise GuardFailure("CLI_HASH_MISMATCH")
        present, value, _ = pod_get(cli, args.pod_id)
        if not present or value is None:
            raise GuardFailure("POD_ABSENT_AT_BIND")
        verify_identity(value, args.pod_id, args.pod_name, args.campaign_prefix)
        log.emit("BOUND", {"pod_id": args.pod_id, "name": args.pod_name,
                           "campaign_prefix": args.campaign_prefix,
                           "cli_sha256": args.runpodctl_sha256,
                           "stop_epoch": args.stop_epoch,
                           "delete_epoch": args.delete_epoch})
        while True:
            if sha256_file(cli) != args.runpodctl_sha256:
                raise GuardFailure("CLI_HASH_MISMATCH")
            present, value, raw = pod_get(cli, args.pod_id)
            if not present:
                active = campaign_active(cli, args.campaign_prefix)
                if active:
                    raise GuardFailure("EXACT_ID_ABSENT_CAMPAIGN_ACTIVE")
                log.emit("TEARDOWN_GREEN", {"exact_id_absent": True,
                                             "campaign_active": []})
                return 0
            assert value is not None
            verify_identity(value, args.pod_id, args.pod_name, args.campaign_prefix)
            now = int(time.time())
            log.emit("HEARTBEAT", {"pod_id": args.pod_id,
                                   "provider_state": value.get("desiredStatus"),
                                   "provider_record_hash": hashlib.sha256(raw.encode()).hexdigest(),
                                   "seconds_to_stop": args.stop_epoch - now,
                                   "seconds_to_delete": args.delete_epoch - now})
            if now >= args.delete_epoch:
                bounded_action(cli, "delete", args.pod_id, log)
            elif now >= args.stop_epoch and not stopped:
                bounded_action(cli, "stop", args.pod_id, log)
                stopped = True
            time.sleep(args.heartbeat_seconds)
    except Exception as exc:
        log.emit("GUARD_BLOCKED", {"type": type(exc).__name__, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```
