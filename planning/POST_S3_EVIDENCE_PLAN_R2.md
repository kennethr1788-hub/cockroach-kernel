# Cockroach Kernel Post-S3 Evidence Plan R2

## Status and revision basis

- `MODE`: planning only
- `SUPERSEDES`: `COCKROACH_KERNEL_POST_S3_EVIDENCE_PLAN_20260726_R1.md`
- `RUNPOD_LIFECYCLE_AUTHORIZED_BY_THIS_DOCUMENT`: no
- `AWS_PUBLIC_DEMO_DEPLOYMENT_AUTHORIZED_BY_THIS_DOCUMENT`: no
- `PUBLIC_RELEASE_AUTHORIZED_BY_THIS_DOCUMENT`: no
- `ACTIVE_S3_RUNTIME_TOUCHED`: no
- `CURRENT_LIVE_STATE_AT_REVISION`: `S3_PRODUCTION_RUNNING`
- `LAST_GREEN_GATE_AT_REVISION`: `CK_P9_INTEGRATION_GREEN`

This revision incorporates the same-hash advisory findings from exact GLM 5.2, Claude Opus 4.8, and AGY bound to Gemini 3.1 Pro High. It keeps the two sequential RunPod campaigns but reallocates effort toward the official judging criteria.

There is no calendar cutoff. Provider stop and terminate times are paid-resource safety fuses, not project deadlines.

## Winning-evidence objective

The final submission must directly prove:

1. CockroachDB is the meaningful persistent memory authority, not an initialized accessory.
2. The working application is deployed on AWS and freely judge-accessible.
3. A realistic developer workflow benefits after declared session/workspace loss.
4. A credible conventional recovery baseline receives the same inputs and a fair configuration.
5. Unsafe or unverifiable continuations are refused without mutation.
6. Every public claim is concise, measured, and traceable to raw evidence.

Runtime hours, trial counts, model count, receipt count, and architectural complexity are not success evidence by themselves.

## Strict execution order

1. Close S3 completely.
2. Implement and verify the thin judge-facing CLI and structured failure output.
3. Package the existing behavior as a bounded AWS-deployed functional demo.
4. Prove free judge access and meaningful CockroachDB/AWS behavior on that surface.
5. Conduct one human-driven, non-synthetic workflow trial and freeze its trace.
6. Qualify a credible comparison protocol.
7. Freeze one evidence-candidate commit and deployment manifest.
8. Run RunPod Run 1 against that exact frozen state.
9. Run RunPod Run 2 against the same exact frozen state.
10. Compile the evidence package and exact claim ledger.
11. Rehearse the required public video against the same live surface and receipts.
12. Proceed to public repository/video/submission actions only through their separate existing gates.

The two RunPod workers are sequential. If the implementation, deployed behavior, scenario contract, or authority logic changes after Run 1, Run 1 cannot support final claims affected by that change.

## Gate 0 — S3 closeout

Do not advance when only the timer expires. Require:

- complete measured runtime and all expected S3 evidence classes;
- retrieved and independently hash-verified raw evidence;
- final latency, error, growth, retry, rollback, quarantine, resource, and deterministic-verdict measurements;
- successful worker teardown;
- exact-ID absence and fresh empty active inventory;
- no matching workload, database, guard, transfer, or watchdog process;
- one frozen final S3 packet;
- required final GLM, Claude, and AGY GREEN over one exact packet hash;
- synchronized repository and resume state.

Target: `POST_S3_0_GREEN`. Any unresolved mechanical or judge blocker produces `POST_S3_0_BLOCKED` and prevents further paid workers.

## Gate 1 — Judge-facing CLI and failure contract

Implement only a thin facade over existing authority:

```text
cockroach-kernel demo
cockroach-kernel demo --explain
cockroach-kernel demo --json
cockroach-kernel inspect <receipt>
```

The default path remains visibly `KEYLESS_LOCAL_REPLAY`, contains promotion and refusal, uses the existing deterministic verifier, and requires no network, credential, private endpoint, paid account, hidden session state, Docker, GPU, or RunPod.

Every refusal must display:

```text
VERDICT: REFUSE
REASON: <stable reason code>
PROVABLE_STATE: <bounded verified result>
ACTION_TAKEN: NONE
NEXT_SAFE_ACTION: <specific inspection or recovery step>
RECEIPT: <canonical receipt path>
```

Acceptance:

- byte-identical verdict, reason, receipt, and fresh-context parity with the underlying implementation;
- two independent clean clones;
- promotion and refusal both pass;
- zero hidden network or credential use;
- concise default output;
- full evidence available through `--explain`, `--json`, and `inspect`;
- clean residue and child-process scans.

