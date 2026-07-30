# EV1-T01 Operator Observation Receipt R1

- `TASK_ID`: `EV1-T01`
- `STATUS`: `HUMAN_OBSERVATIONS_CONFIRMED`
- `UTC_RECORDED`: `2026-07-30T15:25:41Z`
- `CONFIRMATION_SOURCE`: `Kenneth's explicit confirmation in the current Codex conversation`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `MECHANICAL_OUTCOME`: `INFRASTRUCTURE_INVALID_PRESERVED; NON_SCORING`

## Immediate qualitative observation

> I observed that the fresh successor restored both declared files, including
> my saved tagline edit and the untracked verifier, without me recreating them.
> The standalone verifier passed, but the full typecheck failed because the
> test environment placed the dependencies outside the recovered workspace's
> resolution path—not because the recovered files were missing or altered.

## Git and backup counterfactual

> Plain Git would not have recovered this exact state unless I had first
> committed or stashed both the modified tracked file and the untracked
> verifier. A sufficiently recent conventional backup might have restored the
> files, but only if it had captured them before deletion; it would not by
> itself provide the same task-bound recovery decision, provenance, and receipt
> evidence.

Kenneth explicitly confirmed both statements as accurate. These observations
do not convert the frozen full acceptance into a pass. The task remains
infrastructure-invalid and non-scoring because `npm run typecheck` did not exit
zero in the recovered successor.
