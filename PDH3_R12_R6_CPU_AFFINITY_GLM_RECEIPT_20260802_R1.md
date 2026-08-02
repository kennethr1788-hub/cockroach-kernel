# PDH-3 R12 R6 CPU-affinity GLM receipt R1

Status: `CPU_AFFINITY_PACKET_GREEN_PENDING_PAID_PF4_AUTHORIZATION`

UTC reviewed: `2026-08-02T09:39:33Z`

## Exact reviewed artifact

- packet:
  `PDH3_R12_R6_CPU_AFFINITY_PREFLIGHT_PACKET_20260802_R1.md`;
- packet SHA-256:
  `0c3039d1e502b77c18c7985a1f91c9437c4474e63d2fe4007684b062cc3cddf4`;
- implementation commit bound by the packet:
  `8465880b3753e700217231c59ad43f3362ecdd6d`;
- packet-freeze commit:
  `8db36269559d6859c3abe7922606907cdc0a7f20`.

## Judge identity and route proof

- lane: direct `glm-zai`, non-authoring judge only;
- requested model: `glm-5.2`;
- served model reported by the verified wrapper: `glm-5.2`;
- exact-model mode: fallback disabled, model identity required;
- availability smoke immediately before review:
  `READY_GLM_52_DIRECT`;
- raw output:
  `PDH3_R12_R6_CPU_AFFINITY_GLM_RAW_20260802_R1.txt`;
- raw output SHA-256:
  `ec81a1de7301475cd2109dfc30c5283281bf1e9ed0d0b34ffa5733d40b6befd0`.

The judge had no shell, write, repository, credential, browser, provider,
implementation, or worker-launch authority.

## Exact verdict

- overall: `GREEN`;
- affinity math: `GREEN`;
- kernel enforcement: `GREEN`;
- inheritance proof: `GREEN`;
- fail-closed semantics: `GREEN`;
- threshold preservation: `GREEN`;
- evidence classification: `GREEN`;
- authority boundary: `GREEN`;
- findings: none.

The returned packet hash exactly matches the locally computed packet hash.

## Controlling boundary

This verdict closes the prospective packet-design gate only. It does not:

- authorize a paid RunPod lifecycle;
- prove the Linux affinity API is available or permitted in a future worker;
- prove PF-4, PF-2R through PF-8, R6, or the 24-hour campaign;
- convert the prior 32-vCPU/125-GiB rejection into a pass;
- permit stale launch deadlines or controller configuration reuse.

The next legitimate action is a separately authorized paid PF-4 attempt with
fresh provider inventory, pricing, absolute stop/terminate deadlines, exact
packet/controller bindings, and mandatory on-worker affinity evidence before
main-bundle upload.
