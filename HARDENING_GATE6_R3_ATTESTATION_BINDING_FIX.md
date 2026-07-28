# Hardening Gate 6 R3 — Attestation Binding Fix

- `STATUS`: `LOCAL_FIX_GREEN_AWAITING_INDEPENDENT_PREFLIGHT`
- `FAILED_ATTEMPT`: `e5bvtk4s4y7yc0; DELETED`
- `OLD_RUNNER_SHA256`: `f86388fe4ee8c677bd8a7699b0595d7b1e1c92bc681eea047643b1d4df2b88a4`
- `NEW_RUNNER_SHA256`: `9ad46f17706ac1ec931ae6084a41faac98802561190efa3031e7595eff13c2f3`
- `TEST_FILE_SHA256`: `c04e34fa447575a87eb7fae3788379624913c0cfcffbe966093851d8d730fae6`
- `R3_TESTS`: `6/6 PASS`
- `FULL_REGRESSION`: `273/273 PASS ACROSS 24 TEST FILES`
- `FULL_REGRESSION_MANIFEST_SHA256`: `316307b3f95ddf1676b1e553a26c5aad2e151bf9e64da7e4ddce187aecc44075`
- `RUNPOD_RUNNING_INVENTORY`: `[]`
- `UTC_RECORDED`: `2026-07-28T02:26:34Z`

`seccomp_exec.py` writes canonical JSON containing `attestation_sha256`, the
SHA-256 of the canonical record body without that field, and exports that value
to the executed child. The old validator incorrectly demanded that the whole
file SHA-256 equal the embedded body hash. The fix loads the absolute regular
file, requires its bytes to equal the canonical serialization of the parsed
record, recomputes the body hash, and requires both the embedded value and the
exported claim to equal it. Whole-file SHA-256 remains custody metadata only.

Regression tests prove that the expected file hash and record hash differ,
canonical valid records pass, noncanonical encodings fail, and wrong exported
claims fail. No candidate, scenario, comparator, verifier, manifest, seccomp
filter, tool bytes, or acceptance semantics changed.
