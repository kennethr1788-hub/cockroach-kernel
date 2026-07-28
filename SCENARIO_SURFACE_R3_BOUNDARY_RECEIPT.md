# Scenario Surface R3 Boundary Receipt

- `STATUS`: `SCENARIO_SURFACE_R3_BOUNDARY_FROZEN`
- `UTC_CREATED`: `2026-07-28T06:16:04Z`
- `BRANCH`: `main`
- `STARTING_HEAD`: `0c6f05696c1511e29e17dc71d2d92c4b04431580`
- `ORIGIN_RELATION`: `ahead of origin/main by 3 commits`
- `OLD_FROZEN_CANDIDATE`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `OLD_CANDIDATE_IS_ANCESTOR`: `YES`
- `LAST_GREEN_GATE`: `HARDENING_6_RUN1_GREEN`
- `SUPPLEMENTAL_STATUS`: `SUPPLEMENTAL_GENERALIZATION_GREEN`
- `R2_PLAN_SHA256`: `4453424a60e0cb591bde3a7a6da5ceeb7bd752b8cf9dd6abba785b42c61f32cc`
- `R1_PREFLIGHT_STATUS_SHA256`: `c648444acc19f3dbd1aaa142fb54828e4fd5d3783c59d2ef98748181eddfe61c`
- `R1_BLOCKER_PACKET_SHA256`: `b1be8da1e8787f1d79bdfeed9c5fe4a14248cb686aac2b698ecbd39e823c1767`
- `R1_GLM_RECEIPT_SHA256`: `372846a693754d9e54337c7476baa7ac9536d823ed963b6625dd96e4a79903ab`
- `R1_SURFACE_PROBE_SHA256`: `855d09f8a77c30d5ac4085f2f66db28f9960a5b8815dda31b3379941a38dbd55`
- `PYPROJECT_SHA256`: `ca8d0a873ddfa1d628f54ef5ca989b88e087b967f7d366bca66d8b59249b6dbd`
- `CLI_SHA256`: `98c0dc51de474a472d49fe014910bfb7d30454a851ba390e66ebe1aeea5a9caf`
- `RUNPOD_RUNNING_COUNT`: `0`
- `BLACK_BOX_ACTOR_PROCESS_COUNT`: `0`
- `HIDDEN_SEED_CREATED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`
- `GLM_EXACT_MODEL_SMOKE`: `READY_GLM_52_DIRECT; served by glm-5.2`

## Authorized change boundary

The R3 revision may change only:

- `cockroach_kernel/cli.py` and `cockroach_kernel/test_cli.py`;
- `pyproject.toml` only if packaging the existing P7 authority requires it;
- narrowly scoped modules and tests under `cockroach_kernel/`;
- user-facing README/help material for the scenario-driven command;
- new R3 tests and public-fixture preflight code under `fresh-context-black-box/`;
- new append-only R3 contracts, packets, reports, receipts, manifests, and raw test outputs.

Historical Gate 6, supplemental, R1, R2, and old-candidate artifacts are immutable.
No HOME runtime, credentials, private/client data, AWS, live CockroachDB, RunPod
creation, hidden seed, model actor, Gate 7, deployment, public action, or
repository visibility action is authorized.

## Goal and kill line

The goal is one deterministic installed CLI surface that binds explicit typed
recovery inputs to declared disposable roots while reusing the established P7
selection and record authority. Stop before implementation if the frozen
contract is not independently GREEN. Stop later on any unsafe root, invented
byte, replayable consumed warrant, workspace mutation after refusal/invalid,
test failure, hash drift, incomplete preflight evidence, or non-GREEN final
independent review.

## Next allowed action

Freeze `SCENARIO_SURFACE_R3_CONTRACT.md`, build a sanitized same-hash contract
packet, and obtain direct GLM 5.2 GREEN before product code changes.
