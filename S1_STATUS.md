# S1 Foundation Soak

**Status:** `CK_S1_PREFLIGHT_GREEN`
**Parent gate:** `CK_P4_VERIFIER_GREEN`
**Current commit:** `03fb60a`
**Frozen UTC:** `2026-07-25T21:16:30Z`

The authenticated console cleared the prior unknown-price blocker. The frozen
worker is 2 vCPU / 8 GB at $0.08/hour plus $0.004/hour for 20 GB container
storage, with a $0.13 maximum lifecycle estimate. No worker has been created.

Independent GLM 5.2 returned GREEN on packet
`8aa3a3b7da4371ffec5569466f230c8052c7eb9bfe2593678728df3abe91149a`.
Exactly one worker may now launch under the frozen command and deadlines.
