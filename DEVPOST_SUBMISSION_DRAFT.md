# Devpost submission draft

## One-line summary

Cockroach Kernel is a deterministic recovery layer that promotes only the
maximum progress provable from surviving, hash-bound agent state.

## What it does

When an agent workspace disappears, Cockroach Kernel evaluates surviving
representations—committed, uncommitted, and independently captured state—and
builds a fresh successor only when the evidence is valid. Tampered, conflicting,
malformed, unsupported, replayed, or unsafe inputs fail closed. A local
deterministic verifier is the sole authority; model and cloud outputs are
advisory evidence only.

## CockroachDB integration

- Distributed Vector Indexing stores trajectory-linked vectors beside
  transactional receipts so retrieval and operational state share one memory
  layer.
- The CockroachDB Managed MCP Server is used in read-only mode for a bounded
  receipt-view inspection. The MCP path has no write, DDL, or recovery authority.

## AWS integration

AWS Lambda runs a bounded advisory evaluation worker. The worker can return an
advisory result, but it cannot promote or refuse recovery. The local verifier
checks the hash-bound evidence and decides the outcome.

## Judge path

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/cockroach-kernel demo --explain --output-root /tmp/cockroach-kernel-demo
.venv/bin/cockroach-kernel inspect-memory --input examples/memory-snapshot.json
```

The demo is a deterministic, keyless local replay. It is labeled as such and is
not described as a live model call.

## Limitations

The evidence is bounded to a single region and synthetic/disposable workflows.
The system recovers surviving representations, not arbitrary deleted bytes from
nothing. It does not eliminate Git, backups, permissions, or review safeguards.
Multi-region resilience, independent-user validation, MCP write authority, and
unsupported AWS services are not claimed.
