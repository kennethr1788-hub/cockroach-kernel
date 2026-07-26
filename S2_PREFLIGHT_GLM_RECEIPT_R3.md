# S2 Preflight GLM Receipt R3

- `ARTIFACT`: `S2_PREFLIGHT_PACKET_R3.md`
- `PACKET_SHA256`: `f99a5deda6715fe50a186420594d5797820fe263e06e1b9d5c420a91a5abf6b8`
- `ROUTE`: direct `glm-zai`
- `SERVED_MODEL`: `glm-5.2`
- `EXIT_STATUS`: `0`
- `VALIDATION`: `VALID_EXACT_HASH_GREEN`

## Raw result

```text
glm-zai: served by glm-5.2
ROLE: GLM
ARTIFACT: S2_PREFLIGHT_PACKET_R3.md
BUILDER_AND_INFLUENCE_DISCLOSURE: None. No builder direction or external influence applied.
PACKET_SHA256: f99a5deda6715fe50a186420594d5797820fe263e06e1b9d5c420a91a5abf6b8
VERDICT: GREEN
FAILED_CRITERIA: None
EVIDENCE: The canonical packet embeds the complete S2 orchestration source, lifecycle guard code, frozen remote command, spend envelope, payload custody manifest, and raw local evidence anchors. The remote command enforces a continuous 21,600-second execution with exactly 72 checkpoints (300s), 24 safety replays (900s), and 6 hourly summaries (3600s). The embedded contract and source enforce loopback-only database traffic, bounded resource limits (DB: 536870912 bytes, evidence: 134217728 bytes, RSS: 2147483648 bytes), and exact-ID fail-closed teardown. The spend limits accept only 2 vCPU/4 GiB at <=$0.06/h or 2 vCPU/8 GiB at <=$0.08/h, maintaining the active rate <=$0.085/h.
FAILURE_MECHANISM: N/A
MISSING_PROOF: None
NON_BLOCKING_RISKS: Previous attempts R1 and R2 failed to produce a verdict due to output length limits and local egress metadata false positives, but are superseded by the complete and locally successful R3 evidence and source embeds.
RECUSAL_CHECK: None
```
