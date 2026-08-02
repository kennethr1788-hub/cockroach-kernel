# PDH-3 Provider Documentation Compliance Audit

Status: `DOCUMENTATION_AUDIT_COMPLETE__CAMPAIGN_NO_GO`

UTC reviewed: `2026-08-02T04:22:40Z`

Repository: `/Users/kennethruedas/sandbox/cockroach-kernel-build-20260725`

Branch: `evidence/external-validity-r1`

HEAD: `5989e904f5d829ef5e7ae3597477699c8b98d92c`

## 1. Verdict

The candidate is not ready for another 24-hour launch.

The implementation already follows the provider guidance in several important
areas, but seven documentation-backed gaps remain load-bearing:

1. The five `mcp_receipt_view` reads filter `ck.receipts.task_id`, while the
   schema has no index led by `task_id`. The last full-cardinality result is
   consistent with repeated full scans, but the target-scale current-plan versus
   indexed-plan A/B proof has not yet been run.
2. The c500 workload means 500 concurrently executing `querybench` workers on
   one SQL gateway. This substantially exceeds CockroachDB's published guidance
   for a 16- or 32-vCPU host and is not connection-pooled.
3. The current `strace` design projects to about 8.32 GB over 24 hours, exceeding
   its own frozen 2 GiB evidence cap.
4. The RunPod contract uses only disposable container storage. RunPod explicitly
   says container-only data can be lost on interruption, restart, stop, or
   termination. The current design therefore cannot guarantee preservation of
   a failed 24-hour campaign's evidence.
5. Three CockroachDB processes run on one machine and one physical disk. This is
   valid only as a same-host process-recovery experiment; CockroachDB explicitly
   says it is not a production topology and provides no independent failure
   domains.
6. The campaign does not capture the provider-recommended CockroachDB metrics,
   active-session/admission evidence, LSM/storage health, or normal Cockroach log
   channels. `--logtostderr=ERROR` is insufficient for diagnosis or a production-
   behavior claim.
7. The accepted RunPod worker envelope is internally too broad. It can accept a
   CPU/RAM pair that violates CockroachDB's 4 GiB-per-vCPU recommendation, and it
   does not prove the provider disk meets the documented IOPS/throughput needs.

These are repair-and-canary blockers. They are not authorization to launch a Pod
or alter the frozen product candidate.

## 2. Scope and completeness statement

It would be false to say that every document published by both companies was
read. Both providers document products unrelated to this campaign, including
RunPod Serverless, Flash, model endpoints, Hub publishing, and CockroachDB Cloud
features that are not used by the self-hosted synthetic soak.

This audit is complete within the relevant boundary: every official
documentation family capable of changing this campaign's hardware selection,
Pod lifecycle, storage durability, billing, networking, security, CockroachDB
version, topology, memory, storage, query plans, indexes, statistics, connection
concurrency, vector behavior, node faults, observability, or teardown was
inventoried and reviewed.

Official documentation indexes were fetched directly before review:

| Provider index | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| RunPod `https://docs.runpod.io/llms.txt` | 314 | 65,773 | `0d224b84794cdc5fd9e449cee3981678225a716ea2db6635cca237c20dfe790b` |
| CockroachDB `https://www.cockroachlabs.com/docs/llms.txt` | 835 | 99,915 | `789bda063cee5654b1e61dc02ee761fb843103accd734096d8fe23cafc0d3fc6` |

Excluded as non-applicable: RunPod Serverless, Flash, public endpoints, Instant
Clusters, model APIs, model training, Hub publishing, savings plans except their
billing effects, and CockroachDB managed-cloud-only deployment operations,
multi-region SQL locality features, CDC sinks, backups, Kubernetes operators,
and application-driver tutorials not used by this harness.

## 3. Frozen local facts

### 3.1 Binaries and control surface

- CockroachDB Linux binary SHA-256:
  `97a8836b3e816745ba698f47616ff5038ba55f5e252a2959924e9e2d41014d7f`.
- CockroachDB local Darwin binary reports `v26.2.3`, release build, build commit
  `90d3b6080727dc810224a99903cb2e88b81e91ae`.
- CockroachDB v26.2 is a supported Regular release and v26.2.3 is a documented
  production patch release.
- Pinned RunPod CLI version: `2.7.2-309512b`.
- Pinned RunPod CLI SHA-256:
  `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`.
- Both `/private/tmp/runpodctl-v2.7.2-darwin-arm64` and
  `/tmp/runpodctl-v2.7.2-darwin-arm64` currently match that hash.
