# PDH-3 R12 R6 PF-4 minimum-vCPU replacement lifecycle packet R1

Status: `FROZEN_FOR_EXACT_HASH_GLM_5_2_REVIEW__NO_WORKER_CREATED`

UTC frozen: `2026-08-02T11:00:00Z`

Builder: `Codex / Icarus`

Decision requested: determine whether the prospective minimum-vCPU repair and
remaining PF-4-only replacement envelope are sufficiently bounded,
fail-closed, evidence-preserving, and safe to execute. This packet cannot
self-approve. It does not authorize main-bundle upload, PF-2R through PF-7, or
the measured 24-hour campaign.

## 1. Authority and remaining envelope

- operator authorization:
  `PDH3_R12_R6_PF4_RETRY_AUTHORIZATION_20260802_R1.md`;
- authorization SHA-256:
  `4fa410bfcd2e7307b79e7ffca2747b10ad50d0cfff320119ce73e44045a5fe1f`;
- one of the three additional attempts has been consumed and preserved;
- this packet permits at most two remaining sequential creation attempts;
- one worker at a time;
- stop after the first real PF-4 success;
- delete every worker and prove exact-ID absence, empty campaign inventory,
  and `TEARDOWN_GREEN`;
- aggregate campaign cost ceiling remains `$12.00`;
- three consecutive occurrences of the same cgroup-CPU failure stop retries.

Any deterministic defect or capability failure requires local diagnosis, new
hashes, and fresh same-hash GLM 5.2 GREEN. Only provider/capacity failures may
retry under an unchanged exact packet.

## 2. Preserved failure and repair mechanism

The first attempt under the replacement envelope is immutable failed evidence:

- receipt:
  `PDH3_R12_R6_PF4_RETRY_ATTEMPT_01_BLOCKED_RECEIPT_20260802_R1.md`;
- receipt SHA-256:
  `100f7a0201d31f1177108ca64a6a1e70aa4f05d7cdd268708ad07715d1c63dd1`;
- Pod ID: `scdti1prghpxbv`, deleted;
- returned shape: 16 vCPU / 125 GiB / Secure L40S / `US-MO-1`;
- exact affinity readback: 16 CPUs;
- real cgroup v2 effective CPUs: 13;
- fixed minimum: 16;
- every other PF-4 capability check: GREEN;
- main bundle uploaded: false;
- measured 24-hour clock started: false;
- final campaign inventory: `[]`.

Datacenter pinning did not control the provider CPU shape. A second identical
placement retry would be blind. The prospective correction changes only the
creation constraint:

- call RunPod's official GraphQL endpoint using HTTPS;
- authenticate with a host-only Bearer header;
- request `minVcpuCount: 24` and `minMemoryInGb: 94`;
- preserve native `stopAfter` and `terminateAfter` fields in the same creation
  request;
- require post-create provider readback of at least 24 vCPU;
- retain the real cgroup PF-4 minimum of 16 and the 4-GiB-per-effective-CPU
  rule unchanged.

No threshold is weakened. The 24-vCPU provider request is a buffer against the
observed provider/container quota distinction; only measured cgroup accounting
can pass PF-4.

## 3. Official API provenance

Current official sources were fetched read-only on `2026-08-02`:

| Source | Relevant current fact | Retrieved SHA-256 |
|---|---|---|
| `https://docs.runpod.io/sdks/graphql/manage-pods` | official create example includes `minVcpuCount` | `b8ad4fe990fed351979f70d74583f82d5a0a931bb918e765c6122477004eb15d` |
| `https://docs.runpod.io/references/graphql-spec` | `PodFindAndDeployOnDemandInput` exposes `minVcpuCount`, `stopAfter`, and `terminateAfter` | `183a5a3cce8cae73e5721d3b8892e88bd22fb5c153d76866485a9cc6f691c7a8` |
| `https://github.com/runpod/runpodctl/blob/main/cmd/pod/create.go` | CLI binds deadlines and datacenter but omits a `minVcpuCount` flag | `cc03550f7d890526464cc2c666c10e0e75285d7d7aea9b36c40fd7aeaa43274f` |
| `https://github.com/runpod/runpodctl/blob/main/internal/api/graphql.go` | official client sends the API key in a Bearer header | `6c32e7d8e4a4e24a0e4890417bbd4b9476ac3a46e1f5e210937215e1ec86c830` |

