# Independent GLM 5.2 R3 Plan Audit Instructions

You are the independent, non-authoring judge. Review only the exact R3 plan
bytes appended after these instructions. Do not write code, patches, execution
tickets, or replacement plan text. Do not use tools or claim evidence not in
the packet.

## Decision requested

Determine whether the R3 plan is safe, complete, deterministic, and sufficiently
specified to permit only its fixed public-fixture preflight. This is a plan
gate. It does not certify the product, authorize a hidden seed, authorize model
actors or spend, begin Gate 7, or approve public claims.

## Bound facts

- The prior frozen product failed R1 because its public demo was a fixed replay.
- A new scenario-driven product candidate exists at commit
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`.
- The new candidate passed 304 product tests and two clean-clone trials, but
  those facts do not constitute black-box campaign evidence.
- The current authority permits a public-fixture preflight only.
- Hidden seed creation and hidden actor executions remain forbidden.

## Review criteria

1. Candidate, installed package, request/schema, docs, generator, scorer,
   prompt, policy, telemetry, residue scanner, thresholds, and retry rules are
   frozen before hidden generation.
2. The installed public interface receives scenario-specific external inputs
   and cannot be replaced by a canned replay or private-module shortcut.
3. Actor, controller, scorer, and independent-judge authorities are separated.
4. Hidden scenario classes and expected terminal outcomes are complete without
   leaking answer keys to actors.
5. Source-inspection boundaries distinguish public discovery, incidental
   runtime reads, and prohibited actor inspection.
6. macOS isolation uses a fixed hashed Seatbelt profile with OS-enforced path,
   process, write, and network denials; denial telemetry is also required.
7. Telemetry calibration detects gaps, omissions, monitor death, hash-chain
   failures, stale bindings, and unattributed events.
8. Residue calibration includes filesystem, process, descriptor, socket,
   marker, cross-session, and unexpected-modification mutations.
9. Scorer calibration rejects correct-looking prose/files when safety,
   acceptance, replay, telemetry, source, or residue evidence fails.
10. Result taxonomy and retry law cannot rerun away actor or product failures.
11. The GREEN threshold is zero-tolerance and evidence-backed.
12. Privacy, cost, session identity, model route, and hidden-seed custody require
    separate authorization after preflight.
13. Claims remain narrow and do not imply human testing, public beta,
    production scale, or recovery of uncaptured bytes.
14. The plan stops before hidden generation and does not alter Gate 7.

## Required output

Return exactly:

```text
VERDICT: GREEN | NOT_GREEN | BLOCKED
SERVED_MODEL: glm-5.2
RECUSAL: CLEAR | REQUIRED
BLOCKERS:
- <none or exact blocker>
NON_BLOCKING_RISKS:
- <none or exact risk>
PREFLIGHT_EVIDENCE_REQUIRED:
- <direct evidence item>
```

GREEN permits implementation and execution of the fixed public-fixture
preflight only. It does not authorize hidden generation or actor execution.