- The pinned CLI's own help accepts RFC3339 datetimes for `--stop-after` and
  `--terminate-after`. This is more specific than the public docs, whose examples
  describe durations. The pinned executable is the controlling execution proof.

### 3.2 Current database shape

- Three `cockroach start` processes are bound to loopback on one host.
- Every node uses `--insecure`, `--cache=8GiB`, and
  `--max-sql-memory=8GiB`.
- All three stores share the same RunPod container filesystem.
- Production validation currently requires `store_size=None`; no per-store
  capacity limit is imposed.
- The RunPod envelope allows 16-32 vCPU and 94-188 GiB RAM without validating
  the specific CPU/RAM combination.
- All `querybench` traffic targets `nodes[0]` as the sole SQL gateway.
- c500 invokes `cockroach workload run querybench --concurrency=500` with
  `--warmup-conns=0`; this is 500 workload workers, not 500 logical producers
  behind a smaller execution pool.

### 3.3 Current evidence and lifecycle shape

- Workload cardinality is 500,000 tasks, 5,000,000 trajectory events,
  1,000,000 receipts, and 250,000 vectors.
- Schedule is 288 five-minute checkpoints, 24 same-host process `SIGKILL`
  cycles, and exactly 9,976 verifier executions.
- The current Pod uses a 250 GB disposable container disk and no persistent or
  network volume.
- Only TCP SSH is exposed; CockroachDB SQL and HTTP endpoints remain on loopback.
- Global networking is disabled.
- The local detached lifecycle guard binds an exact Pod ID and name, while
  provider-native stop/terminate deadlines are supplied at creation.
- The tracer follows the complete child process tree for `connect` and `sendto`,
  but the observed projection exceeds the frozen trace-size limit.

## 4. CockroachDB documentation reconciliation

| Topic | Official guidance | Current state | Finding |
|---|---|---|---|
| Release | v26.2 is a Regular release; v26.2.3 is a published patch | Exact v26.2.3 release binary is hash-bound | `COMPLIANT` |
| Security | `--insecure` is for short-lived testing, not long-lived deployment | All traffic is loopback inside one disposable Pod | `CONDITIONAL`: acceptable for this synthetic test only; no production-security claim |
| Topology | Do not run multiple node processes on one machine; use distinct machines for production fault tolerance | Three processes share one host and disk | `NON_PRODUCTION_TOPOLOGY`; claim only same-host process recovery |
| CPU | Minimum 8 vCPU cluster, no fewer than 4 vCPU per node; active SQL should generally stay at or below 4x total vCPU | 16-32 host vCPU; 500 active query workers | `BLOCKED`: c500 exceeds the published concurrency envelope |
| RAM | At least 4 GiB/vCPU; `(2 * max-sql-memory) + cache <= 80% RAM` per node | Three processes each use 8 GiB cache and 8 GiB SQL memory | `CONDITIONAL`: aggregate formula needs exact observed-host validation; some accepted CPU/RAM pairs fail 4 GiB/vCPU |
| Storage | Dedicated store volumes; roughly 500 IOPS and 30 MB/s per vCPU; avoid high sustained capacity | Three stores and evidence share one unknown-performance container disk | `BLOCKED`: no provider disk throughput/IOPS proof and no explicit per-store bounds |
| Full scans | Avoid full scans on large tables; use secondary indexes and plan checks | Receipts has no index led by `task_id` | `BLOCKED`: run target-scale A/B plan proof and conditionally add index |
| Index candidate | Index filter columns; use storing columns when they make the query covering | Proposed `receipts(task_id) STORING(status,event_hash)` | `PROVISIONALLY CORRECT`, subject to target-scale plan proof |
| Stale projection | Plan queries against actual predicates | `source_key LIKE ...` is not led by existing `(source_table, source_key, sequence)` unique index | `OPEN`: target-scale EXPLAIN decides whether a separate `source_key` index is justified |
| Statistics | Auto stats are enabled; explicit stats are optional and create background jobs | No plan/statistics receipt exists after bulk seed | `OPEN`: record auto stats or create named stats, then verify job completion before plan freeze |
| EXPLAIN | `EXPLAIN` is dry; `EXPLAIN ANALYZE` executes the statement | No target-scale plan evidence exists | `BLOCKED`: use `EXPLAIN` and read-only `EXPLAIN ANALYZE (DISTSQL)` only |
| Pooling | Reuse connections; avoid connection storms and excessive simultaneously active queries | `--warmup-conns=0`, one gateway, 500 workers | `BLOCKED`: characterize cold versus steady state and preserve c500 semantics honestly |
| Gateway distribution | Production deployments normally distribute SQL traffic across nodes | All traffic targets node 1 | `OPEN`: A/B one gateway versus three gateways without changing total c500 concurrency |
| Bulk inserts | Use empirically chosen multi-row batches; large batches can yield SQLSTATE 40001 | 5,000-task batches plus bounded retry/reconciliation | `CONDITIONAL`: 5,000 exceeds documented examples; historical timing proves feasibility, but target canary must retain timeout evidence |
| Idempotency | Constraints and conflict behavior must preserve correctness | `ON CONFLICT DO NOTHING` plus exact per-field reconciliation and final full reconciliation | `COMPLIANT`: conflicts cannot silently conceal mismatched rows because content mismatches fail closed |
| Vector indexes | ANN is approximate; backfill on non-empty table blocks writes | Index is created empty and maintained during one-row vector inserts; exact validation is separate from ANN recall | `COMPLIANT` |
| Vector insertion | Avoid large batch vector inserts | Persistent clients insert one vector row per transaction | `COMPLIANT` |
| Faults | Graceful maintenance drains; `SIGKILL` bypasses shutdown logic and can cause latency/timeouts | Campaign intentionally uses `SIGKILL` | `CONDITIONAL`: valid crash injection, not maintenance behavior; name it exactly and preserve recovery evidence |
| Failure domains | Three nodes can retain quorum only when failures are independent | All nodes are co-located | `LIMITATION`: no independent-machine or production-HA claim |
| Admission control | Keep it enabled and monitor admission/active SQL behavior | No admission metrics are captured | `BLOCKED`: do not disable; capture admission and active statement metrics |
| Metrics | Capture SQL latency, active statements, CPU, RSS, node health, LSM, storage, and I/O | Mostly process RSS/FD/tree and filesystem size | `BLOCKED`: insufficient provider-native observability |
| Logs | Preserve relevant Cockroach log channels for diagnosis | `--logtostderr=ERROR` only | `BLOCKED`: capture bounded OPS/HEALTH/STORAGE/SQL performance evidence |

