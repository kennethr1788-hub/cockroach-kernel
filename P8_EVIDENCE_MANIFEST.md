# P8 Evidence Manifest

- `UTC_CREATED`: `2026-07-26T10:49:32Z`
- `IMPLEMENTATION_COMMIT`: `a17f60303ebbc1446871f9cac11c7b82f89ffd83`
- `PARENT_GATE`: `CK_S2_RECOVERY_SOAK_GREEN`
- `TARGET_GATE`: `CK_P8_GOLDEN_GREEN`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `CORRECTIONS_SHA256`: `de531da8eaa9a39a2b39ee85206a6fdb348279fe042d55f67b22d3f6b88e11a7`

## Mechanical commands and results

```text
python3 p8-golden/make_fixtures.py
python3 -m py_compile p8-golden/*.py
(cd p8-golden && PYTHONWARNINGS=error python3 -m unittest -v)
python3 p8-golden/run_integration.py
```

- Focused unit tests: 15/15 PASS.
- Inherited P3-P8 unit tests: 116/116 PASS.
- Canonical fixtures: 14 files, regenerated deterministically.
- Incident set: nine incidents containing two expected promotions and seven
  expected refusals, hash
  `dd1d02820c5daaaa58f46a5507fd09aae12c5eb5deebac2601679d47ce751512`.
- Proposals: eight total; one promoted and seven rejected with reason receipts.
- Five-repeat replay and incident/proposal-order independence passed.
- Two fresh-root CockroachDB trials returned byte-equivalent semantics.
- An invalid promotion-receipt hash aborted the entire transaction and left
  `0 policies / 0 proposals / 0 promotions` for the candidate.
- Completed promotion plus duplicate retry left one golden policy, eight
  proposals, and one promotion.
- Explicit rollback restored `policy-p8-v1`.
- Duplicate rollback failed atomically and left `policy-p8-v1` golden.
- Final table counts in each trial: `2 policies / 1 incident set / 8 proposals /
  1 promotion / 1 rollback`.

## Safety and residue

- `gitleaks detect --no-git --source p8-golden`: exit 0, no leaks.
- `detect-secrets`: findings are deterministic synthetic SHA-256 fixture
  values; no credential was accepted as a real secret.
- Private-path scan found only the deliberate `env["HOME"] = fake_home`
  isolation line in the disposable integration runner.
- No symlink or `p8-db-*` generated root remained.
- Both P8 contributor worktrees were removed; their branches were deleted.
- No AWS, RunPod, public action, HOME/live memory, Qdrant, StateV2, launchd,
  client data, credentials, or P9 surface was accessed.

## Principal source hashes

```text
efaeeb1d391253c19ee9125fc465d76e88ffba709389a258ed6640a36f399fb4  P8_CONTRACT.md
e7cefb237a9238d92b6d0afb0ec9b1a69fa458570a40441d049dc17f760d75b6  p8-golden/golden.py
c2c77bde0bc61d5a04328b601ecdd7b4fe2361b46f704c1c6e9606c3d56ef72e  p8-golden/make_fixtures.py
363117ff656ed08105e629ab9a2794a665270d909f85f111a32183b0c898026c  p8-golden/migrations/001_golden.sql
44fd21652694ba067cc1727d64ddfd686b3c63141e92dc44eb56a01e5a345f58  p8-golden/run_integration.py
14419628d991da71ce04ce475c42454da169a133f3c676f52181b521c3091f19  p8-golden/test_golden.py
```

P8 makes no claim of foundation-model retraining. Reflection is untrusted
proposal input; deterministic local replay is the sole pass/fail authority.
