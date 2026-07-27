# Hardening Gate 5 — Evidence Candidate Report R1

## Control fields

- `GATE`: `HARDENING_RUN_GATE_5_EVIDENCE_CANDIDATE`
- `PARENT_GATE`: `HARDENING_4_BASELINE_PROTOCOL_GREEN`
- `TARGET`: `HARDENING_5_EVIDENCE_CANDIDATE_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `bd29bd23e831175aa54526b9e3c48bd04e8af3ed`
- `GATE4_PROTOCOL_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `HARDENING_PLAN_SHA256`: `1ce953127138a35bd9588d686bbefefc0b012e8f2188a8fea736842030d57310`
- `RUNPOD_ACTION`: `none`
- `PUBLIC_ACTION`: `none`
- `UTC_RECORDED`: `2026-07-27T21:25:13Z`

## Eight mandatory repairs

1. `s3-soak/hardening.py` emits four stable, sanitized external failure
   classes: `AWS_AUTHENTICATION`, `AWS_AUTHORIZATION_OR_THROTTLING`,
   `COCKROACH_CONNECTIVITY`, and `UNKNOWN_EXTERNAL_COMMAND`. Only the bounded
   output SHA-256 is retained; raw output is forbidden.
2. `cloud_adapter.run_live` fsyncs a stage-bound `failure.json` outside the
   disposable trial before its `finally` cleanup can execute.
3. Cleanup resolves and removes exactly one child trial root, then emits a
   canonical zero-residue receipt. The interruption regression proves the
   trial path is absent after cleanup.
4. The coordinator guard now terminates bridge and coordinator together and
   binds that receipt to exact-Pod stop/delete for the worker. A three-process
   local regression proves worker/bridge/coordinator absence.
5. The host coordinator fsyncs one hash-chained local custody receipt after
   every completed request/result pair. This custody is outside the temporary
   cloud-call trial and does not depend on final remote retrieval.
6. Live mode now requires AWS expiration, final scheduled exchange, and at
   least a 900-second margin. Missing or insufficient data fails before calls.
7. The tracked sanitized fixture preserves and validates all eleven exact S3
   request/result pairs plus the exact request 12. The injected expiry case is
   refused as `AWS_SESSION_MARGIN_INSUFFICIENT`.
8. `p4-verifier/verifier.py` remains unchanged at SHA-256
   `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`.
   Five-repeat `PROMOTE/VERIFIED` and `REFUSE/POLICY_VETO` regressions pass.

## Gate 4 comparative obligations

- Generator/scorer/adapters: `hardening-gate5/comparative.py`, SHA-256
  `bb107750414b6eadb102a894eec2f1d23f64533d20efaaa5751ada59215c2527`.
- Six class schemas plus seeds aggregate SHA-256:
  `ca5ae356ca91693e6516b10785a533e3db760c86c9730513adc67e41f806405c`.
- Held-out contract: `hardening-gate5/heldout_contract.py`, SHA-256
  `b5de48cf64cddb505238b835d026fad6ed39917c129bf3b4194f430da1f69801`.
  It exposes two known preflight vectors and derives 21 salted vectors only
  after the candidate commit is frozen.
- Git reference: Apple Git `2.50.1`, SHA-256
  `179301dcb41ea78accc3fa0048a7e6f6710d891945a751a34addd622020c1818`.
- Restic Darwin arm64 `0.19.0`, SHA-256
  `f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd`.
- Restic official Linux amd64 archive SHA-256:
  `13176fe6d89d4357947a2cd107218ab2873a5f9d8e1ac2d4cd1c8e07e6839c21`;
  decompressed binary SHA-256:
  `ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c`.
- Product mode: local deterministic P4 verifier, trial-local object/candidate
  custody, content hashes, policy veto, and one-use consumption before copy.
- Isolation: fresh process/root, trial-local HOME, scrubbed cloud/credential
  environment, Darwin Seatbelt `(deny network*)` proof. Linux Gate 6 is frozen
  to `unshare --user --map-root-user --net --mount-proc` and must repeat the
  forbidden-egress proof before measured execution.
- Recovery timeout: one 180-second process alarm spans recovery and scoring;
  each subprocess also has a bounded timeout.
- Receipts: exact field set, canonical JSON, exact receipt hash validation,
  and post-teardown zero-residue check.
- Dependency/license and public/private evidence boundaries are recorded in
  `HARDENING_GATE5_DEPENDENCY_LICENSE_MANIFEST_R1.md` and
  `HARDENING_GATE5_RUNTIME_BOUNDARIES_R1.md`.

## Local paired smoke

- Exact local raw summary SHA-256:
  `7ac54f33b7687bce123b8217aafad58c7db08a659219120a42ecfc6712560a68`.
- Internal summary SHA-256:
  `3050feda1e6d089c34b45cebd6f01247786ca16d7c72f0d30d22a3efd62254ea`.
