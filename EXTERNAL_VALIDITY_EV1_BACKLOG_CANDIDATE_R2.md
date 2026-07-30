# EV1 Genuine-Task Backlog Candidate R2

## Status

- `STATUS`: `CONTENT_COMPLETE_AWAITING_KENNETH_REVIEW`
- `UTC_CREATED`: `2026-07-30T13:29:40Z`
- `R2_REASON`: `R1 preflight found two absolute local paths in the committed Brew Ledger CLAUDE.md; R2 excludes that one non-application instruction file through a deterministic export manifest.`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `MEASURED_TASKS_STARTED`: `0`
- `MEASURED_CLOCK_STARTED`: `FALSE`
- `TASK_ORDER_FROZEN`: `FALSE`
- `HUMAN_AUTHENTICITY_GATE`: `OPEN`

This is the exact candidate backlog for Kenneth's review. It is not genuine-use
evidence and does not authorize task execution. Each source is bound to a clean
committed baseline; unrelated working-tree changes are excluded. All acceptance
commands must run inside generated disposable roots with dependency installation
completed and frozen before measurement, then with network access disabled.

## Ordered backlog

### EV1-T01 — Surface the Brew Ledger product promise

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `LOCAL_SANITIZED_EXPORT_LABEL:brew-ledger@1a92380a9edf12337f80b3c42ba098a7c1724664#d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706`
- `PROJECT_CLASS`: `SMALL_SINGLE_PACKAGE`
- `OBJECTIVE`: Add the already documented Home-page tagline `Document every extraction.` as semantic, accessible copy without changing routes or storage behavior.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `npm run typecheck && npm run build && node scripts/verify-home-tagline.mjs`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `YES — Kenneth must type and visibly save the tagline in the disposable root after the task contract is frozen.`
- `PREDECLARED_REFUSAL_OR_INVALID`: `NONE`
- `DATA_CLASSIFICATION`: `KENNETH_OWNED_NON_CLIENT`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `The source working tree has unrelated later changes. The task uses the exact 76-file manifest-bound export from the source commit; CLAUDE.md alone is excluded because it contains absolute local paths and is not application or acceptance-test code.`

### EV1-T02 — Automate corrupt-storage and import-repair checks

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `LOCAL_SANITIZED_EXPORT_LABEL:brew-ledger@1a92380a9edf12337f80b3c42ba098a7c1724664#d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706`
- `PROJECT_CLASS`: `SMALL_SINGLE_PACKAGE`
- `OBJECTIVE`: Add deterministic tests proving corrupt JSON is quarantined, unknown import keys are ignored, invalid records are rejected, and valid recipe references survive invariant repair.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `npm run typecheck && npm run build && npm run test:storage-contract`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `NO`
- `PREDECLARED_REFUSAL_OR_INVALID`: `NONE`
- `DATA_CLASSIFICATION`: `SYNTHETIC`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `The exact 76-file manifest-bound export excludes CLAUDE.md only. The test runner and dependency graph must be pinned during preflight; measured acceptance must be offline.`

### EV1-T03 — Prove recipe-version invariants

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `LOCAL_SANITIZED_EXPORT_LABEL:brew-ledger@1a92380a9edf12337f80b3c42ba098a7c1724664#d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706`
- `PROJECT_CLASS`: `SMALL_SINGLE_PACKAGE`
- `OBJECTIVE`: Add deterministic tests for monotonic version labels, exclusive favorite and dial-in pointers, cross-group rejection, and cascading cleanup of version-linked Quick Brews.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `npm run typecheck && npm run build && npm run test:recipe-invariants`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `NO`
- `PREDECLARED_REFUSAL_OR_INVALID`: `NONE`
- `DATA_CLASSIFICATION`: `SYNTHETIC`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `The exact 76-file manifest-bound export excludes CLAUDE.md only. The test runner and dependency graph must be pinned during preflight; measured acceptance must be offline.`

### EV1-T04 — Lock local-day dashboard behavior across UTC rollover

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `LOCAL_SANITIZED_EXPORT_LABEL:brew-ledger@1a92380a9edf12337f80b3c42ba098a7c1724664#d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706`
- `PROJECT_CLASS`: `SMALL_SINGLE_PACKAGE`
- `OBJECTIVE`: Extract the dashboard's local-calendar-day selection into a pure helper and add deterministic timezone cases proving a late-Pacific brew remains on the correct local day.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `TZ=America/Los_Angeles npm run test:dashboard-date && TZ=UTC npm run test:dashboard-date && npm run typecheck && npm run build`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `NO`
- `PREDECLARED_REFUSAL_OR_INVALID`: `NONE`
- `DATA_CLASSIFICATION`: `SYNTHETIC`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `The exact 76-file manifest-bound export excludes CLAUDE.md only. The helper must remain deterministic and must not read the wall clock inside verdict logic.`