- current official `runpodctl` main commit observed:
  `22dc71f8a2d7992befda9a40a24f356c43f70398`;
- locally bound CLI remains version `2.7.2-309512b`, SHA-256
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`;
- the new creation request does not depend on an undocumented CLI flag;
- all inventory, get, SSH, delete, and teardown operations remain on the bound
  CLI.

## 4. Provider and worker contract

- RunPod Secure Cloud;
- exactly one NVIDIA L40S;
- image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- minimum provider vCPU readback: 24;
- minimum provider RAM readback: 94 GiB;
- real cgroup effective-CPU minimum: 16;
- 4 GiB RAM per effective CPU;
- compute price ceiling: `$0.99/hour`;
- 250 GB disposable container disk;
- zero persistent volume;
- zero network volume;
- one worker at a time;
- synthetic narrow PF-4 capability material only;
- main archive transfer forbidden.

The frozen current L40S datacenter allowlist is:

`EU-NL-1`, `EUR-IS-2`, `US-IL-1`, `US-MO-1`, `US-NC-1`, `US-TX-3`,
`US-TX-4`.

The GraphQL request leaves `dataCenterId` unset so the Secure Cloud scheduler
may select any currently capable machine satisfying `minVcpuCount: 24`. The
post-create readback rejects any datacenter outside the frozen list, any worker
below 24 provider vCPUs, or any mismatch in cloud, GPU, image, disk, volume,
price, name, or campaign.

## 5. Credential boundary

The operator-authorized local RunPod credential may be read solely from
`~/.runpod/config.toml` and injected into the local controller environment.
The creation request sends it only in the HTTPS `Authorization: Bearer` header.
It is never placed in URL, body, argv, output, receipt, hash, commit, archive,
or worker. Unit tests inspect the request and prove this boundary.

GraphQL errors are normalized into credential-free stable error classes. Raw
HTTP response bodies are not copied into evidence. Any credential exposure is
terminal and forbids retry.

## 6. Fresh campaign, deadlines, and cost

- campaign ID: `ck-pdh3-r12-preflight-r6-minvcpu-r1`;
- remaining attempts: 2;
- launch opens: `2026-08-02T11:08:00Z`;
- launch closes: `2026-08-02T11:53:00Z`;
- native stop deadline: `2026-08-02T13:58:00Z`;
- native terminate deadline: `2026-08-02T14:13:00Z`;
- detached guard heartbeat: 30 seconds;
- successful or failed PF-4 causes immediate deletion.

All attempts share the same absolute provider deadlines. Retry count therefore
cannot multiply the maximum paid lifetime.

```text
compute_rate = $0.99/hour
storage_rate = 250 GB * $0.10/GB-month / 720 = $0.0347222222/hour
maximum_active_rate = $1.0247222222/hour
maximum safety-window exposure = 3.25 hours
mechanical maximum = $3.3303472222
aggregate ceiling = $12.00
```

Unknown price, cost uncertainty, unexpected existing spend, or any possible
aggregate-ceiling breach stops before creation or triggers teardown.

## 7. Implementation and tests

- branch: `evidence/external-validity-r1`;
- implementation commit:
  `4326fe0a8f6253b10282bd21b1446d1df04b15f7`;
- focused verification: 32 tests GREEN;
- `py_compile`: GREEN;
- `git diff --check`: GREEN;
- unrelated untracked `heap_profiler/`: user-owned and excluded.

| Bound file | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_r6_config.py` | `6bda5714c56c92ee889ddfccb324a502609ec4a045ddd661cb1c403edf737c4e` |
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `eb48522771f329a343620a2bc4c25f28ca3e4db7a85e5bc5791b8638445960e3` |
| `post-dogfood/test_pdh3_r12_r6_config.py` | `54ec491c75186407772a89233f6a3d54d12d66d9c3a9700f563a7a2b6059a6f7` |
| `post-dogfood/test_pdh3_r12_r6_launch_pf4.py` | `7cda95b1a080303794a9b47e2740f101c8b5c8015ce741cb88844bfaea7c23f0` |
| `post-dogfood/pdh3_r12_r6_pf4_only.py` | `82bd65a88f530b611f249ea959d995eeb9aca02e227c68c1622127eac9eaabaf` |
| `post-dogfood/pdh3_r12_cpu_affinity.py` | `87de9fb5d02fb1eee468601058086e34dfd4a553765b312672f59584e61dd707` |
| `post-dogfood/pdh3_r12_remote_capability.py` | `ee271da20d92a1251e2804287dbcfd585c5441b4f1f61cf21bc5e62fd6d96d0d` |
| `s2-soak/lifecycle_guard.py` | `70c12ea1ae19f69a43fb38100d90bda8f5e0a41ae30d2b6c509b331933a9e14d` |

