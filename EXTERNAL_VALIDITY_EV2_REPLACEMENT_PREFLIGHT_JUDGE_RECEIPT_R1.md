# EV2 Replacement Campaign Preflight Judge Receipt R1

- `STATUS`: `EV2_REPLACEMENT_PREFLIGHT_GREEN`
- `UTC_CLOSED`: `2026-07-30T11:50:15Z`
- `PACKET`: `EXTERNAL_VALIDITY_EV2_REPLACEMENT_PREFLIGHT_PACKET_R1.md`
- `PACKET_SHA256`: `42cb7faa0080462928b82744288bd3b57dc5f03e6d77407e8f8d33f01181e310`
- `PACKET_COMMIT`: `45ffdbc8bdad6e84cc5b13d87f65f1ab225012a5`
- `REPAIR_COMMIT`: `2c4f2159589c50b2136a95ae2a026d8db438a74d`
- `FAILED_R1_STATUS`: `IMMUTABLE_BLOCKED_ZERO_CREDIT`
- `GLM_ROUTE`: `direct glm-zai`
- `GLM_SERVED_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RECUSAL`: `clear`
- `GLM_RAW_SHA256`: `7e4c5ac84f32559654d786b2a764f0bb4bc8aa174f5511752547e096157c380e`
- `GLM_STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`
- `AGY_ROUTE`: `agy-judge`
- `AGY_MODEL`: `Gemini 3.1 Pro (High)`
- `AGY_PROVIDER_BINDING`: `authenticated inventory -> exact backend override -> provider response`
- `AGY_VERDICT`: `GREEN`
- `AGY_RECUSAL`: `clear`
- `AGY_RAW_SHA256`: `651b5c3e46528e2c65642e08ab0cd121468732e55ecb07a785ae9af942dcaedb`
- `AGY_STDERR_SHA256`: `bf32ab8c082fa1aff618ee172c412b767bf7f636479cf49543749f2ba6ad30ee`
- `NEXT_ALLOWED_ACTION`: `Run final live readiness checks, then execute exactly one replacement 24-execution EV2 campaign into evidence/external-validity-ev2-live-r2.`
- `FORBIDDEN`: `Any further code change, matrix or threshold change, post-execution retuning, second replacement, EV1, EV3, hidden inputs, Gate 9, public claims, release, video, or submission.`

## GLM result

```text
PACKET_SHA256: 42cb7faa0080462928b82744288bd3b57dc5f03e6d77407e8f8d33f01181e310
VERDICT: GREEN
BLOCKERS:
- none
NON_BLOCKING_RISKS:
- none
EVIDENCE_GAPS:
- none
RECUSAL_CHECK: clear
REQUIRED_RERUNS:
- none
```

The direct wrapper independently reported `served by glm-5.2`.

## AGY result

```text
PACKET_SHA256: 42cb7faa0080462928b82744288bd3b57dc5f03e6d77407e8f8d33f01181e310
AGY_VERDICT: GREEN
BLOCKERS:
- NONE
NON_BLOCKING_RISKS:
- NONE
EVIDENCE_GAPS:
- NONE
RECUSAL_CHECK: clear
REQUIRED_RERUNS:
- NONE
```

AGY's wrapper proved its current authenticated provider binding. As documented
by that route, response-level served-model metadata is unavailable; the receipt
does not overstate that operational binding as cryptographic attestation.

Both lanes judged the same exact packet hash. This receipt authorizes only the
single replacement EV2 campaign already explicitly approved by Kenneth. It is
not EV2 outcome evidence and does not predict campaign success.
