# PDH-3 Consecutive Failure Deep Audit

**Status:** `NO_GO_CURRENT_CANDIDATE`

**Audit UTC:** `2026-08-02T03:48:31Z`

**Strict evidence window:** approximately `2026-08-01T03:40:00Z` through `2026-08-02T03:40:00Z`

**Repository:** `/Users/kennethruedas/sandbox/cockroach-kernel-build-20260725`

**Audit branch / HEAD:** `evidence/external-validity-r1` / `5989e904f5d829ef5e7ae3597477699c8b98d92c`

**Frozen product candidate exercised by the campaigns:** `1c483b1930e629c9ecb6d73418b9554897dc08ad`

**Audit boundary:** read-only failure analysis and disposable local diagnostics. No product source was edited, no Pod was created, and no gate was self-approved. The unrelated untracked `heap_profiler/` directory was not touched.

## Executive verdict

The paid attempts did not repeatedly hit one mysterious provider failure. They advanced through three distinct bottleneck classes:

1. setup and vector-index lifecycle failures;
2. an invalid ANN proof and incomplete failure observability;
3. target-scale SQL read latency at concurrency 500.

The first two classes are now empirically closed on the tested worker class. R9, R10, and R11b each completed exact full-cardinality setup; R11b preserved the first decisive c500 failure receipt. The current failure is not a correctness, retry, vector-ingestion, replay, hot-counter, or teardown failure. It is a read-path tail-latency failure:

- `30,882` read operations in `120s`;
- zero execution errors;
- p99 `18,253.6ms` against `5,000ms`;
- maximum `36,507.2ms` against `10,000ms`.

Two mechanisms are simultaneously credible and must be isolated before another paid 24-hour launch:

- Five of the 27 read-mix queries filter one million receipts by `task_id`, while the migration declares no `receipts(task_id)` secondary index. A disposable CockroachDB v26.2.3 diagnostic reproduced a 100,000-row full scan and reduced optimizer cost from `122,531.23` to `135.19` after adding that index, approximately a `906x` cost reduction. This is the leading query-level cause, but target-scale `SHOW INDEXES` and `EXPLAIN ANALYZE` evidence was not captured before the Pod was deleted.
- The campaign sent 500 active clients through one SQL gateway while three Cockroach processes shared one 16-vCPU host. CockroachDB's published starting guidance is approximately `4 * vCPU` active SQL executions. The test was therefore about `7.8x` that starting point and used a GPU-oriented worker whose GPU did not help the SQL workload.

A separate confirmed launch blocker remains: the syscall trace reached `198,763,826` bytes in `2,113.93s`; its own receipt projects `8,322,585,615` bytes over 24 hours against the frozen `2 GiB` cap. Fixing SQL latency alone would not make the 24-hour campaign viable.

Blindly relaunching the current candidate would likely reproduce the failure and spend money without creating better evidence.

## Evidence authority

The decisive current artifacts are:

- `.pdh3-runtime/r8-campaigns/ck-pdh3-scale-r11b-relaunch-r1/retrieval/final-state.json`
  - SHA-256 `28134c924dc7376ced39b59079498c9a66141142eb78eeea86670242a3939361`
- `.pdh3-runtime/r8-campaigns/ck-pdh3-scale-r11b-relaunch-r1/retrieval/final-evidence.tgz`
  - SHA-256 `a6a92c3f1efa28af32460b0554d0861407e655bedb39fad4fd78dd05006ee118`
- `.pdh3-runtime/r8-campaigns/ck-pdh3-scale-r11b-relaunch-r1/retrieval/closeout.json`
  - SHA-256 `c3479b2a70ac0589bfea0cadf944ffc2aee087b2b65b655515a1bffd70f70c6d`
- archive member `evidence/preflight-failed-stage-0001.json`
  - receipt SHA-256 `3e9233d2973be8d29c0535e475f353af7b88b1d2626df744daa97ff7f3ba1e85`

All paid Pods in the audited chain were deleted, exact-ID lookup became absent, and campaign-scoped active inventory was empty. No measured 24-hour clock ever began.

## Strict trailing-24-hour chronology

