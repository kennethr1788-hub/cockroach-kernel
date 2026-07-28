# Fresh-Context Black-Box Preflight — Independent GLM Receipt R1

- `STATUS`: `BLACK_BOX_PREFLIGHT_BLOCKER_INDEPENDENTLY_CONFIRMED`
- `UTC_CREATED`: `2026-07-28T06:01:40Z`
- `PLAN_SHA256`: `4453424a60e0cb591bde3a7a6da5ceeb7bd752b8cf9dd6abba785b42c61f32cc`
- `BLOCKER_PACKET_SHA256`: `b1be8da1e8787f1d79bdfeed9c5fe4a14248cb686aac2b698ecbd39e823c1767`
- `JUDGE_INSTRUCTIONS_SHA256`: `54c841c7c2c2aa0673e297374196dac8f0ffcf5be3b637273b54312b037df597`
- `EXACT_CONCATENATED_PACKET_SHA256`: `4b8f5b1eded66f7e2e8e98b11720a6110028016dabe87a6de5934edb8e15d2ec`
- `PACKET_ORDER`: `judge instructions || R2 plan || blocker packet`
- `JUDGE_ROUTE`: `direct glm-zai`
- `REQUESTED_AND_SERVED_MODEL`: `glm-5.2`
- `FALLBACK`: `disabled`
- `VERDICT`: `GREEN for fail-closed blocker packet`
- `RECUSAL`: `CLEAR`
- `PROPOSED_BLOCKER`: `CONFIRMED`
- `HIDDEN_EXECUTIONS_ALLOWED`: `NO`
- `RAW_OUTPUT`: `FRESH_CONTEXT_BLACK_BOX_PREFLIGHT_GLM_RAW_R1.txt`
- `RAW_OUTPUT_SHA256`: `8b78185392f6be961e7bc2f519e7c6306f535c27a94c056f510e6d32ab12070d`

## Judge conclusion

The judge confirmed that the frozen CLI is not scenario driven and that the
dynamic probe proves it ignores the declared workspaces while returning
identical hardcoded evidence. Proceeding would measure an actor's ability to
trigger a static replay, not the planned recovery behavior.

The judge requires a separately authorized product revision, a new frozen
candidate, a new black-box plan revision, new preflight hashes, and a new
independent review before hidden execution.

## Boundary

`GREEN` applies only to the correctness of stopping fail-closed. It is not a
GREEN black-box campaign, product-surface result, Gate 7 result, or execution
authorization.
