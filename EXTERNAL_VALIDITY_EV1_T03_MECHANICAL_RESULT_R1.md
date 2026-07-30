# EV1-T03 Mechanical Result R1

- `STATUS`: `MECHANICAL_TASK_COMPLETE_OPERATOR_OBSERVATION_REQUIRED`
- `TASK_ID`: `EV1-T03`
- `UTC_VERIFIED`: `2026-07-30T17:45:43Z`
- `TASK_EXECUTION_FILE_SHA256`: `841910fa50b3420de7233fc49eba5c7cef7a22ddeef44e66ef667d81e45e6667`
- `TASK_EXECUTION_RECEIPT_SHA256`: `b0209d1a4e40aa5ea05ad39587be96d8b7dee855c7cacfc488d6cda4ee8158da`
- `OBSERVED_VERDICT`: `PROMOTE`
- `STABLE_REASON`: `MAX_PROVEN_PREFIX`
- `ORIGINAL_WORKSPACE_ABSENT`: `TRUE`
- `EMPTY_HISTORY_SUCCESSOR`: `TRUE`
- `DECLARED_WORK_UNITS`: `3`
- `BYTE_EXACT_RESTORED_WORK_UNITS`: `3`
- `POST_LOSS_TASK_RESTATEMENT_WORDS`: `0`
- `POST_LOSS_MANUAL_INTERVENTIONS`: `0`
- `CAMPAIGN_TEARDOWN_PENDING`: `TRUE`

## Recovered bytes

- `package.json`: `bd2ed03ab53472d30312f51a8d7fe4c49e8d8de70e5176002351d17772c52eb8`
- `scripts/recipe-invariant-cases.cjs`: `4bb447cdd5a701a774c048b9560aceaea49361cff60c0a29f5c5f5c7bfe2e8e7`
- `scripts/run-recipe-invariants.mjs`: `fb98839070f85a1d877b8ccb6d015d0d3dc1e6d541849f18d2c1db03743f7274`

All three hashes equal the declared pre-loss hashes.

## Successor acceptance

- typecheck: exit `0`, log SHA-256 `7ad5370190f3f13153e8329d717ccdfec065241392cd850b68579e68731ca022`
- production build: exit `0`, log SHA-256 `05005a632d3ff5b1175ca3b391ca7b3239b4c769bd320d5cf30e46256d7efe47`
- recipe invariants: exit `0`, log SHA-256 `907a86f674596dea4f981f07fb8d083bface8ca6d69cd7f71253f92b985c6d80`

The product reported `FRESH_CONTEXT_PASS`, `network_used=false`, and
`credentials_used=false`. The execution receipt records zero false promotions,
unsafe mutations, unauthorized path accesses, original-workspace residue
bytes, and task-process residue. Productive continuation occurred after
`115734500` monotonic nanoseconds; full acceptance passed after `15268708958`
monotonic nanoseconds.

## Human-only observation gate

Kenneth must confirm or correct these two statements based on the observed
result:

1. The recovered recipe-invariant work appears usable, and the passing
   typecheck, build, and seven-case invariant suite represent productive
   continuation of the declared task.
2. Ordinary Git alone would have preserved the committed test runner, but it
   would not have preserved the modified `package.json` and untracked
   `scripts/recipe-invariant-cases.cjs` in their exact declared state.

These are operator observations, not facts the builder may self-attest. The
temporary successor remains preserved until the observations and independent
objective-evidence audit are complete.