| Campaign | Pod / UTC interval | Verified failure | What the evidence proves | Disposition |
|---|---|---|---|---|
| R6 `ck-pdh3-scale-r8-relaunch-r6` | `xnlp690a3j3xum`, `05:18:36-05:39:14` | Vector metadata failed after loss of quorum with nodes 1 and 3 down. | Full row counts completed. The artifacts do not prove why the processes died; OOM must not be asserted. | Later empty-index ingestion and recovery design prevented recurrence. Teardown GREEN. |
| R7 controller attempt | `6rbcu2lxia4p2m`, approximately `07:51` | Host controller falsely required an immediate detached PPID after `start_new_session`. | This was a controller defect; no upload or workload occurred. | Double-fork repair demonstrated correct detachment. Worker deleted. |
| R7 `ck-pdh3-scale-r8-relaunch-r7` | `81y4t6r6t9zmpz`, `07:56:49-10:17:36` | `SETUP_DEADLINE_RESERVE_EXHAUSTED:2400` during vector ingestion. | Immutable journal proves `58,250` vectors, not the `~43,250` stated in later repair prose. | Persistent clients, one-row transactions, distributed vectors, and bounded partitions solved the class. Teardown GREEN. |
| R8 `ck-pdh3-scale-r8-relaunch-r8` | `klu635c1c1js3g`, `11:30:41-12:32:53` | `FULL_CARDINALITY_SETUP_NOT_GREEN` because an ANN query returned 95,960 of 250,000 rows. | Exact base-table counts and reconciliation passed. ANN enumeration was an invalid completeness proof, not data loss. | Exact reconciliation plus deterministic recall probes solved the proof defect. Teardown GREEN. |
| R9 `ck-pdh3-scale-r9-relaunch-r1` | `qza6pmry5rnox4`, `17:04:51-17:48:47` | First c500 read mix returned `COMMAND_FAILED`. | Setup GREEN in `2,503.98s`; ANN mean recall `.975`. Exact command failure is unrecoverable because stdout/stderr were hashed then discarded. | Task-scoped trajectory query and exception-path preservation were added. Teardown GREEN. |
| R10 `ck-pdh3-scale-r10-relaunch-r1` | `r1t4eo532ipxku`, `19:09:41-19:45:05` | `CONCURRENCY_STAGE_BLOCKED:500`. | Setup GREEN in `1,925.739s`; ANN mean recall `1.0`. Completed-non-GREEN subchecks were not archived, so local hot-counter reproduction is not proof of the remote cause. | Sixteen counter shards and semantic-non-GREEN evidence preservation worked in R11b. Teardown GREEN. |
| R11 preflight | no Pod | AGY rejected ambiguous cost-envelope accounting. | This was a preflight wording/accounting defect, not runtime evidence. | Disjoint costs and setup margin were rebound; R11b received same-packet GLM/AGY GREEN. |
| R11b `ck-pdh3-scale-r11b-relaunch-r1` | `b0bqi7gp5ehyt9`, `22:56:00-23:31:13` | `CONCURRENCY_STAGE_BLOCKED:500:3e9233...` | Setup GREEN in `1,937.077s`; ANN mean recall `.9875`. Exact failure is read-mix latency only. | Current blocker. Teardown GREEN. |

### Immediate causal predecessors outside the strict window

- R3 exhausted setup reserve after full cardinality while restoring/proving the vector index.
- R4 lost its SQL connection during asynchronous `CREATE VECTOR INDEX` processing.
- R5 found the local SQL gateway refusing metadata connections after schema transition.
- R3 also had a preworkload worker deleted after a permitted worker shape was falsely rejected.

These are included only to explain the setup/index chain. They are not counted as strict-window attempts.

## What R11b proved

### Closed correctness properties

- exact setup counts: 500,000 tasks, 5,000,000 events, 1,000,000 receipts, 250,000 vectors;
- zero missing and zero mismatched rows;
- vector index queryable with mean recall `.9875`;
- 42,379 c500 operations with zero execution errors;
- acknowledged-write delta exact;
- 16-shard contended-update delta exact;
- replay idempotent;
- histograms account for operations;
- Pod evidence retrieved and hash-verified;
- Pod deletion and empty active inventory verified.

### Decisive workload split

| Workload | Operations | p99 | Maximum | Verdict |
|---|---:|---:|---:|---|
| Acknowledgment writes | 5,499 | 2.416s | 2.550s | PASS |
| Sixteen-shard contended updates | 2,999 | 4.832s | 5.100s | PASS |
| Replay | 2,999 | 1.409s | 1.476s | PASS |
| Read mix | 30,882 | 18.254s | 36.507s | **FAIL** |

The hot-counter repair worked. Another contention repair would target the wrong subsystem.

