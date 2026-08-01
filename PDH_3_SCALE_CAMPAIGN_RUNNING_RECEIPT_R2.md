# PDH-3 Replacement Campaign Running Receipt R2

- UTC verified: `2026-08-01T17:05:26Z`
- Campaign: `ck-pdh3-scale-r9-relaunch-r1`
- Pod ID: `qza6pmry5rnox4`
- Pod name: `ck-pdh3-scale-r9-relaunch-r1-01`
- Provider state: `RUNNING`
- Secure Cloud: `true`
- Worker: one NVIDIA L40S, 32 vCPU, 125 GiB RAM
- Compute rate: `$0.99/hour`
- Disposable container disk: `250 GB`
- Persistent/network volume: `0 / none`
- Packet SHA-256: `2909383cc13515102bf9b65c668cbca24ff9b409c7ce7660031ea8cd14e6573a`
- Bindings SHA-256: `5ae1006ff3cd567d5ad6f32204131a594dcb1cfeaab52ea144bbf5055e624c59`
- Transfer archive SHA-256: `1e50f4a9acf7e484b34126ae51c0425fbb908a7b520fdfab63fb72cad4fa0c76`
- GLM preflight: `GREEN`, served by GLM 5.2
- AGY preflight: `GREEN`, same packet hash
- Measured 24-hour clock status: `NOT_YET_PROVED_STARTED`

## Running controls

- Detached lifecycle guard PID: `81473`, PPID `1`, heartbeat advancing
- Remote traced controller PID: `683`, PPID `1`, status running
- Detached supervisor PID: `82889`, PPID `1`, status running
- Provider stop-after: `2026-08-02T20:42:15Z`
- Provider terminate-after: `2026-08-02T20:57:15Z`
- Exact-ID and campaign-inventory teardown remain mandatory

## Receipt bindings

- Frozen judge receipt: `92c2f254d6bc933267072d4b18dce279ee92226d8cc3e8c6d7320a165e0a36b9`
- Guard start receipt: `edf18c09102aa9097358faf310f3d51615257ce4185ef1f6d8a44db365b453b8`
- Remote launch receipt: `2ec2e29f69935c36d7c71c8c02bd71b46b25266c18ff076126567e091fe4ea5c`
- Supervisor start receipt: `6f23b6c1a7465bc000c7a130a5cb13f619743a9d2661200870074cd9b3095ff1`

## Current evidence boundary

This proves only that the exact hash-bound replacement worker, traced
controller, lifecycle guard, and supervisor are running. Target-cardinality
setup, three premeasurement epochs, the 24-hour measured workload, final
retrieval, provider teardown, and final independent review remain OPEN. No
campaign GREEN is claimed.
