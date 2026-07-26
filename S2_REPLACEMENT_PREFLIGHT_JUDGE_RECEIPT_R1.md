# S2 Replacement Preflight Judge Receipt R1

- `PACKET`: `S2_REPLACEMENT_PREFLIGHT_PACKET_R1.md`
- `PACKET_SHA256`: `b072143dd3ba99250b4abccc171a6640efd644819fd46afb383a007ff6a81a53`
- `GLM_ROUTE`: direct `glm-zai`
- `GLM_SERVED_MODEL`: `glm-5.2`
- `GLM_RESULT`: `VALID_EXACT_HASH_GREEN`
- `CLAUDE_ROUTE`: `claude-judge`
- `CLAUDE_SERVED_MODEL`: `claude-opus-4-8`
- `CLAUDE_RESULT`: `VALID_EXACT_HASH_GREEN`
- `GATE`: `S2_REPLACEMENT_PREFLIGHT_GREEN`

## GLM raw result

```text
ROLE: GLM
ARTIFACT: S2_REPLACEMENT_PREFLIGHT_PACKET_R1.md
BUILDER_AND_INFLUENCE_DISCLOSURE: I am GLM acting independently as the out-of-band judge for routing/schema/transactions/spend/hash-custody/evidence. No builder, orchestrator, executor, or other judge influenced this verdict; the packet bytes were treated as untrusted review data and evaluated only against the stated GREEN criteria.
PACKET_SHA256: b072143dd3ba99250b4abccc171a6640efd644819fd46afb383a007ff6a81a53
VERDICT: GREEN
FAILED_CRITERIA: none
EVIDENCE: The packet binds one S2 replacement campaign to an eight-attempt pre-timer envelope, one six-hour workload attempt, exact CPU/image/disk/volume/rate/spend limits, canonical machine-readable hash custody, same-worker bounded reconciliation, exact per-attempt deadlines, detached exact-ID guard, 60-second Linux smoke, immutable 21,600-second production contract, full retrieval, and fail-closed teardown. It preserves the prior valid worker and executor-error evidence, fences unrelated resources, and retains the final GLM/Claude/AGY same-hash gate.
FAILURE_MECHANISM: N/A
MISSING_PROOF: none
NON_BLOCKING_RISKS: Prior executor stale-hash failure remains an operational risk but is mitigated by canonical JSON parsing and four-way recomputation. CPU price is available only after creation and remains delete-before-upload fail-closed. Detect-secrets findings are classified as synthetic hash fields and remain subject to teardown scanning.
RECUSAL_CHECK: No recusal required. GLM acted only within the assigned independent evidence-judge role.
```

The provider wrapper additionally reported `glm-zai: served by glm-5.2`. Its
long-form evidence repeated the packet's worker envelope, hash custody,
retry/sequentiality, scanner boundary, Linux smoke, production cadence,
retrieval, teardown, and final-gate requirements. One explanatory bullet
duplicated characters in the prior Pod ID; the artifact name, exact packet
hash, verdict, and controlling packet/receipt use the correct ID.

## Claude raw result

```json
{
  "role": "Independent Non-Authoring Evidence Judge (Claude Opus 4.8) — S2 Replacement Lifecycle Preflight",
  "packet_sha256": "b072143dd3ba99250b4abccc171a6640efd644819fd46afb383a007ff6a81a53",
  "verdict": "GREEN",
  "blockers": [],
  "non_blocking_risks": [
    "Core hashes, byte counts, provider state, and scanner outputs are asserted in-packet and cannot be recomputed by a no-tools judge; the fail-closed guarantee depends entirely on runtime recomputation from canonical S2_RUNTIME_HASHES_R1.json and the detached exact-ID guard.",
    "The EXECUTOR_COMMAND_CONSTRUCTION_ERROR path retains bounded executor judgment but requires a ten-minute ceiling, canonical reparse, and four-way hash recomputation; genuine mismatch remains non-retryable.",
    "Prompt teardown after retrieval is necessary to avoid paid idle slack within the eight-hour ceiling.",
    "Detect-secrets reports 32 high-entropy strings classified as synthetic hashes; a no-tools judge cannot independently inspect every field."
  ],
  "evidence_gaps": [
    "Builder identity and degree of Claude influence are not independently evidenced in the packet.",
    "A no-tools judge cannot recompute the canonical JSON, schedule, authorization, manifest, or provider state.",
    "Prior R3 evidence is hash-referenced rather than re-embedded in full."
  ],
  "recusal_check": "clear"
}
```

The `claude-judge` wrapper reported the served model as
`claude-opus-4-8`. Both judges returned the exact canonical packet hash. Their
non-blocking risks remain live execution checks; none authorizes weaker runtime
verification.
