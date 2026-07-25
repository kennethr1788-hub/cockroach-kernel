# S1 Foundation Soak

**Status:** `CK_S1_BLOCKED`
**Parent gate:** `CK_P4_VERIFIER_GREEN`
**Blocker:** `RUNPOD_WORKER_MISMATCH`
**Blocked UTC:** `2026-07-25T21:19:38Z`

The authenticated console cleared the prior unknown-price blocker. The frozen
worker is 2 vCPU / 8 GB at $0.08/hour plus $0.004/hour for 20 GB container
storage, with a $0.13 maximum lifecycle estimate. No worker has been created.

Independent GLM 5.2 returned preflight GREEN on the frozen packet. The single
authorized creation returned 2 vCPU / 4 GB at $0.06/hour instead of the frozen
2 vCPU / 8 GB at $0.08/hour. The worker was stopped and deleted before any
payload upload or workload execution. Campaign-scoped inventory is empty.

S1 cannot retry under this packet because a second worker is forbidden. Exact
provider charge is also pending because the immediate billing query returned no
record. S1 execution evidence does not exist and is not claimed.
