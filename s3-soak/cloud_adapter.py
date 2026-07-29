#!/usr/bin/env python3
"""Fixed P9 live-path adapter for the detached S3 host coordinator.

Credential bytes remain process-local. They are never accepted from the worker,
written to evidence, printed, or transferred to RunPod.
"""
from __future__ import annotations

import importlib.util
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from typing import Any
from urllib.parse import quote

import protocol
import hardening

BASE = Path(__file__).resolve().parents[1]
P9 = BASE / "p9-cloud"
sys.path.insert(0, str(P9))
import records  # type: ignore  # noqa: E402

AWS_REQUEST_RE = re.compile(r"RequestId:\s*([A-Za-z0-9-]{8,64})")
AWS_LOGIN_REFRESH_MARKER = b"refresh the temporary credentials automatically"


class CloudAdapterError(RuntimeError):
    pass


def _load_live_completion():
    path = P9 / "live_completion.py"
    spec = importlib.util.spec_from_file_location("s3_live_completion", path)
    if spec is None or spec.loader is None:
        raise CloudAdapterError("LIVE_COMPLETION_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _run(command: list[str], *, family: str,
         env: dict[str, str] | None = None,
         timeout: int = 60) -> tuple[bytes, int]:
    started = time.monotonic_ns()
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            env=env, timeout=timeout, check=False)
    elapsed_ms = int((time.monotonic_ns() - started) / 1_000_000)
    if result.returncode != 0:
        raise hardening.command_failure(family, result.returncode, result.stdout)
    return result.stdout, elapsed_ms


