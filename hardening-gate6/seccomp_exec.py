#!/usr/bin/env python3
"""Install an inherited, fail-closed network-denial seccomp filter and exec.

This launcher is Gate 6 execution infrastructure. It is not product code.  It
must run as an unprivileged Linux x86_64 user with no effective capabilities.
The filter is installed after ``no_new_privs`` and is inherited by every child.
"""
from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
from typing import Any


AUDIT_ARCH_X86_64 = 0xC000003E
BPF_LD = 0x00
BPF_W = 0x00
BPF_ABS = 0x20
BPF_JMP = 0x05
BPF_JEQ = 0x10
BPF_K = 0x00
BPF_RET = 0x06
SECCOMP_RET_KILL_PROCESS = 0x80000000
SECCOMP_RET_ERRNO = 0x00050000
SECCOMP_RET_ALLOW = 0x7FFF0000
PR_SET_NO_NEW_PRIVS = 38
PR_SET_SECCOMP = 22
SECCOMP_MODE_FILTER = 2

# Linux x86_64. Socket operations are denied directly. The additional entries
# close alternate kernel interfaces that can submit network work or acquire a
# socket descriptor without calling socket(2) in the filtered process.
DENIED_SYSCALLS = {
    "socket": 41,
    "connect": 42,
    "accept": 43,
    "sendto": 44,
    "recvfrom": 45,
    "sendmsg": 46,
    "recvmsg": 47,
    "shutdown": 48,
    "bind": 49,
    "listen": 50,
    "getsockname": 51,
    "getpeername": 52,
    "socketpair": 53,
    "setsockopt": 54,
    "getsockopt": 55,
    "unshare": 272,
    "accept4": 288,
    "recvmmsg": 299,
    "setns": 308,
    "sendmmsg": 307,
    "bpf": 321,
    "io_uring_setup": 425,
    "io_uring_enter": 426,
    "io_uring_register": 427,
    "pidfd_getfd": 438,
}


class SockFilter(ctypes.Structure):
    _fields_ = [
        ("code", ctypes.c_ushort),
        ("jt", ctypes.c_ubyte),
        ("jf", ctypes.c_ubyte),
        ("k", ctypes.c_uint32),
    ]


class SockFprog(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ushort),
        ("filter", ctypes.POINTER(SockFilter)),
    ]


class IsolationError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


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


def proc_status() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key] = value.strip()
    return values


def inherited_socket_fds() -> list[int]:
    found: list[int] = []
    for entry in Path("/proc/self/fd").iterdir():
        try:
            descriptor = int(entry.name)
            target = os.readlink(entry)
        except (OSError, ValueError):
            continue
        if descriptor > 2 and target.startswith("socket:["):
            found.append(descriptor)
    return sorted(found)


def filter_spec() -> dict[str, Any]:
    return {
        "architecture": "x86_64",
        "audit_arch": AUDIT_ARCH_X86_64,
        "default_action": "ALLOW",
        "denied_action": "ERRNO_EPERM",
        "denied_syscalls": dict(sorted(DENIED_SYSCALLS.items())),
        "foreign_arch_action": "KILL_PROCESS",
        "version": "hardening-gate6-seccomp-network-deny-v1",
    }


def build_filter() -> tuple[Any, SockFprog]:
    instructions = [
        SockFilter(BPF_LD | BPF_W | BPF_ABS, 0, 0, 4),
        SockFilter(BPF_JMP | BPF_JEQ | BPF_K, 1, 0, AUDIT_ARCH_X86_64),
        SockFilter(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_KILL_PROCESS),
        SockFilter(BPF_LD | BPF_W | BPF_ABS, 0, 0, 0),
    ]
    for number in sorted(set(DENIED_SYSCALLS.values())):
        instructions.extend((
            SockFilter(BPF_JMP | BPF_JEQ | BPF_K, 0, 1, number),
            SockFilter(BPF_RET | BPF_K, 0, 0,
                       SECCOMP_RET_ERRNO | errno.EPERM),
        ))
    instructions.append(SockFilter(BPF_RET | BPF_K, 0, 0, SECCOMP_RET_ALLOW))
    array_type = SockFilter * len(instructions)
    filters = array_type(*instructions)
    return filters, SockFprog(len(instructions), filters)


