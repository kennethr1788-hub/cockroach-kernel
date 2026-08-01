# PDH-3 R8 local repair smoke packet R7

Status: diagnostic-only local smoke contract.

Candidate commit: `c3bc014`

The bounded local campaign exercises the repaired three-node loopback path,
vector-index deferral/restoration, deterministic seed and verifier behavior,
one node kill/restart cycle, and complete disposable-root teardown. It uses
synthetic data, an isolated temporary HOME, disabled CockroachDB diagnostic
reporting, no credentials, and no external cloud calls.

The repair under test permits gateway recovery only inside the vector-index
proof path. A connection failure causes the exact three-node cluster to be
restored and verified before proof continues on a different ready gateway.
The repair must not issue duplicate index DDL after an uncertain server effect.
Blocked runs preserve bounded node log diagnostics before deleting the local
database stores.

This smoke is not RunPod evidence, target-scale evidence, 24-hour evidence,
multi-region evidence, or production traffic evidence. Its only authority is
to reject a broken replacement bundle before paid remote creation.
