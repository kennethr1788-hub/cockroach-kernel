# PDH-3 R12 R6 PF-4 minimum-vCPU result packet R1

Status: `FROZEN_FOR_EXACT_HASH_GLM_5_2_RESULT_REVIEW`

UTC frozen: `2026-08-02T11:12:18Z`

Builder: `Codex / Icarus`

Decision requested: determine whether the exact packet-bound PF-4-only
lifecycle produced valid capability evidence and complete teardown evidence.
The builder cannot self-approve. This packet does not authorize main-bundle
upload, PF-2R through PF-7, or the measured 24-hour campaign.

## 1. Bound preflight authority

- lifecycle packet:
  `PDH3_R12_R6_PF4_MIN_VCPU_LIFECYCLE_PACKET_20260802_R1.md`;
- lifecycle-packet SHA-256:
  `c1bdd33757c7ca894fc0b15d996f91db703d8d44c82484b106d4bd92348517e6`;
- lifecycle-packet commit:
  `de095d68a40af56ba9dd33624042d9fb3c23b647`;
- exact preflight judge: direct `glm-zai`, served model `glm-5.2`;
- preflight verdict: `GREEN`;
- preflight raw SHA-256:
  `d80a27e1807aa4f127270a196ffe41caf634d6c7624914a16019ef9ac9a6184c`;
- runtime configuration SHA-256:
  `844c46e6fcacae6d6e3824c004d7d18eaf1530355626f2563d3b9c3678ae8f08`.

## 2. Provider creation and returned shape

- campaign: `ck-pdh3-r12-preflight-r6-minvcpu-r1`;
- attempt: `1` of at most `2`;
- Pod ID: `luro78hz0upemt`;
- Pod name: `ck-pdh3-r12-preflight-r6-minvcpu-r1-01`;
- provider cloud: Secure Cloud;
- provider GPU: one NVIDIA L40S;
- datacenter: `US-MO-1`, within the frozen allowlist;
- image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- provider vCPUs: `32` (minimum requested and required: `24`);
- provider RAM: `125 GiB` (minimum required: `94 GiB`);
- container disk: `250 GB`;
- persistent/network volume: `0`;
- compute price: `$0.99/hour`, equal to the frozen ceiling;
- provider stop deadline: `2026-08-02T13:58:00Z`;
- provider terminate deadline: `2026-08-02T14:13:00Z`.

The credential-free GraphQL request SHA-256 was
`7ac617e6bb0d8a1dd5d9e6e33ea34c27df8cd9489fa9e151bb99791d2444353e`.
The credential was transmitted only in the HTTPS Bearer header from the local
controller environment and was never uploaded to the worker.

## 3. Measured PF-4 capability result

The worker was affinity-capped to 31 logical CPUs to preserve the declared
4-GiB-per-effective-CPU ratio. Exact affinity application, readback, and child
inheritance passed. Real cgroup-v2 accounting then measured:

- cgroup CPU quota: `27` effective CPUs;
- cgroup memory: `124,999,999,488` bytes;
- required minimum: `16` effective CPUs and 4 GiB per effective CPU;
- container `/proc`/cgroup accounting: available and GREEN;
- available disk before test: `268,415,766,528` bytes;
- sequential throughput: `1,701.760 MiB/s`;
- sustained throughput: `1,656.955 MiB/s`;
- random sync IOPS: `8,098.099`;
- fsync p99: `0.287364 ms` over 200 samples;
- streaming network observer: GREEN;
- process tree: available;
- monotonic clock: advanced;
- benchmark residue removed: true;
- all 15 recorded capability checks: true;
- capability verdict: `GREEN`.

This is a narrow platform-capability result. It is not the full-cardinality
PF-2R through PF-7 preflight and it is not the 24-hour measured workload.

## 4. Workload and claim boundary

- main bundle uploaded: false;
- full-cardinality dataset seeded: false;
- PF-2R through PF-7 executed: false;
- measured 24-hour clock started: false;
- product claim promoted: false.

Only the narrow PF-4 scripts and network observer were transferred and run.

