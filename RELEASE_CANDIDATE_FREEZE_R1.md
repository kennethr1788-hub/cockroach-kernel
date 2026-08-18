# Cockroach Kernel release-candidate freeze R1

Status: `RELEASE_CANDIDATE_VERIFIED_PUBLIC_R3`

This freeze identifies the public candidate. It authorizes neither editing
Devpost fields nor the final Devpost submission.

## Candidate identity

- Branch: `public-release-candidate-20260810`
- Candidate commit/tree: verify with `git rev-parse HEAD` and
  `git rev-parse HEAD^{tree}`; the exact values are recorded in the external
  R5 release packet and its binding.
- Sanitized export manifest: `PUBLIC_EXPORT_MANIFEST_R1.md`
- Freeze date: 2026-08-18 (UTC)
- Target platform: macOS arm64 or another Python 3.12 environment with the
  documented standard-library runtime
- Judge-path receipt: `RELEASE_JUDGE_PATH_CHECK_R1.md`

## Required local path

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/cockroach-kernel --help
.venv/bin/cockroach-kernel demo --explain --output-root /tmp/cockroach-kernel-demo
```

The path is offline, keyless, and free to run. It is a labeled deterministic
replay of the genuine build-time capture; it is not a live GPT-5.6 call.

## Integration and claim ceiling

The candidate may describe only these bounded integrations:

1. CockroachDB Distributed Vector Indexing for receipt-linked trajectory
   retrieval, with bounded single-region evidence.
2. CockroachDB Managed MCP Server in read-only mode for the declared
   receipt-view inspection. The MCP surface is not a recovery authority.
3. AWS Lambda as a bounded advisory worker. Its output is untrusted and the
   local deterministic verifier remains authoritative.

The candidate must not claim MCP write/DDL authority, MCP-controlled recovery,
Bedrock, Bedrock Agents, SageMaker, ECS, EKS, S3, ccloud runtime control,
multi-region or multi-failure-domain resilience, production-scale durability,
arbitrary deleted-byte recovery, or elimination of backups/Git/permissions.

The exact wording is maintained in `COCKROACH_AWS_CLAIMS_R2.md` and the
conservative submission draft is `DEVPOST_SUBMISSION_DRAFT.md`.

## Public-export boundary

The public branch is the completed allowlisted export. Historical audit
packets, runtime directories, local paths, and raw provider receipts are not
public assets. The external R5 packet records the final scan, exact
commit/tree, and anonymous clone verification.

The intended implementation allowlist is limited to the runtime and judgeable
documentation: `LICENSE`, `README.md`, `pyproject.toml`, `cockroach_kernel/`,
`p4-verifier/`, `p7-recovery/`, `p9-cloud/`, `skills/`,
`live_lambda_handler.py`, `test_live_lambda_handler.py`, `examples/`, and
the approved public claim/submission documents.

## Competition alignment checked

The current official rules require a public/open-source repository with a
license and clear setup, an intended-device demonstration, a functional demo
path, meaningful CockroachDB and AWS integration, and free judge access. The
candidate satisfies the local judge-path portion; public export, video, and
submission remain separate gates.

Official rules: https://cockroachdb-ai.devpost.com/rules