### EV1-T05 — Validate the offline signal dataset at runtime

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `LOCAL_PROJECT_LABEL:ai-signal-dashboard@2c088ba8599c75cb02fbd61dfcf259d000729131`
- `PROJECT_CLASS`: `MEDIUM_MULTI_MODULE`
- `OBJECTIVE`: Replace the unchecked JSON cast with a strict runtime schema that rejects duplicate IDs, invalid sources, malformed timestamps, empty titles, and non-array tags before analysis.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `npm run typecheck && npm run build && npm run test:signal-schema`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `NO`
- `PREDECLARED_REFUSAL_OR_INVALID`: `NONE`
- `DATA_CLASSIFICATION`: `SYNTHETIC`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `A package lock and exact dependency graph must be frozen in preflight because the source commit lacks a lockfile; measured acceptance must be offline.`

### EV1-T06 — Make equal-score ranking deterministic

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `LOCAL_PROJECT_LABEL:ai-signal-dashboard@2c088ba8599c75cb02fbd61dfcf259d000729131`
- `PROJECT_CLASS`: `MEDIUM_MULTI_MODULE`
- `OBJECTIVE`: Add a pure ranking comparator with stable tie-breaks by publication time and signal ID, then prove repeated runs produce byte-identical order.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `npm run typecheck && npm run build && npm run test:stable-ranking`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `NO`
- `PREDECLARED_REFUSAL_OR_INVALID`: `NONE`
- `DATA_CLASSIFICATION`: `SYNTHETIC`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `A package lock and exact dependency graph must be frozen in preflight; measured acceptance must be offline.`

### EV1-T07 — Enforce bounded analyze-request payloads

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `LOCAL_PROJECT_LABEL:ai-signal-dashboard@2c088ba8599c75cb02fbd61dfcf259d000729131`
- `PROJECT_CLASS`: `MEDIUM_MULTI_MODULE`
- `OBJECTIVE`: Add explicit length and cardinality limits for focus topics, titles, raw text, and tags; return a stable 400 response for oversized input without invoking a provider.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `npm run typecheck && npm run build && npm run test:api-limits`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `NO`
- `PREDECLARED_REFUSAL_OR_INVALID`: `EXPECTED_INVALID — the task creates an untracked 80 KiB oversized request fixture; capture must return the frozen oversized-state INVALID reason and must not destroy or follow the fixture.`
- `DATA_CLASSIFICATION`: `SYNTHETIC`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `This is a predeclared expected-invalid recovery case; it may not be relabeled as a successful continuation.`

### EV1-T08 — Prevent sample-data symlink escape

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `LOCAL_PROJECT_LABEL:ai-signal-dashboard@2c088ba8599c75cb02fbd61dfcf259d000729131`
- `PROJECT_CLASS`: `MEDIUM_MULTI_MODULE`
- `OBJECTIVE`: Resolve and validate the sample-data file beneath the declared data root, reject symlink escapes, and test both an in-root file and an out-of-root target without reading the latter.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `npm run typecheck && npm run build && npm run test:data-path-containment`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `NO`
- `PREDECLARED_REFUSAL_OR_INVALID`: `EXPECTED_INVALID — the task creates a disposable symlink whose target is outside the generated task root; capture must return the frozen path-escape INVALID reason and must not read, modify, or delete the target.`
- `DATA_CLASSIFICATION`: `SYNTHETIC`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `The out-of-root target must itself be a synthetic canary created by the EV1 harness, never a HOME or unrelated-project file.`

### EV1-T09 — Define versioning and changelog policy

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `PUBLIC_MIT_PROJECT_LABEL:step-realtime-cli@ee6862f7d65d24d4de11eda8306d29356873b529`
- `PROJECT_CLASS`: `MIXED_LANGUAGE_MONOREPO`
- `OBJECTIVE`: Replace the release-document placeholders for SemVer and changelog generation with explicit 0.x rules, breaking-change handling, and a deterministic changelog procedure while preserving the private-package safeguard.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `pnpm exec prettier --check docs/RELEASE.md && node scripts/validate-release-policy.mjs --sections versioning,changelog`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `YES — Kenneth must type and visibly save the one-sentence release principle after the task contract is frozen.`
- `PREDECLARED_REFUSAL_OR_INVALID`: `NONE`
- `DATA_CLASSIFICATION`: `PUBLIC_PERMISSIVE`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `Local disposable fork only; no upstream push, npm publication, or GitHub release is authorized.`

