# Fresh-Context Black-Box Preflight Status R1

- `STATUS`: `BLACK_BOX_PREFLIGHT_BLOCKED`
- `UTC_CREATED`: `2026-07-28T06:01:40Z`
- `BLOCKER`: `FROZEN_CLI_NOT_SCENARIO_DRIVEN`
- `TARGET_PLAN`: `FRESH_CONTEXT_BLACK_BOX_PLAN_R2.md`
- `TARGET_PLAN_SHA256`: `4453424a60e0cb591bde3a7a6da5ceeb7bd752b8cf9dd6abba785b42c61f32cc`
- `FROZEN_PRODUCT_CANDIDATE`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `LAST_GREEN_GATE`: `HARDENING_6_RUN1_GREEN`
- `LAST_GREEN_SUPPLEMENTAL_STATUS`: `SUPPLEMENTAL_GENERALIZATION_GREEN`
- `SURFACE_PROBE`: `SURFACE_BLOCKED`
- `SURFACE_PROBE_HASH`: `5817c3af2b3a84138e66f0e2e44f937fa026e8548ed423cc837eddc50c70f75a`
- `INDEPENDENT_JUDGE`: `glm-5.2 / GREEN blocker confirmation / recusal clear`
- `HIDDEN_SEED_CREATED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`
- `BLACK_BOX_ACTOR_CALLED`: `NO`
- `PAID_RESOURCE_CREATED`: `NO`
- `PRODUCT_MUTATED`: `NO`
- `GATE6_MUTATED`: `NO`
- `GATE7_STARTED`: `NO`

## Finding

The candidate's user-facing CLI exposes only:

- `cockroach-kernel demo`, a no-input deterministic replay with output-format
  and output-root options;
- `cockroach-kernel inspect <receipt>`, a canonical receipt validator.

It does not accept a workspace, scenario, task, manifest, capsule, candidate, or
recovery input. Two different disposable workspaces produced identical demo
results and output manifests and remained unchanged. The frozen demo therefore
cannot bind or recover the R2 plan's hidden scenario workspaces.

Running 18 actor sessions would test invocation of one canned replay rather than
hidden-scenario recovery. That would violate the R2 construct and overstate the
evidence.

## Guardrail result

The operator's guardrail required direct canary, scorer, telemetry, and residue
preflight before hidden execution. The earlier surface-feasibility check failed,
so later preflight work and all hidden execution are forbidden. No attempt was
made to bypass the failure by exposing internal harnesses or changing the
candidate.

## Next allowed action

Stop. Resume only after Kenneth separately authorizes a product revision that
adds a safe, documented, scenario-driven public interface. That revision must:

1. remain deterministic and preserve local verifier authority;
2. accept an explicitly declared disposable workspace or typed recovery input;
3. enforce existing path, one-use, refusal, and no-uncaptured-byte boundaries;
4. receive a new product commit and candidate hash;
5. receive a new black-box plan revision, preflight packet, and independent
   review before any hidden seed or actor session.

## Forbidden actions

- execute any of the 18 R2 hidden sessions;
- generate the R2 hidden seed;
- claim black-box evidence or external validity;
- relabel the canned replay as scenario-driven recovery;
- alter immutable Gate 6 evidence;
- begin Gate 7 under this black-box task;
- use internal implementation harnesses as though they were the public CLI;
- mutate the product without a separate product-revision decision.
