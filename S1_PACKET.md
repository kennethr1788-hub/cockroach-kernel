# Cockroach Kernel S1 Frozen Preflight Packet

- `GATE`: `CK_S1_BLOCKED`
- `BLOCKER`: `RUNPOD_POLICY_BLOCKED`
- `LAST_GREEN_GATE`: `CK_P4_VERIFIER_GREEN`
- `CURRENT_COMMIT`: `97a22fe`
- `P4_PACKET_SHA256`: `0bc2c11084a144bfafde92dae29561ed5810c7b969690e77aa9137c9855b6c43`
- `RUNPODCTL_VERSION`: `2.7.2-309512b`
- `RUNPODCTL_SHA256`: `a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037`
- `CAMPAIGN_ID`: `CK-S1-20260725-FOUNDATION`
- `FROZEN_UTC`: `2026-07-25T20:59:54Z`

## Workload profile

The local P4 unit suite plus P3 integration harness completed without CUDA in
approximately 24 seconds and used standard-library/Python plus the local
CockroachDB binary. CUDA is not required; policy therefore selects a CPU
worker if S1 is reopened.

## RunPod preflight

- pod inventory: `[]`;
- one-worker requirement: satisfied in plan;
- persistent/network volume: none planned;
- synthetic bundle: planned;
- exact CPU hourly price: unavailable from the current CLI/inventory;
- finite maximum campaign cost: cannot be computed;
- worker creation: not attempted.

Unknown price is a mandatory stop under the current RunPod policy. No GPU was
substituted merely to obtain a public price.
