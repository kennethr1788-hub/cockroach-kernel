"""Deterministic coexistence resolver for Git, captured-child, and backup state.

This module is intentionally pure: it validates hash-bound candidate manifests,
applies the R12 defect precedence, and returns a verdict.  It never reads a
filesystem, chooses bytes from an unbound path, calls a model, or mutates a
successor workspace.  The execution harness is responsible for materializing
only the selected manifest after independently verifying its bytes.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any, Iterable

HEX64 = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
VERSION = 1
VERDICTS = {"PROMOTE", "REFUSE", "INVALID"}


class V5ValidationError(ValueError):
    """Internal typed validation failure; callers receive stable reason codes."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_value(value: Any) -> str:
    return sha256_bytes(value if isinstance(value, bytes) else canonical_json(value))


def _hash(value: Any, field: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise V5ValidationError(f"{field}_HASH_INVALID")
    return value


def _id(value: Any, field: str) -> str:
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise V5ValidationError(f"{field}_ID_INVALID")
    return value


def _safe_path(path: Any) -> str:
    if not isinstance(path, str) or not path or "\x00" in path or "\\" in path:
        raise V5ValidationError("REFUSE_UNSAFE_PATH")
    if path.startswith("/") or any(part in {"", ".", ".."} for part in path.split("/")):
        raise V5ValidationError("REFUSE_UNSAFE_PATH")
    if path != unicodedata.normalize("NFC", path):
        raise V5ValidationError("REFUSE_UNSAFE_PATH")
    return path


def _projection(paths: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: item[key] for key in ("path", "type", "executable", "sha256", "target")
             if key in item} for item in sorted(paths, key=lambda p: p["path"])]


def _manifest_without_hash(manifest: dict[str, Any]) -> dict[str, Any]:
    return {key: manifest[key] for key in manifest if key != "manifest_sha256"}


def _validate_manifest(manifest: Any, *, lineage_type: str,
                       expected_parent: str | None) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise V5ValidationError("REFUSE_INVALID_BACKUP" if lineage_type == "INDEPENDENT_BACKUP"
                                else "REFUSE_INVALID_CANDIDATE")
    required = {"version", "capture_id", "lineage_type", "parent_content_root_sha256",
                "paths", "content_root_sha256", "manifest_sha256"}
    if set(manifest) != required:
        raise V5ValidationError("REFUSE_INVALID_BACKUP" if lineage_type == "INDEPENDENT_BACKUP"
                                else "REFUSE_INVALID_CANDIDATE")
    if manifest["version"] != VERSION or manifest["lineage_type"] != lineage_type:
        raise V5ValidationError("REFUSE_INVALID_BACKUP" if lineage_type == "INDEPENDENT_BACKUP"
                                else "REFUSE_INVALID_CANDIDATE")
    _id(manifest["capture_id"], "CAPTURE")
    parent = manifest["parent_content_root_sha256"]
    if parent is not None:
        _hash(parent, "PARENT")
    if lineage_type == "CAPTURED_CHILD" and expected_parent is not None and parent != expected_parent:
        raise V5ValidationError("INVALID_LINEAGE")
    paths = manifest["paths"]
    if not isinstance(paths, list) or not paths:
        raise V5ValidationError("REFUSE_INVALID_BACKUP" if lineage_type == "INDEPENDENT_BACKUP"
                                else "REFUSE_INVALID_CANDIDATE")
    seen: set[str] = set()
    folded: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for item in paths:
        if not isinstance(item, dict) or set(item) not in (
            {"path", "type", "executable", "sha256"},
            {"path", "type", "executable", "sha256", "target"},
        ):
            raise V5ValidationError("REFUSE_UNSAFE_PATH" if isinstance(item, dict) and "path" in item and
                                    (isinstance(item.get("path"), str) and
                                     (item["path"].startswith("/") or ".." in item["path"]))
                                    else ("REFUSE_INVALID_BACKUP" if lineage_type == "INDEPENDENT_BACKUP"
                                          else "REFUSE_INVALID_CANDIDATE"))
        path = _safe_path(item.get("path"))
        folded_key = unicodedata.normalize("NFC", path).casefold()
        if path in seen or folded_key in folded:
            raise V5ValidationError("REFUSE_UNSAFE_PATH")
        seen.add(path)
        folded.add(folded_key)
        if item.get("type") not in {"file", "directory", "symlink"}:
            raise V5ValidationError("REFUSE_UNSAFE_PATH")
        if not isinstance(item.get("executable"), bool):
            raise V5ValidationError("REFUSE_UNSAFE_PATH")
        digest = _hash(item.get("sha256"), "PATH")
        if item["type"] == "directory" and digest != EMPTY_SHA256:
            raise V5ValidationError("REFUSE_INVALID_BACKUP" if lineage_type == "INDEPENDENT_BACKUP"
                                    else "REFUSE_INVALID_CANDIDATE")
        if item["type"] == "symlink":
            target = item.get("target")
            if not isinstance(target, str) or not target or target.startswith("/") or ".." in target.split("/"):
                raise V5ValidationError("REFUSE_UNSAFE_PATH")
        elif "target" in item:
            raise V5ValidationError("REFUSE_INVALID_BACKUP" if lineage_type == "INDEPENDENT_BACKUP"
                                    else "REFUSE_INVALID_CANDIDATE")
        normalized.append(dict(item))
    projection = _projection(normalized)
    if manifest["content_root_sha256"] != sha256_value(projection):
        raise V5ValidationError("REFUSE_INVALID_BACKUP" if lineage_type == "INDEPENDENT_BACKUP"
                                else "REFUSE_INVALID_CANDIDATE")
    if manifest["manifest_sha256"] != sha256_value(_manifest_without_hash(manifest)):
        raise V5ValidationError("REFUSE_INVALID_BACKUP" if lineage_type == "INDEPENDENT_BACKUP"
                                else "REFUSE_INVALID_CANDIDATE")
    return dict(manifest, paths=normalized)


