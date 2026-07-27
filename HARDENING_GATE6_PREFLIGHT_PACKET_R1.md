# Hardening Gate 6 — Preflight Packet R1

## Control fields

- `PACKET_STATUS`: `BLOCKED_MECHANICAL`
- `TARGET_GATE`: `HARDENING_6_RUN1_GREEN`
- `PARENT_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `bd29bd23e831175aa54526b9e3c48bd04e8af3ed`
- `CURRENT_COMMIT_AT_DIAGNOSIS`: `e7d179f9668977e093337db404b90972e6ed898f`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `HARDENING_PLAN_SHA256`: `1ce953127138a35bd9588d686bbefefc0b012e8f2188a8fea736842030d57310`
- `GATE4_PROTOCOL_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `GATE5_PACKET_SHA256`: `8d72c554e3b23b1fafac05b265dd410406e76990b733b48ed9496ff05efaff29`
- `GATE6_EXECUTION_PROMPT_SHA256`: `635c4c457e9f2393ec6be9b71289f0887185c21ef517b3d2be00da4eb705489a`
- `UTC_RECORDED`: `2026-07-27T22:04:15Z`

## Mechanical blocker

The immutable Gate 5 candidate cannot execute the frozen Linux Gate 6
comparison without behaviorally relevant changes:

1. `hardening-gate5/comparative.py` accepts only the Darwin arm64 Restic
   SHA-256 `f6c965a0...` in `ResticAdapter.setup`. The independently verified
   official Linux amd64 Restic binary has SHA-256 `ae7fe58a...`; direct setup
   returns `HarnessError:RESTIC_BINARY_HASH_MISMATCH` before any Restic command.
2. `GitAdapter.tools` reports Apple Git `2.50.1` and its Darwin binary hash
   unconditionally. A Linux worker would therefore emit false tool provenance.
3. `ResticAdapter.tools` reports `darwin/arm64` and the Darwin binary hash
   unconditionally. A Linux worker would therefore emit false tool provenance.
4. Every receipt is unconditionally labeled `LOCAL_SYNTHETIC_PREFLIGHT` and
   `NOT_GATE6_MEASURED_EVIDENCE`. Rewriting that after execution would mutate
   raw evidence and invalidate the canonical receipt hash.
5. The frozen scenario generator embeds `sys.executable` in the common source
   bundle. The local and Linux-like executable paths produce different frozen
   source-bundle hashes (`4e42f9b6...` versus `6b0f3be...`). The Gate 4 contract
   requires source bundles and allowed information to remain frozen.

The current source is byte-identical to candidate commit `bd29bd2` and has
SHA-256 `bb107750...`; this is not post-freeze drift.

## Why orchestration cannot repair it

A wrapper that substitutes hashes, patches tool identities, rewrites receipt
limitations, or changes the executable command would alter candidate behavior,
allowed information, evidence semantics, or canonical raw receipts after
freeze. The Gate 6 authorization explicitly forbids those actions and requires
`EVIDENCE_CANDIDATE_INVALIDATED` instead.

## Provider and cost state

- verified RunPodCTL: `2.7.2-309512b`, SHA-256 `a016e442...`;
- active RunPod inventory before closeout: `[]`;
- worker creation attempts: `0`;
- payload uploads: `0`;
- measured executions: `0`;
- RunPod charge caused by Gate 6: `$0.00`.

## Judge state

No preflight judge was invoked. The packet cannot truthfully request GREEN
while the candidate is mechanically ineligible for the required Linux runtime.
Blocked status does not require the builder to manufacture a judge verdict.

## Required next action

Reopen the applicable Gate 4/Gate 5 contracts, make platform-stable source and
tool-provenance behavior explicit, replace preflight-only receipt labeling with
a frozen campaign-mode contract, rerun the affected independent reviews, and
freeze a new evidence candidate before constructing another Gate 6 packet.
