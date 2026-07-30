
## R2 output-contract amendment

This amendment supersedes only the `Required output` section above. The evidence,
decision request, claim boundaries, and GREEN meaning remain byte-identical.

Served-model identity is validated externally by the direct wrapper and must not
be guessed, adopted, or printed by the judging model. Return exactly:

```
VERDICT: GREEN | NOT_GREEN | INSUFFICIENT_EVIDENCE
RECUSAL: CLEAR | REQUIRED
CONCLUSION_1_BYTE_EXACT_RECOVERY: SUPPORTED | NOT_SUPPORTED | INSUFFICIENT
CONCLUSION_2_FULL_ACCEPTANCE_FAILED: SUPPORTED | NOT_SUPPORTED | INSUFFICIENT
CONCLUSION_3_INFRASTRUCTURE_INVALID_NON_SCORING: SUPPORTED | NOT_SUPPORTED | INSUFFICIENT
CLAIM_CEILING: <one sentence stating the strongest honest claim>
BLOCKERS: <NONE or concise blockers>
RISKS: <NONE or concise non-blocking limitations>
RATIONALE: <concise evidence-grounded reasoning>
```

Do not output a `MODEL_SERVED` field. Any identity claim in generated prose
invalidates the result. This is one bounded replacement for the preserved R1
identity-label failure.
