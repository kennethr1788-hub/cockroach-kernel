# CockroachDB × AWS Claims Manifest

This is a claims-to-implementation map, not a score or a claim of production
scale.

| Claim | Evidence surface | Boundary |
|---|---|---|
| CockroachDB is authoritative persistent memory | `p9-cloud/migrations/001_cloud.sql`, live linked traces | Bounded single-region evidence |
| Distributed vector retrieval shares the transactional memory layer | `context_vectors_vector_idx`, live vector queries | Retrieval does not decide recovery |
| Managed MCP provides bounded inspection | Read-only linked MCP receipt | No write, DDL, or authority |
| Lambda provides bounded advisory evaluation | `p9-cloud/live_deployment_readback.json` | Lambda never emits the recovery verdict |
| Secrets Manager and IAM protect runtime access | Live readback and role template | Credential values are never published |
| CloudWatch provides operational evidence | Lambda log configuration and receipts | No unlimited durability claim |
| Read-only memory inspection skill detects linkage problems | `skills/cockroach-memory-inspection/SKILL.md` and `cockroach_kernel/memory_skill.py` | Advisory report only; no mutation |

Explicit non-claims: ccloud runtime control, Bedrock, Bedrock Agents,
SageMaker, ECS, EKS, S3, arbitrary undelete, production-scale durability, and
recovery of bytes that were never captured.
