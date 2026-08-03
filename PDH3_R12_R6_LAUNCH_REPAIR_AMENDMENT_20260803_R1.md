# PDH-3 R12 R6 launch repair amendment R1

`STATUS`: FROZEN_PENDING_GLM
`BASE_PACKET`: `PDH3_R12_R6_GZIP_PREFLIGHT_PACKET_20260803_R1.md`
`BASE_PACKET_SHA256`: `af8c55b8b2ce2cad83fc7c8b9fbeafc7c811ea53d013db7d048d23671029c890`
`MEASURED_24H_STARTED`: false

## Purpose and scope

This is a narrowly scoped repair to the already authorized, bounded R6
full-cardinality preflight. The first launch attempt at 2026-08-03T11:00Z
performed no provider creation: the host launcher rejected the orchestrator's
private runtime directory because it required that directory not to exist.
The prior attempt is preserved unchanged as failed evidence. This amendment
does not change workload, cardinality, thresholds, worker shape, price ceiling,
attempt count, launch window, stop/terminate deadlines, teardown, or the
prohibition on the 24-hour measured campaign.

## Exact repair binding

The host-only launcher now reuses the exact orchestrator-created runtime
directory only when it is a real, non-symlink directory; otherwise it fails
closed with `RUNTIME_ROOT_INVALID`. It creates the directory itself only when
the orchestrator has not created it. This removes a pre-provider staging bug;
it does not broaden filesystem or provider authority.

The repaired source passed the focused launch/config/remote-preflight tests
(20/20). The rebuilt transfer archive remains exact-member-set verified and
the fresh bundle receipt is bound below. The gzip evidence repair and failure
receipt retrieval remain inherited from the base packet.

## Frozen envelope inherited unchanged

- Maximum 3 sequential attempts, one worker at a time; no replacement after
  main-bundle upload.
- Secure Cloud NVIDIA L40S, at least 24 vCPU and 94 GiB RAM, 250 GiB disposable
  container disk, zero persistent/network volume.
- Exact image `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`.
- Rate ceiling $0.99/hour; aggregate ceiling $12.00.
- Launch window 2026-08-03T11:00:00Z through 11:45:00Z.
- Provider stop deadline 20:45:00Z; terminate deadline 21:00:00Z.
- Synthetic/sanitized payload only; no credentials, HOME, production, client,
  Qdrant, StateV2, launchd, or unrelated repository access.
- PF4, PF2R, PF5, PF6, PF7, and PF8 remain mandatory. A non-GREEN preflight
  cannot authorize the 24-hour campaign.

## New artifact bindings

| Artifact | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_r6_launch_pf4.py` | `f8788916faee35372cb2a5f23c5eb388e5da20d35d1ea130d33090aea9f763e1` |
| `.pdh3-runtime/r12-preflight/r6-gzip-20260803-r1/transfer-r2.tgz` | `6b4914dea402db504e6d0396d4c7fdb302964e18ea0615403fcbafe7f9b1d938` |
| `.pdh3-runtime/r12-preflight/r6-gzip-20260803-r1/bundle-receipt-r2.json` | `2391ca2be7170547a6f28bec723e9e2b91dc6e14ff1fd994b088224202db290b` |

## Gate and judge requirement

The host must recompute every listed hash, update the configured packet and
bundle paths to these exact artifacts, and obtain an independent GLM 5.2
`VERDICT: GREEN` over the final amendment hash before another creation request.
The builder may not self-approve. The retry envelope is exhausted at three
provider attempts, and all failed attempts require exact-ID and campaign
inventory absence before another attempt.
