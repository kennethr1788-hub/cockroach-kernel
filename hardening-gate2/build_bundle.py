#!/usr/bin/env python3
"""Build and verify the deterministic Gate 2 Lambda deployment bundle.

The build root is project-local and disposable. Source comes only from the
current checkout plus the pinned ``aws-demo`` dependency group. Zip metadata
is normalized so identical installed bytes produce identical archives.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
EXCLUDED_PARTS = {"__pycache__", ".git"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def include(path: Path) -> bool:
    return (
        not any(part in EXCLUDED_PARTS for part in path.parts)
        and path.suffix not in EXCLUDED_SUFFIXES
        and not path.name.startswith("test_")
    )


def build(repo: Path, output: Path) -> dict[str, object]:
    repo = repo.resolve()
    output = output.resolve()
    runtime_root = (repo / ".hardening-runtime").resolve()
    if runtime_root not in output.parents:
        raise RuntimeError("OUTPUT_OUTSIDE_PROJECT_RUNTIME")
    if output.exists():
        shutil.rmtree(output)
    stage = output / "stage"
    stage.mkdir(parents=True)

    pip_environment = os.environ.copy()
    pip_environment["PIP_NO_CACHE_DIR"] = "1"
    pip_environment["PYTHONDONTWRITEBYTECODE"] = "1"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-input",
            "--target",
            str(stage),
            ".[aws-demo]",
        ],
        cwd=repo,
        env=pip_environment,
        check=True,
    )

    verifier_source = repo / "p4-verifier"
    verifier_target = stage / "p4-verifier"
    verifier_target.mkdir()
    for name in ("__init__.py", "verifier.py"):
        shutil.copy2(verifier_source / name, verifier_target / name)

    subprocess.run(
        [
            sys.executable,
            str(repo / "hardening-gate2" / "smoke_bundle.py"),
        ],
        cwd=repo,
        env=dict(pip_environment, PYTHONPATH=str(stage)),
        check=True,
    )

    archive = output / "ck-hardening-demo.zip"
    files = sorted(path for path in stage.rglob("*") if path.is_file() and include(path.relative_to(stage)))
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in files:
            relative = path.relative_to(stage).as_posix()
            info = zipfile.ZipInfo(relative, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    distributions = []
    for distribution in importlib.metadata.distributions(path=[str(stage)]):
        name = distribution.metadata.get("Name")
        version = distribution.version
        if name and version:
            distributions.append({"name": name, "version": version})
    distributions.sort(key=lambda item: (item["name"].lower(), item["version"]))

    manifest = {
        "version": "ck-hardening-gate2-bundle-v1",
        "handler": "cockroach_kernel.http_api.lambda_handler",
        "python": sys.version.split()[0],
        "archive": archive.name,
        "archive_sha256": sha256(archive),
        "archive_bytes": archive.stat().st_size,
        "file_count": len(files),
        "distributions": distributions,
        "source_hashes": {
            "cockroach_kernel/http_api.py": sha256(repo / "cockroach_kernel/http_api.py"),
            "cockroach_kernel/cli.py": sha256(repo / "cockroach_kernel/cli.py"),
            "p9-cloud/live_completion.py": sha256(repo / "p9-cloud/live_completion.py"),
            "p9-cloud/lambda_handler.py": sha256(repo / "p9-cloud/lambda_handler.py"),
            "p4-verifier/verifier.py": sha256(repo / "p4-verifier/verifier.py"),
            "pyproject.toml": sha256(repo / "pyproject.toml"),
        },
    }
    manifest_path = output / "bundle-manifest.json"
    manifest_path.write_bytes(canonical(manifest) + b"\n")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.cwd() / ".hardening-runtime" / "gate2-bundle",
    )
    args = parser.parse_args()
    print(canonical(build(args.repo, args.output)).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