def _read_config(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    fields = {
        "cockroach_bin", "cockroach_host", "ca_cert", "keychain_account",
        "keychain_service", "aws_cli", "aws_profile", "aws_region",
    }
    if not isinstance(value, dict) or set(value) != fields:
        raise CloudAdapterError("CONFIG_FIELDS_INVALID")
    for name, item in value.items():
        if not isinstance(item, str) or not item or "\x00" in item:
            raise CloudAdapterError("CONFIG_VALUE_INVALID:" + name)
    for name in ("cockroach_bin", "ca_cert", "aws_cli"):
        resolved = Path(value[name]).resolve()
        if not resolved.is_file():
            raise CloudAdapterError("CONFIG_FILE_MISSING:" + name)
        value[name] = str(resolved)
    if not re.fullmatch(r"[A-Za-z0-9.-]+\.cockroachlabs\.cloud", value["cockroach_host"]):
        raise CloudAdapterError("COCKROACH_HOST_INVALID")
    if value["aws_region"] != "us-west-2" or value["aws_profile"] != "ck-s3":
        raise CloudAdapterError("AWS_SCOPE_INVALID")
    return value


def _password(config: dict[str, Any]) -> bytes:
    result = subprocess.run([
        "/usr/bin/security", "find-generic-password", "-w",
        "-a", config["keychain_account"], "-s", config["keychain_service"],
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False, timeout=30)
    if result.returncode != 0 or not result.stdout.strip():
        raise CloudAdapterError("KEYCHAIN_RETRIEVAL_BLOCKED")
    return result.stdout.rstrip(b"\n")


def _sql_env(config: dict[str, Any], secret: bytes) -> dict[str, str]:
    env = os.environ.copy()
    env["PGPASSWORD"] = secret.decode("utf-8")
    env["COCKROACH_SKIP_ENABLING_DIAGNOSTIC_REPORTING"] = "true"
    return env


def _sql_url(config: dict[str, Any]) -> str:
    cert = quote(config["ca_cert"], safe="/")
    return ("postgresql://ck_runtime@" + config["cockroach_host"] +
            ":26257/cockroach_kernel?sslmode=verify-full&sslrootcert=" + cert)


def _sql(config: dict[str, Any], env: dict[str, str], *, execute: str | None = None,
         file: Path | None = None, timeout: int = 60,
         fmt: str = "tsv") -> tuple[bytes, int]:
    command = [config["cockroach_bin"], "sql", "--url", _sql_url(config),
               "--format", fmt]
    if (execute is None) == (file is None):
        raise CloudAdapterError("SQL_MODE_INVALID")
    if execute is not None:
        command.extend(["--execute", execute])
    else:
        command.extend(["--file", str(file.resolve())])
    return _run(command, family="cockroach", env=env, timeout=timeout)


def _cleanup_sql(task_id: str) -> str:
    if task_id not in {"ck-p9-live-promote-r1", "ck-p9-live-refuse-r1"}:
        raise CloudAdapterError("TASK_ID_INVALID")
    literal = "'" + task_id + "'"
    return (
        "BEGIN;"
        f"DELETE FROM ck.projection_events WHERE projection_id={literal} || '-projection-r1';"
        f"DELETE FROM ck.worker_results WHERE task_id={literal};"
        f"DELETE FROM ck.context_vectors WHERE task_id={literal};"
        f"DELETE FROM ck.receipts WHERE task_id={literal};"
        f"DELETE FROM ck.trajectory_events WHERE task_id={literal};"
        f"DELETE FROM ck.tasks WHERE task_id={literal};"
        "COMMIT;"
    )


def _aws_invoke(config: dict[str, Any], request_path: Path,
                response_path: Path) -> tuple[dict[str, Any], int]:
    aws_env = os.environ.copy()
    aws_env["AWS_PAGER"] = ""
    raw, elapsed = _run([
        config["aws_cli"], "lambda", "invoke", "--function-name", "ck-p9-evaluator",
        "--payload", "fileb://" + str(request_path.resolve()),
        "--cli-binary-format", "raw-in-base64-out", "--log-type", "Tail",
        "--profile", config["aws_profile"],
        "--region", config["aws_region"], "--output", "json", "--no-cli-pager",
        str(response_path.resolve()),
    ], family="aws", env=aws_env, timeout=30)
    metadata = json.loads(raw)
    try:
        log_tail = base64.b64decode(metadata["LogResult"], validate=True).decode("utf-8")
    except (KeyError, ValueError, UnicodeDecodeError) as exc:
        raise CloudAdapterError("AWS_LOG_TAIL_INVALID") from exc
    match = AWS_REQUEST_RE.search(log_tail)
    if match is None:
        raise CloudAdapterError("AWS_REQUEST_ID_MISSING")
    request_id = match.group(1)
    return {
        "status_code": metadata.get("StatusCode"),
        "function_error": metadata.get("FunctionError"),
        "aws_request_id": request_id,
    }, elapsed


def prove_aws_login_provider(config_path: Path) -> dict[str, Any]:
    """Prove the scoped profile uses the refreshable AWS login provider."""
    config = _read_config(config_path.resolve())
    aws_env = os.environ.copy()
    aws_env["AWS_PAGER"] = ""
    listed, list_ms = _run([
        config["aws_cli"], "configure", "list", "--profile",
        config["aws_profile"],
    ], family="aws", env=aws_env, timeout=30)
    if listed.lower().count(b"login") < 2:
        raise CloudAdapterError("AWS_LOGIN_PROVIDER_NOT_ACTIVE")
    help_output, help_ms = _run([
        config["aws_cli"], "login", "help",
    ], family="aws", env=aws_env, timeout=30)
    normalized = b" ".join(help_output.lower().split())
    if AWS_LOGIN_REFRESH_MARKER not in normalized:
        raise CloudAdapterError("AWS_LOGIN_REFRESH_CONTRACT_MISSING")
    version_output, version_ms = _run([
        config["aws_cli"], "--version",
    ], family="aws", env=aws_env, timeout=30)
    core = {
        "version": "s3-aws-login-provider-proof-v1",
        "aws_profile": config["aws_profile"],
        "aws_region": config["aws_region"],
        "credential_provider": "login",
        "automatic_refresh_contract_observed": True,
        "configure_list_output_sha256": protocol.sha256(listed),
        "login_help_output_sha256": protocol.sha256(help_output),
        "aws_cli_version_output_sha256": protocol.sha256(version_output),
        "latency_ms": list_ms + help_ms + version_ms,
        "credential_bytes_recorded": False,
        "status": "PASS",
    }
    return {**core, "receipt_hash": protocol.sha256(core)}


def probe_aws_identity(config_path: Path) -> dict[str, Any]:
    """Perform one sanitized read-only identity probe after the margin."""
    config = _read_config(config_path.resolve())
    aws_env = os.environ.copy()
    aws_env["AWS_PAGER"] = ""
    raw, elapsed = _run([
        config["aws_cli"], "sts", "get-caller-identity",
        "--profile", config["aws_profile"], "--region", config["aws_region"],
        "--output", "json", "--no-cli-pager",
    ], family="aws", env=aws_env, timeout=30)
    value = json.loads(raw)
    if not isinstance(value, dict) or set(value) != {"Account", "Arn", "UserId"}:
        raise CloudAdapterError("AWS_IDENTITY_SCHEMA_INVALID")
    return {
        "identity_fields": sorted(value),
        "identity_output_sha256": protocol.sha256(raw),
        "latency_ms": elapsed,
        "credential_bytes_recorded": False,
        "status": "PASS",
    }


def run_live(request: dict[str, Any], config_path: Path,
             evidence_root: Path) -> tuple[dict[str, int], dict[str, str]]:
    protocol.validate_request(request)
    config = _read_config(config_path.resolve())
    branch = "promote" if request["operation"] == "RUN_PROMOTE" else "refuse"
    live = _load_live_completion()
    evidence_root = evidence_root.resolve()
    evidence_root.mkdir(parents=True, exist_ok=False)
    trial_root = evidence_root / f"trial-{request['sequence']:04d}"
    if trial_root.exists():
        raise CloudAdapterError("TRIAL_ROOT_EXISTS")
    secret = bytearray()
    sql_env: dict[str, str] | None = None
    stage = "CREDENTIAL_ACQUISITION"
    failure: BaseException | None = None
    try:
        secret.extend(_password(config))
        sql_env = _sql_env(config, bytes(secret))
        stage = "TRIAL_PREPARE"
        live.prepare(trial_root)
        prepared = json.loads((trial_root / f"{branch}-prepared.json").read_text())
        task_id = prepared["task_id"]
        stage = "PRESEED_CLEANUP"
        _, cleanup_ms = _sql(config, sql_env, execute=_cleanup_sql(task_id))
        stage = "COCKROACH_SEED"
        seed_raw, transaction_ms = _sql(
            config, sql_env, file=trial_root / f"{branch}-seed.sql")
        stage = "COCKROACH_VECTOR_QUERY"
        vector_raw, vector_ms = _sql(
            config, sql_env, file=trial_root / f"{branch}-vector-query.sql")
        if prepared["vector_id"].encode() not in vector_raw:
            raise CloudAdapterError("VECTOR_LINKAGE_FAILED")
        lambda_request = trial_root / f"{branch}-request.json"
        lambda_response = trial_root / f"{branch}-lambda-response.json"
        stage = "AWS_LAMBDA_INVOKE"
        meta, lambda_ms = _aws_invoke(config, lambda_request, lambda_response)
        response_value = json.loads(lambda_response.read_text(encoding="utf-8"))
        lambda_response.write_bytes(records.canonical_json(response_value) + b"\n")
        (trial_root / f"{branch}-lambda-meta.json").write_bytes(
            records.canonical_json(meta) + b"\n")
        stage = "LOCAL_RECONCILIATION"
        reconciled, finalize_sql = live.reconcile_trial(trial_root, branch)
        finalize_path = trial_root / f"{branch}-finalize.sql"
        finalize_path.write_text(finalize_sql, encoding="utf-8")
        stage = "COCKROACH_FINALIZE"
        _, finalize_ms = _sql(config, sql_env, file=finalize_path)
        feed_sql = (
            "EXPERIMENTAL CHANGEFEED FOR TABLE ck.worker_results "
            "WITH initial_scan='only', format='json'"
        )
        stage = "COCKROACH_CHANGEFEED"
        feed_raw, changefeed_ms = _sql(
            config, sql_env, execute=feed_sql, timeout=30, fmt="ndjson")
        feed_path = trial_root / "changefeed.ndjson"
        feed_path.write_bytes(feed_raw)
        feed = live.inspect_changefeed(feed_path)
        if prepared["request"]["request_id"] not in feed["request_ids"]:
            raise CloudAdapterError("CHANGEFEED_LINKAGE_FAILED")
        restart_raw, restart_ms = _sql(
            config, sql_env, execute=feed_sql, timeout=30, fmt="ndjson")
        restart_path = trial_root / "changefeed-restart.ndjson"
        restart_path.write_bytes(restart_raw)
        restart = live.inspect_changefeed(restart_path)
        if restart["request_ids"] != feed["request_ids"]:
            raise CloudAdapterError("CHANGEFEED_RESTART_MISMATCH")
        changefeed_ms += restart_ms
        audit_sql = (
            "SELECT task_id, receipt_hash, event_hash FROM ck.mcp_receipt_view "
            f"WHERE task_id='{task_id}' LIMIT 2"
        )
        stage = "COCKROACH_AUDIT"
        audit_raw, audit_ms = _sql(config, sql_env, execute=audit_sql)
        if task_id.encode() not in audit_raw:
            raise CloudAdapterError("MCP_AUDIT_LINKAGE_FAILED")
        stage = "POSTTRIAL_CLEANUP"
        _, cleanup2_ms = _sql(config, sql_env, execute=_cleanup_sql(task_id))
        verify_raw, verify_ms = _sql(
            config, sql_env,
            execute=f"SELECT count(*) FROM ck.tasks WHERE task_id='{task_id}'")
        numbers = re.findall(rb"\b\d+\b", verify_raw)
        if not numbers or numbers[-1] != b"0":
            raise CloudAdapterError("CLEANUP_FAILED")
        evidence_hashes = {
            "transaction": protocol.sha256(seed_raw),
            "vector": protocol.sha256(vector_raw),
            "lambda": reconciled["result_receipt_hash"],
            "changefeed": protocol.sha256({
                "initial": feed["inspection_hash"],
                "restart": restart["inspection_hash"],
            }),
            "mcp_audit": protocol.sha256(audit_raw),
            "verifier": protocol.sha256(reconciled["verdicts"]),
            "cleanup": protocol.sha256(verify_raw),
        }
        metrics = {
            "cockroach_ms": transaction_ms + finalize_ms + audit_ms,
            "vector_ms": vector_ms,
            "lambda_ms": lambda_ms,
            "changefeed_ms": changefeed_ms,
            "coordinator_ms": (transaction_ms + vector_ms + lambda_ms +
                               finalize_ms + changefeed_ms + audit_ms +
                               cleanup_ms + cleanup2_ms + verify_ms),
            "lambda_invocations": 1,
            "cockroach_operations": 9,
            "changefeed_rows": feed["rows"] + restart["rows"],
            "coordinator_backlog": 0,
        }
        summary = {
            "version": "s3-cloud-call-summary-v1",
            "sequence": request["sequence"],
            "request_hash": request["request_hash"],
            "operation": request["operation"],
            "metrics": metrics,
            "evidence_hashes": evidence_hashes,
        }
        summary["summary_hash"] = protocol.sha256(summary)
        (evidence_root / "summary.json").write_bytes(protocol.canonical(summary) + b"\n")
        return metrics, evidence_hashes
    except BaseException as exc:
        failure = exc
        if isinstance(exc, hardening.ExternalCommandFailure):
            classified = exc
        else:
            classified = hardening.ExternalCommandFailure(
                command_family="internal",
                return_code=-1,
                output_hash=protocol.sha256(str(exc).encode("utf-8")),
                failure_class=hardening.UNKNOWN_EXTERNAL_COMMAND,
                sqlstate=None,
            )
        receipt = hardening.failure_receipt(
            campaign_id=request["campaign_id"],
            sequence=request["sequence"],
            stage=stage,
            request_hash=request["request_hash"],
            failure=classified,
        )
        # This fsynced receipt is outside the temporary trial and is committed
        # before the finally block is allowed to remove trial-local evidence.
        hardening.write_atomic(evidence_root / "failure.json", receipt)
        raise CloudAdapterError(
            f"STAGE_FAILED:{stage}:{classified.failure_class}"
        ) from exc
    finally:
        if sql_env is not None:
            sql_env.pop("PGPASSWORD", None)
        for index in range(len(secret)):
            secret[index] = 0
        cleanup = hardening.cleanup_trial_exact(trial_root, evidence_root)
        hardening.write_atomic(evidence_root / "cleanup.json", cleanup)
        if failure is not None and not (evidence_root / "failure.json").is_file():
            raise CloudAdapterError("FAILURE_RECEIPT_MISSING")


def run_fixture(request: dict[str, Any]) -> tuple[dict[str, int], dict[str, str]]:
    """Deterministic non-live adapter used only by protocol unit tests."""
    protocol.validate_request(request)
    metrics = {
        "cockroach_ms": 5, "vector_ms": 2, "lambda_ms": 4,
        "changefeed_ms": 3, "coordinator_ms": 20,
        "lambda_invocations": 1, "cockroach_operations": 9,
        "changefeed_rows": 2, "coordinator_backlog": 0,
    }
    hashes = {name: protocol.sha256({"request": request["request_hash"],
                                     "kind": name})
              for name in protocol.EVIDENCE_HASH_FIELDS}
    return metrics, hashes
