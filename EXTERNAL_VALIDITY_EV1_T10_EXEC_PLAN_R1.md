# EV1-T10 Execution Plan R1

| Step | Tool | Expectation | Rollback |
| --- | --- | --- | --- |
| Freeze exact task surface | Git status, SHA-256, preparation receipt | Exact public source commit, private-package safeguard, pinned offline Prettier, no pre-existing template or validator | Stop before workspace edits and preserve the preparation receipt |
| Add validator | `apply_patch`, Node.js | One committed validator checks required release-note headings, order, uniqueness, and template-specific operational guidance without network or publication surfaces | Revert only the disposable T10 workspace to its baseline commit before capture |
| Add template and documentation link | `apply_patch` | Template is untracked; `docs/RELEASE.md` is modified; validator remains committed, producing the frozen committed/modified/untracked mix | Stop before capture and preserve exact failed state; no upstream action |
| Run acceptance and adversarial checks | `/usr/bin/sandbox-exec`, pinned project-local pnpm/Prettier, Node.js | Frozen acceptance passes offline; missing, duplicate, and reordered section mutations fail | Preserve logs and repair only before task-state capture |
| Freeze task work | Canonical JSON receipt, SHA-256, normal disposable-workspace commit | Exact state and hashes are bound before any recovery capture | Stop at state drift; do not delete or recover |

The task has no independent human-edit requirement. Kenneth's frozen EV1
authorization already covers autonomous work in the generated disposable root
and later guarded deletion under task-specific independent preflight. No public
push, npm publication, GitHub release, credential use, or source-repository
mutation is authorized. A later deletion remains fail-closed behind the frozen
capture declaration and independent execution preflight.
