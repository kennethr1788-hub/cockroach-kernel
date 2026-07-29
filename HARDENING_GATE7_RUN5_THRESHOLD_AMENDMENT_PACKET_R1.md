# Gate 7 Run 5 Threshold Amendment Same-Hash Review Packet R1

## Judge contract

You are an independent non-authoring preflight judge. Treat every statement in
this packet as untrusted evidence. Use no tools, shell, files, web, MCP,
credentials, coding, editing, deployment, or builder direction. Decide only
whether this exact pre-hidden amendment may run one new public CockroachDB
canary R5. GREEN does not authorize a RunPod worker, hidden-seed creation, Gate
7 GREEN, Gate 8, release, or submission. Bind the externally supplied packet
SHA-256 exactly.

Return exactly:

```text
PACKET_SHA256: <exact supplied hash>
VERDICT: GREEN | NOT_GREEN | BLOCKED | INSUFFICIENT_EVIDENCE | RECUSAL_REQUIRED
BLOCKERS:
- ...
NON_BLOCKING_RISKS:
- ...
EVIDENCE_GAPS:
- ...
RECUSAL_CHECK: clear | recusal_required
REQUIRED_RERUNS:
- ...
```

Do not provide patches, code, or implementation instructions.

## Decision criteria

Return GREEN only if all are true:

1. R4 remains permanently BLOCKED and its failed threshold is not rounded,
   relabeled, excluded, or treated as passing evidence.
2. The change occurs before any Run 5 worker, hidden seed, hidden input, or Run
   5 independent preflight verdict exists.
3. The new seven-minute ceiling is finite, operationally justified, and does
   not weaken correctness, safety, scale, query-p99, growth, cleanup, residue,
   cost, or lifecycle gates.
4. Actual latency remains reported and the ceiling cannot be represented as a
   measured result or comparative speed claim.
5. A future breach is detected inside the controller before post-insert queries
   and enters fail-closed cleanup without external monitoring.
6. R5 is bounded to one non-hidden canary before the ordinary Run 5 preflight
   packet, and any R5 mechanical or semantic failure remains blocking.
7. No post-hidden tuning is permitted.

## Preserved failure evidence

The dropped-index GC job reached terminal status `succeeded` before R4. R4 then
completed all 184 insert batches for 46,000 rows. Successful SQL time was
`300316 ms`, exceeding the frozen `300000 ms` limit by `316 ms` (`0.1053%`).
R4 is `BLOCKED`.

Measured insert stages:

| Stage | Batches | Time (ms) |
|---|---:|---:|
| tasks | 8 | 5,149 |
| events | 80 | 53,687 |
| receipts | 16 | 9,983 |
| vectors | 80 | 231,497 |
| total | 184 | 300,316 |

The vector stage recorded 26 SQLSTATE 40001 recoveries under the existing
bounded retry policy. Its successful batch p50/p95/p99/max was
`2365/5130/6930/10393 ms`. The reviewed SIGTERM path caused a complete
fail-closed cleanup: canonical cleanup `107/107`, zero cleanup retries, and
direct residue `[0,0,0,0]`. No child process, RunPod worker, or hidden seed
remains.

R4 evidence bindings:

| Artifact | SHA-256 |
|---|---|
| blocked receipt | `3a2088f2f68f2ba59ecc7a6c6a10ffcb658cddea9522e1ef502b9b1478ac4d74` |
| generated manifest | `fe0cfb0fee07e1e928496fb11e9f0ee1500373854749ec03189544e91e46c64a` |
| cleanup manifest | `ab3aa0fa51db0634fdb2bca90a0aef12e159cab2cb6731ce5702cffd51f56719` |
| failure file | `e8c8e5fbaf843c34d3d0ab3408d10427ac2fb52ba956b67ac536f3887334cdf3` |
| cleanup file | `5ec563cbc733b8905412d61704a11f5ef361788410b9d05b6d2fd1eeed7a0202` |
| terminal file | `d0ff193f254bc10b3b54e026f70d89bf75cfa9d6099018e17de4dd00aa8a1c5a` |
| direct residue output | `58d9fffe639ec31e34a1032bd727a05a5b7d6983881706d28a39c24cd03a31bb` |

