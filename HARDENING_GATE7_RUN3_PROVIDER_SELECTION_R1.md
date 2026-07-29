# Hardening Gate 7 Run 3 Provider Selection R1

- UTC frozen: `2026-07-29T04:13:43Z`
- active RunPod inventory: `[]`
- official template inventory: `runpod-ubuntu`, `runpod-ubuntu-2204`,
  `runpod-ubuntu-2404`
- selected template: `runpod-ubuntu-2204`
- selected image: `runpod/base:1.0.2-ubuntu2204`
- worker class: smallest sufficient RunPod CPU worker
- accepted returned shape: exactly 2 vCPU, 4 or 8 GiB RAM, zero GPU
- accepted compute rate: no more than `$0.10/hour`
- accepted total active rate: no more than `$0.12/hour`
- container disk: at most 20 GiB
- persistent/network volume: zero
- aggregate campaign ceiling: `$5.00`
- authenticated account current spend at preflight: `$0.002/hour`
- provider CPU limitation: runpodctl 2.7.2 exposes no pre-creation CPU-flavor
  inventory command; the complete returned shape and current price are therefore
  fail-closed postconditions checked before upload. Prior same-day accepted
  workers returned 2 vCPU, 4 GiB, zero GPU at `$0.06/hour`.

Any mismatched shape, image, disk, volume, GPU, rate, or identity is deleted
before upload and consumes one authorized creation attempt.
