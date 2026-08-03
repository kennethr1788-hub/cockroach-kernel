# PDH-3 R12 R6 GZIP full-cardinality preflight packet R1

`STATUS`: FROZEN_PENDING_GLM
`UTC_FROZEN`: 2026-08-03T10:28:43Z
`CAMPAIGN_ID`: ck-pdh3-r12-preflight-r6-gzip-20260803
`MEASURED_24H_STARTED`: false
`BUILDER_SELF_APPROVAL`: forbidden

## Authorization and envelope

- Authorization file: `PDH3_R12_R6_GZIP_AUTHORIZATION_ENVELOPE_20260803_R1.md`
- Maximum creation attempts: 3, sequential, one worker at a time.
- Replacement after main-bundle upload: forbidden.
- Launch window: 2026-08-03T11:00:00Z through 2026-08-03T11:45:00Z.
- Provider stop deadline: 2026-08-03T20:45:00Z.
- Provider terminate deadline: 2026-08-03T21:00:00Z.
- Maximum successful paid lifetime: 36,000 seconds.
- Aggregate cost ceiling: $12.00.
- Frozen Secure Cloud rate ceiling: $0.99/hour.
- Worker: one NVIDIA L40S, at least 24 vCPU, at least 94 GiB RAM, 250 GiB
  disposable container disk, zero persistent/network volume, and the exact
  image `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`.
- Synthetic and sanitized payload only; no credentials, HOME, client data,
  Qdrant, StateV2, launchd, production data, or unrelated repositories.

## Live provider snapshot

The live snapshot was captured before packet freeze with the hash-pinned
`runpodctl` binary. L40S Secure Cloud was available at $0.99/hour with low
stock; matching datacenters were recorded in the snapshot. No running Pod was
present at capture time.

| Artifact | SHA-256 |
|---|---|
| `.pdh3-runtime/r12-preflight/r6-gzip-20260803-r1/provider-snapshot.json` | `eab90cddcaf1ba826ae1cde361c8bd015b619f3e80efcf128a69763cfe14c4ff` |
| `.pdh3-runtime/r12-preflight/cli-20260803-r1/runpodctl` | `67cc575f518d05258f35c4334422f6f730446b7b88864933ed65a05e990ea1f2` |

## Candidate repair bound to this packet

The previous full-cardinality R6 attempt reached PF6 GREEN and failed PF7 with
`EVIDENCE_PROJECTION_LIMIT`. The repaired candidate makes no workload,
cardinality, latency, fault, or threshold change. PF7 still collects one
resource sample per second and preserves the same canonical record body,
per-record SHA-256, previous-record hash, fsync, and sample count. The stream
is now gzip-compressed canonical JSON-lines (`growth-observer.ndjson.gz`) so
the evidence is losslessly recoverable while remaining inside the growth cap.
The host controller also retrieves `failure.json` when `result.json` is absent,
preserving the actual remote blocker instead of collapsing it into transport
failure.

## Source and payload bindings

| Artifact | SHA-256 |
|---|---|
| `post-dogfood/pdh3_r12_remote_preflight.py` | `35048b3de30265f045d7176f3627ee84806b52a67c9959bb857b1e367945dca0` |
| `post-dogfood/pdh3_r12_r6_run_pf2r_pf7.py` | `66cf9672e95ff4e8411b68906ca5c85bf40e2ea9d4789bea7023d7ae453b74a4` |
| `post-dogfood/pdh3_r12_r6_config.py` | `c7d773b5fb996cf4cffd371f67cd4f80b5a82664cb5c332924aefa9b8c2b36a1` |
| `post-dogfood/pdh3_r12_r6_orchestrator.py` | `4d868cf66308e627a6f2ed9e3576f83535b5a6838131784cfcb74fbf07215ccf` |
| `s2-soak/lifecycle_guard.py` | `51258c2d983a6d0764485ff67ecd5e662085331758a2ce1d41813ea79652a5c6` |
| `.pdh3-runtime/r12-preflight/r6-gzip-20260803-r1/transfer.tgz` | `7a4a0aa7f13c8b7a8b84ee0c3e205cff59cff2d3c791a9cd2e26d18f165345ea` |
| `.pdh3-runtime/r12-preflight/r6-gzip-20260803-r1/bundle-receipt.json` | `47ed2a84619e68219e2027a6d6d5111c06a2a9b86872274eea325f2fe19ee11f` |

The bundle has an exact 52-member set, regular files only, and no host control
plane or credential material. It includes the repaired remote preflight and
the hash-only history manifest for prior attempts.

## Required gates

1. PF4 worker capability, CPU-affinity, tracer, extracted-bundle smoke, and
   remote residue checks.
2. PF2R full-cardinality deterministic setup with exact counts, content
   reconciliation, bounded SQL operations, rollback, and teardown.
3. PF5 exact full-cardinality counts and ANN quality.
4. PF6 named query families, gateway A/B, observer A/B, and mixed epochs.
5. PF7 900-second full-cardinality growth canary. Projected evidence must be
   below 80% of the 20 GiB evidence cap; projected database and network growth
   must remain within their frozen limits. Same-host fault/reconciliation,
   post-fault affinity, off-Pod checkpoint acknowledgment, and partial-successor
   rejection are mandatory.
6. PF8 retrieval must hash-verify all evidence, preserve a remote failure
   receipt if the run blocks, delete the worker, prove exact-ID absence, and
   prove empty campaign inventory.

## Kill lines

Stop and preserve evidence on any hash mismatch, private/credential path,
undeclared egress, nondeterminism, exact-count/content mismatch, latency or
growth threshold breach, missing checkpoint, process/resource leak, failed
teardown, unknown price, deadline drift, or semantic failure receipt. A
non-GREEN preflight cannot authorize the 24-hour campaign.

## Success boundary

This packet authorizes only the bounded full-cardinality preflight. It is GREEN
only after PF4–PF8 complete, evidence and teardown are verified, all hashes
agree, and a fresh independent GLM 5.2 review returns GREEN over the exact
packet hash. The 24-hour measured campaign remains separately blocked until
that result and a separate final-campaign packet are independently GREEN.