## 5. RunPod documentation reconciliation

| Topic | Official guidance | Current state | Finding |
|---|---|---|---|
| Workload choice | Data processing is CPU-focused; prioritize CPU and RAM | L40S GPU is unused and was selected for host RAM | `OPEN`: mechanically compare live CPU Pods; L40S is acceptable only if it is the cheapest available shape that satisfies measured CPU/RAM/disk requirements |
| Cloud tier | Secure Cloud has stronger reliability than Community Cloud | `SECURE` required | `COMPLIANT` |
| Storage | Container disk is temporary; volume/network storage is for checkpoints and durable outputs | Evidence exists only on container disk until final retrieval | `BLOCKED`: no outage-survivable evidence |
| Stop | Stopping clears container disk data | Native stop is a spend fuse after the workload window | `HIGH RISK`: local retrieval must begin and finish before stop; stop cannot be treated as evidence preservation |
| Terminate | Termination permanently deletes non-network-volume data | Delete occurs only after retrieval in ordinary path | `COMPLIANT` ordinary path; provider outage and deadline races remain open |
| Update/reset | Updating a running Pod resets it and erases non-persistent data | Contract does not use update/reset after launch | `COMPLIANT` |
| Maintenance/outage | Unexpected crashes occur; checkpoint long jobs and back up important data | No off-Pod checkpoint stream or volume | `BLOCKED` |
| Billing | Billed per second; zero balance terminates no-volume Pods; at least one hour of credit required | Price is preflighted, but account balance is not bound in the packet | `BLOCKED`: verify balance covers the maximum lifecycle plus margin; do not change auto-pay without owner approval |
| Cost | Live console/API is authoritative for current rate | Frozen historical L40S rate is used | `LIVE_PREFLIGHT_REQUIRED` |
| CLI | CLI supports Pod create/get/list/stop/delete and native deadlines | Pinned CLI and hashes are correct | `COMPLIANT` |
| CLI/doc drift | Public CLI page describes deadline durations; pinned CLI help requires RFC3339 datetime | Packets use RFC3339 datetimes | `COMPLIANT` with pinned-binary evidence; record the divergence |
| Pod identity | RunPod injects `RUNPOD_POD_ID` and a Pod-scoped `RUNPOD_API_KEY` | External local exact-ID guard remains primary | `COMPLIANT`; an in-Pod watchdog is optional only after proving the injected key cannot manage other resources |
| Ports | Exposed ports are public surfaces and require authentication | Only SSH is exposed | `COMPLIANT`, subject to key-only auth verification |
| Global networking | Optional Pod-to-Pod networking, not required here | Disabled | `COMPLIANT` |
| Multi-tenancy | Pods are container-isolated on provider infrastructure | Synthetic public-safe data only | `COMPLIANT` for data scope; do not claim VM-grade isolation |
| API versions | v2 Pod API is documented as beta | Current pinned CLI path is already tested | `COMPLIANT`: do not migrate control APIs inside this campaign without a separate smoke test |

