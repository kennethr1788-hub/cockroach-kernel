# Hardening Gate 4 — Frozen Comparative Baseline Protocol R1

## Control fields

- `GATE`: `HARDENING_RUN_GATE_4_BASELINE_PROTOCOL`
- `PARENT_GATE`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `TARGET`: `HARDENING_4_BASELINE_PROTOCOL_GREEN`
- `PROTOCOL_REVISION`: `R1`
- `CAMPAIGN_CONSUMER`: `HARDENING_6_RUN1`
- `METHODS`: `ORDINARY_GIT`, `GIT_PLUS_RESTIC_0_19_0`, `PRODUCT`
- `SCENARIO_CLASSES`: `6`
- `REPETITIONS_PER_CLASS_METHOD`: `3`
- `MEASURED_EXECUTIONS`: `54`
- `RECOVERY_TIME_BUDGET_SECONDS`: `180`
- `NETWORK_IN_COMPARATIVE_TRIALS`: forbidden
- `PAID_ACCOUNT_OR_PRIVATE_CREDENTIAL`: forbidden
- `ROOT_PRIVILEGE`: forbidden
- `BASELINE_TUNING_AFTER_FREEZE`: forbidden
- `PRODUCT_TUNING_AFTER_RESULTS`: forbidden
- `EXPECTED_WINNER`: none
- `HUMAN_GATE`: none
- `RUNPOD_ACTION_IN_GATE_4`: none

## Purpose and kill line

This protocol measures how much declared work each method can restore and
whether the resulting successor can continue under a common executable
contract. It does not establish general usability, market preference,
production scale, off-site disaster recovery, or global superiority.

Kill the comparative campaign before launch if any method receives different
source bytes, a different event sequence, a different declared loss, a longer
recovery budget, undisclosed operator information, a method-specific success
test, post-result tuning, or shared hidden state. Kill the protocol if a
conventional tool is scored as failing a policy/trajectory capability it does
not claim.

## Frozen methods

### M1 — ordinary Git reference

This is a deliberately ordinary but durable Git workflow, not a local-only
`.git` strawman.

- A fresh Git repository is initialized inside each workspace.
- A fresh bare remote is initialized under that trial’s method custody root,
  outside the disposable workspace and outside the declared loss target.
- Initial committed state and every scenario-defined explicit commit are
  pushed to that remote immediately after the commit completes.
- The harness never auto-adds, auto-commits, stashes, patches, bundles, or
  copies uncommitted/untracked work for Git.
- The bare remote retains every pushed commit for the trial.
- Recovery runs `git fsck --full --strict` on the bare remote, clones with
  `--no-local` into a new empty successor, and checks out the exact frozen
  remote commit SHA.
- Git’s capture/push time, storage bytes, command count, and recovery time are
  recorded.

Committed and pushed bytes are a Git-supported recovery surface. Uncommitted or
untracked byte recovery is `UNSUPPORTED_BY_METHOD`, not a Git command failure.
If a scenario’s executable continuation requires unsupported bytes, the common
executable outcome may still be false; that is reported separately from method
failure.

### M2 — strongest qualified conventional baseline: Git plus Restic 0.19.0

M2 receives the same Git workflow as M1 plus a best-case Restic snapshot at
every frozen completed checkpoint.

#### Version and runtime

- Restic version is exactly `0.19.0`.
- Gate 5 must freeze exact official Darwin arm64 and Linux worker binary
  provenance, SHA-256, size, executable mode, and BSD 2-Clause license notice.
- The campaign must not use a package-manager-floating version or `latest`.
- All Restic commands set `--no-cache`; no global configuration or HOME cache
  is permitted.

#### Storage and permissions

For each M2 trial:

```text
trial/
  workspace/                 # disposable loss target
  successor/                 # absent until recovery
  custody/                   # mode 0700, survives workspace loss
    git-remote.git/           # same durable Git reference as M1
    restic-repository/        # local Restic repository
    restic-password           # mode 0600, ephemeral synthetic secret
    events/                   # checkpoint and command receipts
  temp-home/                  # isolated HOME for subprocesses
```

- The repository is local; no S3, SSH, rclone, cloud, account, socket, or
  network backend is allowed.
- The password is generated from the OS CSPRNG inside the trial after launch,
  never transferred, printed, logged, committed, or included in evidence.
- Evidence records only generation success, file mode, and absence of secret
  exposure—not the password bytes or a reversible representation.
