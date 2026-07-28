# Fresh-Context Black-Box Plan R2 — Independent GLM Audit Receipt

- `STATUS`: `BLACK_BOX_PLAN_R2_INDEPENDENTLY_GREEN`
- `UTC_CREATED`: `2026-07-28T05:35:39Z`
- `TARGET_PLAN`: `FRESH_CONTEXT_BLACK_BOX_PLAN_R2.md`
- `TARGET_PLAN_SHA256`: `4453424a60e0cb591bde3a7a6da5ceeb7bd752b8cf9dd6abba785b42c61f32cc`
- `JUDGE_ROUTE`: `direct glm-zai`
- `REQUESTED_MODEL`: `glm-5.2`
- `SERVED_MODEL`: `glm-5.2`
- `FALLBACK`: `disabled`
- `VERDICT`: `GREEN`
- `RECUSAL`: `CLEAR`
- `R1_CONCERN_1_SANDBOX_RESIDUE`: `RESOLVED`
- `R1_CONCERN_2_SOURCE_INSPECTION`: `RESOLVED`
- `EXECUTION_AUTHORITY`: `NOT_GRANTED`

## Attempt ledger

### Attempt 1 — invalid identity field

- `INSTRUCTIONS`: `FRESH_CONTEXT_BLACK_BOX_GLM_AUDIT_INSTRUCTIONS_R2.md`
- `INSTRUCTIONS_SHA256`: `4e33db5e52716054540785df5fbb697f0d6d51abacf3efdec84ca48750e4e814`
- `PACKET_ORDER`: `instructions R2 || target plan R2`
- `PACKET_SHA256`: `5a090ed425f3185df8715f460128e937a93dec06700d87daac9218ab898f33d6`
- `ROUTE_HEADER`: `glm-zai: served by glm-5.2`
- `RAW_OUTPUT`: `FRESH_CONTEXT_BLACK_BOX_GLM_AUDIT_RAW_R2_ATTEMPT1_INVALID.txt`
- `RAW_OUTPUT_SHA256`: `b04535a4cd7120a0ec0366ee044f6f844b9734737f2e249bf1b3ec7f2342a327`
- `RESULT`: `INVALID_JUDGE_IDENTITY_FIELD`

The substantive verdict was GREEN and both concerns were marked resolved, but
the model-authored field falsely stated `google/gemini-1.5-pro-api`, contradicting
the exact-model-verified route. The attempt was preserved and not counted.

### Attempt 2 — valid controlling audit

- `INSTRUCTIONS`: `FRESH_CONTEXT_BLACK_BOX_GLM_AUDIT_INSTRUCTIONS_R2B.md`
- `INSTRUCTIONS_SHA256`: `1ab20332657558648c6aff525b3d0888547c0fc2a757bbe22bd45a9fb52645f6`
- `INSTRUCTION_CHANGE`: `requires exact echo of externally verified glm-5.2 identity; target plan unchanged`
- `PACKET_ORDER`: `instructions R2B || target plan R2`
- `PACKET_SHA256`: `2ba4b9ba65f36a04458da6cfb01d54c9f5610a53374024bc399d630257d25903`
- `ROUTE_HEADER`: `glm-zai: served by glm-5.2`
- `RAW_OUTPUT`: `FRESH_CONTEXT_BLACK_BOX_GLM_AUDIT_RAW_R2B.txt`
- `RAW_OUTPUT_SHA256`: `f354b405052573e59c430c3587e8adb5fc06d46537bcd863f1b13a2b6440a06f`
- `RESULT`: `VALID_GREEN`

The target plan bytes were identical across both attempts. Only the judge output
instruction was corrected to prevent model-identity invention.

## Controlling verdict

```text
VERDICT: GREEN
SERVED_MODEL: glm-5.2
RECUSAL: CLEAR
R1_CONCERN_1_SANDBOX_RESIDUE: RESOLVED
R1_CONCERN_2_SOURCE_INSPECTION: RESOLVED
BLOCKERS: none
RECOMMENDED_MINIMAL_CORRECTIONS: none
```

GLM found that R2 resolves both R1 methodology concerns. It also correctly
preserved one implementation-stage risk: the specified OS controls, telemetry,
residue mutation tests, and command attribution must still produce direct
preflight evidence before execution. A plan cannot prove its future
implementation.

## Evidence required before execution

1. OS-level deny-canary proof over the exact production sandbox policy and
   enforcement binary.
2. Residue-scanner mutation results for file-descriptor, socket, and
   cross-session residue in addition to the complete R2 fixture set.
3. Scorer calibration proving deterministic actor-command versus
   product-runtime-read attribution.
4. All candidate, package, generator, scorer, prompt, sandbox, monitor,
   telemetry, and residue-scanner hashes required by R2.
5. Campaign seed commitment before the first actor session.

These items are OPEN preflight implementation evidence, not unresolved plan
defects.

## Hygiene

- R2 plan SHA-256 independently recomputed before both audits.
- R2 plan `gitleaks --no-git`: exit `0`, empty report.
- R2B judge instructions `gitleaks --no-git`: exit `0`, empty report.
- Targeted private-path/credential review found no concrete secret, credential,
  operator HOME path, or private/client data.
- `git diff --check`: PASS before receipt creation.

## Boundary

R2 and this verdict do not implement or execute the black-box campaign, invoke a
black-box actor, authorize model spend, create a paid resource, alter Gate 6,
begin Gate 7, or authorize a public claim. The next safe action is to stop or
receive separate authority to implement R2 preflight against public fixed
fixtures only.