Target: `POST_S3_CLI_GREEN`.

## Gate 2 — Functional AWS judge surface

This is required submission packaging, not a new recovery capability.

Deploy the already implemented end-to-end behavior on AWS through a bounded architecture that visibly exercises the real CockroachDB memory layer. The deployed path must preserve the same deterministic authority and must not silently replace real behavior with replay.

The deployment contract must prove:

- an AWS-hosted functional demo URL;
- CockroachDB is the persistent memory layer used during the live interaction;
- at least two required CockroachDB tools are meaningfully exercised and identified;
- at least one AWS service is meaningfully exercised and identified;
- promotion and refusal are both observable;
- every result exposes a receipt or bounded evidence reference;
- deterministic authority remains separate from model/advisory output;
- credentials are never exposed to judges or committed;
- the judge does not need a paid account;
- access remains free and available through the judging period;
- bounded input, rate limits, abuse controls, observability, cost alarms, kill switch, and teardown procedure exist;
- no private code, user data, or unrestricted destructive capability enters the demo;
- the live surface and keyless replay produce behaviorally equivalent verdicts on the frozen demo cases.

The deployment packet must state whether the CockroachDB cluster is single-region or multi-region and claim only the verified topology. Record query plans, index use, transaction/retry behavior, vector retrieval, MCP evidence, AWS request evidence, and access-control boundaries.

### Human gate

Public AWS deployment, a public or judge-accessible endpoint, and continuing cloud cost require a separate explicit in-chat authorization after the exact architecture, services, current prices, maximum spend, access duration, and teardown plan are frozen. This planning document does not grant that authority.

Target: `POST_S3_AWS_DEMO_GREEN`. The RunPod campaigns do not begin until this is GREEN.

## Gate 3 — One realistic human-driven workflow proof

Use one real, non-sensitive codebase and a real development objective. Do not use a canned fixture as the primary proof.

Required procedure:

1. Kenneth states a concrete coding task.
2. A coding agent performs useful work with committed and uncommitted progress.
3. The product records the declared trajectory through its live AWS/CockroachDB path.
4. Kenneth makes one independent saved edit so the proof is not model-only.
5. The disposable workspace and original session undergo the declared loss event.
6. A fresh process with no prior conversation invokes the product.
7. The product promotes or refuses according to its existing deterministic policy.
8. The fresh process attempts continuation without Kenneth restating the task.
9. Tests or an equivalent executable acceptance check run.
10. The full trace, receipts, limitations, and any lost work are preserved.

Measure:

- wall-clock time from loss declaration to verified continuation or refusal;
- declared, provable, retained, and lost work units;
- committed and uncommitted work retained;
- manual interventions and scripted steps;
- task restatement required: yes/no;
- executable checks passed;
- unsafe acceptance or mutation;
- exact CockroachDB and AWS operations used;
- final residue and cleanup.

Label the result `SINGLE_OPERATOR_REAL_WORKFLOW_EVIDENCE`. It is not public-user research and cannot establish population-wide usability.

Target: `POST_S3_REAL_WORKFLOW_GREEN` if the trace is complete and honest. The behavior itself may promote or refuse; the gate grades evidence integrity, not a predetermined favorable result.

## Gate 4 — Baseline qualification

Run 1 cannot use a self-serving baseline. Before freezing it:

1. Research current official documentation for credible recovery mechanisms that a developer would reasonably use.
2. Select the strongest freely reproducible baseline that fits the loss scenario.
3. Include ordinary Git as a reference, but do not treat Git alone as the only competitor.
4. If a periodic snapshot/checkpoint baseline is used, publish its cadence, retained state, storage, permissions, and recovery procedure.
5. Give every method identical initial state, observable inputs, loss event, time budget, executable success test, and allowed operator information.
6. Separate capabilities that the baseline does not claim to provide from actual baseline failures.
7. Freeze the scenario definitions and success rules before running the evidence-candidate build.

The packet must identify construct validity, experimenter bias, baseline tuning, missing data, and limitations. GLM and Claude review the exact protocol before Run 1. Judges may identify defects but do not author the baseline or implementation.

Target: `POST_S3_BASELINE_PROTOCOL_GREEN`.

## Gate 5 — Freeze one evidence candidate

Freeze:

- implementation commit;
- deployed artifact and configuration hashes;
- schema and migration hashes;
- CLI output contract;
- baseline implementations and configuration;
- realistic workflow trace;
- scenario catalog;
- held-out-case generation contract;
- dependency/license manifest;
- public/private evidence boundaries.

No behaviorally relevant change is allowed between Run 1 and Run 2. Any such change creates a new candidate and invalidates affected evidence.

