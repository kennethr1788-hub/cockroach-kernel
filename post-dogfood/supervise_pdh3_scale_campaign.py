#!/usr/bin/env python3
"""Bounded host-side supervisor for one PDH-3 RunPod campaign worker.

The supervisor never interprets successful retrieval or teardown as campaign
success.  It validates the retrieved evidence semantically, records an explicit
campaign terminal state, and attempts exact-worker teardown in ``finally``.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import subprocess
import sys
import tarfile
import time
from typing import Any


GREEN_PENDING_FINAL_GATE = "GREEN_PENDING_FINAL_GATE"
BLOCKED_COMPLETE = "BLOCKED_COMPLETE"
ABSENT_RESULT = "ABSENT_RESULT"
PARTIAL_ARCHIVE = "PARTIAL_ARCHIVE"
TRANSPORT_FAILURE = "TRANSPORT_FAILURE"
TEARDOWN_UNPROVEN = "TEARDOWN_UNPROVEN"

EXIT_CODES = {
    GREEN_PENDING_FINAL_GATE: 0,
    BLOCKED_COMPLETE: 2,
    ABSENT_RESULT: 3,
    PARTIAL_ARCHIVE: 4,
    TRANSPORT_FAILURE: 5,
    TEARDOWN_UNPROVEN: 6,
}

INACTIVE_STATES = {"EXITED", "TERMINATED", "DELETED"}

TERMINAL_EVIDENCE_RECORDS = {
    "evidence/result.json",
    "evidence/MEASURED_CAMPAIGN_GREEN",
}


def load_contract() -> Any:
    path = Path(__file__).resolve().with_name("pdh3_scale_contract.py")
    spec = importlib.util.spec_from_file_location("pdh3_supervisor_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("PDH3_CONTRACT_IMPORT_SPEC_INVALID")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CONTRACT = load_contract()


class SupervisorFailure(RuntimeError):
    pass


class TransportFailure(SupervisorFailure):
    pass


class ArchiveFailure(SupervisorFailure):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes | Any) -> str:
    value = raw if isinstance(raw, bytes) else canonical(raw)
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


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
        temporary.unlink(missing_ok=True)


class ChainLog:
    def __init__(self, path: Path) -> None:
        if path.exists():
            raise SupervisorFailure("LOG_ALREADY_EXISTS")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.previous = "0" * 64
        self.sequence = 0

    def emit(self, event: str, details: dict[str, Any]) -> dict[str, Any]:
        self.sequence += 1
        body = {
            "version": "ck-pdh3-supervisor-log-v1",
            "sequence": self.sequence,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "previous_hash": self.previous,
            "event": event,
            "details": details,
        }
        record = {**body, "event_hash": digest(body)}
        with self.path.open("ab") as handle:
            handle.write(canonical(record) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.previous = record["event_hash"]
        return record


@dataclass(frozen=True)
class Config:
    runpodctl: Path
    runpodctl_sha256: str
    pod_id: str
    pod_name: str
    campaign_prefix: str
    ssh_config: Path
    ssh_alias: str
    remote_root: str
    retrieval: Path
    log: Path
    packet_sha256: str
    trace_tool_sha256: str
    trace_command_sha256: str
    closeout_deadline_epoch: float
    poll_seconds: float = 300.0
    command_timeout_seconds: int = 60
    transfer_timeout_seconds: int = 1_800
    teardown_reserve_seconds: int = 300


def run_command(
    command: list[str], *, timeout: float, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    if timeout <= 0:
        raise TransportFailure("COMMAND_DEADLINE_EXCEEDED")
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TransportFailure("COMMAND_TIMEOUT:" + Path(command[0]).name) from exc


def bounded_timeout(
    deadline_epoch: float,
    maximum_seconds: float,
    *,
    reserve_seconds: float = 0,
) -> float:
    remaining = deadline_epoch - time.time() - reserve_seconds
    if remaining <= 0:
        raise TransportFailure("CLOSEOUT_DEADLINE_EXCEEDED")
    return max(0.1, min(maximum_seconds, remaining))


def validate_config(config: Config) -> None:
    if not re.fullmatch(r"[0-9a-f]{64}", config.runpodctl_sha256):
        raise SupervisorFailure("RUNPODCTL_SHA256_INVALID")
    for label, value in (
        ("PACKET", config.packet_sha256),
        ("TRACE_TOOL", config.trace_tool_sha256),
        ("TRACE_COMMAND", config.trace_command_sha256),
    ):
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise SupervisorFailure(label + "_SHA256_INVALID")
    if not config.pod_name.startswith(config.campaign_prefix):
        raise SupervisorFailure("CAMPAIGN_IDENTITY_INVALID")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", config.ssh_alias):
        raise SupervisorFailure("SSH_ALIAS_INVALID")
    remote = PurePosixPath(config.remote_root)
    if not remote.is_absolute() or ".." in remote.parts or "\x00" in config.remote_root:
        raise SupervisorFailure("REMOTE_ROOT_INVALID")
    if config.closeout_deadline_epoch <= time.time():
        raise SupervisorFailure("CLOSEOUT_DEADLINE_INVALID")
    if not 0.1 <= config.poll_seconds <= 600:
        raise SupervisorFailure("POLL_SECONDS_INVALID")
    if not 1 <= config.command_timeout_seconds <= 300:
        raise SupervisorFailure("COMMAND_TIMEOUT_INVALID")
    if not 1 <= config.transfer_timeout_seconds <= 10_800:
        raise SupervisorFailure("TRANSFER_TIMEOUT_INVALID")
    if not 1 <= config.teardown_reserve_seconds <= 1_800:
        raise SupervisorFailure("TEARDOWN_RESERVE_INVALID")


def verify_cli(config: Config) -> None:
    cli = config.runpodctl.resolve()
    if not cli.is_file() or not os.access(cli, os.X_OK):
        raise SupervisorFailure("RUNPODCTL_NOT_EXECUTABLE")
    if sha256_file(cli) != config.runpodctl_sha256:
        raise SupervisorFailure("RUNPODCTL_SHA256_MISMATCH")


def ssh(config: Config, command: str, *, reserve_seconds: float = 0) -> subprocess.CompletedProcess[str]:
    timeout = bounded_timeout(
        config.closeout_deadline_epoch,
        config.command_timeout_seconds,
        reserve_seconds=reserve_seconds,
    )
    return run_command(
        ["ssh", "-F", str(config.ssh_config), config.ssh_alias, command],
        timeout=timeout,
    )


def remote_state(config: Config, log: ChainLog) -> str:
    root = shlex.quote(config.remote_root)
    command = (
        f"ROOT={root}; "
        'if test -f "$ROOT/network-receipt.json"; then echo TERMINAL; '
        'elif test -f "$ROOT/production.pid" && '
        'kill -0 "$(tr -d \'\\n\' < "$ROOT/production.pid")" 2>/dev/null; '
        "then echo RUNNING; else echo TERMINAL; fi"
    )
    try:
        result = ssh(
            config,
            command,
            reserve_seconds=config.teardown_reserve_seconds,
        )
    except TransportFailure as exc:
        log.emit("REMOTE_STATE_UNAVAILABLE", {"reason": str(exc)})
        return "UNAVAILABLE"
    if result.returncode != 0:
        log.emit(
            "REMOTE_STATE_UNAVAILABLE",
            {"returncode": result.returncode, "stderr_sha256": digest(result.stderr.encode())},
        )
        return "UNAVAILABLE"
    value = result.stdout.strip()
    if value not in {"RUNNING", "TERMINAL"}:
        log.emit("REMOTE_STATE_UNAVAILABLE", {"value_sha256": digest(value.encode())})
        return "UNAVAILABLE"
    return value


def wait_for_terminal(config: Config, log: ChainLog) -> bool:
    cutoff = config.closeout_deadline_epoch - config.teardown_reserve_seconds
    while time.time() < cutoff:
        state = remote_state(config, log)
        log.emit("REMOTE_STATE", {"value": state})
        if state == "TERMINAL":
            return True
        remaining = cutoff - time.time()
        if remaining <= 0:
            break
        time.sleep(min(config.poll_seconds, remaining))
    log.emit("REMOTE_RESULT_DEADLINE", {})
    return False


def package_remote(config: Config) -> None:
    root = shlex.quote(config.remote_root)
    remote = f"""
set -euo pipefail
ROOT={root}
export ROOT
cd "$ROOT"
python3 - <<'PY'
import json
import os
from pathlib import Path
root = Path(os.environ["ROOT"])
summary = {{"version": "ck-pdh3-closeout-summary-v2"}}
for name in (
    "network-receipt.json",
    "evidence/result.json",
    "evidence/MEASURED_CAMPAIGN_GREEN",
    "evidence/failure.json",
    "evidence/setup.json",
    "evidence/teardown.json",
):
    path = root / name
    summary[name] = json.loads(path.read_text()) if path.is_file() else None
raw = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
temporary = root / ".final-state.json.part"
with temporary.open("wb") as handle:
    handle.write(raw)
    handle.flush()
    os.fsync(handle.fileno())
os.replace(temporary, root / "final-state.json")
directory = os.open(root, os.O_RDONLY)
try:
    os.fsync(directory)
finally:
    os.close(directory)
PY
python3 - <<'PY'
import os
from pathlib import Path
import tarfile
root = Path(os.environ["ROOT"])
temporary = root / ".final-evidence.tgz.part"
allowed = [
    "evidence", "network-receipt.json", "production.log", "production.pid",
    "final-state.json", "network-trace", "network-receipt.progress.json",
    "trace-canary", "controller-canary-trace",
    "controller-canary-evidence",
]
allowed.extend(path.name for path in sorted(root.glob("network-trace.*")))
with tarfile.open(temporary, "w:gz") as out:
    for name in allowed:
        path = root / name
        if path.exists() and not path.is_symlink():
            out.add(path, arcname=name, recursive=True)
