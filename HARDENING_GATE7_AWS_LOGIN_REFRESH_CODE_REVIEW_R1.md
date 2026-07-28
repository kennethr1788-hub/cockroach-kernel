# Gate 7 AWS Login Refresh Code Review R1

## Exact source bindings

- `s3-soak/hardening.py`: `9f985eaa36a3ab50e3ebc9c12f088cd3c616ecad4e50a349658c437e45d53934`
- `s3-soak/cloud_adapter.py`: `e1a7a99c11744244312462a8127d1234bc0179b867f1d106c549feca7507a8ca`
- `s3-soak/host_coordinator.py`: `b4c258189c2619815c81fed52732071db49404e30350e2c37057b438d1234fb1`
- `s3-soak/test_hardening.py`: `b23e9b2550da9466d0136b8a7c30aca98c8c3b4226f96c65a2ef5992fbd96612`

These are host-side Gate 7 orchestration and tests. The frozen remote payload
contains only `s3-soak/protocol.py` and `s3-soak/worker.py`; neither changed.

## Receipt primitives

The new pending-window primitive rejects non-integer, past, undersized-margin,
and malformed-hash inputs. Its receipt declares that no future expiry is being
claimed and stays pending until the post-exchange provider probe exists.

The new postcheck primitive requires integer last-exchange/probe/margin/latency
values, a margin of at least 900 seconds, and two 64-character SHA-256 values.
It returns PASS only when the probe epoch is at or after the last exchange plus
the full margin. An early probe returns BLOCKED with a stable reason code.

## Coordinator state machine

The legacy fixed-expiration mode remains available. Live execution selects
exactly one mode: legacy fixed expiration or the explicit AWS-login automatic
refresh mode. Selecting both or neither fails before the coordinator starts.

In automatic-refresh mode the coordinator:

1. proves the login provider and installed refresh contract;
2. writes the pending session receipt;
3. executes the unchanged twelve-request loop with the unchanged Lambda and
   Cockroach operation ceilings;
4. records the wall-clock epoch immediately after each committed result;
5. after result twelve, waits until the final recorded epoch plus 900 seconds;
6. emits hash-chained heartbeats while waiting and continues enforcing the
   stop signal and absolute lifecycle deadline;
7. performs one sanitized read-only identity probe;
8. validates and fsyncs the final postcheck receipt;
9. emits a hash-chained margin-verified event; and
10. only then proceeds to the pre-existing completion-marker and GREEN path.

A failed provider proof, refresh, identity probe, time check, stop check, or
deadline check enters the existing coordinator BLOCKED path. It cannot be
averaged away or relabeled as product success.

## Tests

The complete `s3-soak` suite passed 17/17. The new test proves an 899-second
probe is BLOCKED and an exact 900-second probe is PASS. Existing tests continue
to cover sanitized external failures, expiry-mode rejection, sequence/order,
hash linkage, atomic evidence, coordinator completion waiting, bridge staging,
and exact local shutdown.
