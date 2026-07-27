#!/usr/bin/env python3
"""Create the one authorized Gate 2 database secret without logging its value.

Kenneth enters the dedicated read-only SQL password through ``getpass``. The
``--clipboard`` mode reads a provider-generated value through macOS ``pbpaste``
when a shared terminal makes an interactive prompt unsafe. The secret payload
travels to the project-local AWS CLI through stdin, never argv, stdout, a file,
shell history, or a receipt.
"""
from __future__ import annotations

from getpass import getpass
import json
import os
from pathlib import Path
import subprocess
import sys


SECRET_NAME = "ck-hardening-demo-db"
DEMO_USER = "ck_hardening_demo"
DATABASE = "cockroach_kernel"
MIN_PASSWORD_LENGTH = 20


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    config_path = repo / ".s3-runtime" / "live-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    aws = Path(config["aws_cli"])
    if not aws.is_file():
        print("PROJECT_AWS_CLI_UNAVAILABLE", file=sys.stderr)
        return 2
    environment = os.environ.copy()
    environment.update(
        {
            "AWS_CONFIG_FILE": str(repo / ".s3-runtime" / "aws-auth" / "config"),
            "AWS_LOGIN_CACHE_DIRECTORY": str(repo / ".s3-runtime" / "aws-auth" / "login-cache"),
            "AWS_SHARED_CREDENTIALS_FILE": "/dev/null",
        }
    )
    base = [str(aws), "--profile", "ck-s3", "--region", "us-west-2"]
    exists = subprocess.run(
        base + ["secretsmanager", "describe-secret", "--secret-id", SECRET_NAME],
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if exists.returncode == 0:
        print("SECRET_ALREADY_EXISTS", file=sys.stderr)
        return 3

    arguments = sys.argv[1:]
    if not arguments:
        password = getpass("Paste the dedicated ck_hardening_demo password (hidden): ")
    elif arguments == ["--clipboard"]:
        clipboard = subprocess.run(
            ["/usr/bin/pbpaste"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if clipboard.returncode != 0:
            print("CLIPBOARD_READ_FAILED", file=sys.stderr)
            return 4
        password = clipboard.stdout.decode("utf-8")
        clipboard = None
    else:
        print("USAGE: create_secret.py [--clipboard]", file=sys.stderr)
        return 2
    # CockroachDB Cloud currently generates a 22-character high-entropy
    # credential. Accept that provider-generated shape while still rejecting
    # short or malformed manual input.
    if len(password) < MIN_PASSWORD_LENGTH or "\x00" in password:
        print("PASSWORD_INPUT_INVALID", file=sys.stderr)
        return 4
    secret_value = {
        "database": DATABASE,
        "host": config["cockroach_host"],
        "password": password,
        "port": 26257,
        "user": DEMO_USER,
    }
    request = {
        "Name": SECRET_NAME,
        "Description": "Read-only CockroachDB identity for the bounded Hardening Gate 2 demo",
        "SecretString": json.dumps(secret_value, sort_keys=True, separators=(",", ":")),
        "Tags": [
            {"Key": "Project", "Value": "cockroach-kernel"},
            {"Key": "Gate", "Value": "hardening-2"},
            {"Key": "ManagedBy", "Value": "codex"},
        ],
    }
    password = ""
    secret_value.clear()
    completed = subprocess.run(
        base
        + [
            "secretsmanager",
            "create-secret",
            "--cli-input-json",
            "file:///dev/stdin",
        ],
        env=environment,
        input=(json.dumps(request, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    request.clear()
    if completed.returncode != 0:
        print("SECRET_CREATE_FAILED", file=sys.stderr)
        return 5
    verified = subprocess.run(
        base + ["secretsmanager", "describe-secret", "--secret-id", SECRET_NAME],
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if verified.returncode != 0:
        print("SECRET_READBACK_FAILED", file=sys.stderr)
        return 6
    print("HARDENING_GATE2_SECRET_CREATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
