# S1 foundation soak

`run_soak.py` runs a bounded synthetic workload against one loopback-only
CockroachDB process. Each checkpoint exercises a forced serializable retry,
duplicate-receipt idempotency, rollback, restart recovery, five-repeat
deterministic verdicts, and quarantine exclusion. Canonical JSON receipts are
atomically written and fsynced. The runtime store is removed before closeout;
only evidence remains.

The driver refuses durations above 3,600 seconds and enforces separate database
and evidence growth thresholds. It does not call a model or any network service.
