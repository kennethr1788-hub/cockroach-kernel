# Hardening Gate 6 — Local Preflight Receipt R2

- `STATUS`: `LOCAL_PREFLIGHT_GREEN_NOT_PROVIDER_EVIDENCE`
- `EXECUTION_REVISION`: `R2`
- `PARENT_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `RUNPOD_WORKERS_CREATED`: `0`
- `RUNPOD_ACTIVE_INVENTORY`: `[]`
- `RUNPOD_COST_STATE`: `EXACT_$0.00_FOR_GATE6_R2`
- `UTC_RECORDED`: `2026-07-28T00:27:00Z`

## Mechanical results

- Gate 6 orchestration unit tests: `3/3 PASS`.
- Broader non-live regression: `267/267 PASS` across `23` test files.
- Test-log manifest SHA-256:
  `e36c14c85341d4c2c915200224b03a670a2b6d7eefdbff271d3333e46145a41e`.
- Exact-candidate local paired profile: `18/18` canonical preflight receipts,
  plus `3/3` semantic determinism repeats.
- Local network-denial probe: `BLOCKED` under macOS `sandbox-exec`.
- Local profile elapsed time: `91.13 seconds`.
- Local profile maximum RSS: `98,598,912 bytes`.
- Linear 54-run time estimate: approximately `273.39 seconds` before remote
  setup/custody overhead; selected 2-vCPU/4-GiB CPU class remains sufficient.
- Profile internal summary SHA-256:
  `741d8dfe032033090a2877db93d273375fba36476acddd4d6ade11566b233465`.
- Profile canonical summary file SHA-256:
  `d5dbf4e4b3afdc768746b822a7fbc6314ab8ab2c6178920c672f6b4c3d982e10`.
- Exact 54-row manifest validation: `PASS`.
- Manifest embedded SHA-256:
  `ffbe59a0fa569d9a1cfd1aa6247490a7606ab20a362a072b0d19ca5879ba3b07`.
- Manifest file SHA-256:
  `80d9f88df8b7d2636e7e81e8f8f3cd8f7c98a898bf57d30f51ea2cf2fb1349a7`.
- `git diff --check`: `PASS`.
- Gitleaks: `0` findings.
- detect-secrets: `0` findings.
- New-file private-path scan: `0` private paths; the single literal
  `credential` occurrence is explanatory policy text.

## Candidate and runtime custody

- Frozen comparative SHA-256:
  `f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec`.
- Frozen deterministic verifier SHA-256:
  `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`.
- Gate 4 R2 protocol SHA-256:
  `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`.
- Current Docker registry index and Linux amd64 manifest digests match the
  exact previously reviewed RunPod base image.
- Official Ubuntu Git package SHA-256:
  `8794fcf2c4606c445df0db3dc963c8fb852772208bfb12727a12717c03767af7`.
- Extracted Ubuntu Git executable SHA-256:
  `587ef21868c948b883993e23209b86a72a6ddc06aab1545c697ffc31075acd4a`.
- Official Restic Linux archive/binary hashes match the Gate 5 allowlist.
- Python's expected hash is bound to a prior direct runtime attestation from
  the same immutable image digest and must be reverified remotely before any
  measured row. A mismatch blocks after upload and cannot trigger replacement.

This receipt is not Linux, measured, RunPod, Gate 6, or superiority evidence.
It authorizes only packet freeze and independent preflight review.
