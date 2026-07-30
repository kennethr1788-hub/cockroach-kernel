# EV1 Preflight R2 Judge Receipt

- `STATUS`: `NOT_GREEN; PACKET_CONSTRUCTION_SCOPE_DEFECT`
- `PACKET_SHA256`: `cfc32c214a4034205b93e0143978348f30dfac1a9f53dd423bf0702505e6d69d`
- `GLM_5_2_ATTEMPT_1`: `INVALID_EMPTY_CONTENT_AFTER_FINISH_REASON_LENGTH`
- `GLM_5_2_ATTEMPT_1_STDERR_SHA256`: `fe590c1b1c98947e0c4331ea877ef623c98a631974c0775f7ac9031d03b816b1`
- `GLM_5_2_ATTEMPT_2`: `GREEN; HASH_MATCH; RECUSAL_CLEAR`
- `GLM_5_2_RAW_SHA256`: `4a244d15306d01400ef0ecee503dd0c2ef02ae85e2f9cd0655daa19bfd83cb79`
- `GLM_5_2_STDERR_SHA256`: `322cf8f0e32384379d0ae5ac962ebce4f3b66a06230b5144a74b9ec515cae344`
- `AGY`: `BLOCKED; HASH_MATCH; RECUSAL_CLEAR`
- `AGY_RAW_SHA256`: `dfd6ed42f41feb1064634f44c84ecb394f62a9da52cbeb41d293325b65b57d93`
- `AGY_STDERR_SHA256`: `bf32ab8c082fa1aff618ee172c412b767bf7f636479cf49543749f2ba6ad30ee`
- `MEASURED_TASKS_STARTED`: `0`
- `MEASURED_CLOCK_STARTED`: `FALSE`

## Root cause

The R2 packet extractor selected every later line containing `LIMITATION`, not
only lines inside the ordered backlog section. It therefore copied the frozen
candidate's now-superseded pre-confirmation footer into the judge packet. The
separate R2 human receipt closed that gate, but the stale footer created a real
internal contradiction. AGY correctly refused to reconcile it by assumption.

## Narrow correction

Constrain packet extraction to bytes between `## Ordered backlog` and
`## Aggregate candidate checks`. Preserve the exact backlog, human receipt,
mechanical receipt, product candidate, task contracts, thresholds, and R2 judge
outputs. Freeze a new packet hash and rerun both GLM 5.2 and AGY; no R2 result
may count after the packet changes.
