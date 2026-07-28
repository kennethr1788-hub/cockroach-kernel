# Hardening Gate 6 R3 — Independent Judge Contract Amendment

- `STATUS`: `FROZEN_FOR_PREFLIGHT`
- `SUPERSEDES_ONLY`: `HARDENING_GATE6_EXECUTION_PLAN_R3.md required-judges section and references to Claude as the R3 preflight/final second lane`
- `PRESERVES`: `all candidate, comparison, isolation, evidence, lifecycle, cost, teardown, and Gate 7 boundaries`
- `PRIMARY_INDEPENDENT_LANE`: `GLM 5.2 availability-first authority route`
- `SECOND_INDEPENDENT_LANE`: `agy-judge pinned Gemini 3.1 Pro (High)`
- `CLAUDE_STATE`: `PERMANENTLY_RECUSAL_REQUIRED_FOR_R3`

## Precedence and provenance

The historical R3 plan required GLM plus Claude. Claude's first R3 review then
materially shaped the x32 and inherited-standard-descriptor hardening, so the
revised packet correctly received `RECUSAL_REQUIRED`. Kenneth has explicitly
authorized AGY as the independent replacement. This amendment controls only
the judge-lane identity. All other R3 plan terms remain binding.

Every fresh preflight or final packet must include the Claude recusal receipts
and this amendment. Neither judge may infer that Claude independently approved
the hardened revision. The valid R3 quorum is now:

1. GLM 5.2 returns GREEN with recusal clear; and
2. AGY's pinned Gemini 3.1 Pro (High) returns GREEN with recusal clear;
3. both outputs bind the exact same packet SHA-256.

Any NOT_GREEN, BLOCKED, INSUFFICIENT_EVIDENCE, RECUSAL_REQUIRED, malformed
output, wrong packet hash, route/model-integrity failure, or unavailable lane
blocks provider creation or final closure. A prior verdict over a different
hash cannot count.

## AGY boundary

AGY is non-authoring and receives sanitized packet bytes only through
`agy-judge`. The route uses the signed Antigravity CLI 1.1.5 binary at SHA-256
`6509d6ca54a66e3eaf61dfe35308ba1dfa1e6b552ef5c4f5f861562c6811ecaf`,
wrapper SHA-256
`217cad1a22d4ca63d356fbe97dfa4caaf9475a5c619232af329b8d00d2a6df15`,
exact Gemini 3.1 Pro (High), strict deny-all tool permissions, terminal
sandboxing, no agents/plugins/hooks/MCP, and a fresh non-agent conversation.
AGY may return only verdicts, blockers, risks, evidence gaps, recusal, and
required reruns. It has no implementation, repository, browser, credential,
RunPod, public-action, or Gate 7 authority.

## Final review

After measured execution, evidence retrieval, exact-ID deletion, and empty
scoped inventory, the same two independent lanes review one newly frozen final
packet hash. GREEN requires complete 54-row evidence, isolation attestation,
tool/candidate hashes, paired aggregation, residue and teardown proof, bounded
cost custody, and honest limitations. The builder never self-approves.
