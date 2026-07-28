#!/usr/bin/env python3
"""Fixed public helper for OS-enforced R3 Seatbelt canaries."""
from __future__ import annotations

import json
from pathlib import Path
import socket
import subprocess
import sys


def emit(action: str, result: str, detail: str = "") -> int:
    print(json.dumps({"action": action, "detail": detail, "result": result}, sort_keys=True))
    return 0 if result == "ALLOWED" else 77


def main() -> int:
    action, target = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ""
    try:
        if action == "read":
            Path(target).read_bytes()
        elif action == "expect":
            if Path(target).read_bytes() != b"r3-canary\n":
                return emit(action, "ERROR", "CONTENT_MISMATCH")
        elif action == "write":
            Path(target).write_bytes(b"r3-canary\n")
        elif action == "ipv4":
            socket.create_connection(("127.0.0.1", 9), timeout=0.2)
        elif action == "ipv6":
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            try:
                sock.settimeout(0.2)
                sock.connect(("::1", 9))
            finally:
                sock.close()
        elif action == "dns":
            socket.getaddrinfo("r3-canary.invalid", 443)
        elif action == "child":
            subprocess.run(["/bin/echo", "escape"], check=True)
        else:
            return emit(action, "ERROR", "UNKNOWN_ACTION")
    except (OSError, PermissionError, subprocess.SubprocessError) as exc:
        return emit(action, "DENIED", f"{type(exc).__name__}:{getattr(exc, 'errno', None)}")
    return emit(action, "ALLOWED")


if __name__ == "__main__":
    raise SystemExit(main())
