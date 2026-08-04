"""Scenario-driven recovery surface over the packaged P7 authority.

The public command accepts only canonical typed records and explicitly
declared disposable roots. It never performs undelete or filesystem forensics:
every promoted byte must already exist in a hash-bound representation.
"""
from __future__ import annotations

from dataclasses import dataclass
import fcntl
import json
import os
from pathlib import Path
import shutil
import stat
import sys
from typing import Any, BinaryIO

from p7_runtime import fresh_context
from p7_runtime import records as p7


REQUEST_VERSION = "ck-recovery-request-v1"
CONTRACT_SHA256 = "52fbe37a309cebd3983692c58460fbb6dca64d13eaf6713a5d3c60e88af2fb78"  # pragma: allowlist secret -- public contract SHA-256
MAX_RECORD_BYTES = 65_536
MAX_FILE_BYTES = 65_536
MAX_AGGREGATE_BYTES = 1_048_576
REQUEST_FIELDS = {
    "version",
    "request_id",
    "context",
    "loss_receipt",
    "candidates",
    "warrant",
}


class SurfaceError(ValueError):
    """Stable fail-closed public-surface error."""

    def __init__(
        self,
        reason: str,
        *,
        verdict: str = "INVALID",
        exit_code: int = 2,
        action_taken: str = "NONE",
    ) -> None:
        super().__init__(reason)
        self.reason = reason
        self.verdict = verdict
        self.exit_code = exit_code
        self.action_taken = action_taken


@dataclass(frozen=True)
class Roots:
    sandbox: Path
    request: Path
    workspace: Path
    representation: Path
    custody: Path
    output: Path


def canonical_json(value: Any) -> bytes:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SurfaceError("MALFORMED_RECORD") from exc
    if len(raw) > MAX_RECORD_BYTES:
        raise SurfaceError("RECORD_TOO_LARGE")
    return raw


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SurfaceError("REQUEST_NOT_CANONICAL")
        result[key] = value
    return result


def _read_bounded(handle: BinaryIO, limit: int, reason: str) -> bytes:
    chunks: list[bytes] = []
    size = 0
    while True:
        chunk = handle.read(min(65_536, limit + 1 - size))
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        size += len(chunk)
        if size > limit:
            raise SurfaceError(reason)


def _load_request(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        with path.open("rb") as handle:
            raw = _read_bounded(handle, MAX_RECORD_BYTES, "RECORD_TOO_LARGE")
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                SurfaceError("REQUEST_NOT_CANONICAL")
            ),
        )
    except SurfaceError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, OSError) as exc:
        raise SurfaceError("REQUEST_NOT_CANONICAL") from exc
    if not isinstance(value, dict) or raw != canonical_json(value):
        raise SurfaceError("REQUEST_NOT_CANONICAL")
    return value, raw


