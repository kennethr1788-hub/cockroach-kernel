# Hardening Gate 5 — Dependency and License Manifest R1

## Runtime candidate

| Component | Frozen version/source | License | Runtime role |
|---|---|---|---|
| Python | `>=3.12`, standard library | PSF-2.0 | CLI, verifier, harness |
| setuptools | `75.6.0` build backend | MIT | package build only |
| pg8000 | `1.31.5`, optional extra | BSD-3-Clause | optional AWS demo database transport |
| CockroachDB | cloud service plus project-local verified binary for local tests | CockroachDB licensing terms; service terms apply | durable SQL/vector/changefeed evidence |
| AWS Lambda/API Gateway/CloudWatch | managed AWS services | AWS service terms | bounded public demo/evaluator path |

The default keyless CLI has no third-party Python runtime dependency. The
optional `aws-demo` extra is pinned. No package is installed globally by Gate
5. The release repository license is a Gate 10 release obligation and is not
misrepresented as already present here.

## Comparative preflight tools

| Tool | Frozen version | SHA-256 | License |
|---|---|---|---|
| Apple Git | `2.50.1 (Apple Git-155)` | `179301dcb41ea78accc3fa0048a7e6f6710d891945a751a34addd622020c1818` | GPL-2.0-only upstream Git terms |
| Restic Darwin arm64 | `0.19.0` | `f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd` | BSD-2-Clause |
| Restic Linux amd64 archive | `0.19.0` | `13176fe6d89d4357947a2cd107218ab2873a5f9d8e1ac2d4cd1c8e07e6839c21` | BSD-2-Clause |
| Restic Linux amd64 binary | `0.19.0` | `ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c` | BSD-2-Clause |

Restic provenance is the official `restic/restic` GitHub release `v0.19.0` and
its official `SHA256SUMS`. The downloaded Linux artifacts remain ignored under
`.hardening-runtime/gate5-tools/`; only their provenance and hashes are frozen.
No Restic password bytes enter evidence.
