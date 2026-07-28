# Hardening Gate 6 R3 — Tool Provenance Path Correction

- `STATUS`: `CORRECTED_BEFORE_PROVIDER_CREATION`
- `SUPERSEDED_PACKET_SHA256`: `4f598020da961385056d9a6a3f22d03b849624cfa8458fcc48f56bddb3c4620d`
- `OLD_PROVENANCE`: `HARDENING_GATE6_LINUX_TOOL_PROVENANCE_R2.json`
- `NEW_PROVENANCE`: `HARDENING_GATE6_LINUX_TOOL_PROVENANCE_R3.json`
- `NEW_PROVENANCE_SHA256`: `6d1def307f36102e54778a6c7ef240ebb0375ed4c4aaf6536a33cd194b54eb3b`
- `RESTIC_BINARY_SHA256`: `ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c`
- `RUNPOD_CREATED`: `no`
- `MEASURED_EXECUTIONS`: `0`
- `UTC_RECORDED`: `2026-07-28T02:12:00Z`

The R2 provenance file correctly described the same pinned Restic bytes but
bound its absolute path to the R2 campaign root. R3 wiring passes the R3
campaign root, and `run_campaign.py::validate_tools` compares that path exactly.
Leaving the mismatch would cause `RESTIC_PROVENANCE_DRIFT` before measurement.
The correction changes only the execution revision and Restic absolute path;
the Git, Restic, Python, product, image, package, archive, and binary hashes are
unchanged. The R3 wiring now passes the R3 provenance file. The prior judge
verdicts are stale because the packet hash must change.