def _overlap(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def _strict_descendant(path: Path, root: Path) -> bool:
    return path != root and root in path.parents


def _reject_symlink_chain(path: Path, root: Path) -> None:
    if not _strict_descendant(path, root):
        raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            raise SurfaceError("ROOT_TOPOLOGY_UNSAFE") from exc
        if stat.S_ISLNK(mode):
            raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")


def validate_roots(
    request: str | Path,
    sandbox_root: str | Path,
    workspace: str | Path,
    representation_root: str | Path,
    custody_root: str | Path,
    output_root: str | Path,
) -> Roots:
    raw_paths = {
        "sandbox": Path(sandbox_root),
        "request": Path(request),
        "workspace": Path(workspace),
        "representation": Path(representation_root),
        "custody": Path(custody_root),
        "output": Path(output_root),
    }
    try:
        resolved = {name: path.resolve(strict=True) for name, path in raw_paths.items()}
    except (OSError, RuntimeError) as exc:
        raise SurfaceError("ROOT_TOPOLOGY_UNSAFE") from exc
    sandbox = resolved["sandbox"]
    if raw_paths["sandbox"].is_symlink() or not sandbox.is_dir():
        raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
    home = Path.home().resolve()
    if _overlap(sandbox, home):
        raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
    package_root = Path(__file__).resolve().parent
    for name in ("request", "workspace", "representation", "custody", "output"):
        path = resolved[name]
        if not _strict_descendant(path, sandbox):
            raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
        _reject_symlink_chain(path, sandbox)
    if not resolved["request"].is_file() or raw_paths["request"].is_symlink():
        raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
    roots = [resolved[name] for name in ("workspace", "representation", "custody", "output")]
    if any(not path.is_dir() for path in roots):
        raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
    for index, first in enumerate(roots):
        if _overlap(resolved["request"], first):
            raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
        if _overlap(first, home) or _overlap(first, package_root):
            raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
        for second in roots[index + 1:]:
            if _overlap(first, second):
                raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
    try:
        if any(resolved["output"].iterdir()):
            raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
    except OSError as exc:
        raise SurfaceError("ROOT_TOPOLOGY_UNSAFE") from exc
    return Roots(
        sandbox=sandbox,
        request=resolved["request"],
        workspace=resolved["workspace"],
        representation=resolved["representation"],
        custody=resolved["custody"],
        output=resolved["output"],
    )


def _validate_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict) or set(request) != REQUEST_FIELDS:
        raise SurfaceError("MALFORMED_RECORD")
    if request["version"] != REQUEST_VERSION:
        raise SurfaceError(p7.UNSUPPORTED_SCHEMA)
    if not isinstance(request["context"], dict):
        raise SurfaceError("MALFORMED_RECORD")
    try:
        p7.require_id(request["request_id"])
        # Validate the manifest directly first so the public surface preserves
        # P7's specific UNSAFE_PATH/UNSUPPORTED_SCHEMA reason instead of the
        # context wrapper's intentionally generic MALFORMED_RECORD code.
        p7.validate_manifest(request["context"].get("manifest"))
        p7.validate_context(request["context"])
    except p7.RecoveryError as exc:
        raise SurfaceError(str(exc)) from exc
    candidates = request["candidates"]
    if not isinstance(candidates, list):
        raise SurfaceError("MALFORMED_RECORD")
    for candidate in candidates:
        try:
            p7.validate_candidate(candidate)
            p7.canonical_json(candidate)
        except p7.RecoveryError as exc:
            raise SurfaceError(str(exc)) from exc
    manifest = request["context"]["manifest"]
    loss = request["loss_receipt"]
    if loss is not None:
        try:
            p7.validate_loss_receipt(loss)
        except p7.RecoveryError as exc:
            raise SurfaceError(str(exc)) from exc
        if (
            loss["task_id"] != manifest["task_id"]
            or loss["manifest_hash"] != p7.sha256_hex(manifest)
        ):
            raise SurfaceError("LOSS_MANIFEST_MISMATCH")
        lost = loss["lost_paths"]
        if len(set(lost)) != len(lost) or not set(lost).issubset(p7.declared_paths(manifest)):
            raise SurfaceError("LOSS_MANIFEST_MISMATCH")
    warrant = request["warrant"]
    if warrant is not None:
        try:
            p7.validate_warrant(warrant)
        except p7.RecoveryError as exc:
            raise SurfaceError(str(exc)) from exc
        if warrant["state"] != "ISSUED":
            raise SurfaceError(p7.WARRANT_REPLAY, verdict="REFUSE", exit_code=1)
    canonical_json(request)
    return request


def _safe_relative_file(root: Path, relative: str) -> Path | None:
    try:
        p7.validate_relative_path(relative)
    except p7.RecoveryError as exc:
        raise SurfaceError(str(exc)) from exc
    current = root
    parts = relative.split("/")
    for index, part in enumerate(parts):
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise SurfaceError("REPRESENTATION_UNSAFE") from exc
        if stat.S_ISLNK(mode):
            raise SurfaceError("REPRESENTATION_UNSAFE")
        if index < len(parts) - 1 and not stat.S_ISDIR(mode):
            raise SurfaceError("REPRESENTATION_UNSAFE")
        if index == len(parts) - 1:
            if not stat.S_ISREG(mode) or mode & 0o111:
                raise SurfaceError("REPRESENTATION_UNSAFE")
    return current