Tests cover strict v4 configuration, exact min-vCPU and native deadline
bindings, secret exclusion from URL/body/output, missing-credential refusal,
provider-readback rejection below 24 vCPU, affinity, PF-4 terminal semantics,
cgroup v1/v2 accounting, and teardown requirements.

## 8. Fresh deterministic package

Package root:
`.pdh3-runtime/r12-preflight/pf4-retry-minvcpu-20260802-r2/`

- archive bytes: `143989823`;
- archive SHA-256:
  `5a72110740335cd76128343db28eb26741d5b54f1a1b7ea22dd9a87fd754e1f0`;
- bundle-receipt file SHA-256:
  `408fc202adcb4dea2b35a07c3712f00ed65c44cb50bfef783c52e603ec63a1cf`;
- embedded receipt SHA-256:
  `0bc99abde8d1f954152382c35e8442f03b4a6b331dff0eab7a95c8f151ac4ac1`;
- manifest SHA-256:
  `105493fb7dc70f9567d951c6a7c387526d002076caa409c158459ecccceb2e0b`;
- host-only bindings SHA-256:
  `f02470ee5b6d35132d2963612cf1f33bf41e1000bf93d2da2eb267284b98f625`;
- host-only source-set SHA-256:
  `b0a2c7cb48a8d582a94a0b9ef2623981e9acd0533cce0405605cf7d3ac11f5f9`;
- smoke-receipt file SHA-256:
  `588daf7b5eec4f992121aa98a1c6c62bdcc2cf36340b444c35b77b830dbd82fa`;
- package smoke: GREEN, 35 Python files compiled and 13 bundled tests GREEN.

The archive remains bound but forbidden from transfer during PF-4.

## 9. Attempt and teardown law

For each remaining attempt:

1. verify empty active inventory, available Secure L40S, sufficient balance,
   current spend, CLI hash, packet hash, and credential boundary;
2. create through the exact credential-free-body GraphQL request;
3. persist the credential-free request hash and sanitized response;
4. bind the exact-ID detached lifecycle guard;
5. prove SSH readiness and post-create worker readback;
6. reject below-24 provider vCPU before PF-4;
7. run the narrow PF-4 probe once;
8. retrieve and hash all evidence before deletion;
9. delete and prove exact-ID absence, inventory `[]`, and `TEARDOWN_GREEN`.

A capability failure returns to diagnosis. A transient GraphQL/provider,
capacity, returned-shape, or readiness failure may consume the second numeric
attempt only after complete teardown and only while this packet is unchanged.

## 10. PF-4 pass contract and kill lines

PF-4 GREEN requires all of:

- provider readback at least 24 vCPU and 94 GiB;
- real cgroup effective CPUs at least 16;
- exact affinity application/readback and child inheritance;
- at least 4 GiB RAM per effective CPU;
- unchanged disk, fsync, sequential, sustained, random-sync, network-observer,
  process/resource accounting, and residue gates;
- retrieved hash-valid evidence;
- exact-ID absence, inventory `[]`, and `TEARDOWN_GREEN`.

Stop and teardown on any mismatch, below-threshold result, secret exposure,
unexpected egress, missing evidence, lifecycle failure, cost uncertainty, or
third consecutive 13-effective-CPU result. No threshold weakening, silent
hardware substitution, main-bundle upload, later preflight, or measured
24-hour start is permitted.

## 11. Independent judge contract

GLM 5.2 receives this exact sanitized packet only. It is non-authoring and has
no shell, write, repository, credential, browser, provider, worker-launch,
implementation, or approval authority.

It must return exactly:

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: <exact packet SHA-256>
VERDICT: GREEN|NOT_GREEN|JUDGE_UNAVAILABLE
BLOCKERS:
- none | <blocker>
NON_BLOCKING_RISKS:
- <risk or none>
EVIDENCE_REQUIRED:
- <evidence or none>
```

`GREEN` permits only this minimum-vCPU PF-4-only lifecycle. It does not prove
PF-4 or authorize main-bundle upload, PF-2R through PF-7, or the measured
24-hour campaign.
