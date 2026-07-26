# P6 R2 Judge Results

- `PACKET_SHA256`: `95997a598ef78ed171e3e24179bb1acd0d02ce53c58e8b7a5bbec333b07782d7`
- `GLM_ROUTE_PROOF`: wrapper stderr reported served model `glm-5.2`
- `GLM_CONTENT_VERDICT`: `GREEN`
- `GLM_RESULT`: invalid because the response self-labeled `MODEL: Claude
  3.5 Sonnet`, contradicting the verified wrapper-served identity
- `CLAUDE_ROUTE_PROOF`: wrapper reported served model `claude-opus-4-8`
- `CLAUDE_VERDICT`: `GREEN`
- `R2_GATE`: `NOT_GREEN`

The GLM result is rejected as a route-identity mismatch even though its content
verdict was GREEN. The R2 Claude verdict does not carry to R3.

Claude's non-blocking observations are preserved: the commit layer trusts a
hash-consistent decision produced by the authoritative pure function rather
than re-deriving quorum; correlation is exact-hash-only; the database abort
uses a constraint failure rather than a literal process crash; and retry proof
is idempotent transaction re-execution rather than an injected SQLSTATE 40001
conflict. These are disclosed boundaries, not hidden claims.
