#!/usr/bin/env python3
"""Freeze sanitized, read-only Hardening Gate 2 closeout evidence."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from deploy_demo import Aws, canonical, verify


NAME = "ck-hardening-demo"
LOG_GROUP = f"/aws/lambda/{NAME}"
ACCESS_END = datetime.fromisoformat("2026-09-15T21:00:00+00:00")
ACCOUNT_PATTERN = re.compile(r"(?<![0-9])[0-9]{12}(?![0-9])")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path: Path, value: object) -> str:
    if path.exists():
        raise RuntimeError(f"EVIDENCE_ALREADY_EXISTS:{path.name}")
    data = canonical(value) + b"\n"
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def redact_accounts(value: Any) -> Any:
    if isinstance(value, str):
        return ACCOUNT_PATTERN.sub("<ACCOUNT>", value)
    if isinstance(value, list):
        return [redact_accounts(item) for item in value]
    if isinstance(value, dict):
        return {key: redact_accounts(item) for key, item in value.items()}
    return value


def metric(aws: Aws, name: str, start: datetime, end: datetime) -> dict[str, Any]:
    response = aws.run(
        "cloudwatch",
        "get-metric-statistics",
        "--namespace",
        "AWS/Lambda",
        "--metric-name",
        name,
        "--dimensions",
        f"Name=FunctionName,Value={NAME}",
        "--start-time",
        start.isoformat().replace("+00:00", "Z"),
        "--end-time",
        end.isoformat().replace("+00:00", "Z"),
        "--period",
        "3600",
        "--statistics",
        "Sum",
        "Maximum",
    )
    return {
        "metric": name,
        "datapoints": sorted(response.get("Datapoints", []), key=lambda item: item["Timestamp"]),
    }


def main() -> int:
    repo = Path.cwd().resolve()
    evidence = repo / "evidence/hardening-gate2-closeout-r1"
    if not evidence.is_dir():
        raise RuntimeError("CLOSEOUT_EVIDENCE_DIRECTORY_MISSING")
    aws = Aws(repo)
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=4)

    function = aws.run("lambda", "get-function-configuration", "--function-name", NAME)
    role_policy = redact_accounts(
        aws.run(
            "iam",
            "get-role-policy",
            "--role-name",
            NAME,
            "--policy-name",
            f"{NAME}-runtime",
        )
    )
    api_id = verify(repo)["api_id"]
    stage = aws.run("apigatewayv2", "get-stage", "--api-id", api_id, "--stage-name", "$default")
    routes = aws.run("apigatewayv2", "get-routes", "--api-id", api_id).get("Items", [])
    alarms = aws.run("cloudwatch", "describe-alarms", "--alarm-name-prefix", NAME).get(
        "MetricAlarms", []
    )
    secret = aws.run("secretsmanager", "describe-secret", "--secret-id", f"{NAME}-db")
    streams = aws.run(
        "logs",
        "describe-log-streams",
        "--log-group-name",
        LOG_GROUP,
        "--order-by",
        "LastEventTime",
        "--descending",
        "--limit",
        "10",
    ).get("logStreams", [])
    events = aws.run(
        "logs",
        "filter-log-events",
        "--log-group-name",
        LOG_GROUP,
        "--start-time",
        str(int(start.timestamp() * 1000)),
        "--limit",
        "500",
    ).get("events", [])
    messages = [item.get("message", "") for item in events]
    start_ids = [item.split()[2] for item in messages if item.startswith("START RequestId:")]
    end_ids = [item.split()[2] for item in messages if item.startswith("END RequestId:")]
    reports = [item for item in messages if item.startswith("REPORT RequestId:")]

    aws_record = {
        "version": "ck-hardening-gate2-aws-closeout-v1",
        "utc_recorded": now.isoformat().replace("+00:00", "Z"),
        "configuration": verify(repo),
        "function": {
            "name": function.get("FunctionName"),
            "runtime": function.get("Runtime"),
            "handler": function.get("Handler"),
            "code_size": function.get("CodeSize"),
            "timeout_seconds": function.get("Timeout"),
            "memory_mib": function.get("MemorySize"),
            "state": function.get("State"),
            "last_update_status": function.get("LastUpdateStatus"),
            "architectures": function.get("Architectures"),
            "environment_keys": sorted(function.get("Environment", {}).get("Variables", {})),
        },
        "iam": role_policy,
        "stage": {
            "name": stage.get("StageName"),
            "auto_deploy": stage.get("AutoDeploy"),
            "default_route_settings": stage.get("DefaultRouteSettings"),
        },
        "routes": sorted(
            [
                {
                    "route_key": item.get("RouteKey"),
                    "authorization_type": item.get("AuthorizationType"),
                    "api_key_required": item.get("ApiKeyRequired"),
                }
                for item in routes
            ],
            key=lambda item: item["route_key"],
        ),
        "alarms": sorted(
            [
                {
                    "name": item.get("AlarmName"),
                    "actions_enabled": item.get("ActionsEnabled"),
                    "state": item.get("StateValue"),
                    "metric": item.get("MetricName"),
                    "period": item.get("Period"),
                    "threshold": item.get("Threshold"),
                }
                for item in alarms
            ],
            key=lambda item: item["name"],
        ),
        "secret_metadata": {
            "name": secret.get("Name"),
            "created": secret.get("CreatedDate"),
            "last_changed": secret.get("LastChangedDate"),
            "last_accessed": secret.get("LastAccessedDate"),
            "tag_count": len(secret.get("Tags", [])),
            "secret_value_read": False,
        },
        "logs": {
            "stream_count": len(streams),
            "event_count": len(events),
            "start_count": len(start_ids),
            "end_count": len(end_ids),
            "report_count": len(reports),
            "start_request_ids_sha256": hashlib.sha256(canonical(sorted(start_ids))).hexdigest(),
            "end_request_ids_sha256": hashlib.sha256(canonical(sorted(end_ids))).hexdigest(),
        },
        "metrics": [metric(aws, item, start, now) for item in ("Invocations", "Errors", "Duration", "Throttles")],
        "secret_value_read": False,
        "account_identifier_recorded": False,
    }
    if aws_record["logs"]["start_count"] < 19:
        raise RuntimeError("AWS_REQUEST_EVIDENCE_INCOMPLETE")
    if aws_record["logs"]["start_count"] != aws_record["logs"]["end_count"]:
        raise RuntimeError("AWS_REQUEST_END_MISMATCH")
    if aws_record["logs"]["start_count"] != aws_record["logs"]["report_count"]:
        raise RuntimeError("AWS_REQUEST_REPORT_MISMATCH")

    seconds = max(0.0, (ACCESS_END - now).total_seconds())
    requests = 0.05 * seconds + 2
    rates = {
        "lambda_gb_second_usd": 0.0000166667,
        "lambda_request_per_million_usd": 0.20,
        "http_api_request_per_million_usd": 1.00,
        "secret_per_month_usd": 0.40,
        "secret_per_10000_calls_usd": 0.05,
        "standard_alarm_per_month_usd": 0.10,
        "logs_per_gb_ingested_usd": 0.50,
        "data_transfer_per_gb_usd": 0.09,
    }
    components = {
        "lambda_duration": requests * 8 * 0.256 * rates["lambda_gb_second_usd"],
        "lambda_requests": requests / 1_000_000 * rates["lambda_request_per_million_usd"],
        "http_api_requests": requests / 1_000_000 * rates["http_api_request_per_million_usd"],
        "secret_storage": seconds / (30 * 86400) * rates["secret_per_month_usd"],
        "secret_calls": requests / 10_000 * rates["secret_per_10000_calls_usd"],
        "two_alarms": seconds / (30 * 86400) * 2 * rates["standard_alarm_per_month_usd"],
        "logs_at_1kib_per_invocation": requests * 1024 / (1024**3) * rates["logs_per_gb_ingested_usd"],
        "transfer_at_12kib_per_invocation": requests * 12288 / (1024**3) * rates["data_transfer_per_gb_usd"],
    }
    total = sum(components.values())
    cost = {
        "version": "ck-hardening-gate2-cost-projection-v1",
        "utc_recorded": now.isoformat().replace("+00:00", "Z"),
        "access_end_utc": ACCESS_END.isoformat().replace("+00:00", "Z"),
        "seconds_remaining": seconds,
        "stage_rate_per_second": 0.05,
        "stage_burst": 2,
        "accepted_request_upper_projection": requests,
        "lambda_memory_gb_conservative": 0.256,
        "lambda_timeout_seconds": 8,
        "no_free_tier_assumed": True,
        "rates": rates,
        "components_usd": components,
        "projected_total_usd": total,
        "authorized_ceiling_usd": 12.00,
        "status": "PROJECTED_WITHIN_CEILING" if total <= 12 else "PROJECTED_OVER_CEILING",
        "pricing_sources": [
            "https://aws.amazon.com/lambda/pricing/",
            "https://aws.amazon.com/api-gateway/pricing/",
            "https://aws.amazon.com/secrets-manager/pricing/",
            "https://aws.amazon.com/cloudwatch/pricing/",
            "https://aws.amazon.com/ec2/pricing/on-demand-backup/",
        ],
        "residual": "Stage throttling bounds accepted integration traffic, not arbitrary billed ingress during a denial-of-wallet attack; alarms plus the recorded manual kill line remain required.",
    }
    if total > 12:
        raise RuntimeError("AWS_COST_PROJECTION_EXCEEDS_AUTHORIZATION")

    cross_phase_paths = [
        "S1_R3_EXECUTION_REPORT.md",
        "S1_FINAL_PACKET_R3.md",
        "evidence/p9-mcp-linked-r2/bounded-linked-proof-result.json",
        "evidence/p9-mcp-linked-r2/bounded-linked-proof-events.sanitized.jsonl",
        "evidence/hardening-gate2-live-r2/live-test-result.json",
        "evidence/hardening-gate2-live-r2/evidence-manifest.json",
    ]
    cross_phase = {
        "version": "ck-hardening-gate2-cross-phase-evidence-v1",
        "files": [
            {"path": item, "bytes": (repo / item).stat().st_size, "sha256": sha256(repo / item)}
            for item in cross_phase_paths
        ],
        "transaction_retry_evidence": "S1_R3_EXECUTION_REPORT.md: SQLSTATE 40001 handling passed at all 61 checkpoints.",
        "mcp_evidence": "P9 bounded linked read-only MCP proof; hashes above.",
        "live_replay_evidence": "Gate 2 revision-2 live result; hash above.",
    }

    write_once(evidence / "aws-evidence.json", aws_record)
    write_once(evidence / "cost-projection.json", cost)
    write_once(evidence / "cross-phase-evidence.json", cross_phase)
    files = [
        {
            "path": path.relative_to(evidence).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(evidence.rglob("*"))
        if path.is_file()
    ]
    manifest_body = {"version": "ck-hardening-gate2-closeout-manifest-v1", "files": files}
    manifest_body["manifest_hash"] = hashlib.sha256(canonical(manifest_body)).hexdigest()
    write_once(evidence / "closeout-manifest.json", manifest_body)
    print(canonical({"status": "CLOSEOUT_EVIDENCE_GREEN", "manifest_hash": manifest_body["manifest_hash"], "projected_total_usd": total}).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
