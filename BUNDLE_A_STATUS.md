# Bundle A Status

**Status:** `CK_BUNDLE_A_BLOCKED`
**P4:** `CK_P4_VERIFIER_GREEN`
**S1:** `CK_S1_BLOCKED`
**Blocker:** `RUNPOD_WORKER_MISMATCH`; the provider returned 2 vCPU / 4 GB at
$0.06/hour instead of the frozen 2 vCPU / 8 GB at $0.08/hour.

The worker was stopped and deleted before upload or execution. Bundle A cannot
close without a newly authorized and independently reviewed S1 lifecycle plus
exact billing reconciliation. P4 remains independently GREEN.
