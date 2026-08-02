# PDH-3 R12 R6 PF-4 minimum-vCPU final receipt R1

Status: `PDH3_R12_R6_PF4_MIN_VCPU_GREEN`

UTC closed: `2026-08-02T11:14:12Z`

## Result

- campaign: `ck-pdh3-r12-preflight-r6-minvcpu-r1`;
- successful attempt: `1`;
- Pod ID: `luro78hz0upemt`;
- returned worker: Secure Cloud NVIDIA L40S, `US-MO-1`, 32 provider
  vCPUs, 125 GiB RAM, 250 GB disposable disk, zero persistent/network
  volume, `$0.99/hour`;
- measured effective cgroup capacity: 27 CPUs and 124,999,999,488 bytes;
- PF-4 capability result: `GREEN`;
- main bundle uploaded: false;
- measured 24-hour clock started: false;
- exact-ID absent after deletion: true;
- final Pod inventory: `[]`;
- lifecycle terminal state: `TEARDOWN_GREEN`.

## Hash custody

- preflight packet SHA-256:
  `c1bdd33757c7ca894fc0b15d996f91db703d8d44c82484b106d4bd92348517e6`;
- preflight GLM raw SHA-256:
  `d80a27e1807aa4f127270a196ffe41caf634d6c7624914a16019ef9ac9a6184c`;
- result packet SHA-256:
  `6cfc61dc3f9b9709e2d6724fc9b86f7af9c8e64d2d8778239e428ba171d4b031`;
- capability evidence file SHA-256:
  `676f09cc22405925c5b7e1fc38b60806b2fb524c11b0b0d09e160a1c4a4bd654`;
- host receipt file SHA-256:
  `3e98ddbda3d9b5a7bf92ffe8c216f51a72edab282df05d8c219bfb8e83372e94`;
- terminal receipt file SHA-256:
  `a503dabe395f8f430278d2535af436d308284cf82483c82d91c69b5956dc4c83`;
- lifecycle log SHA-256:
  `bde95d2bb2731c886ac38986c1c91f743d55c67f08820cecb0cc22c7f7700265`;
- lifecycle terminal event hash:
  `93c32387b51bb06298a0fc3a44a6e16e7cf517839495b88848deb301708f7091`.

## Independent final review

- route: direct `glm-zai`;
- served model: `glm-5.2`;
- target result-packet SHA-256:
  `6cfc61dc3f9b9709e2d6724fc9b86f7af9c8e64d2d8778239e428ba171d4b031`;
- verdict: `GREEN`;
- blockers: none;
- non-blocking risks: none;
- missing evidence: none;
- raw output:
  `PDH3_R12_R6_PF4_MIN_VCPU_RESULT_GLM_RAW_20260802_R1.txt`.
- raw-output SHA-256:
  `7cf046547d66dd0221696682acf8150fe5744107b1511f81223ef170d2f27828`.

## Boundary

This closes only the repaired PF-4 capability lifecycle. It does not claim or
authorize PF-2R through PF-7, main-bundle upload, a full-cardinality remote
preflight, or the measured 24-hour campaign.
