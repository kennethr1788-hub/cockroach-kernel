# Hardening Gate 3 Independent Judge Packet R1

You are the independent non-authoring judge. Do not praise the work and do not
suggest code. Find blockers. You have no tools, shell, browser, filesystem,
credential, deployment, implementation, or public-action authority.

Decision requested: Does this single-operator real-workflow trace meet
`HARDENING_3_REAL_WORKFLOW_GREEN` as an honest, complete evidence trace?

Review criteria:

1. all ten required workflow steps are directly evidenced;
2. the three declared work units are genuinely retained after declared loss;
3. the cloud output remains advisory and local deterministic policy is sole
   promotion/refusal authority;
4. overwrite refusal, unchanged original bytes, fresh-root behavior, replay
   refusal, executable checks, and residue assertions are coherent;
5. destructive scope, credential boundary, live-row retention, and cleanup are
   safe and honestly described;
6. limitations are narrow enough that the gate claim remains valid;
7. hashes and cross-record linkages are internally consistent.

Return exactly:

- `SERVED_MODEL: <provider model identity>`
- `PACKET_SHA256: <the supplied packet hash>`
- `VERDICT: GREEN | NOT_GREEN | INSUFFICIENT_EVIDENCE`
- `BLOCKERS:` numbered list or `none`
- `NON_BLOCKING_RISKS:` numbered list or `none`
- `EVIDENCE_BASIS:` concise references to packet sections

GREEN means no blocker remains for Gate 3 evidence integrity. Do not judge
later hardening gates, release readiness, benchmark superiority, or submission
readiness.

## Task contract

# Hardening Gate 3 Task Contract R1

