# Fresh-Context Black-Box Preflight — Product-Surface Blocker Packet R1

- `STATUS_REQUESTED`: `BLACK_BOX_PREFLIGHT_BLOCKED`
- `UTC_FROZEN`: `2026-07-28T05:58:49Z`
- `TARGET_PLAN`: `FRESH_CONTEXT_BLACK_BOX_PLAN_R2.md`
- `TARGET_PLAN_SHA256`: `4453424a60e0cb591bde3a7a6da5ceeb7bd752b8cf9dd6abba785b42c61f32cc`
- `FROZEN_PRODUCT_CANDIDATE`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `LAST_GREEN_GATE`: `HARDENING_6_RUN1_GREEN`
- `SUPPLEMENTAL_STATUS`: `SUPPLEMENTAL_GENERALIZATION_GREEN`
- `PROPOSED_BLOCKER`: `FROZEN_CLI_NOT_SCENARIO_DRIVEN`
- `HIDDEN_SEED_CREATED`: `NO`
- `BLACK_BOX_ACTOR_CALLED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`
- `PAID_RESOURCE_CREATED`: `NO`
- `RUNPOD_LIVE_INVENTORY`: `zero RUNNING; all returned entries EXITED`
- `PRODUCT_MUTATION`: `NO`
- `GATE7_EFFECT`: `NONE`

## Decision requested

Determine whether the frozen product surface can validly support the R2 plan's
18 hidden scenario executions. Confirm or reject the proposed fail-closed
decision to stop before sandbox engineering, hidden generation, and model-actor
execution.

Do not propose or authorize a product change. If a new scenario-driven public
surface is required, classify that as a separate product revision that would
invalidate the current frozen candidate and require a new plan/preflight.

## Controlling R2 requirement

R2 requires a fresh actor to operate the frozen user-facing interface against
six hidden scenario classes, including complete loss, partial/conflicting loss,
no-loss control, tamper, replay, and unsafe-path refusal. The actor cannot see
source or use internal harnesses. The candidate must therefore expose a public
way to bind a disposable scenario/workspace or its declared recovery artifacts
to the product execution.

R2 also prohibits changing the candidate after protocol freeze and requires
stopping before hidden generation when the test would become a scripted
demonstration rather than a user-facing black-box evaluation.

## Candidate identity proof

The current files match the exact candidate Git blobs:

```text
pyproject.toml
ca8d0a873ddfa1d628f54ef5ca989b88e087b967f7d366bca66d8b59249b6dbd

cockroach_kernel/cli.py
98c0dc51de474a472d49fe014910bfb7d30454a851ba390e66ebe1aeea5a9caf
```

`git merge-base --is-ancestor` returned `0` for the candidate against current
HEAD. No later product-file drift was used for this probe.

## Frozen public CLI surface

The packaged entry point is:

```toml
[project.scripts]
cockroach-kernel = "cockroach_kernel.cli:main"
```

Top-level help:

```text
usage: cockroach-kernel [-h] {demo,inspect} ...

positional arguments:
  {demo,inspect}
    demo          run the deterministic keyless replay
    inspect       validate a canonical receipt
```

Demo help:

```text
usage: cockroach-kernel demo [-h] [--explain | --json]
                             [--output-root OUTPUT_ROOT]

options:
  -h, --help            show this help message and exit
  --explain
  --json
  --output-root OUTPUT_ROOT
```

Inspect accepts one existing receipt for validation. Demo accepts only output
format and output destination. Neither command accepts a workspace, input root,
task, scenario, capsule, candidate, manifest, or recovery input.

The packaged replay's `run()` function takes no arguments and hardcodes:

```text
task_id = p9-offline-task-1
candidate_id = p9-offline-candidate-1
declared work = continue synthetic feature
requested and declared path = src/feature.py
```

## Dynamic public-fixture probe

The probe created two separate disposable workspaces:

- workspace A manifest hash:
  `8cefc8f830f5a689c4416cc20be9f70b7f5974e085926a96c8f7126fed498df6`;
- workspace B manifest hash:
  `ad9d549daa5df4f46d15d98c2bfb92ecb75c90213838f8b12fcf7ab44039919d`.

Each contained different task metadata, feature bytes, and independently saved
edit text. The probe launched the public module-equivalent entry point from each
workspace with separate output roots and a minimal temporary HOME/environment.

Observed:

```text
help exit: 0
demo help exit: 0
demo A exit: 0
demo B exit: 0
declared scenario input flags: []
workspaces distinct: true
workspaces unchanged: true
demo outputs identical: true
demo A summary hash: 1d4d5686ccadc322db1eeaa1cad0f6e1d188e10b0c2eb109ddad334948eab341
demo B summary hash: 1d4d5686ccadc322db1eeaa1cad0f6e1d188e10b0c2eb109ddad334948eab341
output A manifest hash: 9d6891d413e180acc04c15f67f912532c4a5fe0f9f0f326e729641aa99c5638e
output B manifest hash: 9d6891d413e180acc04c15f67f912532c4a5fe0f9f0f326e729641aa99c5638e
scenario binding proved: false
teardown verified: true
```

The different workspaces were neither read nor modified by the demo. The demo
produced identical canned replay evidence in both cases.

## Evidence bindings

- `fresh-context-black-box/surface_probe.py`:
  `3accc8062a2a66233ac78849f7c419419a3eef12a092b1a7e80b4009256d6ea3`;
- `fresh-context-black-box/test_surface_probe.py`:
  `e34e28cdae0758a12150c33cdc2e8deb3602c0ecba48cedf86ac820d7ef9aa31`;
- `FRESH_CONTEXT_BLACK_BOX_SURFACE_PROBE_R1.json`:
  `855d09f8a77c30d5ac4085f2f66db28f9960a5b8815dda31b3379941a38dbd55`;
- `FRESH_CONTEXT_BLACK_BOX_SURFACE_TEST_R1.txt`:
  `b62c4d3d1b289901fc7df641122aabe571707cc13da2c89d894cd595904571f0`;
- canonical probe semantic hash:
  `5817c3af2b3a84138e66f0e2e44f937fa026e8548ed423cc837eddc50c70f75a`.

Unit result:

```text
2 tests / PASS
```

The standalone probe returned exit `2` by design for `SURFACE_BLOCKED`. Both
internal CLI demo runs returned exit `0`.

## Proposed fail-closed conclusion

The candidate demonstrates a deterministic replay, but it does not expose a
user-facing scenario-driven recovery surface. Running 18 LLM sessions against
this CLI would measure whether models can invoke the same canned demo, not
whether they can recover six hidden workspaces. That would be construct-invalid
and would manufacture stronger evidence than the product surface supports.

Proposed status:

```text
BLACK_BOX_PREFLIGHT_BLOCKED
BLOCKER: FROZEN_CLI_NOT_SCENARIO_DRIVEN
HIDDEN_EXECUTIONS: 0
```

The R2 guardrail therefore requires stopping before:

- scenario generator and hidden seed;
- sandbox/canary implementation beyond this public surface probe;
- model-route authorization;
- any of the 18 actor sessions;
- any claim based on black-box execution.

## Resume condition

Resume requires a separately authorized product revision that exposes a safe,
documented, scenario-driven public interface while preserving deterministic
authority and all existing safety boundaries. That would be a new frozen
candidate, a new black-box plan revision, new preflight hashes, and a new
independent review. The current candidate cannot be relabeled as scenario-driven.