## Root-cause analysis

### RC-1 — likely unindexed receipt lookup at full cardinality

**Confidence:** high, but target-run plan proof is missing.

`post-dogfood/run_pdh3_local_canary.py::build_query_files` produces 27 read queries:

- 20 exact vector lookups;
- 5 receipt-view lookups by `task_id`;
- 1 stale projection lookup;
- 1 task-scoped trajectory join.

`p9-cloud/migrations/001_cloud.sql` defines `ck.receipts` with primary key `receipt_hash` and no explicit secondary index beginning with `task_id`. The view `ck.mcp_receipt_view` simply exposes the underlying column. A disposable v26.2.3 exact-shape diagnostic showed:

- foreign keys did not create a task-origin secondary index in `SHOW CREATE TABLE`;
- 100,000-row `task_id` filtering used a full scan with optimizer cost `122,531.23`;
- `CREATE INDEX receipts_task_id_idx ON ck.receipts(task_id) STORING(status,event_hash)` changed the plan to a constrained secondary-index scan with cost `135.19`.

Because 5/27 query definitions are receipt lookups, a uniform query picker would execute approximately `5,719` such lookups during 30,882 read operations. At one million receipts, that implies billions of row examinations in 120 seconds if the target plan also scans. This count is an inference; the current combined histogram and absent statement plans cannot prove the exact per-query distribution.

**Smallest correction:** capture target-scale `SHOW INDEXES`, named `EXPLAIN`, and `EXPLAIN ANALYZE (DISTSQL)` first. Add only the demonstrated index if the target plan scans. Bind the index and its completion to the migration and exact setup receipt.

### RC-2 — 500 active clients on one gateway and 16 shared vCPU

**Confidence:** high as a contributing mechanism.

The harness passes `nodes[0].sql_port` to every querybench process. The three database nodes are processes on one 16-vCPU host, not independent compute or failure domains. Querybench uses `--concurrency=500` and `--warmup-conns=0`.

CockroachDB advises starting at approximately four active SQL executions per vCPU and scaling or reducing workload when active executions exceed that level. On 16 vCPU, that is approximately 64 active executions; 500 is about `7.8x` higher. Zero query errors with extreme tail latency is consistent with queued or overloaded execution.

**Smallest correction:** define the claim before changing implementation:

- If 500 means logical producers, retain 500 producers, cap active database executions near a measured pool limit, and report queue time separately from SQL execution time.
- If 500 means simultaneously active SQL statements, select CPU/topology for that literal claim; approximately 125 total vCPU is the published-rule starting estimate, and gateways must be distributed.
- If the claim is one 16-vCPU host, keep c500 as a prospective saturation test rather than retroactively pretending it met the original SLO. Any threshold or claim change requires a fresh contract and cannot reclassify R11b.

Gateway balancing across `167/167/166` is a useful isolation test but does not create CPU capacity because the nodes share one host.

### RC-3 — opaque mixed-query evidence delayed diagnosis

**Confidence:** verified.

The read-mix histogram combines all 27 query definitions and does not preserve a query name. No target-scale `SHOW INDEXES`, per-query plan, per-query histogram, SQL fingerprint, admission-wait, active-session, or per-gateway metrics were captured. Resource snapshots are taken only after a GREEN stage. The real Cockroach store logs were not retrieved; preserved `node.log` files are startup-wrapper output.

R9 discarded command output and R10 discarded semantic-non-GREEN subchecks. R11b fixed the custody path but still cannot identify which read shape generated the tail.

**Smallest correction:** add diagnostic attribution without weakening the final mixed workload: named per-query-family canaries, failed-stage resource sampling, Cockroach logs, Prometheus SQL/admission metrics, and unchanged final mixed c500 verification.

### RC-4 — frozen trace ceiling would fail during a 24-hour run

**Confidence:** confirmed launch blocker; 24-hour projection remains an estimate.

R11b's network progress receipt recorded:

- elapsed `2,113.930489s`;
- trace bytes `198,763,826`;
- average `94,025.715143 B/s`;
- conservative 24-hour projection `8,322,585,615` bytes;
- frozen maximum `2,147,483,648` bytes;
- `projected_cap_exceeded=true`.

The sample includes setup activity, so it does not prove the measured-phase steady-state rate. It does prove that the present packet lacks evidence that a 24-hour run can remain under its own cap.

