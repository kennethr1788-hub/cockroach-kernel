# Scenario Surface R3 Candidate Receipt

- `STATUS`: `R3_CANDIDATE_FROZEN`
- `UTC_CREATED`: `2026-07-28T06:39:05Z`
- `NEW_CANDIDATE_COMMIT`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `OLD_CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `OLD_CANDIDATE_PRESERVED`: `YES`
- `CONTRACT_SHA256`: `52fbe37a309cebd3983692c58460fbb6dca64d13eaf6713a5d3c60e88af2fb78`
- `CONTRACT_AUDIT_PACKET_SHA256`: `d86c6433fd3df150490070fa734c49e27d76bcc55bff2f5d4c7084843ccc867d`
- `PRODUCT_TEST_REPORT_SHA256`: `b1d62c3b15497cf08295d49951130f87e2b432fc2ae813461c147da92d56be`
- `CLEAN_CLONE_RAW_SHA256`: `83556c72d891b92a92f8ad27c26d0d8981fa0fd4fcaaf3586fffb304651bdd47`
- `CLEAN_CLONE_REPORT_SHA256`: `c3738857873ad325cff3a84af1820b6ecb3de37696348145e3ba48d0f173ec21`
- `CLEAN_CLONE_TRIALS`: `2/2 GREEN`
- `TARGETED_AND_REGRESSION_TESTS`: `304 PASS`
- `GITLEAKS_OLD_TO_NEW`: `PASS; 55 commits; 2.20 MB; no leaks`
- `DETECT_SECRETS_PRODUCT_PACKAGE`: `PASS; empty results; no network verification`
- `PRIVATE_PATH_PRODUCT_PACKAGE`: `PASS; no concrete operator path, credential, or private/client datum`
- `HIDDEN_SEED_CREATED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`
- `GATE7_STARTED`: `NO`
- `PUBLIC_OR_PAID_ACTION`: `NONE`

## Candidate product hashes

- `pyproject.toml`: `5aec830e88570393e087b0b9f8b4d1217ef8879cb5c0c643e74a1a2e2e5625e7`
- `README.md`: `3ab7f36445f5790151c20a91d97b68037299933113ccfd8a7e4ac8bb41289fd7`
- `cockroach_kernel/cli.py`: `1f187a879a1946874b74bd043ff550a61963f6086076aed3c64a79bccd32b609`
- `cockroach_kernel/recovery_surface.py`: `bf13e0cdac3a846c48308ad79c89772e1b533a73dec340f13e25180500f69586`
- `p7-recovery/records.py`: `97971f48852e94ada7ecabb7dd0390442b4bde11f38fbdb069b10d396355fd34`
- `p7-recovery/fresh_context.py`: `4fbe7ff002bcb26ceb649295a4a4e94d79f7aecbab10eff1e7a75d1c63c577f7`

The existing P7 record/selector authority source hash is unchanged. The
fresh-context change is import-only package compatibility: relative package
import with direct-script fallback. The new surface packages and calls those
existing P7 modules rather than implementing a second selector.

## Frozen behavior

The candidate exposes `cockroach-kernel recover` with explicit canonical
request, disposable envelope, successor, representation, custody, and output
roots. Exact hash-bound representation bytes are promoted only after a
persistent warrant becomes `CONSUMED`. Missing representations are recorded,
not invented. No-loss, refusal, and pre-consumption invalid cases do not mutate
the successor. Fresh-process replay is refused.

No further product mutation is allowed during R3 plan or preflight work. A
product correction would create a new candidate and invalidate later hashes.
