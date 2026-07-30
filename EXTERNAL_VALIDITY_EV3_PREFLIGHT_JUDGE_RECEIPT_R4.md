# EV3 Cross-Model Preflight Judge Receipt R4

- UTC closed: `2026-07-30T12:44:22Z`
- packet: `EXTERNAL_VALIDITY_EV3_PREFLIGHT_PACKET_R4.md`
- packet SHA-256: `274664240c61671eb604796d4bda0150ea40d9245b9abc65cb59534143025237`
- hidden seed existed during both reviews: `FALSE`
- hidden invocations completed during both reviews: `0`
- builder self-approval: `FALSE`

## GLM 5.2

- exact served model: `glm-5.2`
- fallback: `DISABLED`
- exit: `0`
- raw stdout SHA-256: `8f42f78ed9de9717a9da0092931238b89f4f305d92ba7aaab00d4463329c1ba3`
- raw stderr SHA-256: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`
- verdict: `GREEN`
- hash match: `TRUE`
- recusal: `CLEAR`
- blockers: `NONE`

## AGY

- bound model route: `Gemini 3.1 Pro (High)`
- wrapper: contained judge-only route
- exit: `0`
- raw stdout SHA-256: `4c8942650f1c82ea22ee751a977e43d2a693ce28b7cabdd00b719bb656260125`
- raw stderr SHA-256: `bf32ab8c082fa1aff618ee172c412b767bf7f636479cf49543749f2ba6ad30ee`
- verdict: `GREEN`
- hash match: `TRUE`
- recusal: `CLEAR`
- blockers: `NONE`
- residual: response-level served-model metadata is unavailable in CLI 1.1.8;
  the contained wrapper bound authenticated inventory, exact backend override,
  and provider response instead

Both independent judges reviewed the same immutable packet hash. Neither judge
authored the product, actor harness, scenario matrix, scorer, or packet.
