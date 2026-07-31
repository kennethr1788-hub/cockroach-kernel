# PDH-1 Harness Repair Independent Preflight Packet R1

## Decision requested

Return `GREEN` or `BLOCKED` for one complete 30-execution PDH-1 campaign. Judge
only the evidence harness repair and frozen boundary. Do not propose product
code or implementation direction.

## Unchanged authority

- Product candidate:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- PDH-0 packet:
  `17687d96e46002adca0f712a5b6355bac897e7d11ae11f6e2e5e0fca530f0006`
- PDH-0 independent result: `GLM_5_2_GREEN`
- Product behavior changes: none
- Input matrix changes: none
- Outcome mapping changes: none
- Threshold changes: none
- Paid/cloud authority: none

## Preserved failures

The first 30-execution attempt failed before product import. Its controller had
called `Path.resolve()` on the virtual-environment Python launcher. Because the
launcher is a symlink, that selected the base interpreter and discarded the
candidate installed in the venv. All 30 results were classified
`INFRASTRUCTURE_INVALID`; every disposable root was torn down.

- Full blocked receipt SHA-256:
  `f693c77c087f5489ab31a2a66379ca099a72b064fcead44155d808f7d1ba205f`
- Diagnostic canary attempt 1 blocked receipt SHA-256:
  `b4552c48d43fa8b8a59cc1f93b0e1ff56892036c667316b0ba2a261c89960861`
- Root cause:
  `ModuleNotFoundError: No module named 'cockroach_kernel'`

Neither attempt exercised product recovery behavior and neither counts toward
the measured denominator.

## Narrow repair

The evidence-only controller now preserves the absolute venv launcher path
without resolving its symlink. It also:

- records path-scrubbed stdout and stderr for fail-closed diagnosis;
- accepts an explicit public-canary case/repeat selection;
- distinguishes canary from full-campaign status;
- preserves an explicit receipt filename so failed receipts cannot be
  overwritten.

Controller:
`post-dogfood/run_pdh1_information_boundary.py`

Controller SHA-256:
`3ef65df94c654cd183fbae5c5fbf4b566c79f7109e369484d90fc254fd22a6d9`

## Public canary

One B1 execution in a fresh detached candidate worktree and candidate-only venv
returned:

- status: `PDH_1_INFORMATION_BOUNDARY_CANARY_GREEN`
- exit: `0`
- evidence class: `RECOVERED_EXACT`
- product result: `PROMOTE / MAX_PROVEN_PREFIX`
- workspace bytes: exact
- fresh-context result: `FRESH_CONTEXT_PASS`
- network used: `false`
- credentials used: `false`
- teardown: root absent
- canary receipt SHA-256:
  `7533807e9a7a2b686d23a072db6ed0bac261f2619c2a5c1d47ded2f932ef5490`

## Full-campaign boundary

The next execution must run exactly B1–B6, five fresh roots per case. It must
preserve the failed attempts, use the same frozen candidate, run every product
invocation under the network-denied Seatbelt profile, keep the B4 oracle in
controller memory only, and stop before PDH-2. No post-result tuning is
authorized.

## Required response

Return raw JSON only:

```json
{
  "verdict": "GREEN|BLOCKED",
  "packet_sha256": "<exact supplied packet hash>",
  "repair_scope": "SUPPORTED|UNSUPPORTED",
  "failed_evidence_preserved": "SUPPORTED|UNSUPPORTED",
  "full_campaign_boundary": "SUPPORTED|UNSUPPORTED",
  "blockers": [],
  "non_blocking_risks": []
}
```