os.replace(temporary, root / "final-evidence.tgz")
PY
sha256sum final-evidence.tgz > .final-evidence.tgz.sha256.part
mv .final-evidence.tgz.sha256.part final-evidence.tgz.sha256
"""
    timeout = bounded_timeout(
        config.closeout_deadline_epoch,
        config.transfer_timeout_seconds,
        reserve_seconds=config.teardown_reserve_seconds,
    )
    result = run_command(
        ["ssh", "-F", str(config.ssh_config), config.ssh_alias, remote],
        timeout=timeout,
    )
    if result.returncode != 0:
        raise TransportFailure("REMOTE_PACKAGE_FAILED:" + digest(result.stderr.encode()))


def retrieve_file(config: Config, name: str) -> Path:
    config.retrieval.mkdir(parents=True, exist_ok=True)
    destination = config.retrieval / name
    partial = destination.with_name(destination.name + ".part")
    partial.unlink(missing_ok=True)
    timeout = bounded_timeout(
        config.closeout_deadline_epoch,
        config.transfer_timeout_seconds,
        reserve_seconds=config.teardown_reserve_seconds,
    )
    result = run_command(
        [
            "scp",
            "-F",
            str(config.ssh_config),
            f"{config.ssh_alias}:{config.remote_root}/{name}",
            str(partial),
        ],
        timeout=timeout,
    )
    if result.returncode != 0 or not partial.is_file():
        raise TransportFailure("RETRIEVAL_FAILED:" + name)
    with partial.open("rb+") as handle:
        os.fsync(handle.fileno())
    os.replace(partial, destination)
    directory = os.open(destination.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return destination


def retrieve(config: Config, log: ChainLog) -> tuple[Path, Path]:
    archive = retrieve_file(config, "final-evidence.tgz")
    sidecar = retrieve_file(config, "final-evidence.tgz.sha256")
    final_state = retrieve_file(config, "final-state.json")
    fields = sidecar.read_text(encoding="utf-8").split()
    if not fields or not re.fullmatch(r"[0-9a-f]{64}", fields[0]):
        raise ArchiveFailure("RETRIEVAL_SIDECAR_INVALID")
    observed = sha256_file(archive)
    if observed != fields[0]:
        raise ArchiveFailure("RETRIEVAL_HASH_MISMATCH")
    log.emit(
        "RETRIEVAL_HASH_GREEN",
        {"archive_sha256": observed, "archive_bytes": archive.stat().st_size},
    )
    return archive, final_state


def safe_member_name(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "\x00" not in name


def archive_member(archive: tarfile.TarFile, name: str) -> tarfile.TarInfo:
    """Return a member through one cached exact-name index.

    A production evidence archive contains more than ten thousand receipts;
    repeated ``TarFile.getmember`` reverse scans turn semantic validation into
    quadratic work and can consume the closeout reserve.
    """
    index = getattr(archive, "_pdh3_member_index", None)
    if index is None:
        members = archive.getmembers()
        index = {member.name: member for member in members}
        if len(index) != len(members):
            raise ArchiveFailure("ARCHIVE_MEMBER_NAME_DUPLICATE")
        setattr(archive, "_pdh3_member_index", index)
    try:
        return index[name]
    except KeyError as exc:
        raise KeyError(name) from exc


def read_member_json(archive: tarfile.TarFile, name: str) -> dict[str, Any]:
    member = archive_member(archive, name)
    if not member.isfile():
        raise ArchiveFailure("MEMBER_NOT_REGULAR:" + name)
    handle = archive.extractfile(member)
    if handle is None:
        raise ArchiveFailure("MEMBER_UNREADABLE:" + name)
    raw = handle.read()
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ArchiveFailure("MEMBER_JSON_INVALID:" + name) from exc
    if not isinstance(value, dict):
        raise ArchiveFailure("MEMBER_OBJECT_REQUIRED:" + name)
    if canonical(value) != raw:
        raise ArchiveFailure("MEMBER_JSON_NON_CANONICAL:" + name)
    return value


def verify_embedded_hash(value: dict[str, Any], field: str, label: str) -> None:
    expected = value.get(field)
    if not isinstance(expected, str) or expected != digest({key: item for key, item in value.items() if key != field}):
        raise ArchiveFailure(label + "_HASH_INVALID")


def member_sha256(archive: tarfile.TarFile, name: str) -> str:
    member = archive_member(archive, name)
    if not member.isfile():
        raise ArchiveFailure("MEMBER_NOT_REGULAR:" + name)
    handle = archive.extractfile(member)
    if handle is None:
        raise ArchiveFailure("MEMBER_UNREADABLE:" + name)
    hasher = hashlib.sha256()
    for block in iter(lambda: handle.read(1 << 20), b""):
        hasher.update(block)
    return hasher.hexdigest()


def validate_trace_evidence(
    archive: tarfile.TarFile,
    names: set[str],
    network: dict[str, Any],
    config: Config,
) -> None:
    if network.get("version") != "ck-pdh3-process-tree-egress-observer-v2":
        raise ArchiveFailure("TRACE_VERSION_INVALID")
    if network.get("authoritative") is not True:
        raise ArchiveFailure("TRACE_NOT_AUTHORITATIVE")
    bindings = {
        "packet_sha256": config.packet_sha256,
        "tool_sha256": config.trace_tool_sha256,
        "strace_sha256": CONTRACT.STRACE_BINARY_SHA256,
        "command_sha256": config.trace_command_sha256,
    }
    for field, expected in bindings.items():
        if network.get(field) != expected:
            raise ArchiveFailure("TRACE_" + field.upper() + "_MISMATCH")
    if network.get("trace_stream_mode") != "SINGLE_FILE_PID_PREFIXED_STRACE_F":
        raise ArchiveFailure("TRACE_STREAM_MODE_INVALID")
    status = network.get("status")
    green = network.get("green")
    if status == "GREEN":
        if (
            green is not True
            or network.get("claim")
            != "PROCESS_TREE_OBSERVED_ZERO_EXTERNAL_EGRESS"
            or network.get("child_exit") != 0
            or network.get("external_or_unparseable_count") != 0
            or network.get("violations") != []
            or network.get("observer_error") is not None
        ):
            raise ArchiveFailure("TRACE_GREEN_SEMANTICS_INVALID")
    elif status == "BLOCKED":
        if (
            green is not False
            or network.get("claim") != "PROCESS_TREE_OBSERVATION_BLOCKED"
        ):
            raise ArchiveFailure("TRACE_BLOCKED_SEMANTICS_INVALID")
    else:
        raise ArchiveFailure("TRACE_STATUS_INVALID")
    rows = network.get("trace_files")
    if not isinstance(rows, list) or not rows:
        raise ArchiveFailure("TRACE_FILE_RECORDS_INVALID")
    expected: set[str] = set()
    total_bytes = 0
    for row in rows:
        if not isinstance(row, dict):
            raise ArchiveFailure("TRACE_FILE_RECORD_INVALID")
        name = row.get("name")
        size = row.get("bytes")
        expected_hash = row.get("sha256")
        if (
            not isinstance(name, str)
            or PurePosixPath(name).name != name
            or not (name == "network-trace" or name.startswith("network-trace."))
            or not isinstance(size, int)
            or size < 0
            or not isinstance(expected_hash, str)
            or not re.fullmatch(r"[0-9a-f]{64}", expected_hash)
            or row.get("hash_complete") is not True
        ):
            raise ArchiveFailure("TRACE_FILE_RECORD_INVALID")
        if name in expected:
            raise ArchiveFailure("TRACE_FILE_RECORD_DUPLICATE")
        expected.add(name)
        member = archive_member(archive, name)
        if member.size != size or member_sha256(archive, name) != expected_hash:
            raise ArchiveFailure("TRACE_FILE_EVIDENCE_MISMATCH:" + name)
        total_bytes += size
    actual = {
        name
        for name in names
        if name == "network-trace" or name.startswith("network-trace.")
    }
    if actual != expected:
        raise ArchiveFailure("TRACE_FILE_SET_MISMATCH")
    maximum = network.get("maximum_trace_bytes")
    if (
        network.get("trace_file_count") != len(rows)
        or network.get("trace_bytes") != total_bytes
        or maximum != 2 * 1024**3
        or total_bytes > maximum
    ):
        raise ArchiveFailure("TRACE_SUMMARY_INVALID")


def validate_manifest(
    archive: tarfile.TarFile,
    names: set[str],
) -> tuple[dict[str, Any], set[str]]:
    manifest = read_member_json(archive, "evidence/manifest.json")
    verify_embedded_hash(manifest, "manifest_sha256", "MANIFEST")
    files = manifest.get("files")
    if not isinstance(files, dict) or not all(
        isinstance(name, str) and isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
        for name, value in files.items()
    ):
        raise ArchiveFailure("MANIFEST_FILES_INVALID")
    if manifest.get("file_count") != len(files) or manifest.get("file_set_sha256") != digest(files):
        raise ArchiveFailure("MANIFEST_SUMMARY_INVALID")
    if {"result.json", "MEASURED_CAMPAIGN_GREEN"} & set(files):
        raise ArchiveFailure("MANIFEST_TERMINAL_RECORD_ORDER_INVALID")
    actual_evidence = {
        name
        for name in names
        if name.startswith("evidence/")
        and name != "evidence/manifest.json"
        and archive_member(archive, name).isfile()
    }
    expected_evidence = {"evidence/" + name for name in files}
    missing = expected_evidence - actual_evidence
    unexpected = actual_evidence - expected_evidence
    if missing:
        raise ArchiveFailure("MANIFEST_FILE_SET_MISSING")
    if not unexpected <= TERMINAL_EVIDENCE_RECORDS:
        raise ArchiveFailure("MANIFEST_FILE_SET_MISMATCH")
    for relative, expected in files.items():
        member = archive_member(archive, "evidence/" + relative)
        handle = archive.extractfile(member)
        if handle is None:
            raise ArchiveFailure("MANIFEST_MEMBER_UNREADABLE:" + relative)
        if member_sha256(archive, "evidence/" + relative) != expected:
            raise ArchiveFailure("MANIFEST_MEMBER_HASH_INVALID:" + relative)
    return manifest, unexpected


def require_hex_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ArchiveFailure(label + "_SHA256_INVALID")
    return value


def require_int(
    value: Any,
    label: str,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ArchiveFailure(label + "_INTEGER_INVALID")
    if minimum is not None and value < minimum:
        raise ArchiveFailure(label + "_INTEGER_INVALID")
    if maximum is not None and value > maximum:
        raise ArchiveFailure(label + "_INTEGER_INVALID")
    return value


def require_number(
    value: Any,
    label: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ArchiveFailure(label + "_NUMBER_INVALID")
    observed = float(value)
    if minimum is not None and observed < minimum:
        raise ArchiveFailure(label + "_NUMBER_INVALID")
    if maximum is not None and observed > maximum:
        raise ArchiveFailure(label + "_NUMBER_INVALID")
    return observed


def expected_dataset_counts() -> list[int]:
    return [
        CONTRACT.TASKS,
        CONTRACT.TASKS * CONTRACT.EVENTS_PER_TASK,
        CONTRACT.TASKS * CONTRACT.RECEIPTS_PER_TASK,
        CONTRACT.VECTORS,
    ]


def percentile(values: list[int], numerator: int) -> int:
    ordered = sorted(values)
    index = max(0, (len(ordered) * numerator + 99) // 100 - 1)
    return ordered[index]


def validate_verifier_summary(
    value: Any,
    *,
    lane: str,
    batches: int,
    receipts: int,
    manifest_set_sha256: str,
) -> None:
    if not isinstance(value, dict):
        raise ArchiveFailure(lane.upper() + "_VERIFIER_SUMMARY_INVALID")
    expected = {
        "lane": lane,
        "batch_count": batches,
        "receipt_count": receipts,
        "unique_receipt_hashes": receipts,
        "manifest_set_sha256": manifest_set_sha256,
        "green": True,
    }
    if value != expected:
        raise ArchiveFailure(lane.upper() + "_VERIFIER_SUMMARY_INVALID")


def validate_gate7_vector_set(
    archive: tarfile.TarFile,
    manifest: dict[str, Any],
    *,
    raw_root: str,
    label: str,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    salt_name = raw_root + "/verifier/public-salt.bin"
    vectors_name = raw_root + "/verifier/public-vectors.json"
    if salt_name not in manifest["files"] or vectors_name not in manifest["files"]:
        raise ArchiveFailure(label + "_VERIFIER_VECTOR_INPUTS_MISSING")
    salt_member = archive_member(archive, "evidence/" + salt_name)
    salt_handle = archive.extractfile(salt_member)
    if salt_handle is None:
        raise ArchiveFailure(label + "_VERIFIER_SALT_UNREADABLE")
    salt = salt_handle.read()
    if len(salt) != 32:
        raise ArchiveFailure(label + "_VERIFIER_SALT_INVALID")
    vectors = read_member_json(archive, "evidence/" + vectors_name)
    required = {
        "version",
        "candidate_commit",
        "salt_sha256",
        "failure_vectors",
        "valid_controls",
        "set_hash",
    }
    body = {key: value for key, value in vectors.items() if key != "set_hash"}
    if (
        set(vectors) != required
        or vectors.get("version") != "hardening-gate7-vector-set-v1"
        or vectors.get("candidate_commit") != CONTRACT.PRODUCT_CANDIDATE
        or vectors.get("salt_sha256") != digest(salt)
        or vectors.get("set_hash") != digest(body)
    ):
        raise ArchiveFailure(label + "_VERIFIER_VECTOR_SET_INVALID")
    failures = vectors.get("failure_vectors")
    controls = vectors.get("valid_controls")
    if not isinstance(failures, list) or len(failures) != 21:
        raise ArchiveFailure(label + "_VERIFIER_FAILURE_VECTOR_SET_INVALID")
    if not isinstance(controls, list) or len(controls) != 7:
        raise ArchiveFailure(label + "_VERIFIER_CONTROL_VECTOR_SET_INVALID")
    failure_classes = {
        "tampered-receipt",
        "replayed-warrant",
        "malformed-record",
        "unsupported-value",
        "quarantined-candidate",
        "incomplete-evidence",
        "interrupted-consumption",
    }
    if (
        {row.get("class") for row in failures if isinstance(row, dict)}
        != failure_classes
        or {
            str(row.get("class", "")).removeprefix("valid-control-")
            for row in controls
            if isinstance(row, dict)
        }
        != failure_classes
    ):
        raise ArchiveFailure(label + "_VERIFIER_VECTOR_CLASS_COVERAGE_INVALID")
    ordered: list[dict[str, Any]] = []
    by_hash: dict[str, dict[str, Any]] = {}
    for vector in [*failures, *controls]:
        if not isinstance(vector, dict):
            raise ArchiveFailure(label + "_VERIFIER_VECTOR_INVALID")
        vector_hash = vector.get("vector_hash")
        vector_body = {
            key: value for key, value in vector.items() if key != "vector_hash"
        }
        if (
            not isinstance(vector_hash, str)
            or vector_hash != digest(vector_body)
            or vector_hash in by_hash
            or vector.get("expected_verdict") not in {"PROMOTE", "REFUSE", "INVALID"}
            or not isinstance(vector.get("expected_reason"), str)
            or not vector["expected_reason"]
        ):
            raise ArchiveFailure(label + "_VERIFIER_VECTOR_INVALID")
        by_hash[vector_hash] = vector
        ordered.append(vector)
    return by_hash, ordered


def validate_verifier_batch(
    archive: tarfile.TarFile,
    manifest: dict[str, Any],
    raw_manifest: dict[str, Any],
    checkpoint_verifier: Any,
    *,
    lane: str,
    epoch: int,
    campaign_id: str,
    label: str,
) -> dict[str, Any]:
    raw_root = f"raw/{lane}/epoch-{epoch:04d}"
    campaign_relative_root = "verifier/verifier-campaign"
    campaign_root = raw_root + "/" + campaign_relative_root
    inner_manifest_name = campaign_root + "/manifest.json"
    aggregate_name = campaign_root + "/aggregate.json"
    if (
        inner_manifest_name not in manifest["files"]
        or aggregate_name not in manifest["files"]
    ):
        raise ArchiveFailure(label + "_VERIFIER_CORE_EVIDENCE_MISSING")
    by_vector_hash, ordered_vectors = validate_gate7_vector_set(
        archive,
        manifest,
        raw_root=raw_root,
        label=label,
    )
    expected_campaign = f"{campaign_id}-{lane}-v{epoch:04d}-verifier"
    inner_manifest = read_member_json(
        archive, "evidence/" + inner_manifest_name
    )
    verify_embedded_hash(
        inner_manifest, "manifest_sha256", label + "_VERIFIER_MANIFEST"
    )
    inner_files = inner_manifest.get("files")
    if not isinstance(inner_files, dict) or not all(
        isinstance(name, str)
        and safe_member_name(name)
        and isinstance(value, str)
        and re.fullmatch(r"[0-9a-f]{64}", value)
        for name, value in inner_files.items()
    ):
        raise ArchiveFailure(label + "_VERIFIER_MANIFEST_FILES_INVALID")
    actual_inner_files = {
        relative.removeprefix(campaign_relative_root + "/")
        for relative in raw_manifest["files"]
        if relative.startswith(campaign_relative_root + "/")
        and relative != campaign_relative_root + "/manifest.json"
    }
    if set(inner_files) != actual_inner_files:
        raise ArchiveFailure(label + "_VERIFIER_MANIFEST_FILE_SET_INVALID")
    for relative, expected_hash in inner_files.items():
        if (
            raw_manifest["files"].get(
                campaign_relative_root + "/" + relative
            )
            != expected_hash
        ):
            raise ArchiveFailure(label + "_VERIFIER_MANIFEST_HASH_BINDING_INVALID")
    aggregate = read_member_json(archive, "evidence/" + aggregate_name)
    verify_embedded_hash(
        aggregate, "aggregate_sha256", label + "_VERIFIER_AGGREGATE"
    )
    receipt_names = sorted(
        name
        for name in inner_files
        if re.fullmatch(r"receipts/[A-Za-z0-9._-]+[.]json", name)
    )
    if len(receipt_names) != CONTRACT.VERIFIER_BATCH_SIZE:
        raise ArchiveFailure(label + "_VERIFIER_RECEIPT_COUNT_INVALID")
    expected_executions: list[tuple[str, dict[str, Any]]] = [
        (f"trial-{index:03d}", vector)
        for index, vector in enumerate(ordered_vectors, start=1)
    ]
    controls = [
        vector
        for vector in ordered_vectors
        if str(vector.get("class", "")).startswith("valid-control-")
    ]
    failures = [
        vector
        for vector in ordered_vectors
        if not str(vector.get("class", "")).startswith("valid-control-")
    ]
    try:
        selected = [
            controls[0],
            next(row for row in failures if row.get("expected_verdict") == "REFUSE"),
            next(row for row in failures if row.get("expected_verdict") == "INVALID"),
        ]
    except (IndexError, StopIteration) as exc:
        raise ArchiveFailure(label + "_VERIFIER_DETERMINISM_SET_INVALID") from exc
    for vector in selected:
        verdict_label = str(vector["expected_verdict"]).lower()
        expected_executions.extend(
            (f"det-{verdict_label}-{repetition:02d}", vector)
            for repetition in range(1, 6)
        )
    expected_by_execution = dict(expected_executions)
    if len(expected_by_execution) != CONTRACT.VERIFIER_BATCH_SIZE:
        raise ArchiveFailure(label + "_VERIFIER_EXECUTION_PLAN_INVALID")
    receipts_by_execution: dict[str, dict[str, Any]] = {}
    receipt_hashes: set[str] = set()
    receipt_file_hashes: set[str] = set()
    receipt_sizes: list[int] = []
    receipt_required_keys = {
        "version",
        "candidate_commit",
        "execution_id",
        "vector_hash",
        "vector_class",
        "variant",
        "expected_verdict",
        "expected_reason",
        "observed_verdict",
        "observed_reason",
        "mutation_performed",
        "details",
        "passed",
        "receipt_hash",
    }
    for relative in receipt_names:
        full_name = campaign_root + "/" + relative
        receipt = read_member_json(archive, "evidence/" + full_name)
        verify_embedded_hash(receipt, "receipt_hash", label + "_VERIFIER_RECEIPT")
        execution_id = receipt.get("execution_id")
        vector_hash = receipt.get("vector_hash")
        vector = by_vector_hash.get(vector_hash)
        if (
            set(receipt) != receipt_required_keys
            or not isinstance(execution_id, str)
            or PurePosixPath(relative).stem != execution_id
            or execution_id not in expected_by_execution
            or vector is None
            or vector != expected_by_execution[execution_id]
            or receipt.get("version") != "hardening-gate7-trial-receipt-v1"
            or receipt.get("candidate_commit") != CONTRACT.PRODUCT_CANDIDATE
            or receipt.get("vector_class") != vector.get("class")
            or receipt.get("variant") != vector.get("variant")
            or receipt.get("expected_verdict") != vector.get("expected_verdict")
            or receipt.get("expected_reason") != vector.get("expected_reason")
            or receipt.get("observed_verdict") != vector.get("expected_verdict")
            or receipt.get("observed_reason") != vector.get("expected_reason")
            or receipt.get("mutation_performed") is not False
            or not isinstance(receipt.get("details"), dict)
            or receipt.get("passed") is not True
            or execution_id in receipts_by_execution
            or receipt["receipt_hash"] in receipt_hashes
            or inner_files[relative] in receipt_file_hashes
        ):
            raise ArchiveFailure(label + "_VERIFIER_RECEIPT_SEMANTICS_INVALID")
        receipts_by_execution[execution_id] = receipt
        receipt_hashes.add(receipt["receipt_hash"])
        receipt_file_hashes.add(inner_files[relative])
        receipt_sizes.append(
            archive_member(archive, "evidence/" + full_name).size
        )
    if set(receipts_by_execution) != set(expected_by_execution):
        raise ArchiveFailure(label + "_VERIFIER_EXECUTION_SET_INVALID")
    ordered_receipts = [
        receipts_by_execution[execution_id]
        for execution_id, _ in expected_executions
    ]
    expected_failures = [
        row for row in ordered_receipts if row["expected_verdict"] != "PROMOTE"
    ]
    refusals = [
        row for row in ordered_receipts if row["observed_verdict"] != "PROMOTE"
    ]
    groups: dict[str, set[tuple[str, str]]] = {}
    for row in ordered_receipts:
        if row["execution_id"].startswith("det-"):
            groups.setdefault(row["vector_class"], set()).add(
                (row["observed_verdict"], row["observed_reason"])
            )
    expected_aggregate = {
        "version": "hardening-gate7-aggregate-v1",
        "campaign_id": expected_campaign,
        "candidate_commit": CONTRACT.PRODUCT_CANDIDATE,
        "vector_set_hash": read_member_json(
            archive,
            "evidence/" + raw_root + "/verifier/public-vectors.json",
        )["set_hash"],
        "measured_executions": len(ordered_receipts),
        "failure_trials": 21,
        "valid_controls": 7,
        "determinism_executions": 15,
        "false_promotions": sum(
            row["observed_verdict"] == "PROMOTE" for row in expected_failures
        ),
        "mutation_after_refusal": sum(
            bool(row["mutation_performed"]) for row in refusals
        ),
        "correct_stable_reason_count": sum(
            row["observed_verdict"] == row["expected_verdict"]
            and row["observed_reason"] == row["expected_reason"]
            for row in ordered_receipts
        ),
        "canonical_receipt_count": len(ordered_receipts),
        "valid_control_continuation_count": sum(
            row["vector_class"].startswith("valid-control-")
            and row["observed_verdict"] == "PROMOTE"
            for row in ordered_receipts
        ),
        "hidden_session_state_dependencies": 0,
        "trial_teardown_count": len(ordered_receipts),
        "residue_count": 0,
        "output_schema_compliance_count": len(ordered_receipts),
        "determinism_group_count": len(groups),
        "determinism_stable_group_count": sum(
            len(values) == 1 for values in groups.values()
        ),
        "receipt_bytes_total": sum(receipt_sizes),
        "receipt_bytes_p50": percentile(receipt_sizes, 50),
        "receipt_bytes_p95": percentile(receipt_sizes, 95),
        "receipt_bytes_p99": percentile(receipt_sizes, 99),
        "receipt_hashes": [row["receipt_hash"] for row in ordered_receipts],
        "limitations": [
            "SYNTHETIC_HELD_OUT_FAILURES",
            "NOT_LIVE_MEMORY_WORKLOAD",
            "NOT_PRODUCTION_SCALE",
            "NOT_PUBLIC_USER_EVIDENCE",
        ],
        "green": True,
    }
    expected_aggregate_record = {
        **expected_aggregate,
        "aggregate_sha256": digest(expected_aggregate),
    }
    if aggregate != expected_aggregate_record:
        mismatched = sorted(
            key
            for key in set(aggregate) | set(expected_aggregate_record)
            if aggregate.get(key) != expected_aggregate_record.get(key)
        )
        raise ArchiveFailure(
            label
            + "_VERIFIER_AGGREGATE_SEMANTICS_INVALID:"
            + ",".join(mismatched)
        )
    if (
        inner_manifest.get("version")
        != "hardening-gate7-evidence-manifest-v1"
        or inner_manifest.get("campaign_id") != expected_campaign
        or inner_manifest.get("candidate_commit") != CONTRACT.PRODUCT_CANDIDATE
        or inner_manifest.get("vector_set_hash") != aggregate["vector_set_hash"]
        or inner_manifest.get("aggregate_sha256") != aggregate["aggregate_sha256"]
        or inner_files.get("aggregate.json") != manifest["files"][aggregate_name]
    ):
        raise ArchiveFailure(label + "_VERIFIER_MANIFEST_SEMANTICS_INVALID")
    expected_checkpoint = {
        "aggregate_sha256": aggregate["aggregate_sha256"],
        "aggregate_file_sha256": manifest["files"][aggregate_name],
        "measured_executions": CONTRACT.VERIFIER_BATCH_SIZE,
        "false_promotions": 0,
        "mutation_after_refusal": 0,
        "correct_stable_reason_count": CONTRACT.VERIFIER_BATCH_SIZE,
        "valid_control_continuation_count": 12,
        "trial_teardown_count": CONTRACT.VERIFIER_BATCH_SIZE,
        "residue_count": 0,
    }
    if checkpoint_verifier != expected_checkpoint:
        raise ArchiveFailure(label + "_VERIFIER_CHECKPOINT_BINDING_INVALID")
    return {
        "manifest_sha256": inner_manifest["manifest_sha256"],
        "receipt_hashes": receipt_hashes,
        "receipt_count": len(receipt_hashes),
    }


def validate_raw_epoch_manifest(
    archive: tarfile.TarFile,
    manifest: dict[str, Any],
    checkpoint_raw: Any,
    *,
    lane: str,
    epoch: int,
    label: str,
) -> dict[str, Any]:
    raw_root = f"raw/{lane}/epoch-{epoch:04d}"
    raw_manifest_name = raw_root + "/raw-epoch-manifest.json"
    if raw_manifest_name not in manifest["files"]:
        raise ArchiveFailure(label + "_RAW_MANIFEST_MISSING")
    raw_manifest = read_member_json(
        archive, "evidence/" + raw_manifest_name
    )
    verify_embedded_hash(
        raw_manifest, "manifest_sha256", label + "_RAW_MANIFEST"
    )
    files = raw_manifest.get("files")
    if not isinstance(files, dict) or not all(
        isinstance(name, str)
        and safe_member_name(name)
        and name != "raw-epoch-manifest.json"
        and isinstance(value, str)
        and re.fullmatch(r"[0-9a-f]{64}", value)
        for name, value in files.items()
    ):
        raise ArchiveFailure(label + "_RAW_MANIFEST_FILES_INVALID")
    actual = {
        name.removeprefix(raw_root + "/")
        for name in manifest["files"]
        if name.startswith(raw_root + "/") and name != raw_manifest_name
    }
    if set(files) != actual:
        raise ArchiveFailure(label + "_RAW_MANIFEST_FILE_SET_INVALID")
    for relative, expected_hash in files.items():
        if manifest["files"].get(raw_root + "/" + relative) != expected_hash:
            raise ArchiveFailure(label + "_RAW_MANIFEST_HASH_BINDING_INVALID")
    if (
        raw_manifest.get("version") != "ck-pdh3-raw-epoch-manifest-v1"
        or raw_manifest.get("lane") != lane
        or raw_manifest.get("epoch") != epoch
        or raw_manifest.get("file_count") != len(files)
        or raw_manifest.get("file_set_sha256") != digest(files)
        or not isinstance(checkpoint_raw, dict)
        or checkpoint_raw
        != {
            "path": raw_root,
            "manifest_sha256": raw_manifest["manifest_sha256"],
            "file_count": len(files),
        }
    ):
        raise ArchiveFailure(label + "_RAW_MANIFEST_SEMANTICS_INVALID")
    return raw_manifest


def validate_cluster_readiness(value: Any, label: str) -> None:
    if not isinstance(value, dict) or set(value) != {"nodes", "green"}:
        raise ArchiveFailure(label + "_CLUSTER_READINESS_INVALID")
    nodes = value.get("nodes")
    if (
        value.get("green") is not True
        or not isinstance(nodes, list)
        or len(nodes) != CONTRACT.REQUIRED_LIVE_NODE_PROCESSES
    ):
        raise ArchiveFailure(label + "_CLUSTER_READINESS_INVALID")
    pids: set[int] = set()
    for index, row in enumerate(nodes, start=1):
        if (
            not isinstance(row, dict)
            or set(row) != {"node", "pid", "alive", "sql_ready"}
            or row.get("node") != index
            or row.get("alive") is not True
            or row.get("sql_ready") is not True
        ):
            raise ArchiveFailure(label + "_CLUSTER_READINESS_INVALID")
        pid = require_int(row.get("pid"), label + "_CLUSTER_PID", minimum=1)
        if pid in pids:
            raise ArchiveFailure(label + "_CLUSTER_PID_DUPLICATE")
        pids.add(pid)


def histogram_operation_count(
    archive: tarfile.TarFile,
    name: str,
    label: str,
) -> int:
    member = archive_member(archive, name)
    handle = archive.extractfile(member)
    if handle is None:
        raise ArchiveFailure(label + "_HISTOGRAM_UNREADABLE")
    total = 0
    rows = 0
    for raw in handle:
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ArchiveFailure(label + "_HISTOGRAM_JSON_INVALID") from exc
        counts = value.get("Hist", {}).get("Counts") if isinstance(value, dict) else None
        if (
            not isinstance(value, dict)
            or not isinstance(value.get("Name"), str)
            or not isinstance(counts, list)
        ):
            raise ArchiveFailure(label + "_HISTOGRAM_SCHEMA_INVALID")
        for count in counts:
            total += require_int(count, label + "_HISTOGRAM_COUNT", minimum=0)
        rows += 1
    if rows == 0:
        raise ArchiveFailure(label + "_HISTOGRAM_EMPTY")
    return total


def validate_stage(
    archive: tarfile.TarFile,
    raw_manifest: dict[str, Any],
    value: Any,
    *,
    concurrency: int,
    raw_root: str,
    label: str,
) -> dict[str, Any]:
    required_stage_keys = {
        "concurrency",
        "workloads",
        "total_operations",
        "maximum_latency_ms",
        "acknowledged_write_delta",
        "contended_update_delta",
        "replay_rows",
        "checks",
        "green",
    }
    if not isinstance(value, dict) or set(value) != required_stage_keys:
        raise ArchiveFailure(label + "_STAGE_SCHEMA_INVALID")
    workloads = value.get("workloads")
    kinds = ("read_mix", "ack_write", "contended_update", "replay")
    if value.get("concurrency") != concurrency or not isinstance(workloads, dict) or set(workloads) != set(kinds):
        raise ArchiveFailure(label + "_STAGE_SCHEMA_INVALID")
    operations: dict[str, int] = {}
    p99_values: list[float] = []
    pmax_values: list[float] = []
    histogram_checks: list[bool] = []
    bounded_checks: list[bool] = []
    zero_errors = True
    for kind in kinds:
        workload = workloads[kind]
        if not isinstance(workload, dict) or set(workload) != {
            "kind",
            "execution_boundary",
            "summary",
            "histogram_count",
            "histogram_accounts_for_operations",
            "stdout_sha256",
            "stderr_sha256",
            "histograms_sha256",
        }:
            raise ArchiveFailure(label + "_" + kind.upper() + "_SCHEMA_INVALID")
        if workload.get("kind") != kind:
            raise ArchiveFailure(label + "_" + kind.upper() + "_KIND_INVALID")
        prefix = f"querybench-c{concurrency}-{kind}"
        bindings = {
            "stdout_sha256": prefix + ".stdout.log",
            "stderr_sha256": prefix + ".stderr.log",
            "histograms_sha256": prefix + ".histograms.json",
        }
        for field, relative in bindings.items():
            if workload.get(field) != raw_manifest["files"].get(relative):
                raise ArchiveFailure(label + "_" + kind.upper() + "_RAW_BINDING_INVALID")
        summary = workload.get("summary")
        if not isinstance(summary, dict) or set(summary) != {
            "elapsed_seconds",
            "errors",
            "operations",
            "operations_per_second",
            "latency_ms",
        }:
            raise ArchiveFailure(label + "_" + kind.upper() + "_SUMMARY_INVALID")
        elapsed = require_number(
            summary.get("elapsed_seconds"),
            label + "_" + kind.upper() + "_ELAPSED",
            minimum=0,
        )
        del elapsed
        errors = require_int(
            summary.get("errors"), label + "_" + kind.upper() + "_ERRORS", minimum=0
        )
        operation_count = require_int(
            summary.get("operations"),
            label + "_" + kind.upper() + "_OPERATIONS",
            minimum=1,
        )
        require_number(
            summary.get("operations_per_second"),
            label + "_" + kind.upper() + "_OPS_PER_SECOND",
            minimum=0,
        )
        latency = summary.get("latency_ms")
        if not isinstance(latency, dict) or set(latency) != {"avg", "p50", "p95", "p99", "max"}:
            raise ArchiveFailure(label + "_" + kind.upper() + "_LATENCY_INVALID")
        latency_values = {
            key: require_number(
                latency.get(key),
                label + "_" + kind.upper() + "_" + key.upper(),
                minimum=0,
            )
            for key in latency
        }
        if not (
            latency_values["p50"]
            <= latency_values["p95"]
            <= latency_values["p99"]
            <= latency_values["max"]
        ):
            raise ArchiveFailure(label + "_" + kind.upper() + "_LATENCY_ORDER_INVALID")
        boundary = workload.get("execution_boundary")
        if kind == "read_mix":
            expected_boundary = {
                "mode": "FIXED_DURATION",
                "duration_seconds": CONTRACT.QUERY_DURATION_SECONDS,
                "target_operations": None,
            }
            bounded = True
        else:
            minimum = (
                max(2_000, concurrency * 10)
                if kind == "ack_write"
                else max(1_000, concurrency * 5)
            )
            expected_boundary = {
                "mode": "BOUNDED_FIXED_OPERATIONS",
                "duration_seconds": None,
                "minimum_operations": minimum,
                "maximum_operations": minimum + concurrency - 1,
                "querybench_soft_cap": minimum,
            }
            bounded = minimum <= operation_count <= minimum + concurrency - 1
        if boundary != expected_boundary:
            raise ArchiveFailure(label + "_" + kind.upper() + "_BOUNDARY_INVALID")
        raw_histogram_count = histogram_operation_count(
            archive,
            "evidence/" + raw_root + "/" + bindings["histograms_sha256"],
            label + "_" + kind.upper(),
        )
        histogram_count = require_int(
            workload.get("histogram_count"),
            label + "_" + kind.upper() + "_HISTOGRAM",
            minimum=0,
        )
        histogram_green = (
            raw_histogram_count == histogram_count == operation_count
            and workload.get("histogram_accounts_for_operations") is True
        )
        operations[kind] = operation_count
        p99_values.append(latency_values["p99"])
        pmax_values.append(latency_values["max"])
        histogram_checks.append(histogram_green)
        bounded_checks.append(bounded)
        zero_errors = zero_errors and errors == 0
    total_operations = sum(operations.values())
    maximum_p99 = max(p99_values)
    maximum_pmax = max(pmax_values)
    expected_checks = {
        "zero_errors": zero_errors,
        "minimum_operations": total_operations >= 500,
        "histograms_account_for_operations": all(histogram_checks),
        "bounded_operation_targets_respected": all(bounded_checks),
        "acknowledged_writes_exact": value.get("acknowledged_write_delta")
        == operations["ack_write"],
        "contended_updates_exact": value.get("contended_update_delta")
        == operations["contended_update"],
        "replay_idempotent": value.get("replay_rows") == 1,
        "p99_within_limit": maximum_p99 <= CONTRACT.P99_LIMIT_MS,
        "pmax_within_limit": maximum_pmax <= CONTRACT.PMAX_LIMIT_MS,
    }
    if (
        value.get("total_operations") != total_operations
        or value.get("maximum_latency_ms")
        != {"p99": maximum_p99, "max": maximum_pmax}
        or value.get("acknowledged_write_delta") != operations["ack_write"]
        or value.get("contended_update_delta") != operations["contended_update"]
        or value.get("replay_rows") != 1
        or value.get("checks") != expected_checks
        or value.get("green") is not True
        or not all(expected_checks.values())
    ):
        raise ArchiveFailure(label + "_STAGE_SEMANTICS_INVALID")
    return {
        "total_operations": total_operations,
        "maximum_p99_ms": maximum_p99,
        "maximum_latency_ms": maximum_pmax,
        "acknowledged_write_delta": operations["ack_write"],
        "contended_update_delta": operations["contended_update"],
    }


def validate_checkpoint_resources(checkpoint: dict[str, Any], label: str) -> None:
    resources = checkpoint.get("resources_at_boundary")
    if not isinstance(resources, dict) or set(resources) != {
        "nodes",
        "database_bytes",
        "evidence_bytes",
        "disk_total_bytes",
        "disk_used_bytes",
        "disk_used_fraction",
    }:
        raise ArchiveFailure(label + "_RESOURCES_INVALID")
    nodes = resources.get("nodes")
    if not isinstance(nodes, list) or len(nodes) != CONTRACT.REQUIRED_LIVE_NODE_PROCESSES:
        raise ArchiveFailure(label + "_NODE_SET_INVALID")
    pids: set[int] = set()
    for index, row in enumerate(nodes, start=1):
        if (
            not isinstance(row, dict)
            or set(row) != {"node", "pid", "alive", "rss_kb", "descriptors"}
            or row.get("node") != index
            or row.get("alive") is not True
        ):
            raise ArchiveFailure(label + "_NODE_RESOURCE_INVALID")
        pid = require_int(row.get("pid"), label + "_NODE_PID", minimum=1)
        require_int(row.get("rss_kb"), label + "_NODE_RSS", minimum=0)
        require_int(
            row.get("descriptors"),
            label + "_NODE_DESCRIPTORS",
            minimum=0,
            maximum=CONTRACT.FILE_DESCRIPTORS_PER_NODE_LIMIT,
        )
        if pid in pids:
            raise ArchiveFailure(label + "_NODE_PID_DUPLICATE")
        pids.add(pid)
    if sum(row["rss_kb"] for row in nodes) > CONTRACT.RSS_KB_LIMIT:
        raise ArchiveFailure(label + "_RSS_LIMIT_BREACH")
    scalar_limits = {
        "database_bytes": CONTRACT.DATABASE_BYTES_LIMIT,
        "evidence_bytes": CONTRACT.EVIDENCE_BYTES_LIMIT,
    }
    for field, limit in scalar_limits.items():
        value = resources.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= limit:
            raise ArchiveFailure(label + "_" + field.upper() + "_INVALID")
    disk_fraction = resources.get("disk_used_fraction")
    disk_total = require_int(
        resources.get("disk_total_bytes"), label + "_DISK_TOTAL", minimum=1
    )
    disk_used = require_int(
        resources.get("disk_used_bytes"),
        label + "_DISK_USED",
        minimum=0,
        maximum=disk_total,
    )
    if (
        isinstance(disk_fraction, bool)
        or not isinstance(disk_fraction, (int, float))
        or not 0 <= disk_fraction <= CONTRACT.DISK_USED_FRACTION_LIMIT
        or abs(float(disk_fraction) - disk_used / disk_total) > 1e-12
    ):
        raise ArchiveFailure(label + "_DISK_FRACTION_INVALID")


def validate_fault(
    value: Any,
    *,
    expected_node: int,
    expected_counts: list[int],
    expected_controls: list[int],
    label: str,
) -> None:
    if not isinstance(value, dict):
        raise ArchiveFailure(label + "_FAULT_MISSING")
    if (
        value.get("green") is not True
        or value.get("node") != expected_node
        or value.get("signal") != "SIGKILL"
        or value.get("returncode") != -9
        or not isinstance(value.get("old_pid"), int)
        or not isinstance(value.get("new_pid"), int)
        or value["old_pid"] == value["new_pid"]
        or value.get("before") != expected_counts
        or value.get("during") != expected_counts
        or value.get("after") != expected_counts
        or value.get("controls_before") != expected_controls
        or value.get("controls_during") != expected_controls
        or value.get("controls_after") != expected_controls
    ):
        raise ArchiveFailure(label + "_FAULT_PROOF_INVALID")
    validate_cluster_readiness(value.get("cluster_readiness"), label + "_FAULT")


def validate_checkpoint_series(
    archive: tarfile.TarFile,
    manifest: dict[str, Any],
    result: dict[str, Any],
    *,
    lane: str,
    campaign_id: str,
) -> dict[str, Any]:
    if lane == "measured":
        count = CONTRACT.REQUIRED_CHECKPOINTS
        listed = result.get("checkpoints")
        concurrency = CONTRACT.expected_schedule()["concurrency"]
        fault_epochs = set(CONTRACT.expected_schedule()["fault_epochs"])
        verifier_batches = CONTRACT.VERIFIER_BATCHES
        name_for = lambda epoch: f"checkpoint-{epoch:04d}.json"
    else:
        count = CONTRACT.REMOTE_PREFLIGHT_EPOCHS
        listed = result.get("checkpoints")
        concurrency = [CONTRACT.REMOTE_PREFLIGHT_CONCURRENCY] * count
        fault_epochs = set(range(1, count + 1))
        verifier_batches = count
        name_for = lambda epoch: f"preflight-checkpoint-{epoch:04d}.json"
    if not isinstance(listed, list) or len(listed) != count:
        raise ArchiveFailure(lane.upper() + "_CHECKPOINT_LIST_INVALID")
    files = manifest["files"]
    expected_counts = expected_dataset_counts()
    cumulative_acknowledged = 0
    cumulative_counter = 0
    total_operations = 0
    maximum_p99 = 0.0
    maximum_latency = 0.0
    verifier_executions = 0
    fault_cycles = 0
    verifier_receipt_hashes: set[str] = set()
    verifier_manifests: list[str] = []
    first_boundary: int | None = None
    previous_boundary: int | None = None
    last_snapshot: int | None = None
    for epoch in range(1, count + 1):
        label = f"{lane.upper()}_CHECKPOINT_{epoch:04d}"
        relative = name_for(epoch)
        if relative not in files:
            raise ArchiveFailure(label + "_MISSING")
        checkpoint = read_member_json(archive, "evidence/" + relative)
        verify_embedded_hash(checkpoint, "checkpoint_sha256", label)
        expected_entry = {
            "epoch": epoch,
            "checkpoint_sha256": checkpoint["checkpoint_sha256"],
        }
        if listed[epoch - 1] != expected_entry:
            raise ArchiveFailure(label + "_RESULT_BINDING_INVALID")
        if (
            checkpoint.get("version") != "ck-pdh3-scale-checkpoint-v2"
            or checkpoint.get("lane") != lane
            or checkpoint.get("epoch") != epoch
            or checkpoint.get("concurrency") != concurrency[epoch - 1]
        ):
            raise ArchiveFailure(label + "_SEMANTICS_INVALID")
        raw_manifest = validate_raw_epoch_manifest(
            archive,
            manifest,
            checkpoint.get("raw_evidence"),
            lane=lane,
            epoch=epoch,
            label=label,
        )
        stage = validate_stage(
            archive,
            raw_manifest,
            checkpoint.get("stage"),
            concurrency=concurrency[epoch - 1],
            raw_root=f"raw/{lane}/epoch-{epoch:04d}",
            label=label,
        )
        cumulative_acknowledged += stage["acknowledged_write_delta"]
        cumulative_counter += stage["contended_update_delta"]
        expected_controls = [cumulative_acknowledged, cumulative_counter, 1]
        if (
            checkpoint.get("counts") != expected_counts
            or checkpoint.get("control_counts") != expected_controls
            or checkpoint.get("wrong_task_vector_links") != 0
        ):
            raise ArchiveFailure(label + "_DATASET_OR_CONTROL_COUNTS_INVALID")
        cleanup = checkpoint.get("cleanup_probe")
        if (
            not isinstance(cleanup, dict)
            or set(cleanup) != {"task_id_hash", "residue"}
            or re.fullmatch(r"[0-9a-f]{64}", str(cleanup.get("task_id_hash"))) is None
            or cleanup.get("residue") != 0
        ):
            raise ArchiveFailure(label + "_CLEANUP_PROBE_INVALID")
        dependency = checkpoint.get("dependency_matrix")
        expected_statuses = [
            "ADVISORY",
            "TIMEOUT",
            "THROTTLED",
            "MALFORMED",
            "STALE",
        ]
        if dependency != {"statuses": expected_statuses, "rows": len(expected_statuses)}:
            raise ArchiveFailure(label + "_DEPENDENCY_MATRIX_INVALID")
        validate_cluster_readiness(
            checkpoint.get("cluster_readiness_before_boundary"), label
        )
        verifier = checkpoint.get("verifier")
        if epoch <= verifier_batches:
            batch = validate_verifier_batch(
                archive,
                manifest,
                raw_manifest,
                verifier,
                lane=lane,
                epoch=epoch,
                campaign_id=campaign_id,
                label=label,
            )
            if verifier_receipt_hashes & batch["receipt_hashes"]:
                raise ArchiveFailure(label + "_VERIFIER_GLOBAL_RECEIPT_DUPLICATE")
            verifier_receipt_hashes.update(batch["receipt_hashes"])
            verifier_manifests.append(batch["manifest_sha256"])
            verifier_executions += batch["receipt_count"]
        elif verifier is not None:
            raise ArchiveFailure(label + "_VERIFIER_UNEXPECTED")
        if epoch in fault_epochs:
            fault_index = (epoch - 1 if lane == "preflight" else epoch // CONTRACT.FAULT_EVERY_CHECKPOINTS - 1)
            validate_fault(
                checkpoint.get("fault"),
                expected_node=(fault_index % 3) + 1,
                expected_counts=expected_counts,
                expected_controls=expected_controls,
                label=label,
            )
            fault_cycles += 1
        elif checkpoint.get("fault") is not None:
            raise ArchiveFailure(label + "_FAULT_UNEXPECTED")
        validate_checkpoint_resources(checkpoint, label)
        boundary = require_int(
            checkpoint.get("boundary_monotonic_ns"), label + "_BOUNDARY", minimum=1
        )
        snapshot = require_int(
            checkpoint.get("snapshot_monotonic_ns"), label + "_SNAPSHOT", minimum=boundary
        )
        drift = require_int(
            checkpoint.get("boundary_drift_ns"),
            label + "_BOUNDARY_DRIFT",
            minimum=0,
            maximum=2_000_000_000,
        )
        if drift != abs(snapshot - boundary):
            raise ArchiveFailure(label + "_BOUNDARY_DRIFT_INVALID")
        if previous_boundary is not None and boundary - previous_boundary != CONTRACT.CHECKPOINT_SECONDS * 1_000_000_000:
            raise ArchiveFailure(label + "_BOUNDARY_PROGRESSION_INVALID")
        first_boundary = boundary if first_boundary is None else first_boundary
        previous_boundary = boundary
        last_snapshot = snapshot
        total_operations += stage["total_operations"]
        maximum_p99 = max(maximum_p99, stage["maximum_p99_ms"])
        maximum_latency = max(maximum_latency, stage["maximum_latency_ms"])
    verifier_summary = {
        "lane": lane,
        "batch_count": verifier_batches,
        "receipt_count": verifier_executions,
        "unique_receipt_hashes": len(verifier_receipt_hashes),
        "manifest_set_sha256": digest(verifier_manifests),
        "green": True,
    }
    validate_verifier_summary(
        result.get("verifier_evidence"),
        lane=lane,
        batches=verifier_batches,
        receipts=verifier_executions,
        manifest_set_sha256=verifier_summary["manifest_set_sha256"],
    )
    return {
        "checkpoint_count": count,
        "verifier_executions": verifier_executions,
        "fault_cycles": fault_cycles,
        "total_operations": total_operations,
        "maximum_p99_ms": maximum_p99,
        "maximum_latency_ms": maximum_latency,
        "final_control_counts": [cumulative_acknowledged, cumulative_counter, 1],
        "first_boundary_monotonic_ns": first_boundary,
        "last_snapshot_monotonic_ns": last_snapshot,
        "verifier_summary": verifier_summary,
    }


def validate_setup(setup: dict[str, Any], campaign_id: str) -> None:
    expected_counts = expected_dataset_counts()
    if (
        setup.get("version") != "ck-pdh3-scale-setup-v2"
        or setup.get("campaign_id") != campaign_id
        or setup.get("green") is not True
        or setup.get("expected_counts") != expected_counts
        or setup.get("actual_counts") != expected_counts
        or setup.get("dataset_counts") != expected_counts
        or setup.get("wrong_task_vector_links") != 0
        or setup.get("deadline_met") is not True
        or setup.get("setup_deadline_seconds") != CONTRACT.SETUP_TIMEOUT_SECONDS
        or isinstance(setup.get("setup_elapsed_seconds"), bool)
        or not isinstance(setup.get("setup_elapsed_seconds"), (int, float))
        or not 0 <= setup["setup_elapsed_seconds"] <= CONTRACT.SETUP_TIMEOUT_SECONDS
    ):
        raise ArchiveFailure("PRODUCTION_SETUP_SEMANTICS_INVALID")
    mismatches = setup.get("mismatch_counts")
    reconciliations = setup.get("reconciliations")
    if (
        not isinstance(mismatches, dict)
        or not mismatches
        or any(value != 0 for value in mismatches.values())
        or not isinstance(reconciliations, dict)
        or set(reconciliations) != set(mismatches)
        or any(
            not isinstance(value, dict) or value.get("state") != "EXACT"
            for value in reconciliations.values()
        )
    ):
        raise ArchiveFailure("PRODUCTION_SETUP_RECONCILIATION_INVALID")
    deferred = setup.get("vector_index_deferred")
    restored = setup.get("vector_index_restored")
    query = setup.get("query_targets")
    restored_job = restored.get("job") if isinstance(restored, dict) else None
    completion_mode = (
        restored.get("completion_mode") if isinstance(restored, dict) else None
    )
    asynchronous_completion = (
        completion_mode == "ASYNCHRONOUS_JOB"
        and isinstance(restored_job, dict)
        and restored_job.get("status") == "succeeded"
        and restored_job.get("fraction_completed") == 1.0
        and restored_job.get("description_matches_create") is True
    )
    synchronous_completion = (
        completion_mode == "SYNCHRONOUS_DDL_NO_JOB"
        and isinstance(restored_job, dict)
        and restored_job.get("status") == "missing"
    )
    if (
        not isinstance(deferred, dict)
        or deferred.get("green") is not True
        or not isinstance(restored, dict)
        or restored.get("green") is not True
        or restored.get("queryable") is not True
        or not isinstance(restored.get("metadata"), dict)
        or restored["metadata"].get("green") is not True
        or not (asynchronous_completion or synchronous_completion)
        or not isinstance(query, dict)
        or query
        != {
            "id_width": 6,
            "vector_rows": 20,
            "expected_vector_rows": 20,
            "receipt_rows": 10,
            "expected_receipt_rows": 10,
            "green": True,
        }
    ):
        raise ArchiveFailure("PRODUCTION_SETUP_INDEX_OR_QUERY_PROOF_INVALID")


def validate_trace_progress(
    archive: tarfile.TarFile,
    manifest: dict[str, Any],
    value: Any,
) -> None:
    name = "preflight-trace-progress.json"
    if name not in manifest["files"] or not isinstance(value, dict):
        raise ArchiveFailure("REMOTE_PREFLIGHT_TRACE_EVIDENCE_MISSING")
    record = read_member_json(archive, "evidence/" + name)
    verify_embedded_hash(record, "progress_receipt_sha256", "TRACE_PROGRESS")
    checks = {
        "version": record.get("version")
        == "ck-pdh3-process-tree-egress-observer-v2",
        "hash": True,
        "non_authoritative": record.get("authoritative") is False,
        "in_progress": record.get("status") == "IN_PROGRESS",
        "one_trace_stream": record.get("trace_stream_count") == 1,
        "maximum_bytes": record.get("maximum_trace_bytes")
        == CONTRACT.TRACE_BYTES_LIMIT,
        "current_bytes": isinstance(record.get("trace_bytes"), int)
        and not isinstance(record.get("trace_bytes"), bool)
        and 0 <= record["trace_bytes"] <= CONTRACT.TRACE_BYTES_LIMIT,
        "projection": isinstance(
            record.get("projected_trace_bytes_24h_conservative"), int
        )
        and not isinstance(
            record.get("projected_trace_bytes_24h_conservative"), bool
        )
        and record["projected_trace_bytes_24h_conservative"]
        <= CONTRACT.TRACE_PREFLIGHT_PROJECTION_LIMIT,
        "cap_not_exceeded": record.get("projected_cap_exceeded") is False,
        "scan_progress": isinstance(record.get("scan_count"), int)
        and not isinstance(record.get("scan_count"), bool)
        and record["scan_count"] > 0,
    }
    age = require_number(
        value.get("age_seconds"), "REMOTE_PREFLIGHT_TRACE_AGE", minimum=-2, maximum=90
    )
    del age
    if value != {
        "receipt_sha256": record["progress_receipt_sha256"],
        "file_sha256": manifest["files"][name],
        "age_seconds": value.get("age_seconds"),
        "checks": checks,
        "green": True,
    } or not all(checks.values()):
        raise ArchiveFailure("REMOTE_PREFLIGHT_TRACE_SEMANTICS_INVALID")


def validate_remote_preflight(
    archive: tarfile.TarFile,
    manifest: dict[str, Any],
    result: dict[str, Any],
    *,
    campaign_id: str,
) -> dict[str, Any]:
    if "remote-preflight.json" not in manifest["files"]:
        raise ArchiveFailure("REMOTE_PREFLIGHT_RECEIPT_MISSING")
    preflight = read_member_json(archive, "evidence/remote-preflight.json")
    verify_embedded_hash(preflight, "preflight_sha256", "REMOTE_PREFLIGHT")
    binding = result.get("remote_preflight")
    if (
        not isinstance(binding, dict)
        or binding.get("required") is not True
        or binding.get("preflight_sha256") != preflight["preflight_sha256"]
        or preflight.get("version") != "ck-pdh3-remote-preflight-v1"
        or preflight.get("green") is not True
        or preflight.get("epoch_count") != CONTRACT.REMOTE_PREFLIGHT_EPOCHS
        or preflight.get("concurrency") != CONTRACT.REMOTE_PREFLIGHT_CONCURRENCY
        or preflight.get("fault_count") != CONTRACT.REMOTE_PREFLIGHT_FAULTS
    ):
        raise ArchiveFailure("REMOTE_PREFLIGHT_SEMANTICS_INVALID")
    expected_counts = expected_dataset_counts()
    metrics = validate_checkpoint_series(
        archive,
        manifest,
        preflight,
        lane="preflight",
        campaign_id=campaign_id,
    )
    reset = preflight.get("control_reset")
    query = preflight.get("query_targets_after_reset")
    trace = preflight.get("trace_progress")
    if (
        preflight.get("static_counts_after_reset") != expected_counts
        or not isinstance(reset, dict)
        or reset.get("version") != "ck-pdh3-preflight-control-reset-v1"
        or reset.get("before") != metrics["final_control_counts"]
        or reset.get("after") != [0, 0, 0]
        or reset.get("preflight_advice_rows") != 0
        or reset.get("green") is not True
        or reset.get("reset_sha256")
        != digest({key: item for key, item in reset.items() if key != "reset_sha256"})
        or not isinstance(query, dict)
        or query
        != {
            "id_width": 6,
            "vector_rows": 20,
            "expected_vector_rows": 20,
            "receipt_rows": 10,
            "expected_receipt_rows": 10,
            "green": True,
        }
    ):
        raise ArchiveFailure("REMOTE_PREFLIGHT_RESET_OR_TRACE_INVALID")
    validate_trace_progress(archive, manifest, trace)
    return metrics


def validate_production_result(
    archive: tarfile.TarFile,
    manifest: dict[str, Any],
    result: dict[str, Any],
    marker: dict[str, Any],
    setup: dict[str, Any],
    teardown: dict[str, Any],
    config: Config,
) -> None:
    expected_contract = CONTRACT.production_contract()
    expected_counts = expected_dataset_counts()
    campaign_id = result.get("campaign_id")
    if (
        result.get("version") != "ck-pdh3-production-scale-result-v1"
        or result.get("status") != "GREEN"
        or result.get("production_mode") is not True
        or result.get("product_candidate") != CONTRACT.PRODUCT_CANDIDATE
        or result.get("plan_sha256") != CONTRACT.PLAN_SHA256
        or result.get("packet_sha256") != config.packet_sha256
        or result.get("contract_sha256") != expected_contract["contract_sha256"]
        or result.get("synthetic_only") is not True
        or result.get("credentials_used") is not False
        or result.get("external_cloud_calls") != 0
        or result.get("cluster_topology") != "THREE_NODES_ONE_SECURE_RUNPOD_HOST"
        or result.get("dataset_counts") != expected_counts
        or result.get("checkpoint_count") != CONTRACT.REQUIRED_CHECKPOINTS
        or result.get("verifier_executions") != CONTRACT.VERIFIER_EXECUTIONS
        or result.get("fault_cycles") != len(CONTRACT.expected_schedule()["fault_epochs"])
        or result.get("wrong_task_vector_links") != 0
        or isinstance(result.get("measured_seconds"), bool)
        or not isinstance(result.get("measured_seconds"), (int, float))
        or not CONTRACT.MEASURED_SECONDS <= result["measured_seconds"] <= CONTRACT.MEASURED_SECONDS + 2
        or result.get("precommit_manifest_sha256") != manifest["manifest_sha256"]
        or not isinstance(campaign_id, str)
        or campaign_id != config.campaign_prefix
    ):
        raise ArchiveFailure("PRODUCTION_RESULT_CONTRACT_MISMATCH")
    checks = result.get("green_checks")
    required_checks = {
        "checkpoint_count",
        "verifier_execution_count",
        "dataset_counts",
        "control_counts",
        "cross_task_vector_links",
        "false_promotions",
        "latency",
        "fault_cycles",
    }
    if not isinstance(checks, dict) or set(checks) != required_checks or not all(checks.values()):
        raise ArchiveFailure("PRODUCTION_RESULT_GREEN_CHECKS_INVALID")
    validate_setup(setup, campaign_id)
    validate_remote_preflight(
        archive,
        manifest,
        result,
        campaign_id=campaign_id,
    )
    metrics = validate_checkpoint_series(
        archive,
        manifest,
        result,
        lane="measured",
        campaign_id=campaign_id,
    )
    first_boundary = metrics["first_boundary_monotonic_ns"]
    last_snapshot = metrics["last_snapshot_monotonic_ns"]
    if not isinstance(first_boundary, int) or not isinstance(last_snapshot, int):
        raise ArchiveFailure("PRODUCTION_MEASURED_BOUNDARY_MISSING")
    recomputed_measured_seconds = (
        last_snapshot
        - (first_boundary - CONTRACT.CHECKPOINT_SECONDS * 1_000_000_000)
    ) / 1_000_000_000
    expected_checks = {
        "checkpoint_count": metrics["checkpoint_count"]
        == CONTRACT.REQUIRED_CHECKPOINTS,
        "verifier_execution_count": metrics["verifier_executions"]
        == CONTRACT.VERIFIER_EXECUTIONS,
        "dataset_counts": result.get("dataset_counts") == expected_counts,
        "control_counts": result.get("control_counts")
        == metrics["final_control_counts"],
        "cross_task_vector_links": result.get("wrong_task_vector_links") == 0,
        "false_promotions": True,
        "latency": metrics["maximum_p99_ms"] <= CONTRACT.P99_LIMIT_MS
        and metrics["maximum_latency_ms"] <= CONTRACT.PMAX_LIMIT_MS,
        "fault_cycles": metrics["fault_cycles"]
        == len(CONTRACT.expected_schedule()["fault_epochs"]),
    }
    if (
        result.get("checkpoint_count") != metrics["checkpoint_count"]
        or result.get("verifier_executions") != metrics["verifier_executions"]
        or result.get("fault_cycles") != metrics["fault_cycles"]
        or result.get("total_measured_operations") != metrics["total_operations"]
        or result.get("maximum_p99_ms") != metrics["maximum_p99_ms"]
        or result.get("maximum_latency_ms") != metrics["maximum_latency_ms"]
        or result.get("control_counts") != metrics["final_control_counts"]
        or result.get("expected_control_counts") != metrics["final_control_counts"]
        or abs(float(result["measured_seconds"]) - recomputed_measured_seconds) > 1e-9
        or result.get("green_checks") != expected_checks
        or result.get("limitations")
        != [
            "SYNTHETIC_ONLY",
            "SINGLE_RUNPOD_HOST",
            "NOT_MULTI_REGION",
            "NOT_PRODUCTION_TRAFFIC",
            "LAMBDA_FAILURES_ARE_FROZEN_LOCAL_ADVICE_STATES",
            "GPU_NOT_USED_BY_CPU_BOUND_PROTOCOL",
        ]
    ):
        raise ArchiveFailure("PRODUCTION_RESULT_RECOMPUTATION_MISMATCH")
    local_teardown = result.get("local_teardown")
    if (
        not isinstance(local_teardown, dict)
        or local_teardown.get("green") is not True
        or local_teardown.get("receipt_sha256") != teardown.get("receipt_sha256")
    ):
        raise ArchiveFailure("RESULT_TEARDOWN_BINDING_INVALID")
    verify_embedded_hash(marker, "marker_sha256", "GREEN_MARKER")
    if (
        marker.get("version") != "ck-pdh3-measured-campaign-green-v1"
        or marker.get("campaign_id") != campaign_id
        or marker.get("result_sha256") != result.get("result_sha256")
        or marker.get("teardown_receipt_sha256") != teardown.get("receipt_sha256")
    ):
        raise ArchiveFailure("GREEN_MARKER_BINDING_INVALID")


def validate_archive(
    archive_path: Path,
    final_state_path: Path,
    config: Config,
) -> tuple[str, dict[str, Any]]:
    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            members = archive.getmembers()
            names = [member.name for member in members]
            if len(names) != len(set(names)) or not all(safe_member_name(name) for name in names):
                raise ArchiveFailure("ARCHIVE_MEMBER_SET_UNSAFE")
            setattr(
                archive,
                "_pdh3_member_index",
                {member.name: member for member in members},
            )
            if any(member.issym() or member.islnk() for member in members):
                raise ArchiveFailure("ARCHIVE_LINK_FORBIDDEN")
            required = {
                "evidence/manifest.json",
                "evidence/teardown.json",
                "network-receipt.json",
                "production.log",
                "production.pid",
                "final-state.json",
            }
            missing = sorted(required - set(names))
            if missing:
                raise ArchiveFailure("ARCHIVE_REQUIRED_MEMBER_MISSING:" + ",".join(missing))
            manifest, terminal_extras = validate_manifest(archive, set(names))
            final_state = read_member_json(archive, "final-state.json")
            if final_state_path.read_bytes() != canonical(final_state):
                raise ArchiveFailure("FINAL_STATE_COPY_MISMATCH")
            network = read_member_json(archive, "network-receipt.json")
            teardown = read_member_json(archive, "evidence/teardown.json")
            verify_embedded_hash(network, "receipt_sha256", "NETWORK_RECEIPT")
            verify_embedded_hash(teardown, "receipt_sha256", "TEARDOWN")
            validate_trace_evidence(archive, set(names), network, config)
            if final_state.get("network-receipt.json") != network:
                raise ArchiveFailure("FINAL_STATE_NETWORK_RECEIPT_MISMATCH")
            if final_state.get("evidence/teardown.json") != teardown:
                raise ArchiveFailure("FINAL_STATE_TEARDOWN_MISMATCH")
            result_present = "evidence/result.json" in names
            marker_present = "evidence/MEASURED_CAMPAIGN_GREEN" in names
            failure_present = "evidence/failure.json" in names
            if result_present and failure_present:
                raise ArchiveFailure("RESULT_FAILURE_NOT_EXCLUSIVE")
            if not result_present and not failure_present:
                if terminal_extras:
                    raise ArchiveFailure("ABSENT_RESULT_TERMINAL_RECORD_UNEXPECTED")
                if (
                    final_state.get("evidence/result.json") is not None
                    or final_state.get("evidence/failure.json") is not None
                    or final_state.get("evidence/MEASURED_CAMPAIGN_GREEN") is not None
                ):
                    raise ArchiveFailure("FINAL_STATE_ABSENT_RESULT_MISMATCH")
                return ABSENT_RESULT, {"reason": "RESULT_AND_FAILURE_ABSENT"}
            if failure_present:
                if marker_present or terminal_extras:
                    raise ArchiveFailure("BLOCKED_TERMINAL_RECORD_UNEXPECTED")
                failure = read_member_json(archive, "evidence/failure.json")
                verify_embedded_hash(failure, "failure_sha256", "FAILURE")
                if final_state.get("evidence/failure.json") != failure:
                    raise ArchiveFailure("FINAL_STATE_FAILURE_MISMATCH")
                if final_state.get("evidence/result.json") is not None:
                    raise ArchiveFailure("FINAL_STATE_RESULT_UNEXPECTED")
                if final_state.get("evidence/MEASURED_CAMPAIGN_GREEN") is not None:
                    raise ArchiveFailure("FINAL_STATE_MARKER_UNEXPECTED")
                if network.get("green") is not False or network.get("child_exit") == 0:
                    raise ArchiveFailure("BLOCKED_NETWORK_STATE_INVALID")
                if not all(teardown.get(key) is True for key in ("nodes_stopped", "ports_closed", "generated_root_removed")):
                    raise ArchiveFailure("BLOCKED_LOCAL_TEARDOWN_INVALID")
                return BLOCKED_COMPLETE, {
                    "failure_sha256": failure["failure_sha256"],
                    "teardown_sha256": teardown["receipt_sha256"],
                }
            result = read_member_json(archive, "evidence/result.json")
            verify_embedded_hash(result, "result_sha256", "RESULT")
            if not marker_present or terminal_extras != TERMINAL_EVIDENCE_RECORDS:
                raise ArchiveFailure("GREEN_TERMINAL_RECORD_SET_INVALID")
            marker = read_member_json(
                archive,
                "evidence/MEASURED_CAMPAIGN_GREEN",
            )
            if final_state.get("evidence/result.json") != result:
                raise ArchiveFailure("FINAL_STATE_RESULT_MISMATCH")
            if final_state.get("evidence/MEASURED_CAMPAIGN_GREEN") != marker:
                raise ArchiveFailure("FINAL_STATE_MARKER_MISMATCH")
            if final_state.get("evidence/failure.json") is not None:
                raise ArchiveFailure("FINAL_STATE_FAILURE_UNEXPECTED")
            checks = result.get("green_checks")
            if (
                result.get("status") != "GREEN"
                or result.get("production_mode") is not True
                or not isinstance(checks, dict)
                or not checks
                or not all(value is True for value in checks.values())
            ):
                raise ArchiveFailure("RESULT_SEMANTICS_INVALID")
            if (
                network.get("green") is not True
                or network.get("child_exit") != 0
                or network.get("external_or_unparseable_count") != 0
            ):
                raise ArchiveFailure("NETWORK_RECEIPT_NOT_GREEN")
            if not all(
                teardown.get(key) is True
                for key in ("database_dropped", "nodes_stopped", "ports_closed", "generated_root_removed")
            ):
                raise ArchiveFailure("GREEN_LOCAL_TEARDOWN_INVALID")
            if "evidence/setup.json" not in names:
                raise ArchiveFailure("PRODUCTION_SETUP_RECEIPT_MISSING")
            setup = read_member_json(archive, "evidence/setup.json")
            verify_embedded_hash(setup, "setup_sha256", "SETUP")
            if final_state.get("evidence/setup.json") != setup:
                raise ArchiveFailure("FINAL_STATE_SETUP_MISMATCH")
            if setup.get("green") is not True:
                raise ArchiveFailure("PRODUCTION_SETUP_NOT_GREEN")
            campaign_ids = {
                result.get("campaign_id"),
                setup.get("campaign_id"),
                teardown.get("campaign_id"),
            }
            if None in campaign_ids or len(campaign_ids) != 1:
                raise ArchiveFailure("CAMPAIGN_ID_CROSS_RECEIPT_MISMATCH")
            validate_production_result(
                archive,
                manifest,
                result,
                marker,
                setup,
                teardown,
                config,
            )
            return GREEN_PENDING_FINAL_GATE, {
                "result_sha256": result["result_sha256"],
                "marker_sha256": marker["marker_sha256"],
                "manifest_sha256": manifest["manifest_sha256"],
                "teardown_sha256": teardown["receipt_sha256"],
                "network_receipt_sha256": network["receipt_sha256"],
                "setup_sha256": setup["setup_sha256"],
            }
    except (
        ArchiveFailure,
        KeyError,
        OSError,
        tarfile.TarError,
        json.JSONDecodeError,
        TypeError,
        ValueError,
        UnicodeError,
    ) as exc:
        return PARTIAL_ARCHIVE, {"reason": str(exc), "error_type": type(exc).__name__}


def provider_command(config: Config, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    verify_cli(config)
    timeout = bounded_timeout(config.closeout_deadline_epoch, config.command_timeout_seconds)
    return run_command([str(config.runpodctl.resolve()), *arguments], timeout=timeout)


def record_provider_result(
    config: Config,
    label: str,
    attempt: int,
    result: subprocess.CompletedProcess[str],
) -> None:
    body = {
        "version": "ck-pdh3-provider-command-v1",
        "label": label,
        "attempt": attempt,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    atomic_write(
        config.retrieval / f"provider-{label}-{attempt:03d}.json",
        canonical({**body, "receipt_sha256": digest(body)}),
    )


def structured_pod_not_found(raw: str) -> bool:
    """Recognize only a numeric JSON 404 explicitly scoped to a missing Pod."""
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return False
    if not isinstance(value, dict):
        return False
    candidates = [value]
    if isinstance(value.get("error"), dict):
        candidates.append(value["error"])
    for candidate in candidates:
        codes = [
            candidate[key]
            for key in ("status", "statusCode", "code")
            if key in candidate
        ]
        if not codes or any(
            isinstance(code, bool) or not isinstance(code, int) or code != 404
            for code in codes
        ):
            continue
        messages = [
            candidate[key]
            for key in ("message", "detail", "error")
            if isinstance(candidate.get(key), str)
        ]
        for message in messages:
            normalized = " ".join(message.lower().split())
            if (
                re.search(r"\bpods?\b", normalized)
                and (
                    re.search(r"\bnot[ -]?found\b", normalized)
                    or re.search(r"\bdoes not exist\b", normalized)
                )
            ):
                return True
    return False


def explicit_not_found(result: subprocess.CompletedProcess[str]) -> bool:
    if result.returncode == 0:
        return False
    payloads = [raw for raw in (result.stdout, result.stderr) if raw.strip()]
    return len(payloads) == 1 and structured_pod_not_found(payloads[0])


def active_campaign_rows(result: subprocess.CompletedProcess[str], prefix: str) -> list[dict[str, Any]]:
    if result.returncode != 0:
        raise TransportFailure("POD_LIST_FAILED")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise TransportFailure("POD_LIST_JSON_INVALID") from exc
    if not isinstance(value, list):
        raise TransportFailure("POD_LIST_SCHEMA_INVALID")
    return [
        row
        for row in value
        if isinstance(row, dict)
        and str(row.get("name", "")).startswith(prefix)
        and str(row.get("desiredStatus", "")).upper() not in INACTIVE_STATES
    ]


def delete_exact_worker(config: Config, log: ChainLog) -> dict[str, Any]:
    config.retrieval.mkdir(parents=True, exist_ok=True)
    attempt = 0
    last_error = "TEARDOWN_NOT_ATTEMPTED"
    while time.time() < config.closeout_deadline_epoch:
        attempt += 1
        try:
            deleted = provider_command(
                config, ["pod", "delete", config.pod_id, "--output", "json"]
            )
            record_provider_result(config, "delete", attempt, deleted)
            log.emit("DELETE_ATTEMPT", {"attempt": attempt, "returncode": deleted.returncode})
            exact = provider_command(
                config, ["pod", "get", config.pod_id, "--output", "json"]
            )
            record_provider_result(config, "get", attempt, exact)
            inventory = provider_command(
                config, ["pod", "list", "--all", "--output", "json"]
            )
            record_provider_result(config, "list", attempt, inventory)
            matching = active_campaign_rows(inventory, config.campaign_prefix)
            if explicit_not_found(exact) and matching == []:
                proof = {
                    "exact_id_absent": True,
                    "campaign_active": [],
                    "attempts": attempt,
                }
                log.emit("TEARDOWN_GREEN", proof)
                return proof
            if exact.returncode != 0 and not explicit_not_found(exact):
                last_error = "EXACT_GET_NOT_EXPLICIT_404"
            elif matching:
                last_error = "CAMPAIGN_ACTIVE_NOT_EMPTY"
            else:
                last_error = "EXACT_ID_STILL_PRESENT"
        except (SupervisorFailure, TransportFailure) as exc:
            last_error = str(exc)
            log.emit(
                "TEARDOWN_RETRY",
                {"attempt": attempt, "reason": last_error},
            )
        remaining = config.closeout_deadline_epoch - time.time()
        if remaining <= 0:
            break
        time.sleep(min(10.0, remaining))
    raise SupervisorFailure("TEARDOWN_NOT_PROVEN:" + last_error)


def write_closeout(
    config: Config,
    state: str,
    campaign_state: str,
    details: dict[str, Any],
    teardown: dict[str, Any] | None,
    log: ChainLog,
) -> None:
    body = {
        "version": "ck-pdh3-supervisor-closeout-v1",
        "state": state,
        "campaign_state": campaign_state,
        "pod_id": config.pod_id,
        "pod_name": config.pod_name,
        "details": details,
        "provider_teardown": teardown,
        "supervisor_terminal_hash_before_closeout": log.previous,
    }
    atomic_write(
        config.retrieval / "closeout.json",
        canonical({**body, "closeout_sha256": digest(body)}),
    )


def supervise(config: Config) -> tuple[str, int]:
    validate_config(config)
    verify_cli(config)
    log = ChainLog(config.log.resolve())
    log.emit(
        "SUPERVISOR_START",
        {"pod_id": config.pod_id, "pod_name": config.pod_name},
    )
    campaign_state = ABSENT_RESULT
    final_state = ABSENT_RESULT
    details: dict[str, Any] = {"reason": "REMOTE_RESULT_NOT_OBSERVED"}
    teardown: dict[str, Any] | None = None
    try:
        if wait_for_terminal(config, log):
            try:
                package_remote(config)
                archive, state_path = retrieve(config, log)
                campaign_state, details = validate_archive(
                    archive,
                    state_path,
                    config,
                )
                final_state = campaign_state
            except TransportFailure as exc:
                campaign_state = TRANSPORT_FAILURE
                final_state = TRANSPORT_FAILURE
                details = {"reason": str(exc)}
            except (ArchiveFailure, OSError) as exc:
                campaign_state = PARTIAL_ARCHIVE
                final_state = PARTIAL_ARCHIVE
                details = {"reason": str(exc), "error_type": type(exc).__name__}
        else:
            campaign_state = ABSENT_RESULT
            final_state = ABSENT_RESULT
    finally:
        try:
            teardown = delete_exact_worker(config, log)
        except (SupervisorFailure, TransportFailure) as exc:
            details = {**details, "teardown_error": str(exc)}
            final_state = TEARDOWN_UNPROVEN
        log.emit(
            "SUPERVISOR_TERMINAL",
            {"state": final_state, "campaign_state": campaign_state},
        )
        write_closeout(config, final_state, campaign_state, details, teardown, log)
    return final_state, EXIT_CODES[final_state]


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--runpodctl", type=Path, required=True)
    value.add_argument("--runpodctl-sha256", required=True)
    value.add_argument("--pod-id", required=True)
    value.add_argument("--pod-name", required=True)
    value.add_argument("--campaign-prefix", required=True)
    value.add_argument("--ssh-config", type=Path, required=True)
    value.add_argument("--ssh-alias", required=True)
    value.add_argument("--remote-root", required=True)
    value.add_argument("--retrieval", type=Path, required=True)
    value.add_argument("--log", type=Path, required=True)
    value.add_argument("--packet-sha256", required=True)
    value.add_argument("--trace-tool-sha256", required=True)
    value.add_argument("--trace-command-sha256", required=True)
    value.add_argument("--closeout-deadline-epoch", type=float, required=True)
    value.add_argument("--poll-seconds", type=float, default=300.0)
    value.add_argument("--command-timeout-seconds", type=int, default=60)
    value.add_argument("--transfer-timeout-seconds", type=int, default=1_800)
    value.add_argument("--teardown-reserve-seconds", type=int, default=300)
    return value


def main() -> int:
    args = parser().parse_args()
    config = Config(
        runpodctl=args.runpodctl.resolve(),
        runpodctl_sha256=args.runpodctl_sha256,
        pod_id=args.pod_id,
        pod_name=args.pod_name,
        campaign_prefix=args.campaign_prefix,
        ssh_config=args.ssh_config.resolve(),
        ssh_alias=args.ssh_alias,
        remote_root=args.remote_root,
        retrieval=args.retrieval.resolve(),
        log=args.log.resolve(),
        packet_sha256=args.packet_sha256,
        trace_tool_sha256=args.trace_tool_sha256,
        trace_command_sha256=args.trace_command_sha256,
        closeout_deadline_epoch=args.closeout_deadline_epoch,
        poll_seconds=args.poll_seconds,
        command_timeout_seconds=args.command_timeout_seconds,
        transfer_timeout_seconds=args.transfer_timeout_seconds,
        teardown_reserve_seconds=args.teardown_reserve_seconds,
    )
    state, exit_code = supervise(config)
    print(canonical({"state": state, "exit_code": exit_code}).decode("utf-8"))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
