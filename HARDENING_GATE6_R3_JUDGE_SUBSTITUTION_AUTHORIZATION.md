# Hardening Gate 6 R3 — Judge Substitution Authorization

- `STATUS`: `AUTHORIZED`
- `AUTHORIZED_BY`: `Kenneth`
- `UTC_RECORDED`: `2026-07-28T01:49:40Z`
- `RECUSAL_CAUSE`: `CLAUDE_MATERIALLY_SHAPED_R3_ISOLATION_HARDENING`
- `RECUSED_LANE`: `CLAUDE_OPUS_4_8`
- `REPLACEMENT_LANE`: `AGY_JUDGE_GEMINI_3_1_PRO_HIGH`
- `REQUIRED_PREFLIGHT_QUORUM`: `GLM 5.2 AND AGY GREEN ON THE SAME HASH`
- `REQUIRED_FINAL_QUORUM`: `GLM 5.2 AND AGY GREEN ON THE SAME HASH`
- `GATE7_AUTHORIZED`: `no`

Kenneth explicitly authorizes replacing the recused Claude lane with the
independent AGY judge for Gate 6 R3 preflight and final review. This authority
does not erase, invalidate, or conceal Claude's earlier influence or recusal.
It authorizes one fresh frozen packet to GLM 5.2 and AGY and permits the already
authorized sequential RunPod retries only if both independent lanes return
GREEN with recusal clear.

This does not authorize AGY to code, edit, repair, plan implementation, use
tools, deploy, access credentials, or direct the builder. It does not widen the
RunPod envelope, change the immutable candidate, authorize Gate 7, or waive any
runtime, evidence, billing, teardown, or final-review gate.
