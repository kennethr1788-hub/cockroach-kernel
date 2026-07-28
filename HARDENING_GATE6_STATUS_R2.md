# Hardening Gate 6 Status R2

- `STATUS`: `HARDENING_6_RUN1_BLOCKED`
- `EXECUTION_REVISION`: `R2`
- `BLOCKER`: `UNPRIVILEGED_NETWORK_NAMESPACE_UNAVAILABLE`
- `LAST_GREEN_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_R2_GREEN`
- `CANDIDATE_COMMIT`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `ORCHESTRATION_BASE_COMMIT`: `cede131c59097b615b0f6c02926b35b77505b65f`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `PREFLIGHT_PACKET_SHA256`: `f1df04300bd4d865d2c0d2b87bc8c5f607a98f23e7c45d377edc84c31a04346d`
- `PREFLIGHT_JUDGES`: `GLM 5.2 GREEN; CLAUDE OPUS 4.8 GREEN; RECUSAL CLEAR`
- `FINAL_PACKET_SHA256`: `6f3b1d8a3c10244d88feb99a8a39c9ce13ae836abf9c0117617d7adfcac12ede`
- `FINAL_JUDGES`: `GLM 5.2 BLOCKED CONFIRMED; CLAUDE OPUS 4.8 BLOCKED CONFIRMED; RECUSAL CLEAR`
- `MEASURED_EXECUTIONS_COMPLETED`: `0`
- `RUNPOD_ATTEMPTS`: `1`
- `POD_IDS`: `2sh4lx37f6r73g`
- `COST_STATE`: `BILLING_PENDING_BOUNDED_MAX_$0.0060`
- `RUNPOD_RUNNING_INVENTORY`: `[]`
- `UTC_RECORDED`: `2026-07-28T00:58:13Z`

The returned worker matched every reviewed provider property. Payload transfer,
tree verification, offline Git installation, and the exact Python, Git, Restic,
and product-verifier version/hash wall passed. The required host-unprivileged
network namespace then failed before smoke or measurement:

```text
unshare: unshare failed: Operation not permitted
```

The prompt explicitly classifies inability to create the reviewed unprivileged
network namespace as an isolation/capability failure. No alternate isolation,
root execution, in-process socket guard, host firewall change, replacement Pod,
smoke row, or measured row was used. The worker was stopped and deleted; exact
ID absence, empty campaign inventory, the guard teardown chain, and absence of
remaining local campaign processes all passed.

Gate 6 remains blocked. Gate 7 is forbidden.