def _conflicts(left: dict[str, Any], right: dict[str, Any]) -> list[dict[str, Any]]:
    l = {item["path"]: item for item in left["manifest"]["paths"]}
    r = {item["path"]: item for item in right["manifest"]["paths"]}
    rows: list[dict[str, Any]] = []
    for path in sorted(set(l) | set(r)):
        a, b = l.get(path), r.get(path)
        if a == b:
            continue
        rows.append({
            "path": path,
            "left_candidate_id": left["candidate_id"],
            "left_present": a is not None,
            "left_path_sha256": a.get("sha256") if a else None,
            "left_type": a.get("type") if a else None,
            "left_executable": a.get("executable") if a else None,
            "right_candidate_id": right["candidate_id"],
            "right_present": b is not None,
            "right_path_sha256": b.get("sha256") if b else None,
            "right_type": b.get("type") if b else None,
            "right_executable": b.get("executable") if b else None,
        })
    return rows


def resolve_v5(candidates: Iterable[dict[str, Any]], *, expected_parent: str | None = None) -> dict[str, Any]:
    """Resolve candidates according to the R12 total ordering.

    Candidate envelope: ``{"candidate_id": id, "lineage_type": type,
    "manifest": manifest}``, where type is ``GIT_BASE``, ``CAPTURED_CHILD``,
    or ``INDEPENDENT_BACKUP``.  No filesystem operation occurs.
    """
    raw = list(candidates)
    valid: list[dict[str, Any]] = []
    errors: list[str] = []
    for candidate in raw:
        try:
            if not isinstance(candidate, dict) or set(candidate) != {"candidate_id", "lineage_type", "manifest"}:
                raise V5ValidationError("REFUSE_INVALID_CANDIDATE")
            cid = _id(candidate["candidate_id"], "CANDIDATE")
            lineage = candidate["lineage_type"]
            if lineage not in {"GIT_BASE", "CAPTURED_CHILD", "INDEPENDENT_BACKUP"}:
                raise V5ValidationError("REFUSE_INVALID_CANDIDATE")
            manifest = _validate_manifest(candidate["manifest"], lineage_type=lineage,
                                          expected_parent=expected_parent)
            valid.append({"candidate_id": cid, "lineage_type": lineage, "manifest": manifest})
        except V5ValidationError as exc:
            errors.append(exc.reason)
    precedence = ["REFUSE_UNSAFE_PATH", "REFUSE_INVALID_BACKUP", "REFUSE_INVALID_CANDIDATE", "INVALID_LINEAGE"]
    if errors:
        for reason in precedence:
            if reason in errors:
                return _result("REFUSE" if reason.startswith("REFUSE") else "INVALID", reason, None, valid, [])
    if not valid:
        return _result("REFUSE", "REFUSE_NO_SURVIVING_CANDIDATE", None, [], [])
    pairs = [(a, b) for index, a in enumerate(valid) for b in valid[index + 1:]]
    conflict_rows: list[dict[str, Any]] = []
    for left, right in pairs:
        conflict_rows.extend(_conflicts(left, right))
    if conflict_rows:
        reason = ("REFUSE_INDEPENDENT_PATH_CONFLICT" if any(
            row["left_path_sha256"] == row["right_path_sha256"] and
            (row["left_type"] != row["right_type"] or row["left_executable"] != row["right_executable"])
            for row in conflict_rows) or any(row["left_present"] != row["right_present"] for row in conflict_rows)
            else "REFUSE_INDEPENDENT_CONTENT_CONFLICT")
        return _result("REFUSE", reason, None, valid, conflict_rows)
    selected = min(valid, key=lambda item: item["manifest"]["manifest_sha256"])
    reason = "PROMOTE_EQUIVALENT_CANDIDATES" if len(valid) > 1 else "PROMOTE_SOLE_CANDIDATE"
    return _result("PROMOTE", reason, selected["candidate_id"], valid, [])


def _result(verdict: str, reason: str, selected: str | None,
            valid: list[dict[str, Any]], conflicts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "verdict": verdict,
        "reason_code": reason,
        "selected_candidate_id": selected,
        "candidate_ids": sorted(item["candidate_id"] for item in valid),
        "content_roots": sorted(item["manifest"]["content_root_sha256"] for item in valid),
        "conflict_hashes": sorted(conflicts, key=lambda row: (row["path"], row["left_candidate_id"], row["right_candidate_id"])) or None,
    }