### EV1-T10 — Add a mechanically validated GitHub release-note template

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `PUBLIC_MIT_PROJECT_LABEL:step-realtime-cli@ee6862f7d65d24d4de11eda8306d29356873b529`
- `PROJECT_CLASS`: `MIXED_LANGUAGE_MONOREPO`
- `OBJECTIVE`: Add a release-note template covering highlights, breaking changes, migration, verification, binary checksums, and known limitations, plus a validator that fails when required sections are absent.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `pnpm exec prettier --check docs/RELEASE.md .github/release-notes-template.md && node scripts/validate-release-notes.mjs .github/release-notes-template.md`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `NO`
- `PREDECLARED_REFUSAL_OR_INVALID`: `NONE`
- `DATA_CLASSIFICATION`: `PUBLIC_PERMISSIVE`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `No upstream push, npm publication, or GitHub release is authorized.`

### EV1-T11 — Add a fail-closed npm release dry-run guard

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `PUBLIC_MIT_PROJECT_LABEL:step-realtime-cli@ee6862f7d65d24d4de11eda8306d29356873b529`
- `PROJECT_CLASS`: `MIXED_LANGUAGE_MONOREPO`
- `OBJECTIVE`: Add a local release-readiness command that confirms version consistency and required metadata but refuses any publish path while the root package remains private; it must never contact npm.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `pnpm exec prettier --check docs/RELEASE.md scripts/check-release-readiness.mjs && node scripts/check-release-readiness.mjs --offline-dry-run && pnpm test`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `NO`
- `PREDECLARED_REFUSAL_OR_INVALID`: `NONE`
- `DATA_CLASSIFICATION`: `PUBLIC_PERMISSIVE`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `The command must prove network code is absent and must not run npm publish, create tags, or mutate remotes.`

### EV1-T12 — Generate deterministic binary checksum manifests

- `GENUINE_INTENT_CONFIRMATION`: `PENDING_KENNETH_CONFIRMATION`
- `SOURCE_LOCATION`: `PUBLIC_MIT_PROJECT_LABEL:step-realtime-cli@ee6862f7d65d24d4de11eda8306d29356873b529`
- `PROJECT_CLASS`: `MIXED_LANGUAGE_MONOREPO`
- `OBJECTIVE`: Add an offline manifest generator for prebuilt client binaries that emits canonical sorted SHA-256 entries, rejects duplicate platform labels, and is covered by deterministic fixture tests.
- `ACCEPTANCE_COMMAND_OR_CHECK`: `pnpm exec prettier --check docs/RELEASE.md scripts/build-release-manifest.mjs scripts/build-release-manifest.test.ts && pnpm vitest run scripts/build-release-manifest.test.ts`
- `STATE_MIX`: `COMMITTED, UNCOMMITTED, UNTRACKED`
- `INDEPENDENT_HUMAN_EDIT`: `NO`
- `PREDECLARED_REFUSAL_OR_INVALID`: `NONE`
- `DATA_CLASSIFICATION`: `PUBLIC_PERMISSIVE`
- `DISPOSABLE_DELETION_AUTHORIZED`: `YES`
- `LIMITATION`: `Synthetic binary fixtures only; no actual release, upload, signing key, or external registry access is authorized.`

## Aggregate candidate checks

- `TASK_COUNT`: `12`
- `SMALL_SINGLE_PACKAGE_COUNT`: `4`
- `MEDIUM_MULTI_MODULE_COUNT`: `4`
- `MIXED_LANGUAGE_MONOREPO_COUNT`: `4`
- `COMMITTED_UNCOMMITTED_UNTRACKED_COUNT`: `12`
- `INDEPENDENT_HUMAN_EDIT_COUNT`: `2`
- `PREDECLARED_REFUSAL_OR_INVALID_COUNT`: `2`
- `CLIENT_OR_PRODUCTION_DATA_COUNT`: `0`
- `PAID_SERVICE_REQUIRED_COUNT`: `0`
- `PUBLIC_ACTION_REQUIRED_COUNT`: `0`

## Kenneth's required confirmation

After reviewing every row and the candidate SHA-256, Kenneth must provide a new
explicit confirmation bound to that exact hash. The confirmation must state that
EV1-T01 through EV1-T12 are genuine development tasks he intended independently
of EV1; their objectives, source classifications, acceptance checks, task order,
data boundaries, and deletion permissions are accurate; and the two human edits
remain his responsibility when those tasks occur.

- `CHECKBOX`: `UNCHECKED`
- `CONFIRMED_CANDIDATE_SHA256`:
- `UTC_TIMESTAMP`:
- `LIMITATION`: `Kenneth's R1 confirmation remains preserved but does not cover the R2 sanitized export binding; fresh exact-hash review is required.`
