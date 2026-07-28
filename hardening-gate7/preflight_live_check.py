#!/usr/bin/env python3
"""Read-only, redacted CockroachDB/AWS readiness receipt for Gate 7."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "s3-soak"))
import cloud_adapter  # type: ignore  # noqa: E402
import hardening  # type: ignore  # noqa: E402
import protocol  # type: ignore  # noqa: E402


class ReadinessError(RuntimeError):
    pass


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    raw = protocol.canonical(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = cloud_adapter._read_config(args.config.resolve())
    secret = bytearray()
    sql_env = None
    try:
        secret.extend(cloud_adapter._password(config))
        sql_env = cloud_adapter._sql_env(config, bytes(secret))
        sql = (
            "SELECT current_database(), current_user, version();"
            "SHOW REGIONS FROM CLUSTER;"
            "SELECT count(*) FROM information_schema.tables WHERE table_schema='ck';"
        )
        database_raw, database_ms = cloud_adapter._sql(
            config, sql_env, execute=sql, timeout=60,
        )
        aws_env = os.environ.copy()
        aws_env["AWS_PAGER"] = ""
        started = time.monotonic_ns()
        aws = subprocess.run([
            config["aws_cli"], "sts", "get-caller-identity",
            "--profile", config["aws_profile"],
            "--region", config["aws_region"],
            "--output", "json", "--no-cli-pager",
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=aws_env,
           check=False, timeout=30)
        aws_ms = int((time.monotonic_ns() - started) / 1_000_000)
        if aws.returncode != 0:
            failure = hardening.command_failure("aws", aws.returncode, aws.stdout)
            body = {
                "version": "hardening-gate7-live-readiness-v1",
                "status": "HUMAN_ACTION_REQUIRED",
                "cockroach_reachable": True,
                "cockroach_output_sha256": protocol.sha256(database_raw),
                "cockroach_latency_ms": database_ms,
                "aws_authenticated": False,
                "aws_failure_class": failure.failure_class,
                "aws_failure_output_sha256": failure.output_hash,
                "aws_return_code": aws.returncode,
                "aws_latency_ms": aws_ms,
                "aws_profile": config["aws_profile"],
                "aws_region": config["aws_region"],
                "credential_bytes_recorded": False,
                "read_only": True,
                "next_action": "PROJECT_LOCAL_AWS_LOGIN_BEFORE_CAMPAIGN_READY",
            }
            receipt = dict(body, receipt_sha256=protocol.sha256(body))
            atomic_write(args.output.resolve(), receipt)
            print(protocol.canonical({
                "status": "HUMAN_ACTION_REQUIRED",
                "receipt_sha256": receipt["receipt_sha256"],
                "failure_class": failure.failure_class,
            }).decode("utf-8"))
            return 3
        # Validate JSON but persist only its hash and key shape, never account data.
        identity = json.loads(aws.stdout)
        if set(identity) != {"UserId", "Account", "Arn"}:
            raise ReadinessError("AWS_IDENTITY_SCHEMA_INVALID")
        body = {
            "version": "hardening-gate7-live-readiness-v1",
            "status": "GREEN",
            "cockroach_reachable": True,
            "cockroach_output_sha256": protocol.sha256(database_raw),
            "cockroach_latency_ms": database_ms,
            "aws_authenticated": True,
            "aws_identity_output_sha256": protocol.sha256(aws.stdout),
            "aws_identity_fields": sorted(identity),
            "aws_latency_ms": aws_ms,
            "aws_profile": config["aws_profile"],
            "aws_region": config["aws_region"],
            "cockroach_host_sha256": protocol.sha256(config["cockroach_host"].encode()),
            "credential_bytes_recorded": False,
            "read_only": True,
        }
        receipt = dict(body, receipt_sha256=protocol.sha256(body))
        atomic_write(args.output.resolve(), receipt)
        print(protocol.canonical({
            "status": "GREEN", "receipt_sha256": receipt["receipt_sha256"]
        }).decode("utf-8"))
        return 0
    finally:
        if sql_env is not None:
            sql_env.pop("PGPASSWORD", None)
        for index in range(len(secret)):
            secret[index] = 0


if __name__ == "__main__":
    raise SystemExit(main())
