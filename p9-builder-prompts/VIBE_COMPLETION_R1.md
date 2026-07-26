# Sanitized Vibe P9 completion reliability task

Work only in this clean isolated Git worktree. Read
`P9_COMPLETION_CONTRACT_R1.md`, `P9_COMPLETION_BUILDER_ASSIGNMENTS_R1.md`, and
the existing `p9-cloud/` reliability/fault tests. Create only:

- `p9-cloud/test_completion_reliability.py`

Write bounded standard-library unittest coverage for the completion contract's
fault matrix using existing `records.py`, `retry.py`, `faults.py`,
`mock_transports.py`, and where present `coordinator.py`. Cover 40001 bounded
retry/exhaustion, duplicate idempotency, stale/out-of-order/hash mismatch,
changefeed duplicate/lag/restart/projection mismatch, Lambda timeout/throttle/
malformed/stale/hash mismatch/unavailable, MCP unknown/oversized/write refusal,
injection, denial-of-wallet, and fixed operation/call ceilings. Tests must be
deterministic and perform no network, cloud, browser, credential, HOME, MCP,
RunPod, subprocess, shell, or live SQL action.

Do not edit production source, contracts, packets, receipts, schemas, or other
tests. Do not alter thresholds to manufacture a pass. Run the relevant Python
unittest suite and commit the one-file contribution normally. Do not judge or
claim a gate.
