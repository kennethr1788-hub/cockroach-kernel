# P5 Builder Attempt Receipt

- `UTC`: `2026-07-25T23:25:27Z`
- `PARENT_COMMIT`: `432f0d7a7b0e9276052f17eda1fda029fae27d6d`
- `RESULT`: `BLOCKED`

## Kimi

- Contained-wrapper attempt stopped before model execution:
  `managed K3 max-effort contract missing`.
- Direct approved `kimi-code/k3` retry stopped before model execution:
  `auth.login_required: OAuth provider "managed:kimi-code" requires login`.
- No Kimi files changed.
- Kimi binary SHA-256:
  `550bca0ba6e474f4e0faeadfae03a9294c7c25688670f38ff488ab8cf176d817`.
- Contained wrapper SHA-256:
  `d21dc965c06729079571b26389afa00f6d731f35532f4ec0752e10d3712468ee`.
- The wrapper expects K3 `default_effort=max`; current parsed HOME config is
  valid but declares `default_effort=high`. HOME was not modified.

## Vibe

- Attempt 1 stopped at `16,202 > 12,000` tokens.
- Attempt 2 stopped at `26,400 > 24,000` tokens.
- Neither attempt changed tracked project files.
- Vibe binary SHA-256:
  `49eda5eccca6991033113b0cf30ea7b740078d222d4a74a97d667db14e3da4a4`.
- Generated Vibe session state remains isolated in the failed worktree or
  `/tmp`; it is not implementation evidence.

## Devstral

- Sentinel returned exact requested and served model
  `mistral-medium-3-5`.
- Attempt 1 returned no final text and was rejected.
- Attempt 2 returned a bounded advisory configuration/provenance analysis.
- It produced no code, patch, tool action, repository access, or authority
  decision. Its useful constraints remain advisory until Codex integration.
- Devstral binary SHA-256:
  `7fba7da72e8899633e0a916ad6ac792d3bade1c36bc003f32c29f1e76f0678f3`.

No P5 implementation was accepted. No judge packet was created because the
mechanical builder prerequisite failed first.

