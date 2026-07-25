# P3 durable ledger

`migrations/001_ledger.sql` is the authoritative CockroachDB schema. `ledger.py`
contains the canonical serializer, hash functions, strict record validation,
deterministic verdict function, trajectory hash, and evidence-budget record.

The runtime has no network or model dependency. CockroachDB is used only from
the project-local v26.2.3 binary during the integration harness.
