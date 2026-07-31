# PDH-3 R8 Validation Boundary Disclosure

During a read-only exploratory vector-index probe on 2026-07-31, a validation
lane briefly invoked `cockroach demo` without first supplying the isolated HOME
used by the campaign harness. The process was immediately terminated. That CLI
surface may have refreshed metadata under `~/.cockroach-demo` and may have
attempted CockroachDB diagnostic telemetry; neither absence claim is made.

The subsequent diagnostic node used only loopback ports `29123` and `29124`,
explicitly disabled diagnostic reporting, was stopped, and both ports were
verified closed. No RunPod worker was created and no provider campaign ran.

This exploratory action is excluded from clean R8 candidate evidence. The final
local smoke and extracted-bundle validations must use fresh generated roots, an
explicit isolated HOME, diagnostics disabled, and separately preserved residue
and listener checks. The disclosure may not be deleted, rewritten as zero HOME
mutation, or represented as zero-egress evidence.
