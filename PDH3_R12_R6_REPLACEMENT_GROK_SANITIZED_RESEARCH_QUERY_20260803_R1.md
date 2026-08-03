# Public research question: CockroachDB full-cardinality preflight repair

Research a minimal, production-honest repair for a synthetic CockroachDB v26.2 preflight harness. Do not assume access to source code, private data, credentials, provider accounts, or tools other than public web search/fetch. Cite current primary CockroachDB and RunPod documentation where relevant. Do not redesign the product and do not weaken any cardinality, latency, evidence, cost, or teardown gate.

The harness runs a single-node-hosted three-process CockroachDB test cluster on one disposable Linux GPU worker. Historical failures already repaired include setup-reserve exhaustion, uncertain DDL outcomes, gateway recovery, co-located process-quorum behavior, host-controller detachment, vector-ingest pathology, misuse of ANN as an exact verifier, missing raw remote output, ambiguous semantic terminal states, missing receipt lookup indexes, and excessive packet-capture volume.

The newest failed preflight established these facts:

1. Hardware/resource capability and an extracted Linux smoke passed.
2. A 10,000-task query-plan rung passed with exact counts and prospective secondary indexes.
3. A 50,000-task rung then sent one client command containing five semicolon-separated INSERT...SELECT statements: tasks, one trajectory event per task, two receipts per task, one VECTOR(64) row per task, and one projection per task.
4. The schema already contained a CockroachDB vector index on the vector table. The combined client subprocess exceeded 1,800 seconds and was terminated fail-closed.
5. The database process and generated root cleaned up correctly and evidence was retrieved.
6. The provider Pod was successfully deleted, but the host lifecycle guard failed to recognize this exact RunPodCTL v2.8 JSON error envelope as absence: `{"error":"failed to get pod: pod not found","code":"not_found","status":404}`. Its parser rejected the envelope because it treated every field named status/statusCode/code as though it must be an integer 404; the string `code=not_found` caused false rejection even though `status=404` and the message identified a Pod as not found.

The repository already contains a more robust full-scale seed path with:

- deterministic batches;
- per-table INSERT statements;
- `ON CONFLICT DO NOTHING` for uncertain outcomes;
- exact per-batch content reconciliation that rejects mismatched existing rows;
- bounded retries and deadlines;
- persistent parameterized vector clients using one-row autocommit transactions;
- exact final cardinality/content reconciliation;
- vector-index health and ANN-quality probes.

Research and evaluate the smallest defensible repair for the failed preflight. Address:

1. Whether the plan-analysis rung should reuse the existing robust seed path instead of maintaining a second bulk-seed implementation.
2. How to preserve the three query-plan scales (10k, 50k, 100k) without turning five tables into one client timeout domain.
3. Whether to keep the vector index online during the plan-analysis seed, temporarily defer it, or seed vectors through persistent clients, considering CockroachDB's documented vector-index behavior and the fact that the final full-cardinality path already has a separately proven vector-ingest method.
4. How `ON CONFLICT DO NOTHING` can conceal corrupt or mismatched rows and the exact reconciliation required to prevent that.
5. Per-statement, per-batch, per-scale, and global PF2R deadlines that stay bounded while preventing one SQL operation from consuming the entire setup window.
6. Fail-closed behavior after an uncertain client timeout, including when a retry is safe and when the scale must abort.
7. Exact evidence to emit for every batch/table: statement hash, range, attempt, elapsed time, reconciliation state, inserted/existing/mismatched rows, cumulative counts, and deadline remaining.
8. A narrow lifecycle-parser correction for the RunPodCTL v2.8 absence envelope that accepts a numeric 404 status plus a Pod-specific not-found message while rejecting contradictory numeric status fields, unrelated 404s, malformed JSON, and arbitrary text.
9. Unit, integration, local scale, extracted-bundle, and short remote canaries required before another paid full preflight.
10. Any lateral failure introduced by sharing seed code between the plan-analysis rung and the full-scale rung.

Return:

- VERIFIED_PUBLIC_GUIDANCE
- ROOT_CAUSE_ASSESSMENT
- MINIMAL_REPAIR_RECOMMENDATION
- ALTERNATIVES_REJECTED
- DEADLINE_AND_BATCHING_CONTRACT
- IDEMPOTENCY_AND_RECONCILIATION_CONTRACT
- VECTOR_INDEX_DECISION
- LIFECYCLE_404_PARSER_CONTRACT
- REQUIRED_TESTS
- GO_NO_GO_CHECKLIST
- PRIMARY_SOURCE_LINKS

Make clear which conclusions are public-document facts, which are engineering inferences, and which require empirical validation. This is advisory research only and grants no implementation, judge, provider, or launch authority.
