# EV1 Prospective Genuine-Use Protocol R1

## Status

- `STATUS`: `R2_HUMAN_CONFIRMATION_GREEN; MECHANICAL_AND_JUDGE_PREFLIGHT_REQUIRED`
- `PARENT_GATE`: `LIVE_CONTINUITY_EVIDENCE_GREEN`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `OFFICIAL_RULES_URL`: `https://cockroachdb-ai.devpost.com/rules`
- `LIVE_RULES_RECHECK`: `2026-07-30; deadline observed 2026-08-18 17:00 EDT`
- `MEASURED_TASKS_STARTED`: `0`
- `MEASURED_CLOCK_STARTED`: `FALSE`
- `PUBLIC_CLAIMS_CHANGED`: `FALSE`
- `BACKLOG_SHA256`: `34ffed70e3d52cde2e94e5f3b66dd96cdac1f2aa7de757b11bf6580bb5e536e4`
- `HUMAN_CONFIRMATION_RECEIVED_UTC`: `2026-07-30T13:35:47Z`
- `R1_PREFLIGHT_RESULT`: `BLOCKED_BEFORE_MEASUREMENT_OR_JUDGING`
- `R2_BACKLOG_CANDIDATE_SHA256`: `6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5`
- `R2_HUMAN_CONFIRMATION_RECEIVED_UTC`: `2026-07-30T13:47:28Z`
- `R2_BREW_LEDGER_EXPORT_MANIFEST_SHA256`: `d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706`

This protocol operationalizes EV1 from the independently reviewed
external-validity plan. It is not genuine-use evidence. Task execution remains
forbidden until the mechanical canaries and same-hash GLM 5.2 and AGY preflight
are GREEN.

## Hypothesis

For genuine development work performed in disposable project-scoped workspaces,
the frozen product can preserve declared trajectory and enable a fresh process
to continue useful work without Kenneth restating the task.

## Human authenticity gate

Before task 1, Kenneth must explicitly confirm for every backlog item:

1. the task was genuinely intended independent of this campaign;
2. the stated objective and acceptance test are accurate;
3. the source contains no client, production, credential, HOME-runtime, live
   memory, Qdrant, StateV2, launchd, or restricted third-party data;
4. a disposable clone or generated root may be created and destroyed; and
5. the task order must remain fixed after the first outcome becomes knowable.

A model, prior conversation, inferred backlog, synthetic benchmark, or task
invented solely for EV1 cannot close this gate.

## Sample and calendar

- duration: seven calendar days beginning at the first measured task's UTC start;
- ordered backlog: 12 human-confirmed candidate tasks;
- minimum evaluable sample: 8;
- target completed sample: 8–12;
- project structures: at least one small single-package, one medium multi-module,
  and one mixed-language or monorepo task, with at least three total structures;
- state diversity: at least two tasks with committed, uncommitted, and untracked
  work;
- human-edit diversity: at least two tasks with an independently saved human
  edit;
- refusal diversity: at least two predeclared disposable refusal or invalid
  conditions, natural when possible and never retrofitted after outcomes.

If fewer than eight tasks remain evaluable after seven days, the result is
`INSUFFICIENT_GENUINE_USE_SAMPLE`. The duration, minimum, and thresholds cannot
be relaxed after task 1 starts.

## Inclusion criteria

A task is eligible only when all are true:

- Kenneth confirms it is genuine intended work;
- its objective and deterministic acceptance command are frozen before work;
- the acceptance command can run inside a disposable root without private
  credentials, paid services, or undeclared network access;
- the task can be executed without changing the frozen product candidate;
- source and generated state are synthetic, public/permissively licensed, or
  Kenneth-owned non-client material;
- deletion is limited to the exact generated disposable root; and
- the task is small enough to complete and measure within the seven-day window.

## Exclusion criteria

Exclude and preserve the reason for any task requiring:

- client, production, credential, or private-memory data;
- HOME runtime, live system services, unrelated repository mutation, or public
  release actions;
- a product-candidate, verifier, record-schema, scorer, threshold, or test-
  interface change;
- paid infrastructure or external account access not separately authorized;
- a nondeterministic or subjective acceptance test; or
- replacement after the task's result becomes knowable.

## Per-task procedure

1. Freeze task objective, project class, inclusion evidence, source commit,
   acceptance command, expected state mix, human-edit flag, and refusal flag.
2. Create a generated project-local disposable root from the declared source.
3. Record initial tree, Git state, tool versions, and baseline acceptance result.
4. Perform genuine work normally; do not optimize behavior for this campaign.
5. Kenneth explicitly declares the state permitted for capture.
6. Capture the product receipt, representation hashes, trajectory, and task
   contract.
7. Verify the kill target resolves strictly inside the generated root.
8. Destroy only that disposable workspace through the reviewed kill path.
9. Start a fresh OS process with no original conversation or manually supplied
   task brief.
10. Invoke the frozen continuation interface.
11. Run the predeclared acceptance command without source edits.
12. Record outcome, timings, restatement words, interventions, work units,
   verdicts, residue, unauthorized accesses, and all receipt hashes.
13. Kenneth records one immediate qualitative note and one Git/backup
   counterfactual note; both remain labeled operator assessment and excluded
   from numeric GREEN thresholds.
14. Teardown the generated root and verify no task child, socket, temporary
   root, or undeclared residue remains.

## Measurements

Each task receipt must record:

- task ID, frozen backlog hash, product commit, source commit, and project class;
- declared work units before loss and usable work units after continuation;
- invocation-to-productive-continuation monotonic duration;
- invocation-to-acceptance-pass monotonic duration;
- post-loss task-restatement word count;
- manual intervention count and monotonic duration;
- committed, uncommitted, untracked, and human-edit presence;
- expected and observed verdict plus stable reason code;
- false-promotion, false-refusal, invalid, and unsafe-mutation counts;
- acceptance command, exit status, and output hash;
- unauthorized-path access count, residue bytes, and teardown verdict;
- operator qualitative note and Git/backup counterfactual, explicitly non-scoring;
- receipt hash and prior task-receipt hash.

## Acceptance threshold

`GENUINE_USE_EVIDENCE_GREEN` requires:

- at least 8 evaluable genuine tasks;
- zero false promotions or unsafe mutations;
- zero access outside generated disposable roots;
- at least 80 percent of evaluable tasks pass their frozen acceptance command;
- median productive-continuation time no greater than 300 seconds;
- median post-loss task-restatement count equal to zero words;
- all cleanup and residue checks pass; and
- every failure, exclusion, and intervention remains in the final packet.

## Stop conditions

Stop EV1 immediately on product-candidate drift, undeclared private data,
credential exposure, mutation outside the generated root, unsafe action, false
promotion, loss of evidence, post-outcome retuning, unbounded cost, or teardown
failure.

## Gate sequence

1. Kenneth completes and confirms all 12 backlog rows. `R2_COMPLETE`
2. Freeze the ordered backlog and its SHA-256. `R2_COMPLETE; BYTE_IDENTICAL`
3. Build a sanitized EV1 execution packet containing this protocol and the
   confirmed backlog, with no private paths or task content beyond what is
   required for judging.
4. Run mechanical canaries for scorer, timing, receipt chaining, kill-target
   containment, fresh-process isolation, residue scanning, and failure capture.
5. Obtain same-hash GLM 5.2 and AGY GREEN preflight.
6. Begin task 1 and the seven-day measured clock.

EV3, hidden-input generation, Gate 9, public claims, release, video, and
submission remain outside this draft.
