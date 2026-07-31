# EV1 Twelve-Task Aggregate Report R1

- `STATUS`: `EV1_AGGREGATE_CANDIDATE_FINAL_REVIEW_REQUIRED`
- `CAMPAIGN`: `EXTERNAL_VALIDITY_ITEM3_PROSPECTIVE_TASK_CAMPAIGN`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `BACKLOG_SHA256`: `6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5`
- `GLOBAL_PREFLIGHT_PACKET_SHA256`: `a08bb6c49a64b293488d4c0ecc0357740f7e6187e963bc438d563db574b8f0a2`
- `TASK_ORDER`: `EV1-T01_THROUGH_EV1-T12_FROZEN`
- `TASK_SUBSTITUTIONS_AFTER_RESULTS`: `0`
- `PRODUCT_CANDIDATE_CHANGES_DURING_CAMPAIGN`: `0`
- `EXTERNAL_USERS`: `0`
- `OPERATORS`: `1`

## Terminal outcome accounting

| Class | Tasks | Count | Result |
|---|---|---:|---|
| Evaluable recovery passes | T02, T03, T04, T05, T06, T09, T10, T11, T12 | 9 | 9/9 passed task-specific acceptance |
| Predeclared expected-invalid safety cases | T07, T08 | 2 | 2/2 rejected without workspace deletion or recovery |
| Infrastructure-invalid non-scoring | T01 | 1 | Recovery bytes were produced, but successor acceptance failed because of dependency-layout infrastructure; excluded from pass denominator |

The campaign result is not “12/12 passed.” T01 remains preserved as a
non-scoring infrastructure invalid. T07 and T08 are successful safety outcomes,
not successful continuation outcomes.

## Evaluable recovery metrics

- `EVALUABLE_RECOVERY_TASKS`: `9`
- `EVALUABLE_RECOVERY_PASSES`: `9`
- `DECLARED_WORK_UNITS`: `33`
- `BYTE_EXACT_USABLE_WORK_UNITS`: `33`
- `EMPTY_HISTORY_SUCCESSORS`: `9_OF_9`
- `TASK_SPECIFIC_ACCEPTANCE_PASSES`: `9_OF_9`
- `POST_LOSS_TASK_RESTATEMENT_WORDS`: `0`
- `POST_LOSS_MANUAL_INTERVENTIONS`: `0`
- `FALSE_PROMOTIONS_IN_EVALUABLE_SET`: `0`
- `FALSE_REFUSALS_IN_EVALUABLE_SET`: `0`
- `UNSAFE_MUTATIONS_IN_EVALUABLE_SET`: `0`
- `UNAUTHORIZED_PATH_ACCESSES_IN_EVALUABLE_SET`: `0`
- `PRODUCT_INVOCATION_TO_PRODUCTIVE_RESULT_MEDIAN_MS`: `108.812`
- `PRODUCT_INVOCATION_TO_PRODUCTIVE_RESULT_RANGE_MS`: `100.067_TO_164.060`
- `PRODUCT_INVOCATION_TO_ACCEPTANCE_MEDIAN_MS`: `13924.205`
- `PRODUCT_INVOCATION_TO_ACCEPTANCE_RANGE_MS`: `978.799_TO_15850.417`

The timing clocks begin immediately before product recovery invocation. They do
not include task construction, original-workspace deletion, baseline export,
baseline reconstruction, dependency cloning, operator observation, evidence
review, or teardown. They must not be described as end-to-end disaster-recovery
times.

## Safety outcomes

- T07 exercised an oversized record and closed as
  `INVALID_OVERSIZED_RECORD`. The workspace remained unchanged; deletion and
  recovery were forbidden.
- T08 exercised an unsafe symlink escape and closed as
  `INVALID_UNSAFE_SYMLINK_ESCAPE`. The target was not followed or mutated; the
  workspace remained unchanged; deletion and recovery were forbidden.
- Both safety outcomes received independent objective-evidence GREEN review.
- Both workspaces remain preserved because their frozen contracts forbid
  teardown after the expected-invalid result.

## Human and external-validity classification

- Kenneth authenticated the frozen backlog as genuine intended development work
  and recorded task-level operator observations.
- T01 contained the independently saved human edit, but T01 is infrastructure-
  invalid and non-scoring.
- T09 is model-assisted and permanently excluded from independently-human-edited
  evidence.
- The remaining evaluable tasks did not require an independent human edit.
- Therefore this campaign contains no successful independently-human-edited
  recovery task and no independent external user.
- The tasks used disposable or synthetic project roots. They were not production
  incidents or client workloads.
- The campaign ran across July 30–31, 2026. It is a twelve-task prospective
  single-operator campaign, not a seven-day field trial or multi-day production
  soak.

## Claim allowed by this evidence

> In a frozen twelve-task, single-operator disposable-workspace campaign, nine
> of nine evaluable recovery tasks restored all 33 declared work units
> byte-exactly into empty-history successors and passed their task-specific
> acceptance checks. Two separately predeclared unsafe cases were rejected
> without deletion or recovery. One additional run was infrastructure-invalid
> and excluded from the pass denominator.

## Claims not supported

- “12/12 recovery tasks passed” or an unqualified 100% success rate.
- Independent-user, customer, production, or production-scale validation.
- Seven-day dogfooding or a multi-day field trial.
- Successful independently-human-edited recovery.
- End-to-end recovery in approximately 100 ms.
- Recovery of arbitrary uncaptured bytes or recovery from no surviving
  representation.
- Elimination of ordinary backups, version control, or permission controls.

## Aggregate disposition

The task-level evidence materially improves product-readiness and controlled
workflow evidence. It does not close independent-user or production external
validity. Public claims must use the qualified denominator and limitations above.
This report is a candidate until independent GLM and AGY review the same frozen
aggregate packet hash.
