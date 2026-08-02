# PDH-3 R12 R6 replacement attempt 01 blocked receipt R1

Status: `PDH3_R12_R6_REPLACEMENT_BLOCKED`

Blocker: `RETURNED_WORKER_MISMATCH`

UTC launch: `2026-08-02T09:15:03Z`

UTC closeout verified: `2026-08-02T09:16:39Z`

## Bound execution state

- implementation commit:
  `618bc82eed309e157855e997383cd9e79687e4ce`;
- controller launch HEAD:
  `94e6f0f20d979da91e73a8d19e4bc001a38a9ad2`;
- packet:
  `PDH3_R12_R6_REPLACEMENT_PREFLIGHT_PACKET_20260802_R1.md`;
- packet SHA-256:
  `0bec28d822bcf61ebb9560fc172eb8933428bbd1773c1d33a120c508a8362802`;
- config SHA-256:
  `90fac7667076a39b729f3fd6a711df356c0df8465e5efd96b6163d9e1e230f1a`;
- direct GLM 5.2 raw-result SHA-256:
  `2ca6a726052bdb0e2970e6524731e28016221d9b42d320cc584cb172f4cc282c`;
- GLM verdict: `GREEN` for one replacement preflight;
- archive SHA-256:
  `3152cd00011d1c8c23d873a051b3651407379699ffb9e180a3581f86b44a3418`.

## Attempt result

- Pod ID: `zby5qthlswc7cy`;
- name: `ck-pdh3-r12-preflight-r6-replacement-20260802a-01`;
- requested/returned compute rate: `$0.99/hour`;
- returned cloud/GPU: Secure Cloud, one `NVIDIA L40S`;
- returned image:
  `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- returned disposable disk: 250 GB;
- returned persistent/network volume: 0 GB;
- returned CPU: 32 vCPU;
- returned RAM: 125 GiB;
- frozen minimum RAM for 32 returned vCPU: 128 GiB;
- shortfall: 3 GiB;
- elapsed controller attempt: 37.023 seconds;
- main bundle uploaded: `false`;
- PF-4 payload uploaded: `false`;
- 24-hour measured clock started: `false`.

All returned properties other than the frozen RAM-per-vCPU ratio were within
the packet. `125 < 4 * 32`, so `exact_shape()` correctly returned false. The
controller classified the attempt `RETURNED_WORKER_MISMATCH`, refused upload,
deleted the Pod, exhausted the mechanically single-attempt envelope, and
returned blocked.

## Teardown and live provider proof

- provider delete response: `deleted: true`;
- exact-ID lookup after deletion: HTTP 404 `pod not found`;
- post-delete campaign inventory: `[]`;
- fresh global active Pod inventory: `[]`;
- lifecycle chain: 3 hash-valid events;
- lifecycle terminal event: `TEARDOWN_GREEN`;
- lifecycle terminal event hash:
  `37532df40515372858281e1a2c32422929cc1aa6d8dc71e93ee10a220c712b1e`;
- matching orchestrator/controller/guard processes after closeout: none;
- current account spend after closeout: `$0.002/hour` from unrelated retained
  storage;
- Pod billing query for the attempt window: empty/delayed (`[]`);
- exact provider charge: not yet itemized; no zero-charge claim is made.

## Evidence hashes

| Evidence | SHA-256 |
|---|---|
| `attempt-01/attempt-result.json` | `eb0c979e4970b2c5b9025f5d955574317b20b7b105439dc6063a0bbd3888dfa2` |
| `attempt-01/create.stdout` | `4446a5f2f8b8567aca42f850bdcb2ed5ddea57b891f6b684a2bffe45cc9b80ec` |
| `attempt-01/pod-get.json` | `5c85273ad6134a44b4da6c0f73ec47e14f24085fb3e59b09c01770ae3df8e931` |
| `attempt-01/delete.stdout` | `ff3c51846b1c09abd9519e55c3c859f4f80d095e3b32034cf8cb1840bd9cf213` |
| `attempt-01/post-delete-inventory.json` | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |
| `attempt-01/lifecycle.ndjson` | `c7d7f26a74aacb9720d86733ae05f989e24205b896203dbf0ea66c23cafc906c` |
| `attempt-ledger.json` | `ab58c6a775bc3950d8716662a05c9a2947b19d12c6687a1b7dfc2d5376d2aff1` |
| `ORCHESTRATOR_BLOCKED.json` | `056810ff79c8257b194d51bbf4597d46b5fc6bf4fa62da1a4b1834b7b7b01d65` |
| `pf4_create.stderr` | `e057fcb2e0067280092ac91a82e79aa7144677b21cea00026330247665fe23dc` |
| `precreate-account-sanitized.json` | `31dd5585f909908f3d75be8360fe5409ccdd87ac9ad2278c667833123e792bd5` |
| `precreate-inventory.json` | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |

Raw provider create evidence contains only provider-returned metadata and public
SSH keys; it is kept in the ignored runtime evidence tree and is not copied
into the repository.

## Controlling result and resume action

This attempt is not PF-4 evidence and cannot advance R6. The prior repaired
payload remains untested on-provider because no upload occurred.

No additional creation attempt is authorized under the packet. A legitimate
resume requires a new operator authorization and one fresh same-hash review
packet. That packet must either select a provider shape satisfying the existing
ratio or prospectively justify and test a bounded effective-vCPU cap; it may
not silently weaken or reinterpret this failed attempt after the result became
known.
