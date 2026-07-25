# S1 RunPod Lifecycle Receipt

- `CAMPAIGN_ID`: `CK-S1-20260725-FOUNDATION`
- `POD_ID`: `48bqdill8w3vt0`
- `PACKET_SHA256`: `8aa3a3b7da4371ffec5569466f230c8052c7eb9bfe2593678728df3abe91149a`
- `CREATED_UTC`: `2026-07-25T21:19:06.362Z`
- `STOPPED_UTC`: `2026-07-25T21:19:20Z`
- `DELETED_CONFIRMED_UTC`: `2026-07-25T21:19:38Z`
- `RESULT`: `BLOCKED`
- `BLOCKER`: `RUNPOD_WORKER_MISMATCH`

## Returned worker

- compute: CPU;
- vCPU: 2;
- RAM: 4 GB;
- compute price: $0.06/hour;
- image: `runpod/base:1.0.2-ubuntu2204`;
- container disk: 20 GB;
- persistent/network volume: 0 GB / none;
- GPU count: 0;
- provider region: `US-NC-1`, Secure Cloud;
- exposed provider access port: SSH only.

The frozen packet authorized 2 vCPU / 8 GB at $0.08/hour. RunPodCTL did not
expose a CPU-flavor selector and the provider allocated 2 vCPU / 4 GB at
$0.06/hour. The cheaper worker was not silently accepted. It was stopped and
deleted before readiness, SSH, payload upload, extraction, or workload start.

Campaign-scoped running inventory and all-status inventory both returned `[]`
after deletion. No S1 SSH, transfer, child, workload, database, watchdog, or
paid background process remains. The first immediate pod-scoped billing query
returned `[]`; exact provider charge is therefore not yet available and is not
fabricated.
