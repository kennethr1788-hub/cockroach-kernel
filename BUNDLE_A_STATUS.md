# Bundle A Status

**Status:** `CK_BUNDLE_A_BLOCKED`
**P4:** `CK_P4_VERIFIER_GREEN`
**S1:** `CK_S1_BLOCKED`
**Blocker:** `RUNPOD_PRICE_DRIFT`; the authenticated console's smallest current
CPU offering is 2 vCPU / 8 GB at $0.08/hour, while the second-lifecycle
authorization requires exactly 2 vCPU / 4 GB at no more than $0.06/hour.

The first worker remains stopped and deleted, and no second worker was created.
Bundle A cannot close without a newly authorized or later price-compliant,
independently reviewed S1 lifecycle plus exact billing reconciliation. P4
remains independently GREEN.
