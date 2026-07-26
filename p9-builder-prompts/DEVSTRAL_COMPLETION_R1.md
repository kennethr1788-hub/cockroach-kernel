# Sanitized Devstral P9 completion boundary review

This is a one-turn no-tool text-only contribution. Review only the supplied P9
completion contract summary. Return a compact typed boundary checklist for:
exact AWS Lambda name/region, exact CockroachDB objects, fixed operation enum,
parameterized SQL only, credential separation, read-only single-cluster MCP,
sinkless changefeed no-write-back, payload/invocation/cost/retention ceilings,
campaign cleanup, and clean-state assertions. Name every field and its allowed
type/value. Flag contradictions; do not write code, implementation plans,
patches, commands, credentials, account identifiers, URLs beyond official
service docs, or verdicts. Do not judge or claim a gate.

Frozen facts: campaign `ck-p9-completion-r1`; AWS `us-west-2` function
`ck-p9-evaluator`; CockroachDB cluster `cockroach-kernel`, database/schema
`cockroach_kernel.ck`; exact six tables, view `ck.mcp_receipt_view`, vector
index `context_vectors_vector_idx`; request/response <=16 KiB; observations <=16
and <=256 bytes; one in-flight Lambda call; <=1,000 P9/S3 calls; <=$5 AWS;
temporary OAuth read-only only for this cluster; local verifier is sole
PROMOTE/REFUSE/INVALID authority; dynamic SQL/shell/URL/ARN/path/command and
credential transfer are forbidden.
