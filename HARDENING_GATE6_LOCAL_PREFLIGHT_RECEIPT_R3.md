# Hardening Gate 6 — Local Preflight Receipt R3

- `STATUS`: `LOCAL_PREFLIGHT_GREEN_NOT_PROVIDER_EVIDENCE`
- `EXECUTION_REVISION`: `R3`
- `PARENT_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `RUNPOD_WORKERS_CREATED_R3`: `0`
- `RUNPOD_ACTIVE_INVENTORY`: `[]`
- `RUNPOD_COST_STATE_R3`: `EXACT_$0.00`
- `UTC_RECORDED`: `2026-07-28T01:22:12Z`

## Mechanical results

- R2 plus R3 Gate 6 unit tests: `7/7 PASS`.
- Broader project regression: `271/271 PASS` across `24` established test
  files, including the new R3 tests.
- Test-log aggregate SHA-256: `5cc6b7e67108086cb3921e7ca834c621cdc358b67de1faff8b63fb4101ac1436`.
- Exact 54-row R3 manifest validation: `PASS`.
- Manifest embedded SHA-256:
  `1e73682e0eb880c95f5826d731cf6c1b6fe1f61e342bfb2d36c7fd1d3600d711`.
- Manifest file SHA-256:
  `a4c7c12c135475b712199916a8257b90543a1dd2b346e15bb6519f1d9ec80d3d`.
- Python byte compilation: `PASS`.
- `git diff --check`: `PASS`.
- Candidate comparative/verifier/scenario diff from candidate commit: empty.
- Current RunPod running inventory: empty; Gate 6 campaign-scoped active
  inventory: empty.

## Platform limitation

The local host is macOS arm64 and cannot execute the Linux x86_64 seccomp
filter. Local tests validate the BPF instruction structure, foreign-architecture
kill branch, syscall deny coverage, R3 manifest, and fail-closed attestation
wall. Direct kernel proof remains mandatory in the capability-only RunPod
canary before benchmark upload. This receipt is not Linux, RunPod, measured,
network-denial, or Gate 6 completion evidence.
