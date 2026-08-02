# PDH-3 R12 R6 PF-4-only final receipt R1

Status: `PF4_ONLY_BLOCKED_CONFIRMED`

Blocker: `EFFECTIVE_CGROUP_CPU_BELOW_MINIMUM`

UTC closed: `2026-08-02T10:10:23Z`

## Execution result

- operator authorization: recorded;
- exact-hash lifecycle preflight: GLM 5.2 GREEN;
- worker created: one;
- Pod ID: `7g0k4sfm35r1gh`;
- returned shape: 16 vCPU / 188 GiB / L40S;
- real affinity application/readback: exactly 16 CPUs, GREEN;
- real cgroup CPU quota: 13 CPUs;
- fixed minimum: 16 CPUs;
- PF-4: BLOCKED;
- main bundle uploaded: false;
- measured 24-hour clock started: false;
- worker deleted: true;
- exact Pod lookup: absent;
- campaign and current provider inventory: `[]`;
- lifecycle terminal: `TEARDOWN_GREEN`.

## Independent result review

- packet:
  `PDH3_R12_R6_PF4_ONLY_RESULT_REVIEW_PACKET_20260802_R1.md`;
- packet SHA-256:
  `7b29fad5cd22c02bb205e3de2de184e9e9f9c3a2bfce4b956f503633bf30abab`;
- judge: direct GLM 5.2, exact model, fallback disabled;
- raw output:
  `PDH3_R12_R6_PF4_ONLY_RESULT_GLM_RAW_20260802_R1.txt`;
- raw output SHA-256:
  `0238009bb038830b52e97bd9567734ba1fe57c2f1db3c794ec0305308b6fde70`;
- verdict: `BLOCKED_CLASSIFICATION_CORRECT`;
- blocker load-bearing: YES;
- teardown proved: YES;
- retry authorized by current packet: NO.

## Evidence

- full attempt receipt:
  `PDH3_R12_R6_PF4_ONLY_ATTEMPT_01_BLOCKED_RECEIPT_20260802_R1.md`;
- attempt receipt SHA-256:
  `64250201dea64e60d27372c44e71361624b3e29cf62bf691ade505932a6f7578`;
- raw local evidence root:
  `.pdh3-runtime/r12-preflight/r6-pf4-affinity-20260802-r1-run/`;
- terminal evidence SHA-256:
  `738b40cb1e1e6d7af8583cf64a4713962b176368206c27170cbbf95e767a9038`;
- capability evidence SHA-256:
  `c997d72a57f02cc1e03f6c86d1348c573e94431fd742880017ea7eb3fc51047d`;
- lifecycle evidence SHA-256:
  `18b483e37e7f575dba1cd198c8a22dffdc52bf5899977220e757f4c67e5303d2`.

## Resume boundary

Do not rerun this packet. The next safe step requires fresh operator authority
for a new provider-selection packet that demands at least 16 effective cgroup
CPUs after real accounting and selects hardware with CPU headroom. Preserve the
fixed minimum, all evidence, and this failed attempt unchanged. New dates,
costs, source bindings, and same-hash preflight are required.
