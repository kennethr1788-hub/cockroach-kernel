# S3 Preflight Judge Attempt Log R3

- `PACKET_SHA256`: `098cf186e1e8da56f1e6731f21e09e2833c3b7eea4c3df0cd88e4d18fb2cb2c9`
- `PACKET_COMMIT`: `08807f3baa49d6d98f56acd0c8ab5ecdd6172139`
- `PACKET_TAG`: `ck-s3-preflight-packet-r3`
- `RUNPOD_ATTEMPTS_BEFORE_JUDGMENT`: `0`

## GLM 5.2

1. Exact-model attempt one failed closed after the provider returned HTTP 200
   with empty content and `finish_reason=length` at 16,384 output tokens.
2. Exact-model attempt two returned a substantively GREEN response but labeled
   its role `CLAUDE_JUDGE`; the schema/identity contradiction invalidated it.
3. Exact-model attempt three returned valid compact JSON with role
   `GLM_5_2_JUDGE`, the exact packet hash, verdict `GREEN`, no blockers, and
   recusal `CLEAR`. The wrapper reported served model `glm-5.2`.

No GLM fallback model was used. Invalid attempts do not count toward the gate.

## Claude Opus 4.8

The pinned `claude-judge` wrapper returned valid structured JSON on its first R3
attempt with exact served model `claude-opus-4-8`, the exact packet hash,
verdict `GREEN`, no blockers, and recusal `clear`.

The packet was not changed between the two valid judge results. The preflight
judge gate is GREEN; production evidence gaps remain open by design.
