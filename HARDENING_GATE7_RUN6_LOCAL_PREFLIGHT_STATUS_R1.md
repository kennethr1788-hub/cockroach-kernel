# Hardening Gate 7 Run 6 — Local Preflight Status R1

- `STATUS`: `RUN6_LOCAL_PREFLIGHT_GREEN`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `ORCHESTRATION_COMMIT_TESTED`: `d71163392091e69975cbd74104f45cd72bf00420`
- `PREFLIGHT_CONTRACT_SHA256`: `ebad36e2e87e9c043c30c328ed564655710344652cabc24c51b551fc0226a087`
- `LOCAL_RECEIPT_INTERNAL_SHA256`: `325744ba71f5263a4a8fcc8ca064e9447e91e47ceb7d2b0169a8018ec534c5e1`
- `LOCAL_RECEIPT_FILE_SHA256`: `019f39a04c6e984c337bf5dde153e3ebcb204b324819ff060e3c2e83f2cd5729`
- `SOURCE_BINDINGS_INTERNAL_SHA256`: `44afd2b2d15626642ed22eec525e039ea8f305f243797cd686c12c16b3a52cc9`
- `SOURCE_BINDINGS_FILE_SHA256`: `267f6870295f60a0f3fe68a06cb8a6f0172a70d91f312f7b07c1a23bf7f46332`
- `WORKER_BUNDLE_SHA256`: `77568eea6f33ec574a0a60c969c8a176f3f0c3024e9e5809ccf67438ec3e2890`
- `WORKER_BUNDLE_BYTES`: `144548380`
- `AWS_READINESS`: `GREEN; READ_ONLY; CREDENTIAL_BYTES_NOT_RECORDED`
- `COCKROACH_READINESS`: `GREEN; READ_ONLY`
- `PUBLIC_CANARY`: `84_OF_84_GREEN; NON_HIDDEN; NON_MEASURED`
- `EXTRACTED_BUNDLE_SMOKE`: `GREEN`
- `LIFECYCLE_GUARD`: `GREEN`
- `COORDINATOR_GUARD`: `GREEN`
- `ACTIVE_RUNPOD_INVENTORY`: `[]`
- `HIDDEN_SEED_EXISTS`: `NO`
- `RUNPOD_CREATED`: `NO`

Two earlier local invocations recorded AWS login pending because the project-local
AWS configuration and login-cache paths were not passed into the subprocess. A
third invocation proved cloud readiness but retained a stale console label. The
status emitter was repaired, retested, committed, and the fourth invocation is
the authoritative receipt above. None of those invocations created a worker or
hidden input.

Gitleaks found one false positive in the canonical receipt: the SHA-256 value
bound to the literal key `detect-secrets-receipt.json`. The match contained no
credential, token, secret, account identifier, endpoint, or private data.

This status authorizes construction of the sanitized same-hash GLM 5.2 and AGY
preflight packet only. It does not authorize worker creation until both judges
return GREEN on that exact packet hash.
