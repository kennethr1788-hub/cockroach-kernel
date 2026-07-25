# S1 Foundation Soak

**Status:** `CK_S1_BLOCKED`
**Parent gate:** `CK_P4_VERIFIER_GREEN`
**Blocker:** `RUNPOD_PRICE_DRIFT`
**Blocked UTC:** `2026-07-25T21:26:51Z`

The authenticated console cleared the prior unknown-price blocker. The frozen
worker is 2 vCPU / 8 GB at $0.08/hour plus $0.004/hour for 20 GB container
storage, with a $0.13 maximum lifecycle estimate. No worker has been created.

Independent GLM 5.2 returned preflight GREEN on the frozen packet. The single
authorized creation returned 2 vCPU / 4 GB at $0.06/hour instead of the frozen
2 vCPU / 8 GB at $0.08/hour. The worker was stopped and deleted before any
payload upload or workload execution. Campaign-scoped inventory is empty.

Kenneth subsequently authorized one second and final lifecycle with an exact
2 vCPU / 4 GB target, a compute ceiling of $0.06/hour, and a total active-rate
ceiling of $0.065/hour. Before any new packet, judge request, or worker
creation, the authenticated RunPod console was rechecked. Its CPU inventory
offered 2 vCPU / 8 GB at $0.08/hour as the smallest class. The authorized
2 vCPU / 4 GB class was not offered, and the smallest offered compute rate
exceeded the authorized ceiling.

The mandatory price-drift stop therefore fired before the final worker was
created. The second-worker authorization remains unspent, but it is not usable
without a new operator authorization because the stated hardware and price
conditions do not currently pass. Exact provider charge for the first failed
worker remains pending: the bounded pod-scoped reconciliation query again
returned `[]`. S1 execution evidence does not exist and is not claimed.
