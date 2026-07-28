#!/usr/bin/env python3
"""Public-fixture feasibility probe for the frozen black-box candidate."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_COMMIT = "8718fbecc2b145ff36ce8c3ed655e92b5906aeab"
EXPECTED_PYPROJECT_SHA256 = "ca8d0a873ddfa1d628f54ef5ca989b88e087b967f7d366bca66d8b59249b6dbd"
EXPECTED_CLI_SHA256 = "98c0dc51de474a472d49fe014910bfb7d30454a851ba390e66ebe1aeea5a9caf"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def minimal_environment(root: Path) -> dict[str, str]:
    path_value = os.environ.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin")
    return {
        "HOME": str(root / "empty-home"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": path_value,
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(REPOSITORY_ROOT),
        "TMPDIR": str(root / "tmp"),
    }


def run_command(
    arguments: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def write_scenario(root: Path, label: str) -> dict[str, str]:
    (root / "src").mkdir(parents=True)
    (root / "notes").mkdir(parents=True)
    (root / "task.json").write_bytes(
        canonical_bytes(
            {
                "scenario": label,
                "goal": f"continue feature {label}",
                "declared_paths": ["src/feature.py", "notes/human-edit.md"],
            }
        )
        + b"\n"
    )
    (root / "src" / "feature.py").write_text(
        f"def value():\n    return {label!r}\n",
        encoding="utf-8",
    )
    (root / "notes" / "human-edit.md").write_text(
        f"independent saved edit for {label}\n",
        encoding="utf-8",
    )
    return manifest(root)


def probe() -> dict[str, Any]:
    pyproject_hash = sha256_file(REPOSITORY_ROOT / "pyproject.toml")
    cli_hash = sha256_file(REPOSITORY_ROOT / "cockroach_kernel" / "cli.py")
    if pyproject_hash != EXPECTED_PYPROJECT_SHA256 or cli_hash != EXPECTED_CLI_SHA256:
        raise RuntimeError("FROZEN_CANDIDATE_HASH_MISMATCH")

    temporary_root = Path(tempfile.mkdtemp(prefix="ck-black-box-surface-"))
    result: dict[str, Any]
    try:
        (temporary_root / "empty-home").mkdir()
        (temporary_root / "tmp").mkdir()
        workspace_a = temporary_root / "workspace-a"
        workspace_b = temporary_root / "workspace-b"
        workspace_a.mkdir()
        workspace_b.mkdir()
        output_a = temporary_root / "output-a"
        output_b = temporary_root / "output-b"
        before_a = write_scenario(workspace_a, "alpha")
        before_b = write_scenario(workspace_b, "omega")
        environment = minimal_environment(temporary_root)

        base_command = [sys.executable, "-m", "cockroach_kernel.cli"]
        help_result = run_command(base_command + ["--help"], cwd=workspace_a, environment=environment)
        demo_help = run_command(base_command + ["demo", "--help"], cwd=workspace_a, environment=environment)
        run_a = run_command(
            base_command + ["demo", "--json", "--output-root", str(output_a)],
            cwd=workspace_a,
            environment=environment,
        )
        run_b = run_command(
            base_command + ["demo", "--json", "--output-root", str(output_b)],
            cwd=workspace_b,
            environment=environment,
        )

        parsed_a = json.loads(run_a.stdout) if run_a.returncode == 0 else None
        parsed_b = json.loads(run_b.stdout) if run_b.returncode == 0 else None
        after_a = manifest(workspace_a)
        after_b = manifest(workspace_b)
        output_manifest_a = manifest(output_a) if output_a.is_dir() else {}
        output_manifest_b = manifest(output_b) if output_b.is_dir() else {}

        help_text = help_result.stdout + help_result.stderr
        demo_help_text = demo_help.stdout + demo_help.stderr
        declared_input_flags = sorted(
            token
            for token in (
                "--workspace",
                "--input-root",
                "--capsule",
                "--scenario",
                "--task",
                "--manifest",
                "--receipt",
            )
            if token in demo_help_text
        )
        outputs_identical = parsed_a == parsed_b and output_manifest_a == output_manifest_b
        workspaces_distinct = before_a != before_b
        workspaces_unchanged = before_a == after_a and before_b == after_b
        scenario_binding_proved = bool(declared_input_flags) and not outputs_identical
        status = "SURFACE_GREEN" if scenario_binding_proved else "SURFACE_BLOCKED"
        blocker = None if scenario_binding_proved else "FROZEN_CLI_NOT_SCENARIO_DRIVEN"

        result = {
            "schema_version": "black-box-surface-probe-v1",
            "candidate_commit": CANDIDATE_COMMIT,
            "candidate_hashes": {
                "pyproject_toml": pyproject_hash,
                "cockroach_kernel_cli_py": cli_hash,
            },
            "commands": {
                "help_exit": help_result.returncode,
                "demo_help_exit": demo_help.returncode,
                "demo_a_exit": run_a.returncode,
                "demo_b_exit": run_b.returncode,
            },
            "public_commands": ["demo", "inspect"] if "{demo,inspect}" in help_text else [],
            "declared_demo_input_flags": declared_input_flags,
            "workspace_a_manifest_hash": sha256_bytes(canonical_bytes(before_a)),
            "workspace_b_manifest_hash": sha256_bytes(canonical_bytes(before_b)),
            "workspaces_distinct": workspaces_distinct,
            "workspaces_unchanged": workspaces_unchanged,
            "demo_outputs_identical": outputs_identical,
            "demo_a_summary_hash": parsed_a.get("summary_hash") if isinstance(parsed_a, dict) else None,
            "demo_b_summary_hash": parsed_b.get("summary_hash") if isinstance(parsed_b, dict) else None,
            "output_manifest_a_hash": sha256_bytes(canonical_bytes(output_manifest_a)),
            "output_manifest_b_hash": sha256_bytes(canonical_bytes(output_manifest_b)),
            "scenario_binding_proved": scenario_binding_proved,
            "status": status,
            "blocker": blocker,
        }
    finally:
        shutil.rmtree(temporary_root, ignore_errors=False)
    result["teardown_verified"] = not temporary_root.exists()
    result["probe_hash"] = sha256_bytes(canonical_bytes(result))
    return result


def main() -> int:
    result = probe()
    print(canonical_bytes(result).decode("utf-8"))
    return 0 if result["status"] == "SURFACE_GREEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
