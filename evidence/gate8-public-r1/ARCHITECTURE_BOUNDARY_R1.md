# Gate 8 Architecture and Authority Boundaries R1

```mermaid
flowchart LR
    D["Developer and coding agent"] --> C["Capture CLI<br/>declared work and intent"]
    C --> K["CockroachDB memory layer<br/>tasks, trajectory events, receipts,<br/>vectors, results, projections"]
    C --> L["AWS Lambda<br/>bounded advisory evaluation"]
    L --> V["Schema and hash validation"]
    K --> V
    M["Managed MCP<br/>read-only inspection and audit"] -.-> K
    F["Advisory model fan-out<br/>proposals only; no filesystem authority"] --> V
    V --> A["Deterministic local authority<br/>PROMOTE, REFUSE, or INVALID"]
    A --> S["Fresh-process successor<br/>one-use, receipt-bound materialization"]
    A --> R["Canonical refusal and evidence receipts"]
```

## Load-bearing boundaries

- CockroachDB is persistent memory, not verdict authority.
- AWS Lambda and model output are untrusted advisory inputs. Both are
  schema-validated and hash-bound before deterministic evaluation.
- Managed MCP is read-only and cannot mutate memory, recover files, or decide
  pass/fail.
- The deterministic local verifier is the sole promotion/refusal authority.
- Filesystem actions are scoped to declared disposable roots. Absolute paths,
  traversal, unsupported state, tampering, and warrant replay fail closed.
- A successor contains only captured, declared representations that passed the
  frozen policy. Arbitrary uncaptured bytes cannot be recovered from nothing.
