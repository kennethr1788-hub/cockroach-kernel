# EV1-T01 Result Classification Audit Packet R1

## Role and boundary

You are an independent non-authoring GLM judge. Assess only whether the stated
classification follows from the evidence summarized below. Do not propose code,
change the frozen outcome, treat operator testimony as mechanical proof, or
upgrade a failed acceptance command to GREEN.

This packet is sanitized. It contains no credentials, account identifiers,
client data, private memory, source code, or external action authority.

## Decision requested

Determine whether all three conclusions are supported:

1. The product demonstrated byte-exact recovery of both declared work units
   through a one-use, fresh-process recovery path.
2. The task did not demonstrate complete end-to-end acceptance because the
   first frozen successor acceptance command failed.
3. `INFRASTRUCTURE_INVALID_DEPENDENCY_LAYOUT; NON_SCORING` is the honest result
   classification. The evidence must not be described as a complete task pass.

## Frozen evidence facts

- Product candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`.
- The original disposable workspace was guarded-deleted and remained absent.
- The recovery child returned `PROMOTE`, reason `MAX_PROVEN_PREFIX`, and
  `FRESH_CONTEXT_PASS`.
- Recovery log SHA-256:
  `66313857e46c7a33c5b86a542e4ca275c5379a9e6b8a34891b09e4a2e1912615`.
- Restored tracked page SHA-256:
  `4e58758472be64bb40458e4f201340d8ef98b7c848dc5ae7cd3323145cbc643e`.
- Restored untracked verifier SHA-256:
  `ef03dd17029435a469b80cb683ce6f2d5c64b2454940863e9ff78abeab6aa431`.
- Both restored hashes exactly matched their declared pre-loss hashes.
- A standalone post-recovery semantic verifier exited zero with
  `TAGLINE_SEMANTIC_AND_UNIQUE`; its log SHA-256 is
  `823994e1443f06d130d5b7475572a36f790c685f8f4e04d91508487dd6ae55b3`.
- The frozen full acceptance sequence was `npm run typecheck`, then
  `npm run build`, then the semantic verifier. It stopped at the first command.
- `npm run typecheck` exited nonzero. Its log SHA-256 is
  `f0255770ab810ed0cc911c7998c88c75d6cf3805508fe8660bfa8874bfc0ac7d`.
- Representative raw error signatures were:
  - `TS2307: Cannot find module 'next' or its corresponding type declarations.`
  - `TS2307: Cannot find module 'react' or its corresponding type declarations.`
  - `TS2307: Cannot find module 'next/navigation' or its corresponding type declarations.`
  - cascading `TS7026` missing `JSX.IntrinsicElements` errors.
- The dependency inventory recorded Next, React, React DOM, and their type
  packages as installed before loss.
- The evidence runner preserved that dependency tree in a project-local control
  directory outside the temporary recovered successor's Node/TypeScript module
  resolution ancestry. The recovered source files themselves matched the
  declared hashes.
- No source edit or second recovery occurred after the result became known.
- The one-use warrant was consumed, task process residue was zero, and the
  failure receipt was preserved.
- Operator observations were recorded separately and expressly do not override
  the mechanical failure.

## Required output

Return exactly these fields in plain text:

```
MODEL_SERVED: <actual served model>
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

`GREEN` means all three conclusions and the conservative claim ceiling are
supported. Do not return GREEN if the evidence supports only file restoration
but not the stated classification boundary.
