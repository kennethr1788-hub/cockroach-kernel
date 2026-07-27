# Hardening Gate 2 CockroachDB Identity Receipt R1

- `UTC_CREATED`: `2026-07-27T17:50:41Z`
- `TARGET_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `SQL_USER`: `ck_hardening_demo`
- `CLUSTER`: `cockroach-kernel`
- `DATABASE`: `cockroach_kernel`
- `IDENTITY_CREATED`: `yes`
- `PASSWORD_RECORDED_OR_PRINTED`: `no`
- `PASSWORD_CLIPBOARD_STATE`: `temporary_pending_AWS_secret_handoff`
- `GRANT_EXECUTION_RESULT`: `Success`
- `AWS_SECRET_CREATED`: `no`

## Exact grants applied

```sql
GRANT USAGE ON SCHEMA ck TO ck_hardening_demo;
GRANT SELECT ON TABLE ck.tasks TO ck_hardening_demo;
GRANT SELECT ON TABLE ck.receipts TO ck_hardening_demo;
GRANT SELECT ON TABLE ck.context_vectors TO ck_hardening_demo;
GRANT SELECT ON TABLE ck.worker_results TO ck_hardening_demo;
```

No `INSERT`, `UPDATE`, `DELETE`, DDL, changefeed, MCP, admin, ownership, or
role-management grant was applied. CockroachDB Cloud showed one successful
execution for the five-statement grant batch. The provider-generated password
was copied without being read by the executor and remains only in the temporary
clipboard pending the hidden project-local AWS Secrets Manager handoff.

The provider-generated credential is 22 characters. The project-local secret
helper's prior 24-character minimum rejected the provider's own generated
format before submission. The helper was narrowed to accept provider-generated
credentials of at least 20 characters while retaining NUL and short-input
rejection. No credential bytes were added to source, logs, receipts, argv, or
tool output.
