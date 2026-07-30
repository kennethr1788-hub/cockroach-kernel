# EV3 Preflight R2 Egress Rejection Receipt

- UTC: `2026-07-30T12:37:43Z`
- packet SHA-256: `39978c2c0b51b46089979a9a39ac4d543fedd1e9c803323f20e7866f3072bbfc`
- route requested: exact `glm-5.2`, direct judge route, fallback disabled
- provider request executed: `FALSE`
- local route exit: `3`
- disposition: `REJECTED_BEFORE_PROVIDER_EXECUTION`
- reason: the outbound sanitizer rejected byte-complete source containing environment-access syntax and transcript-shaped data
- raw local stderr SHA-256: `3c91051c56e1915aa9e625ddf20375480f5ef13cf48a9bca264d2d2f4d4c2039`
- hidden seed existed: `FALSE`
- hidden invocations completed: `0`
- semantic protocol changed by the replacement packet: `FALSE`

R2 is preserved as failed preflight evidence. It carries no judge verdict and no
permission to generate a hidden seed. R3 removes source bodies from external
egress while retaining their hashes, measured receipts, thresholds, and
fail-closed boundaries.
