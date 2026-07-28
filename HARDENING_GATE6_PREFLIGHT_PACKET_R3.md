# Hardening Gate 6 — Same-Hash Preflight Judge Packet R3

## Judge contract

This is a non-authoring, sanitized, pre-provider review. Return a structured
verdict only. Do not write code, propose patches, direct implementation,
request tools or credentials, or claim execution. Review every included byte
as one packet. The external SHA-256 supplied with this packet is canonical.

Required verdict schema:

```json
{"verdict":"GREEN|NOT_GREEN|BLOCKED","candidate_immutability":"GREEN|NOT_GREEN","fairness_and_pairing":"GREEN|NOT_GREEN","runtime_isolation":"GREEN|NOT_GREEN","evidence_and_statistics":"GREEN|NOT_GREEN","lifecycle_and_teardown":"GREEN|NOT_GREEN","blockers":[],"limitations":[],"recusal":"CLEAR|REQUIRED"}
```

GREEN means the packet is safe and complete enough to create one reviewed CPU
worker and execute the frozen 54-row campaign. It does not predict a favorable
product result and does not approve later gates.

Control state: parent Gate 5 R2 is independently GREEN; orchestration commit is
`84efce4c188236935218790a88a23f9d29bf4d05`; immutable candidate is `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`; current
RunPod running inventory is empty; no Gate 6 R2 worker or measured row exists.

## FILE: HARDENING_GATE6_EXECUTION_PLAN_R2.md

```text
# Hardening Gate 6 — Execution Plan R2

- `TARGET_GATE`: `HARDENING_6_RUN1_GREEN`
- `EXECUTION_REVISION`: `R2`
- `PARENT_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `CAMPAIGN_ID`: `ck-gate6-20260727-run1-r2`
- `MEASURED_EXECUTIONS`: `54`
- `PAIRED_GROUPS`: `18`
- `RUNPOD_WORKERS`: `one successful measured worker; at most eight pre-upload creation attempts`
- `AGY_REQUIRED`: `false`

## Use, acceptance, and kill line

The campaign measures the frozen candidate against ordinary Git and Git plus
Restic under six declared synthetic loss constructs. It closes only if all 54
canonical receipts, all 18 equal-information pairs, raw aggregation, network
denial, custody, teardown, and same-hash independent reviews pass. A favorable
product score is not an acceptance condition.

Kill before measurement on candidate/contract/tool/payload drift, unequal pair
inputs or budget, unavailable unprivileged network denial, unknown price,
unbounded exposure, or a non-green required preflight judge. Kill during the
campaign on an invalid row or receipt, false promotion, unsafe acceptance,
mutation after loss/refusal, nondeterminism, residue, evidence-chain failure,
or inability to guarantee worker deletion.

## Frozen order

`HARDENING_GATE6_EXECUTION_MANIFEST_R2.json` contains every
`(scenario_class, repetition, method)` tuple exactly once. For each scenario,
the method order is the `scenario_index mod 3` rotation implemented and judged
at Gate 5. The same rotation is used for all three repetitions of a class.

Every row executes in a fresh process and trial root. The common candidate
harness emits the canonical receipt. Gate 6 orchestration validates but never
rewrites that receipt, then fsyncs a hash-chained checkpoint before advancing.

## Runtime and isolation

The generic CPU worker is the exact immutable image named in
`HARDENING_GATE6_LINUX_TOOL_PROVENANCE_R2.json`. Two vCPU and 4 GiB is
sufficient: the 18-execution local profile completed in 91.13 seconds with
98,598,912-byte maximum RSS. The 54-run estimate is approximately 274 seconds;
the six-hour workload ceiling is a fail-safe, not an expected duration.

Before measurement, the worker must:

1. match the reviewed CPU/RAM/image/disk/zero-volume/rate envelope;
2. verify the payload hash before extraction;
3. install only the hash-bound Ubuntu Git package already inside the payload;
4. match the frozen Git, Python, Restic, and product versions and byte hashes;
5. create a dedicated host-unprivileged `gate6` user;
6. prove `unshare --user --map-root-user --net --mount-proc` works for that
   user and blocks a forbidden network probe;
7. complete a non-measured canonical smoke in a fresh root;
8. prove the detached local exact-ID lifecycle guard is advancing.

No credential enters the payload or measured environment. Every measured
child receives only the frozen PATH and Git/Restic selectors. Its own trial
environment further reduces this to trial-local HOME and fixed locale/timezone
variables.

## Evidence and reporting

The runner preserves 54 raw canonical receipts, the 54-event checkpoint chain,
18 paired reports, per-method/class raw statistics, baseline wins/ties/losses,
unsupported and unfavorable outcomes, actual canonical receipt byte sizes,
runtime/tool evidence, and a complete file/hash manifest. It reports medians,
minima, maxima, and exact numerators/denominators without p-values or
population inference.

The canonical candidate's `evidence_bytes` field is zero because it is emitted
before the receipt file exists. Gate 6 does not rewrite it. The orchestration
separately measures and reports actual canonical receipt bytes; this limitation
is mandatory in the final packet.

The Gate 3 operator trace remains a separate hash-bound reference and is never
pooled with the 54 synthetic executions.

## Wall-7 decision

`AGY_REQUIRED=false`. The measured process performs no model call, prompt or
untrusted-content ingestion, memory write, agent dispatch, tool choice, or
external egress. GLM and Claude are out-of-band, non-authoring reviewers of a
sanitized frozen packet. This introduces no distinct Wall-7 mechanism beyond
the judge boundary already governed by packet hashing and deny-all authority.

## Required judges

Before worker creation and again after teardown, the exact same byte-complete
packet and canonical hash go to:

1. GLM for fairness, pairing, statistics, schema, and numerical completeness;
2. Claude Opus 4.8 through `claude-judge` for process isolation, lifecycle,
   evidence custody, teardown, and candidate immutability.

