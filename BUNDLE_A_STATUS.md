# Bundle A Status

**Status:** `CK_BUNDLE_A_BLOCKED`
**P4:** `CK_P4_VERIFIER_GREEN`
**S1:** `CK_S1_PREFLIGHT_PENDING_JUDGE`
**Blocker:** the frozen lifecycle packet requires independent preflight GREEN;
no worker exists and spend remains $0.

Bundle A cannot close until the single bounded S1 worker completes, exact cost
and teardown are reconciled, and the final S1 packet receives independent GLM
GREEN.
