# R4 Public Canary R2 Evidence Manifest

## Candidate

- Freeze commit: `bcb4ecc7e2e15ddfbd4da46d01a524a79f8ee71b`
- Plan: `FRESH_CONTEXT_BLACK_BOX_R4_PUBLIC_CANARY_PLAN_R2.md`
  - SHA-256: `9b0648975a2b8021eefb5d17995d50562eca295e60700c709197703d68940593`
- Schema: `fresh-context-black-box/r4_action_response_r2.schema.json`
  - SHA-256: `8844b9cacf5ecab7822d9045d03664c55f97d36e475822dc8abfde72a5e01b26`
- Runner: `fresh-context-black-box/r4_public_canary_r2.py`
  - SHA-256: `ad981d883d156c1309d8c0d1a3b520bf2af9ee5c133e807f3cd44604733603f0`
- Tests: `fresh-context-black-box/test_r4_public_canary_r2.py`
  - SHA-256: `f0284ec0c37bfafba4f2c5086bc7e2b5ef3662149f24077adfa5dfe750da4f2a`

## Raw R2 evidence

- `evidence/black-box-r4-public-canary/r4-public-canary-r2/FINAL_SUMMARY.json`
  - file SHA-256: `59054de434f5c3334ded1686e7efd79d6cda6d800793e0748297e4c18adbd2cc`
  - embedded summary hash: `58154efd260d5a31da32b94b68004a6799c14f5496efaf51a1320821e26ff832`
- `public-01.json`
  - SHA-256: `cc0da6d5396e2bc01779b609915a9eeb659667515790b8db868129cc88a3e3ec`
- `public-02.json`
  - SHA-256: `0f75fe8b2eebda79d561bf99c27b85f14460018b8d38ca824ae50910c9b4f09d`
- `public-03.json`
  - SHA-256: `c182693223cacfa49cb6f0dd4dc8bd3c943c5027330b727d2994bb5226955305`

## Verification

- R2 contract tests: `8/8 PASS`
- Python compile gate: `PASS`
- `detect-secrets` on R2 evidence: `0 findings`
- Targeted new-file gitleaks classification: `0 findings in R2 files`
- Disposable runtime roots after execution: `0`
- Loaded Ollama models after execution: `0`
- Hidden seed and hidden executions: `0 / 0`

The repository-wide gitleaks scan contained historical findings outside this
candidate and is not represented as a clean-repository result.

## Preserved parent failure

`BLACK_BOX_R4_PUBLIC_CANARY_R1_STATUS.md` is SHA-256
`614792320b65ca346f58c9775e05342664a41e082b507bc18c19cadab367eeb4`.
R1 remains `NOT_GREEN_SAFE_REJECTION`; R2 does not overwrite it.
