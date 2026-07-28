# Hardening Gate 6 — Execution Plan R2

- `TARGET_GATE`: `HARDENING_6_RUN1_GREEN`
- `EXECUTION_REVISION`: `R2`
- `PARENT_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `CAMPAIGN_ID`: `ck-gate6-20260727-run1-r2`
- `MEASURED_EXECUTIONS`: `54`
- `PAIRED_GROUPS`: `18`
- `RUNPOD_WORKERS`: `one successful measured worker; at most eight pre-upload creation attempts`
- `AGY_REQUIRED`: `false`

## Use, acceptance, and kill line

The campaign measures the frozen candidate against ordinary Git and Git plus
Restic under six declared synthetic loss constructs. It closes only if all 54
canonical receipts, all 18 equal-information pairs, raw aggregation, network
denial, custody, teardown, and same-hash independent reviews pass. A favorable
product score is not an acceptance condition.

Kill before measurement on candidate/contract/tool/payload drift, unequal pair
inputs or budget, unavailable unprivileged network denial, unknown price,
unbounded exposure, or a non-green required preflight judge. Kill during the
campaign on an invalid row or receipt, false promotion, unsafe acceptance,
mutation after loss/refusal, nondeterminism, residue, evidence-chain failure,
or inability to guarantee worker deletion.

## Frozen order

`HARDENING_GATE6_EXECUTION_MANIFEST_R2.json` contains every
`(scenario_class, repetition, method)` tuple exactly once. For each scenario,
the method order is the `scenario_index mod 3` rotation implemented and judged
at Gate 5. The same rotation is used for all three repetitions of a class.

Every row executes in a fresh process and trial root. The common candidate
harness emits the canonical receipt. Gate 6 orchestration validates but never
rewrites that receipt, then fsyncs a hash-chained checkpoint before advancing.

## Runtime and isolation

The generic CPU worker is the exact immutable image named in
`HARDENING_GATE6_LINUX_TOOL_PROVENANCE_R2.json`. Two vCPU and 4 GiB is
sufficient: the 18-execution local profile completed in 91.13 seconds with
98,598,912-byte maximum RSS. The 54-run estimate is approximately 274 seconds;
the six-hour workload ceiling is a fail-safe, not an expected duration.

Before measurement, the worker must:

1. match the reviewed CPU/RAM/image/disk/zero-volume/rate envelope;
2. verify the payload hash before extraction;
3. install only the hash-bound Ubuntu Git package already inside the payload;
4. match the frozen Git, Python, Restic, and product versions and byte hashes;
5. create a dedicated host-unprivileged `gate6` user;
6. prove `unshare --user --map-root-user --net --mount-proc` works for that
   user and blocks a forbidden network probe;
7. complete a non-measured canonical smoke in a fresh root;
8. prove the detached local exact-ID lifecycle guard is advancing.

No credential enters the payload or measured environment. Every measured
child receives only the frozen PATH and Git/Restic selectors. Its own trial
environment further reduces this to trial-local HOME and fixed locale/timezone
variables.

## Evidence and reporting

The runner preserves 54 raw canonical receipts, the 54-event checkpoint chain,
18 paired reports, per-method/class raw statistics, baseline wins/ties/losses,
unsupported and unfavorable outcomes, actual canonical receipt byte sizes,
runtime/tool evidence, and a complete file/hash manifest. It reports medians,
minima, maxima, and exact numerators/denominators without p-values or
population inference.

The canonical candidate's `evidence_bytes` field is zero because it is emitted
before the receipt file exists. Gate 6 does not rewrite it. The orchestration
separately measures and reports actual canonical receipt bytes; this limitation
is mandatory in the final packet.

The Gate 3 operator trace remains a separate hash-bound reference and is never
pooled with the 54 synthetic executions.

## Wall-7 decision

`AGY_REQUIRED=false`. The measured process performs no model call, prompt or
untrusted-content ingestion, memory write, agent dispatch, tool choice, or
external egress. GLM and Claude are out-of-band, non-authoring reviewers of a
sanitized frozen packet. This introduces no distinct Wall-7 mechanism beyond
the judge boundary already governed by packet hashing and deny-all authority.

## Required judges

Before worker creation and again after teardown, the exact same byte-complete
packet and canonical hash go to:

1. GLM for fairness, pairing, statistics, schema, and numerical completeness;
2. Claude Opus 4.8 through `claude-judge` for process isolation, lifecycle,
   evidence custody, teardown, and candidate immutability.

Both are non-authoring. The builder never self-approves.
