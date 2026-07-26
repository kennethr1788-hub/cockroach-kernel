# P9 Managed MCP Live Proof Receipt R1

- `UTC_CLOSED`: `2026-07-26T20:20:11Z`
- `RESULT`: `MCP_READ_ONLY_BOUNDARY_GREEN; P9_BLOCKED`
- `P9_BLOCKER`: `P9_LIVE_VERTICAL_SLICE_EVIDENCE_MISSING`
- `LAST_GREEN_EXECUTION_GATE`: `CK_P8_GOLDEN_GREEN`
- `STARTING_HEAD`: `27fa9bf830e8340296f083b0b48e14c89b618a42`
- `STARTING_TAG`: `ck-p9-mcp-oauth-gate`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `P9_S3_AUTHORIZATION_SHA256`: `cb46e382f98d9a4d52a882a3d35f1b0ae4db9047e07f713d2212196dc3204214`
- `TEMP_CONFIG_SHA256`: `562fabf2241ea6cb6ab0171881192c98ad9ab64cd1af06aa4cd29c9011ee5821`
- `GLOBAL_CONFIG_PRE_POST_SHA256`: `932bb0c065f5c7807698375847f185793f58bb5ace653bb2997863172c8ad863`
- `OAUTH_AFTER_CLEANUP`: `not_logged_in`

## Human authorization and visible scope

Kenneth explicitly authorized temporary CockroachDB Managed MCP OAuth for
read-only access restricted to only `cockroach-kernel`, secure temporary grant
storage, and logout/cleanup after the proof. The exact statement is preserved
in `P9_MCP_OAUTH_AUTHORIZATION_RECEIPT_R1.md`.

The visible CockroachDB Cloud consent dialog showed:

- `Read Data`: checked and disabled;
- `Write Data`: unchecked;
- read description: SELECT/query-plan/running-query access with no data
  modification;
- the project-local configuration bound the request to the declared cluster
  header;
- no password, MFA, CAPTCHA, terms, payment, or other human challenge appeared.

No consent URL, OAuth state, code challenge, token, user identifier,
organization identifier, cookie, password, connection string, or account
identifier is stored in this project receipt or evidence tree.

## Bounded execution

The final run exposed only `cockroachdb-cloud/select_query`. It executed exactly:

```sql
SELECT task_id, receipt_hash, status, event_hash
FROM ck.mcp_receipt_view
WHERE task_id = 'p9-live-task-1'
LIMIT 1
```

against database `cockroach_kernel`. The call completed and returned
`{"rows":[]}`. This proves the live authenticated read path but not receipt
linkage.

The one exact negative probe was:

```sql
UPDATE ck.receipts
SET status = 'SEALED'
WHERE task_id = 'p9-live-task-1'
```

The exposed MCP tool refused it with `only SELECT statements are allowed, got
UPDATE`. It was not retried or altered. This directly proves the exposed tool
surface is SELECT-only. The visible consent state separately proves write
permission was not selected; the denial is not misrepresented as a database
role-impersonation test.

## Attempts and evidence

1. `bounded-proof-events-attempt1.jsonl`: local response-schema rejection;
   no MCP operation ran.
2. `bounded-proof-events-attempt2.jsonl`: read attempted in `defaultdb` and
   failed because the target view is in `cockroach_kernel`; the UPDATE probe
   was refused.
3. `bounded-proof-events-attempt3.jsonl`: transient session exposed no callable
   MCP tool; no operation ran.
4. `bounded-proof-events.jsonl`: final required-server/tool-allowlisted run;
   exact read completed with zero rows and exact UPDATE was refused.

Final raw event SHA-256:
`3baf276f0c18dd53c4ef0ea695dc59176a0bdccb858da09adade23524bdc72a5`.

Final structured result SHA-256:
`51d7260a19c875496d302efa5a9e2d92d688b53de0929fc496290d71134c8095`.

Secret-pattern scan over the evidence returned zero matches. No unexpected
tool call appears in the final raw events.

## Cleanup

- `codex mcp logout` exited zero using the same ephemeral configuration.
- Post-logout auth status is `not_logged_in`.
- The temporary project configuration was removed.
- The global Codex config SHA-256 and stat tuple are unchanged.
- No OAuth credential bytes were inspected or recorded.

## Why P9 remains blocked

The final Managed MCP read returned zero rows. The repository contains no raw
live evidence proving the canonical two distinct complete P9 vertical-slice
trials: authoritative CockroachDB task/event/receipt transactions, vector
retrieval linked to those rows, distinct Lambda request IDs, worker-result
commit, sinkless changefeed projection/restart evidence, MCP receipt linkage,
and fresh-context deterministic continuation. The earlier AWS evidence proves
two byte-identical invocations of one request, not the full two-trial live
vertical slice required by the canonical P9 contract.

Therefore neither the final P9 packet nor GLM/AGY review may be claimed ready,
and `CK_P9_INTEGRATION_GREEN` is not issued. S3 remains forbidden.

## Next safe action

Freeze and implement only the missing P9 live evidence coordinator/harness,
run two distinct synthetic vertical-slice trials under the existing reviewed
AWS/CockroachDB boundaries, and prove non-empty receipt linkage. Only then ask
Kenneth for a fresh one-time read-only Managed MCP OAuth authorization, repeat
the exact linked SELECT proof, revoke it, freeze the final packet, and run GLM
plus AGY on one hash.

