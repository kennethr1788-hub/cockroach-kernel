# Cockroach Kernel Post-Dogfooding External-Validity Plan R2

## Status and scope

- `STATUS`: `PLANNING_ONLY_NOT_EXECUTION_EVIDENCE`
- `PARENT_GATE`: `EV1_AGGREGATE_EVIDENCE_GREEN`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `OBJECTIVE`: Improve external validity, scale evidence, and continuity evidence
  without adding product features or inflating claims.
- `PUBLIC_ACTIONS`: `FORBIDDEN`
- `PRODUCTION_DATA`: `FORBIDDEN`
- `CLIENT_DATA`: `FORBIDDEN`
- `REAL_WORKSPACE_DESTRUCTION`: `FORBIDDEN`
- `PAID_EXECUTION`: `SEPARATE_EXPLICIT_AUTHORIZATION_REQUIRED`
- `PRODUCT_MUTATION`: `FORBIDDEN_UNLESS_A_SEPARATE_REVISION_GATE_IS_OPENED`

This plan does not attempt to prove arbitrary recovery from zero surviving
information. That is impossible. It converts the limitation into a tested,
fail-closed information boundary.

## GLM review profile

- `REVIEWER`: `GLM 5.2`
- `ROUTE`: direct non-authoring `glm-zai`
- `SERVED_MODEL_VERIFICATION`: `glm-5.2`
- `FALLBACK`: disabled
- `ROLE`: advisory plan auditor only
- `TOOLS_OR_WRITE_AUTHORITY`: none
- `VERDICT`: `PLAN_SOUND`
- `BLOCKERS`: none
- `REVIEW_CLASSIFICATION`: advisory; not an execution gate or implementation
  receipt

GLM concluded that all four tests map to distinct evidence gaps and are not
ceremonial repetition. Its load-bearing corrections are incorporated below:

1. Run the information-boundary matrix before expensive testing.
2. Use a genuinely external developer for the human-edit evidence if the goal
   is independent-user validation.
3. Inspect internal receipts and write/model/egress traces in the impossible-
   recovery case, not only the final verdict.
4. Place hard cost, retry, duration, identity, and teardown controls around the
   scale and multi-region campaigns.
5. Run scale before multi-region continuity.
6. Preserve production-shaped, production, client-failover, and actual
   topology-fault claims as separate evidence classes.

## Global execution law

All phases bind the same product candidate unless a failure proves a product
defect. If a product change is required:

1. Stop the current campaign.
2. Preserve the failed evidence.
3. Open a separately authorized product-revision gate.
4. Re-run every earlier test whose behavior or claim is affected.
5. Freeze a new candidate before resuming external-validity testing.

Every campaign must freeze, before hidden or measured execution:

- candidate commit and source hashes;
- workload and task manifest;
- acceptance thresholds;
- allowed and forbidden paths;
- synthetic-data policy;
- model and tool bindings;
- cost ceiling and maximum paid lifetime;
- attempt and retry ceiling;
- stop and teardown commands;
- evidence schema;
- permitted and forbidden claims;
- independent review packet.

No result becomes GREEN from a builder summary. Failed, invalid, interrupted,
and excluded attempts remain visible and may not be pooled into a later pass.

## Ordered gates

### PDH-0 — Candidate and evidence freeze

#### Goal

Bind the current product candidate and prove that the four campaigns can run
without modifying product behavior or touching forbidden state.

#### Required work

1. Revalidate the current commit, EV1 aggregate receipt, Gate 8 evidence, and
   clean-clone path.
2. Freeze one parent manifest covering all four tests.
3. Declare shared stable reason codes and outcome classes:
   - `RECOVERED_EXACT`
   - `RECOVERED_MAXIMUM_PROVABLE_SUBSET`
   - `UNRECOVERABLE_NO_SURVIVING_REPRESENTATION`
   - `INVALID_TAMPERED_EVIDENCE`
   - `INVALID_UNSAFE_INPUT`
   - `INFRASTRUCTURE_INVALID`
4. Prove all test roots are disposable and contain no credentials, private
   memory, HOME runtime, client data, or production data.
5. Obtain an independent same-hash preflight review before PDH-1.

#### GREEN

`PDH_0_CANDIDATE_FREEZE_GREEN`

#### Kill line

Stop on candidate drift, missing evidence, private-data exposure, an outcome
class the current product cannot express without modification, or an
unbounded-cost path.

---

### PDH-1 — Captured-versus-uncaptured information boundary

#### Why first

This is inexpensive and proves the absolute honesty boundary before scale or
external-user testing. It must demonstrate that unavailable bytes are never
guessed, synthesized, temporarily written, or silently represented as
recovered.

