# S3 Preflight Judge Receipt R8

- `PACKET`: `S3_PREFLIGHT_PACKET_R8.md`
- `PACKET_SHA256`: `318f5fcadf4d30df11261ede0beb2b816fe7ba0b688b3a6e550b621bb175246a`
- `PACKET_BYTES`: `261607`
- `GLM_ROUTE`: `direct glm-zai`
- `GLM_SERVED_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RAW_OUTPUT_SHA256`: `033ba2c815b134c227c18dcff2901c0ee7d318bda565e783275c9b5893dedb4a`
- `CLAUDE_ROUTE`: `claude-judge`
- `CLAUDE_SERVED_MODEL`: `claude-opus-4-8`
- `CLAUDE_VERDICT`: `GREEN`
- `CLAUDE_RAW_OUTPUT_SHA256`: `4714e450afd6a6907657d9605c6987752a40606a6ed38536a330e1b51474578e`
- `CLAUDE_RECUSAL_CHECK`: `clear`
- `GATE`: `S3_PREFLIGHT_R8_GREEN`
- `UTC_RECORDED`: `2026-07-27T01:23:06Z`

Both judges evaluated the exact frozen R8 packet hash and returned GREEN with
no blockers. The GLM output's final paragraph incorrectly says "Claude leg."
That sentence is preserved verbatim but rejected as a role label: direct route
telemetry independently proves the served model was `glm-5.2`, and the output
counts only as the GLM leg. The separately pinned wrapper proves the Claude leg
was served by exact `claude-opus-4-8`. Neither judge output directed a repair.

This receipt authorizes only the next pre-start attempt inside the unchanged
retry, rate, cost, worker-shape, deadline, credential, and teardown envelope.
It does not establish campaign-ready or production GREEN.
