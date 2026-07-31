# PDH-3 Scale Controller Local Smoke Packet R1

## Purpose

Exercise the same three-node cluster, schema, synthetic seeding, query,
verifier, fault, dependency-state, cleanup, evidence, and teardown code paths
used by production mode at a deliberately reduced local scale. This packet
authorizes no paid resource and creates no scale claim.

## Bindings

- Product candidate:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- Plan SHA-256:
  `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- Contract source SHA-256:
  `244caca40024bb2bfa1bd6909c1562f31efa1401e179ab99aa923c86bfda0cee`
- Controller source SHA-256:
  `de4fd0cba5ac07bb13867fef1b740d77817abf26918b0f0e2e391cfee488e94e`
- CockroachDB:
  v26.2.3 Darwin arm64, previously checksum-verified in P2.

## Reduced workload

- 60 measured seconds;
- one 60-second checkpoint;
- 100 tasks;
- three trajectory events per task;
- one receipt per task;
- 50 vectors;
- concurrency 10;
- one three-node crash/restart cycle;
- one 43-execution verifier batch;
- five synthetic dependency-advice states;
- one concurrent cleanup probe.

## GREEN

- all exact counts agree;
- query and histogram accounting agree;
- verifier batch is GREEN;
- dependency-state and cleanup probes pass;
- one node survives SIGKILL/restart with no dataset drift;
- zero cross-task vectors;
- no credential or external cloud call;
- all nodes, ports, and generated roots are removed.

The production packet must be reconstructed from the final tested source
hashes. This local packet cannot authorize a RunPod worker.
