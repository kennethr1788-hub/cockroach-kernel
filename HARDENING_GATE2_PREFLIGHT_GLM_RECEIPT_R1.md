# Hardening Gate 2 Preflight GLM Receipt R1

- `UTC_REVIEWED`: `2026-07-27T16:57:52Z`
- `JUDGE_ROUTE`: `glm-zai`
- `SERVED_MODEL`: `glm-4.7`
- `JUDGE_ROLE`: `independent_non_authoring_public_demo_preflight`
- `TOOLS_OR_WRITE_AUTHORITY`: `none`
- `PACKET`: `HARDENING_GATE2_PUBLIC_DEMO_AUTHORIZATION_PACKET_R1.md`
- `PACKET_SHA256`: `4189d411ae296bcac93e1ef55bf1fe774dbb9d2c1c0debca1a198c3374d87ea7`
- `WRAPPER_SHA256`: `0b94755754de89557ffb9d00b45b8d8fef6578614d00563db2320e940f83748f`
- `EXIT_STATUS`: `0`

## Raw verdict

```json
{
  "verdict": "GREEN",
  "packet_sha256": "4189d411ae296bcac93e1ef55bf1fe774dbb9d2c1c0debca1a198c3374d87ea7",
  "blocking_findings": [],
  "nonblocking_findings": [
    "Denial-of-wallet protection relies on manual intervention (alarms) and best-effort API Gateway throttling rather than an automated, provider-enforced hard spend cap.",
    "CockroachDB cluster eligibility requires manual external verification because the free trial expires before the judging period ends."
  ],
  "reason": "The packet defines a narrow, read-only architecture with minimal attack surface (fixed routes, parameterized queries, no mutation authority). It accurately identifies and quantifies residual risks, specifically the lack of a hard automated spend cap and the soft nature of throttling, and explicitly requires human acknowledgment of these risks as a condition for deployment. Credential boundaries are strict (least privilege IAM and SQL roles), and the authorization text is precise and comprehensive."
}
```

This is a preflight verdict on the authorization packet, not a Gate 2 GREEN
verdict. Kenneth's human authorization, AWS login, cluster-access continuity,
live deployment evidence, teardown plan validation, and final independent
review remain open.
