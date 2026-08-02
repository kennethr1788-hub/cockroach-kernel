# PDH-3 R12 Extensive Preflight Plan

Status: `PREFLIGHT_PLAN_FROZEN_FOR_INDEPENDENT_REVIEW__NO_RUNPOD_LAUNCH`

Plan revision: `R1`

Date: `2026-08-02`

Builder/author: `Codex / Icarus`

Independent judge: `GLM direct judge route, non-authoring, sanitized packet, no tools`

## 1. Decision and boundary

This plan is the mandatory pre-launch gate for one possible replacement PDH-3
24-hour campaign. It is not permission to create, start, stop, or delete a
RunPod worker. It does not mark any campaign gate GREEN.

The preflight exists to answer one question:

> Can the unchanged full-cardinality workload begin a 24-hour measured clock on
> one mechanically selected worker without a known query-plan failure, evidence
> overflow, evidence-loss path, resource-sizing contradiction, or ambiguous
> terminal state?

The current answer is `NO_GO`. It may become `GO_FOR_SEPARATELY_AUTHORIZED_24H_RUN`
only after every stage in section 8 is directly GREEN and the final evidence
packet receives an independent same-hash GREEN review.

This revision authorizes planning and independent review only. It does not
authorize:

- product-candidate mutation;
- RunPod creation or provider spend;
- a 24-hour campaign;
- persistent or network volumes;
- AWS, CockroachDB Cloud, GitHub, or package-registry credentials;
- HOME, Qdrant, StateV2, launchd, client data, or production data;
- changed claims, thresholds, workload cardinality, or hidden-result tuning.

## 2. Bound authority and source evidence

### 2.1 Repository authority

- Branch: `evidence/external-validity-r1`
- Current repository HEAD: `5989e904f5d829ef5e7ae3597477699c8b98d92c`
- Frozen product candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- Frozen production-plan SHA-256:
  `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`

### 2.2 New audit evidence

- `PDH_3_CONSECUTIVE_FAILURE_DEEP_AUDIT_20260802.md`
  - SHA-256:
    `eba662ae0349b0a68cd4452186c7665f0e17fcff7e71bcb77d9c030415a8cdc9`
- `PDH3_PROVIDER_DOCUMENTATION_COMPLIANCE_AUDIT_20260802.md`
  - SHA-256:
    `5e2e0f88373fe75ab1199409f54310b8d997a26dc8f373c4d361acfe3483235f`
- RunPod documentation index snapshot:
  `0d224b84794cdc5fd9e449cee3981678225a716ea2db6635cca237c20dfe790b`
- CockroachDB v26.2 documentation index snapshot:
  `789bda063cee5654b1e61dc02ee761fb843103accd734096d8fe23cafc0d3fc6`

### 2.3 Tool and runtime provenance

- CockroachDB Linux v26.2.3 binary SHA-256:
  `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`