## 6. Mandatory correction set

### C1. Prove and conditionally fix the receipt query plan

Run on a fresh full-cardinality diagnostic dataset before any measured clock:

1. Record `SHOW INDEXES FROM ck.receipts` and `SHOW STATISTICS FOR TABLE
   ck.receipts`.
2. Record `EXPLAIN` and read-only `EXPLAIN ANALYZE (DISTSQL)` for all five
   receipt-view predicates and the stale-projection predicate.
3. Freeze the current-plan evidence before changing schema.
4. Add only if confirmed:

   `CREATE INDEX receipts_task_id_idx ON ck.receipts (task_id) STORING (status, event_hash);`

5. Wait for the schema-change job to succeed.
6. Record fresh statistics or prove suitable auto statistics exist and are
   current.
7. Repeat identical plans and isolated latency measurements.
8. Reject the candidate if the filtered receipts plan still contains a full
   scan or if row/count/content reconciliation changes.

Do not require a full scan as a prerequisite to the diagnostic; the correct
gate is a same-query current-plan/indexed-plan A/B result.

### C2. Preserve c500 semantics and diagnose admission pressure

Do not silently reinterpret c500 as 500 logical producers behind a smaller
pool. That would be a prospective contract change.

For canaries only, run the frozen 500-worker workload with named query-family
histograms and record:

- actual concurrently active SQL statements;
- open and newly established connections;
- CPU and SQL service latency;
- admission wait metrics;
- one-gateway versus evenly distributed three-gateway execution;
- cold-start interval separately from steady-state interval.

If the literal 500-active-statement gate remains required, the final worker must
pass it without hiding queries behind a smaller pool. If realistic pooling is
preferred, amend the claim and contract prospectively and never reclassify the
prior failures.

### C3. Replace the oversized network trace with a proved bounded mechanism

The current 8.32 GB projection fails the frozen 2 GiB cap. Before replacement,
prove the exact worker supports the proposed primitive. An acceptable design
must:

- observe every descendant from process start;
- bind destination class, bytes, packets, and denials;
- fail closed on observer loss;
- emit hash-chained summaries;
- preserve enough raw evidence to audit the summaries;
- project below the cap with at least a two-times safety margin during a
  15-minute full-cardinality measured-phase canary.

Do not claim cgroup counters alone prove destination allow-list conformance.
Network namespaces, nftables/eBPF, or another enforcement mechanism require an
actual capability smoke test on the selected RunPod image.

### C4. Make evidence survive a provider interruption

Current authorization forbids persistent and network volumes. Therefore one of
these must be explicitly chosen before launch:

1. obtain new owner authorization for a bounded volume and bind its lifecycle,
   cost, encryption limitations, and deletion; or
2. retain the no-volume contract but pull hash-bound incremental checkpoints and
   raw failure evidence off-Pod to the local supervisor throughout the run.

The second option preserves the current storage boundary and is recommended for
this synthetic campaign. Its canary must kill the remote process after a
checkpoint, prove the local copy remains independently verifiable, and prove
retrieval never requires stopping or updating the Pod.

### C5. Correct topology and fault claims

Keep the single worker if the objective is one successful bounded campaign, but
state the result as:

`three-process, single-host crash/restart/reconciliation evidence`

Never call it independent-node, availability-zone, multi-domain, production-HA,
or infrastructure-outage evidence. A real three-machine topology would require
new cost, networking, lifecycle, and authorization gates and is not the minimal
path to one honest successful run.

### C6. Add provider-native observability

At a bounded interval, collect from all three processes:

