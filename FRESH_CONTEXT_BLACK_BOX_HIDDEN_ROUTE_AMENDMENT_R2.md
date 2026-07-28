# Hidden Campaign Actor Route Amendment R2

- `STATUS`: `PROPOSED_REPAIR_PENDING_INDEPENDENT_REVIEW`
- `PRESERVES_R1_BLOCKER`: `YES`
- `ACTOR_ROUTE`: `local Ollama 0.30.11`
- `MODEL`: `qwen2.5-coder:7b`
- `MODEL_DIGEST`: `dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364`
- `MODEL_CLASS`: `Qwen2.5 Coder 7.6B / Q4_K_M / 32768 context`
- `IDENTITY_PROOF`: `live /api/tags digest plus response.model on every request`
- `SESSION_ISOLATION`: `one stateless /api/generate request; no context supplied or reused; controller-unique session ID`
- `TOOLS`: `none exposed`
- `NETWORK_EGRESS`: `loopback only`
- `PRIVACY`: `synthetic prompt remains local`
- `INCREMENTAL_COST`: `$0`
- `KEEP_ALIVE`: `0; unload after request`
- `RUN_COUNT`: `unchanged 18 valid sessions`
- `RETRY_LAW`: `unchanged`
- `OPERATOR_AUTHORIZATION`: `Kenneth authorized the hidden campaign generally before this route repair; the R2 route is local, zero-cost, and no-egress, but was not named verbatim in his authorization text`
- `HIDDEN_SEED_CREATED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`

This narrows the authorized privacy and cost surface and repairs the missing
served-model identity proof. It does not change the product, scenario matrix,
threshold, scorer, evidence standard, or final independent review.
