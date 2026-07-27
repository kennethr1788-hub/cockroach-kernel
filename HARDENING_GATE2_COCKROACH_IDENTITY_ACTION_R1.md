# Hardening Gate 2 CockroachDB Identity Action R1

- `STATUS`: `HUMAN_ACTION_REQUIRED`
- `BLOCKER`: `COCKROACH_DEDICATED_READ_ONLY_IDENTITY_REQUIRED`
- `LAST_GREEN_GATE`: `HARDENING_1_CLI_GREEN`
- `BLOCKED_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `UTC_RECORDED`: `2026-07-27T17:39:41Z`

The stored `ck_runtime` project credential now fails SQL authentication. That
identity is also intentionally broader than the public demo's read-only
contract and must not be reused or silently repaired for the public endpoint.

Kenneth must use the authenticated CockroachDB Cloud console to create exactly
one SQL user named:

```text
ck_hardening_demo
```

Generate and retain its password without pasting it into chat. In the
CockroachDB SQL console, apply exactly:

```sql
GRANT USAGE ON SCHEMA ck TO ck_hardening_demo;
GRANT SELECT ON TABLE ck.tasks TO ck_hardening_demo;
GRANT SELECT ON TABLE ck.receipts TO ck_hardening_demo;
GRANT SELECT ON TABLE ck.context_vectors TO ck_hardening_demo;
GRANT SELECT ON TABLE ck.worker_results TO ck_hardening_demo;
```

Do not grant `INSERT`, `UPDATE`, `DELETE`, `DDL`, `CHANGEFEED`, `MCP`, admin,
ownership, or role-management authority.

After the grants succeed, run the project-local credential handoff:

```bash
cd /Users/kennethruedas/sandbox/cockroach-kernel-build-20260725
python3.12 hardening-gate2/create_secret.py
```

Enter the generated password only at the hidden prompt. The script sends the
fixed five-field secret directly to AWS Secrets Manager through stdin and does
not write or print it. Reply only:

```text
Gate 2 read-only SQL user and secret complete
```

If CockroachDB asks for MFA, CAPTCHA, payment, terms, plan/resource-limit
changes, or any broader permission, stop and report the screen without sharing
credential material.
