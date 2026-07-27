# Hardening Gate 3 Human Action Required

- `STATUS`: `HUMAN_ACTION_REQUIRED`
- `LAST_GREEN_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `GATE_2_GREEN_COMMIT`: `9123fa0c550b151943e5997ea465cd5311c0cb3e`
- `GATE_2_PACKET_SHA256`: `5c7624937bdae41f64dbd5e2c66f34afc3326fdacfdb1484ef118c964e386b41`
- `NEXT_TARGET`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `UTC_RECORDED`: `2026-07-27T19:04:47Z`

## Required action

Kenneth must provide both facts directly:

1. state one concrete coding task for one real, non-sensitive codebase; and
2. after the isolated Gate 3 trace is armed, visibly make and save one
   independent non-sensitive edit in the declared file.

The task statement should identify the target codebase, the concrete expected
behavior, and an executable acceptance check. The saved edit must be Kenneth's
own action; no model may infer, simulate, or self-attest it.

No Gate 3 implementation, live trajectory mutation, declared-loss event,
fresh-context continuation, promotion/refusal, or cleanup may be claimed before
both human facts are directly evidenced.

Resume from the current clean `main` branch after Kenneth states the task. The
builder will then freeze the isolated workflow, stop for the visible saved
edit, and continue only after direct file-state evidence.
