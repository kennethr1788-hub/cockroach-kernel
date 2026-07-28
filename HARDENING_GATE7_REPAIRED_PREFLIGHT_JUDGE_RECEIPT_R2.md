# Hardening Gate 7 Repaired Preflight Judge Receipt R2

- `UTC_CREATED`: `2026-07-28T19:28:58Z`
- `PACKET`: `HARDENING_GATE7_EXPANDED_PREFLIGHT_PACKET_R2.md`
- `PACKET_SHA256`: `4fd89d699dccd0d3e15451fab40435ad2e9b3f7300061ff8791913dc4b7ecf44`
- `PACKET_BYTES`: `252919`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `SOURCE_BINDINGS_SHA256`: `49359c601dce27ebfafe6f6cfde8151f09e430e58a443896992ef4ec5d75384a`
- `TRANSFER_ARCHIVE_SHA256`: `b95c6b8e20ec30473676b8f2dbe7e128fdb78bfd33a72105131c51bf45634eb0`
- `GLM_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RECUSAL_CHECK`: `clear`
- `GLM_RAW_SHA256`: `992fac52e9ff60d6cbab0e3e59b8320489ce9374cec29fe0f577d8894e26a581`
- `GLM_STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`
- `AGY_MODEL_BINDING`: `Gemini 3.1 Pro (High); authenticated inventory to exact backend override to provider response`
- `AGY_VERDICT`: `GREEN`
- `AGY_RECUSAL_CHECK`: `clear`
- `AGY_RAW_SHA256`: `1bc3e4db300cdf6c97378fa61b1ed3835ceca3f4f41a93c0bbd1dc2777393290`
- `AGY_STDERR_SHA256`: `704cd697e3c35f59e1936b327608c169e0648d6966e31ac5a99ade7b5816186e`
- `SAME_HASH`: `YES`
- `BLOCKERS`: `NONE`
- `ACTIVE_RUNPOD_INVENTORY`: `[]`
- `HIDDEN_SEED_CREATED`: `NO`
- `MEASURED_CAMPAIGN_STARTED`: `NO`
- `DECISION`: `REPLACEMENT_PROVIDER_READINESS_AUTHORIZED`

Both independent non-authoring judges returned valid GREEN verdicts over the
same repaired packet hash with recusal clear. Their raw outputs are preserved
under `.hardening-runtime/gate7-r2/judges-r2/` and are bound above by SHA-256.
This receipt authorizes only the already operator-approved replacement
provider-readiness lifecycle. It does not predict campaign results or waive
any measurement, evidence, teardown, or final-review gate.
