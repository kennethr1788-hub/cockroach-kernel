# PDH-3 Vector Ingest Repair R8

## Classification

- `STATUS`: `LOCAL_REPAIR_GREEN_REMOTE_PREFLIGHT_PENDING`
- `PARENT_COMMIT`: `25f0876a30953f125fe722089c6d94ef8352e8f4`
- `R7_TERMINAL_STATE`: `BLOCKED_COMPLETE`
- `R7_BLOCKER`: `SETUP_DEADLINE_RESERVE_EXHAUSTED:reserve_seconds=2400`
- `R7_MEASURED_CLOCK_STARTED`: `false`
- `R7_WORKER`: `81y4t6r6t9zmpz` (deleted; campaign inventory empty)

## Verified failure mechanism

R7 completed all relational seed targets but inserted only approximately
43,250 of 250,000 vector rows before the reserved setup tail was reached. The
controller maintained the vector index while executing 250-row vector insert
statements. Every synthetic vector had the same value. Observed throughput was
approximately 7.056 vectors/second and deteriorated materially as the index
grew.

CockroachDB's current vector-index documentation says that large batched
`VECTOR` inserts can degrade performance and should be avoided. It also says a
larger maximum partition size improves write throughput by reducing partition
splits and merges. The official example uses four persistent clients, one row
and one transaction per execute.

Primary references:

- https://www.cockroachlabs.com/docs/stable/vector-indexes
- https://vector-examples.s3.us-east-2.amazonaws.com/fast_insert.py

## Minimal repair

1. Replace 250-row vector statements with four persistent `pg8000` clients,
   each executing one parameterized row per transaction.
2. Replace the degenerate identical-vector generator with a deterministic
   three-coordinate base-101 projection. It yields more than one million
   possible distinct points while retaining exactly 64 dimensions and fully
   synthetic, reproducible inputs.
3. Retain `ON CONFLICT (vector_id) DO NOTHING` only for uncertain/retry-safe
   insertion. A full-cardinality comparison independently checks task, event,
   namespace, vector value, and digest, so an existing mismatched row cannot be
   concealed as success.
4. Keep the vector index present during seed and set
   `max_partition_size=4096`, within CockroachDB's documented range. No
   post-load index backfill is introduced.
5. Vendor the already-declared pure-Python PostgreSQL client and exact pinned
   transitive dependencies in the credential-free transfer bundle.

## Dependency custody

| Artifact | SHA-256 | License |
|---|---|---|
| `pg8000-1.31.5-py3-none-any.whl` | `0af2c1926b153307639868d2ee5cef6cd3a7d07448e12736989b10e1d491e201` | BSD-3-Clause |
| `scramp-1.4.15-py3-none-any.whl` | `9d6102948d9005e3802384a328429dfd67d691a65791007c354ff89895857396` | MIT-0 |
| `asn1crypto-1.5.1-py2.py3-none-any.whl` | `db4e40728b728508912cbb3d44f19ce188f218e9eba635821bb4b68564f8fd67` | MIT |
| `python_dateutil-2.9.0.post0-py2.py3-none-any.whl` | `a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427` | Apache-2.0/BSD-3-Clause |
| `six-1.17.0-py2.py3-none-any.whl` | `4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274` | MIT |

## Verification

- Campaign unit tests: `42/42` GREEN.
- Bundle-builder tests: GREEN.
- Supervisor, contract, local-canary, traced-wrapper, Gate-7, and verifier
  suites: GREEN.
- Pure-Python client imports directly from the five vendored wheels: GREEN.
- Real disposable single-node CockroachDB v26.2.3 vector smoke:
  - vectors: `5,000/5,000`;
  - workers: `4`, exactly `1,250` rows each;
  - elapsed: `30.256146582774818` seconds;
  - exact SQLSTATE `40001` retries: `4`;
  - content mismatches: `0`;
  - forced-index returned/distinct rows: `5,000/5,000`;
  - index proof: GREEN;
  - generated root: removed;
  - database process: absent.

The earlier three-node local campaign smoke did not reach the vector path: its
`cockroach init` timed out under the host's constrained free-disk condition.
It emitted a failure receipt and GREEN teardown. It is not counted as repair
evidence.

## Remote pre-measurement gate

Before the 24-hour measured clock begins, the replacement worker must execute
a material-scale extracted-bundle vector setup canary on the same worker image
and topology. It must prove:

- four persistent single-row clients;
- distributed deterministic vectors;
- full content reconciliation;
- forced-index coverage;
- cluster health and teardown;
- an observed completion-rate projection sufficient for 250,000 vectors
  inside the frozen setup window with its reserved tail.

Failure of that canary prohibits starting the 24-hour measured workload.
