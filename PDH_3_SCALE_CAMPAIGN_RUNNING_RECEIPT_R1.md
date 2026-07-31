# PDH-3 Production-Shaped Scale Campaign Running Receipt R1

- `STATUS`: `RUNNING_NOT_GREEN`
- `UTC_CAPTURED`: `2026-07-31T04:49:32Z`
- `PRODUCT_CANDIDATE`:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `ORCHESTRATION_COMMIT`:
  `9102ebe2add2e106477b4d5d45c71b30fc0372b8`
- `PACKET_SHA256`:
  `f5dd2ee116960f6383facf91228ee0b8b81718d6341607f9f427211cbcc38b0b`
- `POD_ID`: `gk32ovieth095v`
- `POD_NAME`: `ck-pdh3-scale-r1-a07`
- `PROVIDER_SHAPE`: `Secure Cloud / 1x L40S / 16 vCPU / 188 GB RAM`
- `COMPUTE_RATE`: `$0.99/hour`
- `CONTAINER_DISK`: `250 GB disposable`
- `PERSISTENT_OR_NETWORK_VOLUME`: `NONE`
- `PROVIDER_STOP_AFTER`: `2026-08-01T07:45:00Z`
- `PROVIDER_TERMINATE_AFTER`: `2026-08-01T08:00:00Z`
- `PRODUCTION_WRAPPER_PID`: `1377`
- `PRODUCTION_START_OBSERVED_UTC`: `2026-07-31T04:46:53Z`
- `FIRST_SEED_BATCH_UTC`: `2026-07-31T04:47:23Z`
- `MEASURED_24_HOUR_START`: `PENDING_AFTER_SETUP`

## Canary evidence

- hash-verified R7 bundle and packet upload: `GREEN`;
- extracted bundle manifest: `GREEN`;
- exact vendored tracer binary: `GREEN`;
- real loopback/connect/destinationless-send wrapper canary: `GREEN`;
- three-node 60-second controller canary: `GREEN`;
- verifier executions: `43`;
- fault cycles: `1`;
- maximum p99: `130.0 ms`;
- maximum latency: `142.6 ms`;
- traced controller-canary calls: `537`;
- external or unparseable destinations: `0`;
- controller result SHA-256:
  `4ebe93a9664f89b5f3113871e7e40e76409fad7c78dfb3d9cf5d74844c981385`;
- controller teardown receipt SHA-256:
  `4967db0255ee254d9e568bd3cdfe29bbdee936650bbec9346caae449784fb28d`;
- controller trace receipt SHA-256:
  `4ff525f3b67e72503b69a992aedcebaf5a644dd43401d87ebb4545474b68bd35`.

## Local custody

Two detached, caffeinated processes are active:

1. the hash-pinned exact-ID lifecycle guard, which provides bounded provider
   stop/delete retries and verifies exact-ID absence;
2. a retrieval supervisor, which polls every five minutes, packages and
   downloads final evidence, verifies its SHA-256, and deletes only Pod
   `gk32ovieth095v` after completion.

The provider-native stop and termination deadlines remain independent
fallbacks. This running receipt is not a final campaign result and cannot be
used to mark `PDH_3_PRODUCTION_SHAPED_SCALE_GREEN`.

## Local raw artifact bindings

- create response:
  `17d8e0fe0c3682dd9ade281569039900c4ddf0918bf3e08011da62cdd02aa93a`
- provider detail:
  `9c06312e4a7e857ab2b84f8e435ae97f54338cb62cd22ea911a880552bc33873`
- readiness:
  `46deceaf2302af8db7146f21c76120019dfb90558c83f8f5a2d87648b51f4097`
- upload/extract/trace canary:
  `b56ea5a0a6f7cf4b7ae252e2f7a1d53f2b3951837c407ae4bcffd3183973266b`
- controller canary debug:
  `c9eb849a0d02aa6023215f105f1c24ee020ea0f72132ce887fd7acebc2b86144`
- production start:
  `020e3866a264d18536cc66f9b9d930fdcc55555a21b12791f228579a415f177f`
- early health:
  `bb237cb3abb58d1f0942d480cae5a804975c40373016cc0ed584b67dfb7eed07`

No AWS login, CockroachDB Cloud login, account credential, private data, HOME
runtime, Qdrant, StateV2, launchd, client data, or production data is used by
the measured campaign.
