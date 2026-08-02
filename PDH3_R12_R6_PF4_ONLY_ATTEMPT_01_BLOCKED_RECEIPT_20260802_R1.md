# PDH-3 R12 R6 PF-4-only attempt 01 blocked receipt R1

Status: `PF4_ONLY_BLOCKED`

Blocker: `EFFECTIVE_CGROUP_CPU_BELOW_MINIMUM`

UTC worker ready: `2026-08-02T10:05:31Z`

UTC teardown green: `2026-08-02T10:06:22Z`

## Authority and frozen candidate

- authorization receipt SHA-256:
  `c55b77a8392082321e6d0b08a48085b5ff8e8be66775cb5a9e4dfbadd69c437b`;
- frozen lifecycle packet SHA-256:
  `723d95c459c2ef85ba29486a39c052dd36d69a1ba14976cdc6dabe71ba4367d3`;
- same-hash GLM preflight: GREEN;
- PF-4-only implementation commit:
  `7219df502461e1bce06ad9707be1fb44294632c2`;
- lifecycle packet commit:
  `7dffd6013e59f366c37f1e694df09ff658f4a95c`;
- GLM receipt commit:
  `02ed5561d903e1673fd627bb342779ec920366a1`;
- host configuration SHA-256:
  `db34c21f0c54f772d4c7553f1c512cf5b1e090add595aaf958f3c805e55fbca5`.

## Provider and worker identity

- campaign: `ck-pdh3-r12-preflight-r6-pf4-aff-r1`;
- Pod ID: `7g0k4sfm35r1gh`;
- Pod name: `ck-pdh3-r12-preflight-r6-pf4-aff-r1-01`;
- provider-returned shape: 16 vCPU / 188 GiB RAM / one L40S;
- compute price: `$0.99/hour`;
- container disk: 250 GB disposable;
- persistent/network volume: zero;
- worker state before PF-4: `PF4_WORKER_READY_PREUPLOAD`;
- main bundle uploaded: false;
- measured 24-hour clock started: false.

## Direct PF-4 result

The real Linux affinity operation passed:

- pre-apply scheduling mask: 128 CPUs;
- deterministic target: CPUs 0 through 15;
- post-apply readback: exactly CPUs 0 through 15;
- affinity exactness: GREEN;
- affinity plan SHA-256:
  `fea066c0793ff75fc9c502750740ad58558901655a4a27e16c33a394434a1897`.

The real container CPU accounting failed the fixed minimum:

- provider allocation: 16 vCPUs;
- scheduling-affinity limit: 16 CPUs;
- cgroup v1 CPU quota: 13 CPUs;
- effective runtime CPU count: 13;
- frozen minimum: 16;
- `checks.cpu`: false;
- overall PF-4 receipt: false.

All other capability checks passed: RAM, disk total and availability, disk
used fraction, sequential and sustained I/O, fsync latency, random-sync IOPS,
resource-accounting availability, process-tree access, monotonic clock,
streaming network observer, residue cleanup, and affinity exactness.

The controlling implementation computes effective CPU as the minimum of the
provider allocation and cgroup constraints. The observed cgroup quota is
therefore a genuine fail-closed resource result. It cannot be converted to
GREEN by the advertised 16-vCPU label or by the successful 16-CPU affinity
mask.

## Evidence bindings

Runtime root:
`.pdh3-runtime/r12-preflight/r6-pf4-affinity-20260802-r1-run/`

| Evidence | SHA-256 |
|---|---|
| `PF4_ONLY_TERMINAL.json` | `738b40cb1e1e6d7af8583cf64a4713962b176368206c27170cbbf95e767a9038` |
| `PF4_CAPABILITY_RECEIPT.json` | `c997d72a57f02cc1e03f6c86d1348c573e94431fd742880017ea7eb3fc51047d` |
| `PF4_FAILURE_RECEIPT.json` | `c997d72a57f02cc1e03f6c86d1348c573e94431fd742880017ea7eb3fc51047d` |
| `running-worker-receipt.json` | `0517a6ca5d797d9a84b5f0810a6fabf2946da3fdbedce07cf7ae52e37bf2066d` |
| `attempt-ledger.json` | `7f05a55ed7033a9e509bdb6f5de2f2bb5eb151a373b998aa63153e7e240e12c3` |
| `attempt-01/lifecycle.ndjson` | `18b483e37e7f575dba1cd198c8a22dffdc52bf5899977220e757f4c67e5303d2` |
| `attempt-01/pod-get.json` | `3c15ec36b12727c0d3193173d96e47c0c02d186dbbb61a94121476ff38c5ff77` |
| `pf4-only-capability.stderr` | `4480b26554e8b005949adec49f2102a59dda38c1a92abe52a93ed328bb6059e3` |
| `pf4-delete.stdout` | `92d168238499bd385871da679e5b9b6379bed800feccf261f42f9857277e6c2e` |
| `pf4-post-delete-inventory.json` | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |

The terminal and capability receipts were independently canonicalized locally;
their embedded receipt hashes matched exactly.

## Teardown and spend state

- provider deletion command: successful;
- exact Pod lookup: 404 / absent;
- campaign-scoped active inventory: `[]`;
- lifecycle chain: four valid hash-linked records;
- terminal lifecycle event: `TEARDOWN_GREEN`;
- terminal event hash:
  `a273ba6120aec3a6e850a82fa43e93b9ce3444d65a23b7e14329a6305101f665`;
- active campaign process: none;
- current RunPod Pod inventory: `[]`.

The account balance observed before and after the attempt changed by
`$0.0019444444`. This is recorded only as a balance delta, not asserted as an
exact isolated charge because provider settlement timing is not proven.

## Controlling conclusion

The attempt is preserved as valid negative provider evidence. It does not
authorize a retry and cannot advance PF-4 or R6.

The next safe action, if separately authorized, is a fresh provider-selection
packet that requires at least 16 effective CPUs after real cgroup accounting
and uses a worker class with CPU headroom. The fixed minimum must not be
weakened. New dates, costs, payload bindings, and same-hash independent
preflight are required before any replacement worker.
