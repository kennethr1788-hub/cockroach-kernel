# Release judge-path check R1

Status: `LOCAL_JUDGE_PATH_GREEN_R2`

This is a local, keyless packaging check. It is not a public-release receipt,
an AWS deployment receipt, or a substitute for the required public video and
Devpost submission.

## Frozen candidate

- Candidate branch: `public-release-candidate-20260810`
- Source candidate commit: `3053166d2dc2909e7329e35e5621bffa2907f23e`
- Source candidate tree: `0d25af55cde4fbf58789c520293156c656e65d29`
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
source-test module. The repository still contains development/audit material
that must be excluded from a public export; the public release must be built
from an allowlist rather than publishing this checkout wholesale.

## Current anonymous-clone verification

On 2026-08-18 UTC, an anonymous shallow clone resolved to the commit and tree
above. A fresh Python 3.12 environment passed `--help`, the deterministic
promotion/refusal demo, and `inspect-memory` without credentials or network
use. Output hashes were:

- help: `4c9edda665667bba105a7d6b16cf4d6a1126c211e768c904e7e79fca9697459a`
- demo: `66f19fce175da266d5a6b26f0c063f0ceee5997965e3beaf7ad1577571005bf6`
- memory inspection: `37a564d80cc48daeff9b75a1ecda5bfa00bc41caba63066c7df376c204d1a3a9`

Recorded UTC: `2026-08-18T05:00:48Z`
