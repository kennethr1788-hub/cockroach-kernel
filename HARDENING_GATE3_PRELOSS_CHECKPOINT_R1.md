# Hardening Gate 3 Pre-Loss Checkpoint R1

- `STATUS`: `CAPTURE_GREEN_LOSS_NOT_YET_EXECUTED`
- `CAMPAIGN_ID`: `CK-G3-20260727T192406Z`
- `TASK_ID`: `ck-g3-real-workflow-r1`
- `LAST_GREEN_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `TARGET_GATE`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `UTC_RECORDED`: `2026-07-27T19:44:36Z`
- `SOURCE_COMMIT`: `ba1217c4d830a3c7633e352c0e10712d6b817cee`
- `DISPOSABLE_AGENT_COMMIT`: `f8b2e5d7e15352bf2762bd000875a85a0b56a75b`
- `CAPTURE_RECEIPT_SHA256`: `c4ae85a6ef201d98f2079b077f0d86784c905cb93539128d2bee371b8d326ee0`
- `LIVE_RECEIPT_SHA256`: `4ef1c44450f694763d971b1ce5cf5ee48c6f5c032c4ca4abbbdc2cf5838f2ff3`
- `MANIFEST_FILE_SHA256`: `61e7330a71b296a3a371b0f8fa2d415df511bff72fb1922247b94ae9f79ed7de`
- `MANIFEST_RECORD_HASH`: `112dc84805470594a0b6b6951e386fe807a98af0d47a951c6bbd618296ae92bf`
- `TRAJECTORY_RECORD_HASH`: `16ed0d96d489038ecf7cc2f918e393ca0b2d74c04c61bac99de6dad06b52d62d`
- `DECISION_RECORD_HASH`: `452a35a89c52a5a432edf992c5c7ea860fe32b871ebd80154c80d29cc83ad6ec`
- `HUMAN_EDIT_SHA256`: `13d6838a0f987de6c2f9353e07193b7601a7a711c5f0ee15d56f0bcd4b4699e5`

## Frozen state

The content-addressed custody root is outside the disposable workspace and
contains exactly three declared work objects: one committed agent unit, one
uncommitted agent unit, and Kenneth's independently saved edit. Every object
filename equals its SHA-256 and every object was rehashed before this
checkpoint.

The pre-capture executable suite passed 14 tests. Five local deterministic
verifier executions returned `PROMOTE / VERIFIED`. The P7 selector returned
`PROMOTE / MAX_PROVEN_PREFIX`.

AWS returned a schema-valid advisory response bound to the frozen request.
One CockroachDB transaction inserted the Gate 3 task, trajectory event,
receipt, context vector, worker result, and projection. Joined readback and the
MCP receipt view both returned the exact Gate 3 task. No credential bytes are
stored in the evidence.

## Loss authorization boundary

The only allowed destructive target is:

`.hardening-runtime/gate3-real-workflow/workspace`

The loss step must rehash all declared workspace files and all three custody
objects before deleting that exact disposable root. The canonical repository,
custody root, HOME state, cloud configuration, and unrelated files are not
destructive targets.

The orchestrating Codex conversation remains active. The successor proof must
therefore be described narrowly: a fresh OS process receives no conversation
input and may use only the frozen custody packet plus the exact local base
commit. This is not evidence that the orchestrating conversation itself was
destroyed.
