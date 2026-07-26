# P9 Live Cleanup Receipt R1

- `RESULT`: `GREEN`
- `UTC_CLOSED`: `2026-07-26T22:08:00Z`
- `CAMPAIGN`: `ck-p9-completion-r1`
- `CLOSE_RECEIPT_SHA256`: `e52539b4ca83f6a90d875eab2743de087900e629b9e5a67e76c14cbee4788aff`
- `TEMP_CLIENT_TEARDOWN`: `GREEN`
- `OAUTH_STATE`: `Not logged in`

The first CockroachDB web-shell cleanup attempt placed the exact scoped
deletes inside `BEGIN`/`COMMIT`. The web shell rejected statement 1 (`BEGIN`)
with SQLSTATE `XXUUU`, so no statement in that batch executed. The same six
ID-scoped deletes were then executed individually in foreign-key-safe order:
projection events, worker results, context vectors, receipts, trajectory
events, and tasks. Every individual statement reported success.

A separate runtime-identity readback returned zero for all six classes:

```text
tasks events receipts vectors workers projections
0     0      0        0       0       0
```

The local coordinator accepted its exact twelfth `CLEANUP_TRIAL` operation for
both trials. No CockroachDB client, sinkless changefeed, child, or evidence
process remained. The temporary CA certificate was explicitly unlinked and
its exact temporary directory removed. The OAuth grant was revoked. Existing
P9 AWS resources intentionally remain for S3 under the prior reviewed
preservation contract; no RunPod resource exists.
