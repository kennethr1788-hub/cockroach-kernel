# Gate 7 Run 5 Public Canary R1 Blocked Receipt

- `STATUS`: `BLOCKED`
- `CAMPAIGN_ID`: `ck-g7r5-public-collision-r1`
- `HIDDEN`: `false`
- `RUNPOD_WORKER_CREATED`: `false`
- `TERMINAL_BLOCKER`: `VECTOR_CLEANUP_TIMEOUT_BATCH_77`
- `EXCEPTION_TYPE`: `TimeoutExpired`
- `FAILURE_RECEIPT_SHA256`: `e8040ed2d2d1e7feb3964fcbf25067c6886fb532d87f53632c7045edf5e9d0a0`
- `TERMINAL_RECEIPT_SHA256`: `06f499afafa1802de878a7e54df635822fc0ea99c3b9c9d86a3e5901ed6f410f`
- `CLEANUP_RECEIPT_SHA256`: `38aefa1c1e13b5adf5c056b848ee21c090fb35cff17b3593a4b51dc1471c2f71`
- `CLEANUP_STATUS`: `PASS`
- `CLEANUP_BATCHES`: `107`
- `CLEANUP_MS`: `88375`
- `CANONICAL_RESIDUE`: `[0,0,0,0]`
- `DIRECT_RESIDUE`: `[0,0,0,0]`
- `DIRECT_RESIDUE_OUTPUT_SHA256`: `58d9fffe639ec31e34a1032bd727a05a5b7d6983881706d28a39c24cd03a31bb`
- `CREDENTIAL_BYTES_RECORDED`: `false`

The original live execution completed insertion and 200 queries. Cleanup batch
77 exceeded the generic 120-second subprocess timeout, so the original canary
correctly emitted `BLOCKED`. Its fail-closed cleanup path then ran the complete
107-batch plan and both the canonical receipt and an independent host-only
campaign-prefix query proved zero residue.

R1 remains immutable blocked evidence. It cannot be relabeled GREEN. The narrow
pre-hidden repair applies the existing 300-second vector batch timeout to vector
cleanup while retaining the 120-second bound for non-vector cleanup. A new
campaign ID and fresh live public canary are required before packet freeze.