def _safe_workspace_target(root: Path, relative: str) -> tuple[Path, bool]:
    try:
        p7.validate_relative_path(relative)
    except p7.RecoveryError as exc:
        raise SurfaceError(str(exc)) from exc
    current = root
    parts = relative.split("/")
    for index, part in enumerate(parts):
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            return root.joinpath(*parts), False
        except OSError as exc:
            raise SurfaceError("ROOT_TOPOLOGY_UNSAFE") from exc
        if stat.S_ISLNK(mode):
            raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
        if index < len(parts) - 1 and not stat.S_ISDIR(mode):
            raise SurfaceError("WORKSPACE_PATH_CONFLICT", verdict="REFUSE", exit_code=1)
        if index == len(parts) - 1:
            return current, True
    raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")


def _read_representation(path: Path) -> bytes:
    try:
        with path.open("rb") as handle:
            return _read_bounded(handle, MAX_FILE_BYTES, "AGGREGATE_LIMIT_EXCEEDED")
    except SurfaceError:
        raise
    except OSError as exc:
        raise SurfaceError("REPRESENTATION_UNSAFE") from exc


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    raw = canonical_json(value) + b"\n"
    if path.parent.is_symlink() or (path.exists() and path.is_symlink()):
        raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def _load_sidecar(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
    try:
        with path.open("rb") as handle:
            raw = _read_bounded(handle, MAX_RECORD_BYTES + 1, "RECORD_TOO_LARGE")
        if not raw.endswith(b"\n"):
            raise SurfaceError("REQUEST_NOT_CANONICAL")
        value = json.loads(raw[:-1].decode("utf-8"), object_pairs_hook=_unique_object)
    except SurfaceError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SurfaceError("REQUEST_NOT_CANONICAL") from exc
    if not isinstance(value, dict) or raw != canonical_json(value) + b"\n":
        raise SurfaceError("REQUEST_NOT_CANONICAL")
    expected = {
        "version",
        "warrant_id",
        "task_id",
        "candidate_id",
        "request_hash",
        "decision_hash",
        "state",
        "state_hash",
    }
    if set(value) != expected:
        raise SurfaceError("MALFORMED_RECORD")
    body = {key: value[key] for key in value if key != "state_hash"}
    if value["state_hash"] != p7.sha256_hex(body):
        raise SurfaceError("TAMPERED_EVIDENCE")
    return value


def _sidecar(
    warrant: dict[str, Any], request_hash: str, decision_hash: str, state: str
) -> dict[str, Any]:
    body = {
        "version": "ck-custody-v1",
        "warrant_id": warrant["warrant_id"],
        "task_id": warrant["task_id"],
        "candidate_id": warrant["candidate_id"],
        "request_hash": request_hash,
        "decision_hash": decision_hash,
        "state": state,
    }
    return dict(body, state_hash=p7.sha256_hex(body))


def _ensure_private_directory(root: Path, name: str) -> Path:
    path = root / name
    try:
        path.mkdir(mode=0o700)
    except FileExistsError:
        pass
    except OSError as exc:
        raise SurfaceError("ROOT_TOPOLOGY_UNSAFE") from exc
    if path.is_symlink() or not path.is_dir():
        raise SurfaceError("ROOT_TOPOLOGY_UNSAFE")
    return path


def _refusal_decision(
    request: dict[str, Any], reason: str
) -> dict[str, Any]:
    manifest = request["context"]["manifest"]
    return p7.make_decision(
        manifest["task_id"], "REFUSE", reason, None, request["candidates"]
    )


def _unrecovered_ledger(
    request: dict[str, Any], promoted_paths: list[str]
) -> dict[str, Any]:
    loss = request["loss_receipt"]
    lost_paths = [] if loss is None else sorted(loss["lost_paths"])
    promoted = sorted(promoted_paths)
    body = {
        "version": "ck-unrecovered-ledger-v1",
        "task_id": request["context"]["manifest"]["task_id"],
        "manifest_hash": p7.sha256_hex(request["context"]["manifest"]),
        "recovered_paths": promoted,
        "unrecovered_items": [
            {"path": path, "reason": "NO_PROVEN_REPRESENTATION"}
            for path in lost_paths
            if path not in promoted
        ],
    }
    return dict(body, ledger_hash=p7.sha256_hex(body))


def _mutation_manifest(
    request_id: str,
    promoted: dict[str, bytes],
    *,
    interrupted: bool = False,
    preservation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = {
        "version": "ck-mutation-manifest-v1",
        "request_id": request_id,
        "promoted_paths": sorted(promoted),
        "file_hashes": {path: p7.sha256_hex(promoted[path]) for path in sorted(promoted)},
        "interrupted": interrupted,
        "preservation": preservation or {
            "verified": False,
            "before_hash": None,
            "after_hash": None,
            "preserved_paths": [],
        },
    }
    return dict(body, manifest_hash=p7.sha256_hex(body))


def _workspace_snapshot(workspace: Path) -> dict[str, str]:
    """Hash every pre-existing regular file in the successor workspace."""
    snapshot: dict[str, str] = {}
    for root, directories, files in os.walk(workspace, topdown=True, followlinks=False):
        root_path = Path(root)
        for name in sorted(directories):
            if (root_path / name).is_symlink():
                raise SurfaceError("WORKSPACE_SYMLINK_UNSAFE")
        for name in sorted(files):
            path = root_path / name
            if path.is_symlink() or not path.is_file():
                raise SurfaceError("WORKSPACE_FILE_UNSAFE")
            relative = path.relative_to(workspace).as_posix()
            snapshot[relative] = p7.sha256_hex(path.read_bytes())
    return snapshot


def _preservation_proof(before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
    changed = sorted(path for path, value in before.items() if after.get(path) != value)
    if changed:
        raise SurfaceError(
            "PRESERVATION_PROOF_FAILED",
            action_taken="WARRANT_CONSUMED_PRESERVATION_UNPROVEN",
        )
    body = {
        "verified": True,
        "before_hash": p7.sha256_hex(canonical_json(before)),
        "after_hash": p7.sha256_hex(canonical_json(after)),
        "preserved_paths": sorted(before),
        "changed_paths": changed,
    }
    return body


def _seal_no_action(request_hash: str) -> dict[str, Any]:
    body = {
        "version": "ck-no-action-receipt-v1",
        "request_hash": request_hash,
        "verdict": "NO_ACTION",
        "reason": "NO_DECLARED_LOSS",
        "action_taken": "NONE",
    }
    return dict(body, receipt_hash=p7.sha256_hex(body))


def _write_outputs(
    output_root: Path,
    request_hash: str,
    decision: dict[str, Any],
    receipt: dict[str, Any],
    ledger: dict[str, Any],
    mutation: dict[str, Any],
    verdict: str,
    reason: str,
    fresh_ok: bool,
    fresh_reason: str,
) -> dict[str, Any]:
    receipt_name = (
        "promotion-receipt.json"
        if verdict == "PROMOTE"
        else "no-action-receipt.json"
        if verdict == "NO_ACTION"
        else "refusal-receipt.json"
    )
    records = {
        "decision.json": decision,
        receipt_name: receipt,
        "unrecovered-ledger.json": ledger,
        "mutation-manifest.json": mutation,
    }
    for name, value in records.items():
        _atomic_json(output_root / name, value)
    body = {
        "version": "ck-recovery-summary-v1",
        "verdict": verdict,
        "reason": reason,
        "action_taken": "VERIFIED_REPRESENTATION_PROMOTED" if verdict == "PROMOTE" else "NONE",
        "request_hash": request_hash,
        "contract_hash": CONTRACT_SHA256,
        "decision_hash": p7.sha256_hex(decision),
        "receipt_hash": receipt["receipt_hash"],
        "ledger_hash": ledger["ledger_hash"],
        "mutation_manifest_hash": mutation["manifest_hash"],
        "fresh_context_continued": fresh_ok,
        "fresh_context_reason": fresh_reason,
        "network_used": False,
        "credentials_used": False,
        "files": sorted(records),
    }
    summary = dict(body, summary_hash=p7.sha256_hex(body))
    _atomic_json(output_root / "summary.json", summary)
    return summary


def _write_refusal(
    roots: Roots, request: dict[str, Any], request_hash: str, reason: str
) -> dict[str, Any]:
    decision = _refusal_decision(request, reason)
    receipt = p7.build_refusal_receipt(decision)
    return _write_outputs(
        roots.output,
        request_hash,
        decision,
        receipt,
        _unrecovered_ledger(request, []),
        _mutation_manifest(request["request_id"], {}),
        "REFUSE",
        reason,
        False,
        "NOT_A_PROMOTION",
    )


def _stage_files(workspace: Path, request_id: str, files: dict[str, bytes]) -> Path:
    stage = workspace / f".ck-stage-{request_id}"
    try:
        stage.mkdir(mode=0o700)
    except OSError as exc:
        raise SurfaceError("PROMOTION_INTERRUPTED") from exc
    try:
        for index, path in enumerate(sorted(files)):
            target = stage / f"{index:04d}.bin"
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(target, flags, 0o600)
            with os.fdopen(descriptor, "wb", closefd=True) as handle:
                handle.write(files[path])
                handle.flush()
                os.fsync(handle.fileno())
        _fsync_directory(stage)
        _fsync_directory(workspace)
        return stage
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _open_child_directory(parent_fd: int, name: str) -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        return os.open(name, flags, dir_fd=parent_fd)
    except FileNotFoundError:
        os.mkdir(name, mode=0o700, dir_fd=parent_fd)
        os.fsync(parent_fd)
        return os.open(name, flags, dir_fd=parent_fd)


def _promote_staged(
    workspace: Path,
    stage: Path,
    files: dict[str, bytes],
    *,
    fault: str | None,
) -> dict[str, bytes]:
    promoted: dict[str, bytes] = {}
    workspace_fd = os.open(workspace, os.O_RDONLY)
    stage_fd = os.open(stage, os.O_RDONLY)
    try:
        for index, relative in enumerate(sorted(files)):
            parts = relative.split("/")
            parent_fd = os.dup(workspace_fd)
            try:
                for part in parts[:-1]:
                    child_fd = _open_child_directory(parent_fd, part)
                    os.close(parent_fd)
                    parent_fd = child_fd
                os.link(
                    f"{index:04d}.bin",
                    parts[-1],
                    src_dir_fd=stage_fd,
                    dst_dir_fd=parent_fd,
                    follow_symlinks=False,
                )
                os.fsync(parent_fd)
                promoted[relative] = files[relative]
            finally:
                os.close(parent_fd)
            if fault == "after-first-file" and len(promoted) == 1:
                raise SurfaceError(
                    "PROMOTION_INTERRUPTED",
                    action_taken="PARTIAL_PROMOTION_WARRANT_CONSUMED",
                )
        return promoted
    except SurfaceError:
        raise
    except OSError as exc:
        raise SurfaceError(
            "PROMOTION_INTERRUPTED",
            action_taken=(
                "PARTIAL_PROMOTION_WARRANT_CONSUMED" if promoted else "WARRANT_CONSUMED_NO_PROMOTION"
            ),
        ) from exc
    finally:
        os.close(stage_fd)
        os.close(workspace_fd)


def execute_recovery(
    *,
    request_path: str | Path,
    sandbox_root: str | Path,
    workspace: str | Path,
    representation_root: str | Path,
    custody_root: str | Path,
    output_root: str | Path,
    fault: str | None = None,
) -> tuple[int, dict[str, Any]]:
    """Execute one deterministic recovery request.

    ``fault`` is test-only and is not exposed by the public CLI.
    """
    roots = validate_roots(
        request_path,
        sandbox_root,
        workspace,
        representation_root,
        custody_root,
        output_root,
    )
    request, raw_request = _load_request(roots.request)
    request = _validate_request(request)
    request_hash = p7.sha256_hex(raw_request)
    manifest = request["context"]["manifest"]
    if request["loss_receipt"] is None:
        decision = {
            "version": "ck-recovery-decision-v1",
            "task_id": manifest["task_id"],
            "decision": "NO_ACTION",
            "reason": "NO_DECLARED_LOSS",
            "candidate_id": None,
            "candidates_hash": p7.sha256_hex([]),
        }
        summary = _write_outputs(
            roots.output,
            request_hash,
            decision,
            _seal_no_action(request_hash),
            _unrecovered_ledger(request, []),
            _mutation_manifest(request["request_id"], {}),
            "NO_ACTION",
            "NO_DECLARED_LOSS",
            False,
            "NO_RECOVERY_REQUIRED",
        )
        return 0, summary

    decision = p7.select_candidate(request["candidates"], request["context"])
    if decision["decision"] != "PROMOTE":
        summary = _write_refusal(roots, request, request_hash, decision["reason"])
        return 1, summary
    candidate = next(
        item for item in request["candidates"] if item["candidate_id"] == decision["candidate_id"]
    )
    warrant = request["warrant"]
    if warrant is None:
        return 1, _write_refusal(roots, request, request_hash, "WARRANT_REQUIRED")
    decision_hash = p7.sha256_hex(decision)
    if (
        warrant["task_id"] != decision["task_id"]
        or warrant["candidate_id"] != decision["candidate_id"]
        or warrant["decision_hash"] != decision_hash
    ):
        return 1, _write_refusal(roots, request, request_hash, "WARRANT_BINDING_MISMATCH")

    # Replay is a custody fact and must dominate incidental successor state.
    # A previous interrupted promotion may have written a strict prefix, but
    # the consumed warrant still makes every later invocation a replay.
    existing_state_path = (
        roots.custody / "warrants" / f"{warrant['warrant_id']}.json"
    )
    if existing_state_path.exists():
        existing_state = _load_sidecar(existing_state_path)
        if existing_state["state"] in {"CONSUMED", "INVALID"}:
            return 1, _write_refusal(
                roots, request, request_hash, p7.WARRANT_REPLAY
            )
        if (
            existing_state["request_hash"] != request_hash
            or existing_state["decision_hash"] != decision_hash
        ):
            return 1, _write_refusal(
                roots, request, request_hash, "WARRANT_BINDING_MISMATCH"
            )

    lost_paths = set(request["loss_receipt"]["lost_paths"])
    candidate_base = roots.representation / candidate["candidate_id"]
    if candidate_base.exists():
        if candidate_base.is_symlink() or not candidate_base.is_dir():
            raise SurfaceError("REPRESENTATION_UNSAFE")
    representations: dict[str, bytes] = {}
    aggregate = 0
    for relative in sorted(lost_paths & set(candidate["declared_paths"])):
        representation = _safe_relative_file(candidate_base, relative)
        if representation is None:
            continue
        raw = _read_representation(representation)
        aggregate += len(raw)
        if aggregate > MAX_AGGREGATE_BYTES:
            raise SurfaceError("AGGREGATE_LIMIT_EXCEEDED")
        if p7.sha256_hex(raw) != candidate["file_hashes"][relative]:
            raise SurfaceError("REPRESENTATION_HASH_MISMATCH")
        _, exists = _safe_workspace_target(roots.workspace, relative)
        if exists:
            return 1, _write_refusal(
                roots, request, request_hash, "WORKSPACE_PATH_CONFLICT"
            )
        representations[relative] = raw
    if not representations:
        return 1, _write_refusal(
            roots, request, request_hash, p7.NO_SURVIVING_CANDIDATE
        )

    test_path = candidate["executable_test"]["path"]
    if test_path in lost_paths and test_path not in representations:
        return 1, _write_refusal(
            roots, request, request_hash, p7.EXECUTABLE_TEST_FAILED
        )
    if test_path not in lost_paths:
        existing_test = _safe_relative_file(roots.workspace, test_path)
        if existing_test is None:
            return 1, _write_refusal(
                roots, request, request_hash, p7.EXECUTABLE_TEST_FAILED
            )
        if p7.sha256_hex(_read_representation(existing_test)) != candidate["file_hashes"][test_path]:
            return 1, _write_refusal(
                roots, request, request_hash, p7.EXECUTABLE_TEST_FAILED
            )

    lock_dir = _ensure_private_directory(roots.custody, "locks")
    warrant_dir = _ensure_private_directory(roots.custody, "warrants")
    lock_path = lock_dir / f"{warrant['warrant_id']}.lock"
    state_path = warrant_dir / f"{warrant['warrant_id']}.json"
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    lock_fd = os.open(lock_path, flags, 0o600)
    stage: Path | None = None
    promoted: dict[str, bytes] = {}
    preservation_before: dict[str, str] = {}
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        if state_path.exists():
            state = _load_sidecar(state_path)
            if state["state"] in {"CONSUMED", "INVALID"}:
                return 1, _write_refusal(roots, request, request_hash, p7.WARRANT_REPLAY)
            if (
                state["request_hash"] != request_hash
                or state["decision_hash"] != decision_hash
            ):
                return 1, _write_refusal(
                    roots, request, request_hash, "WARRANT_BINDING_MISMATCH"
                )
        else:
            _atomic_json(
                state_path,
                _sidecar(warrant, request_hash, decision_hash, "ISSUED"),
            )
        preservation_before = _workspace_snapshot(roots.workspace)
        stage = _stage_files(roots.workspace, request["request_id"], representations)
        _atomic_json(
            state_path,
            _sidecar(warrant, request_hash, decision_hash, "CONSUMED"),
        )
        if fault == "after-consume":
            raise SurfaceError(
                "PROMOTION_INTERRUPTED",
                action_taken="WARRANT_CONSUMED_NO_PROMOTION",
            )
        promoted = _promote_staged(
            roots.workspace,
            stage,
            representations,
            fault=fault,
        )
    finally:
        if stage is not None:
            shutil.rmtree(stage, ignore_errors=True)
            try:
                _fsync_directory(roots.workspace)
            except OSError:
                pass
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)

    receipt = p7.build_promotion_receipt(decision, dict(warrant, state="CONSUMED"), list(promoted))
    ledger = _unrecovered_ledger(request, list(promoted))
    preservation = _preservation_proof(preservation_before, _workspace_snapshot(roots.workspace))
    mutation = _mutation_manifest(request["request_id"], promoted, preservation=preservation)
    fresh_ok, fresh_reason = fresh_context.verify_workspace(
        decision, candidate, roots.workspace
    )
    if not fresh_ok:
        raise SurfaceError(
            "PROMOTION_INTERRUPTED",
            action_taken="WARRANT_CONSUMED_PROMOTION_UNVERIFIED",
        )
    summary = _write_outputs(
        roots.output,
        request_hash,
        decision,
        receipt,
        ledger,
        mutation,
        "PROMOTE",
        decision["reason"],
        fresh_ok,
        fresh_reason,
    )
    return 0, summary


def run_cli(args: Any) -> int:
    try:
        status, summary = execute_recovery(
            request_path=args.request,
            sandbox_root=args.sandbox_root,
            workspace=args.workspace,
            representation_root=args.representation_root,
            custody_root=args.custody_root,
            output_root=args.output_root,
        )
        print(canonical_json(summary).decode("utf-8"))
        return status
    except SurfaceError as exc:
        result = {
            "version": "ck-recovery-error-v1",
            "verdict": exc.verdict,
            "reason": exc.reason,
            "action_taken": exc.action_taken,
        }
        print(canonical_json(result).decode("utf-8"), file=sys.stderr)
        return exc.exit_code
    except (OSError, p7.RecoveryError, RuntimeError) as exc:
        result = {
            "version": "ck-recovery-error-v1",
            "verdict": "INVALID",
            "reason": str(exc) or "DEPENDENCY_UNAVAILABLE",
            "action_taken": "NONE",
        }
        print(canonical_json(result).decode("utf-8"), file=sys.stderr)
        return 2