**Smallest correction:** run a frozen 15-minute representative measured-phase trace canary and require a safety-margined projection below 2 GiB. If the proof mechanism is changed, obtain new same-hash review; merely raising the cap hides the design problem.

### RC-5 — container disk observability is unreliable

**Confidence:** verified observability gap, not a proven latency cause.

Node logs repeatedly report `/proc/diskstats did not parse`. Containers and newer kernels expose varying diskstats formats and overlay filesystems may not map cleanly to a visible device. Use cgroup v2 `io.stat`, `findmnt`, `df`, and `du` as the container-scoped evidence path. Do not fabricate missing Cockroach counters or bind host `/proc` as a workaround.

## Evidence and custody defects

1. `PDH_3_VECTOR_INGEST_REPAIR_R8.md` says R7 reached approximately 43,250 vectors; the immutable journal proves 58,250.
2. The latest bundled `PDH3_ATTEMPT_HISTORY_MANIFEST.json` covers only original attempts 1-7 and does not bind replacement campaigns R3-R11b.
3. R9's exact command failure and R10's exact failed subcheck are unrecoverable. Later local reproductions are useful hypotheses, not replacements for remote evidence.
4. The R11b packet preserved the direct failure and should supersede speculative c500 narratives.

These defects do not erase the runtime results, but they prevent a clean final evidence chain until corrected append-only.

## Primary-source solution map

