# CockroachDB × AWS Claims Manifest R2

This manifest defines the release claim ceiling. It is not a production-scale
attestation.

| Required tool/service | Release claim | Evidence boundary |
|---|---|---|
| CockroachDB Distributed Vector Indexing | Trajectory-linked vectors and transactional receipts share the CockroachDB memory layer. | Bounded schema, vector probes, and single-region readback. |
| CockroachDB Managed MCP Server | A read-only bounded receipt-view inspection is supported. | One declared query surface; no write, DDL, token-revocation, or recovery authority. |
| AWS Lambda | A bounded advisory worker can return an advisory result. | Synthetic/captured readback; local verifier remains authoritative. |

## Explicit non-claims

No MCP write/DDL/recovery authority, ccloud runtime control, Bedrock, Bedrock
Agents, SageMaker, ECS, EKS, S3, multi-region resilience, production-scale
durability, arbitrary undelete, or recovery of bytes with no surviving
representation is claimed.
