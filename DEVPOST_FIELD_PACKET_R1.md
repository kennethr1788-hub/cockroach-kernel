# Devpost field packet R1

Status: `DRAFT_READY_VIDEO_AND_DEMO_URL_PENDING`

This packet is prepared for the submission form. It is not a submission
receipt, and it must not be submitted until the video and functional demo URL
are filled and cross-checked.

## Project fields

- Title: `Cockroach Kernel`
- One-line summary: `A deterministic recovery layer that promotes only the maximum progress provable from surviving, hash-bound agent state.`
- Repository (private candidate branch):
  `https://github.com/kennethr1788-hub/cockroach-kernel/tree/public-release-candidate-20260810`
- Final public repository URL: `PENDING_PUBLIC_VISIBILITY_GATE`
- Functional demo URL: `PENDING_FUNCTIONAL_DEMO_URL`
- Video URL: `PENDING_VIDEO_URL`

## Required tool disclosures

CockroachDB tools:

1. Distributed Vector Indexing for receipt-linked trajectory retrieval beside
   transactional records.
2. Managed MCP Server in read-only mode for a bounded receipt-view inspection.

AWS service:

- AWS Lambda as a bounded advisory worker. The local deterministic verifier is
  the sole recovery authority.

## Testing instructions

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/cockroach-kernel --help
.venv/bin/cockroach-kernel demo --explain --output-root /tmp/cockroach-kernel-demo
.venv/bin/cockroach-kernel inspect-memory --input examples/memory-snapshot.json
```

No credentials or paid services are required for this local test path. The
demo is explicitly labeled `KEYLESS_LOCAL_REPLAY`; it is not a live model call
or arbitrary undelete mechanism.

## Claims guard

Do not claim MCP write/DDL/recovery authority, Bedrock, Bedrock Agents,
SageMaker, ECS, EKS, S3, multi-region resilience, production-scale
durability, arbitrary deleted-byte recovery, or recovery without a surviving
representation. See `COCKROACH_AWS_CLAIMS_R2.md`.
