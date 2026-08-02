# PDH-3 R12 R6 Full Preflight Attempt 02 — Blocked Receipt

- `STATUS`: `BLOCKED`
- `BLOCKER`: `REMOTE_EXTRACTED_SMOKE_FAILED`
- `FAILED_CHECK`: `post-dogfood/test_pdh3_local_canary.py`
- `ROOT_CAUSE`: `MACOS_PRIVATE_TMP_LITERAL_ON_LINUX`
- `UTC_CREATED`: `2026-08-02T12:21:33Z`
- `CAMPAIGN_ID`: `ck-pdh3-r12-preflight-r6-full-r3`
- `POD_ID`: `vp1qs5vg9e2rg8`
- `PACKET_SHA256`: `938d8c1c34c4ca73986a60b1d18f8c8149c80c20628258dd5d88247d496fda64`
- `ARCHIVE_SHA256`: `333488646b1635f2979373512a4d577c0a28a1272345a065d9904f8cd51d59f8`
- `WORKER`: Secure Cloud L40S, `US-MO-1`, 32 provider vCPU, 125 GiB RAM, `$0.99/hour`

PF-4 creation and capability were GREEN. The repaired v3 smoke receipt was retrieved and validated before teardown. It proves exactly one failed check: the test created its synthetic teardown root under the macOS-only literal `/private/tmp`, which is absent on Ubuntu. The underlying check did not reach product workload execution. Full-cardinality setup did not begin, no measured checkpoint was emitted, and the 24-hour clock did not begin.

The worker was deleted. Exact Pod lookup returned provider 404 and active campaign inventory was empty.

| Evidence | SHA-256 |
|---|---|
| `PF8_HOST_TERMINAL.json` | `11af3bfc685a5c5104905e258df06d7aff65b4ef661c2e9d40c9c0735c83d098` |
| `remote-smoke.json` | `5c26cd75cb585051cc9dc0ae6019d4490be56beb81411a2cd75207fbf84fd8be` |
| `remote-smoke-host-diagnostic.json` | `b897e15feb9e09457d84b193a985e0ea82d34175a81ff8e08e4626778d77877f` |
| `ORCHESTRATOR_BLOCKED.json` | `16d94bd3e883ce0a03b30e4b5f3e3e02fc75292a41fec8dffab349caa8edbf22` |
| `main-bundle-upload-started.json` | `43daeec55384ac6fe277dc52f60befa1a634d8911ea21ef95ad4fa9eda384039` |
| `attempt-01/lifecycle.ndjson` | `c82b4dae721423300a6458cd607bf521f3dd8bcbf31ded1033469c21cb34d365` |

The prospective correction is restricted to one platform-stable generated-root constant: `/tmp` on Linux and `/private/tmp` elsewhere. Both execution and the affected test must use the same constant. No cardinality, threshold, query, evidence, or teardown requirement may change.
