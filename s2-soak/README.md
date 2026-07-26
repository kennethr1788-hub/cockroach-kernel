# S2 Orchestration and Recovery Soak

This synthetic-only harness combines the P5 advisory lanes, P6 deterministic
quorum and handoffs, P4 quarantine, and P7 declared-loss recovery contract
against a disposable loopback CockroachDB node.

Production mode rejects schedule drift and requires exactly:

- 21,600 seconds of actual execution;
- 72 checkpoint probes at 300-second cadence;
- 24 full safety replays at 900-second cadence;
- six hourly summaries at 3,600-second cadence.

The runtime emits separate hash-chained streams, exercises actual declared
loss inside a generated root, consumes recovery warrants before reconstructing
exact surviving bytes, proves replay and interrupted recovery fail closed, and
removes the database and every generated recovery root on exit.

No model client, cloud credential, HOME state, private data, live memory, AWS,
Qdrant, StateV2, or public surface is part of the payload.