| Problem | Primary guidance | Required use here |
|---|---|---|
| Full scans on non-primary predicates | [CockroachDB performance best practices](https://www.cockroachlabs.com/docs/v26.2/performance-best-practices-overview), [index design](https://www.cockroachlabs.com/docs/stable/schema-design-indexes) | Add plan guards and only the query-supporting index proved necessary. |
| Stale optimizer knowledge after bulk load | [CREATE STATISTICS](https://www.cockroachlabs.com/docs/v26.2/create-statistics) | Create and verify statistics after full seed and before the c500 canary. |
| Query attribution | [EXPLAIN ANALYZE](https://www.cockroachlabs.com/docs/v26.2/explain-analyze) | Capture KV rows/bytes, full scans, contention, and distributed plan for each read class. |
| Excess active SQL concurrency | [Connection pooling](https://www.cockroachlabs.com/docs/v26.2/connection-pooling), [common issues](https://www.cockroachlabs.com/docs/stable/common-issues-to-monitor) | Define logical clients versus active statements; size pools/topology prospectively. |
| Single SQL gateway | [SQL layer](https://www.cockroachlabs.com/docs/v26.2/architecture/sql-layer) | Distribute a fixed aggregate 500 across gateways for isolation and final load if claim-compatible. |
| Runtime attribution | [Metrics](https://www.cockroachlabs.com/docs/v26.2/metrics), [Prometheus endpoint](https://www.cockroachlabs.com/docs/stable/prometheus-endpoint) | Sample connection, active-statement, latency, admission, CPU, memory, L0, and stall metrics. |
| Container I/O evidence | [Linux I/O statistics](https://cdn.kernel.org/doc/html/latest/admin-guide/iostats.html), [cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html) | Use format-aware host facts and cgroup `io.stat`; mark unavailable counters honestly. |
| Pod custody | [RunPod Pod management](https://docs.runpod.io/pods/manage-pods), [Pod creation API](https://docs.runpod.io/api-reference/pods/POST/pods) | Retrieve/hash before termination; bind exact ID/name/deadlines; prefer CPU-fit hardware for SQL. |

## Repair and validation sequence

### P0 — zero-cost diagnosis before product mutation

1. Freeze an append-only diagnostic amendment. Preserve the workload, full cardinality, c500 requirement, 120-second duration, and original 5s/10s thresholds.
2. Add a migration assertion listing every target index. Do not assume FK behavior.
3. At representative cardinality, capture named plans for all 27 read queries.
4. Fail on a full scan for point-read classes using `NO_FULL_SCAN` or an equivalent plan/row-read guard.
5. Generate post-seed statistics and prove completion.
6. Split diagnostics into vector, receipt, stale-projection, and trajectory families while retaining the unchanged final mixed workload.
7. Preserve query name, SQL fingerprint, gateway, SQLSTATE, attempts, timing, histogram, and plan hash.

### P1 — local full-cardinality canary

1. Run isolated read families at c10, c50, c100, c250, and c500.
2. Preserve the first concurrency where p99 diverges.
3. Run the unchanged 27-query mixed c500 stage three complete times.
4. Capture one-second process, file-descriptor, cgroup, SQL-session, admission, CPU, memory, and I/O samples on both GREEN and non-GREEN exits.
5. Retrieve actual Cockroach store logs.
6. Prove all failed `Future` results and subprocess outputs are consumed and retained.

### P2 — topology and observer isolation

1. Compare one gateway against deterministic `167/167/166` allocation without changing aggregate concurrency.
2. Prewarm the declared fixed pool; separately report connection establishment if connection-storm behavior is a claim.
3. Run the 15-minute representative trace-volume canary and project 24-hour size with safety margin.
4. A/B the observer only as a diagnostic. Never remove egress proof merely to obtain a pass.
5. Record `ulimit`, cgroup CPU/memory/PID/I/O state, database sessions/queries, admission waits, and per-process RSS/FDs.

### P3 — short remote proof before another 24-hour campaign

1. Select hardware mechanically from the meaning of 500, not from GPU prestige. The SQL workload receives no material benefit from L40S compute.
2. Preserve one worker and one campaign.
3. Seed full cardinality.
4. Run three c500 preflight epochs with named diagnostics and the unchanged final mixed gate.
5. Require the trace projection to remain within cap.
6. Retrieve and hash all evidence, then delete and verify absence.

Only a GREEN P3 permits freezing a new 24-hour packet. P3 is not the 24-hour campaign and must not be reported as one.

## Go / no-go checklist for a future 24-hour launch

- [ ] Exact target index inventory is captured and hash-bound.
- [ ] Every point-read query is proven not to full-scan at target cardinality.
- [ ] Post-seed optimizer statistics are fresh and receipt-bound.
- [ ] Per-query-family c500 evidence meets the original latency thresholds.
- [ ] The unchanged mixed c500 stage passes three complete epochs.
- [ ] The semantics of 500 logical producers versus 500 active SQL statements are explicit.
- [ ] CPU and topology match those semantics; a GPU label is not used as a proxy for SQL capacity.
- [ ] Aggregate connections are gateway-balanced or a single-gateway claim is explicitly proved.
- [ ] Prometheus, session, admission, CPU, memory, FD, cgroup, and real store-log evidence exists on failure and success.
- [ ] A representative trace canary projects below 2 GiB with safety margin.
- [ ] All raw stdout, stderr, histograms, plans, logs, and resource samples survive semantic non-GREEN and exceptions.
- [ ] R7's vector-count prose is corrected append-only to 58,250.
- [ ] The attempt-history manifest binds R3-R11b and their immutable failure hashes.
- [ ] The replacement packet receives independent same-hash review.
- [ ] Exact-ID lifecycle guard, provider deadlines, retrieval-before-delete, and empty-inventory verification remain unchanged.

Until every item is checked with direct evidence, the correct result is:

`PDH3_24H_RELAUNCH_BLOCKED`

## Seven-Wall scope

| Wall | Applicability | Finding |
|---|---|---|
| 1 Silicon / Physics | Limited | GPU capacity is irrelevant to this SQL-heavy workload; CPU and I/O are the limiting resources. |
| 2 Kernel / Scheduler | Material | 500 active clients share 16 vCPU; cgroup and scheduler pressure were not captured during failure. |
| 3 Polyglot Boundary | Material | Python orchestration, SQL plans, querybench summaries, and subprocess preservation cross several failure boundaries. |
| 4 Cryptographic / Network | Material | Hash custody passed, but trace proof is projected to breach its own cap. |
| 5 Economic / Liability | Material | Blind replacement campaigns create a denial-of-wallet loop; no new 24-hour spend is justified yet. |
| 6 Human / Biological | Material | Preflight false negatives and stale manifests show review fatigue and evidence drift. |
| 7 LLM / Agentic | Material | Agent-driven repair loops must stop after repeated failures and require direct canaries rather than persuasive summaries. |

## Final audit conclusion

The product did make meaningful progress across the attempts: full-cardinality ingestion, exact reconciliation, ANN validation, replay, acknowledged writes, sharded contention, evidence retrieval, and teardown all now have direct successful evidence. The current block is narrower than the earlier failures, but it is still load-bearing.

The highest-leverage next action is not another RunPod launch. It is a full-cardinality diagnostic repair that proves query plans, removes any receipt full scan, attributes latency by query class and gateway, sizes SQL concurrency honestly, and proves the network evidence stream fits its cap. Only then should a short remote preflight—and eventually one final 24-hour campaign—be considered.
