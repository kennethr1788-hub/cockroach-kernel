# Cockroach Kernel

Cockroach Kernel is a deterministic developer-work recovery prototype. It can
promote exact bytes from a surviving, hash-bound representation into a declared
disposable successor workspace. The local verifier and typed records—not a
model—decide whether recovery is permitted.

It does **not** undelete arbitrary files, inspect storage blocks, or reconstruct
bytes that were never captured in an allowed representation.

## Install

The supported local path is Python 3.12:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/cockroach-kernel --help
```

Runtime behavior uses only the Python standard library. The optional AWS demo
dependency is not required for local recovery.

## Scenario-driven recovery

Create one disposable envelope outside HOME. Inside it, create five existing,
non-overlapping paths: a canonical request file, successor workspace,
representation root, custody root, and empty output root. Then run:

```bash
cockroach-kernel recover \
  --request /private/tmp/example/request.json \
  --sandbox-root /private/tmp/example \
  --workspace /private/tmp/example/workspace \
  --representation-root /private/tmp/example/representations \
  --custody-root /private/tmp/example/custody \
  --output-root /private/tmp/example/output
```

The canonical request has exactly these fields:

```json
{"candidates":[],"context":{"manifest":{},"policy_version":"policy-v1","quorum_decision_hash":"<sha256>","trajectory_receipt":{}},"loss_receipt":null,"request_id":"request-1","version":"ck-recovery-request-v1","warrant":null}
```

The embedded manifest, trajectory receipt, candidates, loss receipt, and
warrant use the strict P7 record contract. For candidate `candidate-1` and path
`src/feature.py`, its bytes must exist at:

```text
<representation-root>/candidate-1/src/feature.py
```

The representation must be a regular non-executable file whose SHA-256 matches
the candidate record. Missing representations are recorded as
`NO_PROVEN_REPRESENTATION`; their bytes are never invented.

Successful recovery writes canonical decision, receipt, unrecovered-ledger,
mutation-manifest, and summary records. A warrant is consumed in persistent,
locked custody before promotion and cannot be replayed in a fresh process.
Refusal, invalid input before consumption, and clean/no-loss controls do not
mutate the successor workspace.

## Other public commands

```bash
cockroach-kernel demo --explain
cockroach-kernel inspect <canonical-receipt.json>
```

`demo` is a clearly labeled deterministic keyless replay retained for
compatibility. `inspect` validates its canonical receipts. Neither substitutes
for the external-input `recover` command.

## Conflicting surviving evidence

When more than one sealed representation survives, the continuation brief can
carry a deterministic recovery decision. It returns `CONTINUE` only when the
hash-bound facts agree, `QUARANTINE` for tampered or conflicting duplicate
records, and `HUMAN_REVIEW_REQUIRED` when the evidence is incomplete or
contradictory. It never selects a winner or creates missing bytes; the P4
verifier remains the sole recovery authority.

## Safety boundary

- All roots must already exist beneath one disposable envelope outside HOME.
- Roots must be distinct and non-overlapping.
- Absolute record paths, traversal, backslashes, NUL, symlinks, executable
  files, unknown fields, noncanonical JSON, unsupported versions, and hash
  mismatches fail closed.
- The command uses no network, model, credentials, AWS, or CockroachDB service.
- Each record and represented file is capped at 64 KiB; aggregate represented
  bytes are capped at 1 MiB.

The full frozen contract is in `SCENARIO_SURFACE_R3_CONTRACT.md`.
