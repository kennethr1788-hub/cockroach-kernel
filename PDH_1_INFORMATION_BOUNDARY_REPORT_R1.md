# PDH-1 Information-Boundary Report R1

- `MECHANICAL_STATUS`: `PDH_1_INFORMATION_BOUNDARY_MECHANICAL_GREEN`
- `PRODUCT_CANDIDATE`:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `MEASURED_EXECUTIONS`: `30`
- `PASS`: `30`
- `FAIL`: `0`
- `MODEL_CALLS`: `0`
- `NETWORK_DENIAL_PROBE`: `GREEN`
- `DISPOSABLE_ROOT_TEARDOWN`: `30_OF_30`
- `B4_ORACLE_MATERIALIZED`: `0_OF_5`
- `MECHANICAL_RECEIPT_FILE_SHA256`:
  `9de60ade4e7ca403f4025802d8e1d71aeaec1819d5906e9d639cd4b5ca091b19`
- `MECHANICAL_RECEIPT_INTERNAL_SHA256`:
  `c1d0a6b0fc090ac6b9263c6be08ced045bc2c7393c9d60a22521acc07c99f189`

## Measured matrix

| Case | Repeats | Evidence outcome | Product verdict / reason | Deterministic |
|---|---:|---|---|---|
| B1 committed and captured | 5 | `RECOVERED_EXACT` | `PROMOTE / MAX_PROVEN_PREFIX` | yes |
| B2 modified tracked and captured | 5 | `RECOVERED_EXACT` | `PROMOTE / MAX_PROVEN_PREFIX` | yes |
| B3 untracked and captured | 5 | `RECOVERED_EXACT` | `PROMOTE / MAX_PROVEN_PREFIX` | yes |
| B4 created after capture, then lost | 5 | `UNRECOVERABLE_NO_SURVIVING_REPRESENTATION` | `REFUSE / NO_SURVIVING_CANDIDATE` | yes |
| B5 partial surviving representation | 5 | `RECOVERED_MAXIMUM_PROVABLE_SUBSET` | `PROMOTE / MAX_PROVEN_PREFIX` | yes |
| B6 tampered representation | 5 | `INVALID_TAMPERED_EVIDENCE` | `INVALID / REPRESENTATION_HASH_MISMATCH` | yes |

B1–B3 restored the exact frozen file hash. B4 wrote no replacement file and
listed the path as `NO_PROVEN_REPRESENTATION`. Its 257 oracle bytes existed
only in controller memory, were not passed to the child process, and were not
found in any case-root file. B5 restored only `src/provable.py` and listed
`notes/unverifiable.txt` as unrecovered. B6 made no workspace or output write.

## Enforcement and instrumentation

- Every product invocation used `/usr/bin/sandbox-exec`.
- Sandbox binary SHA-256:
  `8857d087219f0f39d3e3c163e5d0a0aed690cc22f34b50c7eee3d74f93e69688`
- Seatbelt profile SHA-256:
  `5c358b8d847211333e7ba22df82d84f796b5f30a41a2682209a949d783adbd08`
- A loopback connection probe failed under the same `(deny network*)` profile.
- The child environment contained only locale, fixed PATH, Python isolation,
  deterministic hash seed, and the disposable temp path.
- Every run records before/after root and workspace manifests, changed-file
  hashes, exact stdout/stderr hashes, product result, custody tree, output tree,
  one declared CLI tool call, zero model calls, and zero network egress.
- Static import scanning found no network or model client imports in
  `recovery_surface.py`, `cli.py`, `records.py`, or `fresh_context.py`.

## Failure preservation

The first full campaign and first diagnostic canary are preserved as
infrastructure-invalid evidence. They did not import or execute the product
because the evidence controller resolved the venv launcher to the base Python.
After a narrow evidence-only repair, a one-case public canary passed and an
independent GLM 5.2 same-packet preflight returned GREEN. No product, input,
outcome, or threshold changed.

## Exact claim supported mechanically

> Across 30 frozen local executions, explicitly captured representations were
> restored byte-exactly, partial evidence restored only its provable subset,
> absent evidence produced a deterministic refusal without inventing bytes,
> and tampered evidence was rejected without mutation.

This report is not independently GREEN until the final review packet returns a
valid GREEN verdict.
