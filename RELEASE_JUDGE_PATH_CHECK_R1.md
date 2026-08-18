# Release judge-path check R1

Status: `LOCAL_JUDGE_PATH_GREEN_R3`

This is a local, keyless packaging check. It is not a public-release receipt,
an AWS deployment receipt, or a substitute for the required public video and
Devpost submission.

## Frozen candidate

- Candidate branch: `public-release-candidate-20260810`
- Source candidate commit/tree: verify with `git rev-parse HEAD` and
  `git rev-parse HEAD^{tree}`; the exact values are recorded in the external
  R5 release packet and its binding.
- Sanitized export: explicit allowlist; see `PUBLIC_EXPORT_MANIFEST_R1.md`
- Python target: Python 3.12
- Dependency policy: runtime standard library; build backend pinned to
  `setuptools==75.6.0`
- Network/credential requirement for this path: none

## Fresh-install trials

Each trial used a new virtual environment and installed the candidate from a
local source path. The command sequence was:

```text
python3.12 -m venv .venv
.venv/bin/python -m pip install /path/to/candidate
.venv/bin/cockroach-kernel --help
.venv/bin/cockroach-kernel demo --explain --output-root /tmp/cockroach-kernel-demo
.venv/bin/cockroach-kernel inspect-memory --input examples/memory-snapshot.json
```

Observed on 2026-08-10:

| Trial | Fresh environment | Help | Demo promotion | Demo refusal | Memory inspection |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | `/tmp/ck-public-final-1-venv.DIMapQ` | pass | pass | pass | pass |
| 2 | `/tmp/ck-public-final-2-venv.FrdQ9W` | pass | pass | pass | pass |

The two demo outputs were byte-identical:

- `promotion-receipt.json`: `eb1ea7a909b0cab76e8e7ef711c9dfe493affdf7f420ff43066fc75d525965bc`
- `refusal-receipt.json`: `f94310e76ffc8c99c335e577f14117fe017dc277658fed0f0d79e8ef13404afd`

The demo output explicitly reports `KEYLESS_LOCAL_REPLAY`,
`NETWORK_USED: false`, and `CREDENTIALS_USED: false`. The local verifier is
the authority; cloud services and model endpoints are not invoked.

The installed package's scoped regression suites also passed from the fresh
environment:

- P7 records/recovery suite: 29 tests
- P9 cloud-boundary suite: 114 tests
- P4 verifier suite: 6 tests

These suites were run with explicit package import roots; the documented judge
path itself remains the shorter CLI path above.

## Scope and limitation

This check proves the declared clean-clone CLI path, not every historical
source-test module. The public branch is the sanitized allowlisted release;
historical development/audit material is not part of this branch.

## Current anonymous-clone verification

On 2026-08-18 UTC, an anonymous shallow clone resolved to the exact commit/tree
recorded in the external R5 release packet. A fresh Python 3.12 environment
passed `--help`, the deterministic promotion/refusal demo, and
`inspect-memory` without credentials or network use. Output hashes were:

- help: `4c9edda665667bba105a7d6b16cf4d6a1126c211e768c904e7e79fca9697459a`
- demo: see the current R5 packet's anonymous-clone verification record
- memory inspection: `37a564d80cc48daeff9b75a1ecda5bfa00bc41caba63066c7df376c204d1a3a9`

Recorded UTC: `2026-08-18T05:00:48Z`
