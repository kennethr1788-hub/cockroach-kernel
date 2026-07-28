# Hardening Gate 6 — Source Binding R2

- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `CANDIDATE_COMPARATIVE_SHA256`: `f9fa1d5ce7076c8fa96a1b5d9053f50c58902c557f1d6fbf340c0c356d12a1ec`
- `GATE6_ORCHESTRATOR_SHA256`: `825523e7011e3942bd7ac162322d8e7b673339a16f2dd8c1ccb854ed721db653`
- `LIFECYCLE_GUARD_SHA256`: `4644aa756f47c3d53b82c239657ce22605d4a9caab3e6a8651c4f459d95c6f0c`
- `PRODUCT_VERIFIER_SHA256`: `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`
- `GATE4_PROTOCOL_R1_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `GATE4_PROTOCOL_R2_SHA256`: `a17705c4b6f273b4a538249393bd63d8f645540db57d0cc36082259331f8fe52`
- `GATE5_FINAL_PACKET_SHA256`: `41efeb9270b76a0d4e1f711d5b1ab3270ecd92d32eccce93f07bef8a6ba036c0`
- `GATE5_STATUS_SHA256`: `c9bf7e330187695e2b359ed3510aaa00d7bd5c7026f421aede7430c7ea8a1cae`
- `GATE5_CHECKPOINT_SHA256`: `6b3fd1abbfee8144224149e0202e225d8a6898970e03f5cc9b84bdca42783465`
- `GATE5_JUDGE_RECEIPTS_SHA256`: `aff4cd568995238f6fe885937ff6cbc51853cfd0d31625abb7784be4a3342efb`
- `GATE5_EVIDENCE_REPORT_SHA256`: `5d65945758d1b5f5aff77c9c24f6d28ded69e3e1ffddabe56e3db81433f10757`
- `UTC_RECORDED`: `2026-07-28T00:37:19Z`

Gate 5 independently reviewed and froze the exact candidate source. Gate 6
does not change that source. Its new review concerns Linux tool binding,
orchestration, network denial, balanced pairing, evidence custody, RunPod
lifecycle, cost bounds, and teardown.

The raw candidate comparative source is deliberately excluded from the R3
external packet because a local egress rule classifies its ephemeral Restic
password assignment as a secret assignment. The source remains locally
available, committed, hash-bound, unit-tested, and included in the scanner-clean
RunPod payload. This is a sanitization boundary, not evidence that the source
contains a static credential.