## 5. Teardown and credential-residue proof

- PF-4 execution return code: `0`;
- delete command completed;
- exact-ID lookup after deletion: provider `404 pod not found`, exit `1`;
- exact-ID stderr SHA-256:
  `abb343a1a20364080e68a3fa77e863e71c3dc444e3f06cb1467cdf87df479556`;
- fresh campaign/account Pod inventory: `[]`;
- lifecycle hash chain: valid, four events;
- terminal lifecycle event: `TEARDOWN_GREEN`;
- terminal lifecycle event hash:
  `93c32387b51bb06298a0fc3a44a6e16e7cf517839495b88848deb301708f7091`;
- detached guard process: exited after teardown;
- paid worker remaining: none.

The bound CLI created a 53-byte parser/config placeholder under the guard's
isolated sandbox HOME. It did not contain the exact active API key; a byte-exact
credential scan found zero credential copies before cleanup. The unnecessary
placeholder was removed from the sandbox runtime, followed by a second
byte-exact scan finding zero credential copies. `gitleaks --redact` returned
exit 0, `detect-secrets` returned zero findings, and a targeted credential-name
scan returned no paths. This cleanup did not alter any measured worker or
lifecycle evidence.

## 6. Core evidence hashes

| Evidence | SHA-256 |
|---|---|
| `attempt-01/create.request.json` | `7ac617e6bb0d8a1dd5d9e6e33ea34c27df8cd9489fa9e151bb99791d2444353e` |
| `attempt-01/create.stdout` | `536aa3aeaee06012883944ff7ee143f3d1c07f8fd374fa92a1d69689dce12221` |
| `attempt-01/pod-get.json` | `4b45aeb025ac4285a64d944e9b48446b35396ea9a24c79da8a8a3f4c16c2f7a9` |
| `attempt-01/lifecycle.ndjson` | `bde95d2bb2731c886ac38986c1c91f743d55c67f08820cecb0cc22c7f7700265` |
| `attempt-ledger.json` | `52c8bf333eb4a77040dc2d41c33bbbe5727ecd13c0dc37b8bba58a1f2bf0ef17` |
| `running-worker-receipt.json` | `720b5003f7dec46ea9cc347431f0da5799c125b3c95e427190c9066f4b80ff70` |
| `PF4_CAPABILITY_RECEIPT.json` | `676f09cc22405925c5b7e1fc38b60806b2fb524c11b0b0d09e160a1c4a4bd654` |
| `PF4_HOST_RECEIPT.json` | `3e98ddbda3d9b5a7bf92ffe8c216f51a72edab282df05d8c219bfb8e83372e94` |
| `PF4_ONLY_TERMINAL.json` | `a503dabe395f8f430278d2535af436d308284cf82483c82d91c69b5956dc4c83` |
| `pf4-only-delete.stdout` | `3c629eebcd72e4ecd34dd9c0407d6c4fab3dcf3bb48d24282a0cd274db2cdf3d` |

The terminal receipt binds:

- status: `PF4_ONLY_GREEN`;
- internal receipt SHA-256:
  `77c9d08e031c4bc0a66fa696d05c7ef87677e49507019e099f0e16d668ca175b`;
- teardown internal receipt SHA-256:
  `6d6c653d3963ea3f6ddd87ee12dbd530b25b3693a80107ede52b264f2b7b65d8`.

## 7. Result-review contract

The independent GLM 5.2 reviewer receives this exact sanitized result packet
only. It has no shell, write, repository, credential, browser, provider,
worker-launch, implementation, or approval authority.

It must return exactly:

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: <exact result-packet SHA-256>
VERDICT: GREEN|NOT_GREEN|JUDGE_UNAVAILABLE
BLOCKERS:
- none | <blocker>
NON_BLOCKING_RISKS:
- <risk or none>
EVIDENCE_REQUIRED:
- <evidence or none>
```

`GREEN` validates only this PF-4-only capability and teardown result. It does
not authorize or validate later preflight stages or the 24-hour campaign.