Both are non-authoring. The builder never self-approves.
```

## FILE: HARDENING_GATE6_EXECUTION_WIRING_R2.md

```text
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
```

## FILE: HARDENING_GATE6_EXECUTION_MANIFEST_R2.json

```text
{"campaign_id":"ck-gate6-20260727-run1-r2","candidate_commit":"8718fbecc2b145ff36ce8c3ed655e92b5906aeab","evidence_mode":"MEASURED_GATE6","execution_revision":"R2","manifest_sha256":"ffbe59a0fa569d9a1cfd1aa6247490a7606ab20a362a072b0d19ca5879ba3b07","methods":["ordinary-git","git-plus-restic-0.19.0","product"],"recovery_budget_seconds":180,"repetitions":[1,2,3],"rotation_rule":"scenario_index_mod_3_as_frozen_by_gate5_run_smoke","row_count":54,"rows":[{"execution_order":1,"method":"ordinary-git","receipt_name":"001--committed-only--r1--ordinary-git.json","repetition":1,"row_sha256":"479490b37b4214e81be6ad4a2be0cbbcc54378c83e0ecbcc267a6c5cf5de7db9","scenario_class":"committed-only","sequence":1},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"002--committed-only--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"60fc2873fe9c12dbf442abffa0208fe72b3ca6977e6b5cfe68840c4b55b9df53","scenario_class":"committed-only","sequence":2},{"execution_order":3,"method":"product","receipt_name":"003--committed-only--r1--product.json","repetition":1,"row_sha256":"ee7f9359c56172127c45b0f9189d0554b3c0c315e8fa8ecab5650b0b5de09cb0","scenario_class":"committed-only","sequence":3},{"execution_order":1,"method":"ordinary-git","receipt_name":"004--committed-only--r2--ordinary-git.json","repetition":2,"row_sha256":"8d47bcf59febb725847f84ee51b4eab07e4852f9e5e7fdac33f107377c88adb1","scenario_class":"committed-only","sequence":4},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"005--committed-only--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"47c6c30389e2f2ba09918f32fea6cf9694a88f23343e77711088c0c125235e25","scenario_class":"committed-only","sequence":5},{"execution_order":3,"method":"product","receipt_name":"006--committed-only--r2--product.json","repetition":2,"row_sha256":"afd76c4c2d6b181100f43aa144c6cb7e798a438b9c2159cac8d0cbf5f5f368b5","scenario_class":"committed-only","sequence":6},{"execution_order":1,"method":"ordinary-git","receipt_name":"007--committed-only--r3--ordinary-git.json","repetition":3,"row_sha256":"acb6b683e84339d2ce08ac71018781b647705aff0ec764ce14979ef2a83da761","scenario_class":"committed-only","sequence":7},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"008--committed-only--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"d1ef09296bb8d808ef27a8c0d3fcf7a0d6bc94a1560e5b8657e4c5b2be19c57d","scenario_class":"committed-only","sequence":8},{"execution_order":3,"method":"product","receipt_name":"009--committed-only--r3--product.json","repetition":3,"row_sha256":"399da93cc6269c8cbd9d78ac07e05d824c374dc6702b38b63e740a1f8375deed","scenario_class":"committed-only","sequence":9},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"010--committed-plus-uncommitted--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"92ff8ff99830dc29c9770627e48fa7ebfeae876b3d0e06f7ffdf05f0d22c65c0","scenario_class":"committed-plus-uncommitted","sequence":10},{"execution_order":2,"method":"product","receipt_name":"011--committed-plus-uncommitted--r1--product.json","repetition":1,"row_sha256":"b636b3e4f0cfc372dd5074020007d528aa0a7370b90be88e1cac09f1e6f82975","scenario_class":"committed-plus-uncommitted","sequence":11},{"execution_order":3,"method":"ordinary-git","receipt_name":"012--committed-plus-uncommitted--r1--ordinary-git.json","repetition":1,"row_sha256":"8179cff27d9a0114c086150fcc1ac744d041f6aa2680b77e87c9f07b2916061b","scenario_class":"committed-plus-uncommitted","sequence":12},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"013--committed-plus-uncommitted--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"b74e22822cf646da75a796fe5701c7c1d0e72b607cbe4e891db5ae4ff3d1ef67","scenario_class":"committed-plus-uncommitted","sequence":13},{"execution_order":2,"method":"product","receipt_name":"014--committed-plus-uncommitted--r2--product.json","repetition":2,"row_sha256":"7d3882e9786629d33e8246dc659fe3c0d27114ed10ee524a451272b558bdbb7c","scenario_class":"committed-plus-uncommitted","sequence":14},{"execution_order":3,"method":"ordinary-git","receipt_name":"015--committed-plus-uncommitted--r2--ordinary-git.json","repetition":2,"row_sha256":"1fbc00f5c459c0ed31c5f76f77e5a31080dbb4fb62d6a1570ca68b4051e8c37d","scenario_class":"committed-plus-uncommitted","sequence":15},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"016--committed-plus-uncommitted--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"af4271e7f9ab3c8fbc9c8ee78efb720035bcab29d982a1c2f60fd87839327f32","scenario_class":"committed-plus-uncommitted","sequence":16},{"execution_order":2,"method":"product","receipt_name":"017--committed-plus-uncommitted--r3--product.json","repetition":3,"row_sha256":"a7b6673e41c6a2df9bffae62a16fed04a221a122fe3a0295569b364daec1d458","scenario_class":"committed-plus-uncommitted","sequence":17},{"execution_order":3,"method":"ordinary-git","receipt_name":"018--committed-plus-uncommitted--r3--ordinary-git.json","repetition":3,"row_sha256":"3419162323edd35238a259f5b3abc2e184fedeb7380326f1851e7caf591a67a7","scenario_class":"committed-plus-uncommitted","sequence":18},{"execution_order":1,"method":"product","receipt_name":"019--complete-loss--r1--product.json","repetition":1,"row_sha256":"ba29258457f921553e5c9e37180cb11dcf7de13af8be3cbcf836176c9ed5a51f","scenario_class":"complete-loss","sequence":19},{"execution_order":2,"method":"ordinary-git","receipt_name":"020--complete-loss--r1--ordinary-git.json","repetition":1,"row_sha256":"a677b0b8c8be45091483fdb515f612b2d367958beec8ff32e3a4f40825468146","scenario_class":"complete-loss","sequence":20},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"021--complete-loss--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"70f1c8fbe60570b6a6d0bd7b7babc865d5158c136c3e7ece41987161222c6f29","scenario_class":"complete-loss","sequence":21},{"execution_order":1,"method":"product","receipt_name":"022--complete-loss--r2--product.json","repetition":2,"row_sha256":"d2bdc12ad83800c151e6d0d9287b279699c6dd3e6f089df04fd290ff3692583d","scenario_class":"complete-loss","sequence":22},{"execution_order":2,"method":"ordinary-git","receipt_name":"023--complete-loss--r2--ordinary-git.json","repetition":2,"row_sha256":"e585ea98590a2d9d2ad8e4609addda70a390c370531d0f1d64304271016a991a","scenario_class":"complete-loss","sequence":23},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"024--complete-loss--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"728838c0c63d3a341697b06f907e4b48d3296918c9a78a74575f45fda2faf4c4","scenario_class":"complete-loss","sequence":24},{"execution_order":1,"method":"product","receipt_name":"025--complete-loss--r3--product.json","repetition":3,"row_sha256":"6f8e2fcadefbdb9ea598d6d25666cc45e995aedf9f4056474d30fc5676f4cf10","scenario_class":"complete-loss","sequence":25},{"execution_order":2,"method":"ordinary-git","receipt_name":"026--complete-loss--r3--ordinary-git.json","repetition":3,"row_sha256":"e1a48948060bdabbd37a26f9729be2623583ff1c7bfc51d836b119fcabf76013","scenario_class":"complete-loss","sequence":26},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"027--complete-loss--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"2dda42922736885cd6ccd57c6e71469bca9bbf86ffeaddf57704030dd8494ddf","scenario_class":"complete-loss","sequence":27},{"execution_order":1,"method":"ordinary-git","receipt_name":"028--partial-loss--r1--ordinary-git.json","repetition":1,"row_sha256":"006f4bca238a5083b8507cbbf1172c1817eb7491e237ad3c52faa6e8e17488d6","scenario_class":"partial-loss","sequence":28},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"029--partial-loss--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"a51a56a862ec4d840e1d557748784a6410d89776d4311d3494db26e675b0c095","scenario_class":"partial-loss","sequence":29},{"execution_order":3,"method":"product","receipt_name":"030--partial-loss--r1--product.json","repetition":1,"row_sha256":"ebae460545116a1ef6fc21dfa5c555904e865d2bd894f647d65f8a3746d0eabd","scenario_class":"partial-loss","sequence":30},{"execution_order":1,"method":"ordinary-git","receipt_name":"031--partial-loss--r2--ordinary-git.json","repetition":2,"row_sha256":"837c4228f1b8ad0101f7574bf4a418addc0dc258e54a00dfc70a6ef35f11beb7","scenario_class":"partial-loss","sequence":31},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"032--partial-loss--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"3686cdc3f8bd5e67df8548e25a2a3982e7e4695fcec653a6a567f862d0feb1e0","scenario_class":"partial-loss","sequence":32},{"execution_order":3,"method":"product","receipt_name":"033--partial-loss--r2--product.json","repetition":2,"row_sha256":"d283400a25155fd109e6740e8191a9c9a323b04269b242cc83f1727530f21c06","scenario_class":"partial-loss","sequence":33},{"execution_order":1,"method":"ordinary-git","receipt_name":"034--partial-loss--r3--ordinary-git.json","repetition":3,"row_sha256":"2c92f9e71caadc70173d016296ed92d3d7a1fb9235b1e058543e4a8530a6eca0","scenario_class":"partial-loss","sequence":34},{"execution_order":2,"method":"git-plus-restic-0.19.0","receipt_name":"035--partial-loss--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"e984f5966b6bf073d81a570b2545033110c9ef8a203c34e68a055d139fbab7c8","scenario_class":"partial-loss","sequence":35},{"execution_order":3,"method":"product","receipt_name":"036--partial-loss--r3--product.json","repetition":3,"row_sha256":"553dfb86c022576a83e7e9a58a9c8227de856bf950b9754237457357e4f4b4e7","scenario_class":"partial-loss","sequence":36},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"037--conflicting-stale--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"d62d085394b3c6f4ccc8049e8b7f34f363cfa8d4650bb18e785c74ef7ed8fbea","scenario_class":"conflicting-stale","sequence":37},{"execution_order":2,"method":"product","receipt_name":"038--conflicting-stale--r1--product.json","repetition":1,"row_sha256":"a145eca12e2bf2680b799f9eee7e826dd7881dc94ab9e9806a7e2e950bfe2a67","scenario_class":"conflicting-stale","sequence":38},{"execution_order":3,"method":"ordinary-git","receipt_name":"039--conflicting-stale--r1--ordinary-git.json","repetition":1,"row_sha256":"481cad49bdb19ce7c4cb310f2036975f4d1355099e15bc150b5382cce0c564fd","scenario_class":"conflicting-stale","sequence":39},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"040--conflicting-stale--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"1b7d47e4b862f022fe54e55dbbe265413c18666ceb142225af06741edf773eae","scenario_class":"conflicting-stale","sequence":40},{"execution_order":2,"method":"product","receipt_name":"041--conflicting-stale--r2--product.json","repetition":2,"row_sha256":"934b973395074ea9893acc162bc5cd90ec4c44cc430d538e5c85c4be3790a711","scenario_class":"conflicting-stale","sequence":41},{"execution_order":3,"method":"ordinary-git","receipt_name":"042--conflicting-stale--r2--ordinary-git.json","repetition":2,"row_sha256":"2fe1c1b1c1df27f4a89d30d70b606fedad400c936fa088087cd735509cc026ee","scenario_class":"conflicting-stale","sequence":42},{"execution_order":1,"method":"git-plus-restic-0.19.0","receipt_name":"043--conflicting-stale--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"f5d239e84920307f76556647842d140c39103361fd8060fa4696656a51a91e45","scenario_class":"conflicting-stale","sequence":43},{"execution_order":2,"method":"product","receipt_name":"044--conflicting-stale--r3--product.json","repetition":3,"row_sha256":"593337ecc8ac8f55cd913ff03038eb9830c435dfe74d1ab4c3d0daf6e60ae0bb","scenario_class":"conflicting-stale","sequence":44},{"execution_order":3,"method":"ordinary-git","receipt_name":"045--conflicting-stale--r3--ordinary-git.json","repetition":3,"row_sha256":"db9e2c5c440360d6a487abd910cb070022da7e7ce27ae641a6aad70e4565e525","scenario_class":"conflicting-stale","sequence":45},{"execution_order":1,"method":"product","receipt_name":"046--clean-control--r1--product.json","repetition":1,"row_sha256":"607df8505b9d959a3463c57591dcebc79e9c3bad47539bdff2f12f9839032957","scenario_class":"clean-control","sequence":46},{"execution_order":2,"method":"ordinary-git","receipt_name":"047--clean-control--r1--ordinary-git.json","repetition":1,"row_sha256":"fa104fd0d608d3ae35b6412285342a1c27d8f82c640200205003078afde8bf5e","scenario_class":"clean-control","sequence":47},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"048--clean-control--r1--git-plus-restic-0.19.0.json","repetition":1,"row_sha256":"b3faf6cf0833c91c5243fba32e05812ca24cb7381338e00aa0e65ca201954bfc","scenario_class":"clean-control","sequence":48},{"execution_order":1,"method":"product","receipt_name":"049--clean-control--r2--product.json","repetition":2,"row_sha256":"9816f500f9a04ca77d23f5a1e389faa0d8f03fbe088f2061cc7badd64e5a0b34","scenario_class":"clean-control","sequence":49},{"execution_order":2,"method":"ordinary-git","receipt_name":"050--clean-control--r2--ordinary-git.json","repetition":2,"row_sha256":"3f29a7ffeb7a4021ef47ae086f9f8023d6068e8aaeae7ebb8807fe17e813d2b8","scenario_class":"clean-control","sequence":50},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"051--clean-control--r2--git-plus-restic-0.19.0.json","repetition":2,"row_sha256":"ee09e31e3e2fb83cc6723f518278db8ba2965aa5a4c879953b240f8d22af6166","scenario_class":"clean-control","sequence":51},{"execution_order":1,"method":"product","receipt_name":"052--clean-control--r3--product.json","repetition":3,"row_sha256":"c11315bf8ff9252331e1d742f5a4483c35b7448a254c4f2f697afaad81f40227","scenario_class":"clean-control","sequence":52},{"execution_order":2,"method":"ordinary-git","receipt_name":"053--clean-control--r3--ordinary-git.json","repetition":3,"row_sha256":"fde23d5ba2758c22986b5fa394095c319fac97526be4597ebe3ae3c303d16f26","scenario_class":"clean-control","sequence":53},{"execution_order":3,"method":"git-plus-restic-0.19.0","receipt_name":"054--clean-control--r3--git-plus-restic-0.19.0.json","repetition":3,"row_sha256":"da1abe76f65b9e42f2e9939120150abd0cc2c402d2f11cc1e63451e7b068d6c7","scenario_class":"clean-control","sequence":54}],"scenario_classes":["committed-only","committed-plus-uncommitted","complete-loss","partial-loss","conflicting-stale","clean-control"],"version":"hardening-gate6-execution-manifest-v1"}
```

## FILE: HARDENING_GATE6_LINUX_TOOL_PROVENANCE_R2.json

```text
{"architecture":"x86_64","execution_revision":"R2","git":{"deb_sha256":"8794fcf2c4606c445df0db3dc963c8fb852772208bfb12727a12717c03767af7","package":"git_2.34.1-1ubuntu1.17_amd64.deb","path":"/usr/bin/git","sha256":"587ef21868c948b883993e23209b86a72a6ddc06aab1545c697ffc31075acd4a","source":"Ubuntu jammy security package","version":"git version 2.34.1"},"image":{"linux_amd64_manifest_digest":"sha256:27b844c0606ec6e5550fa90bc6647c4b41cf4ee53a44781bd3dbff8ca1beb297","name":"runpod/base:1.0.2-ubuntu2204","registry_index_digest":"sha256:ffe1c3b1ec997f7eaaef8561c2a701792c79ece19754d528222a14ee25d24cb0"},"platform":"Linux","product":{"path":"bundle/p4-verifier/verifier.py","sha256":"a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40","version":"p4-deterministic-verifier-v1"},"python":{"path":"/usr/bin/python3","sha256":"d6bca2b84e73c7775a0dd5e6a76899cfe4ee62863d7c8f88513811d1fda23f49","source":"prior direct runtime attestation from the same immutable image digest; mandatory remote byte recheck before measurement","version":"Python 3.10.12"},"restic":{"archive_sha256":"13176fe6d89d4357947a2cd107218ab2873a5f9d8e1ac2d4cd1c8e07e6839c21","path":"/workspace/ck-gate6-20260727-run1-r2/bundle/runtime/restic","sha256":"ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c","source":"official Restic 0.19.0 Linux amd64 release","version":"restic 0.19.0 compiled with go1.26.4 on linux/amd64"},"version":"hardening-gate6-linux-tool-provenance-v1"}
```

## FILE: HARDENING_GATE6_RUNPOD_SCHEDULE_R2.json

```text
{"accepted_active_rate_usd_per_hour_max":"0.10","accepted_compute_rate_usd_per_hour_by_memory_gib":{"4":"0.06","8":"0.08"},"accepted_container_disk_gb":20,"accepted_cpu_count":2,"accepted_gpu_count":0,"accepted_image":"runpod/base:1.0.2-ubuntu2204","accepted_memory_gib_values":[4,8],"accepted_network_volume_gb":0,"accepted_template_id":"runpod-ubuntu-2204","aggregate_runpod_exposure_usd_max":"25.00","attempt_names":["ck-gate6-20260727-r2-a01","ck-gate6-20260727-r2-a02","ck-gate6-20260727-r2-a03","ck-gate6-20260727-r2-a04","ck-gate6-20260727-r2-a05","ck-gate6-20260727-r2-a06","ck-gate6-20260727-r2-a07","ck-gate6-20260727-r2-a08"],"campaign_id":"ck-gate6-20260727-run1-r2","campaign_prefix":"ck-gate6-20260727-r2-","execution_revision":"R2","maximum_creation_attempts":8,"maximum_measured_workers":1,"maximum_measured_workload_seconds":21600,"maximum_paid_lifetime_seconds":28800,"maximum_simultaneous_workers":1,"provider_stop_epoch":1785225000,"provider_stop_utc":"2026-07-28T07:50:00Z","provider_terminate_epoch":1785225900,"provider_terminate_utc":"2026-07-28T08:05:00Z","schema_version":"hardening-gate6-runpod-schedule-v1"}
```

## FILE: HARDENING_GATE6_LOCAL_PREFLIGHT_RECEIPT_R2.md

```text
# Hardening Gate 6 — Local Preflight Receipt R2

- `STATUS`: `LOCAL_PREFLIGHT_GREEN_NOT_PROVIDER_EVIDENCE`
- `EXECUTION_REVISION`: `R2`
- `PARENT_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `RUNPOD_WORKERS_CREATED`: `0`
- `RUNPOD_ACTIVE_INVENTORY`: `[]`
- `RUNPOD_COST_STATE`: `EXACT_$0.00_FOR_GATE6_R2`
- `UTC_RECORDED`: `2026-07-28T00:27:00Z`

## Mechanical results

- Gate 6 orchestration unit tests: `3/3 PASS`.
- Broader non-live regression: `267/267 PASS` across `23` test files.
- Test-log manifest SHA-256:
  `e36c14c85341d4c2c915200224b03a670a2b6d7eefdbff271d3333e46145a41e`.
- Exact-candidate local paired profile: `18/18` canonical preflight receipts,
  plus `3/3` semantic determinism repeats.
- Local network-denial probe: `BLOCKED` under macOS `sandbox-exec`.
- Local profile elapsed time: `91.13 seconds`.
- Local profile maximum RSS: `98,598,912 bytes`.
- Linear 54-run time estimate: approximately `273.39 seconds` before remote
  setup/custody overhead; selected 2-vCPU/4-GiB CPU class remains sufficient.
- Profile internal summary SHA-256:
  `741d8dfe032033090a2877db93d273375fba36476acddd4d6ade11566b233465`.
- Profile canonical summary file SHA-256:
  `d5dbf4e4b3afdc768746b822a7fbc6314ab8ab2c6178920c672f6b4c3d982e10`.
- Exact 54-row manifest validation: `PASS`.
- Manifest embedded SHA-256:
  `ffbe59a0fa569d9a1cfd1aa6247490a7606ab20a362a072b0d19ca5879ba3b07`.
- Manifest file SHA-256:
  `80d9f88df8b7d2636e7e81e8f8f3cd8f7c98a898bf57d30f51ea2cf2fb1349a7`.
- `git diff --check`: `PASS`.
- Gitleaks: `0` findings.
- detect-secrets: `0` findings.
- New-file private-path scan: `0` private paths; the single literal
  `credential` occurrence is explanatory policy text.

## Candidate and runtime custody

- Frozen comparative SHA-256:
  `f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec`.
- Frozen deterministic verifier SHA-256:
  `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`.
- Gate 4 R2 protocol SHA-256:
  `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`.
- Current Docker registry index and Linux amd64 manifest digests match the
  exact previously reviewed RunPod base image.
- Official Ubuntu Git package SHA-256:
  `8794fcf2c4606c445df0db3dc963c8fb852772208bfb12727a12717c03767af7`.
- Extracted Ubuntu Git executable SHA-256:
  `587ef21868c948b883993e23209b86a72a6ddc06aab1545c697ffc31075acd4a`.
- Official Restic Linux archive/binary hashes match the Gate 5 allowlist.
- Python's expected hash is bound to a prior direct runtime attestation from
  the same immutable image digest and must be reverified remotely before any
  measured row. A mismatch blocks after upload and cannot trigger replacement.

This receipt is not Linux, measured, RunPod, Gate 6, or superiority evidence.
It authorizes only packet freeze and independent preflight review.
```

## FILE: HARDENING_GATE6_PAYLOAD_RECEIPT_R2.md

```text
# Hardening Gate 6 — Payload Receipt R2

- `STATUS`: `PAYLOAD_GREEN_FOR_PREFLIGHT_REVIEW`
- `EXECUTION_REVISION`: `R2`
- `SOURCE_COMMIT`: `3558ce481d609ccf755f57758b74cd6e67305dad`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `PAYLOAD_PATH_LOCAL_PRIVATE`: `.hardening-runtime/gate6-r2/ck-gate6-r2-payload.tar.gz`
- `PAYLOAD_BYTES`: `14224525`
- `PAYLOAD_SHA256`: `d9b98d5c66596501f2f46a7e87f54994518325b1acacca1768561652772cf283`
- `PAYLOAD_TREE_MANIFEST_SHA256`: `a686863a6e413b632de1b8965865879f19c910081d63ddc239a18acf25dbac8d`
- `FILE_COUNT_EXCLUDING_TREE_MANIFEST`: `11`
- `UTC_RECORDED`: `2026-07-28T00:28:00Z`

## Included

- Gate 4 R1 plus R2 protocols;
- exact 54-row R2 execution manifest and execution plan;
- public-safe Gate 3 hash reference;
- frozen Linux tool provenance;
- exact candidate comparative source and deterministic verifier;
- Gate 6 R2 orchestration;
- official Restic 0.19.0 Linux amd64 binary;
- hash-bound Ubuntu Jammy Git amd64 package.

## Excluded

Credentials, OAuth or AWS sessions, CockroachDB secrets, SSH material, HOME
state, private/raw Gate 3 evidence, provider responses, unrelated source,
sealed Gate 7 vectors, client data, persistent volumes, and cloud configuration.

## Mechanical verification

- archive extraction: `PASS`;
- all `11/11` tree-manifest entries: `PASS`;
- Gitleaks: `0` findings;
- detect-secrets: `0` findings;
- private-path scan: no private path, account identifier, credential value, or
  key material. The `14` lexical matches are policy descriptions and the
  candidate's trial-local CSPRNG Restic-password implementation; no secret
  bytes exist before each isolated trial creates and later destroys them.
- Gitleaks output SHA-256:
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`.
- detect-secrets output SHA-256:
  `bfe885a805a694d3c8a6a74fe2d375caf6f7d833d07574c62adf11079a65a29f`. <!-- gitleaks:allow -->
- classified lexical scan SHA-256:
  `3729241caa8b3708ee109a2aef1c6af04dc5a757dca7790dba67a538a2b7890f`.

This receipt authorizes only independent preflight review. Upload remains
forbidden until the same-hash required quorum is GREEN and a returned worker
passes the reviewed provider envelope.
```

## FILE: HARDENING_GATE6_GATE3_TRACE_REFERENCE_R2.json

```text
{"capture_receipt_sha256":"c4ae85a6ef201d98f2079b077f0d86784c905cb93539128d2bee371b8d326ee0","continuation_receipt_sha256":"cb2bcc1df56f6a88276b2a685fc9f3bc5e30816bb54d151091364d384d06a050","execution_revision":"R2","final_packet_sha256":"7ce89c16bed4c6fef8a442df401e564c140bc0eb5ad03b0d8bb87c780f7f4614","judge_state":"GLM_4_7_GREEN","pooled_with_synthetic_campaign":false,"residue_receipt_sha256":"03be225cf64c4a741e683b3f725725be97372c22e174b58f6901ee254162249","status":"HARDENING_3_REAL_WORKFLOW_GREEN","version":"hardening-gate6-gate3-reference-v1"}
```

## FILE: HARDENING_GATE6_SOURCE_BINDING_R2.md

```text
# Hardening Gate 6 — Source Binding R2

- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `CANDIDATE_COMPARATIVE_SHA256`: `f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec`
- `GATE6_ORCHESTRATOR_SHA256`: `825523e7011e3942bd7ac162322d8e7b673339a16f2dd8c1ccb854ed721db653`
- `LIFECYCLE_GUARD_SHA256`: `4644aa756f47c3d53b82c239657ce22605d4a9caab3e6a8651c4f459d95c6f0c`
- `PRODUCT_VERIFIER_SHA256`: `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`
- `GATE4_PROTOCOL_R1_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `GATE4_PROTOCOL_R2_SHA256`: `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`
- `GATE5_FINAL_PACKET_SHA256`: `41efeb9270b76a0d4e1f711d5b1ab3270ecd92d32eccce93f07bef8a6ba036c0`
- `GATE5_STATUS_SHA256`: `c9bf7e330187695e2b359ed3510aaa00d7bd5c7026f421aede7430c7ea8a1cae`
- `GATE5_CHECKPOINT_SHA256`: `6b3fd1abbfee8144224149e0202e225d8a6898970e03f5cc9b84bdca42783465`
- `GATE5_JUDGE_RECEIPTS_SHA256`: `aff4cd568995238f6fe885937ff6cbc51853cfd0d31625abb7784be4a3342efb`
- `GATE5_EVIDENCE_REPORT_SHA256`: `5d65945758d1b5f5aff77c9c24f6d28ded69e3e1ffddabe56e3db81433f10757`
- `UTC_RECORDED`: `2026-07-28T00:37:19Z`

Gate 5 independently reviewed and froze the exact candidate source. Gate 6
does not change that source. Its new review concerns Linux tool binding,
orchestration, network denial, balanced pairing, evidence custody, RunPod
lifecycle, cost bounds, and teardown.

The raw candidate comparative source is deliberately excluded from the R3
external packet because a local egress rule classifies its ephemeral Restic
password assignment as a secret assignment. The source remains locally
available, committed, hash-bound, unit-tested, and included in the scanner-clean
RunPod payload. This is a sanitization boundary, not evidence that the source
contains a static credential.
```

## FILE: HARDENING_GATE6_PREFLIGHT_EGRESS_BLOCK_RECEIPT_R2.md

```text
# Hardening Gate 6 — Preflight Egress Block Receipt R2

- `STATUS`: `PREFLIGHT_JUDGE_CALLS_BLOCKED_BEFORE_PROVIDER_EXECUTION`
- `PACKET_SHA256`: `1fd134ff0bf56f489e6875bcd3ffe5edb791418e75b58fa6bee7731b34661650`
- `PACKET_PATH`: `HARDENING_GATE6_PREFLIGHT_PACKET_R2.md`
- `GLM_EXIT_STATUS`: `3`
- `CLAUDE_EXIT_STATUS`: `2`
- `PROVIDER_EXECUTION`: `NO`
- `JUDGE_VERDICT_EXISTS`: `NO`
- `UTC_RECORDED`: `2026-07-28T00:37:19Z`

## Raw local boundary output

```text
GLM:
egress-gateway: blocked glm-zai:glm-5.2 egress: secret assignment
glm-zai: egress gateway blocked prompt before provider execution

Claude:
egress-gateway: blocked claude-opus-judge egress: secret assignment
claude-judge: egress gateway blocked the packet
```

The only assignment matching the local boundary rule is the candidate's
trial-local Restic-password path plus CSPRNG generation. It contains no static
secret, provider credential, or reusable value. The immutable candidate will
not be modified, and the egress gateway will not be weakened or bypassed.

The next packet may omit the raw candidate comparative source only because its
exact source hash and prior same-hash Gate 5 GLM/Claude GREEN receipts remain
included. The new Gate 6 packet must disclose that the judges are evaluating
the execution, lifecycle, isolation, pairing, and evidence design—not
re-adjudicating candidate source already frozen at Gate 5.
```

## FILE: HARDENING_GATE4_BASELINE_PROTOCOL_R1.md

```text
# Hardening Gate 4 — Frozen Comparative Baseline Protocol R1

## Control fields

- `GATE`: `HARDENING_RUN_GATE_4_BASELINE_PROTOCOL`
- `PARENT_GATE`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `TARGET`: `HARDENING_4_BASELINE_PROTOCOL_GREEN`
- `PROTOCOL_REVISION`: `R1`
- `CAMPAIGN_CONSUMER`: `HARDENING_6_RUN1`
- `METHODS`: `ORDINARY_GIT`, `GIT_PLUS_RESTIC_0_19_0`, `PRODUCT`
- `SCENARIO_CLASSES`: `6`
- `REPETITIONS_PER_CLASS_METHOD`: `3`
- `MEASURED_EXECUTIONS`: `54`
- `RECOVERY_TIME_BUDGET_SECONDS`: `180`
- `NETWORK_IN_COMPARATIVE_TRIALS`: forbidden
- `PAID_ACCOUNT_OR_PRIVATE_CREDENTIAL`: forbidden
- `ROOT_PRIVILEGE`: forbidden
- `BASELINE_TUNING_AFTER_FREEZE`: forbidden
- `PRODUCT_TUNING_AFTER_RESULTS`: forbidden
- `EXPECTED_WINNER`: none
- `HUMAN_GATE`: none
- `RUNPOD_ACTION_IN_GATE_4`: none

## Purpose and kill line

This protocol measures how much declared work each method can restore and
whether the resulting successor can continue under a common executable
contract. It does not establish general usability, market preference,
production scale, off-site disaster recovery, or global superiority.

Kill the comparative campaign before launch if any method receives different
source bytes, a different event sequence, a different declared loss, a longer
recovery budget, undisclosed operator information, a method-specific success
test, post-result tuning, or shared hidden state. Kill the protocol if a
conventional tool is scored as failing a policy/trajectory capability it does
not claim.

## Frozen methods

### M1 — ordinary Git reference

This is a deliberately ordinary but durable Git workflow, not a local-only
`.git` strawman.

- A fresh Git repository is initialized inside each workspace.
- A fresh bare remote is initialized under that trial’s method custody root,
  outside the disposable workspace and outside the declared loss target.
- Initial committed state and every scenario-defined explicit commit are
  pushed to that remote immediately after the commit completes.
- The harness never auto-adds, auto-commits, stashes, patches, bundles, or
  copies uncommitted/untracked work for Git.
- The bare remote retains every pushed commit for the trial.
- Recovery runs `git fsck --full --strict` on the bare remote, clones with
  `--no-local` into a new empty successor, and checks out the exact frozen
  remote commit SHA.
- Git’s capture/push time, storage bytes, command count, and recovery time are
  recorded.

Committed and pushed bytes are a Git-supported recovery surface. Uncommitted or
untracked byte recovery is `UNSUPPORTED_BY_METHOD`, not a Git command failure.
If a scenario’s executable continuation requires unsupported bytes, the common
executable outcome may still be false; that is reported separately from method
failure.

### M2 — strongest qualified conventional baseline: Git plus Restic 0.19.0

M2 receives the same Git workflow as M1 plus a best-case Restic snapshot at
every frozen completed checkpoint.

#### Version and runtime

- Restic version is exactly `0.19.0`.
- Gate 5 must freeze exact official Darwin arm64 and Linux worker binary
  provenance, SHA-256, size, executable mode, and BSD 2-Clause license notice.
- The campaign must not use a package-manager-floating version or `latest`.
- All Restic commands set `--no-cache`; no global configuration or HOME cache
  is permitted.

#### Storage and permissions

For each M2 trial:

```text
trial/
  workspace/                 # disposable loss target
  successor/                 # absent until recovery
  custody/                   # mode 0700, survives workspace loss
    git-remote.git/           # same durable Git reference as M1
    restic-repository/        # local Restic repository
    restic-password           # mode 0600, ephemeral synthetic secret
    events/                   # checkpoint and command receipts
  temp-home/                  # isolated HOME for subprocesses
```

- The repository is local; no S3, SSH, rclone, cloud, account, socket, or
  network backend is allowed.
- The password is generated from the OS CSPRNG inside the trial after launch,
  never transferred, printed, logged, committed, or included in evidence.
- Evidence records only generation success, file mode, and absence of secret
  exposure—not the password bytes or a reversible representation.
- `RESTIC_PASSWORD_FILE` points to the trial-local file.
- The repository and password survive only because they are outside the
  declared workspace loss target. The product receives an equivalent
  outside-workspace custody class.
- Every completed snapshot is retained through scoring; no `forget`, `prune`,
  rewrite, or retention deletion occurs before teardown.

#### Cadence and retained state

The scenario generator emits a finite ordered event stream. Four possible
checkpoint labels exist:

```text
BASE_COMMITTED
AGENT_PROGRESS_SAVED
HUMAN_EDIT_SAVED
FINAL_PRELOSS
```

Only labels present in a scenario are emitted. At each emitted label, all file
writes and explicit Git operations finish and the workspace is quiescent. The
same canonical event packet is then offered to all three adapters. M2 runs and
fully completes a snapshot before the next event or the loss event begins.

M2 backs up the entire relative `workspace` directory, including `.git`,
uncommitted tracked files, and untracked files. It uses no exclusions except
method-generated paths are already outside `workspace`. Symlinks, absolute
paths, device files, sockets, and paths escaping the generated trial root are
forbidden by the scenario schema rather than silently excluded.

Each capture uses a deterministic host label and tags containing the scenario,
repetition, and checkpoint ID. The exact snapshot ID returned by the successful
capture is parsed from machine-readable output and hash-bound into the
checkpoint receipt. The harness never selects `latest` during recovery.

The capture transaction is valid only if:

1. Restic exits zero;
2. an exact snapshot ID is present;
3. `restic snapshots --json` contains that ID with the expected path/tags;
4. the captured source-manifest hash equals the event’s workspace-manifest
   hash;
5. the repository integrity command frozen by Gate 5 succeeds.

Capture and integrity-check latency are recorded as **pre-loss capture
overhead**, not hidden inside recovery latency.

#### Recovery procedure

1. Verify the successor path does not exist and is under the current trial.
2. Verify the selected snapshot ID is exactly the snapshot bound to the last
   successfully completed checkpoint permitted by the scenario.
3. Run the frozen repository-integrity command.
4. Restore the exact snapshot’s `workspace` subtree into a new empty successor.
5. Never restore in place and never use `--delete`.
6. Recompute the canonical file manifest, declared work-unit hashes, and Git
   status from the successor.
7. Run the identical executable success command used for M1 and M3.
8. Record command results, elapsed monotonic time, retained units, storage,
   residue, and teardown.

The full-data integrity command may be run before loss as capture validation and
again outside the timed recovery interval for evidence integrity. The timed
recovery interval includes the exact-snapshot repository check required by the
frozen harness, restore, manifest verification, and executable success test.

### M3 — product

Gate 5 must freeze one exact product adapter and evidence-candidate commit.
Within this protocol:

- the product receives the same canonical source workspace and event packets;
- its persistent custody is outside the disposable workspace but inside the
  trial root, matching M1/M2’s survival class;
- no live AWS, public endpoint, private credential, model call, prior session,
  HOME state, or undeclared network is available during the paired campaign;
- any local CockroachDB/runtime component is version/hash frozen and receives a
  fresh trial namespace or fresh database state;
- the deterministic verifier remains the only promotion/refusal authority;
- the adapter may persist declared task/trajectory records only from the common
  event packets; it may not read M1/M2 repositories or scoring keys;
- recovery starts in a new process with an empty successor and no conversation
  history;
- product capture/evidence cost and recovery cost are separately measured.

Gate 2 and Gate 3 are the live AWS/CockroachDB evidence surfaces. Gate 6 is a
reproducible local paired comparison; its local configuration must be disclosed
as a limitation and must not be described as live cloud evidence.

## Common trial construction

### Canonical source and pairing

For each `(scenario_class, repetition)` pair, the generator produces one
canonical source bundle from a frozen seed. The bundle contains:

- relative POSIX file paths and SHA-256 content hashes;
- file modes restricted to regular non-executable or declared executable
  files;
- ordered edit operations;
- ordered checkpoint events;
- explicit Git commit boundaries;
- declared work units and dependency edges;
- the declared loss operation;
- the expected post-recovery file manifest where a unique safe continuation
  exists;
- one executable success command and expected exit/result hash;
- a public task contract available equally to every method;
- policy applicability flags and expected safe behavior.

The canonical source bundle is materialized independently into three fresh
method roots. Before method-specific capture begins, all three source manifests
must be byte-identical. Method custody data is excluded from that comparison
because it is produced by each method after receiving the same events.

Seeds, generators, source bundles, scenario order, and expected results freeze
at Gate 5 before any measured result. The three methods for a pair run in a
deterministically rotated order so fixed thermal/cache/order effects do not
always favor one method. No method shares a cache, repository, database,
process, or filesystem root with another.

### Equal information contract

Every method receives:

1. the same public task contract;
2. the same initial workspace bytes;
3. the same ordered edit/checkpoint packets as they occur;
4. the same explicit Git commit events;
5. the same declared loss receipt at recovery start;
6. the same executable success command;
7. the same 180-second recovery budget;
8. its own pre-loss artifacts and no other method’s artifacts.

No method receives the expected manifest, hidden score key, another method’s
output, a human task restatement, or post-loss help. The scorer—not any method
adapter—holds expected hashes and applies the common test.

Method-native configuration is allowed only when fully frozen here or at Gate
5. Ordinary Git gets no automatic commit. Restic gets a completed snapshot at
every common checkpoint. The product gets no event that Restic did not also get
and no recovery hint beyond the declared loss packet.

### Environment isolation

Every execution uses a new root and a new harness process. Subprocesses receive:

```text
HOME=<trial>/temp-home
GIT_CONFIG_NOSYSTEM=1
GIT_CONFIG_GLOBAL=/dev/null
GIT_TERMINAL_PROMPT=0
LANG=C
LC_ALL=C
TZ=UTC
```

Any cache/config variable used by the frozen tools must point under the trial
root. No inherited AWS, CockroachDB, Git credential helper, SSH agent, browser,
cloud, model, or user-level configuration is allowed. The network-deny method
for the Linux worker is frozen and proven at Gate 5. A forbidden egress attempt
invalidates the trial and blocks the campaign.

## Frozen scenario classes

Each class has three seeded repetitions with varied filenames, content, edit
order, and dependency graph but the same construct.

### C1 — committed-only

All required work units are committed and pushed before loss. The entire
workspace is deleted. The unique expected continuation is the committed state.
This is the positive control for Git’s core recovery contract.

### C2 — committed plus uncommitted

The base is committed and pushed. Later required tracked edits and at least one
required untracked file are saved but not committed. The final checkpoint
completes before full workspace deletion. The executable test requires both
committed and uncommitted units.

Git’s inability to retain those uncommitted/untracked units is classified as
unsupported retention; any resulting executable-test miss is still reported.

### C3 — complete declared workspace loss

The scenario contains multiple dependent saved edits across the common
checkpoint stream. The declared workspace, including its local Git metadata,
is deleted. External method custody survives. The unique expected continuation
is the last completed safe checkpoint.

### C4 — partial state loss

A frozen subset of declared paths is removed or replaced with earlier bytes;
the loss receipt names those operations. The original workspace is then sealed
and every method must produce a fresh successor rather than repairing in place.
The expected continuation is the last completed safe checkpoint.

### C5 — conflicting or stale continuation

The common stream contains two declared candidate states: one is newer by event
order but fails a frozen dependency/policy constraint; the other is the last
safe executable continuation. Conventional methods apply only their disclosed
selection rule: M1 recovers the exact pushed commit; M2 restores the exact last
completed snapshot selected by its checkpoint rule. They are not expected to
infer intent, policy, or quorum.

Content recovery and executable continuation are scored for all methods.
Trajectory/policy adjudication is `UNSUPPORTED_BY_METHOD` for M1/M2 and is
scored only for M3. A conventional method is never labeled unsafe merely for
lacking an adjudicator; unsafe acceptance requires an actual mutation or
affirmative safe/promotion claim contrary to the frozen contract.

### C6 — clean control

No loss operation occurs. The workspace remains byte-identical to the last
checkpoint. The correct common outcome is no destructive change and a passing
executable test. Methods may return `NO_ACTION` or produce a separate successor;
either is acceptable if the original is untouched and the common test passes.
This detects recovery routines that mutate healthy state.

## Loss and recovery timing

The harness records capture overhead separately. The 180-second recovery clock
starts immediately before the adapter receives the declared loss receipt and
ends only after:

1. the adapter has returned;
2. the successor/no-action target has been selected;
3. canonical manifest scoring has completed;
4. the common executable success command has completed;
5. the final canonical trial receipt has been fsynced.

Timeout is an observed failure for a method that claims the attempted core
operation. It is not converted into `UNSUPPORTED`. Setup before the common
event stream and teardown after the final receipt are measured separately.

## Outcome taxonomy

Method status and construct scores are separate.

### Method operation status

- `SUCCESS`: claimed capture/recovery operation completed and produced a target.
- `NO_ACTION`: clean-control no-op with the original untouched.
- `PARTIAL`: a target was produced with some but not all declared units.
- `UNSUPPORTED_BY_METHOD`: capability is outside the method’s documented
  contract; not counted as a command failure.
- `FAILURE`: the method claims the operation but command, integrity, selection,
  or restore failed.
- `TIMEOUT`: the claimed operation exceeded 180 seconds.
- `INVALID_TRIAL`: common harness/pairing/isolation evidence failed; rerun is
  forbidden without a new packet and independent review.

### Common construct scores

- `declared_work_units_total`
- `declared_work_units_retained`
- `provable_work_retention_ratio`
- `committed_units_retained`
- `uncommitted_units_retained`
- `untracked_units_retained`
- `manifest_exact_match`
- `executable_continuation_pass`
- `wall_clock_recovery_ms`
- `capture_overhead_ms`
- `scripted_command_count`
- `human_intervention_count`
- `task_restatement_required`
- `original_workspace_mutated_after_loss`
- `unsafe_acceptance`
- `deterministic_outcome`
- `storage_bytes_pre_loss`
- `evidence_bytes`
- `residue_bytes_after_teardown`
- `cleanup_pass`

### Method-specific constructs

- Git: exact pushed commit, object/connectivity check, tracked content.
- Restic: exact snapshot ID, repository integrity, restored snapshot bytes.
- Product: candidate/evidence linkage, deterministic promotion/refusal, stable
  reason code, one-use behavior, and no mutation after refusal.

Method-specific constructs are shown but never averaged into a cross-method
score. No single composite “winner score” is permitted.

## Canonical receipt schema

Every measured execution emits one canonical JSON object with sorted keys,
UTF-8, no insignificant whitespace, SHA-256 over exact bytes, and these fields:

```text
schema_version
campaign_id
protocol_sha256
candidate_commit
scenario_class
scenario_seed_hash
repetition
method
execution_order
source_manifest_sha256
event_stream_sha256
loss_receipt_sha256
allowed_information_sha256
tool_versions
tool_binary_sha256
method_configuration_sha256
capture_checkpoint_receipts
selected_recovery_artifact_id
operation_status
unsupported_capabilities
declared_work_units_total
declared_work_units_retained
retained_work_unit_ids
lost_work_unit_ids
committed_units_retained
uncommitted_units_retained
untracked_units_retained
manifest_exact_match
executable_command_sha256
executable_exit_status
executable_result_sha256
executable_continuation_pass
capture_overhead_ms
wall_clock_recovery_ms
setup_ms
teardown_ms
scripted_command_count
human_intervention_count
task_restatement_required
unsafe_acceptance
original_workspace_mutated_after_loss
deterministic_outcome
storage_bytes_pre_loss
evidence_bytes
residue_bytes_after_teardown
cleanup_pass
command_receipt_hashes
limitations
receipt_sha256
```

Secrets, absolute host paths, raw environment dumps, provider credentials, and
expected hidden scoring keys are forbidden from receipts.

## Statistics and reporting

- The unit of pairing is `(scenario_class, repetition)`.
- Publish all 54 execution receipts and a paired table; never only aggregates.
- For binary outcomes, report exact numerator/denominator by method and class.
- For retention, report paired raw ratios, median, minimum, and maximum.
- For time and storage, report raw values and median by method/class; p95 is not
  reported for three observations.
- Report paired method differences but no p-values, confidence claims, or
  population inference from `n=3`.
- Failed, partial, unsupported, timeout, and invalid-trial counts remain visible.
- An invalid common trial blocks the campaign rather than being silently
  dropped or replaced.
- Gate 3’s single-operator workflow is displayed separately and never pooled
  with the 54 synthetic executions.
- A Restic or Git win is preserved. Public comparative wording must quote the
  exact methods, six classes, three repetitions, candidate commit, and
  limitations.

## Determinism

The scenario generator and scorer must reproduce identical source, event,
loss, allowed-information, and expected-result hashes from a frozen seed.
Method storage bytes may be nondeterministic because of timestamps,
encryption, or native metadata; determinism therefore compares semantic output:

```text
operation_status
retained_work_unit_ids
manifest_exact_match
executable_continuation_pass
unsafe_acceptance
method-specific verdict/reason where applicable
```

The Run 1 three repetitions are not duplicate-byte determinism probes. A
separate frozen local preflight repeats representative inputs before campaign
launch and must pass the semantic comparison.

## Teardown and residue

After final receipt custody is proven, each trial removes only its explicit
generated root. Before removal, record process, socket, mount, child-process,
and path inventory. After removal, verify:

- workspace, successor, custody, repository, password, bare remote, temp HOME,
  caches, sockets, and child processes are absent;
- no path outside the generated trial root changed;
- no network, provider, HOME, credential, Qdrant, StateV2, launchd, cron,
  client/private data, or unrelated repository was touched.

A process leak, secret exposure, cross-trial residue, or undeclared path change
is a critical campaign blocker.

## Construct validity and bias disclosure

### What the experiment can support

- byte/work-unit retention under the six declared synthetic loss constructs;
- executable continuation under one frozen small-workspace test contract;
- relative command/time/storage overhead inside one worker environment;
- product refusal/trajectory behavior only where that behavior is applicable;
- reproducibility of the exact frozen harness and candidate.

### What it cannot support

- all developer workflows, repository sizes, operating systems, backup media,
  cloud failures, hardware loss, or attacker models;
- general user preference, cognitive load, or time saved in the population;
- production capacity, multi-region resilience, off-site disaster recovery, or
  long-term retention;
- a claim that Git, Restic, Kopia, Borg, Time Machine, or other products are
  generally inferior;
- a claim that restored bytes prove correct developer intent;
- statistical significance or population generalization.

### Experimenter bias controls

- baseline and product interfaces freeze before measured evidence;
- M2 receives every common completed checkpoint, the most favorable disclosed
  cadence possible under this event-driven experiment;
- the scorer is method-neutral and holds hidden expected hashes;
- order rotates deterministically;
- all raw results and losses are preserved;
- no behaviorally relevant repair follows a measured result;
- independent GLM and Claude reviewers inspect one exact packet before Gate 4
  can close.

### Remaining bias and missing data

- The product team authored the scenarios and success rules.
- Selecting Restic rather than Kopia/Borg avoids a multi-baseline campaign and
  may omit a tool that performs better on some workloads.
- Completed pre-loss checkpoints favor snapshot tools; interruption during
  capture is deferred to the held-out failure campaign.
- Local storage omits real backup-network latency and off-site durability.
- Small synthetic fixtures may overstate absolute speed and understate storage
  pressure.
- The product’s local comparative mode is not its live AWS deployment.
- There is no public-user sample; Gate 3 is one operator trace.

These limitations are mandatory in the Gate 6 report and any public claim.

## Gate 5 obligations before execution

Gate 4 freezes design, not a runnable benchmark. Gate 5 must bind:

1. exact scenario generator and scorer source;
2. all six scenario schemas and seeds;
3. method adapter source and command contracts;
4. exact Git and Restic binary provenance/hashes/licenses;
5. product candidate commit and local runtime/database mode;
6. network-deny and environment-isolation proof;
7. capture/recovery timeout enforcement;
8. canonical receipt generation and validation;
9. local paired smoke and semantic determinism proof;
10. dependency/license manifest and RunPod payload scans.

Any change to cadence, allowed information, scenario meaning, success rules,
tool version, method selection, or scoring after Gate 4 requires a new protocol
revision and full Gate 4 judge rerun.

## Gate 4 acceptance

`HARDENING_4_BASELINE_PROTOCOL_GREEN` is allowed only when:

- this protocol and the research receipt are frozen and hash-bound;
- GLM independently returns GREEN for fairness, statistics, schema, and
  construct validity over the exact packet hash;
- Claude Opus 4.8 independently returns GREEN for harness/lifecycle semantics
  and baseline comparability over the same exact packet hash;
- both judges remain non-authoring and no packet bytes change afterward;
- repository state, packet hash, judge receipts, and `RESUME_STATE.md` agree.

Gate 4 GREEN does not claim a benchmark ran, a baseline or product won, Gate 5
is complete, a RunPod worker was created, or any public claim is supported.
```

## FILE: HARDENING_GATE4_BASELINE_PROTOCOL_R2.md

```text
# Hardening Gate 4 — Comparative Baseline Protocol R2 Amendment

## Control fields

- `STATUS`: `AMENDED_PENDING_INDEPENDENT_REVIEW`
- `PARENT_PROTOCOL`: `HARDENING_GATE4_BASELINE_PROTOCOL_R1.md`
- `PARENT_PROTOCOL_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `SUPERSEDES_FOR_NEW_CAMPAIGNS`: `R1_PLATFORM_AND_EVIDENCE_MODE_CLAUSES_ONLY`
- `METHODS`: `ORDINARY_GIT; GIT_PLUS_RESTIC_0_19_0; PRODUCT`
- `MEASURED_EXECUTIONS`: `54`
- `HUMAN_GATE`: `none`
- `RUNPOD_ACTION`: `none`

R1 remains incorporated by its exact hash except where this amendment is more
specific. Historical R1/Gate 5/Gate 6 evidence is preserved and does not gain
authority from this amendment.

## A1 — Platform-neutral common source

The common executable command embedded in every scenario is exactly:

```json
["python3","tests/check.py"]
```

No absolute interpreter path, host path, `sys.executable`, architecture, or
operating-system string may enter the scenario, source-bundle, event, loss, or
allowed-information hash. The executable is resolved only at trial runtime
inside the frozen isolated `PATH`. Its observed version and binary SHA-256 are
recorded in every canonical receipt.

The same `(scenario_class, repetition)` must therefore produce byte-identical
public bytes and hashes on Darwin arm64 and Linux amd64. A mismatch blocks the
campaign before measurement.

## A2 — Runtime-attested tool provenance

The harness does not claim one host's Git identity on another host.

- `CK_GATE5_GIT` names the exact Git executable selected before a campaign.
- The harness verifies it is a regular file, invokes `<git> --version`, hashes
  its exact bytes, uses that same executable for every Git command, and places
  the observed version/hash in each applicable receipt.
- Python is resolved from the isolated trial `PATH`, version-invoked, hashed,
  used by the common executable command, and recorded in every receipt.
- Gate 6 freezes the exact Linux Python and Git paths, versions, and hashes in
  the independently reviewed preflight packet. Every measured receipt must
  equal that frozen provenance; drift blocks the campaign.

Restic remains version `0.19.0` and is accepted only when its exact binary hash
matches one of these official release artifacts and its own version output
matches the corresponding value:

| Platform | Binary SHA-256 | Required version output |
|---|---|---|
| Darwin arm64 | `f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd` | `restic 0.19.0 compiled with go1.26.4 on darwin/arm64` |
| Linux amd64 | `ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c` | `restic 0.19.0 compiled with go1.26.4 on linux/amd64` |

The official Linux archive remains hash-bound at
`13176fe6d89d4357947a2cd107218ab2873a5f9d8e1ac2d4cd1c8e07e6839c21`.
No other Restic hash/version/platform is permitted.

## A3 — Canonical evidence mode

The canonical receipt schema is revision `gate5-comparative-receipt-v2` and
adds these required fields:

```text
evidence_mode
runtime_platform
```

`evidence_mode` is exactly one of:

- `PREFLIGHT`: local or remote non-measured contract/smoke evidence. Required
  limitations are `LOCAL_SYNTHETIC_PREFLIGHT`, `NOT_LIVE_AWS`, and
  `NOT_GATE6_MEASURED_EVIDENCE`.
- `MEASURED_GATE6`: the frozen Linux RunPod 54-row comparative campaign.
  Required limitations are `SYNTHETIC_PAIRED_COMPARATIVE`, `NOT_LIVE_AWS`,
  `NOT_PRODUCT_SCALE`, and `RUNPOD_GENERIC_COMPUTE`.

`MEASURED_GATE6` fails closed unless the runtime reports Linux, the candidate
commit is exactly 40 lowercase hexadecimal characters, and the campaign ID is
an explicit non-default `ck-gate6-*` identifier. Receipts are emitted directly
with their true mode; post-execution relabeling or canonical-byte rewriting is
forbidden.

## A4 — Unchanged fairness and authority

All R1 fairness, pairing, method, scenario, metric, timeout, no-tuning,
network-denial, residue, raw-reporting, and limitation clauses remain binding.
The product verifier and its sole promotion/refusal authority are unchanged.
This amendment does not authorize a RunPod worker, measured execution, public
claim, release, or submission.

## Kill line

Block before measurement if the source hash varies by platform, a tool receipt
does not match observed bytes, an unallowlisted Restic artifact is supplied, a
measured receipt carries preflight labels (or vice versa), or any R1 fairness or
authority clause changes without another independently reviewed amendment.
```

## FILE: HARDENING_GATE5_STATUS.md

```text
# Hardening Gate 5 Status

- `STATUS`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `LAST_GREEN_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `NEXT_TARGET`: `HARDENING_6_RUN1_R2_PREFLIGHT`
- `PARENT_GATE`: `HARDENING_4_BASELINE_PROTOCOL_R2_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `GATE4_PROTOCOL_SHA256`: `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`
- `EVIDENCE_REPORT`: `HARDENING_GATE5_EVIDENCE_REPORT_R2.md`
- `FINAL_PACKET_SHA256`: `41efeb9270b76a0d4e1f711d5b1ab3270ecd92d32eccce93f07bef8a6ba036c0`
- `LOCAL_SMOKE_SUMMARY_SHA256`: `781531c80ce1415ca208c4f2119cb57be660db73276f556610f1b57dd83b7c1b`
- `JUDGE_STATE`: `GLM_5_2_GREEN; CLAUDE_OPUS_4_8_GREEN_RECUSAL_CLEAR`
- `GLM_RAW_SHA256`: `aeb7368a182fd1ad4cdfc615e0e31828c1ec80a1e36418ca585b9c1b5d6cc644`
- `CLAUDE_RAW_SHA256`: `120f440b93e0ed0557910bda585bf2958dad5d12a377acb145cdd704766907b4`
- `BLOCKERS`: `none`
- `UTC_RECORDED`: `2026-07-27T22:57:33Z`

The R2 candidate preserves all original Gate 5 obligations and repairs the
five Linux portability/evidence defects that blocked Gate 6. It produced 18
exact-candidate preflight receipts plus three semantic repeats under network
denial with zero trial residue. Independent GLM 5.2 and exact Claude Opus 4.8
returned GREEN over one sanitized packet hash; Claude recusal is clear.

This status does not claim Gate 6, a measured 54-execution campaign, a baseline
or product winner, Linux RunPod execution, S3-R2, release, or submission.
Behaviorally relevant changes after candidate commit `8718fbe` invalidate new
downstream evidence and require another candidate. Gate 6 R2 still requires a
separate Linux preflight packet and its declared same-hash reviews before any
RunPod worker.
```

## FILE: HARDENING_GATE5_GREEN_CHECKPOINT_R2.md

```text
# Hardening Gate 5 — Green Checkpoint R2

- `STATUS`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `PARENT_GATE`: `HARDENING_4_BASELINE_PROTOCOL_R2_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `GATE4_PROTOCOL_R2_SHA256`: `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`
- `FINAL_PACKET_SHA256`: `41efeb9270b76a0d4e1f711d5b1ab3270ecd92d32eccce93f07bef8a6ba036c0`
- `STATUS_FILE_SHA256`: `c9bf7e330187695e2b359ed3510aaa00d7bd5c7026f421aede7430c7ea8a1cae`
- `EVIDENCE_REPORT_SHA256`: `5d65945758d1b5f5aff77c9c24f6d28ded69e3e1ffddabe56e3db81433f10757`
- `JUDGE_RECEIPTS_SHA256`: `aff4cd568995238f6fe885937ff6cbc51853cfd0d31625abb7784be4a3342efb`
- `SECRET_SCAN_CLASSIFICATION_SHA256`: `db854b232615376316124f81af409309ea2de411764e255cfd9a5a209a122749`
- `SANITIZED_SMOKE_SUMMARY_SHA256`: `08d23b3fe14b2c623c79344f203e74ec5571fb696d88a2e0c1fb93f294ba6801`
- `GLM_RAW_SHA256`: `aeb7368a182fd1ad4cdfc615e0e31828c1ec80a1e36418ca585b9c1b5d6cc644`
- `CLAUDE_RAW_SHA256`: `120f440b93e0ed0557910bda585bf2958dad5d12a377acb145cdd704766907b4`
- `JUDGE_STATE`: `GLM_5_2_GREEN; CLAUDE_OPUS_4_8_GREEN_RECUSAL_CLEAR`
- `CHECKPOINT_TAG`: `hardening-gate5-r2-green`
- `NEXT_TARGET`: `HARDENING_6_RUN1_R2_PREFLIGHT`
- `UTC_RECORDED`: `2026-07-27T22:57:33Z`

The candidate is frozen for a new Gate 6 preflight. This checkpoint does not
authorize provider creation or claim any Linux measured execution. Gate 6 must
freeze exact Linux tool provenance, orchestration, payload, worker/cost/lifecycle
controls, and obtain its separately required same-hash reviews first.
```

## FILE: HARDENING_GATE5_JUDGE_RECEIPTS_R3.md

```text
# Hardening Gate 4/5 — Independent Judge Receipts R3

- `PACKET`: `HARDENING_GATE5_JUDGE_PACKET_R3.md`
- `PACKET_SHA256`: `41efeb9270b76a0d4e1f711d5b1ab3270ecd92d32eccce93f07bef8a6ba036c0`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `GLM_VERDICT`: `GREEN`
- `GLM_GATE4`: `GREEN`
- `GLM_GATE5`: `GREEN`
- `GLM_SERVED_MODEL`: `glm-5.2`
- `GLM_RAW_SHA256`: `aeb7368a182fd1ad4cdfc615e0e31828c1ec80a1e36418ca585b9c1b5d6cc644`
- `GLM_STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`
- `CLAUDE_VERDICT`: `GREEN`
- `CLAUDE_SERVED_MODEL`: `claude-opus-4-8`
- `CLAUDE_EFFORT`: `max`
- `CLAUDE_TOOLS`: `none`
- `CLAUDE_RECUSAL`: `clear`
- `CLAUDE_RAW_SHA256`: `120f440b93e0ed0557910bda585bf2958dad5d12a377acb145cdd704766907b4`
- `CLAUDE_STDERR_SHA256`: `c6dea656f0336e75a49164fdfd39a7ef9db366b633581d0bc82b708a31bf5e64`
- `UTC_RECORDED`: `2026-07-27T22:57:33Z`

Both independent families reviewed the same exact packet and returned GREEN.
GLM explicitly returned Gate 4 and Gate 5 GREEN. Claude reported no blockers
and a clear recusal check. Claude's no-tool evidence gaps and both judges'
residual limitations remain carried into Gate 6; they are not evidence that a
Linux campaign has already run.

The first GLM R3 egress attempt was blocked locally before provider execution
because the packet rendered a scanner label as an assignment. Its zero-byte
stdout and exact sanitizer error remain in ignored runtime custody. The packet
was reformatted without changing candidate bytes, rehashed, rescanned, and the
successful same-hash panel used only the final hash above.
```

## FILE: HARDENING_GATE5_EVIDENCE_REPORT_R2.md

```text
# Hardening Gate 5 — Portability Repair Evidence Report R2

## Control fields

- `STATUS`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `PARENT_GREEN_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_GREEN_R1`
- `BLOCKER_BEING_REPAIRED`: `EVIDENCE_CANDIDATE_INVALIDATED`
- `TARGET`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `CANDIDATE_PARENT_COMMIT`: `381e74fa5f6c1d55a743b6ccabf4c4674618eee2`
- `CANDIDATE_DIFF_SHA256`: `662980134ae0ab7516478b5247588940d21e4d2b609806407e72be0760b6231e`
- `GATE4_PROTOCOL_R1_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `GATE4_PROTOCOL_R2_SHA256`: `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `HARDENING_PLAN_SHA256`: `1ce953127138a35bd9588d686bbefefc0b012e8f2188a8fea736842030d57310`
- `RUNPOD_ACTION`: `none`
- `PUBLIC_ACTION`: `none`
- `UTC_RECORDED`: `2026-07-27T22:49:43Z`
- `FINAL_JUDGE_PACKET_SHA256`: `41efeb9270b76a0d4e1f711d5b1ab3270ecd92d32eccce93f07bef8a6ba036c0`
- `GLM_JUDGE`: `GLM_5_2_GREEN_GATE4_AND_GATE5`
- `CLAUDE_JUDGE`: `CLAUDE_OPUS_4_8_GREEN_RECUSAL_CLEAR`

## Exact repair

The R1 candidate remains historical and invalid for Linux Gate 6. R2 changes
only the portability and evidence-mode contract that caused the blocker:

1. Scenario bytes now embed the platform-neutral command
   `["python3","tests/check.py"]`; no absolute interpreter path enters source,
   event, loss, or allowed-information hashes.
2. The interpreter is resolved from the isolated trial `PATH`, version-invoked,
   byte-hashed, used for the executable test, and recorded in every method's
   receipt.
3. `CK_GATE5_GIT` selects one exact Git binary. The same binary is used for all
   Git operations, version-invoked, byte-hashed, and recorded instead of
   unconditionally claiming Apple Git.
4. Restic accepts only the exact official Darwin arm64 or Linux amd64 0.19.0
   binary hash, and its observed version output must match the hash-specific
   allowlist.
5. Canonical receipts use schema `gate5-comparative-receipt-v2` with required
   `evidence_mode` and `runtime_platform` fields.
6. `MEASURED_GATE6` fails closed unless the runtime is Linux, candidate commit
   is 40 lowercase hexadecimal characters, and campaign ID begins
   `ck-gate6-`. Preflight and measured limitations are exact and disjoint.
7. The validator requires the correct tool-provenance key set for each method
   and 64-character lowercase SHA-256 values.

No scenario class, repetition, method, event order, loss operation, work unit,
expected result, score, timeout, authority rule, verifier byte, held-out vector,
or conventional-baseline capability changed.

## Frozen source and runtime hashes

| Artifact | SHA-256 |
|---|---|
| `HARDENING_GATE4_BASELINE_PROTOCOL_R2.md` | `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52` |
| `hardening-gate5/comparative.py` | `f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec` |
| `hardening-gate5/run_smoke.py` | `91ad388ef6d4972cc2c6a248dd147eb1d93a38515a2c6d645ccb395b28fb3de6` |
| `hardening-gate5/test_comparative.py` | `605b0346a08d7181b563f29eb819dada0618fe7c980cf372d60435ca2d46c50f` |
| `hardening-gate5/scenarios/seeds.json` | `e2116b9bbe68671072cc6419e494d722fb4e285493338421ea58a806676c6f6d` |
| `hardening-gate5/heldout_contract.py` | `b5de48cf64cddb505238b835d026fad6ed39917c129bf3b4194f430da1f69801` |
| `p4-verifier/verifier.py` | `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40` |
| official Restic Linux amd64 archive | `13176fe6d89d4357947a2cd107218ab2873a5f9d8e1ac2d4cd1c8e07e6839c21` |
| official Restic Linux amd64 binary | `ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c` |

## Mechanical evidence

- Parser/compile gate: PASS.
- Comparative contract tests: `7/7` PASS, including platform-neutral source,
  both evidence modes, Linux-only measured guard, candidate/campaign guards,
  and both Restic platform hashes.
- Broader non-live regression set: `264/264` PASS across 22 test files.
- Exact-candidate smoke: `18/18` canonical preflight receipts plus three
  semantic repeats, all from candidate
  `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`.
- Pair source/event/loss equality: `6/6` classes for the one-repetition smoke.
- Receipt schema/mode/candidate/protocol validation: `18/18`.
- Python provenance present: `18/18`; Git provenance present for all twelve
  Git-bearing receipts; Restic provenance present for all six Restic receipts.
- Network-denial probe: `BLOCKED`.
- Cleanup: `18/18`; residue bytes: `0`.
- Internal smoke summary SHA-256:
  `781531c80ce1415ca208c4f2119cb57be660db73276f556610f1b57dd83b7c1b`.
- Raw summary SHA-256:
  `f79137a47eac4a634044f8b5dec23e4e93c1a94e163b0343190a14c5aa6998d3`.
- Raw 22-file evidence manifest SHA-256:
  `f88a0d6f86d4f3e1b5c96d85f64e845da47a4790ae33b9d14838f54e36e1b487`.
- Tracked sanitized summary:
  `evidence/hardening-gate5-portability-r2/summary.json`.
- `git diff --check`: PASS.
- Gitleaks staged scan: no leaks. `detect-secrets` reported only six
  unverified high-entropy hexadecimal test/provenance hashes; no credential.

## Fail-closed boundary

This report does not claim Linux execution, Gate 6 measured evidence, a
54-execution campaign, product superiority, S3-R2, release, or submission.
Gate 6 must still verify the exact Linux Git/Python/Restic versions and hashes,
freeze them in its preflight packet, prove unprivileged network denial, and
obtain its separately required preflight reviews before any measured worker.
Any behaviorally relevant change after candidate commit `8718fbe` invalidates
new downstream evidence.

## Independent review

GLM 5.2 and exact Claude Opus 4.8 independently reviewed the same sanitized
packet hash. GLM returned overall GREEN with Gate 4 and Gate 5 individually
GREEN. Claude returned GREEN, no blockers, and `recusal_check=clear`. Their
limitations remain mandatory for Gate 6 and public claims.
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

## FILE: p4-verifier/verifier.py

```text
"""P4 deterministic verifier and quarantine authority."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
ALLOWED = {
    "version", "candidate_id", "source_receipt_hash", "payload", "payload_hash",
    "schema_version", "provenance", "supported", "one_use_state", "quarantined",
    "policy_veto", "requested_paths", "declared_paths",
}


class VerifyError(ValueError):
    pass


def canonical(value: Any) -> bytes:
    try:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise VerifyError("MALFORMED_RECORD") from exc
    if len(raw) > 65536:
        raise VerifyError("RECORD_TOO_LARGE")
    return raw


def digest(value: Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def _paths_safe(paths: Any, declared: Any) -> bool:
    if not isinstance(paths, list) or not isinstance(declared, list):
        return False
    declared_set = set(declared)
    for path in paths:
        if not isinstance(path, str) or "\x00" in path or path.startswith("/"):
            return False
        parts = path.split("/")
        if ".." in parts or path not in declared_set:
            return False
    return True


@dataclass
class Quarantine:
    _records: dict[str, dict[str, Any]] = field(default_factory=dict)

    def insert(self, record: dict[str, Any]) -> None:
        candidate_id = record.get("candidate_id")
        if not isinstance(candidate_id, str) or not ID_RE.fullmatch(candidate_id):
            raise VerifyError("INVALID_ID")
        self._records[candidate_id] = json.loads(canonical(record))

    def contains(self, candidate_id: str) -> bool:
        return candidate_id in self._records

    def active(self) -> list[dict[str, Any]]:
        # Quarantined records have no active retrieval path by construction.
        return []

    def retrieve(self, candidate_id: str) -> None:
        return None


def verify(record: Any, quarantine: Quarantine | None = None) -> tuple[str, str]:
    """Return only deterministic (verdict, stable_reason_code)."""
    if not isinstance(record, dict):
        return "INVALID", "MALFORMED_RECORD"
    if set(record) - ALLOWED:
        return "INVALID", "UNKNOWN_FIELD"
    required = ALLOWED
    if not required.issubset(record):
        return "INVALID", "MISSING_FIELD"
    if not isinstance(record["candidate_id"], str) or not ID_RE.fullmatch(record["candidate_id"]):
        return "INVALID", "INVALID_ID"
    if record["schema_version"] != "p4-v1":
        return "REFUSE", "UNSUPPORTED_SCHEMA"
    if not isinstance(record["source_receipt_hash"], str) or not HEX64_RE.fullmatch(record["source_receipt_hash"]):
        return "INVALID", "INVALID_RECEIPT_HASH"
    if record["payload_hash"] != digest(record["payload"]):
        return "REFUSE", "HASH_MISMATCH"
    if not isinstance(record["provenance"], dict) or not record["provenance"].get("source"):
        return "INVALID", "MISSING_PROVENANCE"
    if record["one_use_state"] == "CONSUMED":
        return "REFUSE", "REPLAYED_TICKET"
    if record["quarantined"] or (quarantine and quarantine.contains(record["candidate_id"])):
        return "REFUSE", "QUARANTINED_INPUT"
    if not record["supported"]:
        return "REFUSE", "UNSUPPORTED_INPUT"
    if record["policy_veto"]:
        return "REFUSE", "POLICY_VETO"
    if not _paths_safe(record["requested_paths"], record["declared_paths"]):
        return "REFUSE", "UNSAFE_PATH"
    return "PROMOTE", "VERIFIED"
```
