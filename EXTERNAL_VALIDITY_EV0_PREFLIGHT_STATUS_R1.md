# External Validity EV0 Preflight Status R1

- `STATUS`: `SUPERSEDED_BEFORE_CLOUD_MUTATION`
- `UTC_CLOSED`: `2026-07-30T09:10:38Z`
- `PLAN_SHA256`: `396dd65f616a83982e26952fc5c7138839abb3acceaabced8b5748babd6bd530`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `GATE8_PACKET_SHA256`: `887cc444cb94ec94c2e9ffeed71f8f1113656e8cb799aa190687d592790fe0aa`
- `GATE8_CLAIM_MANIFEST_SHA256`: `11afb9f54906b625de82947cf27aebd0a548655c926a598bdca2921b17976921`
- `PREFLIGHT_PACKET_SHA256`: `ffeb64dfd66be1fdde2a622347004ee4519e528dbd8162bf018b1ab909e9189f`
- `RULES_SNAPSHOT_SHA256`: `70f6831f510b6d0e26cbcabd58ed5ea60ba32673c0a5a4b922adc8ffc243bab0`
- `MECHANICAL_TESTS`: `182_PASS; 0_FAIL`
- `PUBLIC_CANARIES`: `RECOVERY_PASS; CONNECTION_INTERRUPTION_PASS; MISTRAL_PASS; STEPFUN_PASS`
- `SECRET_SCANS`: `GITLEAKS_ZERO; DETECT_SECRETS_ZERO`
- `HIDDEN_SEED_EXISTS`: `FALSE`
- `GLM_JUDGE`: `GLM_5_2_GREEN; EXACT_PACKET_HASH; RECUSAL_PASSED`
- `AGY_JUDGE`: `GEMINI_3_1_PRO_HIGH_GREEN; EXACT_PACKET_HASH; RECUSAL_CLEAR`
- `NEXT_ALLOWED_ACTION`: `Obtain the temporary human-controlled Managed MCP Read Data OAuth grant, create three exact read-only-denial receipts, then execute only the frozen EV2 live campaign.`
- `FORBIDDEN`: `EV1, EV3, hidden inputs, Gate 9, feature changes, product behavior changes, RunPod, release, publication, video, or submission.`

The first GLM response returned GREEN reasoning but copied the historical Gate 8
packet hash into its `PACKET_SHA256` field. It is preserved as invalid and does
not count. The R2 GLM response bound the correct unchanged preflight packet hash
and is the only counted GLM verdict.

The Kimi public canary did not authenticate and is preserved as a failed route.
StepFun replaced it before protocol freeze. The initial StepFun response was
truncated at its bounded output ceiling and is also preserved; its retry changed
only the output allowance, not the prompt, expected schema, or result.

This receipt was superseded when four trailing blank lines were removed from
the byte-complete harness. No cloud mutation occurred under this packet. The
current authority is `EXTERNAL_VALIDITY_EV0_PREFLIGHT_STATUS_R2.md`.

This receipt authorizes no cloud mutation by itself. The Managed MCP consent is
a human-controlled OAuth gate. The live campaign must remain fail-closed until
the exact read-only scope is visibly granted and the three frozen denial
receipts exist.
