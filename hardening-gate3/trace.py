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
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.workspace, args.custody)
    elif args.command == "destroy":
        destroy(args.workspace, args.custody)
    else:
        continue_fresh(args.custody, args.source, args.successor)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, TraceError, subprocess.TimeoutExpired) as exc:
        print(canonical({"status": "GATE3_BLOCKED", "reason": str(exc) or exc.__class__.__name__}).decode(),
              file=sys.stderr)
        raise SystemExit(2)