Target: `POST_S3_EVIDENCE_CANDIDATE_GREEN`.

## Gate 6 — RunPod Run 1: paired comparative evidence

### Purpose

Measure whether the existing product improves recovery under fair, judge-legible scenarios.

### Workload

Use scenario diversity rather than excessive repetition:

- six frozen scenario classes;
- three recovery methods: ordinary Git reference, the qualified strongest baseline, and Cockroach Kernel;
- three repetitions per class and method;
- 54 synthetic paired executions;
- one separately reported real-workflow trace from Gate 3;
- new root and process for every measured execution;
- identical inputs, information, loss event, expected executable result, and time budget.

The six classes must cover committed-only, committed-plus-uncommitted, complete declared workspace loss, partial state, conflicting/stale continuation, and clean control. Unsafe/tampered behavior belongs primarily in Run 2.

### Metrics

- provable work retained as a proportion of declared work;
- executable continuation success;
- unsafe acceptance;
- wall-clock time to verified continuation;
- scripted and human interventions;
- task restatement;
- deterministic outcome;
- storage/evidence overhead;
- residue and cleanup.

Report paired scenario results, not only aggregates. Do not predeclare a product win. If a baseline wins, preserve it and narrow the claim.

### RunPod controls

- profile locally;
- use the smallest sufficient current CPU worker unless measured CUDA need exists;
- freeze exact worker, image, price, bounded spend, paid lifetime, storage, payload, safety fuses, and teardown before creation;
- one worker only;
- synthetic/sanitized bundle plus the explicitly approved non-sensitive real-workflow trace;
- no private/client data or credentials;
- retrieve and hash evidence before deletion;
- prove exact-ID absence and empty active inventory.

### Review

- preflight: GLM for fairness/statistics/schema and Claude for harness/lifecycle semantics;
- final: GLM and Claude over one exact final packet hash;
- add AGY only for a distinct Wall-7 condition introduced by the frozen packet.

Target: `POST_S3_RUN1_GREEN` when the benchmark is fair, complete, reproducible, retrieved, torn down, and independently reviewed—not when the product merely scores highest.

## Gate 7 — RunPod Run 2: held-out failure and production-memory evidence

### Purpose

Prove fail-closed behavior on unseen variants and measure the CockroachDB memory path under a bounded realistic workload. Do not spend the campaign re-proving a deterministic function on identical bytes.

### Failure workload

Seven classes:

1. tampered receipt;
2. replayed or consumed warrant;
3. malformed canonical record;
4. unsupported schema/value;
5. quarantined candidate;
6. missing or incomplete evidence;
7. interruption between consumption and mutation.

For each class:

- freeze two known preflight vectors used only for local harness validation;
- generate three held-out variants after `EVIDENCE_CANDIDATE_COMMIT` freezes;
- hash the held-out vectors before execution;
- do not tune the implementation after seeing results;
- run one execution per held-out vector in a fresh root/database state/process.

Add seven valid held-out controls. Total measured held-out trials: 28. Separately run one five-repeat determinism probe for one representative `PROMOTE`, `REFUSE`, and `INVALID` input: 15 executions. Total measured executions: 43.

### Memory workload

Using the same frozen implementation and actual AWS/CockroachDB path, run a bounded long-horizon synthetic trajectory workload sized from local profiling and free-tier/cost constraints. Measure:

- stored trajectory/event/receipt/vector counts;
- transaction retry and duplicate behavior;
- vector-query recall on task-bound expected neighbors;
- p50/p95/p99 write and retrieval latency;
- changefeed cursor continuity;
- restart and rollback behavior;
- database and evidence growth;
- query-plan/index evidence;
- actual verified cluster topology;
- concurrency level actually exercised;
- access-control, audit, and observability evidence.

Do not call this universal scale, multi-region, or production capacity unless the actual topology and workload prove those terms.

### Safety thresholds

- false promotions: `0`;
- mutation after refusal: `0`;
- correct stable reason code: `100%`;
- representative determinism probes: `100%`;
- canonical receipt emitted: `100%`;
- valid-control continuation: `100%`;
- hidden session-state dependencies: `0`;
- trial teardown: `100%`;
- residue: `0`;
- output-schema compliance: `100%`.

Any critical failure blocks the campaign; do not average it away.

### Review

- preflight: GLM for workload/schema/held-out design and AGY for refusal, injection, egress, excessive agency, and mutation boundaries;
- final: GLM and AGY over one exact final packet hash;
- use Claude only for a distinct unresolved process/lifecycle ambiguity.

Target: `POST_S3_RUN2_GREEN`.

## Gate 8 — Evidence package

Produce:

