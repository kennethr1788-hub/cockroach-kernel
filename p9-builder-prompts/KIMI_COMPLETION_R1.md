# Sanitized Kimi K3 P9 completion task

Work only in this clean isolated Git worktree. Read
`P9_COMPLETION_CONTRACT_R1.md`, `P9_COMPLETION_BUILDER_ASSIGNMENTS_R1.md`, and
the existing `p9-cloud/` source/tests. Implement only:

- `p9-cloud/coordinator.py`: a standard-library-only, no-network coordinator
  core with the exact 12-operation enum frozen in the contract, strict
  canonical JSON/unknown-field rejection, identifier and 16 KiB bounds,
  sequence/parent hash-chain validation, replay protection, and deterministic
  trial fixtures for `ck-p9-live-promote-r1` and
  `ck-p9-live-refuse-r1`.
- `p9-cloud/test_coordinator.py`: bounded unit tests proving valid sequencing,
  distinct fixtures, unknown/dynamic operation refusal, stale/duplicate/out-of-
  order/hash mismatch refusal, oversize refusal, and no cloud verdict authority.

Do not edit contracts, packets, receipts, migration/schema, existing authority
logic, or any file outside those two paths. Do not use credentials, browser,
cloud, MCP, RunPod, HOME, private data, network clients, subprocess, dynamic
SQL, shell, URL, ARN, path, or commands. The output is untrusted contribution
code; do not judge or claim a gate. Run the relevant Python unittest suite and
commit your two-file contribution normally.