#### Frozen matrix

| Case | Input state | Required outcome |
|---|---|---|
| B1 | Committed and captured | `RECOVERED_EXACT` |
| B2 | Modified tracked and captured | `RECOVERED_EXACT` |
| B3 | Untracked and captured | `RECOVERED_EXACT` |
| B4 | Created after final capture, then deleted | `UNRECOVERABLE_NO_SURVIVING_REPRESENTATION` |
| B5 | Partial surviving representation with unverifiable remainder | `RECOVERED_MAXIMUM_PROVABLE_SUBSET` or fail-closed refusal |
| B6 | Tampered surviving representation | `INVALID_TAMPERED_EVIDENCE` |

#### Required instrumentation

1. Freeze byte hashes for every declared recoverable input.
2. For B4, record that the missing bytes never entered any capture, Git object,
   receipt, replay, autosave, fixture, prompt, or test oracle accessible to the
   recovery process.
3. Run the verifier under its declared network-denied boundary.
4. Record all model-call counters, tool calls, file writes, output-manifest
   entries, and stable reason codes.
5. Assert for B4:
   - zero model invocations;
   - zero network egress;
   - zero writes containing a replacement for the missing file;
   - no discarded guessed candidate;
   - no recovered-content claim.
6. For B5, require the receipt to enumerate recovered and unrecoverable units
   separately. Missing bytes may not be filled from a model.
7. Repeat every case five times over frozen inputs and compare verdict,
   reasons, hashes, and custody state.

#### GREEN

- B1–B3 recover byte-exactly.
- B4 produces the explicit no-surviving-representation result without creating
  candidate bytes.
- B5 never overstates its provable subset.
- B6 is invalid and causes no destructive action.
- All repeated results are deterministic.
- Independent final review returns GREEN.

`PDH_1_INFORMATION_BOUNDARY_GREEN`

#### Claim after GREEN

Permitted:

> Bounded recovery of explicitly captured representations, with deterministic
> refusal when no surviving representation exists.

Still forbidden:

- arbitrary file recovery;
- zero-data-loss recovery;
- recovery from nothing;
- forensic disk recovery.

#### Kill line

Any guessed byte, model invocation in the verdict path, undeclared read, false
recovery, nondeterminism, or destructive action on invalid input stops the
campaign and opens a product-defect gate.

---

### PDH-2 — Independently human-saved recovery

#### Goal

Prove that a person outside the builder/operator context can create meaningful
work, lose the disposable workspace, invoke the documented recovery path, and
continue without the original conversation.

Kenneth may run one public canary, but that canary does not count as independent
user evidence. The measured trial requires a trusted external developer. A
confidentiality agreement may protect unreleased details, but the tester must
remain free to report failure and must not become an author or judge.

#### Tester packet

The tester receives only:

- a prebuilt private test package;
- a disposable repository;
- one prescribed but meaningful development objective;
- installation and execution instructions;
- the allowed-root and teardown boundary;
- an observation and consent form.

The tester does not receive:

- source architecture;
- expected result hashes;
- benchmark thresholds;
- prior campaign results;
- product roadmap;
- hidden recovery internals.

#### Trial

1. Freeze one task and its deterministic acceptance test before the tester
   begins.
2. The tester personally creates:
   - one committed change;
   - one modified tracked change;
   - one untracked saved file.
3. The tester attests that the human edit is their own and was not generated by
   the product or a model.
4. Record pre-loss hashes and passing task acceptance without disclosing
   unnecessary content.
5. Capture only the declared disposable state.
6. Terminate the original process and remove only the disposable workspace.
7. Start a new context-empty process.
8. The tester invokes the documented public path without restating the task.
9. Measure:
   - exact recovered hashes;
   - empty-history successor;
   - acceptance result;
   - recovery time;
   - restatement words;
   - manual interventions;
   - tester-reported clarity;
   - residue and teardown.
10. The tester returns only the canonical receipt, environment classification,
    outcome, and consented observation.

#### GREEN

- All three declared work classes are recovered byte-exactly.
- Acceptance passes.
- No task restatement or builder intervention is required.
- The tester confirms the result was usable.
- No undeclared state is read.
- Independent evidence review returns GREEN.

`PDH_2_EXTERNAL_HUMAN_RECOVERY_GREEN`

#### Claim after GREEN

Permitted:

> One blinded external developer successfully recovered and continued a frozen
> disposable development task.

Still forbidden:

- customer validation;
- broad user validation;
- production usage;
- population-level usability;
- independently reproduced architecture.

#### Human gate

Kenneth must select the tester and obtain consent. No model may impersonate the
tester, provide the human edit, or manufacture the observation.

