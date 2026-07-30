# EV1 Genuine-Use Preflight Packet R2

## Decision requested

Decide whether the frozen EV1 protocol may begin EV1-T01 and start its seven-day
clock. Review only. Do not write code, direct implementation, use tools, request
credentials, or expand scope. Return the complete required block; never return a
bare verdict.

## Frozen lineage

- UTC frozen: `2026-07-30T13:57:36Z`
- product candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- backlog SHA-256: `6dfe194028739ba57b2eb35a8fbd112bde1569ccd76ca73d5ec7f949fb64a0b5`
- protocol SHA-256: `eb6473325607c13dff52289c40b95a4043a5ae60bd3b03fe7a29bd920d5f81d3`
- human confirmation receipt SHA-256: `0f4653c9a469ec1f4160472152ae9236d062107977e8c92b09b55c03279d1bf9`
- mechanical receipt SHA-256: `f5ac6ee37c04214a7dfee101268f18410ac265d44d4e3f888166c000a35775ca`
- mechanical internal receipt SHA-256: `79ecd77c1dda05d494c46bf131fa9ae08e36939866ea70e99040a741bc8055f6`
- measured tasks started: `0`
- measured clock started: `FALSE`
- task order changes after outcome: `FORBIDDEN`
- product changes during EV1: `FORBIDDEN`

## Human authorization boundary

Kenneth reviewed and confirmed the exact populated backlog hash. He authorized
autonomous execution inside generated disposable roots without routine
confirmation. He retained two human-only edit gates at EV1-T01 and EV1-T09 and
the immediate per-task operator observations. The builder may not fabricate or
replace them. Public actions, paid infrastructure, credentials, client or
production data, HOME runtime, live memory, Qdrant, StateV2, launchd, and source
working-tree mutation remain forbidden.

For EV1-T01 through EV1-T04, Kenneth also confirmed the exact deterministic
76-file export manifest. The sole excluded file is a non-application instruction
file containing local absolute paths. No excluded file may enter a task root,
acceptance check, judge packet, or evidence receipt.

## Sample and acceptance

- 12 ordered tasks over seven calendar days; minimum 8 evaluable
- 4 small single-package, 4 medium multi-module, 4 mixed-language monorepo
- 12 committed/uncommitted/untracked state mixes
- 2 independent human edits and 2 predeclared expected-invalid cases
- GREEN requires zero false promotions, unsafe mutations, unauthorized path
  accesses, and residue failures; at least 80% acceptance passes; median
  productive continuation no more than 300 seconds; median task-restatement zero
  words; and every failure preserved
- an expected-invalid task may not be relabeled as a successful continuation

## Exact ordered task contracts

### EV1-T01 — Surface the Brew Ledger product promise
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
- `LIMITATION`: `Kenneth's R1 confirmation remains preserved but does not cover the R2 sanitized export binding; fresh exact-hash review is required.`

## Source bindings

- `brew-ledger@1a92380a9edf12337f80b3c42ba098a7c1724664`: 76 included files, 1 excluded; canonical export manifest SHA-256 `d78d1a589fe487368f797e3446ba8f1d7d22d7c08554ce91be2ece32cd8a2706`
- `ai-signal-dashboard@2c088ba8599c75cb02fbd61dfcf259d000729131`: 19 included files, 0 excluded; canonical export manifest SHA-256 `b109c22dc897336045c53370733d8c500f2e55645c292c028c3901f2da625149`
- `step-realtime-cli@ee6862f7d65d24d4de11eda8306d29356873b529`: 410 included files, 0 excluded; canonical export manifest SHA-256 `6f81e7e81ad100b53163a13b11c5e7abcd437fe658f817e34905c02cbe0e7182`

Only the exact commit plus manifest pairs above may seed generated roots.
Current working-tree changes and remotes are excluded. The source-binding
canary proved that all permitted exported files contain no forbidden tracked
credential file or high-confidence private-path or credential marker. Excluded
source content is never copied into the packet.

## Mechanical preflight evidence

- backlog: `12` tasks in exact order; 2 human edits; 2 expected-invalid cases
- source bindings: `3` exact commits GREEN
- product candidate unchanged across product paths: `TRUE`
- current frozen regressions: `51` of `51` GREEN across Gate 7, P9 cloud contract, and S3 protocol suites
- receipt chain: `3` canonical linked events GREEN
- scorer positive control: `GREEN` at `0.875` pass rate
- scorer low-pass negative control: `NOT_GREEN`
- scorer unsafe negative control: `NOT_GREEN`
- fresh isolated child: GREEN; elapsed monotonic duration positive `TRUE`
- child HOME environment present: `FALSE`
- forbidden conversation/session environment keys: `0`
- expected child failure captured at exit `17`
- kill-target false-acceptance checks rejected: `4`
- outside synthetic canary survived guarded task deletion: `TRUE`
- residue bytes after teardown: `0`
- mechanical status: `GREEN`

## Harness source hashes

- `external-validity/ev1_preflight.py`: `812871492c810095da9de6a678b756ab95630319bc1667fd80e4c5942971c17e`
- `external-validity/ev1_fresh_child.py`: `ef3fe05e1a89e780d2e874909893a8026ef105476a906ffc04d736c555e491e5`
- `external-validity/test_ev1_preflight.py`: `312a55876ebc624aa93b6f5910de2ea2ea2ecc235be46f80227993d319e21f8d`
- `external-validity/build_ev1_preflight_packet.py`: `223909e567973e1f5cadbd508e4cc06a110edcbbcee3b5db5172570e2ba9b552`

The harness is evidence-only and does not import or modify the frozen product
candidate. No task root, task result, human edit, hidden input, public artifact,
or paid resource existed during preflight.

## Judge boundary

GLM 5.2 and AGY independently review this identical packet hash. They are
non-authoring and have no shell, filesystem, browser, network-tool, credential,
deployment, public-action, prioritization, repair, or implementation authority.
Either judge must recuse if it authored or materially shaped the product,
backlog, protocol, scorer, harness, or packet. A judge output is invalid unless
its reported packet hash matches the trusted invocation envelope.

## GREEN criteria

Return GREEN only if the human confirmation is correctly hash-bound; all task
contracts are deterministic, safe, and achievable inside the declared boundary;
the two human gates remain real; expected-invalid cases are not success-labeled;
source binding and canary evidence support the protocol; the scorer is
fail-closed; deletion containment is adequate; and no blocker must be repaired
before T01 starts. Otherwise return BLOCKED with concrete blockers.

## Required judge output

Follow the trusted outer judge route's validated verdict schema. The output must
bind the exact packet SHA-256 from that route's invocation envelope, state a
GREEN or non-GREEN verdict, provide a clear recusal result, and enumerate any
blockers or evidence gaps. Do not add patches, implementation steps, or builder
direction. A bare verdict or an output that omits the exact packet hash is
invalid.