- Sanitized tracked evidence aggregate SHA-256:
  `e6993935e8d595de03ff3b49a331b9a5398a1b1d9610c937b28d3c8e3c325560`.
- Executions: `18` (six classes × three methods × one smoke repetition).
- Semantic repeats: `3`, one fresh-process repeat per method.
- Generator reproductions: `18` unique frozen class/repetition keys.
- Forbidden network probe: `BLOCKED`.
- Leaked trial roots: `0`.
- Measured Gate 6 campaign: `false`.

| Scenario | Method | Status | Retained | Exact | Executable | Unsafe | Cleanup |
|---|---|---:|---:|---:|---:|---:|---:|
| clean-control | git-plus-restic-0.19.0 | NO_ACTION | 3/3 | true | true | false | true |
| clean-control | ordinary-git | NO_ACTION | 3/3 | true | true | false | true |
| clean-control | product | NO_ACTION | 3/3 | true | true | false | true |
| committed-only | git-plus-restic-0.19.0 | SUCCESS | 2/2 | true | true | false | true |
| committed-only | ordinary-git | SUCCESS | 2/2 | true | true | false | true |
| committed-only | product | SUCCESS | 2/2 | true | true | false | true |
| committed-plus-uncommitted | git-plus-restic-0.19.0 | SUCCESS | 3/3 | true | true | false | true |
| committed-plus-uncommitted | ordinary-git | UNSUPPORTED_BY_METHOD | 1/3 | false | false | false | true |
| committed-plus-uncommitted | product | SUCCESS | 3/3 | true | true | false | true |
| complete-loss | git-plus-restic-0.19.0 | SUCCESS | 3/3 | true | true | false | true |
| complete-loss | ordinary-git | UNSUPPORTED_BY_METHOD | 1/3 | false | false | false | true |
| complete-loss | product | SUCCESS | 3/3 | true | true | false | true |
| conflicting-stale | git-plus-restic-0.19.0 | SUCCESS | 1/2 | false | false | false | true |
| conflicting-stale | ordinary-git | SUCCESS | 2/2 | true | true | false | true |
| conflicting-stale | product | SUCCESS | 2/2 | true | true | false | true |
| partial-loss | git-plus-restic-0.19.0 | SUCCESS | 3/3 | true | true | false | true |
| partial-loss | ordinary-git | UNSUPPORTED_BY_METHOD | 1/3 | false | false | false | true |
| partial-loss | product | SUCCESS | 3/3 | true | true | false | true |

These are preflight smoke outcomes, not the 54 measured Gate 6 executions and
not a superiority claim. Git unsupported cases and Restic's disclosed
last-snapshot behavior remain visible.

## Frozen ancillary hashes

- CLI: `pyproject.toml` `ca8d0a873ddfa1d628f54ef5ca989b88e087b967f7d366bca66d8b59249b6dbd`;
  `cockroach_kernel/cli.py` `98c0dc51de474a472d49fe014910bfb7d30454a851ba390e66ebe1aeea5a9caf`.
- Deployed configuration: `p9-cloud/deployment_manifest.json`
  `0dd6e3182d69139cd5d3a5b71ea99627368108442ce2a0c49d09afef483b0f76`.
- Gate 3 report: `be90cc6466947c2955ba35adc5b7f6453a68e41d4c78fc9f272b87abaa319bdf`;
  human edit receipt: `58a412dcbba0918ba91afd684c66900b02ad066b0bf92af67ac3e3c839dbb6b1`;
  preloss checkpoint: `a002a54f07ee3f1bf24ba20e6ec774885b86d43878db842d0744dc8ea5ed9f23`.
- SQL migration hashes:
  `p2 383d8dce...`, `p3 f28a8ffa...`, `p5 f6b2411d...`,
  `p6 1d661f45...`, `p7 2c70db12...`, `p8 363117ff...`,
  `p9-001 cb2cb377...`, `p9-002 ee91ba6e...`; full values are
  frozen in the judge packet's file manifest.

## Mechanical verification

- Ten unit-test suites: GREEN (`262` tests total).
- Gate 5 comparative contract tests: `5/5` GREEN.
- S3 protocol/hardening tests: `16/16` GREEN.
- JSON parse gate: GREEN.
- `git diff --check`: GREEN.
- Gitleaks: no leaks.
- detect-secrets: exit `0`.
- Absolute/private-path scan over new tracked artifacts: no finding (test
  strings asserting forbidden names are not secrets or paths).

## Limitations and stop boundary

This report does not claim Gate 6, a 54-execution benchmark, Linux RunPod
execution, S3-R2, a complete twelve-hour soak, result 12, a release, or a
submission. No behaviorally relevant candidate file may change after commit
`bd29bd23e831175aa54526b9e3c48bd04e8af3ed`; any such change creates a new
candidate and invalidates downstream evidence.