#### Kill line

Stop on tester exposure to expected hashes, builder assistance after loss,
model-authored “human” work, replacement of a failed task, private-data access,
or inability to revoke and tear down the test package.

---

### PDH-3 — Production-shaped application scale

#### Goal

Measure the real application protocol under a workload large and contentious
enough to expose transaction, vector-isolation, queueing, custody, evidence-
growth, and recovery defects.

Generic database traffic may supplement the campaign, but it cannot substitute
for the application-specific trajectory workload.

#### Preflight calibration

1. Run an offline/local public canary with no paid resources.
2. Estimate row growth, evidence growth, request rate, runtime, and cost.
3. Freeze a stepped load envelope rather than blindly launching the maximum:
   - Stage A: 10 concurrent trajectories;
   - Stage B: 50;
   - Stage C: 100;
   - Stage D: 250;
   - Stage E: up to 500 only if every earlier stage remains inside the frozen
     cost, latency, error, and growth ceilings.
4. Target the largest safely affordable envelope, potentially:
   - 1–5 million trajectory events;
   - 100,000–250,000 task-bound vector records;
   - up to 10,000 recovery/verifier operations.
5. These are ceilings, not claims. The final claim uses only measured values.

#### Workload mix

- captured committed, modified, and untracked states;
- stale receipts and stale projections;
- conflicting edits;
- duplicates and replay attempts;
- unsupported and unsafe inputs;
- transaction contention and SQLSTATE `40001`;
- delayed, malformed, duplicated, and unavailable Lambda advice;
- process crash and restart;
- queue backpressure;
- ticket consumption interruption;
- cleanup under load.

#### Measurements

- completed operations and concurrency;
- throughput and p50/p95/p99/pMax;
- retry and exhausted-retry counts;
- exact recovery rate;
- false promotion, false refusal, invalid, and infrastructure-invalid counts;
- task-bound vector cross-contamination;
- queue depth and recovery;
- acknowledged-write loss;
- database, telemetry, receipt, manifest, and evidence bytes;
- process, descriptor, memory, and disk state;
- cleanup and residue;
- cost per 1,000 trajectories and recovery operations.

#### Cost and lifecycle controls

An AWS Budget alert is evidence only; it is not a teardown controller.
Execution requires:

- explicit total and hourly cost ceilings;
- reserved or maximum concurrency;
- finite operation and duration limits;
- provider-native stop/termination deadlines where available;
- a detached exact-resource-ID guard;
- one paid campaign resource at a time;
- bounded creation retries before workload start;
- no replacement after hidden/measured execution begins;
- exact billing reconciliation;
- resource inventory proving zero residual paid resources.

#### GREEN

- Every completed operation is accounted for.
- Zero false promotions and unauthorized cross-task vector results.
- Zero acknowledged-write loss.
- Retry, restart, queue, custody, and cleanup behavior satisfy frozen
  thresholds.
- No cost, growth, resource, or evidence threshold is exceeded.
- Final independent same-hash review returns GREEN.

`PDH_3_PRODUCTION_SHAPED_SCALE_GREEN`

#### Claim after GREEN

Permitted:

> Validated against a measured production-shaped scale envelope of exactly
> `<measured values>`.

Still forbidden:

- production validated;
- production traffic;
- unlimited scale;
- globally representative performance;
- customer workload.

#### Kill line

Stop on cost uncertainty, threshold breach, false verdict, cross-task memory
leak, lost acknowledged write, missing checkpoint, evidence mismatch, or
unverified teardown.

---

### PDH-4 — Multi-region continuity and extended soak

#### Goal

Separate three claims that must not be conflated:

1. multi-region configuration;
2. client-routing continuity;
3. actual database-region fault survival.

#### Topology choice

The preflight must select and label one of two evidence modes:

**Mode A — Managed configuration/client continuity**

- Disposable multi-region CockroachDB Cloud configuration.
- AWS callers in at least two regions.
- Real client-routing interruption.
- No claim of database-region survival unless the provider exposes a genuine
  region-fault test.

**Mode B — Actual disposable topology fault**

- At least five disposable CockroachDB nodes distributed `2+2+1` across three
  AWS regions so a five-replica region-survival configuration is physically
  possible.
- Same schema and application protocol as the candidate.
- AWS clients in at least two regions.
- Explicitly stop or isolate the test nodes in one region, then restore them.
- Label this as a disposable self-hosted topology test if it is not the managed
  candidate deployment.

The mode is frozen before provisioning. Evidence from the two modes may not be
pooled to imply a stronger topology than either actually tested.

#### Duration and event schedule

