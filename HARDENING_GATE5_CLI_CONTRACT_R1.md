# Hardening Gate 5 — Frozen CLI Contract R1

Judge-facing commands remain:

```text
python3.12 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/cockroach-kernel demo --explain --output-root <fresh-relative-root>
.venv/bin/cockroach-kernel inspect <canonical-receipt>
```

The deterministic keyless replay remains the default judge path. It uses no
network, paid account, private credential, AWS session, or live CockroachDB
cluster. Gate 5 changes S3 custody/failure behavior and adds a comparative
preflight harness; it does not change the CLI's P4 pass/refuse authority.

- `pyproject.toml` SHA-256: `ca8d0a873ddfa1d628f54ef5ca989b88e087b967f7d366bca66d8b59249b6dbd`
- `cockroach_kernel/cli.py` SHA-256: `98c0dc51de474a472d49fe014910bfb7d30454a851ba390e66ebe1aeea5a9caf`
- `p4-verifier/verifier.py` SHA-256: `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`