1. one-page scorecard aligned to the five official criteria;
2. canonical claim-to-evidence manifest;
3. complete private raw evidence archive;
4. sanitized public evidence subset;
5. architectural diagram showing the real AWS, CockroachDB, agent, advisory, and deterministic-authority boundaries.

Mechanical gates:

- missing referenced artifacts: `0`;
- hash mismatches: `0`;
- displayed metrics without source receipts: `0`;
- public claims without evidence: `0`;
- contradictory metrics: `0`;
- public-package credentials/private paths/private evidence: `0`;
- replay/live ambiguity: `0`.

Remove the six-persona retrieval drill. Independent judges may review the compact packet, but internal model retrieval speed is not treated as user or competition evidence.

Target: `POST_S3_EVIDENCE_PACKAGE_GREEN`.

## Gate 9 — Exact public claim

Every clause maps:

```text
CLAIM -> METRIC -> TEST -> RECEIPT -> SHA-256 -> LIMITATION
```

Replace the vulnerable provisional claim with:

> After declared loss, Cockroach Kernel reconstructs the longest contiguous continuation among declared candidates that passes its deterministic evidence and policy checks. It refuses candidates it cannot verify.

Use this wording only if the frozen implementation and receipts directly prove `longest contiguous`. Otherwise replace it with `a continuation` and state the exact selection policy.

Required gates:

- evidence-mapped clauses: `100%`;
- unsupported clauses: `0`;
- claim/result contradictions: `0`;
- unqualified first/only/perfect/everything/safest/global-optimality claims: `0`;
- non-identical comparative inputs: `0`;
- replay described as live: `0`.

Any measured comparative claim must quote the exact scenario population and baseline. One single-operator workflow cannot support population-wide usability claims.

Final independent review:

- GLM: numerical validity, fairness, and traceability;
- AGY: overclaiming, Wall-7 boundaries, misleading replay/live language, and authority implications;
- Claude remains optional under non-authoring independence rules.

Target: `POST_S3_CLAIMS_GREEN`.

## Gate 10 — Submission-surface parity

Before public action, verify:

- public repository contains the exact release code, license, dependencies, setup/run instructions, example configuration/data, and functional demo URL;
- the AWS demo remains freely accessible through the judging period under the frozen cost/access plan;
- the sub-three-minute public video shows the actual product functioning and the CockroachDB memory layer at work;
- Devpost text names the exact CockroachDB tools and AWS services and explains their meaningful behavior;
- README, video, demo, scorecard, and Devpost claims all bind the same release commit and evidence manifest;
- no planned, replayed, or synthetic behavior is described as live production evidence;
- no public action occurs without the applicable separate release/video/submission gate.

Target: `POST_S3_SUBMISSION_PARITY_GREEN`.

## RunPod lifecycle law

For each of the two authorized future campaigns:

- no simultaneous or residual worker;
- maximum eight pre-workload creation attempts in a 45-minute launch window;
- retries only for transient creation/capacity/readiness/SSH/transfer/shape failures;
- every failed worker is deleted and proven absent before retry;
- no replacement after measured execution begins;
- exact finite price and bounded maximum spend frozen before creation;
- stop for unknown/unbounded rate, policy conflict, or billing/account-setting change;
- provider stop/terminate safety fuses required;
- evidence retrieved before deletion;
- exact-ID absence and fresh empty inventory required.

This plan does not itself authorize those paid lifecycles.

## Global stop conditions

Stop and preserve exact state on:

- S3 not fully GREEN;
- active or residual earlier worker;
- more than one paid worker;
- missing AWS demo authority or access proof;
- unknown/unbounded cost;
- provider billing/account-setting change;
- secret, credential, private/client data, or unrelated-project exposure;
- implementation, deployment, payload, runtime, or packet hash drift;
- unfair baseline inputs or tuning;
- held-out vector exposure before candidate freeze;
- missing evidence or hash mismatch;
- false promotion or mutation after refusal;
- hidden session-state dependency;
- inability to retrieve evidence or prove teardown;
- required independent judge unavailable or not GREEN.

## Human gates remaining

- Public or judge-accessible AWS deployment and its continuing cost/access envelope.
- Each bounded RunPod lifecycle after exact price and maximum spend are frozen, unless a later explicit execution prompt supplies sufficient bounded authorization.
- Public repository visibility, video publication, and Devpost submission.
- Any provider account/billing-setting change, secret transfer, or policy exception.

## Completion

The program completes only when Gates 0 through 10 are GREEN, both RunPod workers are deleted, active inventory is empty, the AWS demo is judge-accessible, the real workflow proof exists, and every public claim matches the frozen evidence.

Final marker: `CK_POST_S3_EVIDENCE_GREEN`.
