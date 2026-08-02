# PDH-3 R12 R6 PF-4-only result review packet R1

Status: `FROZEN_FOR_INDEPENDENT_FAILURE_CLASSIFICATION`

UTC frozen: `2026-08-02T10:09:00Z`

Decision requested: independently determine whether attempt 01 was correctly
classified as blocked, whether the blocker is load-bearing, whether teardown
is adequately proved, and whether any retry is authorized by the evidence.

## Exact result

- attempted gate: PF-4 only;
- frozen launch packet SHA-256:
  `723d95c459c2ef85ba29486a39c052dd36d69a1ba14976cdc6dabe71ba4367d3`;
- Pod ID: `7g0k4sfm35r1gh`;
- provider readback: 16 vCPU / 188 GiB / L40S / `$0.99/hour`;
- real affinity set/readback: exact 16-CPU mask, GREEN;
- real cgroup v1 CPU quota: 13 CPUs;
- effective runtime CPUs: 13;
- fixed minimum: 16;
- capability verdict: false because `checks.cpu` is false;
- every other PF-4 capability check: true;
- main bundle uploaded: false;
- measured 24-hour clock started: false;
- worker deleted: true;
- exact-ID absent: true;
- campaign active inventory: `[]`;
- lifecycle terminal event: `TEARDOWN_GREEN`.

## Exact evidence

- blocked receipt:
  `PDH3_R12_R6_PF4_ONLY_ATTEMPT_01_BLOCKED_RECEIPT_20260802_R1.md`;
- blocked receipt SHA-256:
  `64250201dea64e60d27372c44e71361624b3e29cf62bf691ade505932a6f7578`;
- terminal file SHA-256:
  `738b40cb1e1e6d7af8583cf64a4713962b176368206c27170cbbf95e767a9038`;
- capability file SHA-256:
  `c997d72a57f02cc1e03f6c86d1348c573e94431fd742880017ea7eb3fc51047d`;
- lifecycle chain SHA-256:
  `18b483e37e7f575dba1cd198c8a22dffdc52bf5899977220e757f4c67e5303d2`;
- lifecycle terminal event hash:
  `a273ba6120aec3a6e850a82fa43e93b9ce3444d65a23b7e14329a6305101f665`;
- terminal embedded receipt hash: locally recomputed and matched;
- capability embedded receipt hash: locally recomputed and matched;
- current provider Pod inventory: `[]`.

## Classification proposed by the builder

`PF4_ONLY_BLOCKED: EFFECTIVE_CGROUP_CPU_BELOW_MINIMUM`

The advertised 16-vCPU label and exact 16-CPU scheduling mask do not override a
13-CPU cgroup quota. The current fixed contract correctly takes the minimum of
provider and container constraints. Weakening the minimum or ignoring cgroup
accounting would manufacture a pass.

No retry is authorized by the completed one-attempt packet. A future retry
would need new operator authority, a fresh provider-selection packet requiring
at least 16 effective cgroup CPUs, current price/deadline/cost bindings, and a
new same-hash preflight. The worker shape should have CPU headroom; no specific
unverified replacement shape is asserted as sufficient.

## Judge boundary and required response

GLM 5.2 receives this exact sanitized packet as a non-authoring judge. It has
no shell, filesystem write, repository, browser, credential, provider,
implementation, retry, or approval authority.

Return exactly:

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: <exact packet SHA-256>
VERDICT: BLOCKED_CLASSIFICATION_CORRECT|CLASSIFICATION_INCORRECT|JUDGE_UNAVAILABLE
BLOCKER_LOAD_BEARING: YES|NO
TEARDOWN_PROVED: YES|NO
RETRY_AUTHORIZED_BY_CURRENT_PACKET: YES|NO
FINDINGS:
- <finding or none>
```
