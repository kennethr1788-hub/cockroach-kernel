# Gate 7 Run 5 Worker Preflight Judge Receipt R1

- `STATUS`: `GREEN`
- `UTC_CREATED`: `2026-07-29T21:30:52Z`
- `PACKET_SHA256`: `2b1af0712b00b373ae62b53365abc7268399bffc56f7196ba3c71801859cbe02`
- `PACKET_COMMIT`: `c710e822f773e86defa7d95bfbf605d9df325451`
- `GLM_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `AGY_MODEL`: `Gemini 3.1 Pro (High)`
- `AGY_VERDICT`: `GREEN`
- `SAME_HASH`: `YES`
- `RECUSAL_CHECK`: `clear`
- `AUTHORITY`: `ONE_BOUNDED_RUN5_WORKER_AFTER_ALL_CAMPAIGN_READY_CHECKS`

## Raw evidence

- GLM raw SHA-256:
  `fedecbe06701b47b3cbdbd743e741c7e51b65d2c4b7fe26a94ee3977d95e651b`;
- AGY raw SHA-256:
  `9d8aa8b2490cf4a2b79025a45caaf83696462fd00e43f00dcb265ce11399f516`.

GLM preserved one non-blocking risk: observed insert latency is variable and
the successful 305017 ms public canary relies on the independently approved
420000 ms ceiling. Actual Run 5 latency must remain reported and a mechanical
ceiling breach remains blocking.

This receipt authorizes no hidden seed until the worker also passes exact
identity, image, price, storage, transfer-hash, extracted-smoke, unprivileged,
lifecycle-guard, AWS, and CockroachDB readiness checks.
