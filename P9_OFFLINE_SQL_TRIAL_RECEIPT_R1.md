# P9 Offline SQL Trial Receipt R1

- UTC: `2026-07-26T13:48:46Z`
- PARENT_COMMIT: `4ce609eaa5fa7b74fcb65c8c84cc6083eb3b7886`
- COCKROACH_VERSION: `v26.2.3`
- COCKROACH_BINARY_SHA256: `9e6448bfb19c5811ea565020fc84bf7e1ed8fc0c8236ab8512a48e141018aa5c`
- DATA: synthetic only
- NETWORK: loopback only
- LIVE_CLUSTER: untouched

Trial 1 applied `001_cloud.sql` in a fresh project-local disposable root. It
created seven `ck` tables/views and one `context_vectors_vector_idx`. The test
database was dropped, the process stopped, and the generated root was deleted.

Trial 2 applied `001_cloud.sql`, created the synthetic local `ck_runtime`
identity outside the migration, then applied `002_runtime_grants.sql`.
`ck_runtime` successfully selected the empty `ck.mcp_receipt_view`; creating a
table failed with `does not have CREATE privilege on schema ck`; updating
`ck.tasks` failed with `does not have UPDATE privilege on relation tasks`.
The database and synthetic identity were dropped, the process stopped, and the
generated root was deleted.

Post-trial checks found no listener on either trial port, no matching database
process, and no `p9sql.*` or `p9grants.*` temporary root.

This receipt proves local v26.2.3 schema and grant behavior only. It does not
prove live CockroachDB Cloud, Managed MCP, AWS IAM, or Lambda behavior.
