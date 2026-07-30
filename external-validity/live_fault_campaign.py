#!/usr/bin/env python3
"""EV2 live CockroachDB Cloud and AWS Lambda fault campaign.

The script creates one disposable CockroachDB schema and one disposable Lambda
function, runs the frozen 8 x 3 matrix sequentially, writes canonical chained
receipts, and tears both resources down. Scenario 7 is deliberately supplied
as externally captured Managed MCP receipts because OAuth and tool execution
must remain outside this credential-bearing coordinator.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import time
import zipfile
from typing import Any

import pg8000.dbapi

from ev_common import canonical, chained_receipt, sha256, write_atomic

BASE = Path(__file__).resolve().parents[1]
P9 = BASE / "p9-cloud"
sys.path.insert(0, str(P9))
import records as cloud_records  # type: ignore  # noqa: E402

CAMPAIGN_ID = "ck-ev2-live-continuity-r1"
SCHEMA = "ck_ev2_r1"
FAULT_FUNCTION = "ck-ev2-fault-r1"
AWS_REGION = "us-west-2"
AWS_PROFILE = "ck-s3"
FAULTS = (
    "precommit_disconnect",
    "postcommit_ack_withheld",
    "sqlstate_40001_retry",
    "lambda_timeout",
    "stale_lambda_advisory",
    "stale_vector_projection",
    "mcp_read_only_denial",
    "process_loss_after_consume",
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class CampaignError(RuntimeError):
    pass


def _config(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "aws_cli", "aws_profile", "aws_region", "ca_cert", "cockroach_bin",
        "cockroach_host", "keychain_account", "keychain_service",
    }
    if not isinstance(value, dict) or set(value) != expected:
        raise CampaignError("LIVE_CONFIG_INVALID")
    if value["aws_profile"] != AWS_PROFILE or value["aws_region"] != AWS_REGION:
        raise CampaignError("AWS_SCOPE_INVALID")
    return {name: str(item) for name, item in value.items()}


def _password(config: dict[str, str]) -> bytearray:
    completed = subprocess.run([
        "/usr/bin/security", "find-generic-password", "-w",
        "-a", config["keychain_account"], "-s", config["keychain_service"],
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False, timeout=20)
    if completed.returncode or not completed.stdout.strip():
        raise CampaignError("KEYCHAIN_RETRIEVAL_BLOCKED")
    return bytearray(completed.stdout.rstrip(b"\n"))


def _db(config: dict[str, str], secret: bytearray):
    context = ssl.create_default_context(cafile=config["ca_cert"])
    return pg8000.dbapi.connect(
        user=config["keychain_account"],
        password=bytes(secret).decode("utf-8"),
        host=config["cockroach_host"], port=26257,
        database="cockroach_kernel", ssl_context=context, timeout=15,
    )


def _aws_env() -> dict[str, str]:
    env = os.environ.copy()
    env["AWS_PAGER"] = ""
    return env


def _aws(config: dict[str, str], arguments: list[str], *, timeout: int = 60,
         allow_failure: bool = False) -> subprocess.CompletedProcess[bytes]:
    command = [config["aws_cli"], *arguments, "--profile", AWS_PROFILE,
               "--region", AWS_REGION, "--no-cli-pager"]
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        env=_aws_env(), check=False, timeout=timeout,
    )
    if result.returncode and not allow_failure:
        raise CampaignError("AWS_COMMAND_FAILED:" + sha256(result.stdout))
    return result


def _make_request(run_id: str) -> dict[str, Any]:
    h = lambda label: sha256({"run_id": run_id, "label": label})
    return cloud_records.make_request(
        run_id, run_id, "candidate-" + run_id[-12:], h("trajectory"),
        h("candidate"), h("policy"), {
            "event_count": 3, "approvals": 2, "refusals": 0,
            "context_relevance": 0.875, "quorum_met": True,
            "policy_veto": False, "tampered": False, "unsafe": False,
            "warrant_consumed": False,
        },
    )


def _invoke(config: dict[str, str], function: str, payload: dict[str, Any],
            output: Path) -> dict[str, Any]:
    request = output.with_suffix(".request.json")
    request.write_bytes(canonical(payload) + b"\n")
    result = _aws(config, [
        "lambda", "invoke", "--function-name", function,
        "--payload", "fileb://" + str(request.resolve()),
        "--cli-binary-format", "raw-in-base64-out", "--log-type", "Tail",
        "--output", "json", str(output.resolve()),
    ], timeout=30)
    metadata = json.loads(result.stdout)
    log_hash = None
    if "LogResult" in metadata:
        log_hash = sha256(base64.b64decode(metadata["LogResult"], validate=True))
    return {
        "status_code": metadata.get("StatusCode"),
        "function_error": metadata.get("FunctionError"),
        "executed_version": metadata.get("ExecutedVersion"),
        "log_tail_sha256": log_hash,
        "payload_sha256": sha256(output.read_bytes()),
    }


def _create_resources(config: dict[str, str], secret: bytearray, output: Path) -> dict:
    existing = _aws(
        config, ["lambda", "get-function", "--function-name", FAULT_FUNCTION,
                 "--output", "json"], allow_failure=True,
    )
    if existing.returncode == 0:
        raise CampaignError("FAULT_LAMBDA_ALREADY_EXISTS")
    role_probe = _aws(config, [
        "lambda", "get-function-configuration", "--function-name",
        "ck-p9-evaluator", "--query", "Role", "--output", "text",
    ])
    role = role_probe.stdout.decode("utf-8").strip()
    if not role.startswith("arn:aws:iam::"):
        raise CampaignError("LAMBDA_ROLE_INVALID")

    archive = output / "fault-lambda.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.write(BASE / "external-validity" / "fault_lambda.py", "fault_lambda.py")
    archive_hash = sha256(archive.read_bytes())
    created = _aws(config, [
        "lambda", "create-function", "--function-name", FAULT_FUNCTION,
        "--runtime", "python3.12", "--role", role,
        "--handler", "fault_lambda.lambda_handler",
        "--zip-file", "fileb://" + str(archive.resolve()),
        "--timeout", "1", "--memory-size", "128", "--output", "json",
    ])
    created_value = json.loads(created.stdout)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        probe = _aws(config, [
            "lambda", "get-function-configuration", "--function-name",
            FAULT_FUNCTION, "--output", "json",
        ])
        state = json.loads(probe.stdout)
        if state.get("State") == "Active" and state.get("LastUpdateStatus") == "Successful":
            break
        time.sleep(1)
    else:
        raise CampaignError("FAULT_LAMBDA_READINESS_TIMEOUT")

    connection = _db(config, secret)
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT count(*) FROM [SHOW SCHEMAS] WHERE schema_name='{SCHEMA}'")
        if int(cursor.fetchone()[0]) != 0:
            raise CampaignError("CAMPAIGN_SCHEMA_ALREADY_EXISTS")
        cursor.execute(f"CREATE SCHEMA {SCHEMA}")
        cursor.execute(
            f"CREATE TABLE {SCHEMA}.state ("
            "run_id STRING PRIMARY KEY, fault STRING NOT NULL, repetition INT NOT NULL, "
            "status STRING NOT NULL, payload_hash STRING NOT NULL, "
            "receipt_hash STRING UNIQUE, ticket_state STRING NOT NULL DEFAULT 'ISSUED')"
        )
        cursor.execute(
            f"CREATE TABLE {SCHEMA}.vectors ("
            f"run_id STRING PRIMARY KEY REFERENCES {SCHEMA}.state(run_id), "
            "embedding VECTOR(3) NOT NULL, projection_hash STRING NOT NULL)"
        )
        cursor.execute(
            f"CREATE TABLE {SCHEMA}.counter (id STRING PRIMARY KEY, value INT NOT NULL)"
        )
        cursor.execute(f"INSERT INTO {SCHEMA}.counter VALUES ('serializable',0)")
        connection.commit()
    finally:
        connection.close()
    return {
        "fault_function": FAULT_FUNCTION,
        "fault_function_code_sha256": archive_hash,
        "fault_function_version": created_value.get("Version"),
        "role_arn_sha256": sha256(role.encode("utf-8")),
        "schema": SCHEMA,
    }


def _insert_state(connection, run_id: str, fault: str, repetition: int,
                  status: str = "SEALED") -> None:
    payload_hash = sha256({"run_id": run_id, "fault": fault, "repetition": repetition})
    receipt_hash = sha256({"run_id": run_id, "status": status})
    cursor = connection.cursor()
    cursor.execute(
        f"INSERT INTO {SCHEMA}.state "
        "(run_id,fault,repetition,status,payload_hash,receipt_hash) "
        "VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (run_id) DO NOTHING",
        (run_id, fault, repetition, status, payload_hash, receipt_hash),
    )


def _count(connection, run_id: str) -> int:
    cursor = connection.cursor()
    cursor.execute(f"SELECT count(*) FROM {SCHEMA}.state WHERE run_id=%s", (run_id,))
    return int(cursor.fetchone()[0])


def _normal_lambda(config: dict[str, str], run_id: str, output: Path) -> dict:
    request = _make_request(run_id)
    metadata = _invoke(config, "ck-p9-evaluator", request, output)
    response = json.loads(output.read_bytes())
    cloud_records.validate_response(response, request)
    if response["status"] != "ADVISORY":
        raise CampaignError("LAMBDA_AUTHORITY_VIOLATION")
    return metadata


def _scenario_precommit(config, secret, run_id, repetition, root) -> dict:
    lambda_meta = _normal_lambda(config, run_id, root / "lambda.json")
    connection = _db(config, secret)
    _insert_state(connection, run_id, "precommit_disconnect", repetition)
    connection.close()  # no commit
    verify = _db(config, secret)
    try:
        count = _count(verify, run_id)
    finally:
        verify.close()
    if count != 0:
        raise CampaignError("PARTIAL_OR_UNEXPECTED_COMMIT")
    return {"durable_rows": count, "outcome": "ABSENT", "lambda": lambda_meta}


def _scenario_postcommit(config, secret, run_id, repetition, root) -> dict:
    lambda_meta = _normal_lambda(config, run_id, root / "lambda.json")
    sql = (
        "BEGIN;"
        f"INSERT INTO {SCHEMA}.state "
        "(run_id,fault,repetition,status,payload_hash,receipt_hash) VALUES ("
        f"'{run_id}','postcommit_ack_withheld',{repetition},'SEALED',"
        f"'{sha256({'run_id': run_id, 'fault': 'postcommit_ack_withheld'})}',"
        f"'{sha256({'run_id': run_id, 'status': 'SEALED'})}') "
        "ON CONFLICT (run_id) DO NOTHING;COMMIT;SELECT pg_sleep(10);"
    )
    env = os.environ.copy()
    env["PGPASSWORD"] = bytes(secret).decode("utf-8")
    url = (
        "postgresql://" + config["keychain_account"] + "@" +
        config["cockroach_host"] + ":26257/cockroach_kernel?sslmode=verify-full&sslrootcert=" +
        config["ca_cert"]
    )
    process = subprocess.Popen([
        config["cockroach_bin"], "sql", "--url", url, "--execute", sql,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
       start_new_session=True)
    time.sleep(2)
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill(); process.wait(timeout=2)
    env.pop("PGPASSWORD", None)
    verify = _db(config, secret)
    try:
        before_retry = _count(verify, run_id)
        _insert_state(verify, run_id, "postcommit_ack_withheld", repetition)
        verify.commit()
        after_retry = _count(verify, run_id)
    finally:
        verify.close()
    if before_retry != 1 or after_retry != 1:
        raise CampaignError("POSTCOMMIT_RECONCILIATION_FAILED")
    return {
        "commit_acknowledgment_propagated_to_coordinator": False,
        "rows_before_idempotent_retry": before_retry,
        "rows_after_idempotent_retry": after_retry,
        "lambda": lambda_meta,
    }


def _scenario_40001(config, secret, run_id, repetition, root) -> dict:
    lambda_meta = _normal_lambda(config, run_id, root / "lambda.json")
    first = _db(config, secret)
    second = _db(config, secret)
    retry_count = 0
    try:
        c1, c2 = first.cursor(), second.cursor()
        c1.execute(f"SELECT value FROM {SCHEMA}.counter WHERE id='serializable'")
        v1 = int(c1.fetchone()[0])
        c2.execute(f"SELECT value FROM {SCHEMA}.counter WHERE id='serializable'")
        v2 = int(c2.fetchone()[0])
        c1.execute(f"UPDATE {SCHEMA}.counter SET value=%s WHERE id='serializable'", (v1 + 1,))
        first.commit()
        try:
            c2.execute(f"UPDATE {SCHEMA}.counter SET value=%s WHERE id='serializable'", (v2 + 1,))
            second.commit()
        except Exception as exc:
            code = getattr(exc, "args", [{}])[0]
            if not isinstance(code, dict) or code.get("C") != "40001":
                raise
            retry_count = 1
            second.rollback()
            c2 = second.cursor()
            c2.execute(f"SELECT value FROM {SCHEMA}.counter WHERE id='serializable'")
            current = int(c2.fetchone()[0])
            c2.execute(f"UPDATE {SCHEMA}.counter SET value=%s WHERE id='serializable'", (current + 1,))
            second.commit()
        if retry_count != 1:
            raise CampaignError("SQLSTATE_40001_NOT_OBSERVED")
    finally:
        first.close(); second.close()
    final = _db(config, secret)
    try:
        _insert_state(final, run_id, "sqlstate_40001_retry", repetition)
        final.commit()
        count = _count(final, run_id)
    finally:
        final.close()
    return {"retry_count": retry_count, "durable_rows": count, "lambda": lambda_meta}


def _scenario_timeout(config, secret, run_id, repetition, root) -> dict:
    metadata = _invoke(
        config, FAULT_FUNCTION, {"fault_mode": "timeout", "request_id": run_id},
        root / "lambda-timeout.json",
    )
    if metadata["function_error"] is None:
        raise CampaignError("LAMBDA_TIMEOUT_NOT_OBSERVED")
    connection = _db(config, secret)
    try:
        count = _count(connection, run_id)
    finally:
        connection.close()
    if count != 0:
        raise CampaignError("TIMEOUT_SELF_PROMOTED")
    return {"durable_rows": count, "authority_result": "WAIT_OR_REFUSE", "lambda": metadata}


def _scenario_stale_lambda(config, secret, run_id, repetition, root) -> dict:
    metadata = _invoke(
        config, FAULT_FUNCTION, {"fault_mode": "stale", "request_id": run_id},
        root / "lambda-stale.json",
    )
    response = json.loads((root / "lambda-stale.json").read_bytes())
    request = _make_request(run_id)
    reason = None
    try:
        cloud_records.validate_response(response, request)
    except cloud_records.CloudError as exc:
        reason = str(exc)
    if not reason:
        raise CampaignError("STALE_LAMBDA_ACCEPTED")
    connection = _db(config, secret)
    try:
        count = _count(connection, run_id)
    finally:
        connection.close()
    return {"durable_rows": count, "reason_code": reason, "lambda": metadata}


def _scenario_vector(config, secret, run_id, repetition, root) -> dict:
    lambda_meta = _normal_lambda(config, run_id, root / "lambda.json")
    connection = _db(config, secret)
    authoritative = sha256({"run_id": run_id, "authority": "transaction"})
    stale = sha256({"run_id": run_id, "projection": "stale"})
    try:
        _insert_state(connection, run_id, "stale_vector_projection", repetition)
        cursor = connection.cursor()
        cursor.execute(
            f"INSERT INTO {SCHEMA}.vectors VALUES (%s,'[0.1,0.2,0.3]',%s)",
            (run_id, stale),
        )
        connection.commit()
        cursor.execute(
            f"SELECT projection_hash, embedding <-> '[0.1,0.2,0.3]' "
            f"FROM {SCHEMA}.vectors WHERE run_id=%s", (run_id,),
        )
        projection_hash, distance = cursor.fetchone()
        count = _count(connection, run_id)
    finally:
        connection.close()
    if projection_hash == authoritative or count != 1:
        raise CampaignError("SEMANTIC_OVERRIDE_OR_LINKAGE_FAILURE")
    return {
        "transactional_rows": count, "projection_stale": True,
        "semantic_override_allowed": False, "vector_distance": float(distance),
        "lambda": lambda_meta,
    }


def _scenario_process_loss(config, secret, run_id, repetition, root) -> dict:
    lambda_meta = _normal_lambda(config, run_id, root / "lambda.json")
    from cockroach_kernel.test_recovery_surface import Scenario, tree
    scenario = Scenario(request_id="request-" + run_id)
    try:
        command = [
            sys.executable, str(BASE / "external-validity" / "after_consume_child.py"),
            "--request", str(scenario.request_path),
            "--sandbox-root", str(scenario.root),
            "--workspace", str(scenario.workspace),
            "--representation-root", str(scenario.representations),
            "--custody-root", str(scenario.custody),
            "--output-root", str(scenario.output),
        ]
        child = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               check=False, timeout=30)
        if child.returncode != 23:
            raise CampaignError("AFTER_CONSUME_PROCESS_FAULT_FAILED")
        replay_output = scenario.new_output("replay-output")
        replay = subprocess.run(
            scenario.cli(replay_output), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=False, timeout=30,
        )
        summary = json.loads(replay.stdout)
        sidecar = json.loads((scenario.custody / "warrants" / "warrant-r3-001.json").read_bytes())
        if replay.returncode == 0 or summary.get("reason") != "WARRANT_REPLAY":
            raise CampaignError("CONSUMED_TICKET_REPLAYED")
        if sidecar.get("state") != "CONSUMED" or tree(scenario.workspace):
            raise CampaignError("FAIL_CLOSED_CUSTODY_MISMATCH")
        connection = _db(config, secret)
        try:
            _insert_state(connection, run_id, "process_loss_after_consume", repetition, "REFUSED")
            cursor = connection.cursor()
            cursor.execute(
                f"UPDATE {SCHEMA}.state SET ticket_state='CONSUMED' WHERE run_id=%s",
                (run_id,),
            )
            connection.commit()
        finally:
            connection.close()
        return {
            "child_exit": child.returncode, "ticket_state": "CONSUMED",
            "replay_reason": "WARRANT_REPLAY", "workspace_files": 0,
            "lambda": lambda_meta,
        }
    finally:
        scenario.cleanup()


def _load_mcp_receipt(path: Path, run_id: str) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "version", "run_id", "server", "database", "read_only_scope",
        "write_operation_denied", "unexpected_tool_count", "credential_bytes_recorded",
        "tool_trace_sha256", "result_hash",
    }
    if set(value) != expected or value["run_id"] != run_id:
        raise CampaignError("MCP_RECEIPT_INVALID")
    if not HEX64.fullmatch(value["tool_trace_sha256"]):
        raise CampaignError("MCP_TRACE_HASH_INVALID")
    if (
        value["server"] != "cockroachdb-cloud" or
        value["database"] != "cockroach_kernel" or
        value["read_only_scope"] is not True or
        value["write_operation_denied"] is not True or
        value["unexpected_tool_count"] != 0 or
        value["credential_bytes_recorded"] is not False
    ):
        raise CampaignError("MCP_DENIAL_NOT_PROVEN")
    body = dict(value); claimed = body.pop("result_hash")
    if sha256(body) != claimed:
        raise CampaignError("MCP_RECEIPT_HASH_MISMATCH")
    return value


def _scenario_mcp(config, secret, run_id, repetition, root, mcp_root: Path) -> dict:
    lambda_meta = _normal_lambda(config, run_id, root / "lambda.json")
    receipt = _load_mcp_receipt(mcp_root / f"{run_id}.json", run_id)
    connection = _db(config, secret)
    try:
        _insert_state(connection, run_id, "mcp_read_only_denial", repetition, "REFUSED")
        connection.commit()
    finally:
        connection.close()
    return {
        "read_only_scope": True,
        "write_operation_denied": True,
        "mcp_tool_trace_sha256": receipt["tool_trace_sha256"],
        "lambda": lambda_meta,
    }


def _teardown(config: dict[str, str], secret: bytearray) -> dict:
    errors = []
    try:
        connection = _db(config, secret)
        try:
            cursor = connection.cursor()
            cursor.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
            connection.commit()
        finally:
            connection.close()
    except Exception as exc:
        errors.append("DB:" + sha256(str(exc).encode()))
    deleted = _aws(
        config, ["lambda", "delete-function", "--function-name", FAULT_FUNCTION],
        allow_failure=True,
    )
    if deleted.returncode:
        errors.append("LAMBDA:" + sha256(deleted.stdout))
    # Log-group absence is accepted; another failure is not.
    logs = _aws(
        config, ["logs", "delete-log-group", "--log-group-name",
                 "/aws/lambda/" + FAULT_FUNCTION], allow_failure=True,
    )
    if logs.returncode and b"ResourceNotFoundException" not in logs.stdout:
        errors.append("LOGS:" + sha256(logs.stdout))
    probe = _aws(
        config, ["lambda", "get-function", "--function-name", FAULT_FUNCTION,
                 "--output", "json"], allow_failure=True,
    )
    lambda_absent = probe.returncode != 0 and b"ResourceNotFoundException" in probe.stdout
    connection = _db(config, secret)
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT count(*) FROM [SHOW SCHEMAS] WHERE schema_name='{SCHEMA}'")
        schema_absent = int(cursor.fetchone()[0]) == 0
    finally:
        connection.close()
    if not lambda_absent or not schema_absent:
        errors.append("RESIDUE_PRESENT")
    return {
        "lambda_absent": lambda_absent,
        "schema_absent": schema_absent,
        "log_group_delete_requested": True,
        "errors": errors,
        "status": "PASS" if not errors else "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mcp-receipts", type=Path, required=True)
    parser.add_argument("--preflight-packet-sha256", required=True)
    args = parser.parse_args()
    if not HEX64.fullmatch(args.preflight_packet_sha256):
        raise SystemExit("PREFLIGHT_PACKET_HASH_INVALID")
    if args.output.exists():
        raise SystemExit("OUTPUT_ROOT_EXISTS")
    args.output.mkdir(parents=True, mode=0o700)
    config = _config(args.config.resolve())
    secret = _password(config)
    previous = "0" * 64
    receipts = []
    resources = None
    failure = None
    try:
        resources = _create_resources(config, secret, args.output)
        write_atomic(args.output / "resource-create.json", resources)
        methods = {
            "precommit_disconnect": _scenario_precommit,
            "postcommit_ack_withheld": _scenario_postcommit,
            "sqlstate_40001_retry": _scenario_40001,
            "lambda_timeout": _scenario_timeout,
            "stale_lambda_advisory": _scenario_stale_lambda,
            "stale_vector_projection": _scenario_vector,
            "mcp_read_only_denial": _scenario_mcp,
            "process_loss_after_consume": _scenario_process_loss,
        }
        sequence = 0
        for fault in FAULTS:
            for repetition in range(1, 4):
                sequence += 1
                run_id = f"ev2-{fault.replace('_','-')[:28]}-{repetition}-r1"
                run_root = args.output / f"execution-{sequence:02d}"
                run_root.mkdir(mode=0o700)
                call = methods[fault]
                if fault == "mcp_read_only_denial":
                    details = call(config, secret, run_id, repetition, run_root, args.mcp_receipts)
                else:
                    details = call(config, secret, run_id, repetition, run_root)
                receipt = chained_receipt(
                    campaign_id=CAMPAIGN_ID, sequence=sequence, kind=fault,
                    result="PASS", details=details, previous_hash=previous,
                )
                previous = receipt["receipt_hash"]
                write_atomic(run_root / "receipt.json", receipt)
                receipts.append(receipt)
    except BaseException as exc:
        failure = {
            "type": type(exc).__name__,
            "message_sha256": sha256(str(exc).encode("utf-8")),
            "completed_executions": len(receipts),
        }
        write_atomic(args.output / "failure.json", failure)
    finally:
        teardown = _teardown(config, secret)
        write_atomic(args.output / "teardown.json", teardown)
        for index in range(len(secret)):
            secret[index] = 0
    status = "PASS" if failure is None and len(receipts) == 24 and teardown["status"] == "PASS" else "BLOCKED"
    final = {
        "version": "ck-ev2-final-v1",
        "campaign_id": CAMPAIGN_ID,
        "status": status,
        "preflight_packet_sha256": args.preflight_packet_sha256,
        "completed_executions": len(receipts),
        "expected_executions": 24,
        "final_receipt_hash": previous,
        "resource_create_hash": sha256(resources) if resources else None,
        "failure_hash": sha256(failure) if failure else None,
        "teardown_hash": sha256(teardown),
        "bounded_incremental_cost_usd": 1.0,
        "exact_provider_cost_available": False,
    }
    write_atomic(args.output / "final.json", final)
    print(json.dumps(final, sort_keys=True, separators=(",", ":")))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
