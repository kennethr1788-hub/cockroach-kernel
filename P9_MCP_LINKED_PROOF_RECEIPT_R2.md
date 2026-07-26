# P9 Managed MCP Linked Proof Receipt R2

- `RESULT`: `P9_LINKED_MCP_PROOF_GREEN_AND_REVOKED`
- `UTC_CLOSED`: `2026-07-26T22:08:00Z`
- `SERVER`: `cockroachdb-cloud`
- `DATABASE`: `cockroach_kernel`
- `OPERATIONS`: `1`
- `GLOBAL_CONFIG_SHA256`: `932bb0c065f5c7807698375847f185793f58bb5ace653bb2997863172c8ad863`
- `AUTH_AFTER_CLEANUP`: `Not logged in`
- `EVIDENCE_ROOT`: `evidence/p9-mcp-linked-r2/`

Kenneth's explicit authorization in the canonical execution prompt was used
for one fresh OAuth grant. The visible consent dialog showed `Read Data`
checked and disabled and `Write Data` unchecked. The command-line
configuration bound the server to only the declared cluster. No password,
MFA, CAPTCHA, terms, payment, or other human challenge appeared.

Exactly one `cockroachdb-cloud/select_query` tool call executed the frozen
bounded SELECT against `ck.mcp_receipt_view`. It returned exactly the two
declared task IDs, distinct nonempty receipt and event hashes, and `SEALED`
status for both. The structured result was `GREEN`, recorded one operation,
reported no unexpected tool, and observed no credential material.

No UPDATE or other write probe was repeated because the earlier R1 proof
already established the SELECT-only tool boundary and the R2 contract allowed
only the final exact read. No other MCP tool, server, shell, web, filesystem,
or browser operation was available to the bounded proof agent.

After the query, `codex mcp logout` removed the OAuth credential. A scoped
status check reported `Not logged in`. The global Codex configuration SHA-256
still equals the frozen pre-flow value; its unchanged file modification time
predates this flow. No OAuth token, state, callback code, cookie, account,
organization, cluster identifier, or connection string is stored in this
receipt or its evidence tree.

Evidence SHA-256 values:

- prompt: `84242c874ca9b5565a2afef402f8e8b25a0d4cc2d9141d99f6dcb5145a008b09`
- schema: `f1814dac81e89ae8167fd3cc6b63ea76bb5af9ef9cccb3ba1cf60dbb612df4cc`
- structured result: `8f8cc80e21d2420e120b3f3222f45885eaa69169579643fe888d33ead5574f5d`
- sanitized event trace: `8b92099d2848f7df84f671090473a5fc1044f702a94fff3c5c5f20b14cfe7795`