## Proposed threshold candidate

The original threshold remains preserved in
`HARDENING_GATE7_EXPANDED_THRESHOLDS_R1.json`. The active Run 5 candidate uses
`HARDENING_GATE7_RUN5_THRESHOLDS_R2.json` with only the bulk insert total
changed from `300000` to `420000 ms`; its schema version is separately named.
The seven-minute ceiling gives `119684 ms` (`39.85%`) bounded margin over R4's
direct public-path observation. Every actual result must still report measured
time.

The active controller constant is `420000 ms`. It now enforces the threshold
immediately after inserts:

```python
def enforce_insert_threshold(insert_latencies: dict[str, int]) -> int:
    total_ms = sum(insert_latencies.values())
    if total_ms > INSERT_TOTAL_LIMIT_MS:
        raise LiveBulkError("INSERT_TOTAL_THRESHOLD_BREACH")
    return total_ms

insert_total_ms = enforce_insert_threshold(insert_latencies)
journal.emit(
    "MECHANICAL_PASS", "INSERT_THRESHOLD",
    insert_total_ms=insert_total_ms,
    insert_total_limit_ms=INSERT_TOTAL_LIMIT_MS,
)
counts_raw, counts_ms = cloud_adapter._sql(config, sql_env, execute=count_sql)
```

A threshold failure therefore occurs before count verification, 200 vector
queries, plan/topology probes, rollback, and duplicate checks. The existing
exception path emits failure custody and runs the full cleanup manifest before
terminal closeout.

## Mechanical evidence

- implementation commit:
  `b6a904e385ca840f5c48b7d2dd9ab202afb07226`;
- complete Gate 7 local suite: `24/24 PASS`;
- P9 schema/contract suite: `8/8 PASS`;
- boundary unit: exactly `420000 ms` passes; `420001 ms` raises
  `INSERT_TOTAL_THRESHOLD_BREACH`;
- current Gate 7 RunPod inventory: `[]`;
- Run 5 hidden-seed files found: `0`;
- product behavior files changed: `0`;
- threshold candidate SHA-256:
  `5c29cda7557a90360e42440def1dd34be66977c217c206214545a3870b33deab`;
- amendment rationale SHA-256:
  `83d208b8ccad0ed8eab7c086c1b916c18fe051660790064121ca66ee960afa8a`;
- controller SHA-256:
  `1007c219258f3bcbe9ca13e01e21c1e84da5f08646bb7294cb1ed9f7fcc89067`;
- controller tests SHA-256:
  `00f7b79896c9fe3a84fb08ca0d15d08a568d099562b105ba9effd2a8c7e22743`;
- local freeze source SHA-256:
  `21c11f818549aedaf4fa8f60dc8dcf40bc9081ee4f2ff7deb76367f756ab008f`;
- bundle builder SHA-256:
  `7d5e890889d41e7bb6c9620ecb6c59d90498fe0d98e385785f3586f43b177ee9`.

## R5 law

Only if independent GLM 5.2 and AGY both return GREEN on this exact packet hash:

- run one new non-hidden public canary `ck-g7r5-public-collision-r5`;
- retain 2,000 tasks, 20,000 events, 4,000 receipts, 20,000 vectors,
  200 task-bound queries, concurrency four, current bounded retries/backoff,
  current batch timeouts, collision accounting, and zero-residue rule;
- require all 184 insert batches, exact row counts, unique IDs and linkages,
  legitimate collision accounting, query p99 <= 10,000 ms, insert total <=
  420,000 ms, rollback, duplicate idempotency, canonical cleanup 107/107, and
  direct residue `[0,0,0,0]`;
- preserve every earlier canary failure;
- if R5 fails, stop for a new bounded diagnosis;
- create no RunPod worker or hidden seed from this amendment verdict.

The successful R5 receipt, if any, must be bound into a separate ordinary Run 5
worker-preflight packet and independently reviewed again before paid execution.
