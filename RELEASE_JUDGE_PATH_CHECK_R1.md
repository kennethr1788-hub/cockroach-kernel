# Release judge-path check R1

Status: `LOCAL_JUDGE_PATH_GREEN`

This is a local, keyless packaging check. It is not a public-release receipt,
an AWS deployment receipt, or a substitute for the required public video and
Devpost submission.

## Frozen candidate

- Candidate branch: `submission-candidate-20260810`
- Base source commit: `8f56f430be6ff06480325b7ee3421aab0ebf316f`
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
| 1 | `/tmp/ck-release-final-venv.52IAUB` | pass | pass | pass | pass |
| 2 | `/tmp/ck-release-final2-venv.KldsO3` | pass | pass | pass | pass |

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

Recorded UTC: `2026-08-10T08:59:57Z`
