# Project Runtime Cleanup Receipt R2

## Scope

This second cleanup pass is limited to reproducible dependency installations, superseded worker-transfer copies, extracted staging trees, and one already-expanded installer package. It does not delete application source, Git history, campaign receipts, manifests, raw logs, final evidence, current runtime tools, required preserved workspaces, or ambiguous hardening evidence.

## Preconditions

- `UTC_FROZEN`: `2026-08-02T13:08:30Z`
- `BASE_COMMIT`: `248c3dfe7ef5d973a1db0e8a5d0f135a5e6be160`
- `RUNPOD_INVENTORY`: `[]`
- `MATCHING_CAMPAIGN_OR_TASK_PROCESSES`: `NONE`
- `TARGET_MOUNTS`: `NONE`
- `TARGETS_ARE_NOT_SYMLINKS`: `true`
- `AWS_EXPANDED_RUNTIME`: `aws-cli/2.36.8 Python/3.14.6 Darwin/25.5.0 exe/arm64`
- `TARGET_COUNT`: `16`
- `TOTAL_TARGET_BYTES`: `4560579518`
- `TARGET_LIST_SHA256`: `bf683fe44bf29de3a0333bbbabebfbdb990f331f07acf316f437c0f04d2a878b`
- `STATUS`: `FROZEN_BEFORE_DELETION`

## Exact target manifest

| Target | Kind | Bytes | Files | Internal symlinks | SHA-256 if file |
|---|---:|---:|---:|---:|---|
| `.ev1-runtime/EV1-T01/dependency-runtime` | directory | 338479282 | 10624 | 16 | — |
| `.ev1-runtime/EV1-T02/dependency-runtime` | directory | 338479282 | 10624 | 16 | — |
| `.ev1-runtime/EV1-T03/dependency-runtime` | directory | 338479282 | 10624 | 16 | — |
| `.ev1-runtime/EV1-T04/dependency-runtime` | directory | 338479282 | 10624 | 16 | — |
| `.ev1-runtime/EV1-T05/dependency-runtime` | directory | 364392894 | 11968 | 7 | — |
| `.ev1-runtime/EV1-T06/dependency-runtime` | directory | 364392894 | 11968 | 7 | — |
| `.ev1-runtime/EV1-T09/dependency-runtime/node_modules` | directory | 8580952 | 57 | 1 | — |
| `.ev1-runtime/EV1-T09/dependency-attempt-r1-node_modules` | directory | 607147989 | 19726 | 1321 | — |
| `.ev1-runtime/EV1-T10/dependency-runtime/node_modules` | directory | 8580952 | 57 | 1 | — |
| `.ev1-runtime/EV1-T11/dependency-runtime` | directory | 607147989 | 19726 | 1321 | — |
| `.ev1-runtime/EV1-T12/dependency-runtime` | directory | 607147989 | 19726 | 1321 | — |
| `.s3-runtime/bundles/worker-r1.tar.gz` | file | 144500645 | 1 | 0 | `51df007f8ffc79b164e5b3b6e0e95115e2fc57b8f2efff4de19992eb6c117cd0` |
| `.s3-runtime/bundles/worker-r2.tar.gz` | file | 144500700 | 1 | 0 | `5c33c443e8e4d0e0b8c6c539ddd94c4c291625a73e4c257daec5fc69ae38140f` |
| `.s3-runtime/bundles/worker-stage-r2` | directory | 145453315 | 74 | 0 | — |
| `.s3-runtime/staging-worker-r1` | directory | 145441142 | 72 | 0 | — |
| `.s3-runtime/download/AWSCLIV2.pkg` | file | 59374929 | 1 | 0 | `d8d61d31fe5e55f7addf9e0f08e44c5e1aab0af8ba53699d94c34e13d447bcff` |

## Preserved classes

- All EV1 control, preparation, work, capture, preflight, mechanical-result, result, audit, and aggregate receipts.
- EV1-T07 and EV1-T08 workspaces and their exact invalid-safety evidence.
- EV1-T05 failed preparation workspace and its failure evidence.
- Package manifests and lockfiles in the T09 and T10 dependency roots; only their generated `node_modules` trees are targets.
- `.s3-runtime/bundles/worker-r3.tar.gz` as the latest worker archive, SHA-256 `c0f0514c09d63da833361ec34ef2cbc2f0e96c210fca043cbc7d3c33a8e703d4`.
- Project-local expanded AWS CLI runtime and authenticated configuration boundary.
- All `.hardening-runtime`, `p2-cleanroom`, and remaining `.pdh3-runtime` content because their evidence/runtime roles are not uniformly disposable.
- Operator-owned untracked `heap_profiler/`.

## Kill line

Abort without deleting if a target path differs from this exact list, resolves outside the repository, is a mount, is active in a task/campaign process, or if the retained worker archive or expanded AWS runtime fails verification.