- `/metrics` or `/_status/vars` provider metrics;
- active SQL sessions/statements and gateway distribution;
- SQL service latency and admission waits;
- process CPU/RSS/FD/PID state;
- Pebble/LSM health, including L0 indicators and read amplification;
- store capacity, write/read throughput, IOPS, and queue/service time;
- node liveness and restart markers;
- real bounded Cockroach OPS/HEALTH/STORAGE/SQL performance logs.

Do not disable admission control or logging to manufacture a latency pass.

### C7. Tighten hardware verification

At live preflight, enumerate current CPU and GPU offers and select mechanically:

- CPU/RAM pair satisfies at least 4 GiB per observed vCPU;
- aggregate three-process memory settings satisfy the documented formula with
  room for Python, querybench, tracing, logs, and the OS;
- measured disk meets the required workload throughput and IOPS;
- explicit per-store bounds plus evidence/output reserves cannot exceed the
  250 GB disk or 70% campaign limit;
- quoted compute plus storage remains within the authorized rate/lifecycle
  ceiling;
- exact account credit is sufficient for the maximum lifecycle plus a bounded
  safety margin.

The L40S label is not evidence of suitability. Its GPU is unused.

## 7. Provider-documentation-aligned canary ladder

1. `LOCAL_SCHEMA_PLAN`: current-plan/indexed-plan A/B on representative data.
2. `LOCAL_CORRECTNESS`: complete unit/integration suite, exact reconciliation,
   vector recall, timeout/idempotency, and failure-state tests.
3. `REMOTE_CAPABILITY`: selected worker identity, CPU/RAM pairing, disk I/O,
   namespaces/firewall/observer capability, account balance, and deadline proof.
4. `REMOTE_FULL_CARDINALITY_SETUP`: exact 500k/5M/1M/250k counts and content,
   schema job completion, statistics, index plans, and vector quality.
5. `REMOTE_QUERY_FAMILIES`: named receipt/vector/projection/trajectory histograms,
   cold versus steady state, one versus three gateways, literal c500 preserved.
6. `REMOTE_OBSERVABILITY_AND_GROWTH`: 15-minute full-cardinality evidence,
   network-proof, DB, logs, telemetry, receipts, and disk projection.
7. `REMOTE_FAULT_AND_CHECKPOINT`: one `SIGKILL` crash/restart reconciliation plus
   one off-Pod incremental checkpoint recovery test.
8. `FREEZE`: new packet, source hashes, exact thresholds, disclosure language,
   live price/cost, and independent same-hash review.
9. `FINAL_24_HOUR`: only after every prior rung is directly GREEN.

No reduced-cardinality result may authorize a target-cardinality query-plan,
storage, or concurrency conclusion.

## 8. Go/no-go checklist

- [ ] Current-plan/indexed-plan A/B proves the chosen receipts plan at full
      cardinality.
- [ ] The stale-projection plan is measured and either indexed or proved
      immaterial.
- [ ] Schema-change and statistics jobs are complete and receipt-bound.
- [ ] c500 semantics are explicit and unchanged, or the contract is amended
      prospectively.
- [ ] Active-statement/admission evidence is within the chosen contract.
- [ ] Named query-family p99 and maximum latency gates pass.
- [ ] Network/egress evidence projects below 1 GiB with two-times margin under
      the 2 GiB cap.
- [ ] Evidence survives a simulated Pod/process interruption through a verified
      off-Pod checkpoint or newly authorized persistent mechanism.
- [ ] Worker CPU/RAM pairing satisfies CockroachDB sizing guidance.
- [ ] Remote disk IOPS, throughput, capacity, and per-store bounds pass.
- [ ] CockroachDB metrics and required log channels are continuously present.
- [ ] Fault receipts say same-host process crash, not independent failure domain.
- [ ] Account balance, live rate, maximum cost, stop, terminate, and retrieval
      reserve are all verified.
- [ ] Stop cannot erase the only copy of evidence before retrieval.
- [ ] Pinned CLI/binary hashes, image, ports, volumes, Pod identity, and
      inventory all match.
- [ ] All previous failures remain append-only and no hidden-result tuning occurs.
- [ ] Fresh same-hash independent review returns GREEN.

Any unchecked item is `NO_GO`.

## 9. Official source set reviewed

### CockroachDB