- `STATUS`: `TASK_CONFIRMED_TRACE_NOT_YET_ARMED`
- `LAST_GREEN_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `TARGET_GATE`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `TARGET_CODEBASE`: disposable local clone of the Cockroach Kernel repository
- `SOURCE_COMMIT`: `ba1217c4d830a3c7633e352c0e10712d6b817cee`
- `DISPOSABLE_WORKSPACE`: `.hardening-runtime/gate3-real-workflow/workspace`
- `DATA_CLASS`: non-sensitive project source and synthetic evidence only
- `UTC_RECORDED`: `2026-07-27T19:24:06Z`

## Kenneth's task selection

Kenneth accepted the immediately preceding recommended Gate 3 task and directed
Codex to perform it. The concrete task is:

> Harden the existing CLI so a completed receipt set cannot be silently
> overwritten. The first `cockroach-kernel demo` execution into a clean output
> root must succeed. A second execution targeting that same root must fail
> closed with exit code `2` and one stable sanitized reason code while leaving
> the original receipt bytes unchanged. A new clean output root must continue
> to work normally. Failed writes must leave no temporary-file residue.

This is evidence-integrity hardening, not a new product feature.

## Executable acceptance contract

The isolated successor must prove all of the following:

1. `python3.12 -m unittest cockroach_kernel.test_cli cockroach_kernel.test_http_api`
   exits `0`;
2. the first CLI demo execution into a fresh output root exits `0`;
3. SHA-256 hashes are captured for both original receipts;
4. the second execution into the same root exits `2` with the frozen stable
   overwrite-refusal reason code;
5. the original receipt hashes remain byte-identical after the refusal;
6. no `*.tmp` or other partial write residue remains;
7. a demo execution into another fresh output root exits `0`.

## Human-owned edit

After the isolated trace is armed, Kenneth must personally type and save one
non-sensitive acceptance statement in the declared file:

`.hardening-runtime/gate3-real-workflow/workspace/GATE3_HUMAN_ACCEPTANCE.txt`

Chrome control and CUA may display or navigate to the file, but neither Codex
nor any automation may type or save Kenneth's statement. Direct file-state
evidence and Kenneth's confirmation are required before implementation begins.

## Kill line

Stop without implementation, loss simulation, cloud recording, promotion, or
cleanup if the declared human edit is absent; if any credential, HOME state,
private/client data, unrelated repository, canonical source checkout, or
undeclared external surface would be touched; or if the disposable-workspace
boundary cannot be proved.

## Human edit receipt

# Hardening Gate 3 Human Edit Receipt R1

- `STATUS`: `HUMAN_EDIT_VERIFIED`
- `CAMPAIGN_ID`: `CK-G3-20260727T192406Z`
- `TASK_CONTRACT`: `HARDENING_GATE3_TASK_CONTRACT_R1.md`
- `TRACE_PREFLIGHT`: `HARDENING_GATE3_TRACE_PREFLIGHT_R1.md`
- `DECLARED_FILE`: `.hardening-runtime/gate3-real-workflow/workspace/GATE3_HUMAN_ACCEPTANCE.txt`
- `PLACEHOLDER_SHA256`: `5b04275e2f60c6df290b6dbc7950671640dd1f3ff17b1238c98c33ac6c3d8a78`
- `SAVED_FILE_SHA256`: `13d6838a0f987de6c2f9353e07193b7601a7a711c5f0ee15d56f0bcd4b4699e5`
- `FILE_MTIME_UTC`: `2026-07-27T19:31:39Z`
- `FILE_SIZE_BYTES`: `140`
- `HUMAN_TEXT_LOCATION`: first non-comment, nonempty line following `KENNETH_ACCEPTANCE:`
- `HUMAN_TEXT_LENGTH`: `9`
- `VERIFICATION_UTC`: `2026-07-27T19:33:12Z`

## Direct confirmation

Kenneth stated in the active Codex conversation:

> I personally typed and saved the Gate 3 acceptance edit.

## File-state verification

The saved file differs from the frozen model-created placeholder. The declared
field is followed by one nonempty, non-comment human line. The human text is
not copied into this receipt; its exact saved bytes are bound by SHA-256.

This receipt closes only the human-edit prerequisite. It does not claim task
implementation, live trajectory recording, declared loss, continuation,
cleanup, independent review, or Gate 3 GREEN.

## Pre-loss checkpoint

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

## Final report

# Hardening Gate 3 Real Workflow Report R1

- `STATUS`: `AWAITING_INDEPENDENT_GLM_REVIEW`
- `CAMPAIGN_ID`: `CK-G3-20260727T192406Z`
- `TASK_ID`: `ck-g3-real-workflow-r1`
- `LAST_GREEN_GATE`: `HARDENING_2_AWS_DEMO_GREEN`
- `TARGET_GATE`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `EVIDENCE_CLASS`: `SINGLE_OPERATOR_REAL_WORKFLOW_EVIDENCE`
- `BASE_COMMIT`: `ba1217c4d830a3c7633e352c0e10712d6b817cee`
- `DISPOSABLE_AGENT_COMMIT`: `f8b2e5d7e15352bf2762bd000875a85a0b56a75b`
- `PRELOSS_CHECKPOINT_COMMIT`: `8a2e151615d9d1a327de5439dd19561e51fd6be0`
- `CAPTURE_RECEIPT_SHA256`: `c4ae85a6ef201d98f2079b077f0d86784c905cb93539128d2bee371b8d326ee0`
- `LOSS_RECEIPT_SHA256`: `0d1b614458234496784c31f91cfe0474887fb4a0f5b4eca226fab5444999e9ba`
- `CONTINUATION_RECEIPT_SHA256`: `cb2bcc1df56f6a88276b2a685fc9f3bc5e30816bb54d151091364d384d06a050`
- `RESIDUE_RECEIPT_SHA256`: `03be225cf64c4a741e683b3f725725be97372c22e1740b58f6901ee254162249`
- `EVIDENCE_MANIFEST_RECORD_HASH`: `bdb98a84fc39da166c2bd071249f5491b60be6763b9a8d56b7104368ec2b487e`
- `EVIDENCE_MANIFEST_FILE_SHA256`: `0c4596c5e4cc42eed4838d110b25f0b9c3e6933e1bf4c427f4e87192590f7d75`

## Ten-step trace

1. Kenneth's concrete task was frozen: refuse repeated CLI demo receipt-set
   writes without changing the existing bytes or leaving partial residue.
2. Codex produced useful committed progress in `cockroach_kernel/cli.py` and a
   useful uncommitted edge-case test in `cockroach_kernel/test_cli.py`.
3. The product recorded the declared trajectory through one real AWS Lambda
   advisory invocation and one CockroachDB transaction containing a task,
   event, immutable receipt, vector, worker result, and projection.
4. Kenneth independently typed and saved the declared human edit. Its bytes
   are not copied into the public report; SHA-256 binds them.
5. The exact disposable workspace was deleted after all three work objects
   were rehashed against content-addressed custody outside it.
6. A fresh OS process ran with an empty temporary HOME and no conversation
   input. It received only the custody root, the exact local base repository,
   and the successor target.
7. Five P4 verdicts returned `PROMOTE / VERIFIED`; the P7 selector returned
   `PROMOTE / MAX_PROVEN_PREFIX`; the one-use warrant was consumed before
   successor materialization.
8. The fresh process reconstructed and continued without Kenneth restating
   the task. Committed agent, uncommitted agent, and human units were retained.
9. Fourteen tests passed. A first demo run exited `0`; the second run against
   the same output root exited `2` with `OUTPUT_ALREADY_EXISTS`; both original
   receipt hashes were unchanged; dot-file residue was empty; a fresh output
   root exited `0`.
10. Promotion, unrecovered-work, replay, loss, continuation, and residue
    receipts were preserved. Replay exited `2` with `WARRANT_REPLAY` before a
    successor was created. The original and both successor roots, plus the
    temporary HOME, are absent; custody remains.

## Measured result

- Declared work units: `3`
- Provable work units: `3`
- Retained work units: `3`
- Lost work units: `0` file-content units
- Committed agent unit retained: `yes`
- Uncommitted agent unit retained: `yes`
- Independent human unit retained: `yes`
- Task restatement required: `no`
- Loss-to-verified-continuation wall clock: `23,981 ms`
- Executable checks passed: `14/14`
- Second-run overwrite refusal: exit `2`, reason `OUTPUT_ALREADY_EXISTS`
- Original receipt mutation: `none`
- Temporary write residue: `none`
- Replay mutation: `none`
- Unrecovered ledger items: `0`
- Live Cockroach readback counts for task/event/receipt/vector/result/projection:
  `1/1/1/1/1/1`
- Live count output SHA-256:
  `6e9bbe0b10cb5a5674c0cdd32a4b2da4eae7be296c25aa488eb475ed7ad1f246`

## Cloud and authority boundary

AWS Lambda emitted advisory observations only. The response was validated and
hash-bound to the request before the CockroachDB transaction. CockroachDB is
the persistent live trajectory/evidence ledger. Local P4/P7 deterministic
logic alone selected the candidate and authorized reconstruction. No cloud or
model output decided pass/fail or performed deletion.

The live Gate 3 rows are intentionally retained as immutable evidence. The
least-privilege runtime identity has `SELECT` and `INSERT` but no `DELETE` on
the relevant tables; retained evidence is therefore declared state, not
temporary residue.

## Honest limitations and failed attempts

- The disposable Git branch and local commit object were not reconstructed.
  The changed file bytes represented by that commit were retained exactly.
- The orchestrating Codex conversation remained active. What was destroyed was
  the disposable workspace and its local Git session. The continuation proof
  is a fresh OS process with no conversation input; it is not proof that this
  orchestration conversation was terminated.
- The first fresh-process launch never started because its sanitized `PATH`
  omitted the project Python location. The warrant remained `ISSUED` and no
  successor existed. The corrected launch changed only `PATH` and succeeded.
- The first cleanup receipt attempt deleted the verified successor and then
  stopped because macOS resolves `/tmp` through `/private/tmp`. Custody was
  intact. The cleanup was made idempotent, the exact empty temporary HOME was
  removed, and the final residue receipt passed.
- This is one single-operator trace, not public-user research or proof of
  population-wide usability.

## Gate boundary

This report does not self-approve Gate 3. `HARDENING_3_REAL_WORKFLOW_GREEN`
may be recorded only if an independent GLM judge returns GREEN over the exact
frozen packet hash and its verdict is preserved unchanged.

## Trace harness source

#!/usr/bin/env python3
"""Gate 3 real-workflow capture, declared loss, and fresh-process continuation.

The custody root is outside the disposable workspace. Only three declared,
non-sensitive work units are stored as content-addressed objects. Committed
base state is reconstructed from an exact local Git commit; no network remote,
credential byte, or hidden conversation state enters the successor.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any


REPO = Path(__file__).resolve().parents[1]
P9 = REPO / "p9-cloud"
S3 = REPO / "s3-soak"
P7 = REPO / "p7-recovery" / "records.py"
P4 = REPO / "p4-verifier" / "verifier.py"
CONFIG = REPO / ".s3-runtime" / "live-config.json"
AWS_CONFIG = REPO / ".s3-runtime" / "aws-auth" / "config"
AWS_CACHE = REPO / ".s3-runtime" / "aws-auth" / "login-cache"

TASK_ID = "ck-g3-real-workflow-r1"
CAMPAIGN_ID = "CK-G3-20260727T192406Z"
BASE_COMMIT = "ba1217c4d830a3c7633e352c0e10712d6b817cee"
AGENT_COMMIT = "f8b2e5d7e15352bf2762bd000875a85a0b56a75b"
HUMAN_HASH = "13d6838a0f987de6c2f9353e07193b7601a7a711c5f0ee15d56f0bcd4b4699e5"
TASK_CONTRACT_HASH = "3a9a2b7f1dc305ff0099e51e5716c2dc0ac523190ea9ecc83196382b8dfea290"
DECLARED_PATHS = (
    "cockroach_kernel/cli.py",
    "cockroach_kernel/test_cli.py",
    "GATE3_HUMAN_ACCEPTANCE.txt",
)
EXPECTED_STATUS = (
    " M cockroach_kernel/test_cli.py",
    "?? GATE3_HUMAN_ACCEPTANCE.txt",
)
NAMESPACE = "ck-g3-real-workflow"


class TraceError(RuntimeError):
    pass


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise TraceError("MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, str(S3))
sys.path.insert(0, str(P9))
import records as cloud_records  # type: ignore  # noqa: E402
import context_vector  # type: ignore  # noqa: E402
import cloud_adapter  # type: ignore  # noqa: E402

p7 = _module("gate3_p7_records", P7)
p4 = _module("gate3_p4_verifier", P4)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    raw = canonical(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path: Path) -> Any:
    return json.loads(path.read_bytes())


def run(command: list[str], *, cwd: Path | None = None,
        timeout: int = 180) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=timeout, check=False)
    return result


def require_ok(result: subprocess.CompletedProcess[bytes], code: str) -> None:
    if result.returncode != 0:
        raise TraceError(f"{code}:{sha256(result.stdout)}")


def safe_relative(value: str) -> str:
    if (not value or value.startswith("/") or "\\" in value or "\x00" in value
            or any(part in {"", ".", ".."} for part in value.split("/"))):
        raise TraceError("UNSAFE_PATH")
    return value


def safe_target(root: Path, relative: str) -> Path:
    safe_relative(relative)
    target = root.joinpath(*relative.split("/"))
    if root.resolve() not in target.resolve(strict=False).parents:
        raise TraceError("UNSAFE_PATH")
    return target


def put_object(objects: Path, raw: bytes) -> str:
    digest = sha256(raw)
    target = objects / digest
    if target.exists():
        if target.is_symlink() or sha256(target.read_bytes()) != digest:
            raise TraceError("OBJECT_COLLISION")
        return digest
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb", closefd=True) as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return digest


def git(workspace: Path, *args: str) -> str:
    result = run(["git", "-C", str(workspace), *args])
    require_ok(result, "GIT_FAILED")
    return result.stdout.decode("utf-8").rstrip("\n")


def test_suite(workspace: Path) -> dict[str, Any]:
    started = time.monotonic_ns()
    result = run(["python3.12", "-m", "unittest",
                  "cockroach_kernel.test_cli", "cockroach_kernel.test_http_api"],
                 cwd=workspace)
    elapsed = (time.monotonic_ns() - started) // 1_000_000
    receipt = {
        "command": "python3.12 -m unittest cockroach_kernel.test_cli cockroach_kernel.test_http_api",
        "exit_status": result.returncode,
        "output_sha256": sha256(result.stdout),
        "elapsed_ms": elapsed,
    }
    if result.returncode != 0:
        raise TraceError("EXECUTABLE_TEST_FAILED:" + receipt["output_sha256"])
    return receipt


def build_recovery(manifest: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    events = []
    for sequence, name in enumerate(("TASK_DECLARED", "AGENT_COMMITTED",
                                     "AGENT_UNCOMMITTED", "HUMAN_EDIT_SAVED",
                                     "LIVE_RECORD_ARMED")):
        events.append({"sequence": sequence, "event": name,
                       "event_hash": p7.sha256_hex({"sequence": sequence, "event": name})})
    previous = ""
    for event in events:
        previous = p7.sha256_hex({"previous": previous, "event": event})
    trajectory = {
        "version": p7.VERSION, "receipt_id": "rcpt-g3-trajectory-r1",
        "task_id": TASK_ID, "manifest_hash": p7.sha256_hex(manifest),
        "events": events, "trajectory_hash": previous,
    }
    quorum = {"decision": "PROMOTE", "reason": "GATE3_DECLARED_TRACE",
              "approvals": 3, "refusals": 0}
    file_hashes = {item["path"]: item["content_hash"] for item in manifest["files"]}
    candidate = {
        "version": p7.VERSION, "candidate_id": "cand-g3-real-r1",
        "task_id": TASK_ID,
        "provenance": {"source": "gate3-content-addressed-custody"},
        "source_receipt_hash": p7.sha256_hex(trajectory),
        "policy_version": "gate3-policy-r1", "policy_veto": False,
        "tampered": False, "quorum_decision": quorum,
        "prefix_length": len(events),
        "integrity_hash": p7.trajectory_integrity_hash(events, len(events)),
        "declared_paths": list(DECLARED_PATHS), "file_hashes": file_hashes,
        "executable_test": {
            "test_id": "test-g3-cli-r1", "path": "cockroach_kernel/test_cli.py",
            "feature_hash": file_hashes["cockroach_kernel/test_cli.py"], "passed": True,
        },
    }
    context = {"manifest": manifest, "trajectory_receipt": trajectory,
               "policy_version": "gate3-policy-r1",
               "quorum_decision_hash": p7.sha256_hex(quorum)}
    decision = p7.select_candidate([candidate], context)
    if decision["decision"] != "PROMOTE":
        raise TraceError("RECOVERY_POLICY_REFUSED")
    warrant = p7.make_warrant("warrant-g3-real-r1", TASK_ID,
                              candidate["candidate_id"], decision)
    return trajectory, candidate, context, decision, warrant


def prepare(workspace: Path, custody: Path) -> None:
    workspace = workspace.resolve()
    custody = custody.resolve()
    if custody.exists() or not workspace.is_dir() or workspace.is_symlink():
        raise TraceError("ROOT_STATE_INVALID")
    if git(workspace, "rev-parse", "HEAD") != AGENT_COMMIT:
        raise TraceError("AGENT_COMMIT_DRIFT")
    status = tuple(git(workspace, "status", "--porcelain=v1", "-uall").splitlines())
    if status != EXPECTED_STATUS:
        raise TraceError("WORKSPACE_STATUS_DRIFT")
    if sha256((workspace / DECLARED_PATHS[2]).read_bytes()) != HUMAN_HASH:
        raise TraceError("HUMAN_EDIT_DRIFT")
    test_receipt = test_suite(workspace)

    custody.mkdir(parents=True, mode=0o700)
    objects = custody / "objects"
    objects.mkdir(mode=0o700)
    files = []
    for relative in DECLARED_PATHS:
        target = safe_target(workspace, relative)
        if target.is_symlink() or not target.is_file():
            raise TraceError("DECLARED_FILE_INVALID")
        raw = target.read_bytes()
        digest = put_object(objects, raw)
        files.append({"path": relative, "content_hash": digest,
                      "executable": False, "is_symlink": False})
    manifest = {"version": p7.VERSION, "manifest_id": "manifest-g3-real-r1",
                "task_id": TASK_ID, "files": files}
    p7.validate_manifest(manifest)
    trajectory, candidate, context, decision, warrant = build_recovery(manifest)

    p4_payload = {"manifest_hash": p7.sha256_hex(manifest),
                  "trajectory_hash": p7.sha256_hex(trajectory),
                  "task_contract_hash": TASK_CONTRACT_HASH}
    p4_candidate = {
        "version": "p4-v1", "candidate_id": "cand-g3-real-r1",
        "source_receipt_hash": p7.sha256_hex(trajectory),
        "payload": p4_payload, "payload_hash": p4.digest(p4_payload),
        "schema_version": "p4-v1",
        "provenance": {"source": "gate3-content-addressed-custody"},
        "supported": True, "one_use_state": "ISSUED", "quarantined": False,
        "policy_veto": False, "requested_paths": list(DECLARED_PATHS),
        "declared_paths": list(DECLARED_PATHS),
    }
    verdicts = [p4.verify(p4_candidate) for _ in range(5)]
    if verdicts != [("PROMOTE", "VERIFIED")] * 5:
        raise TraceError("P4_VERIFIER_REFUSED")

    for name, value in (("manifest.json", manifest), ("trajectory.json", trajectory),
                        ("candidate.json", candidate), ("context.json", context),
                        ("decision.json", decision), ("warrant.json", warrant),
                        ("p4-candidate.json", p4_candidate)):
        write_json(custody / name, value)
    write_json(custody / "warrant-state.json", warrant)
    write_json(custody / "pre-capture-test.json", test_receipt)

    request = cloud_records.make_request(
        "request-g3-real-r1", TASK_ID, p4_candidate["candidate_id"],
        p7.sha256_hex(trajectory), cloud_records.sha256_hex(p4_candidate),
        cloud_records.sha256_hex({"policy": "gate3-policy-r1"}),
        {"event_count": 5, "approvals": 3, "refusals": 0,
         "context_relevance": 1.0, "quorum_met": True, "policy_veto": False,
         "tampered": False, "unsafe": False, "warrant_consumed": False},
    )
    request_path = custody / "lambda-request.json"
    response_path = custody / "lambda-response.json"
    write_json(request_path, request)

    os.environ["AWS_CONFIG_FILE"] = str(AWS_CONFIG)
    os.environ["AWS_LOGIN_CACHE_DIRECTORY"] = str(AWS_CACHE)
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "/dev/null"
    config = cloud_adapter._read_config(CONFIG)
    meta, lambda_ms = cloud_adapter._aws_invoke(config, request_path, response_path)
    response = json.loads(response_path.read_bytes())
    cloud_records.validate_response(response)
    if not cloud_records.response_matches_request(request, response):
        raise TraceError("LAMBDA_RESPONSE_LINKAGE_FAILED")
    if meta.get("status_code") != 200 or meta.get("function_error") not in (None, ""):
        raise TraceError("LAMBDA_INVOCATION_FAILED")
    write_json(response_path, response)

    aws_request_id = meta.get("aws_request_id")
    if not isinstance(aws_request_id, str):
        raise TraceError("AWS_REQUEST_ID_INVALID")
    aws_request_id_hash = cloud_records.sha256_hex(aws_request_id.encode("utf-8"))
    event_json = {"kind": "gate3-real-workflow", "manifest_hash": p7.sha256_hex(manifest),
                  "trajectory_hash": p7.sha256_hex(trajectory)}
    task_json = {"kind": "real-workflow", "task_contract_hash": TASK_CONTRACT_HASH}
    task_hash = cloud_records.sha256_hex(task_json)
    state_hash = cloud_records.sha256_hex({"agent_commit": AGENT_COMMIT,
                                           "manifest_hash": p7.sha256_hex(manifest)})
    event_hash = cloud_records.sha256_hex(event_json)
    receipt_json = {"kind": "gate3-custody-receipt",
                    "manifest_hash": p7.sha256_hex(manifest),
                    "trajectory_hash": p7.sha256_hex(trajectory),
                    "response_hash": response["response_hash"]}
    receipt_hash = cloud_records.sha256_hex(receipt_json)
    vector = context_vector.context_vector(
        "refuse receipt overwrite preserve committed uncommitted human progress", NAMESPACE)
    vector_digest = context_vector.vector_digest(vector)
    result_json = {"version": "gate3-worker-result-v1",
                   "request_hash": request["request_hash"],
                   "response_hash": response["response_hash"],
                   "aws_request_id_hash": aws_request_id_hash,
                   "status": "ADVISORY"}
    result_hash = cloud_records.sha256_hex(result_json)
    projection_json = {"version": "gate3-projection-v1",
                       "request_id": request["request_id"],
                       "result_hash": result_hash, "receipt_hash": receipt_hash}
    projection_hash = cloud_records.sha256_hex(projection_json)

    def q(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    vector_text = "[" + ",".join(format(item, ".6f") for item in vector) + "]"
    sql = f"""BEGIN;
INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash) VALUES ({q(TASK_ID)},{q(CAMPAIGN_ID)},{q(canonical(task_json).decode())}::JSONB,decode({q(task_hash)},'hex'),decode({q(state_hash)},'hex'));
INSERT INTO ck.trajectory_events(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash) VALUES ('event-g3-real-r1',{q(TASK_ID)},0,decode('{'0' * 64}','hex'),decode({q(state_hash)},'hex'),{q(canonical(event_json).decode())}::JSONB,decode({q(event_hash)},'hex'));
INSERT INTO ck.receipts(receipt_hash,task_id,event_hash,status,receipt_json) VALUES (decode({q(receipt_hash)},'hex'),{q(TASK_ID)},decode({q(event_hash)},'hex'),'SEALED',{q(canonical(receipt_json).decode())}::JSONB);
INSERT INTO ck.context_vectors(vector_id,task_id,event_hash,namespace,vector,vector_digest) VALUES ('vector-g3-real-r1',{q(TASK_ID)},decode({q(event_hash)},'hex'),{q(NAMESPACE)},{q(vector_text)}::VECTOR(64),decode({q(vector_digest)},'hex'));
INSERT INTO ck.worker_results(request_id,task_id,candidate_id,request_hash,response_hash,attempt,supersedes,status,result_json,result_hash) VALUES ({q(request['request_id'])},{q(TASK_ID)},{q(p4_candidate['candidate_id'])},decode({q(request['request_hash'])},'hex'),decode({q(response['response_hash'])},'hex'),1,NULL,'ADVISORY',{q(canonical(result_json).decode())}::JSONB,decode({q(result_hash)},'hex'));
INSERT INTO ck.projection_events(projection_id,source_table,source_key,receipt_hash,sequence,projected_json,projection_hash) VALUES ('projection-g3-real-r1','worker_results',{q(request['request_id'])},decode({q(receipt_hash)},'hex'),1,{q(canonical(projection_json).decode())}::JSONB,decode({q(projection_hash)},'hex'));
COMMIT;"""
    secret = bytearray(cloud_adapter._password(config))
    sql_env = cloud_adapter._sql_env(config, bytes(secret))
    try:
        existing, _ = cloud_adapter._sql(
            config, sql_env, execute=f"SELECT count(*) FROM ck.tasks WHERE task_id={q(TASK_ID)}")
        if re.findall(rb"\b\d+\b", existing)[-1:] != [b"0"]:
            raise TraceError("LIVE_TASK_ALREADY_EXISTS")
        cloud_adapter._sql(config, sql_env, execute=sql, timeout=90)
        audit_sql = ("SELECT t.task_id, encode(r.receipt_hash,'hex'), w.status, "
                     "encode(w.response_hash,'hex'), v.vector_id, p.projection_id "
                     "FROM ck.tasks t JOIN ck.receipts r USING(task_id) "
                     "JOIN ck.worker_results w USING(task_id) "
                     "JOIN ck.context_vectors v USING(task_id) "
                     "JOIN ck.projection_events p ON p.source_key=w.request_id "
                     f"WHERE t.task_id={q(TASK_ID)}")
        audit, sql_ms = cloud_adapter._sql(config, sql_env, execute=audit_sql)
        mcp, mcp_ms = cloud_adapter._sql(
            config, sql_env,
            execute=("SELECT task_id,receipt_hash,status,event_hash FROM ck.mcp_receipt_view "
                     f"WHERE task_id={q(TASK_ID)}"))
        if TASK_ID.encode() not in audit or TASK_ID.encode() not in mcp:
            raise TraceError("LIVE_READBACK_FAILED")
    finally:
        sql_env.pop("PGPASSWORD", None)
        for index in range(len(secret)):
            secret[index] = 0

    live_receipt = {
        "version": "gate3-live-receipt-v1", "task_id": TASK_ID,
        "lambda_ms": lambda_ms, "sql_readback_ms": sql_ms, "mcp_readback_ms": mcp_ms,
        "request_hash": request["request_hash"], "response_hash": response["response_hash"],
        "aws_request_id_hash": aws_request_id_hash, "task_hash": task_hash,
        "state_hash": state_hash, "event_hash": event_hash,
        "receipt_hash": receipt_hash, "vector_digest": vector_digest,
        "result_hash": result_hash, "projection_hash": projection_hash,
        "audit_output_hash": sha256(audit), "mcp_output_hash": sha256(mcp),
        "cloud_role": "ADVISORY", "deterministic_authority": "P4_AND_P7_LOCAL",
    }
    write_json(custody / "live-receipt.json", live_receipt)
    capture = {
        "version": "gate3-capture-v1", "task_id": TASK_ID,
        "base_commit": BASE_COMMIT, "agent_commit": AGENT_COMMIT,
        "manifest_hash": p7.sha256_hex(manifest),
        "trajectory_hash": p7.sha256_hex(trajectory),
        "decision_hash": p7.sha256_hex(decision),
        "human_edit_hash": HUMAN_HASH, "declared_work_units": 3,
        "committed_agent_units": 1, "uncommitted_agent_units": 1,
        "human_units": 1, "p4_verdicts": [list(item) for item in verdicts],
        "live_receipt_hash": sha256((custody / "live-receipt.json").read_bytes()),
        "workspace_status": list(status), "test_receipt": test_receipt,
    }
    write_json(custody / "capture-receipt.json", capture)
    print(canonical({"status": "GATE3_CAPTURE_GREEN",
                     "capture_hash": sha256((custody / "capture-receipt.json").read_bytes())}).decode())


def destroy(workspace: Path, custody: Path) -> None:
    workspace = workspace.resolve()
    custody = custody.resolve()
    expected = (REPO / ".hardening-runtime" / "gate3-real-workflow" / "workspace").resolve()
    if workspace != expected or workspace.is_symlink() or not workspace.is_dir():
        raise TraceError("LOSS_TARGET_INVALID")
    manifest = read_json(custody / "manifest.json")
    for item in manifest["files"]:
        target = safe_target(workspace, item["path"])
        if target.is_symlink() or sha256(target.read_bytes()) != item["content_hash"]:
            raise TraceError("PRELOSS_MANIFEST_DRIFT")
        obj = custody / "objects" / item["content_hash"]
        if obj.is_symlink() or sha256(obj.read_bytes()) != item["content_hash"]:
            raise TraceError("CUSTODY_OBJECT_DRIFT")
    started = time.time_ns()
    shutil.rmtree(workspace)
    if workspace.exists() or workspace.is_symlink():
        raise TraceError("LOSS_RESIDUE")
    loss = {
        "version": "gate3-loss-v1", "task_id": TASK_ID,
        "target_relative": ".hardening-runtime/gate3-real-workflow/workspace",
        "manifest_hash": p7.sha256_hex(manifest),
        "lost_paths": [item["path"] for item in manifest["files"]],
        "workspace_absent": True, "original_disposable_git_session_absent": True,
        "started_unix_ns": started, "completed_unix_ns": time.time_ns(),
        "limitation": "The orchestrating Codex conversation remained active; continuation is isolated in a fresh OS process with no conversation input.",
    }
    write_json(custody / "loss-receipt.json", loss)
    print(canonical({"status": "DECLARED_LOSS_GREEN",
                     "loss_receipt_hash": sha256((custody / "loss-receipt.json").read_bytes())}).decode())


def consume_warrant(custody: Path) -> dict[str, Any]:
    lock_path = custody / "warrant.lock"
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        state_path = custody / "warrant-state.json"
        state = read_json(state_path)
        p7.validate_warrant(state)
        if state["state"] != "ISSUED":
            raise TraceError("WARRANT_REPLAY")
        state["state"] = "CONSUMED"
        write_json(state_path, state)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    return state


def cli_acceptance(successor: Path, evidence: Path) -> dict[str, Any]:
    suite = test_suite(successor)
    first = evidence / "demo-first"
    second_fresh = evidence / "demo-fresh"
    first.mkdir(parents=True)
    first_run = run(["python3.12", "-m", "cockroach_kernel.cli", "demo",
                     "--output-root", str(first)], cwd=successor)
    require_ok(first_run, "FIRST_DEMO_FAILED")
    names = ("promotion-receipt.json", "refusal-receipt.json")
    original = {name: sha256((first / name).read_bytes()) for name in names}
    second_run = run(["python3.12", "-m", "cockroach_kernel.cli", "demo",
                      "--output-root", str(first)], cwd=successor)
    if second_run.returncode != 2 or b"REASON: OUTPUT_ALREADY_EXISTS" not in second_run.stdout:
        raise TraceError("OVERWRITE_REFUSAL_FAILED:" + sha256(second_run.stdout))
    after = {name: sha256((first / name).read_bytes()) for name in names}
    if after != original:
        raise TraceError("ORIGINAL_RECEIPT_MUTATED")
    residue = sorted(path.name for path in first.iterdir() if path.name.startswith("."))
    if residue:
        raise TraceError("TEMP_RESIDUE")
    fresh_run = run(["python3.12", "-m", "cockroach_kernel.cli", "demo",
                     "--output-root", str(second_fresh)], cwd=successor)
    require_ok(fresh_run, "FRESH_DEMO_FAILED")
    return {"suite": suite, "first_exit": first_run.returncode,
            "second_exit": second_run.returncode,
            "second_reason": "OUTPUT_ALREADY_EXISTS", "original_hashes": original,
            "post_refusal_hashes": after, "temporary_residue": residue,
            "fresh_root_exit": fresh_run.returncode,
            "first_output_hash": sha256(first_run.stdout),
            "second_output_hash": sha256(second_run.stdout),
            "fresh_output_hash": sha256(fresh_run.stdout)}


def continue_fresh(custody: Path, source: Path, successor: Path) -> None:
    continuation_started_ns = time.time_ns()
    custody, source, successor = custody.resolve(), source.resolve(), successor.resolve()
    if successor.exists() or not (custody / "loss-receipt.json").is_file():
        raise TraceError("CONTINUATION_ROOT_STATE_INVALID")
    manifest = read_json(custody / "manifest.json")
    context = read_json(custody / "context.json")
    candidate = read_json(custody / "candidate.json")
    decision = read_json(custody / "decision.json")
    p4_candidate = read_json(custody / "p4-candidate.json")
    if p7.select_candidate([candidate], context) != decision:
        raise TraceError("DECISION_DRIFT")
    p4_verdicts = [p4.verify(p4_candidate) for _ in range(5)]
    if p4_verdicts != [("PROMOTE", "VERIFIED")] * 5:
        raise TraceError("FRESH_VERIFIER_REFUSED")
    consumed = consume_warrant(custody)
    clone = run(["git", "clone", "--no-hardlinks", "--no-checkout", str(source),
                 str(successor)], timeout=180)
    require_ok(clone, "SUCCESSOR_CLONE_FAILED")
    checkout = run(["git", "-C", str(successor), "checkout", "--detach", BASE_COMMIT])
    require_ok(checkout, "BASE_CHECKOUT_FAILED")
    for item in manifest["files"]:
        obj = custody / "objects" / item["content_hash"]
        if obj.is_symlink() or sha256(obj.read_bytes()) != item["content_hash"]:
            raise TraceError("CUSTODY_OBJECT_DRIFT")
        target = safe_target(successor, item["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(obj.read_bytes())
        if sha256(target.read_bytes()) != item["content_hash"]:
            raise TraceError("SUCCESSOR_OBJECT_DRIFT")
    evidence = custody / "continuation-evidence"
    evidence.mkdir()
    acceptance = cli_acceptance(successor, evidence)
    promotion = p7.build_promotion_receipt(decision, consumed, list(DECLARED_PATHS))
    ledger = p7.make_unrecovered_ledger("ledger-g3-real-r1", manifest,
                                        list(DECLARED_PATHS))
    write_json(custody / "promotion-receipt.json", promotion)
    write_json(custody / "unrecovered-ledger.json", ledger)
    receipt = {
        "version": "gate3-fresh-continuation-v1", "task_id": TASK_ID,
        "fresh_process_pid": os.getpid(), "conversation_input": False,
        "task_restatement_required": False, "decision": decision,
        "p4_verdicts": [list(item) for item in p4_verdicts],
        "warrant_state": consumed["state"], "recovered_paths": list(DECLARED_PATHS),
        "unrecovered_items": ledger["unrecovered_items"],
        "committed_agent_unit_retained": True,
        "uncommitted_agent_unit_retained": True, "human_unit_retained": True,
        "acceptance": acceptance,
        "successor_status": git(successor, "status", "--porcelain=v1", "-uall").splitlines(),
        "lost_work": ["disposable branch name and local commit object were not recreated; their changed file bytes were retained"],
        "continuation_started_unix_ns": continuation_started_ns,
        "continuation_completed_unix_ns": time.time_ns(),
        "loss_to_verified_continuation_ms": (
            time.time_ns() - int(read_json(custody / "loss-receipt.json")["completed_unix_ns"])
        ) // 1_000_000,
    }
    write_json(custody / "continuation-receipt.json", receipt)
    print(canonical({"status": "FRESH_CONTINUATION_GREEN",
                     "receipt_hash": sha256((custody / "continuation-receipt.json").read_bytes())}).decode())


def cleanup(custody: Path, successor: Path) -> None:
    custody, successor = custody.resolve(), successor.resolve()
    expected_successor = (
        REPO / ".hardening-runtime" / "gate3-real-workflow" / "successor-r1"
    ).resolve()
    original = (
        REPO / ".hardening-runtime" / "gate3-real-workflow" / "workspace"
    ).resolve()
    if successor != expected_successor or successor.is_symlink():
        raise TraceError("CLEANUP_TARGET_INVALID")
    manifest = read_json(custody / "manifest.json")
    if successor.is_dir():
        for item in manifest["files"]:
            target = safe_target(successor, item["path"])
            if target.is_symlink() or sha256(target.read_bytes()) != item["content_hash"]:
                raise TraceError("PRECLEAN_SUCCESSOR_DRIFT")
        before = {
            "head": git(successor, "rev-parse", "HEAD"),
            "status": git(successor, "status", "--porcelain=v1", "-uall").splitlines(),
        }
        shutil.rmtree(successor)
    else:
        continuation = read_json(custody / "continuation-receipt.json")
        before = {"head": BASE_COMMIT, "status": continuation["successor_status"]}
    temporary_home = Path("/tmp/ck-g3-empty-home-20260727")
    if temporary_home.exists():
        if temporary_home.is_symlink():
            raise TraceError("TEMP_HOME_TARGET_INVALID")
        shutil.rmtree(temporary_home)
    residue = {
        "version": "gate3-residue-v1", "task_id": TASK_ID,
        "original_workspace_absent": not original.exists(),
        "successor_absent": not successor.exists(),
        "replay_successor_absent": not (
            REPO / ".hardening-runtime" / "gate3-real-workflow" / "successor-replay-r1"
        ).exists(),
        "temporary_home_absent": not temporary_home.exists(),
        "custody_preserved": custody.is_dir(),
        "live_rows_retained_as_declared_immutable_evidence": True,
        "successor_before_cleanup": before,
    }
    if not all(residue[key] for key in (
        "original_workspace_absent", "successor_absent", "replay_successor_absent",
        "temporary_home_absent", "custody_preserved")):
        raise TraceError("CLEANUP_RESIDUE")
    write_json(custody / "residue-receipt.json", residue)
    entries = []
    for path in sorted(custody.rglob("*"), key=lambda item: item.as_posix()):
        if (not path.is_file() or path.name in {"evidence-manifest.json", "warrant.lock"}
                or path.is_symlink()):
            continue
        entries.append({"path": path.relative_to(custody).as_posix(),
                        "bytes": path.stat().st_size,
                        "sha256": sha256(path.read_bytes())})
    evidence_manifest = {"version": "gate3-evidence-manifest-v1",
                         "task_id": TASK_ID, "entries": entries}
    evidence_manifest["manifest_hash"] = sha256(canonical(evidence_manifest))
    write_json(custody / "evidence-manifest.json", evidence_manifest)
    print(canonical({"status": "GATE3_CLEANUP_GREEN",
                     "residue_receipt_hash": sha256(
                         (custody / "residue-receipt.json").read_bytes()),
                     "evidence_manifest_hash": evidence_manifest["manifest_hash"]}).decode())


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--workspace", type=Path, required=True)
    prepare_parser.add_argument("--custody", type=Path, required=True)
    destroy_parser = sub.add_parser("destroy")
    destroy_parser.add_argument("--workspace", type=Path, required=True)
    destroy_parser.add_argument("--custody", type=Path, required=True)
    continue_parser = sub.add_parser("continue")
    continue_parser.add_argument("--custody", type=Path, required=True)
    continue_parser.add_argument("--source", type=Path, required=True)
    continue_parser.add_argument("--successor", type=Path, required=True)
    cleanup_parser = sub.add_parser("cleanup")
    cleanup_parser.add_argument("--custody", type=Path, required=True)
    cleanup_parser.add_argument("--successor", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.workspace, args.custody)
    elif args.command == "destroy":
        destroy(args.workspace, args.custody)
    elif args.command == "continue":
        continue_fresh(args.custody, args.source, args.successor)
    else:
        cleanup(args.custody, args.successor)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, TraceError, subprocess.TimeoutExpired) as exc:
        print(canonical({"status": "GATE3_BLOCKED", "reason": str(exc) or exc.__class__.__name__}).decode(),
              file=sys.stderr)
        raise SystemExit(2)

## Evidence: manifest.json

```json
{"files":[{"content_hash":"31a50d286d780a23c7b7789bd97b33c20ed67875278e5802175940a16d9aa4a8","executable":false,"is_symlink":false,"path":"cockroach_kernel/cli.py"},{"content_hash":"f0359d4792502109e4103b9288fafd7d0c4daf6e9d2f42890260c384b49d3756","executable":false,"is_symlink":false,"path":"cockroach_kernel/test_cli.py"},{"content_hash":"13d6838a0f987de6c2f9353e07193b7601a7a711c5f0ee15d56f0bcd4b4699e5","executable":false,"is_symlink":false,"path":"GATE3_HUMAN_ACCEPTANCE.txt"}],"manifest_id":"manifest-g3-real-r1","task_id":"ck-g3-real-workflow-r1","version":"p7-v1"}
```

## Evidence: trajectory.json

```json
{"events":[{"event":"TASK_DECLARED","event_hash":"b21a71917e3efd9264714ad10e49d003b4d8cd4f27b938b86a7c00d9d756ccec","sequence":0},{"event":"AGENT_COMMITTED","event_hash":"fb9dd0fc9c2b591d3babc0b0e87dfaa63ddbe4ea9376b5f663d92afc024d00b4","sequence":1},{"event":"AGENT_UNCOMMITTED","event_hash":"d265e2d90dbeb76cb21849bebedb91238756125cfac05289c8af9f20d07e3ade","sequence":2},{"event":"HUMAN_EDIT_SAVED","event_hash":"667bfc3e8359b2666d12726dd776e78fc10d7dea3396e63bf8354a08d10c16a8","sequence":3},{"event":"LIVE_RECORD_ARMED","event_hash":"747301216c890b5cc8ae137000bbd849075834667d1e349885fe7af27cc7d01d","sequence":4}],"manifest_hash":"112dc84805470594a0b6b6951e386fe807a98af0d47a951c6bbd618296ae92bf","receipt_id":"rcpt-g3-trajectory-r1","task_id":"ck-g3-real-workflow-r1","trajectory_hash":"a9b74e02546b8c1243f751155c865ed72cf0659e50801e22d37c71529e29c425","version":"p7-v1"}
```

## Evidence: candidate.json

```json
{"candidate_id":"cand-g3-real-r1","declared_paths":["cockroach_kernel/cli.py","cockroach_kernel/test_cli.py","GATE3_HUMAN_ACCEPTANCE.txt"],"executable_test":{"feature_hash":"f0359d4792502109e4103b9288fafd7d0c4daf6e9d2f42890260c384b49d3756","passed":true,"path":"cockroach_kernel/test_cli.py","test_id":"test-g3-cli-r1"},"file_hashes":{"GATE3_HUMAN_ACCEPTANCE.txt":"13d6838a0f987de6c2f9353e07193b7601a7a711c5f0ee15d56f0bcd4b4699e5","cockroach_kernel/cli.py":"31a50d286d780a23c7b7789bd97b33c20ed67875278e5802175940a16d9aa4a8","cockroach_kernel/test_cli.py":"f0359d4792502109e4103b9288fafd7d0c4daf6e9d2f42890260c384b49d3756"},"integrity_hash":"85ecc5951a5856cad8b694ce8987ceaacc6ec1b98152657de114b5615479d912","policy_version":"gate3-policy-r1","policy_veto":false,"prefix_length":5,"provenance":{"source":"gate3-content-addressed-custody"},"quorum_decision":{"approvals":3,"decision":"PROMOTE","reason":"GATE3_DECLARED_TRACE","refusals":0},"source_receipt_hash":"16ed0d96d489038ecf7cc2f918e393ca0b2d74c04c61bac99de6dad06b52d62d","tampered":false,"task_id":"ck-g3-real-workflow-r1","version":"p7-v1"}
```

## Evidence: context.json

```json
{"manifest":{"files":[{"content_hash":"31a50d286d780a23c7b7789bd97b33c20ed67875278e5802175940a16d9aa4a8","executable":false,"is_symlink":false,"path":"cockroach_kernel/cli.py"},{"content_hash":"f0359d4792502109e4103b9288fafd7d0c4daf6e9d2f42890260c384b49d3756","executable":false,"is_symlink":false,"path":"cockroach_kernel/test_cli.py"},{"content_hash":"13d6838a0f987de6c2f9353e07193b7601a7a711c5f0ee15d56f0bcd4b4699e5","executable":false,"is_symlink":false,"path":"GATE3_HUMAN_ACCEPTANCE.txt"}],"manifest_id":"manifest-g3-real-r1","task_id":"ck-g3-real-workflow-r1","version":"p7-v1"},"policy_version":"gate3-policy-r1","quorum_decision_hash":"ac2eb3b72b11bb15e606cedca5835941b1659a159d6d8e5947db04425a65786a","trajectory_receipt":{"events":[{"event":"TASK_DECLARED","event_hash":"b21a71917e3efd9264714ad10e49d003b4d8cd4f27b938b86a7c00d9d756ccec","sequence":0},{"event":"AGENT_COMMITTED","event_hash":"fb9dd0fc9c2b591d3babc0b0e87dfaa63ddbe4ea9376b5f663d92afc024d00b4","sequence":1},{"event":"AGENT_UNCOMMITTED","event_hash":"d265e2d90dbeb76cb21849bebedb91238756125cfac05289c8af9f20d07e3ade","sequence":2},{"event":"HUMAN_EDIT_SAVED","event_hash":"667bfc3e8359b2666d12726dd776e78fc10d7dea3396e63bf8354a08d10c16a8","sequence":3},{"event":"LIVE_RECORD_ARMED","event_hash":"747301216c890b5cc8ae137000bbd849075834667d1e349885fe7af27cc7d01d","sequence":4}],"manifest_hash":"112dc84805470594a0b6b6951e386fe807a98af0d47a951c6bbd618296ae92bf","receipt_id":"rcpt-g3-trajectory-r1","task_id":"ck-g3-real-workflow-r1","trajectory_hash":"a9b74e02546b8c1243f751155c865ed72cf0659e50801e22d37c71529e29c425","version":"p7-v1"}}
```

## Evidence: decision.json

```json
{"candidate_id":"cand-g3-real-r1","candidates_hash":"46942d37dcd829b4e8e9583954083bf73a183e07d283e5247aff9920e252c737","decision":"PROMOTE","reason":"MAX_PROVEN_PREFIX","task_id":"ck-g3-real-workflow-r1","version":"p7-v1"}
```

## Evidence: warrant.json

```json
{"candidate_id":"cand-g3-real-r1","decision_hash":"452a35a89c52a5a432edf992c5c7ea860fe32b871ebd80154c80d29cc83ad6ec","state":"ISSUED","task_id":"ck-g3-real-workflow-r1","version":"p7-v1","warrant_id":"warrant-g3-real-r1"}
```

## Evidence: capture-receipt.json

```json
{"agent_commit":"f8b2e5d7e15352bf2762bd000875a85a0b56a75b","base_commit":"ba1217c4d830a3c7633e352c0e10712d6b817cee","committed_agent_units":1,"decision_hash":"452a35a89c52a5a432edf992c5c7ea860fe32b871ebd80154c80d29cc83ad6ec","declared_work_units":3,"human_edit_hash":"13d6838a0f987de6c2f9353e07193b7601a7a711c5f0ee15d56f0bcd4b4699e5","human_units":1,"live_receipt_hash":"4ef1c44450f694763d971b1ce5cf5ee48c6f5c032c4ca4abbbdc2cf5838f2ff3","manifest_hash":"112dc84805470594a0b6b6951e386fe807a98af0d47a951c6bbd618296ae92bf","p4_verdicts":[["PROMOTE","VERIFIED"],["PROMOTE","VERIFIED"],["PROMOTE","VERIFIED"],["PROMOTE","VERIFIED"],["PROMOTE","VERIFIED"]],"task_id":"ck-g3-real-workflow-r1","test_receipt":{"command":"python3.12 -m unittest cockroach_kernel.test_cli cockroach_kernel.test_http_api","elapsed_ms":148,"exit_status":0,"output_sha256":"b957e608ed1516a2a6645519bfd76f885dc919ebb9359dcf73d422cb17d40281"},"trajectory_hash":"16ed0d96d489038ecf7cc2f918e393ca0b2d74c04c61bac99de6dad06b52d62d","uncommitted_agent_units":1,"version":"gate3-capture-v1","workspace_status":[" M cockroach_kernel/test_cli.py","?? GATE3_HUMAN_ACCEPTANCE.txt"]}
```

## Evidence: live-receipt.json

```json
{"audit_output_hash":"9ecb5cb1f5e026422fbba98170a062b4fcf3672416aa9ff8097f802651ab5f09","aws_request_id_hash":"4189bc41a47e1c6d61faf2e5e9868b573e432befd82266f8fe386a5cb01cdfe6","cloud_role":"ADVISORY","deterministic_authority":"P4_AND_P7_LOCAL","event_hash":"f04153635eaf86a1d28b953781153a52628204a387cf2fb5b50249318d0ddbc7","lambda_ms":1121,"mcp_output_hash":"bbe8aa288f67beb2df5fd5753cf36df7808df90cc16cccd81ed739ecb5fe4691","mcp_readback_ms":452,"projection_hash":"90c143eca6463db2d1aa3b951184a3d3e5ed949e38531c49d5208e2590a07d1e","receipt_hash":"e6a01d9ff6713f5404cf11577a499b49ecd5e45b546e813d2008beb40acdfd63","request_hash":"4d4ac9092fedbd33856bf53a333cb9be88b057e073a352f8c355454f06175772","response_hash":"e4e66491093185244aef97fb61ce5a68e671703adb70cfc98e7de8505559122d","result_hash":"cd7271f00e2e31b21e5a929edd8787b11e63a9e3217fa23fc47cd8befc7a77bc","sql_readback_ms":457,"state_hash":"085ae687379bbd387715cd1cedef905122fcd1cfd8366b988d12ad480fa2dbf7","task_hash":"3d8453023ad08f40aef3344f2c1d747cbb7ba685f82d8a1a3efc2135e3ef3c5e","task_id":"ck-g3-real-workflow-r1","vector_digest":"d561a0e576d3dfde031b013df99cb386a51739b10be07babcfcd29e5fc3269f7","version":"gate3-live-receipt-v1"}
```

## Evidence: loss-receipt.json

```json
{"completed_unix_ns":1785181536562909000,"limitation":"The orchestrating Codex conversation remained active; continuation is isolated in a fresh OS process with no conversation input.","lost_paths":["cockroach_kernel/cli.py","cockroach_kernel/test_cli.py","GATE3_HUMAN_ACCEPTANCE.txt"],"manifest_hash":"112dc84805470594a0b6b6951e386fe807a98af0d47a951c6bbd618296ae92bf","original_disposable_git_session_absent":true,"started_unix_ns":1785181536348166000,"target_relative":".hardening-runtime/gate3-real-workflow/workspace","task_id":"ck-g3-real-workflow-r1","version":"gate3-loss-v1","workspace_absent":true}
```

## Evidence: continuation-receipt.json

```json
{"acceptance":{"first_exit":0,"first_output_hash":"4d6f369f19b6e4264916bb7355a78149298837b2343e32fd3e78d5fcfc44764c","fresh_output_hash":"15afea909617b18cce5f8c37952d051a8092cb7a117be7f0afea8482f525ffc5","fresh_root_exit":0,"original_hashes":{"promotion-receipt.json":"eb1ea7a909b0cab76e8e7ef711c9dfe493affdf7f420ff43066fc75d525965bc","refusal-receipt.json":"f94310e76ffc8c99c335e577f14117fe017dc277658fed0f0d79e8ef13404afd"},"post_refusal_hashes":{"promotion-receipt.json":"eb1ea7a909b0cab76e8e7ef711c9dfe493affdf7f420ff43066fc75d525965bc","refusal-receipt.json":"f94310e76ffc8c99c335e577f14117fe017dc277658fed0f0d79e8ef13404afd"},"second_exit":2,"second_output_hash":"4ac60ec878a088ec368fef2c955fc046b664e086bb77651727956116f2dba3d0","second_reason":"OUTPUT_ALREADY_EXISTS","suite":{"command":"python3.12 -m unittest cockroach_kernel.test_cli cockroach_kernel.test_http_api","elapsed_ms":95,"exit_status":0,"output_sha256":"8ee6bb02fad2699fdaa1db4705f9e7c4a7fe3bdb709c76eb4936f891cfee8eab"},"temporary_residue":[]},"committed_agent_unit_retained":true,"continuation_completed_unix_ns":1785181560544739000,"continuation_started_unix_ns":1785181559631942000,"conversation_input":false,"decision":{"candidate_id":"cand-g3-real-r1","candidates_hash":"46942d37dcd829b4e8e9583954083bf73a183e07d283e5247aff9920e252c737","decision":"PROMOTE","reason":"MAX_PROVEN_PREFIX","task_id":"ck-g3-real-workflow-r1","version":"p7-v1"},"fresh_process_pid":17946,"human_unit_retained":true,"loss_to_verified_continuation_ms":23981,"lost_work":["disposable branch name and local commit object were not recreated; their changed file bytes were retained"],"p4_verdicts":[["PROMOTE","VERIFIED"],["PROMOTE","VERIFIED"],["PROMOTE","VERIFIED"],["PROMOTE","VERIFIED"],["PROMOTE","VERIFIED"]],"recovered_paths":["cockroach_kernel/cli.py","cockroach_kernel/test_cli.py","GATE3_HUMAN_ACCEPTANCE.txt"],"successor_status":[" M cockroach_kernel/cli.py"," M cockroach_kernel/test_cli.py","?? GATE3_HUMAN_ACCEPTANCE.txt"],"task_id":"ck-g3-real-workflow-r1","task_restatement_required":false,"uncommitted_agent_unit_retained":true,"unrecovered_items":[],"version":"gate3-fresh-continuation-v1","warrant_state":"CONSUMED"}
```

## Evidence: promotion-receipt.json

```json
{"candidate_id":"cand-g3-real-r1","decision_hash":"452a35a89c52a5a432edf992c5c7ea860fe32b871ebd80154c80d29cc83ad6ec","promoted_paths":["GATE3_HUMAN_ACCEPTANCE.txt","cockroach_kernel/cli.py","cockroach_kernel/test_cli.py"],"receipt_hash":"1c00d190614c1a6557d5dd63253e8878b3662c8102277e5f60080570d4ce84bb","receipt_id":"rcpt-1c00d190614c1a6557d5dd63253e8878","task_id":"ck-g3-real-workflow-r1","version":"p7-v1","warrant_id":"warrant-g3-real-r1"}
```

## Evidence: unrecovered-ledger.json

```json
{"ledger_id":"ledger-g3-real-r1","manifest_hash":"112dc84805470594a0b6b6951e386fe807a98af0d47a951c6bbd618296ae92bf","recovered_paths":["GATE3_HUMAN_ACCEPTANCE.txt","cockroach_kernel/cli.py","cockroach_kernel/test_cli.py"],"task_id":"ck-g3-real-workflow-r1","unrecovered_items":[],"version":"p7-v1"}
```

## Evidence: residue-receipt.json

```json
{"custody_preserved":true,"live_rows_retained_as_declared_immutable_evidence":true,"original_workspace_absent":true,"replay_successor_absent":true,"successor_absent":true,"successor_before_cleanup":{"head":"ba1217c4d830a3c7633e352c0e10712d6b817cee","status":[" M cockroach_kernel/cli.py"," M cockroach_kernel/test_cli.py","?? GATE3_HUMAN_ACCEPTANCE.txt"]},"task_id":"ck-g3-real-workflow-r1","temporary_home_absent":true,"version":"gate3-residue-v1"}
```

## Evidence: evidence-manifest.json

```json
{"entries":[{"bytes":1098,"path":"candidate.json","sha256":"896a38012fd2248b456972c1d456ee4684a64a5549e04a3e51b1bc505410bcaf"},{"bytes":1141,"path":"capture-receipt.json","sha256":"c4ae85a6ef201d98f2079b077f0d86784c905cb93539128d2bee371b8d326ee0"},{"bytes":1612,"path":"context.json","sha256":"6998156a9b5b641ee7952690f38318f4877e1324ec782eba4723adf1cdfc30b4"},{"bytes":851,"path":"continuation-evidence/demo-first/promotion-receipt.json","sha256":"eb1ea7a909b0cab76e8e7ef711c9dfe493affdf7f420ff43066fc75d525965bc"},{"bytes":756,"path":"continuation-evidence/demo-first/refusal-receipt.json","sha256":"f94310e76ffc8c99c335e577f14117fe017dc277658fed0f0d79e8ef13404afd"},{"bytes":851,"path":"continuation-evidence/demo-fresh/promotion-receipt.json","sha256":"eb1ea7a909b0cab76e8e7ef711c9dfe493affdf7f420ff43066fc75d525965bc"},{"bytes":756,"path":"continuation-evidence/demo-fresh/refusal-receipt.json","sha256":"f94310e76ffc8c99c335e577f14117fe017dc277658fed0f0d79e8ef13404afd"},{"bytes":2187,"path":"continuation-receipt.json","sha256":"cb2bcc1df56f6a88276b2a685fc9f3bc5e30816bb54d151091364d384d06a050"},{"bytes":223,"path":"decision.json","sha256":"4e304799d543b620dec385b2de440d2a680d1092f62b09f378f2c159185c3e29"},{"bytes":629,"path":"lambda-request.json","sha256":"a685ad33b42b5800c45cda103cf883bfd7e8766b76b0de47f48fa1b3a7752c6f"},{"bytes":594,"path":"lambda-response.json","sha256":"d3f9802adad8f9c46533959573d43c62be8700a4083e86a639a1d27f500094d5"},{"bytes":1196,"path":"live-receipt.json","sha256":"4ef1c44450f694763d971b1ce5cf5ee48c6f5c032c4ca4abbbdc2cf5838f2ff3"},{"bytes":608,"path":"loss-receipt.json","sha256":"0d1b614458234496784c31f91cfe0474887fb4a0f5b4eca226fab5444999e9ba"},{"bytes":574,"path":"manifest.json","sha256":"61e7330a71b296a3a371b0f8fa2d415df511bff72fb1922247b94ae9f79ed7de"},{"bytes":140,"path":"objects/13d6838a0f987de6c2f9353e07193b7601a7a711c5f0ee15d56f0bcd4b4699e5","sha256":"13d6838a0f987de6c2f9353e07193b7601a7a711c5f0ee15d56f0bcd4b4699e5"},{"bytes":12097,"path":"objects/31a50d286d780a23c7b7789bd97b33c20ed67875278e5802175940a16d9aa4a8","sha256":"31a50d286d780a23c7b7789bd97b33c20ed67875278e5802175940a16d9aa4a8"},{"bytes":5938,"path":"objects/f0359d4792502109e4103b9288fafd7d0c4daf6e9d2f42890260c384b49d3756","sha256":"f0359d4792502109e4103b9288fafd7d0c4daf6e9d2f42890260c384b49d3756"},{"bytes":868,"path":"p4-candidate.json","sha256":"2c6f8b3182ac57b9721d5eb63faaa69cdb1218415ada9f9761d3dd28aec3caad"},{"bytes":210,"path":"pre-capture-test.json","sha256":"9a72285a88bfff1bcabbdf36651a7402d9389c9e89fedf0ce0b305159efd545b"},{"bytes":445,"path":"promotion-receipt.json","sha256":"5285f6ed7ef05beb50857425681991e5e59feb6651bd952976c73719cdeb6ece"},{"bytes":53,"path":"replay-attempt.stdout","sha256":"1c24d3bde0440fb8f30071f8f67d638b5a121d5c7caf31dfd049feff13b52526"},{"bytes":450,"path":"residue-receipt.json","sha256":"03be225cf64c4a741e683b3f725725be97372c22e1740b58f6901ee254162249"},{"bytes":879,"path":"trajectory.json","sha256":"7a0f4d24735545b6fec2b0e0f68690a332dcba7bdcdfacab2ba90c46d67202a2"},{"bytes":299,"path":"unrecovered-ledger.json","sha256":"27e94eb55f9e597d124e84a4af068ce579a0770a26565a38565acc701f23636b"},{"bytes":224,"path":"warrant-state.json","sha256":"6cbe52744f5d8e614b69fd0f24dbc956ad37c9fa2e86821fb7592ba90106e299"},{"bytes":222,"path":"warrant.json","sha256":"ad792387ae12496e5f21582d10b349641afa0ae24c011653418b30d75e5ec27d"}],"manifest_hash":"bdb98a84fc39da166c2bd071249f5491b60be6763b9a8d56b7104368ec2b487e","task_id":"ck-g3-real-workflow-r1","version":"gate3-evidence-manifest-v1"}
```

## Recovered source: cockroach_kernel/cli.py

```python
"""Thin CLI facade over the frozen P9 keyless replay and P4 verifier."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Sequence


MAX_RECEIPT_BYTES = 65_536
RECEIPT_VERSION = "ck-cli-receipt-v1"
OUTPUT_LOCK_NAME = ".cockroach-kernel-demo.lock"
RECEIPT_FIELDS = {
    "version",
    "replay_label",
    "branch",
    "verdict",
    "reason",
    "provable_state",
    "action_taken",
    "next_safe_action",
    "source_result_hash",
    "source_receipt_hash",
    "fresh_context_continued",
    "fresh_context_reason",
    "receipt_hash",
}


def _runtime() -> Any:
    """Import the packaged P9 runtime without changing its authority logic."""
    try:
        import p9_runtime

        runtime_path = Path(p9_runtime.__file__).resolve().parent
    except ModuleNotFoundError:
        runtime_path = Path(__file__).resolve().parents[1] / "p9-cloud"
        if not runtime_path.is_dir():
            raise RuntimeError("P9_RUNTIME_UNAVAILABLE")
    runtime_dir = str(runtime_path)
    if runtime_dir not in sys.path:
        sys.path.insert(0, runtime_dir)
    import run_offline

    return run_offline


def canonical_json(value: Any) -> bytes:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("RECEIPT_MALFORMED") from exc
    if len(raw) > MAX_RECEIPT_BYTES:
        raise ValueError("RECEIPT_TOO_LARGE")
    return raw


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
    return hashlib.sha256(raw).hexdigest()


def _receipt_body(result: dict[str, Any], branch: str) -> dict[str, Any]:
    if branch == "promote":
        verdict = result["local_verdict"]
        reason = result["local_reason"]
        continued = result["fresh_context"]
        fresh_reason = result["fresh_context_reason"]
        action = "VERIFIED_CONTINUATION_RECONSTRUCTED"
        next_action = "Inspect the canonical receipt or continue from the verified capsule."
        state = {
            "capsule_hash": result["capsule_hash"],
            "declared_hash": result["declared_hash"],
            "projection_state": result["projection_state"],
            "task_id": result["task_id"],
        }
    elif branch == "refuse":
        verdict = result["tampered_verdict"]
        reason = result["tampered_reason"]
        continued = False
        fresh_reason = "CAPSULE_NOT_PROMOTED"
        action = "NONE"
        next_action = "Inspect the receipt and provide an untampered declared candidate."
        state = {
            "declared_hash": result["declared_hash"],
            "rejected_candidate": "tampered_replay_vector",
            "task_id": result["task_id"],
        }
    else:
        raise ValueError("BRANCH_INVALID")
    return {
        "version": RECEIPT_VERSION,
        "replay_label": "KEYLESS_LOCAL_REPLAY",
        "branch": branch,
        "verdict": verdict,
        "reason": reason,
        "provable_state": state,
        "action_taken": action,
        "next_safe_action": next_action,
        "source_result_hash": result["result_hash"],
        "source_receipt_hash": result["receipt_hash"],
        "fresh_context_continued": continued,
        "fresh_context_reason": fresh_reason,
    }


def make_receipt(result: dict[str, Any], branch: str) -> dict[str, Any]:
    body = _receipt_body(result, branch)
    receipt = dict(body, receipt_hash=digest(body))
    validate_receipt(receipt)
    return receipt


def validate_receipt(receipt: Any) -> dict[str, Any]:
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_FIELDS:
        raise ValueError("RECEIPT_FIELDS_INVALID")
    if receipt["version"] != RECEIPT_VERSION:
        raise ValueError("RECEIPT_VERSION_UNSUPPORTED")
    if receipt["replay_label"] != "KEYLESS_LOCAL_REPLAY":
        raise ValueError("REPLAY_LABEL_INVALID")
    if receipt["branch"] not in {"promote", "refuse"}:
        raise ValueError("RECEIPT_BRANCH_INVALID")
    if receipt["verdict"] not in {"PROMOTE", "REFUSE", "INVALID"}:
        raise ValueError("RECEIPT_VERDICT_INVALID")
    expected = "PROMOTE" if receipt["branch"] == "promote" else "REFUSE"
    if receipt["verdict"] != expected:
        raise ValueError("RECEIPT_BRANCH_VERDICT_MISMATCH")
    if not isinstance(receipt["reason"], str) or not receipt["reason"]:
        raise ValueError("RECEIPT_REASON_INVALID")
    if not isinstance(receipt["provable_state"], dict):
        raise ValueError("RECEIPT_STATE_INVALID")
    if receipt["branch"] == "refuse" and receipt["action_taken"] != "NONE":
        raise ValueError("REFUSAL_ACTION_INVALID")
    for key in ("source_result_hash", "source_receipt_hash", "receipt_hash"):
        value = receipt[key]
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError("RECEIPT_HASH_INVALID")
        try:
            int(value, 16)
        except ValueError as exc:
            raise ValueError("RECEIPT_HASH_INVALID") from exc
    body = {key: receipt[key] for key in receipt if key != "receipt_hash"}
    if receipt["receipt_hash"] != digest(body):
        raise ValueError("RECEIPT_HASH_MISMATCH")
    canonical_json(receipt)
    return receipt


def _atomic_write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink() or (path.exists() and path.is_symlink()):
        raise ValueError("OUTPUT_SYMLINK_REFUSED")
    if path.exists():
        raise ValueError("OUTPUT_ALREADY_EXISTS")
    raw = canonical_json(value) + b"\n"
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as exc:
            raise ValueError("OUTPUT_ALREADY_EXISTS") from exc
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def _write_receipt_set(output_root: Path, receipts: dict[str, dict[str, Any]]) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    if output_root.is_symlink() or not output_root.is_dir():
        raise ValueError("OUTPUT_ROOT_INVALID")
    lock_path = output_root / OUTPUT_LOCK_NAME
    try:
        lock_descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError("OUTPUT_BUSY") from exc
    created: list[Path] = []
    try:
        os.close(lock_descriptor)
        targets = {name: output_root / name for name in receipts}
        if any(path.exists() or path.is_symlink() for path in targets.values()):
            raise ValueError("OUTPUT_ALREADY_EXISTS")
        for name, value in receipts.items():
            target = targets[name]
            _atomic_write_new(target, value)
            created.append(target)
    except Exception:
        for target in reversed(created):
            if target.is_file() and not target.is_symlink():
                target.unlink()
        raise
    finally:
        if lock_path.is_file() and not lock_path.is_symlink():
            lock_path.unlink()
        directory = os.open(output_root, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)


def run_demo(output_root: Path) -> dict[str, Any]:
    result = _runtime().run()
    promotion = make_receipt(result, "promote")
    refusal = make_receipt(result, "refuse")
    _write_receipt_set(
        output_root,
        {
            "promotion-receipt.json": promotion,
            "refusal-receipt.json": refusal,
        },
    )
    summary = {
        "version": "ck-cli-demo-v1",
        "replay_label": "KEYLESS_LOCAL_REPLAY",
        "network_used": False,
        "credentials_used": False,
        "promotion": promotion,
        "promotion_receipt": "promotion-receipt.json",
        "refusal": refusal,
        "refusal_receipt": "refusal-receipt.json",
        "source_result_hash": result["result_hash"],
    }
    summary["summary_hash"] = digest(summary)
    return summary


def _format_block(label: str, receipt: dict[str, Any], receipt_path: str) -> list[str]:
    state = canonical_json(receipt["provable_state"]).decode("utf-8")
    return [
        label,
        f"VERDICT: {receipt['verdict']}",
        f"REASON: {receipt['reason']}",
        f"PROVABLE_STATE: {state}",
        f"ACTION_TAKEN: {receipt['action_taken']}",
        f"NEXT_SAFE_ACTION: {receipt['next_safe_action']}",
        f"RECEIPT: {receipt_path}",
    ]


def _demo_command(args: argparse.Namespace) -> int:
    output_root = Path(args.output_root).resolve()
    summary = run_demo(output_root)
    if args.json:
        print(canonical_json(summary).decode("utf-8"))
        return 0
    lines = ["MODE: KEYLESS_LOCAL_REPLAY"]
    lines.extend(
        _format_block(
            "PROMOTION",
            summary["promotion"],
            str(output_root / summary["promotion_receipt"]),
        )
    )
    lines.extend(
        _format_block(
            "REFUSAL",
            summary["refusal"],
            str(output_root / summary["refusal_receipt"]),
        )
    )
    if args.explain:
        lines.extend(
            [
                "AUTHORITY: deterministic local P4 verifier",
                "CLOUD_ROLE: captured advisory evidence only",
                "NETWORK_USED: false",
                "CREDENTIALS_USED: false",
                f"SOURCE_RESULT_HASH: {summary['source_result_hash']}",
                f"SUMMARY_HASH: {summary['summary_hash']}",
            ]
        )
    print("\n".join(lines))
    return 0


def _inspect_command(args: argparse.Namespace) -> int:
    path = Path(args.receipt)
    if path.is_symlink() or not path.is_file():
        raise ValueError("RECEIPT_PATH_INVALID")
    raw = path.read_bytes()
    if len(raw) > MAX_RECEIPT_BYTES + 1:
        raise ValueError("RECEIPT_TOO_LARGE")
    if not raw.endswith(b"\n"):
        raise ValueError("RECEIPT_NOT_CANONICAL")
    try:
        receipt = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("RECEIPT_JSON_INVALID") from exc
    validate_receipt(receipt)
    if raw != canonical_json(receipt) + b"\n":
        raise ValueError("RECEIPT_NOT_CANONICAL")
    print(canonical_json(receipt).decode("utf-8"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cockroach-kernel")
    subcommands = parser.add_subparsers(dest="command", required=True)
    demo = subcommands.add_parser("demo", help="run the deterministic keyless replay")
    format_group = demo.add_mutually_exclusive_group()
    format_group.add_argument("--explain", action="store_true")
    format_group.add_argument("--json", action="store_true")
    demo.add_argument("--output-root", default="cockroach-kernel-evidence")
    demo.set_defaults(handler=_demo_command)
    inspect = subcommands.add_parser("inspect", help="validate a canonical receipt")
    inspect.add_argument("receipt")
    inspect.set_defaults(handler=_inspect_command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, ValueError, RuntimeError) as exc:
        code = str(exc) or exc.__class__.__name__
        print(f"VERDICT: INVALID\nREASON: {code}\nACTION_TAKEN: NONE", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

```

## Recovered source: cockroach_kernel/test_cli.py

```python
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from cockroach_kernel import cli


class CliTests(unittest.TestCase):
    def test_demo_writes_promotion_and_refusal_receipts(self):
        with tempfile.TemporaryDirectory() as root:
            result = cli.run_demo(Path(root))
            promotion = json.loads((Path(root) / "promotion-receipt.json").read_bytes())
            refusal = json.loads((Path(root) / "refusal-receipt.json").read_bytes())
        self.assertEqual(result["replay_label"], "KEYLESS_LOCAL_REPLAY")
        self.assertEqual(promotion["verdict"], "PROMOTE")
        self.assertEqual(promotion["reason"], "VERIFIED")
        self.assertTrue(promotion["fresh_context_continued"])
        self.assertEqual(refusal["verdict"], "REFUSE")
        self.assertEqual(refusal["reason"], "HASH_MISMATCH")
        self.assertEqual(refusal["action_taken"], "NONE")

    def test_receipts_are_byte_identical_across_fresh_roots(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            cli.run_demo(Path(first))
            cli.run_demo(Path(second))
            for name in ("promotion-receipt.json", "refusal-receipt.json"):
                self.assertEqual((Path(first) / name).read_bytes(), (Path(second) / name).read_bytes())

    def test_default_output_contains_structured_refusal_contract(self):
        with tempfile.TemporaryDirectory() as root, contextlib.redirect_stdout(io.StringIO()) as out:
            status = cli.main(["demo", "--output-root", root])
        self.assertEqual(status, 0)
        text = out.getvalue()
        self.assertIn("MODE: KEYLESS_LOCAL_REPLAY", text)
        self.assertIn("VERDICT: REFUSE", text)
        self.assertIn("REASON: HASH_MISMATCH", text)
        self.assertIn("ACTION_TAKEN: NONE", text)
        self.assertIn("NEXT_SAFE_ACTION:", text)
        self.assertIn("RECEIPT:", text)

    def test_json_output_is_canonical_and_has_no_network_or_credentials(self):
        with tempfile.TemporaryDirectory() as root, contextlib.redirect_stdout(io.StringIO()) as out:
            status = cli.main(["demo", "--json", "--output-root", root])
        self.assertEqual(status, 0)
        raw = out.getvalue().rstrip("\n").encode("utf-8")
        parsed = json.loads(raw)
        self.assertEqual(raw, cli.canonical_json(parsed))
        self.assertFalse(parsed["network_used"])
        self.assertFalse(parsed["credentials_used"])

    def test_inspect_validates_canonical_receipt(self):
        with tempfile.TemporaryDirectory() as root:
            cli.run_demo(Path(root))
            receipt = Path(root) / "refusal-receipt.json"
            with contextlib.redirect_stdout(io.StringIO()) as out:
                status = cli.main(["inspect", str(receipt)])
            self.assertEqual(status, 0)
            self.assertEqual(json.loads(out.getvalue()), json.loads(receipt.read_bytes()))

    def test_inspect_rejects_tamper_without_action(self):
        with tempfile.TemporaryDirectory() as root:
            cli.run_demo(Path(root))
            receipt = Path(root) / "refusal-receipt.json"
            record = json.loads(receipt.read_bytes())
            record["reason"] = "VERIFIED"
            receipt.write_bytes(cli.canonical_json(record) + b"\n")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                status = cli.main(["inspect", str(receipt)])
        self.assertEqual(status, 2)
        self.assertIn("VERDICT: INVALID", stderr.getvalue())
        self.assertIn("REASON: RECEIPT_HASH_MISMATCH", stderr.getvalue())
        self.assertIn("ACTION_TAKEN: NONE", stderr.getvalue())

    def test_demo_refuses_to_overwrite_existing_receipts(self):
        with tempfile.TemporaryDirectory() as root:
            first_status = cli.main(["demo", "--output-root", root])
            self.assertEqual(first_status, 0)
            before = {
                name: (Path(root) / name).read_bytes()
                for name in ("promotion-receipt.json", "refusal-receipt.json")
            }
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                second_status = cli.main(["demo", "--output-root", root])
            after = {
                name: (Path(root) / name).read_bytes()
                for name in ("promotion-receipt.json", "refusal-receipt.json")
            }
            residue = [path.name for path in Path(root).iterdir() if path.name.startswith(".")]
        self.assertEqual(second_status, 2)
        self.assertIn("VERDICT: INVALID", stderr.getvalue())
        self.assertIn("REASON: OUTPUT_ALREADY_EXISTS", stderr.getvalue())
        self.assertIn("ACTION_TAKEN: NONE", stderr.getvalue())
        self.assertEqual(after, before)
        self.assertEqual(residue, [])

    def test_partial_receipt_set_refuses_without_creating_a_sibling(self):
        names = ("promotion-receipt.json", "refusal-receipt.json")
        for existing, absent in (names, tuple(reversed(names))):
            with self.subTest(existing=existing), tempfile.TemporaryDirectory() as root:
                sentinel = b"preexisting-evidence\n"
                (Path(root) / existing).write_bytes(sentinel)
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    status = cli.main(["demo", "--output-root", root])
                residue = [path.name for path in Path(root).iterdir() if path.name.startswith(".")]
                self.assertEqual(status, 2)
                self.assertIn("REASON: OUTPUT_ALREADY_EXISTS", stderr.getvalue())
                self.assertEqual((Path(root) / existing).read_bytes(), sentinel)
                self.assertFalse((Path(root) / absent).exists())
                self.assertEqual(residue, [])


if __name__ == "__main__":
    unittest.main()

```
