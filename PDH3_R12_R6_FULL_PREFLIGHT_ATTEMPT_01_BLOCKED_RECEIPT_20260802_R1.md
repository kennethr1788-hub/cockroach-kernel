# PDH-3 R12 R6 Full Preflight Attempt 01 — Blocked Receipt

- `STATUS`: `BLOCKED`
- `BLOCKER`: `REMOTE_EXTRACTED_SMOKE_FAILED`
- `UTC_CREATED`: `2026-08-02T12:06:09Z`
- `CAMPAIGN_ID`: `ck-pdh3-r12-preflight-r6-full-r2`
- `POD_ID`: `n3s5q9f8h3i2aj`
- `POD_NAME`: `ck-pdh3-r12-preflight-r6-full-r2-01`
- `PACKET_SHA256`: `044a13b0037650edbecce168da7f54e5ad260aafd0c104cd1a3a1056cb9d40d9`
- `GLM_RAW_SHA256`: `4819a3d5180292b6d9fc283b5ba80e92964177909e8c543a4d4f38e665f0f179`
- `ARCHIVE_SHA256`: `018ed0af97b7e533ad6fdec316db006c1990628dcab2a94c42980c199cbfa2ae`
- `WORKER`: Secure Cloud L40S, `US-MO-1`, 32 provider vCPU, 125 GiB RAM, `$0.99/hour`

## Timeline

- Lifecycle bound: `2026-08-02T11:54:14Z`
- Worker ready before upload: `2026-08-02T11:54:35Z`
- Last observed heartbeat: `2026-08-02T11:55:24Z`
- Host terminal BLOCKED: `2026-08-02T11:55:42Z`
- Teardown GREEN: `2026-08-02T11:55:57Z`

## Direct Results

- `PF4_CREATE`: GREEN.
- `PF4_CAPABILITY`: GREEN.
- Main bundle upload began; replacement was forbidden for this campaign from that point.
- Remote archive transfer and extraction completed.
- The extracted-bundle smoke returned nonzero with `EXTRACTED_BUNDLE_SMOKE_BLOCKED`.
- Full-cardinality setup did not begin.
- No measured checkpoint was emitted (`last_checkpoint_sequence=0`).
- The 24-hour measured clock did not begin.
- The worker was deleted. Exact Pod lookup returned provider `404`; campaign-scoped active inventory was empty.

## Evidence Hashes

| Evidence | SHA-256 |
|---|---|
| `attempt-01/lifecycle.ndjson` | `ac8b5a926ff01be88b1b4a07bd42e31bf78bede2272eceb9cf7f59d6078f7ebf` |
| `PF4_HOST_RECEIPT.json` | `22e264bd2ec71d8b5735984f27dce3160fc8da7134c86f8fd3f56f6209f899bd` |
| `PF4_CAPABILITY_RECEIPT.json` | `fcbeed3c262d3963c2aca82cc40cfa61cb6317ffe1200255d053c1aa162c7c73` |
| `ORCHESTRATOR_BLOCKED.json` | `53cda24ba46953ad876274246675966c7911c8a227416563cd4e1294e9c67cf6` |
| `PF8_HOST_TERMINAL.json` | `011b5adf5ee01779e2f0a42ae8c488962e225c8e873acd03a5e94ba1610d3cf2` |
| `main-bundle-upload-started.json` | `3e0f148c82d507db2513f8e029d3d85abf441d38fb41c25c86dbeb3fc38087e4` |
| `remote-smoke.stderr` | `a3ff47aed710ef1bbae49f1c0e56d175aa626ff45ee5adb4e26c0194d32d1499` |
| `remote-smoke.stdout` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Root Cause and Evidence Limitation

The remote smoke implementation wrote a detailed receipt before returning nonzero, but the host runner raised on the nonzero process status before retrieving that receipt. The lifecycle then correctly deleted the worker. Consequently, this attempt proves that one or more extracted Linux smoke checks failed, but it cannot identify which check. It is not durability evidence and cannot be relabeled as a workload result.

The prospective repair must preserve bounded per-check diagnostics, retrieve and validate the remote receipt before interpreting the command status, and close each retry under a fresh reviewed packet. This failed attempt remains immutable evidence.
