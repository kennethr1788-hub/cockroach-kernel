# PDH-3 R12 R6 R6 Full-Cardinality Preflight Failure Review Packet

- `STATUS`: `FROZEN_FOR_INDEPENDENT_FAILURE_CLASSIFICATION`
- `UTC_FROZEN`: `2026-08-03T06:31:51Z`
- `DECISION_REQUESTED`: Independently classify the failed paid preflight, determine whether teardown and evidence preservation are proved, and confirm that the old packet cannot authorize a replacement.
- `MEASURED_24H_STARTED`: `false`
- `BUILDER_SELF_APPROVAL`: `forbidden`

## Bound inputs

- Prospective packet SHA-256: `17585b9b4dad64d0f3311c2d42e746bc70ec91b535a74ac93902580901da0d79`.
- Prospective independent verdict: GLM 5.2 GREEN before worker creation.
- Blocked receipt: `PDH3_R12_R6_R6_FULL_PREFLIGHT_BLOCKED_RECEIPT_20260803_R1.md`.
- Blocked receipt SHA-256: `975673a63254fd489a6de15721f3466a42058a7bfa9b8b3ac6df2402d1c861c9`.
- Pod ID: `mzbblmsmmppz9u`.
- Retrieved archive SHA-256: `071919bdcdd8ea223c8155749fc99ad8046922d276934afd196f03fe084f0058`.
- Remote archive SHA-256: `071919bdcdd8ea223c8155749fc99ad8046922d276934afd196f03fe084f0058`.
- Remote child stderr SHA-256: `0e8a7314676ce081238159d0ba1c2a0753d31b103846954b775824b029f3ea59`.
- 50k teardown SHA-256: `314e09afac30db69a5de243757fd84327ad34bbf9b180d8c14e47c8b7133c0b8`.
- Network receipt SHA-256: `b9e734921574fbdad9e781b59956683cbf0680f11ee2203b4bb91f7256b29eed`.
- Pod delete response SHA-256: `313c663340820a52ab057daffd3c38a76ed8043b57f6250679daced78432e809`.
- Lifecycle stream SHA-256: `b320f4b24d413d4306cef9595ac4ee593a74fd6a998d5dd33cbc36a501fee5fd`.

## Verified facts

1. PF-4 and the extracted Linux smoke were GREEN.
2. The 10k Plan A/B rung was GREEN with exact counts, expected index selection, no prohibited post-index full scan, no result mismatch, and teardown GREEN.
3. The 50k rung timed out after 1,800 seconds inside one SQL subprocess containing five table-population statements. The stable error was `SQL_TIMEOUT:3cf7b0a02c010bf7f5af473bd5610bc34403acaa837243d81ff58a60617c0231`.
4. The 50k generated database root and process were cleaned up with a GREEN teardown receipt.
5. The child exit made the network observer fail closed. It recorded no egress violation but may not be claimed GREEN.
6. PF-5, PF-6, and PF-7 did not run. Full cardinality and the 24-hour campaign were never reached.
7. Best-effort evidence retrieval succeeded and local/remote archive hashes match.
8. Pod deletion returned true. Fresh exact lookup returned `404 not_found`, and active inventory returned `[]`.
9. The local lifecycle guard continued retrying exact lookup after the Pod was absent. The two remaining local controller processes were terminated after evidence preservation and provider-absence verification; no matching process remains.
10. The main-bundle upload marker exists. The reviewed packet explicitly ended replacement authority at that point.

## Builder classification

`PDH3_R12_R6_R6_FULL_PREFLIGHT_BLOCKED: PF2R_SCALE_50000_COMBINED_SEED_SQL_TIMEOUT`

Secondary defect: `LIFECYCLE_GUARD_404_ABSENCE_NOT_TERMINAL`.

No replacement is authorized by the completed packet. A new operator-authorized, independently reviewed prospective packet is required. No 24-hour measured campaign may begin.

## Judge boundary and required response

The judge receives this sanitized packet only. It has no shell, filesystem, write, repository, browser, credential, RunPod, implementation, retry, or approval authority.

Return exactly:

```text
SERVED_MODEL: glm-5.2
TARGET_PACKET_SHA256: <exact packet SHA-256>
VERDICT: BLOCKED_CLASSIFICATION_CORRECT | CLASSIFICATION_INCORRECT | JUDGE_UNAVAILABLE
PRIMARY_BLOCKER_LOAD_BEARING: YES | NO
SECONDARY_LIFECYCLE_DEFECT_VALID: YES | NO
EVIDENCE_RETRIEVAL_PROVED: YES | NO
PROVIDER_TEARDOWN_PROVED: YES | NO
OLD_PACKET_RETRY_AUTHORIZED: YES | NO
FINDINGS:
- <finding or NONE>
```
