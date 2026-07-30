# EV1-T09 Dependency Attempt R1 — Quarantined

- `STATUS`: `PRESERVED_NON_ACCEPTANCE_DEPENDENCY_ATTEMPT`
- `TASK_ID`: `EV1-T09`
- `TRIGGER`: `Host fallback pnpm 11.9.0 implicitly ran a full workspace install when asked to execute Prettier.`
- `PACKAGES_OBSERVED`: `522`
- `QUARANTINED_TREE`: `.ev1-runtime/EV1-T09/dependency-attempt-r1-node_modules`
- `QUARANTINED_TREE_SIZE`: `647528_KiB`
- `GENERATED_PRE_COMMIT_HOOK_SHA256`: `00f4004c9fb1bb5868365b62a3694b00f34a1537181db3bc86e33c9d7e714639`
- `GENERATED_PRE_PUSH_HOOK_SHA256`: `697fe3bcba6f43610f4605b94880e316361bae1896959c08d8daedae54c59f79`
- `IMPLICIT_WORKSPACE_EDIT`: `pnpm-workspace.yaml allowBuilds placeholders; removed exactly before task commit`
- `ACCEPTANCE_EVIDENCE`: `NOT_ELIGIBLE`
- `SOURCE_REPOSITORY_MUTATED`: `FALSE`
- `PRODUCT_CANDIDATE_MUTATED`: `FALSE`
- `PUBLIC_ACTION`: `FALSE`
- `REPLACEMENT_RUNTIME`: `CAMPAIGN_LOCAL_PNPM_10.17.0_AND_PRETTIER_3.8.1`
- `PINNED_PNPM_ENTRY_SHA256`: `b276da51dc8ca5b0d3ee3371695b50fc8b3244b281b091c63a3f082a88dadeb9`
- `PINNED_PRETTIER_ENTRY_SHA256`: `ac5523cd57e7e9d8eac71caef7e022a8a8489bcdc19ca8a778b7e728ec103b93`

The implicit dependency tree and generated hooks were moved out of the
workspace intact. The two hooks are preserved under the task control root. The
workspace now uses a minimal campaign-local runtime selected through an
explicit PATH; its exact `pnpm exec prettier --check docs/RELEASE.md` invocation
passed without any install or lifecycle script.