- [v26.2 release notes](https://www.cockroachlabs.com/docs/releases/v26.2)
- [release support policy](https://www.cockroachlabs.com/docs/releases/release-support-policy)
- [SQL performance best practices](https://www.cockroachlabs.com/docs/v26.2/performance-best-practices-overview)
- [connection pooling](https://www.cockroachlabs.com/docs/v26.2/connection-pooling)
- [common issues to monitor](https://www.cockroachlabs.com/docs/v26.2/common-issues-to-monitor)
- [CREATE STATISTICS](https://www.cockroachlabs.com/docs/v26.2/create-statistics)
- [EXPLAIN](https://www.cockroachlabs.com/docs/v26.2/explain)
- [EXPLAIN ANALYZE](https://www.cockroachlabs.com/docs/v26.2/explain-analyze)
- [vector indexes](https://www.cockroachlabs.com/docs/v26.2/vector-indexes)
- [VECTOR](https://www.cockroachlabs.com/docs/v26.2/vector)
- [admission control](https://www.cockroachlabs.com/docs/v26.2/admission-control)
- [Cockroach workload](https://www.cockroachlabs.com/docs/v26.2/cockroach-workload)
- [metrics](https://www.cockroachlabs.com/docs/v26.2/metrics)
- [Prometheus endpoint](https://www.cockroachlabs.com/docs/v26.2/prometheus-endpoint)
- [SHOW SESSIONS](https://www.cockroachlabs.com/docs/v26.2/show-sessions)
- [node shutdown](https://www.cockroachlabs.com/docs/v26.2/node-shutdown)
- [replication layer](https://www.cockroachlabs.com/docs/v26.2/architecture/replication-layer)
- [deploy on-premises](https://www.cockroachlabs.com/docs/v26.2/deploy-cockroachdb-on-premises)
- [topology patterns](https://www.cockroachlabs.com/docs/v26.2/topology-patterns)
- [start a single-node cluster](https://www.cockroachlabs.com/docs/v26.2/cockroach-start-single-node)
- [storage dashboard](https://www.cockroachlabs.com/docs/v26.2/ui-storage-dashboard)
- [overload dashboard](https://www.cockroachlabs.com/docs/v26.2/ui-overload-dashboard)
- [essential self-hosted alerts](https://www.cockroachlabs.com/docs/v26.2/essential-alerts-self-hosted)
- [TLS/PKI security reference](https://www.cockroachlabs.com/docs/v26.2/security-reference/transport-layer-security)
- [local testing](https://www.cockroachlabs.com/docs/v26.2/local-testing)

### RunPod

- [Pods overview](https://docs.runpod.io/pods/overview)
- [choose a Pod](https://docs.runpod.io/pods/choose-a-pod)
- [manage Pods](https://docs.runpod.io/pods/manage-pods)
- [maintenance, outages, and data safety](https://docs.runpod.io/pods/maintenance-and-outages)
- [storage types](https://docs.runpod.io/pods/storage/types)
- [Pods pricing](https://docs.runpod.io/pods/pricing)
- [billing overview](https://docs.runpod.io/accounts-billing/billing)
- [Pod API v1 create](https://docs.runpod.io/api-reference/pods/POST/pods)
- [Pod API v2 create](https://docs.runpod.io/api-reference-v2/pods/create-a-pod)
- [CPU catalog API](https://docs.runpod.io/api-reference-v2/catalog/list-cpu-types)
- [CPU types reference](https://docs.runpod.io/references/cpu-types)
- [RunPod CLI Pod reference](https://docs.runpod.io/runpodctl/reference/runpodctl-pod)
- [RunPod CLI overview](https://docs.runpod.io/runpodctl/overview)
- [template environment variables](https://docs.runpod.io/pods/templates/environment-variables)
- [Pod termination API](https://docs.runpod.io/api-reference-v2/pods/terminate-a-pod)
- [SSH](https://docs.runpod.io/pods/configuration/use-ssh)
- [exposed ports](https://docs.runpod.io/pods/configuration/expose-ports)
- [Pod networking](https://docs.runpod.io/pods/networking)
- [security and compliance](https://docs.runpod.io/references/security-and-compliance)
- [Pod list API](https://docs.runpod.io/api-reference/pods/GET/pods)
- [Pod migration/troubleshooting](https://docs.runpod.io/pods/troubleshooting/pod-migration)
- [release notes](https://docs.runpod.io/release-notes)

## 10. Final recommendation

`RESEARCH_GO_FOR_REPAIR_AND_CANARIES__24_HOUR_LAUNCH_NO_GO`

The most efficient honest path is not another blind 24-hour attempt. It is:

`receipt-plan A/B -> literal-c500 diagnostics -> bounded egress proof -> off-Pod evidence checkpoint -> full-cardinality remote preflight -> frozen independent review -> one 24-hour campaign`

