# Hardening Gate 7 Run 6 — Final Judge Receipt R1

- `UTC_CREATED`: `2026-07-30T06:29:23Z`
- `PACKET`: `HARDENING_GATE7_RUN6_FINAL_PACKET_R1.md`
- `PACKET_SHA256`: `1f9fa31524fb857a37b444df4b5ff7f1aa79847e941c863ffd1a993566efa89a`
- `PACKET_COMMIT`: `e2340669d071291b8e421607264e535d7cc47fd6`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `SAME_HASH`: `YES`
- `RECUSAL_STATE`: `GLM_CLEAR; AGY_CLEAR`
- `TERMINAL_RESULT`: `HARDENING_7_EXPANDED_GREEN`

## GLM lane

- `MODEL`: `glm-5.2`
- `MODEL_PROOF`: `wrapper-verified exact served model; fallback disabled`
- `VERDICT`: `GREEN`
- `PACKET_SHA256_RETURNED`: `1f9fa31524fb857a37b444df4b5ff7f1aa79847e941c863ffd1a993566efa89a`
- `RECUSAL_CLEAR`: `true`
- `RAW_SHA256`: `7f44183827573db550216a4899ad709fa90c87d740514a4925031761fbbdb429`
- `STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`

The first GLM response returned a substantively GREEN JSON object but also an
unsolicited AGY-form block, violating the exact one-object schema. It is
preserved with SHA-256
`29f618a730b3cb9c13e845cf2b1fc21c03f4306cb593c8b5486c876d41380757`
and is not counted. The packet did not change before the valid rerun.

## AGY lane

- `MODEL_BINDING`: `Gemini 3.1 Pro (High); authenticated inventory to exact backend override to provider response`
- `RESPONSE_LEVEL_SERVED_MODEL_METADATA`: `UNAVAILABLE_IN_CLI_1_1_8; NOT_OVERSTATED`
- `VERDICT`: `GREEN`
- `PACKET_SHA256_RETURNED`: `1f9fa31524fb857a37b444df4b5ff7f1aa79847e941c863ffd1a993566efa89a`
- `RECUSAL_CHECK`: `clear`
- `RAW_SHA256`: `7f395dcf711e3e89d45b93e72dfc356cd32488308b89888d22825d4479481e52`
- `STDERR_SHA256`: `e67c408defde5733d6d882bf2bfc28d4fc7c62958fdffb764b94d887b9ae50bf`

## Shared result

Both independent lanes found no blocker, no evidence gap, and no required
rerun. Both preserved the same non-blocking limitations: synthetic and
single-implementation evidence, bounded single-region scale, captured-state
recovery rather than arbitrary undelete, and mathematical rather than exact
provider billing evidence.

Gate 7 is independently GREEN. This receipt does not approve Gate 9, release,
publication, video, or submission.