- `RESTIC_PASSWORD_FILE` points to the trial-local file.
- The repository and password survive only because they are outside the
  declared workspace loss target. The product receives an equivalent
  outside-workspace custody class.
- Every completed snapshot is retained through scoring; no `forget`, `prune`,
  rewrite, or retention deletion occurs before teardown.

#### Cadence and retained state

The scenario generator emits a finite ordered event stream. Four possible
checkpoint labels exist:

```text
BASE_COMMITTED
AGENT_PROGRESS_SAVED
HUMAN_EDIT_SAVED
FINAL_PRELOSS
```

Only labels present in a scenario are emitted. At each emitted label, all file
writes and explicit Git operations finish and the workspace is quiescent. The
same canonical event packet is then offered to all three adapters. M2 runs and
fully completes a snapshot before the next event or the loss event begins.

M2 backs up the entire relative `workspace` directory, including `.git`,
uncommitted tracked files, and untracked files. It uses no exclusions except
method-generated paths are already outside `workspace`. Symlinks, absolute
paths, device files, sockets, and paths escaping the generated trial root are
forbidden by the scenario schema rather than silently excluded.

Each capture uses a deterministic host label and tags containing the scenario,
repetition, and checkpoint ID. The exact snapshot ID returned by the successful
capture is parsed from machine-readable output and hash-bound into the
checkpoint receipt. The harness never selects `latest` during recovery.

The capture transaction is valid only if:

1. Restic exits zero;
2. an exact snapshot ID is present;
3. `restic snapshots --json` contains that ID with the expected path/tags;
4. the captured source-manifest hash equals the event’s workspace-manifest
   hash;
5. the repository integrity command frozen by Gate 5 succeeds.

Capture and integrity-check latency are recorded as **pre-loss capture
overhead**, not hidden inside recovery latency.

#### Recovery procedure

1. Verify the successor path does not exist and is under the current trial.
2. Verify the selected snapshot ID is exactly the snapshot bound to the last
   successfully completed checkpoint permitted by the scenario.
3. Run the frozen repository-integrity command.
4. Restore the exact snapshot’s `workspace` subtree into a new empty successor.
5. Never restore in place and never use `--delete`.
6. Recompute the canonical file manifest, declared work-unit hashes, and Git
   status from the successor.
7. Run the identical executable success command used for M1 and M3.
8. Record command results, elapsed monotonic time, retained units, storage,
   residue, and teardown.

The full-data integrity command may be run before loss as capture validation and
again outside the timed recovery interval for evidence integrity. The timed
recovery interval includes the exact-snapshot repository check required by the
frozen harness, restore, manifest verification, and executable success test.

### M3 — product

Gate 5 must freeze one exact product adapter and evidence-candidate commit.
Within this protocol:

- the product receives the same canonical source workspace and event packets;
- its persistent custody is outside the disposable workspace but inside the
  trial root, matching M1/M2’s survival class;
- no live AWS, public endpoint, private credential, model call, prior session,
  HOME state, or undeclared network is available during the paired campaign;
- any local CockroachDB/runtime component is version/hash frozen and receives a
  fresh trial namespace or fresh database state;
- the deterministic verifier remains the only promotion/refusal authority;
- the adapter may persist declared task/trajectory records only from the common
  event packets; it may not read M1/M2 repositories or scoring keys;
- recovery starts in a new process with an empty successor and no conversation
  history;
- product capture/evidence cost and recovery cost are separately measured.

Gate 2 and Gate 3 are the live AWS/CockroachDB evidence surfaces. Gate 6 is a
reproducible local paired comparison; its local configuration must be disclosed
as a limitation and must not be described as live cloud evidence.

## Common trial construction

### Canonical source and pairing

For each `(scenario_class, repetition)` pair, the generator produces one
canonical source bundle from a frozen seed. The bundle contains:

- relative POSIX file paths and SHA-256 content hashes;
- file modes restricted to regular non-executable or declared executable
  files;
- ordered edit operations;
- ordered checkpoint events;
- explicit Git commit boundaries;
- declared work units and dependency edges;
- the declared loss operation;
- the expected post-recovery file manifest where a unique safe continuation
  exists;
- one executable success command and expected exit/result hash;
- a public task contract available equally to every method;
- policy applicability flags and expected safe behavior.

