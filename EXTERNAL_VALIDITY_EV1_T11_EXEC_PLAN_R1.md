# EV1-T11 Execution Plan R1

| Step | Tool | Expectation | Rollback |
| --- | --- | --- | --- |
| Requalify the offline dependency runtime | Fresh exact-commit export, APFS copy-on-write clone, `/usr/bin/sandbox-exec`, canonical receipt | The previously quarantined dependency tree is disclosed as provenance only; after cloning it into the fresh workspace, every relative workspace link resolves inside that workspace and the unchanged `pnpm test` suite passes with network denied | Preserve the canary receipt and stop before task work if link containment, runtime identity, or the full test suite fails |
| Prepare the disposable task workspace | Git archive, SHA-256, synthetic local HOME/XDG roots | Exact public MIT source commit, clean baseline, private root package, pinned offline runtime, no credentials or source-repository mutation | Tear down only the exact generated T11 root and preserve the preparation receipt |
| Add the release-readiness guard | `apply_patch`, Node.js | One committed local command validates deterministic release metadata and workspace dependency consistency, requires `--offline-dry-run`, and returns a fail-closed publish refusal while the root remains private | Revert only the disposable T11 workspace to its baseline before capture |
| Add documentation and cases | `apply_patch` | `docs/RELEASE.md` is modified and a deterministic cases file remains untracked, producing the frozen committed/modified/untracked mix | Stop before capture and preserve the exact failed state; no upstream action |
| Run acceptance and adversarial checks | `/usr/bin/sandbox-exec`, pinned pnpm, Node.js | Prettier, the release-readiness command, and the unchanged full test suite pass offline; private=false, metadata drift, workspace-reference drift, missing/unknown flags, and publish-like flags fail without external action | Preserve logs and repair only before task-state capture |
| Freeze task work | Canonical JSON receipt, SHA-256, normal disposable-workspace commit | Exact state and file hashes are bound before recovery capture | Stop on state drift; do not capture, delete, or recover |

The task has no independent human-edit requirement. Kenneth's frozen EV1
authorization covers autonomous work inside the generated disposable root. A
later guarded deletion remains fail-closed behind Kenneth's exact-state capture
declaration and an independent same-packet execution preflight.

No npm contact, npm publication, Git tag, remote mutation, public action,
credential use, source-repository mutation, or product-candidate change is
authorized. The dependency tree produced during the failed EV1-T09 dependency
attempt is not retroactively accepted as EV1-T09 evidence. It may be reused only
as a byte-bound, offline T11 runtime if the fresh canary proves containment and
the unchanged full test suite passes.
