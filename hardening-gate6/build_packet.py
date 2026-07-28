#!/usr/bin/env python3
"""Build the byte-complete sanitized Gate 6 preflight packet."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path


HEADER = """# Hardening Gate 6 — Same-Hash Preflight Judge Packet R2

## Judge contract

This is a non-authoring, sanitized, pre-provider review. Return a structured
verdict only. Do not write code, propose patches, direct implementation,
request tools or credentials, or claim execution. Review every included byte
as one packet. The external SHA-256 supplied with this packet is canonical.

Required verdict schema:

```json
{"verdict":"GREEN|NOT_GREEN|BLOCKED","candidate_immutability":"GREEN|NOT_GREEN","fairness_and_pairing":"GREEN|NOT_GREEN","runtime_isolation":"GREEN|NOT_GREEN","evidence_and_statistics":"GREEN|NOT_GREEN","lifecycle_and_teardown":"GREEN|NOT_GREEN","blockers":[],"limitations":[],"recusal":"CLEAR|REQUIRED"}
```

GREEN means the packet is safe and complete enough to create one reviewed CPU
worker and execute the frozen 54-row campaign. It does not predict a favorable
product result and does not approve later gates.

Control state: parent Gate 5 R2 is independently GREEN; orchestration commit is
`{orchestration_commit}`; immutable candidate is `{candidate_commit}`; current
RunPod running inventory is empty; no Gate 6 R2 worker or measured row exists.
"""


def atomic_write(path: Path, raw: bytes) -> None:
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
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--orchestration-commit", required=True)
    parser.add_argument("--candidate-commit", required=True)
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()
    for label, value in (
        ("orchestration commit", args.orchestration_commit),
        ("candidate commit", args.candidate_commit),
    ):
        if len(value) != 40 or any(character not in "0123456789abcdef" for character in value):
            raise SystemExit(f"invalid {label}: {value!r}")
    header = HEADER.format(
        orchestration_commit=args.orchestration_commit,
        candidate_commit=args.candidate_commit,
    )
    sections = [header.rstrip(), ""]
    for path in args.files:
        raw = path.read_text(encoding="utf-8")
        sections.extend((f"## FILE: {path.as_posix()}", "", "```text",
                         raw.rstrip(), "```", ""))
    packet = "\n".join(sections).encode("utf-8")
    atomic_write(args.output.resolve(), packet)
    print(hashlib.sha256(packet).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