- Total measured duration: 12–24 hours, selected and costed at preflight.
- Baseline: at least 2 hours.
- Region or routing fault: at least 30 minutes.
- Restoration and convergence observation: at least 2 hours.
- Remaining time: steady mixed application workload.
- Five-minute canonical checkpoints.

#### Measurements

- topology and survival-goal evidence;
- acknowledged-write RPO;
- request success during fault;
- p50/p95/p99 before, during, and after fault;
- retries and exhausted retries;
- duplicate ticket consumption;
- lost, duplicated, or orphaned events;
- vector/task isolation;
- recovery verdict correctness;
- lease/range or node convergence after restoration;
- database and evidence growth;
- cost;
- residue and exact-resource teardown.

#### Frozen minimum acceptance

- RPO `0` for acknowledged application writes.
- Zero false recovery verdicts.
- Zero cross-task memory leakage.
- At least 99% successful measured application operations during the declared
  fault window, excluding explicitly preclassified client transport probes.
- Restored topology reaches the frozen convergence condition.
- p99 remains within the predeclared multiple of baseline.
- No missing checkpoint or evidence-chain break.
- All paid resources, volumes, IPs, functions, logs with retention cost, and
  test credentials are removed or returned to the predeclared retained state.

Exact latency and convergence thresholds are calibrated publicly before the
measured campaign, then frozen.

#### Cost and teardown controls

Apply all PDH-3 controls independently to every region and service. The
resource registry must include clusters, nodes, Lambda functions, queues,
object stores, logs, addresses, volumes, snapshots, and cross-region transfer.
Budget alerts do not replace exact-ID teardown guards or provider deadlines.

#### GREEN

Mode A:

`PDH_4_MULTI_REGION_CLIENT_CONTINUITY_GREEN`

Mode B:

`PDH_4_DISPOSABLE_REGION_FAULT_GREEN`

#### Claim after GREEN

Mode A permits:

> Multi-region configuration and cross-region client continuity were validated
> under the declared routing fault.

Mode B permits:

> Multi-region continuity was validated under an explicit disposable
> topology-region fault.

Still forbidden:

- production regional outage;
- CockroachDB Cloud region-failure validation when only self-hosted nodes were
  faulted;
- zero-downtime global availability;
- indefinite durability.

#### Kill line

Stop on topology mismatch, inability to prove which nodes were faulted,
acknowledged-write loss, false verdict, cross-region leakage, unbounded cost,
evidence loss, or incomplete teardown.

---

### PDH-5 — Aggregate evidence and competition-claim freeze

#### Required work

1. Preserve each campaign independently; do not pool incompatible modes.
2. Update the official-criteria scorecard with exact measured results.
3. Map every sentence of every proposed claim to:
   - source receipt;
   - file hash;
   - product commit;
   - evidence mode;
   - denominator;
   - limitation.
4. Preserve all failures, invalids, interrupted runs, canaries, and excluded
   cases.
5. Re-run the public secret/private-path scan.
6. Freeze one sanitized final evidence packet.
7. Obtain independent GLM and AGY review over the same packet hash.
8. Do not begin public release, README claims, video claims, or submission from
   this plan alone.

#### Final disposition

`PDH_EXTERNAL_VALIDITY_GREEN` requires every executed campaign to be truthfully
classified and the final same-hash independent review to return GREEN.

If a planned campaign is deliberately skipped, the aggregate may still close
as `PDH_EXTERNAL_VALIDITY_PARTIAL_GREEN`, but the corresponding limitation and
prohibited claim remain open.

## Dependency and execution order

```text
PDH-0 candidate freeze
  -> PDH-1 information boundary
  -> PDH-2 external human recovery
  -> PDH-3 production-shaped scale
  -> PDH-4 multi-region continuity
  -> PDH-5 aggregate claim freeze
```

PDH-1 is a hard dependency for every later campaign. PDH-2 is the intended
next test, but tester availability does not authorize fabricated evidence. If
the human gate remains unavailable, record `PDH_2_EXTERNAL_TESTER_BLOCKED` and
Kenneth may separately authorize proceeding to PDH-3 while preserving the
independent-user gap.

PDH-3 is a hard dependency for PDH-4 because scale and application thresholds
must be understood before paying for a multi-region topology.

## Value priority

1. `PDH-1`: highest certainty per unit cost; proves the honesty boundary.
2. `PDH-2`: highest remaining Real-World Impact value if an external tester is
   available.
3. `PDH-3`: strongest remaining Technical Implementation and Product Readiness
   evidence.
4. `PDH-4`: useful only after the earlier gates; highest cost and operational
   risk.
5. `PDH-5`: required synthesis, not new evidence.

No additional product feature is authorized or required by this plan.
