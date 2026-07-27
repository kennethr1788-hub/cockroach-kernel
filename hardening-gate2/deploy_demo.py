#!/usr/bin/env python3
"""Deploy and verify the exact bounded Hardening Gate 2 AWS surface.

The script never reads the database secret value. It resolves only secret
metadata, constructs a least-privilege execution policy, and rolls back any
AWS resources it creates if deployment fails. The pre-existing project secret
is intentionally outside rollback ownership.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any


NAME = "ck-hardening-demo"
SECRET_NAME = "ck-hardening-demo-db"
REGION = "us-west-2"
PROFILE = "ck-s3"
LOG_GROUP = f"/aws/lambda/{NAME}"
ROUTES = {"GET /demo/promote", "GET /demo/refuse"}
ALARM_NAMES = {f"{NAME}-errors", f"{NAME}-invocations-5000"}


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Aws:
    def __init__(self, repo: Path) -> None:
        self.repo = repo.resolve()
        self.binary = (
            self.repo
            / ".s3-runtime/aws-expanded-r1/aws-cli.pkg/Payload/aws-cli/aws"
        )
        self.environment = os.environ.copy()
        self.environment.update(
            {
                "AWS_CONFIG_FILE": str(self.repo / ".s3-runtime/aws-auth/config"),
                "AWS_LOGIN_CACHE_DIRECTORY": str(
                    self.repo / ".s3-runtime/aws-auth/login-cache"
                ),
                "AWS_SHARED_CREDENTIALS_FILE": "/dev/null",
                "AWS_PAGER": "",
            }
        )
        if not self.binary.is_file():
            raise RuntimeError("PROJECT_AWS_CLI_MISSING")

    def run(
        self,
        *arguments: str,
        expect_json: bool = True,
        check: bool = True,
    ) -> Any:
        command = [
            str(self.binary),
            *arguments,
            "--profile",
            PROFILE,
            "--region",
            REGION,
            "--no-cli-pager",
        ]
        completed = subprocess.run(
            command,
            cwd=self.repo,
            env=self.environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if check and completed.returncode != 0:
            error = completed.stderr.strip().splitlines()
            stable = error[-1] if error else "AWS_COMMAND_FAILED"
            raise RuntimeError(f"AWS_COMMAND_FAILED:{arguments[0]}:{stable}")
        if completed.returncode != 0:
            return None
        if not expect_json:
            return completed.stdout.strip()
        output = completed.stdout.strip()
        return json.loads(output) if output else {}


def require_absent(aws: Aws) -> None:
    if aws.run("lambda", "get-function", "--function-name", NAME, check=False):
        raise RuntimeError("PREEXISTING_LAMBDA")
    if aws.run("iam", "get-role", "--role-name", NAME, check=False):
        raise RuntimeError("PREEXISTING_IAM_ROLE")
    apis = aws.run("apigatewayv2", "get-apis").get("Items", [])
    if [item for item in apis if item.get("Name") == NAME]:
        raise RuntimeError("PREEXISTING_HTTP_API")
    groups = aws.run(
        "logs",
        "describe-log-groups",
        "--log-group-name-prefix",
        LOG_GROUP,
    ).get("logGroups", [])
    if [item for item in groups if item.get("logGroupName") == LOG_GROUP]:
        raise RuntimeError("PREEXISTING_LOG_GROUP")
    alarms = aws.run(
        "cloudwatch", "describe-alarms", "--alarm-name-prefix", NAME
    ).get("MetricAlarms", [])
    if alarms:
        raise RuntimeError("PREEXISTING_ALARM")


def secret_metadata(aws: Aws) -> dict[str, Any]:
    secret = aws.run(
        "secretsmanager", "describe-secret", "--secret-id", SECRET_NAME
    )
    if secret.get("Name") != SECRET_NAME or secret.get("RotationEnabled") is True:
        raise RuntimeError("SECRET_METADATA_INVALID")
    tags = {item.get("Key"): item.get("Value") for item in secret.get("Tags", [])}
    expected = {
        "Project": "cockroach-kernel",
        "Gate": "hardening-2",
        "ManagedBy": "codex",
    }
    if tags != expected:
        raise RuntimeError("SECRET_TAGS_INVALID")
    arn = secret.get("ARN")
    if not isinstance(arn, str) or not arn:
        raise RuntimeError("SECRET_ARN_MISSING")
    return {"arn": arn, "rotation": False, "tags": tags}


def account_id(aws: Aws) -> str:
    identity = aws.run("sts", "get-caller-identity")
    value = identity.get("Account")
    if not isinstance(value, str) or len(value) != 12 or not value.isdigit():
        raise RuntimeError("AWS_ACCOUNT_INVALID")
    return value


def create_policy(runtime_root: Path, account: str, secret_arn: str) -> Path:
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "WriteExactLambdaLogs",
                "Effect": "Allow",
                "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
                "Resource": (
                    f"arn:aws:logs:{REGION}:{account}:"
                    f"log-group:{LOG_GROUP}:*"
                ),
            },
            {
                "Sid": "ReadExactDatabaseSecret",
                "Effect": "Allow",
                "Action": "secretsmanager:GetSecretValue",
                "Resource": secret_arn,
            },
        ],
    }
    path = runtime_root / "lambda-inline-policy.json"
    path.write_bytes(canonical(policy) + b"\n")
    return path


def rollback(aws: Aws, created: list[str], api_id: str | None) -> None:
    if "api" in created and api_id:
        aws.run("apigatewayv2", "delete-api", "--api-id", api_id, check=False)
    if "lambda" in created:
        aws.run("lambda", "delete-function", "--function-name", NAME, check=False)
    if "alarms" in created:
        aws.run(
            "cloudwatch",
            "delete-alarms",
            "--alarm-names",
            *sorted(ALARM_NAMES),
            check=False,
        )
    if "log_group" in created:
        aws.run(
            "logs", "delete-log-group", "--log-group-name", LOG_GROUP, check=False
        )
    if "role" in created:
        aws.run(
            "iam",
            "delete-role-policy",
            "--role-name",
            NAME,
            "--policy-name",
            f"{NAME}-runtime",
            check=False,
        )
        aws.run("iam", "delete-role", "--role-name", NAME, check=False)


def deploy(repo: Path) -> dict[str, Any]:
    aws = Aws(repo)
    require_absent(aws)
    secret = secret_metadata(aws)
    account = account_id(aws)
    runtime_root = repo / ".hardening-runtime/gate2-deploy"
    runtime_root.mkdir(parents=True, exist_ok=True)
    policy_path = create_policy(runtime_root, account, secret["arn"])
    trust_path = repo / "hardening-gate2/lambda-trust-policy.json"
    bundle_path = repo / ".hardening-runtime/gate2-bundle/ck-hardening-demo.zip"
    if sha256(bundle_path) != "1fbcaf5b79a648653a26669b224d78f50239380c0318506c01a5a2df21df3f58":
        raise RuntimeError("BUNDLE_HASH_MISMATCH")

    created: list[str] = []
    api_id: str | None = None
    try:
        role = aws.run(
            "iam",
            "create-role",
            "--role-name",
            NAME,
            "--assume-role-policy-document",
            f"file://{trust_path}",
            "--tags",
            "Key=Project,Value=cockroach-kernel",
            "Key=Gate,Value=hardening-2",
            "Key=ManagedBy,Value=codex",
        )["Role"]
        created.append("role")
        role_arn = role["Arn"]
        aws.run(
            "iam",
            "put-role-policy",
            "--role-name",
            NAME,
            "--policy-name",
            f"{NAME}-runtime",
            "--policy-document",
            f"file://{policy_path}",
        )

        aws.run("logs", "create-log-group", "--log-group-name", LOG_GROUP)
        created.append("log_group")
        aws.run(
            "logs",
            "put-retention-policy",
            "--log-group-name",
            LOG_GROUP,
            "--retention-in-days",
            "1",
        )

        aws.run(
            "cloudwatch",
            "put-metric-alarm",
            "--alarm-name",
            f"{NAME}-errors",
            "--namespace",
            "AWS/Lambda",
            "--metric-name",
            "Errors",
            "--dimensions",
            f"Name=FunctionName,Value={NAME}",
            "--statistic",
            "Sum",
            "--period",
            "60",
            "--evaluation-periods",
            "1",
            "--threshold",
            "1",
            "--comparison-operator",
            "GreaterThanOrEqualToThreshold",
            "--treat-missing-data",
            "notBreaching",
        )
        created.append("alarms")
        aws.run(
            "cloudwatch",
            "put-metric-alarm",
            "--alarm-name",
            f"{NAME}-invocations-5000",
            "--namespace",
            "AWS/Lambda",
            "--metric-name",
            "Invocations",
            "--dimensions",
            f"Name=FunctionName,Value={NAME}",
            "--statistic",
            "Sum",
            "--period",
            "86400",
            "--evaluation-periods",
            "1",
            "--threshold",
            "5000",
            "--comparison-operator",
            "GreaterThanOrEqualToThreshold",
            "--treat-missing-data",
            "notBreaching",
        )

        # IAM role propagation is eventually consistent. Use a bounded retry,
        # without changing any deployment property between attempts.
        function = None
        for delay in (5, 10, 15, 20):
            function = aws.run(
                "lambda",
                "create-function",
                "--function-name",
                NAME,
                "--runtime",
                "python3.12",
                "--role",
                role_arn,
                "--handler",
                "cockroach_kernel.http_api.lambda_handler",
                "--zip-file",
                f"fileb://{bundle_path}",
                "--timeout",
                "8",
                "--memory-size",
                "256",
                "--environment",
                f"Variables={{CK_DEMO_SECRET_ID={SECRET_NAME}}}",
                "--tags",
                "Project=cockroach-kernel,Gate=hardening-2,ManagedBy=codex",
                check=False,
            )
            if function:
                break
            time.sleep(delay)
        if not function:
            raise RuntimeError("LAMBDA_CREATE_FAILED_AFTER_BOUNDED_RETRY")
        created.append("lambda")
        function_arn = function["FunctionArn"]
        aws.run(
            "lambda",
            "wait",
            "function-active-v2",
            "--function-name",
            NAME,
            expect_json=False,
        )

        api = aws.run(
            "apigatewayv2",
            "create-api",
            "--name",
            NAME,
            "--protocol-type",
            "HTTP",
            "--tags",
            "Project=cockroach-kernel,Gate=hardening-2,ManagedBy=codex",
        )
        api_id = api["ApiId"]
        endpoint = api["ApiEndpoint"]
        created.append("api")
        integration = aws.run(
            "apigatewayv2",
            "create-integration",
            "--api-id",
            api_id,
            "--integration-type",
            "AWS_PROXY",
            "--integration-uri",
            function_arn,
            "--payload-format-version",
            "2.0",
            "--timeout-in-millis",
            "8000",
        )
        integration_id = integration["IntegrationId"]
        for route in sorted(ROUTES):
            aws.run(
                "apigatewayv2",
                "create-route",
                "--api-id",
                api_id,
                "--route-key",
                route,
                "--target",
                f"integrations/{integration_id}",
            )
        aws.run(
            "apigatewayv2",
            "create-stage",
            "--api-id",
            api_id,
            "--stage-name",
            "$default",
            "--auto-deploy",
            "--default-route-settings",
            "ThrottlingBurstLimit=2,ThrottlingRateLimit=0.05",
            "--tags",
            "Project=cockroach-kernel,Gate=hardening-2,ManagedBy=codex",
        )
        for suffix, route_path in (
            ("promote", "demo/promote"),
            ("refuse", "demo/refuse"),
        ):
            aws.run(
                "lambda",
                "add-permission",
                "--function-name",
                NAME,
                "--statement-id",
                f"api-{suffix}",
                "--action",
                "lambda:InvokeFunction",
                "--principal",
                "apigateway.amazonaws.com",
                "--source-arn",
                (
                    f"arn:aws:execute-api:{REGION}:{account}:"
                    f"{api_id}/*/GET/{route_path}"
                ),
            )

        verified = verify(repo, expected_api_id=api_id)
        verified["endpoint"] = endpoint
        verified["bundle_sha256"] = sha256(bundle_path)
        verified["inline_policy_sha256"] = sha256(policy_path)
        verified["created_resources"] = sorted(created)
        output = runtime_root / "deployment-result.json"
        output.write_bytes(canonical(verified) + b"\n")
        verified["result_sha256"] = sha256(output)
        return verified
    except Exception:
        rollback(aws, created, api_id)
        raise


def verify(repo: Path, expected_api_id: str | None = None) -> dict[str, Any]:
    aws = Aws(repo)
    secret_metadata(aws)
    function = aws.run("lambda", "get-function-configuration", "--function-name", NAME)
    expected_function = {
        "FunctionName": NAME,
        "Runtime": "python3.12",
        "Handler": "cockroach_kernel.http_api.lambda_handler",
        "MemorySize": 256,
        "Timeout": 8,
    }
    if any(function.get(key) != value for key, value in expected_function.items()):
        raise RuntimeError("LAMBDA_CONFIGURATION_MISMATCH")
    if function.get("Environment", {}).get("Variables") != {
        "CK_DEMO_SECRET_ID": SECRET_NAME
    }:
        raise RuntimeError("LAMBDA_ENVIRONMENT_MISMATCH")

    role = aws.run("iam", "get-role", "--role-name", NAME).get("Role", {})
    if role.get("RoleName") != NAME:
        raise RuntimeError("ROLE_MISSING")
    role_policy = aws.run(
        "iam",
        "get-role-policy",
        "--role-name",
        NAME,
        "--policy-name",
        f"{NAME}-runtime",
    ).get("PolicyDocument", {})
    actions = {
        action
        for statement in role_policy.get("Statement", [])
        for action in (
            statement.get("Action")
            if isinstance(statement.get("Action"), list)
            else [statement.get("Action")]
        )
    }
    if actions != {
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "secretsmanager:GetSecretValue",
    }:
        raise RuntimeError("ROLE_POLICY_ACTIONS_MISMATCH")

    apis = [
        item
        for item in aws.run("apigatewayv2", "get-apis").get("Items", [])
        if item.get("Name") == NAME
    ]
    if len(apis) != 1:
        raise RuntimeError("HTTP_API_COUNT_MISMATCH")
    api = apis[0]
    api_id = api.get("ApiId")
    if expected_api_id and api_id != expected_api_id:
        raise RuntimeError("HTTP_API_ID_MISMATCH")
    routes = aws.run("apigatewayv2", "get-routes", "--api-id", api_id).get(
        "Items", []
    )
    if {item.get("RouteKey") for item in routes} != ROUTES:
        raise RuntimeError("HTTP_API_ROUTES_MISMATCH")
    stage = aws.run(
        "apigatewayv2",
        "get-stage",
        "--api-id",
        api_id,
        "--stage-name",
        "$default",
    )
    settings = stage.get("DefaultRouteSettings", {})
    if settings.get("ThrottlingBurstLimit") != 2 or settings.get(
        "ThrottlingRateLimit"
    ) != 0.05:
        raise RuntimeError("HTTP_API_THROTTLE_MISMATCH")

    groups = aws.run(
        "logs", "describe-log-groups", "--log-group-name-prefix", LOG_GROUP
    ).get("logGroups", [])
    exact_groups = [item for item in groups if item.get("logGroupName") == LOG_GROUP]
    if len(exact_groups) != 1 or exact_groups[0].get("retentionInDays") != 1:
        raise RuntimeError("LOG_RETENTION_MISMATCH")
    alarms = aws.run(
        "cloudwatch", "describe-alarms", "--alarm-name-prefix", NAME
    ).get("MetricAlarms", [])
    if {item.get("AlarmName") for item in alarms} != ALARM_NAMES:
        raise RuntimeError("ALARM_SET_MISMATCH")
    if any(item.get("ActionsEnabled") is False for item in alarms):
        raise RuntimeError("ALARM_DISABLED")

    policy = aws.run("lambda", "get-policy", "--function-name", NAME)
    statements = json.loads(policy["Policy"]).get("Statement", [])
    statement_ids = {item.get("Sid") for item in statements}
    if statement_ids != {"api-promote", "api-refuse"}:
        raise RuntimeError("LAMBDA_RESOURCE_POLICY_MISMATCH")

    endpoint = api.get("ApiEndpoint")
    if not isinstance(endpoint, str) or not endpoint.startswith("https://"):
        raise RuntimeError("HTTP_API_ENDPOINT_INVALID")
    return {
        "status": "DEPLOYED_CONFIGURATION_GREEN",
        "api_id": api_id,
        "endpoint": endpoint,
        "routes": sorted(ROUTES),
        "runtime": function.get("Runtime"),
        "memory_mib": function.get("MemorySize"),
        "timeout_seconds": function.get("Timeout"),
        "stage_rate_limit_per_second": settings.get("ThrottlingRateLimit"),
        "stage_burst_limit": settings.get("ThrottlingBurstLimit"),
        "log_retention_days": exact_groups[0].get("retentionInDays"),
        "alarms": sorted(ALARM_NAMES),
        "iam_actions": sorted(actions),
        "secret_value_read": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--action", choices=("deploy", "verify"), default="deploy")
    args = parser.parse_args()
    result = (
        deploy(args.repo.resolve())
        if args.action == "deploy"
        else verify(args.repo.resolve())
    )
    print(canonical(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
