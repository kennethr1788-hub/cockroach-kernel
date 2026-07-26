# P9 Managed MCP OAuth Authorization Receipt

- `UTC`: `2026-07-26T20:11:52Z`
- `RESULT`: `HUMAN_AUTHORIZATION_RECORDED`
- `GATE`: `MCP_OAUTH_HUMAN_GATE`
- `LAST_GREEN_GATE`: `CK_P8_GOLDEN_GREEN`
- `VERIFIED_HEAD`: `27fa9bf830e8340296f083b0b48e14c89b618a42`
- `VERIFIED_TAG`: `ck-p9-mcp-oauth-gate`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `P9_S3_AUTHORIZATION_SHA256`: `cb46e382f98d9a4d52a882a3d35f1b0ae4db9047e07f713d2212196dc3204214`
- `GLOBAL_CODEX_CONFIG_PRE_SHA256`: `932bb0c065f5c7807698375847f185793f58bb5ace653bb2997863172c8ad863`

## Kenneth's explicit confirmation

> I authorize CockroachDB Managed MCP OAuth for read-only access to only the cockroach-kernel cluster. I understand Codex may securely store the temporary OAuth grant, and I authorize logout and cleanup after the bounded P9 proof.

## Enforced boundary

- The temporary project-scoped configuration binds only the declared
  `cockroach-kernel` cluster ID shown by the authenticated CockroachDB Cloud
  Connect dialog.
- The OAuth permission level must be read-only.
- The normal secure Codex credential store may hold the temporary grant, but
  credential bytes may not be read, printed, logged, committed, or transferred.
- `~/.codex/config.toml` must not be edited; its pre-flow SHA-256 is frozen above.
- Stop on write scope, another cluster, password, MFA, CAPTCHA, terms,
  payment/billing change, or any other human challenge.
- After the bounded proof, run `codex mcp logout`, remove the temporary
  project configuration, and verify the global config hash is unchanged.
- This receipt does not close P9 and does not authorize S3, RunPod, P10, P11,
  release, or any public action.

