# Hardening Gate 5 — Portability Repair Evidence Report R2

## Control fields

- `STATUS`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `PARENT_GREEN_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_GREEN_R1`
- `BLOCKER_BEING_REPAIRED`: `EVIDENCE_CANDIDATE_INVALIDATED`
- `TARGET`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `CANDIDATE_PARENT_COMMIT`: `381e74fa5f6c1d55a743b6ccabf4c4674618eee2`
- `CANDIDATE_DIFF_SHA256`: `662980134ae0ab7516478b5247588940d21e4d2b609806407e72be0760b6231e`
- `GATE4_PROTOCOL_R1_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `GATE4_PROTOCOL_R2_SHA256`: `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `HARDENING_PLAN_SHA256`: `1ce953127138a35bd9588d686bbefefc0b012e8f2188a8fea736842030d57310`
- `RUNPOD_ACTION`: `none`
- `PUBLIC_ACTION`: `none`
- `UTC_RECORDED`: `2026-07-27T22:49:43Z`
- `FINAL_JUDGE_PACKET_SHA256`: `41efeb9270b76a0d4e1f711d5b1ab3270ecd92d32eccce93f07bef8a6ba036c0`
- `GLM_JUDGE`: `GLM_5_2_GREEN_GATE4_AND_GATE5`
- `CLAUDE_JUDGE`: `CLAUDE_OPUS_4_8_GREEN_RECUSAL_CLEAR`

## Exact repair

The R1 candidate remains historical and invalid for Linux Gate 6. R2 changes
only the portability and evidence-mode contract that caused the blocker:

1. Scenario bytes now embed the platform-neutral command
   `["python3","tests/check.py"]`; no absolute interpreter path enters source,
   event, loss, or allowed-information hashes.
2. The interpreter is resolved from the isolated trial `PATH`, version-invoked,
   byte-hashed, used for the executable test, and recorded in every method's
   receipt.
3. `CK_GATE5_GIT` selects one exact Git binary. The same binary is used for all
   Git operations, version-invoked, byte-hashed, and recorded instead of
   unconditionally claiming Apple Git.
4. Restic accepts only the exact official Darwin arm64 or Linux amd64 0.19.0
   binary hash, and its observed version output must match the hash-specific
   allowlist.
5. Canonical receipts use schema `gate5-comparative-receipt-v2` with required
   `evidence_mode` and `runtime_platform` fields.
6. `MEASURED_GATE6` fails closed unless the runtime is Linux, candidate commit
   is 40 lowercase hexadecimal characters, and campaign ID begins
   `ck-gate6-`. Preflight and measured limitations are exact and disjoint.
7. The validator requires the correct tool-provenance key set for each method
   and 64-character lowercase SHA-256 values.

No scenario class, repetition, method, event order, loss operation, work unit,
expected result, score, timeout, authority rule, verifier byte, held-out vector,
or conventional-baseline capability changed.

## Frozen source and runtime hashes

| Artifact | SHA-256 |
|---|---|
| `HARDENING_GATE4_BASELINE_PROTOCOL_R2.md` | `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52` |
| `hardening-gate5/comparative.py` | `f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec` |
| `hardening-gate5/run_smoke.py` | `91ad388ef6d4972cc2c6a248dd147eb1d93a38515a2c6d645ccb395b28fb3de6` |
| `hardening-gate5/test_comparative.py` | `605b0346a08d7181b563f29eb819dada0618fe7c980cf372d60435ca2d46c50f` |
| `hardening-gate5/scenarios/seeds.json` | `e2116b9bbe68671072cc6419e494d722fb4e285493338421ea58a806676c6f6d` |
| `hardening-gate5/heldout_contract.py` | `b5de48cf64cddb505238b835d026fad6ed39917c129bf3b4194f430da1f69801` |
| `p4-verifier/verifier.py` | `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40` |
| official Restic Linux amd64 archive | `13176fe6d89d4357947a2cd107218ab2873a5f9d8e1ac2d4cd1c8e07e6839c21` |
| official Restic Linux amd64 binary | `ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c` |

## Mechanical evidence

- Parser/compile gate: PASS.
- Comparative contract tests: `7/7` PASS, including platform-neutral source,
  both evidence modes, Linux-only measured guard, candidate/campaign guards,
  and both Restic platform hashes.
- Broader non-live regression set: `264/264` PASS across 22 test files.
- Exact-candidate smoke: `18/18` canonical preflight receipts plus three
  semantic repeats, all from candidate
  `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`.
- Pair source/event/loss equality: `6/6` classes for the one-repetition smoke.
- Receipt schema/mode/candidate/protocol validation: `18/18`.
- Python provenance present: `18/18`; Git provenance present for all twelve
  Git-bearing receipts; Restic provenance present for all six Restic receipts.
- Network-denial probe: `BLOCKED`.
- Cleanup: `18/18`; residue bytes: `0`.
- Internal smoke summary SHA-256:
  `781531c80ce1415ca208c4f2119cb57be660db73276f556610f1b57dd83b7c1b`.
- Raw summary SHA-256:
  `f79137a47eac4a634044f8b5dec23e4e93c1a94e163b0343190a14c5aa6998d3`.
- Raw 22-file evidence manifest SHA-256:
  `f88a0d6f86d4f3e1b5c96d85f64e845da47a4790ae33b9d14838f54e36e1b487`.
- Tracked sanitized summary:
  `evidence/hardening-gate5-portability-r2/summary.json`.
- `git diff --check`: PASS.
- Gitleaks staged scan: no leaks. `detect-secrets` reported only six
  unverified high-entropy hexadecimal test/provenance hashes; no credential.

## Fail-closed boundary

This report does not claim Linux execution, Gate 6 measured evidence, a
54-execution campaign, product superiority, S3-R2, release, or submission.
Gate 6 must still verify the exact Linux Git/Python/Restic versions and hashes,
freeze them in its preflight packet, prove unprivileged network denial, and
obtain its separately required preflight reviews before any measured worker.
Any behaviorally relevant change after candidate commit `8718fbe` invalidates
new downstream evidence.

## Independent review

GLM 5.2 and exact Claude Opus 4.8 independently reviewed the same sanitized
packet hash. GLM returned overall GREEN with Gate 4 and Gate 5 individually
GREEN. Claude returned GREEN, no blockers, and `recusal_check=clear`. Their
limitations remain mandatory for Gate 6 and public claims.
