# S1 Foundation Soak

**Status:** `CK_S1_FOUNDATION_SOAK_GREEN`
**Parent gate:** `CK_P4_VERIFIER_GREEN`
**Blocker:** `NONE`
**Green UTC:** `2026-07-25T22:52:29Z`

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

Kenneth then authorized the independently reviewed R3 retry envelope. Attempt 1
returned an authorized 2-vCPU/4-GB worker at $0.06/hour. The complete frozen
3,600-second workload passed with 61/61 checkpoints, all receipt and telemetry
hashes valid, all semantic gates passing, database/evidence growth below their
limits, and empty runtime residue. Raw evidence was retrieved and verified.

The worker was stopped and deleted; scoped running/all-status inventories are
empty and Pod get returns 404. The remaining blocker is exact provider billing:
both Pod-scoped billing queries still return `[]`, and the authenticated Cloud
CPU explorer states billing is one hour behind. Kenneth explicitly accepted the
visible account-side charge and directed that delayed itemization not block S1.
No exact amount is fabricated. S1 then awaited final independent review only.

Independent GLM 5.2 returned GREEN on completed packet SHA-256
`46e6a9081c949d586d9ea4812a31e6baf033342bef380bdf4a8ed50e73cf25b1`.
S1 is GREEN. No later phase was started.
