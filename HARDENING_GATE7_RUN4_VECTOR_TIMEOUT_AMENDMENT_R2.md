# Gate 7 Run 4 Vector Timeout Amendment R2

- `STATUS`: `LOCALLY_GREEN_LIVE_CANARY_REQUIRED`
- `UTC_CREATED`: `2026-07-29T05:15:39Z`
- `PARENT_CANARY`: `PUBLIC_CANARY_R1_BLOCKED`
- `RUNPOD_CREATION`: `FORBIDDEN`
- `HIDDEN_SEED`: `ABSENT`

## Amendment

The public R1 canary showed that a valid live vector batch can remain in the
CockroachDB command for more than 120 seconds under serialization pressure.
The repair does not reduce workload size, concurrency, target counts, or
adversarial coverage:

- normal SQL batch timeout remains 120 seconds;
- vector SQL batch timeout is bounded at 300 seconds;
- SQLSTATE `40001` retries remain limited to three;
- retries now use deterministic bounded backoff of 250, 500, and 750 ms;
- cleanup retries use the same bounded backoff;
- timeout exceptions still fail closed and are never retried as if an insert
  were known not to have committed.

## Local verification

- Entire Gate 7 suite: `21/21 PASS` in `35.825s`.
- The retry test proves the vector path receives a 300-second timeout and the
  first serialization retry waits exactly 250 ms.
- Non-retryable SQLSTATE `23505` still fails closed.
- Source SHA-256: `c36fc53d3c999e80aa85b6b74d161bad2217a7e2b9bd2c2afbe7286d75b15150`.
- Test SHA-256: `3b744954d07ca9cc681a260bd818975c5e90938086532e92c5aea01061c8ecec`.

## Next gate

Run one fresh public/non-hidden full 46,000-row canary under a new campaign ID.
It must emit canonical GREEN, exact counts, all 35 cleanup passes, and residue
`[0,0,0,0]`. The failed R1 evidence remains immutable.
