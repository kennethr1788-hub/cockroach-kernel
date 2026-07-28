# Hardening Gate 6 — Same-Hash Preflight Judge Receipt R4

- `STATUS`: `GATE6_R2_RUNPOD_PREFLIGHT_GREEN`
- `PACKET_SHA256`: `f1df04300bd4d865d2c0d2b87bc8c5f607a98f23e7c45d377edc84c31a04346d`
- `GLM_MODEL`: `glm-5.2`
- `GLM_VERDICT`: `GREEN`
- `GLM_RECUSAL`: `CLEAR`
- `GLM_RAW_SHA256`: `ce0824bd2cc86fbbac9efbe98c5d7033600574e29103ed934cfaf7c576a70feb`
- `CLAUDE_MODEL`: `claude-opus-4-8`
- `CLAUDE_VERDICT`: `GREEN`
- `CLAUDE_RECUSAL`: `CLEAR`
- `CLAUDE_RAW_SHA256`: `03e7fe84ff394d88016f9ccff415effcccfa16e6b585b4c46c11ff40851d0c3e`
- `AGY_REQUIRED`: `false`
- `UTC_RECORDED`: `2026-07-28T00:48:07Z`

Both required independent, non-authoring judges reviewed the same canonical R4
packet. Their verdicts authorize only the bounded RunPod lifecycle and measured
Gate 6 campaign described by that packet. They do not constitute runtime
evidence or Gate 6 completion.

The limitations remain mandatory: synthetic paired comparison; three
repetitions per class and method; no population-level inference; the raw
candidate comparative source was hash-bound to the independently GREEN Gate 5
candidate but omitted from this external packet because the local egress
gateway classified its ephemeral password assignment; SSH uses disclosed TOFU;
and provider-side tool identity, network denial, measurement, evidence custody,
cost, and teardown still require direct proof.