The canonical source bundle is materialized independently into three fresh
method roots. Before method-specific capture begins, all three source manifests
must be byte-identical. Method custody data is excluded from that comparison
because it is produced by each method after receiving the same events.

Seeds, generators, source bundles, scenario order, and expected results freeze
at Gate 5 before any measured result. The three methods for a pair run in a
deterministically rotated order so fixed thermal/cache/order effects do not
always favor one method. No method shares a cache, repository, database,
process, or filesystem root with another.

### Equal information contract

Every method receives:

1. the same public task contract;
2. the same initial workspace bytes;
3. the same ordered edit/checkpoint packets as they occur;
4. the same explicit Git commit events;
5. the same declared loss receipt at recovery start;
6. the same executable success command;
7. the same 180-second recovery budget;
8. its own pre-loss artifacts and no other method’s artifacts.

No method receives the expected manifest, hidden score key, another method’s
output, a human task restatement, or post-loss help. The scorer—not any method
adapter—holds expected hashes and applies the common test.

Method-native configuration is allowed only when fully frozen here or at Gate
5. Ordinary Git gets no automatic commit. Restic gets a completed snapshot at
every common checkpoint. The product gets no event that Restic did not also get
and no recovery hint beyond the declared loss packet.

### Environment isolation

Every execution uses a new root and a new harness process. Subprocesses receive:

```text
HOME=<trial>/temp-home
GIT_CONFIG_NOSYSTEM=1
GIT_CONFIG_GLOBAL=/dev/null
GIT_TERMINAL_PROMPT=0
LANG=C
LC_ALL=C
TZ=UTC
```

Any cache/config variable used by the frozen tools must point under the trial
root. No inherited AWS, CockroachDB, Git credential helper, SSH agent, browser,
cloud, model, or user-level configuration is allowed. The network-deny method
for the Linux worker is frozen and proven at Gate 5. A forbidden egress attempt
invalidates the trial and blocks the campaign.

## Frozen scenario classes

Each class has three seeded repetitions with varied filenames, content, edit
order, and dependency graph but the same construct.

### C1 — committed-only

All required work units are committed and pushed before loss. The entire
workspace is deleted. The unique expected continuation is the committed state.
This is the positive control for Git’s core recovery contract.

### C2 — committed plus uncommitted

The base is committed and pushed. Later required tracked edits and at least one
required untracked file are saved but not committed. The final checkpoint
completes before full workspace deletion. The executable test requires both
committed and uncommitted units.

Git’s inability to retain those uncommitted/untracked units is classified as
unsupported retention; any resulting executable-test miss is still reported.

### C3 — complete declared workspace loss

The scenario contains multiple dependent saved edits across the common
checkpoint stream. The declared workspace, including its local Git metadata,
is deleted. External method custody survives. The unique expected continuation
is the last completed safe checkpoint.

### C4 — partial state loss

A frozen subset of declared paths is removed or replaced with earlier bytes;
the loss receipt names those operations. The original workspace is then sealed
and every method must produce a fresh successor rather than repairing in place.
The expected continuation is the last completed safe checkpoint.

### C5 — conflicting or stale continuation

The common stream contains two declared candidate states: one is newer by event
order but fails a frozen dependency/policy constraint; the other is the last
safe executable continuation. Conventional methods apply only their disclosed
selection rule: M1 recovers the exact pushed commit; M2 restores the exact last
completed snapshot selected by its checkpoint rule. They are not expected to
infer intent, policy, or quorum.

Content recovery and executable continuation are scored for all methods.
Trajectory/policy adjudication is `UNSUPPORTED_BY_METHOD` for M1/M2 and is
scored only for M3. A conventional method is never labeled unsafe merely for
lacking an adjudicator; unsafe acceptance requires an actual mutation or
affirmative safe/promotion claim contrary to the frozen contract.

### C6 — clean control

No loss operation occurs. The workspace remains byte-identical to the last
checkpoint. The correct common outcome is no destructive change and a passing
executable test. Methods may return `NO_ACTION` or produce a separate successor;
either is acceptable if the original is untouched and the common test passes.
This detects recovery routines that mutate healthy state.

## Loss and recovery timing

The harness records capture overhead separately. The 180-second recovery clock
starts immediately before the adapter receives the declared loss receipt and
ends only after:

1. the adapter has returned;
2. the successor/no-action target has been selected;
3. canonical manifest scoring has completed;
4. the common executable success command has completed;
5. the final canonical trial receipt has been fsynced.

