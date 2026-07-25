# P5 Builder Assignments

All inputs are synthetic and non-sensitive. No builder may access credentials,
HOME runtime, live memory, client data, deployment, or authoritative policy.

- Kimi worktree: `../cockroach-kernel-p5-kimi`; own `p5-lanes/manifest.py` and fixtures.
- Vibe worktree: `../cockroach-kernel-p5-vibe`; own adversarial test proposals only.
- Devstral: one-turn sanitized boundary analysis; no repository or tool access.
- Codex: reviews and reimplements/integrates accepted work with `apply_patch`.

Every handoff must state scope, files, tests, limitations, and hashes.

