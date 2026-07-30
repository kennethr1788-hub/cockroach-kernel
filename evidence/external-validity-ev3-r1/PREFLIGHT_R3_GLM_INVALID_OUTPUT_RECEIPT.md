# EV3 Preflight R3 GLM Invalid-Output Receipt

- UTC closed: `2026-07-30T12:42:02Z`
- packet SHA-256: `a3f4c0ffed5323eca2d2c5238c99c93934c8fa0d8aafcf7740c4338f94a862cc`
- exact served model: `glm-5.2`
- provider calls: `3`
- valid verdicts: `0`
- hidden seed existed: `FALSE`
- hidden invocations completed: `0`

Attempt outcomes:

1. The default 4,096-token bound returned HTTP 200 with empty content and
   `finish_reason=length`. Stderr SHA-256:
   `fe590c1b1c98947e0c4331ea877ef623c98a631974c0775f7ac9031d03b816b1`.
2. An 8,192-token retry returned a complete procedural BLOCKED response because
   the packet hash was not present in the prompt. Raw output SHA-256:
   `b750560bc4c35d6aa841b94d7741e544a53b52c79d72a9bad9d8e3288694c3c0`.
3. The trusted-envelope retry supplied the exact packet hash but returned only
   the bare token `BLOCKED`, contrary to the required five-field schema. Raw
   output SHA-256:
   `57ae2fe82645cb38f3b828263b6ee49a867e4d57a08fcc77c2306594981188d2`.

R3 carries no valid judgment and no authority to create the hidden seed. R4
removes the contradictory bare-verdict instruction while preserving all
campaign semantics, evidence thresholds, actor bindings, and product hashes.