def install_filter() -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                           ctypes.c_ulong, ctypes.c_ulong]
    libc.prctl.restype = ctypes.c_int
    if libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:
        value = ctypes.get_errno()
        raise IsolationError(f"NO_NEW_PRIVS_FAILED:{value}")
    filters, program = build_filter()
    if libc.prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER,
                  ctypes.cast(ctypes.pointer(program), ctypes.c_void_p).value,
                  0, 0) != 0:
        value = ctypes.get_errno()
        raise IsolationError(f"SECCOMP_FILTER_FAILED:{value}")
    # Keep the backing array alive until prctl has copied the filter.
    del filters


def network_probe() -> int:
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError as error:
        if error.errno == errno.EPERM:
            return error.errno
        raise IsolationError(f"NETWORK_PROBE_WRONG_ERRNO:{error.errno}") from error
    raise IsolationError("NETWORK_PROBE_UNEXPECTEDLY_ALLOWED")


def validate_host() -> dict[str, Any]:
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise IsolationError("PLATFORM_MUST_BE_LINUX_X86_64")
    if os.geteuid() == 0 or os.getuid() == 0:
        raise IsolationError("USER_MUST_BE_UNPRIVILEGED")
    status = proc_status()
    if int(status.get("CapEff", "-1"), 16) != 0:
        raise IsolationError("EFFECTIVE_CAPABILITIES_MUST_BE_ZERO")
    sockets = inherited_socket_fds()
    if sockets:
        raise IsolationError("INHERITED_SOCKET_FD_PRESENT")
    return {"cap_eff": status["CapEff"], "inherited_socket_fds": sockets}


def attest(path: Path) -> dict[str, Any]:
    status = proc_status()
    if status.get("NoNewPrivs") != "1" or status.get("Seccomp") != "2":
        raise IsolationError("KERNEL_STATUS_ATTESTATION_FAILED")
    socket_errno = network_probe()
    result = subprocess.run(["/bin/true"], check=False)
    if result.returncode != 0:
        raise IsolationError("EXEC_CANARY_FAILED")
    record: dict[str, Any] = {
        "version": "hardening-gate6-isolation-attestation-v1",
        "uid": os.getuid(),
        "euid": os.geteuid(),
        "gid": os.getgid(),
        "egid": os.getegid(),
        "cap_eff": status["CapEff"],
        "no_new_privs": int(status["NoNewPrivs"]),
        "seccomp_mode": int(status["Seccomp"]),
        "seccomp_filters": int(status.get("Seccomp_filters", "1")),
        "network_socket_probe_errno": socket_errno,
        "network_socket_probe_result": "DENIED_EPERM",
        "exec_canary": "PASS",
        "inherited_socket_fds": [],
        "filter_spec": filter_spec(),
        "filter_spec_sha256": digest(filter_spec()),
    }
    record["attestation_sha256"] = digest(record)
    atomic_write(path, canonical(record))
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attestation", required=True, type=Path)
    parser.add_argument("--canary-only", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    host = validate_host()
    install_filter()
    record = attest(args.attestation.resolve())
    if args.canary_only:
        print(canonical({"status": "GREEN", **host,
                         "attestation_sha256": record["attestation_sha256"]}).decode())
        return 0
    if not args.command:
        raise IsolationError("COMMAND_REQUIRED")
    environment = dict(os.environ)
    environment["CK_GATE6_ISOLATION_ATTESTATION"] = str(args.attestation.resolve())
    environment["CK_GATE6_ISOLATION_ATTESTATION_SHA256"] = record["attestation_sha256"]
    os.execvpe(args.command[0], args.command, environment)
    return 127


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IsolationError as error:
        print(f"ISOLATION_BLOCKED:{error}", file=sys.stderr)
        raise SystemExit(70)
