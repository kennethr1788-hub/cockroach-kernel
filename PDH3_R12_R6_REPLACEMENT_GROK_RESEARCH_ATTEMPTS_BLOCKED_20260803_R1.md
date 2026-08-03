# PDH-3 R12 Replacement Grok Research Attempts — Blocked

- `STATUS`: `GROK_RESEARCH_ROUTE_UNAVAILABLE`
- `UTC_RECORDED`: `2026-08-03T07:25:21Z`
- `QUALIFIED_WRAPPER`: `/Users/kennethruedas/.local/bin/grok-research-safe`
- `WRAPPER_SHA256`: `b8eb2d0e560895177317fbfaaa78fc00ac4d974c94eed02791a0eb87e247c4cb`
- `OUTPUT_ACCEPTED`: `false`
- `AUTHORITY_GRANTED`: `none`

## Attempts

1. The first sanitized public-research query had SHA-256 `49d0412d2fcf68e0e91cb77b4311b50316f434bfa5e27d3b180ae918a1a673f4`. The qualified wrapper returned exit `78`: `GROK_RESEARCH_BLOCKED: model result was cancelled, malformed, or served by an unapproved model`.
2. The shorter sanitized query had SHA-256 `ef186ce1df0c9b619860e3d7ccf3cc5121216bed60ead44a2b789005bcd63b68`. The same qualified wrapper returned the same exit `78` classification.
3. One minimal public wrapper smoke returned the same exit `78` classification. Its transient prompt was not persisted and therefore is not hash-bound evidence.

No unqualified Grok route was used. No project path, source file, credential, provider state, private data, or deployment authority was sent. No Grok output was accepted as research or evidence.

The prior operator-supplied Grok sixteen-agent report remains disclosed context. It identified target-scale plan confirmation, batched/idempotent writes, continuous observability, bounded timeouts, and a canary ladder as necessary. The current replacement decision was independently derived from the retrieved failed-attempt artifacts and current official CockroachDB documentation because the fresh qualified Grok route was unavailable.
