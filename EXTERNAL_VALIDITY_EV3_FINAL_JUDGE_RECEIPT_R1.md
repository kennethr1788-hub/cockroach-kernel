# EV3 Final Cross-Model Judge Receipt R1

- UTC closed: `2026-07-30T12:51:07Z`
- final packet SHA-256: `f6288d648a01035f43a696ae21157bee38e03d2bdf0ace33265d20c3f8b035e0`
- product candidate: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- campaign: `ev3-3e165324fce8`
- completed hidden executions: `24`
- builder self-approval: `FALSE`

## GLM 5.2

- exact served model: `glm-5.2`
- fallback: `DISABLED`
- exit: `0`
- verdict: `GREEN`
- hash match: `TRUE`
- recusal: `CLEAR`
- blockers: `NONE`
- raw stdout SHA-256: `b04407dd7d46d77f78aa9422e8f6c23f4309e8049da3fa5f0e4eb46d15f13c45`
- raw stderr SHA-256: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`

## AGY

- bound model route: `Gemini 3.1 Pro (High)`
- wrapper: contained judge-only route
- exit: `0`
- verdict: `GREEN`
- hash match: `TRUE`
- recusal: `CLEAR`
- blockers: `NONE`
- evidence gaps: `NONE`
- required reruns: `NONE`
- raw stdout SHA-256: `e44c52a892368d601e4e8d4eafbe4eb1b1024eefd51142354af6bca3ebfb30af`
- raw stderr SHA-256: `bf32ab8c082fa1aff618ee172c412b767bf7f636479cf49543749f2ba6ad30ee`
- residual: response-level served-model metadata is unavailable in CLI 1.1.8;
  authenticated inventory, exact backend override, and provider response were
  bound by the contained wrapper

Both independent judges reviewed the same immutable final packet hash. Neither
judge authored the product, protocol, hidden inputs, scorer, evidence, or
packet.
