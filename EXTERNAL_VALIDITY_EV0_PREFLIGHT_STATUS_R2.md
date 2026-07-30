# External Validity EV0 Preflight Status R2

The packet's internal title retains `R1`; this status and the filename classify
the byte-corrected packet as R2. The SHA-256 is the controlling identifier.

- `STATUS`: `EXTERNAL_VALIDITY_PREFLIGHT_GREEN_FOR_EV2`
- `PLAN_SHA256`: `396dd65f616a83982e26952fc5c7138839abb3acceaabced8b5748babd6bd530`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `GATE8_PACKET_SHA256`: `887cc444cb94ec94c2e9ffeed71f8f1113656e8cb799aa190687d592790fe0aa`
- `GATE8_CLAIM_MANIFEST_SHA256`: `11afb9f54906b625de82947cf27aebd0a548655c926a598bdca2921b17976921`
- `PREFLIGHT_PACKET_SHA256`: `41a341d60ab776e8a01f38f6ae142661e54751ef8878083d43f5c822045e55b4`
- `RULES_SNAPSHOT_SHA256`: `70f6831f510b6d0e26cbcabd58ed5ea60ba32673c0a5a4b922adc8ffc243bab0`
- `MECHANICAL_TESTS`: `182_PASS; 0_FAIL`
- `PUBLIC_CANARIES`: `RECOVERY_PASS; CONNECTION_INTERRUPTION_PASS; MISTRAL_PASS; STEPFUN_PASS`
- `SECRET_SCANS`: `GITLEAKS_ZERO; DETECT_SECRETS_ZERO`
- `HIDDEN_SEED_EXISTS`: `FALSE`
- `GLM_JUDGE`: `GLM_5_2_GREEN; EXACT_PACKET_HASH; RECUSAL_PASS`
- `GLM_RAW_SHA256`: `a0e643b72500579af12bcfd69747d4a052f586f4b2e57323204131a9c5724b4c`
- `AGY_JUDGE`: `GEMINI_3_1_PRO_HIGH_GREEN; EXACT_PACKET_HASH; RECUSAL_CLEAR`
- `AGY_RAW_SHA256`: `2aec17897dc737192daeddf3537e3c434ed40f571845d166cc756a12d4afde29`
- `NEXT_ALLOWED_ACTION`: `Obtain the temporary human-controlled Managed MCP Read Data OAuth grant, create three exact read-only-denial receipts, then execute only the frozen EV2 live campaign.`
- `FORBIDDEN`: `EV1, EV3, hidden inputs, Gate 9, feature changes, product behavior changes, RunPod, release, publication, video, or submission.`

The first AGY attempt emitted no valid verdict and is preserved as an
infrastructure failure. The bounded same-packet retry returned GREEN. No packet,
test, threshold, or campaign code changed between attempts.

This gate is protocol readiness, not EV2 evidence. No cloud mutation occurred
before both independent verdicts bound the exact R2 packet hash. Managed MCP
OAuth remains a human-controlled consent gate, and the campaign remains blocked
until Read Data only is visibly granted for the declared cluster.
