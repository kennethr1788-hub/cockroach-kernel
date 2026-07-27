# Hardening Gate 4 — Comparative Baseline Protocol R2 Amendment

## Control fields

- `STATUS`: `AMENDED_PENDING_INDEPENDENT_REVIEW`
- `PARENT_PROTOCOL`: `HARDENING_GATE4_BASELINE_PROTOCOL_R1.md`
- `PARENT_PROTOCOL_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `SUPERSEDES_FOR_NEW_CAMPAIGNS`: `R1_PLATFORM_AND_EVIDENCE_MODE_CLAUSES_ONLY`
- `METHODS`: `ORDINARY_GIT; GIT_PLUS_RESTIC_0_19_0; PRODUCT`
- `MEASURED_EXECUTIONS`: `54`
- `HUMAN_GATE`: `none`
- `RUNPOD_ACTION`: `none`

R1 remains incorporated by its exact hash except where this amendment is more
specific. Historical R1/Gate 5/Gate 6 evidence is preserved and does not gain
authority from this amendment.

## A1 — Platform-neutral common source

The common executable command embedded in every scenario is exactly:

```json
["python3","tests/check.py"]
```

No absolute interpreter path, host path, `sys.executable`, architecture, or
operating-system string may enter the scenario, source-bundle, event, loss, or
allowed-information hash. The executable is resolved only at trial runtime
inside the frozen isolated `PATH`. Its observed version and binary SHA-256 are
recorded in every canonical receipt.

The same `(scenario_class, repetition)` must therefore produce byte-identical
public bytes and hashes on Darwin arm64 and Linux amd64. A mismatch blocks the
campaign before measurement.

## A2 — Runtime-attested tool provenance

The harness does not claim one host's Git identity on another host.

- `CK_GATE5_GIT` names the exact Git executable selected before a campaign.
- The harness verifies it is a regular file, invokes `<git> --version`, hashes
  its exact bytes, uses that same executable for every Git command, and places
  the observed version/hash in each applicable receipt.
- Python is resolved from the isolated trial `PATH`, version-invoked, hashed,
  used by the common executable command, and recorded in every receipt.
- Gate 6 freezes the exact Linux Python and Git paths, versions, and hashes in
  the independently reviewed preflight packet. Every measured receipt must
  equal that frozen provenance; drift blocks the campaign.

Restic remains version `0.19.0` and is accepted only when its exact binary hash
matches one of these official release artifacts and its own version output
matches the corresponding value:

| Platform | Binary SHA-256 | Required version output |
|---|---|---|
| Darwin arm64 | `f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd` | `restic 0.19.0 compiled with go1.26.4 on darwin/arm64` |
| Linux amd64 | `ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c` | `restic 0.19.0 compiled with go1.26.4 on linux/amd64` |

The official Linux archive remains hash-bound at
`13176fe6d89d4357947a2cd107218ab2873a5f9d8e1ac2d4cd1c8e07e6839c21`.
No other Restic hash/version/platform is permitted.

## A3 — Canonical evidence mode

The canonical receipt schema is revision `gate5-comparative-receipt-v2` and
adds these required fields:

```text
evidence_mode
runtime_platform
```

`evidence_mode` is exactly one of:

- `PREFLIGHT`: local or remote non-measured contract/smoke evidence. Required
  limitations are `LOCAL_SYNTHETIC_PREFLIGHT`, `NOT_LIVE_AWS`, and
  `NOT_GATE6_MEASURED_EVIDENCE`.
- `MEASURED_GATE6`: the frozen Linux RunPod 54-row comparative campaign.
  Required limitations are `SYNTHETIC_PAIRED_COMPARATIVE`, `NOT_LIVE_AWS`,
  `NOT_PRODUCT_SCALE`, and `RUNPOD_GENERIC_COMPUTE`.

`MEASURED_GATE6` fails closed unless the runtime reports Linux, the candidate
commit is exactly 40 lowercase hexadecimal characters, and the campaign ID is
an explicit non-default `ck-gate6-*` identifier. Receipts are emitted directly
with their true mode; post-execution relabeling or canonical-byte rewriting is
forbidden.

## A4 — Unchanged fairness and authority

All R1 fairness, pairing, method, scenario, metric, timeout, no-tuning,
network-denial, residue, raw-reporting, and limitation clauses remain binding.
The product verifier and its sole promotion/refusal authority are unchanged.
This amendment does not authorize a RunPod worker, measured execution, public
claim, release, or submission.

## Kill line

Block before measurement if the source hash varies by platform, a tool receipt
does not match observed bytes, an unallowlisted Restic artifact is supplied, a
measured receipt carries preflight labels (or vice versa), or any R1 fairness or
authority clause changes without another independently reviewed amendment.