Timeout is an observed failure for a method that claims the attempted core
operation. It is not converted into `UNSUPPORTED`. Setup before the common
event stream and teardown after the final receipt are measured separately.

## Outcome taxonomy

Method status and construct scores are separate.

### Method operation status

- `SUCCESS`: claimed capture/recovery operation completed and produced a target.
- `NO_ACTION`: clean-control no-op with the original untouched.
- `PARTIAL`: a target was produced with some but not all declared units.
- `UNSUPPORTED_BY_METHOD`: capability is outside the method’s documented
  contract; not counted as a command failure.
- `FAILURE`: the method claims the operation but command, integrity, selection,
  or restore failed.
- `TIMEOUT`: the claimed operation exceeded 180 seconds.
- `INVALID_TRIAL`: common harness/pairing/isolation evidence failed; rerun is
  forbidden without a new packet and independent review.

### Common construct scores

- `declared_work_units_total`
- `declared_work_units_retained`
- `provable_work_retention_ratio`
- `committed_units_retained`
- `uncommitted_units_retained`
- `untracked_units_retained`
- `manifest_exact_match`
- `executable_continuation_pass`
- `wall_clock_recovery_ms`
- `capture_overhead_ms`
- `scripted_command_count`
- `human_intervention_count`
- `task_restatement_required`
- `original_workspace_mutated_after_loss`
- `unsafe_acceptance`
- `deterministic_outcome`
- `storage_bytes_pre_loss`
- `evidence_bytes`
- `residue_bytes_after_teardown`
- `cleanup_pass`

### Method-specific constructs

- Git: exact pushed commit, object/connectivity check, tracked content.
- Restic: exact snapshot ID, repository integrity, restored snapshot bytes.
- Product: candidate/evidence linkage, deterministic promotion/refusal, stable
  reason code, one-use behavior, and no mutation after refusal.

Method-specific constructs are shown but never averaged into a cross-method
score. No single composite “winner score” is permitted.

## Canonical receipt schema

Every measured execution emits one canonical JSON object with sorted keys,
UTF-8, no insignificant whitespace, SHA-256 over exact bytes, and these fields:

```text
schema_version
campaign_id
protocol_sha256
candidate_commit
scenario_class
scenario_seed_hash
repetition
method
execution_order
source_manifest_sha256
event_stream_sha256
loss_receipt_sha256
allowed_information_sha256
tool_versions
tool_binary_sha256
method_configuration_sha256
capture_checkpoint_receipts
selected_recovery_artifact_id
operation_status
unsupported_capabilities
declared_work_units_total
declared_work_units_retained
retained_work_unit_ids
lost_work_unit_ids
committed_units_retained
uncommitted_units_retained
untracked_units_retained
manifest_exact_match
executable_command_sha256
executable_exit_status
executable_result_sha256
executable_continuation_pass
capture_overhead_ms
wall_clock_recovery_ms
setup_ms
teardown_ms
scripted_command_count
human_intervention_count
task_restatement_required
unsafe_acceptance
original_workspace_mutated_after_loss
deterministic_outcome
storage_bytes_pre_loss
evidence_bytes
residue_bytes_after_teardown
cleanup_pass
command_receipt_hashes
limitations
receipt_sha256
```

Secrets, absolute host paths, raw environment dumps, provider credentials, and
expected hidden scoring keys are forbidden from receipts.

## Statistics and reporting

- The unit of pairing is `(scenario_class, repetition)`.
- Publish all 54 execution receipts and a paired table; never only aggregates.
- For binary outcomes, report exact numerator/denominator by method and class.
- For retention, report paired raw ratios, median, minimum, and maximum.
- For time and storage, report raw values and median by method/class; p95 is not
  reported for three observations.
- Report paired method differences but no p-values, confidence claims, or
  population inference from `n=3`.
- Failed, partial, unsupported, timeout, and invalid-trial counts remain visible.
- An invalid common trial blocks the campaign rather than being silently
  dropped or replaced.
- Gate 3’s single-operator workflow is displayed separately and never pooled
  with the 54 synthetic executions.
- A Restic or Git win is preserved. Public comparative wording must quote the
  exact methods, six classes, three repetitions, candidate commit, and
  limitations.

## Determinism