- RunPod CLI version: `2.7.2-309512b`
- RunPod CLI SHA-256:
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`

All runtime, image, price, inventory, and account-capacity facts remain
`LIVE_PREFLIGHT_REQUIRED`; historical availability is not current proof.

## 3. Verified facts, assumptions, and prohibited inferences

### 3.1 Verified facts

1. R11b completed exact setup at 500,000 tasks, 5,000,000 trajectory events,
   1,000,000 receipts, and 250,000 vectors in 1,937 seconds.
2. R11b reconciled exact seeded contents and achieved ANN mean recall `0.9875`.
3. Its first c500 stage completed 42,379 operations with zero execution errors.
4. Acknowledgement, 16-shard update, and replay families passed their gates.
5. The combined read mix failed: p99 `18,253.6 ms` and maximum
   `36,507.2 ms`, against unchanged limits of `5,000 ms` and `10,000 ms`.
6. Five of 27 read definitions filter `ck.receipts.task_id`; the production
   migration has no secondary index led by `task_id`.
7. A disposable 100,000-row CockroachDB v26.2.3 reproduction changed the
   receipts predicate from a full scan with optimizer cost `122,531.23` to a
   constrained covering secondary-index scan with cost `135.19` after adding
   `receipts(task_id) STORING(status,event_hash)`.
8. This local plan result is strong diagnostic evidence but is not target-scale
   proof.
9. R11b produced 198,763,826 trace bytes in 2,113.93 seconds; its own linear
   projection was about 8.32 GB over 24 hours, above the frozen 2 GiB cap.
10. The current c500 implementation creates 500 concurrent querybench workers,
    targets one SQL gateway, and uses `--warmup-conns=0`.
11. The current three CockroachDB processes share one worker and one physical
    failure domain.
12. The current no-volume design keeps its only remote evidence copy on
    disposable container storage until retrieval.
13. No measured 24-hour clock has begun. Prior workers were deleted and their
    failures are preserved.
14. Deterministic `ON CONFLICT DO NOTHING` retry inserts are followed by exact
    row-count and field/content reconciliation, so a conflict cannot silently
    authorize success when stored contents differ.

### 3.2 Assumptions that preflight must resolve

1. The five target-scale receipt predicates still full-scan without the
   candidate index.
2. The stale-projection `source_key` predicate may full-scan because the current
   unique index is led by `source_table`.
3. The candidate receipt index is sufficient to bring every isolated read
   family and the unchanged mixed c500 workload under the original limits.
4. The selected worker supports the proposed low-volume egress mechanism with
   the required namespace, cgroup, firewall, or eBPF capabilities.
5. Off-Pod incremental evidence retrieval can survive a remote process loss
   without delaying or corrupting the measured workload.
6. The exact offered CPU/RAM/disk pair is sufficient for three CockroachDB
   processes plus querybench, controller, telemetry, logging, and OS reserve.
7. Single-gateway concentration, not only the missing index, may contribute to
   tail latency.
8. A short full-cardinality canary can predict plan selection, latency, and
   evidence slope; it cannot prove 24-hour stationarity by itself.

### 3.3 Prohibited inferences

- A local plan is not proof of the target-scale remote plan.
- A GPU model name is not evidence of SQL suitability.
- Three processes on one host are not independent nodes or production HA.
- cgroup byte counters alone do not prove destination allow-list conformance.
- a successful command is not a successful semantic gate;
- setup GREEN is not campaign GREEN;
- a missing result is not a failed result with known cause and is never GREEN;
- evidence retrieved after failure may diagnose the failure but may not
  retroactively pass the run;
- a reduced-cardinality result may not authorize a target-cardinality plan,
  storage, concurrency, or growth claim.

## 4. Invariants that may not be weakened

The following remain unchanged unless Kenneth separately authorizes a
prospective contract amendment and a new independent review:

- 500,000 tasks;
- 5,000,000 trajectory events;
- 1,000,000 receipts;
- 250,000 task-bound vectors;
- 9,976 verifier executions in the final campaign;
- 288 five-minute checkpoints in the final campaign;
- 24 scheduled same-host process kill/restart/reconciliation cycles;
- literal c500 means 500 querybench workers, not 500 logical producers hidden
  behind a smaller pool;
- 120-second query stages;
- p99 no greater than `5,000 ms`;
- maximum latency no greater than `10,000 ms`;
- zero execution errors;
- zero false promotions, cross-task vector links, acknowledged-write loss,
  accepted replays, and undeclared external egress destinations;
- trace/evidence network-proof ceiling: 2 GiB;
- database ceiling: 100 GiB;
- total evidence ceiling: 20 GiB;
- disk-used fraction: no more than 70 percent;
- exactly three live CockroachDB processes during non-fault intervals;
- one paid worker at a time;
- retrieval and hash verification before worker deletion;
- no replacement after workload upload or measured execution begins;
- prior failed evidence remains append-only and unmodified.

## 5. Prospective correction envelope

The preflight may evaluate only these bounded corrections. None is authorized by
this planning artifact alone.

### 5.1 Conditional receipt index

Candidate DDL:

```sql
CREATE INDEX receipts_task_id_idx
ON ck.receipts (task_id)
STORING (status, event_hash);
```

It may be proposed for the candidate only after current-plan evidence is frozen.
After creation, the schema job must finish successfully, suitable statistics
must be current, and identical read-only queries must be re-run. The candidate
is rejected if the filtered predicate still full-scans, reconciliation changes,
or write/replay semantics regress.

### 5.2 Conditional stale-projection index

No projection index is preselected. First capture the exact target plan and rows
read for the `source_key` predicate. Add the smallest leading index only if the
target plan and isolated latency demonstrate material full-scan cost. This
decision must be frozen before the final hidden mixed canary.

### 5.3 Diagnostic attribution

Add named diagnostic families without changing the final mixed query set:

- `vector_exact`;
- `receipt_view`;
- `stale_projection`;
- `trajectory_join`;
- `ack_write`;
- `contended_update`;
- `replay`.

Each observation must bind query name, SQL fingerprint, gateway, SQLSTATE,
attempts, operations, errors, duration, p50/p90/p99/max, plan hash, and resource
window hash. The final gate remains the unchanged aggregate mixed workload.

### 5.4 Gateway diagnostic

Compare the literal 500-worker load through:

- one gateway; and
- deterministic `167/167/166` gateway allocation.

Aggregate concurrency remains 500. Connection establishment is reported
separately from steady-state latency. This is a diagnostic, not permission to
redefine c500 or retroactively alter R11b.

### 5.5 Low-volume network proof

Replace the oversized full syscall trace only after a capability canary proves a
mechanism that:

- starts before the observed process tree;
- follows all descendants;
- enforces or independently binds allowed destinations;
- records destination class, bytes, packets, denials, observer liveness, and
  loss/drop counters;
- fails closed on observer loss or counter discontinuity;
- emits canonical hash-chained summaries every 30 to 60 seconds;
- retains bounded raw audit samples;
- projects no more than 1 GiB over 24 hours, leaving a two-times margin below
  the 2 GiB ceiling.

Full packet payload capture is not required. Destination proof cannot consist
only of aggregate cgroup byte counts. Any residual blind spot must be named and
must not contradict the public claim.

### 5.6 Interruption-survivable evidence

Preserve the existing zero-volume boundary. During remote canaries, pull
canonical checkpoint manifests and the raw files they bind to the local
supervisor incrementally. Each transfer must include remote hash, local hash,
monotonic sequence, previous-manifest hash, and acknowledgement time.

The recovery canary must:

1. complete and export a checkpoint;
2. verify its local independent copy;
3. kill the remote campaign process, not the worker;
4. prove the exported checkpoint remains valid without further remote access;
5. prove partial/newer files cannot be mistaken for a complete checkpoint;
6. resume only the preflight canary if the frozen protocol permits it;
7. preserve the interruption as evidence.

No Pod interruption can be honestly survived without a durable provider volume
or an already verified off-Pod copy. This plan chooses the off-Pod copy.

### 5.7 Provider-native observability

Collect continuously from all three CockroachDB processes:

- `/metrics` or `/_status/vars` data required for SQL service latency,
  admission, CPU, RSS, node liveness, and storage health;
- active SQL sessions/statements, connection counts, query fingerprints, and
  gateway distribution;
- admission wait and overload indicators;
- process CPU/RSS/FD/PID and complete process-tree state;
- cgroup CPU, memory, PIDs, and I/O;
- store bytes, capacity, read/write throughput, IOPS, queue/service time,
  Pebble/LSM L0 and stall/read-amplification signals;
- bounded real CockroachDB `OPS`, `HEALTH`, `STORAGE`, and SQL performance logs;
- observer health, dropped samples, and collection overhead.

Use one-second sampling for active sessions, admission, latency, and query
fingerprints during canaries; use five-second sampling for cgroup, process,
store, and node metrics. A canary must A/B observer on/off and reject overhead
greater than 10 percent in p99 under an otherwise identical frozen workload.
Admission control and logging may not be disabled to manufacture a pass.

## 6. Hardware and cost selection gate

Before any paid creation request, read current RunPod inventory and price from
the authenticated provider surface. Select mechanically; do not hardcode L40S
for prestige.

The candidate worker must satisfy all of the following:

1. Secure Cloud and the independently reviewed image.
2. Exact CPU/RAM pair recorded, with at least 4 GiB RAM per observed vCPU.
3. Three processes each configured at 8 GiB cache and 8 GiB SQL memory fit the
   documented aggregate memory formula with explicit reserve for querybench,
   Python, observers, logs, kernel, and OS page cache.
4. Disk can hold bounded stores, evidence, logs, and transfer staging below both
   250 GB and 70 percent used.
5. A pre-upload disk benchmark passes frozen minimum throughput, random IOPS,
   fsync latency, and sustained-write criteria derived from the measured R11b
   setup and projected campaign growth. Threshold values must be frozen before
   live inventory is seen.
6. CPU and disk throttling status are observable.
7. GPU is optional and unused; it has no evidentiary value for this SQL test.
8. Live compute rate, storage rate, maximum paid lifetime, aggregate prior spend,
   account credit, retrieval reserve, and teardown reserve fit the current
   owner-authorized cost envelope.
9. Provider-native stop and terminate deadlines are included in the creation
   request; exact-ID local lifecycle guard remains active.
10. One-worker-at-a-time inventory is verified immediately before creation.

If exact price, credit sufficiency, returned hardware, deadline inclusion,
worker identity, storage configuration, or deletion guarantee is unknown, stop
with `PREFLIGHT_BLOCKED__RUNPOD_LIFECYCLE_OR_COST`.

## 7. Evidence model and terminal-state law

### 7.1 Canonical receipt fields

Every stage receipt must contain:

- schema version;
- stage ID and attempt ID;
- candidate commit and source-manifest SHA-256;
- plan SHA-256 and active packet SHA-256;
- worker ID and hardware only when remote;
- UTC start/end and monotonic duration;
- exact commands or canonical command hashes;
- input, output, stdout, stderr, plan, histogram, telemetry, and log hashes;
- expected and observed counts;
- thresholds and measured values;
- observer health and missing-sample counts;
- prior receipt hash;
- semantic result: `GREEN`, `BLOCKED`, `FAILED`, or `INVALID`;
- stable reason codes;
- teardown and residue state where applicable;
- canonical receipt SHA-256.

### 7.2 Terminal states

- `GREEN`: command and every semantic assertion passed with complete evidence.
- `FAILED`: execution completed and direct evidence proves an acceptance failure.
- `BLOCKED`: a required prerequisite, authority, capability, cost, or evidence
  property could not be established.
- `INVALID`: protocol drift, mixed hashes, missing required evidence, observer
  loss, hidden-result tuning, unsafe state, or contamination makes the result
  non-evaluable.

Absent result, partial archive, transport failure, supervisor loss, hash
mismatch, or ambiguous exit can never be mapped to `GREEN`. The supervisor must
implement these as mutually exclusive terminal branches and test each branch.

### 7.3 Append-only failure custody

The attempt-history manifest must bind every prior PDH-3 attempt from R3 through
R11b and preserve:

- worker ID;
- start/end UTC;
- failure class;
- raw evidence paths and hashes;
- teardown and inventory evidence;
- known missing evidence;
- corrected append-only disclosures, including the R7 vector-count correction
  to `58,250` and the unrecoverable R9/R10 remote-output gaps.

No historical artifact is overwritten or relabeled.

## 8. Extensive preflight execution ladder

Stages are sequential. A stage may begin only from a frozen input manifest and
the immediately prior GREEN receipt. A non-GREEN result stops the ladder.

### PF-0 — contract and custody freeze (local, zero cost)

Inputs:

- the two audits in section 2;
- current candidate source;
- current contract and all R3-R11b lifecycle receipts;
- official source snapshot hashes.

Actions:

1. Create an append-only failure-history manifest.
2. Freeze the unchanged workload and thresholds from section 4.
3. Freeze correction scope from section 5.
4. Freeze all test SQL, workload files, schemas, validators, observers,
   supervisor branches, evidence schemas, and teardown commands.
5. Scan the transfer candidate for secrets, credentials, absolute private paths,
   symlinks, sockets, devices, caches, archives, and unrelated data.
6. Prove the candidate has no AWS, CockroachDB Cloud, GitHub, package-registry,
   HOME, Qdrant, StateV2, launchd, client, or production dependency.

Pass:

- all hashes agree;
- every prior attempt is present or explicitly disclosed as missing;
- frozen workload/threshold comparison matches section 4;
- secret/private-path scan is clean;
- packet is deterministic across two builds.

Kill:

- mixed candidate or plan hashes;
- silent threshold/workload change;
- missing prior failure custody;
- private or secret material.

### PF-1 — implementation and supervisor proof (local, zero cost)

Actions:

1. Run unit tests for canonical receipts, hash chains, growth projections, named
   histograms, plan parsing, missing-sample detection, and cost arithmetic.
2. Run all supervisor terminal branches: GREEN, semantic failure, absent result,
   partial archive, corrupt archive, transport failure, observer loss, deadline,
   and teardown failure.
3. Prove every child future is drained, every subprocess has a bounded timeout,
   timeout is normalized to a stable terminal state, and no child/process leak
   remains.
4. Re-run seed timeout/idempotency tests and exact field/content reconciliation.
5. Prove the measured clock cannot start until all explicit start predicates are
   simultaneously true.

Pass:

- complete test matrix GREEN;
- zero ambiguous terminal mappings;
- zero resource residue;
- deterministic receipts across five identical inputs.

Kill:

- any partial or absent result maps to success;
- any SQL operation can exceed the remaining bounded setup deadline without
  cancellation and reconciliation;
- any lost stdout/stderr or undrained future on failure.

### PF-2 — schema and plan A/B (local, zero cost)

Actions:

1. Build fresh representative datasets at 10,000, 50,000, and 100,000 tasks.
2. Freeze current `SHOW INDEXES`, `SHOW STATISTICS`, `EXPLAIN`, and read-only
   `EXPLAIN ANALYZE (DISTSQL)` evidence for every point-read query.
3. Apply only the candidate receipt index after current-plan evidence is frozen.
4. Wait for schema job completion and refresh/prove statistics.
5. Repeat byte-identical queries and record plan, rows read, latency, and result
   hashes.
6. Diagnose the stale-projection predicate and conditionally choose the smallest
   index before later hidden mixed canaries.
7. Run exact content/count reconciliation and all write/replay regressions.

Pass:

- no point-read family full-scans after the selected correction;
- identical query results before/after;
- receipt-view indexed plan is constrained and covering or an independently
  justified smaller correct plan;
- schema/statistics jobs complete;
- zero correctness or write regression.

Kill:

- target predicate still full-scans;
- plan parser cannot distinguish full versus constrained scans;
- row/result hash changes;
- unreviewed DDL is required.

### PF-3 — local full-cardinality predictive canary (local, zero provider cost)

Run only if the host can satisfy explicit disk, memory, and process fuses without
touching HOME runtime or live services. Otherwise mark
`PREFLIGHT_BLOCKED__LOCAL_FULL_CARDINALITY_RESOURCE_BOUNDARY` and move neither
the dataset nor the conclusion to a weaker scale.

Actions:

1. Seed exact full cardinality in a generated sandbox root.
2. Reconcile every table and vector probe.
3. Capture target-scale index/statistics/plans.
4. Run named query families at c10, c50, c100, c250, and c500.
5. Preserve the first divergence point.
6. Run the unchanged mixed c500 stage three complete 120-second epochs.
7. Capture one-second SQL/admission metrics and five-second system/store metrics
   before, during, and after each epoch.
8. Tear down and verify no residue.

Pass:

- exact cardinality and reconciliation;
- all named families and all three unchanged mixed epochs meet 5s/10s limits;
- zero execution errors;
- no observer gaps, leaks, or threshold breach;
- all raw failure outputs would have been preserved if non-GREEN.

Kill:

- host memory/disk pressure approaches a frozen fuse;
- any live/Home service is touched;
- any named or mixed latency gate fails;
- resource or evidence slope is non-linear without explanation.

### PF-4 — remote capability and lifecycle canary (paid, separately authorized)

This is the first stage that can create a worker. It requires fresh owner
authorization naming the live cost envelope and permitted creation retries.

Before upload:

1. Enumerate live CPU and GPU offers and freeze the selection proof.
2. Verify exact worker identity, price, CPU, RAM, disk, image, ports, zero
   volumes, deadlines, and one-worker inventory.
3. Benchmark disk throughput, random IOPS, fsync latency, and sustained writes.
4. Smoke network namespace/cgroup/firewall/eBPF capabilities needed by the
   selected observer.
5. Smoke metrics/log endpoints, cgroup files, clock monotonicity, fsync,
   process-tree tracking, and incremental off-Pod retrieval.
6. Start the detached exact-ID lifecycle guard and prove its heartbeat.

Pass:

- every property matches the frozen packet;
- selected observer enforces or proves its declared boundary;
- disk and resource criteria pass;
- provider deadlines and local guard are active;
- first off-Pod checkpoint round-trip hash matches.

Kill:

- capability or hardware mismatch;
- price or account-credit uncertainty;
- undeclared egress;
- inability to retrieve while worker remains running;
- inability to guarantee teardown.

On any exit, retrieve available evidence, delete the worker, prove exact-ID
absence and empty campaign inventory, and reconcile known cost.

### PF-5 — remote full-cardinality setup and target plan (same worker)

Actions:

1. Upload only the frozen verified bundle and recheck its hash before extraction.
2. Verify all runtime binary hashes.
3. Start observer and metrics collection before database processes.
4. Seed exact 500,000/5,000,000/1,000,000/250,000 cardinality within the frozen
   setup deadline.
5. Reconcile every count and deterministic field/content rule.
6. Verify vector index health and ANN recall at least equal to the frozen gate.
7. Wait for selected schema and statistics jobs.
8. Capture target-scale current/selected plans, rows read, optimizer estimates,
   plan hashes, and isolated query latency.
9. Export and independently verify a full setup receipt off-Pod.

Pass:

- exact content and counts;
- no missing/mismatched rows;
- plan gates match PF-2 and contain no prohibited full scan;
- schema/statistics complete;
- observer has zero gaps;
- setup evidence survives off-Pod.

Kill:

- any count/content mismatch;
- uncertain DDL or statistics state;
- plan regression at target scale;
- setup consumes the retrieval/teardown reserve;
- observer or export failure.

### PF-6 — remote query, gateway, and admission matrix (same worker)

Actions:

1. Run named read families at c10/c50/c100/c250/c500.
2. Separate cold connection establishment from steady-state measurement.
3. Run one-gateway and `167/167/166` three-gateway diagnostics at literal c500.
4. Record actual active statements, connections, admission waits, CPU, SQL
   service latency, plans, store health, and all named histograms.
5. A/B observers on/off on identical frozen canary inputs and order-randomize the
   A/B to reduce thermal/cache bias.
6. Run the unchanged aggregate mixed c500 workload three complete 120-second
   epochs with the observer enabled.

Pass:

- every named family meets original 5s/10s limits;
- each unchanged mixed epoch meets original limits;
- zero execution errors;
- observer overhead no more than 10 percent p99;
- no admission, connection, LSM, I/O, CPU, or memory signal contradicts the
  selected worker claim;
- literal c500 semantics preserved.

Kill:

- any family or mixed epoch fails;
- gateway distribution hides concurrency;
- observer-disabled only pass;
- missing raw output, plan, histogram, or metric window.

### PF-7 — 15-minute growth, evidence, and interruption canary (same worker)

Actions:

1. Run a 15-minute representative measured-phase segment at full cardinality
   with the selected observer and continuous off-Pod export.
2. Record separate database, Cockroach logs, controller logs, metrics,
   telemetry, receipts, manifests, network proof, and staging bytes.
3. Compute observed, conservative linear, confidence-bound, and maximum-window
   24-hour projections; do not use only the mean.
4. Require network-proof projection no greater than 1 GiB.
5. Require every other class to fit its frozen ceiling with at least 20 percent
   headroom and no unexplained accelerating slope.
6. Complete one scheduled `SIGKILL` process crash/restart/reconciliation cycle,
   explicitly labeled same-host.
7. Export a canonical checkpoint, verify it locally, kill the remote campaign
   process, and prove the local complete checkpoint remains independently valid
   while a partial successor cannot be accepted.
8. Verify controller, observer, database, and transfer processes reach their
   declared terminal states without leaks.

Pass:

- all growth projections and headroom gates pass;
- zero undeclared destination or observer loss;
- same-host process recovery and exact reconciliation pass;
- interruption-survivable checkpoint proof passes;
- local/remote hashes agree;
- worker teardown remains available.

Kill:

- network projection over 1 GiB;
- any evidence class threatens its ceiling;
- non-linear growth cannot be bounded;
- missed checkpoint or broken hash chain;
- fault or interruption recovery ambiguity.

### PF-8 — remote closeout and final freeze

Actions:

1. Flush, fsync, export, and independently hash-verify every evidence class.
2. Stop all workloads and observers.
3. Delete the worker.
4. Prove exact-ID lookup absence and empty campaign-scoped active/all-status
   inventory.
5. Verify no SSH, transfer, supervisor, watchdog, database, or paid process
   remains.
6. Record exact known cost and any provider billing lag separately; do not invent
   a charge.
7. Run residue, secret, private-path, symlink, and source-manifest scans.
8. Freeze the complete candidate packet and hashes.
9. Obtain fresh independent GLM same-hash review of the complete evidence packet.

Pass:

- all PF-0 through PF-8 receipts GREEN;
- every artifact hash and count agrees;
- worker and paid-resource inventory empty;
- final independent verdict GREEN with exact packet and served-model identity;
- no unresolved critical/high finding.

Only then set:

`PDH3_R12_PREFLIGHT_GREEN__24H_RUN_REQUIRES_SEPARATE_AUTHORIZATION`

Otherwise set:

`PDH3_R12_PREFLIGHT_BLOCKED`

with exact blocker, last GREEN stage, hashes, evidence paths, cost state, teardown
state, and next safe action.

## 9. Measured-clock start predicates for the later 24-hour campaign

Even after PF-8 GREEN, the later 24-hour measured clock may start only when a
separately authorized campaign proves all predicates again on its actual worker:

1. packet, source, binary, image, and tool hashes match;
2. worker hardware, price, storage, ports, deadlines, and campaign ID match;
3. exact full cardinality and reconciliation pass;
4. selected schema/statistics jobs are complete;
5. target plans remain constrained and hash-consistent;
6. three unchanged mixed c500 preflight epochs pass;
7. observer and native metrics are live with zero gaps;
8. 15-minute growth projection remains inside all gates;
9. off-Pod checkpoint export is live and independently verified;
10. lifecycle guard heartbeat, retrieval reserve, and teardown guarantee are
    current;
11. no other paid campaign worker exists;
12. independent preflight packet verdict is GREEN.

These predicates are conjoined. A missing predicate means the measured clock
does not begin.

## 10. Cost and retry law for preflight execution

This review packet sets no new spend authorization. A later execution prompt
must freeze:

- live worker type and observed price;
- setup/canary/retrieval/teardown time budget;
- maximum paid lifetime;
- aggregate campaign cost including prior attempts;
- maximum creation attempts and launch window;
- retryable versus non-retryable failure classes;
- provider-native stop/terminate deadlines;
- exact-ID guard and deletion proof.

Retries may occur only before upload for transient creation, capacity,
pre-upload readiness, or returned-property mismatch. Every failed worker must be
deleted and absence-proved before another creation. No replacement is allowed
after upload, full-cardinality setup, hidden/canary result visibility, or any
measured execution begins without fresh explicit authorization.

## 11. Claim boundary

A successful preflight or later 24-hour campaign may support only:

- deterministic correctness at the declared synthetic cardinality;
- sustained bounded single-worker execution;
- literal c500 load under the documented worker and gateway configuration;
- same-host three-process crash/restart/reconciliation;
- bounded evidence growth and interruption-survivable off-Pod checkpoints;
- exact verifier schedule, if the later campaign completes it.

It may not support claims of:

- production incident recovery;
- production-scale customer traffic;
- independent-machine or availability-zone fault tolerance;
- CockroachDB Cloud production durability;
- recovery of uncaptured deleted bytes;
- multi-region resilience;
- external-user validation.

## 12. Plan-review judge contract

The independent GLM judge reviews this exact plan revision only. The judge is
non-authoring and receives sanitized content with no credentials, shell, write,
deployment, RunPod, billing, browser, repository, or implementation authority.

The judge must assess:

1. whether the plan addresses every verified R11b blocker without weakening the
   workload or thresholds;
2. whether its canaries are predictive of the target-scale remote path;
3. SQL/index/statistics correctness and plan-proof sufficiency;
4. literal-c500 semantics, gateway/admission diagnostics, and hardware sizing;
5. low-volume egress proof and evidence-growth validity;
6. interruption-survivable evidence and container-storage limitations;
7. observability completeness and measurement perturbation;
8. supervisor terminal-state completeness and false-success paths;
9. lifecycle, retry, cost, teardown, and denial-of-wallet boundaries;
10. topology and public-claim honesty;
11. whether any stage is ceremonial, redundant, untestable, or missing a kill
    line;
12. whether the plan is safe and sufficient to execute as a preflight, not
    whether the 24-hour campaign itself is already GREEN.

Required response schema:

```text
SERVED_MODEL: <provider-reported model>
TARGET_PLAN_SHA256: <exact hash supplied with the review request>
VERDICT: GREEN | NOT_GREEN | BLOCKED | JUDGE_UNAVAILABLE
CRITICAL_FINDINGS:
- <finding or NONE>
HIGH_FINDINGS:
- <finding or NONE>
REQUIRED_CORRECTIONS:
- <smallest correction or NONE>
NONBLOCKING_OBSERVATIONS:
- <observation or NONE>
RATIONALE: <concise evidence-based explanation>
```

`GREEN` means only that this plan is fit to begin under a separately authorized
execution envelope. It is not implementation evidence and does not authorize a
RunPod launch.

## 13. Current terminal state

`PDH3_R12_PREFLIGHT_PLAN_READY_FOR_INDEPENDENT_REVIEW`

`PDH3_24H_CAMPAIGN_NO_GO`

