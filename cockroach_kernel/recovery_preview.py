"""Read-only, deterministic recovery preview.

The preview explains the projected outcome and evidence before any warrant is
consumed or workspace mutation occurs. It deliberately shares the recovery
surface validators and never writes files, opens a connection, or invokes a
model.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from p7_runtime import records as p7

from .continuation_brief import canonical_json, digest
from . import recovery_surface as surface


PREVIEW_VERSION = "ck-recovery-preview-v1"


def preview_recovery(
    *,
    request_path: str | Path,
    sandbox_root: str | Path,
    workspace: str | Path,
    representation_root: str | Path,
    custody_root: str | Path,
    output_root: str | Path,
) -> dict[str, Any]:
    """Return a hash-bound projection without consuming custody or mutating roots."""
    roots = surface.validate_roots(
        request_path, sandbox_root, workspace, representation_root, custody_root, output_root
    )
    request, raw_request = surface._load_request(roots.request)
    request = surface._validate_request(request)
    request_hash = p7.sha256_hex(raw_request)
    manifest = request["context"]["manifest"]
    body: dict[str, Any] = {
        "version": PREVIEW_VERSION,
        "request_hash": request_hash,
        "task_id": manifest["task_id"],
        "no_side_effects": True,
        "warrant_consumed": False,
        "workspace_mutated": False,
        "evidence_basis": {
            "manifest_hash": p7.sha256_hex(manifest),
            "trajectory_hash": request["context"]["trajectory_receipt"]["trajectory_hash"],
        },
    }
    if request["loss_receipt"] is None:
        body.update({
            "projected_verdict": "NO_ACTION",
            "reason": "NO_DECLARED_LOSS",
            "candidate_id": None,
            "surviving_paths": [],
            "unavailable_paths": [],
            "path_status": [],
        })
        return dict(body, preview_hash=digest(body))

    decision = p7.select_candidate(request["candidates"], request["context"])
    body["decision_hash"] = p7.sha256_hex(decision)
    body["projected_verdict"] = "PROMOTE" if decision["decision"] == "PROMOTE" else "REFUSE"
    body["reason"] = decision["reason"]
    body["candidate_id"] = decision.get("candidate_id")
    if decision["decision"] != "PROMOTE":
        body.update({"surviving_paths": [], "unavailable_paths": [], "path_status": []})
        return dict(body, preview_hash=digest(body))

    candidate = next(item for item in request["candidates"] if item["candidate_id"] == decision["candidate_id"])
    lost = set(request["loss_receipt"]["lost_paths"])
    surviving: list[str] = []
    unavailable: list[str] = []
    path_status: list[dict[str, str]] = []
    candidate_base = roots.representation / candidate["candidate_id"]
    for relative in sorted(lost & set(candidate["declared_paths"])):
        path = surface._safe_relative_file(candidate_base, relative)
        if path is None:
            unavailable.append(relative)
            path_status.append({"path": relative, "status": "MISSING_REPRESENTATION"})
            continue
        raw = surface._read_representation(path)
        if p7.sha256_hex(raw) != candidate["file_hashes"][relative]:
            unavailable.append(relative)
            path_status.append({"path": relative, "status": "HASH_MISMATCH"})
            continue
        target, exists = surface._safe_workspace_target(roots.workspace, relative)
        if exists:
            unavailable.append(relative)
            path_status.append({"path": relative, "status": "WORKSPACE_CONFLICT"})
            continue
        surviving.append(relative)
        path_status.append({"path": relative, "status": "VERIFIED_SURVIVOR"})
    body.update({
        "surviving_paths": surviving,
        "unavailable_paths": unavailable,
        "path_status": path_status,
        "preservation_proof_pending": True,
        "execution_required_for_final_verdict": True,
    })
    return dict(body, preview_hash=digest(body))
