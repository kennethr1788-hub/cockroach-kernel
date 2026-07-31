# EV1 Twelve-Task Aggregate Final Receipt R1

- `STATUS`: `EV1_AGGREGATE_EVIDENCE_GREEN`
- `UTC_CLOSED`: `2026-07-31T00:47:22Z`
- `PRODUCT_CANDIDATE`: `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- `FROZEN_CANDIDATE_COMMIT`: `bf27c61`
- `PARSER_ONLY_REPAIR_COMMIT`: `567ead7`
- `AGGREGATE_REPORT_SHA256`: `30c4ff7e587928c7f05524a73860986d6923cda67cf86aaea8a18b4060ce94ce`
- `MANIFEST_FILE_SHA256`: `080e8e2d4e944e2466430681b2e91373d5e7d7087eea2dffa6dc7fc701ed6f4a`
- `MANIFEST_RECEIPT_SHA256`: `885e3aa75b5e55fe2324b56465559d8dc244d95fa241fc5fb1c21df3e4ba5d2e`
- `REVIEW_CONTENT_SHA256`: `73b0a764924ae787ed30f59742aaaf92fc78a665fea0913935f30572975c4bb3`
- `PACKET_SHA256`: `bcf2c335d6e2b735bc781f85e17f4e823ff0518f79ae4897d8c45fecd7adc6e6`
- `JUDGE_RECEIPT_FILE_SHA256`: `566ea2aac2013c5fa28e221e8cfefdafa0ed79b099f2a5a40f892364cd73c36d`
- `JUDGE_RECEIPT_SHA256`: `e34560b132c72d156dc754dd1e68ef6311d242d3c47f591b28ebe8670d3ecf74`
- `GLM_RAW_SHA256`: `b340bfc86f57444e6ffa85a29666ce5d92b6abd75d7582116bc074ccfcbbf361`
- `AGY_RAW_SHA256`: `00c489ae795ed474c73d47b59fcc5a45347f78d2bbebde264a5f559d51241898`
- `SAME_PACKET`: `TRUE`
- `RECUSAL_CLEAR`: `TRUE`

## Terminal accounting

- Nine of nine evaluable recovery tasks passed task-specific acceptance.
- All 33 declared work units in the evaluable set were restored byte-exactly and
  were usable after continuation.
- All nine evaluable tasks used empty-history successors.
- Two predeclared unsafe cases returned their expected `INVALID` outcomes
  without deletion or recovery.
- One task was infrastructure-invalid and remains non-scoring.
- The result is not `12/12 passed` and is not an unqualified 100% recovery
  result.

## Independent review

GLM 5.2 returned `GREEN` with outcome accounting, metrics, limitations, and the
qualified claim all `SUPPORTED`. It returned no blockers, evidence gaps, or
required reruns and explicitly rejected the unqualified `12/12` claim.

AGY returned `GREEN` over the same packet hash with no blockers, evidence gaps,
or required reruns. Its authenticated route was bound to Gemini 3.1 Pro (High);
response-level served-model metadata was not exposed by the provider CLI and is
not claimed.

The first GLM validator invocation was rejected only because the local parser
incorrectly required a word boundary after `[]`. The exact raw GLM response was
preserved, hash-bound, and reused after the parser-only repair. It was not
regenerated or edited.

## Claim supported

> In a frozen twelve-task, single-operator disposable-workspace campaign, nine
> of nine evaluable recovery tasks restored all 33 declared work units
> byte-exactly into empty-history successors and passed their task-specific
> acceptance checks. Two separately predeclared unsafe cases were rejected
> without deletion or recovery. One additional run was infrastructure-invalid
> and excluded from the pass denominator.

## Permanent limitations

- This was one operator with zero independent external users.
- The workspaces were disposable or synthetic, not production workloads.
- The campaign was not a seven-day field trial.
- T01 contained the independently saved human edit but was infrastructure-
  invalid and non-scoring.
- T09 was model-assisted and cannot support an independently-human-edited claim.
- No successful evaluable task contained an independently human-saved edit.
- The measured product invocation latency is not end-to-end incident recovery
  time.
- The evidence does not support recovery of arbitrary uncaptured bytes or
  recovery when no surviving representation exists.

## Custody and boundary

The expected-invalid T07 and T08 workspaces remain preserved as their frozen
contracts require. No product behavior, Gate 3–8 evidence, release surface,
public artifact, video, submission, HOME runtime, or live memory was changed by
this closeout.
