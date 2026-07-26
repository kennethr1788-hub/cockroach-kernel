# P9 Kimi Project-Local Requalification Packet R1

## Scope

Requalify one contained Kimi K3 builder invocation for the disposable P9 worktree.
This packet does not authorize cloud actions, credential extraction, HOME mutation,
deployment, S3, or use outside P9.

## Frozen inputs

- Canonical wrapper: `/Users/kennethruedas/.hermes/scripts/kimi-codex-worker.sh`
- Canonical wrapper SHA-256: `d21dc965c06729079571b26389afa00f6d731f35532f4ec0752e10d3712468ee`
- Project-local launcher: `p9-tooling/kimi-max-effort-worker.py`
- Project-local launcher SHA-256: `df86427059bed2532c669599e67579a08a1772c035aca4a317dba7be8e779975`
- Generated patched wrapper SHA-256: `528f82e25402e39cf4c1057327ec9f7fc94ad739aab6b662a773d2cb89d2863d`
- Model alias: `kimi-code/k3`
- Required provider model: `k3`
- Required context size: `1048576`
- Required capabilities: `thinking`, `always_thinking`, `image_in`, `video_in`, `tool_use`
- Required supported effort: `max`

## Exact correction

The canonical wrapper currently rejects the source model entry unless its
`default_effort` already equals `max`. The project-local launcher performs one exact
source transformation after verifying the canonical wrapper hash:

1. Require `max` to be present in `support_efforts`.
2. Copy the model dictionary in the canonical wrapper's existing isolated-config step.
3. Set the copied dictionary's `default_effort` to `max`.
4. Write only the existing temporary isolated config.

No source configuration or credential is written. All original repository scans,
egress sanitization, binary hashes, OAuth copy isolation, `sandbox-exec` profile,
timeouts, disabled skills, disabled cron, and post-run checks remain byte-identical
outside this exact transformation.

## Acceptance

- Launcher self-test verifies source hash and generated shell syntax.
- Independent GLM confirms the correction preserves containment and enforces max effort.
- Builder operates only in `/Users/kennethruedas/sandbox/ck-p9-kimi-20260726`.
- No HOME file changes.
- No cloud or credential actions.

## Kill line

Stop and leave Kimi unavailable if the wrapper hash drifts, the exact source block is
not found once, `max` is unsupported, syntax validation fails, independent review is
not GREEN, or the contained worker reports a boundary failure.
