#!/usr/bin/env python3
"""Launch the reviewed Kimi worker with max effort in its isolated config only.

This does not modify the canonical HOME wrapper or Kimi configuration. It verifies
the reviewed wrapper hash, applies one exact in-memory source transformation, checks
the generated shell syntax, executes it from a private temporary file, then removes
that file.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import tempfile


SOURCE_WRAPPER = Path("/Users/kennethruedas/.hermes/scripts/kimi-codex-worker.sh")
SOURCE_SHA256 = "d21dc965c06729079571b26389afa00f6d731f35532f4ec0752e10d3712468ee"

OLD_BLOCK = '''if model_config.get("default_effort") != "max" or "max" not in model_config.get("support_efforts", []):
    raise SystemExit("managed K3 max-effort contract missing")
out = {
'''

NEW_BLOCK = '''if "max" not in model_config.get("support_efforts", []):
    raise SystemExit("managed K3 max-effort capability missing")
# Force max only in the isolated config written below. Never mutate the source config.
model_config = dict(model_config)
model_config["default_effort"] = "max"
data["models"][model] = model_config
out = {
'''


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_patched_wrapper() -> bytes:
    source = SOURCE_WRAPPER.read_bytes()
    actual = sha256_bytes(source)
    if actual != SOURCE_SHA256:
        raise SystemExit(f"source wrapper hash drifted: {actual}")
    text = source.decode("utf-8")
    if text.count(OLD_BLOCK) != 1:
        raise SystemExit("expected max-effort block not found exactly once")
    patched = text.replace(OLD_BLOCK, NEW_BLOCK, 1).encode("utf-8")
    if patched == source:
        raise SystemExit("wrapper transformation made no change")
    return patched


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args, remainder = parser.parse_known_args()
    patched = build_patched_wrapper()

    with tempfile.NamedTemporaryFile(prefix="ck-p9-kimi-worker-", suffix=".sh", delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(patched)
    try:
        temp_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        subprocess.run(["/bin/bash", "-n", str(temp_path)], check=True)
        if args.self_test:
            print(f"SOURCE_SHA256={SOURCE_SHA256}")
            print(f"PATCHED_SHA256={sha256_bytes(patched)}")
            print("MAX_EFFORT_ISOLATED_PATCH=GREEN")
            return 0
        if not remainder:
            raise SystemExit("worker arguments are required")
        return subprocess.run([str(temp_path), *remainder], check=False).returncode
    finally:
        temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