The scenario generator and scorer must reproduce identical source, event,
loss, allowed-information, and expected-result hashes from a frozen seed.
Method storage bytes may be nondeterministic because of timestamps,
encryption, or native metadata; determinism therefore compares semantic output:

```text
operation_status
retained_work_unit_ids
manifest_exact_match
executable_continuation_pass
unsafe_acceptance
method-specific verdict/reason where applicable
```

The Run 1 three repetitions are not duplicate-byte determinism probes. A
separate frozen local preflight repeats representative inputs before campaign
launch and must pass the semantic comparison.

## Teardown and residue

After final receipt custody is proven, each trial removes only its explicit
generated root. Before removal, record process, socket, mount, child-process,
and path inventory. After removal, verify:

- workspace, successor, custody, repository, password, bare remote, temp HOME,
  caches, sockets, and child processes are absent;
- no path outside the generated trial root changed;
- no network, provider, HOME, credential, Qdrant, StateV2, launchd, cron,
  client/private data, or unrelated repository was touched.

A process leak, secret exposure, cross-trial residue, or undeclared path change
is a critical campaign blocker.

## Construct validity and bias disclosure

### What the experiment can support

- byte/work-unit retention under the six declared synthetic loss constructs;
- executable continuation under one frozen small-workspace test contract;
- relative command/time/storage overhead inside one worker environment;
- product refusal/trajectory behavior only where that behavior is applicable;
- reproducibility of the exact frozen harness and candidate.

### What it cannot support

- all developer workflows, repository sizes, operating systems, backup media,
  cloud failures, hardware loss, or attacker models;
- general user preference, cognitive load, or time saved in the population;
- production capacity, multi-region resilience, off-site disaster recovery, or
  long-term retention;
- a claim that Git, Restic, Kopia, Borg, Time Machine, or other products are
  generally inferior;
- a claim that restored bytes prove correct developer intent;
- statistical significance or population generalization.

### Experimenter bias controls

- baseline and product interfaces freeze before measured evidence;
- M2 receives every common completed checkpoint, the most favorable disclosed
  cadence possible under this event-driven experiment;
- the scorer is method-neutral and holds hidden expected hashes;
- order rotates deterministically;
- all raw results and losses are preserved;
- no behaviorally relevant repair follows a measured result;
- independent GLM and Claude reviewers inspect one exact packet before Gate 4
  can close.

### Remaining bias and missing data

- The product team authored the scenarios and success rules.
- Selecting Restic rather than Kopia/Borg avoids a multi-baseline campaign and
  may omit a tool that performs better on some workloads.
- Completed pre-loss checkpoints favor snapshot tools; interruption during
  capture is deferred to the held-out failure campaign.
- Local storage omits real backup-network latency and off-site durability.
- Small synthetic fixtures may overstate absolute speed and understate storage
  pressure.
- The product’s local comparative mode is not its live AWS deployment.
- There is no public-user sample; Gate 3 is one operator trace.

These limitations are mandatory in the Gate 6 report and any public claim.

## Gate 5 obligations before execution

Gate 4 freezes design, not a runnable benchmark. Gate 5 must bind:

1. exact scenario generator and scorer source;
2. all six scenario schemas and seeds;
3. method adapter source and command contracts;
4. exact Git and Restic binary provenance/hashes/licenses;
5. product candidate commit and local runtime/database mode;
6. network-deny and environment-isolation proof;
7. capture/recovery timeout enforcement;
8. canonical receipt generation and validation;
9. local paired smoke and semantic determinism proof;
10. dependency/license manifest and RunPod payload scans.

Any change to cadence, allowed information, scenario meaning, success rules,
tool version, method selection, or scoring after Gate 4 requires a new protocol
revision and full Gate 4 judge rerun.

## Gate 4 acceptance

`HARDENING_4_BASELINE_PROTOCOL_GREEN` is allowed only when:

- this protocol and the research receipt are frozen and hash-bound;
- GLM independently returns GREEN for fairness, statistics, schema, and
  construct validity over the exact packet hash;
- Claude Opus 4.8 independently returns GREEN for harness/lifecycle semantics
  and baseline comparability over the same exact packet hash;
- both judges remain non-authoring and no packet bytes change afterward;
- repository state, packet hash, judge receipts, and `RESUME_STATE.md` agree.

Gate 4 GREEN does not claim a benchmark ran, a baseline or product won, Gate 5
is complete, a RunPod worker was created, or any public claim is supported.

