#!/usr/bin/env python3
"""Materialize and execute deterministic public-surface Gate 7 scenarios.

This runner-side module contains no expected verdicts and imports no oracle or
generator contract. It consumes only one hash-bound case input.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import multiprocessing
import os
from pathlib import Path
import sys
from typing import Any


BASE = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path, *, package_paths: list[str] | None = None):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
        submodule_search_locations=package_paths,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("MODULE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


try:
    from p7_runtime import records as p7
    from cockroach_kernel import recovery_surface as surface
except ModuleNotFoundError:
    package_root = BASE / "p7-recovery"
    _load("p7_runtime", package_root / "__init__.py", package_paths=[str(package_root)])
    p7 = _load("p7_runtime.records", package_root / "records.py")
    _load("p7_runtime.fresh_context", package_root / "fresh_context.py")
    surface = _load(
        "cockroach_kernel.recovery_surface",
        BASE / "cockroach_kernel" / "recovery_surface.py",
    )


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: bytes | Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def deterministic_bytes(seed: bytes, label: str, size: int) -> bytes:
    if size < 0:
        raise ValueError("NEGATIVE_SIZE")
    output = bytearray()
    counter = 0
    while len(output) < size:
        output.extend(hashlib.sha256(
            seed + label.encode("utf-8") + counter.to_bytes(8, "big")
        ).digest())
        counter += 1
    return bytes(output[:size])


def tree(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = {"kind": "symlink", "target": os.readlink(path)}
        elif path.is_file():
            raw = path.read_bytes()
            result[relative] = {"kind": "file", "bytes": len(raw), "sha256": digest(raw)}
        elif path.is_dir():
            result[relative] = {"kind": "directory"}
        else:
            result[relative] = {"kind": "special"}
    return result


def _base_files(topology: str, seed: bytes) -> dict[str, bytes]:
    marker = seed.hex()[:16]
    if topology == "T1_SMALL_SINGLE_PACKAGE" or topology == "NONE":
        return {
            "README.md": f"small {marker}\n".encode(),
            "src/feature.py": f"def recovered():\n    return {marker!r}\n".encode(),
            "state/uncommitted.txt": f"work {marker}\n".encode(),
        }
    if topology == "T2_MEDIUM_SERVICE":
        files = {
            "src/feature.py": f"def recovered():\n    return {marker!r}\n".encode(),
            "migrations/001.sql": f"-- migration {marker}\n".encode(),
            "config/service.json": canonical({"marker": marker, "version": 1}),
            "fixtures/input.json": canonical({"records": [marker, "held-out"]}),
        }
        for index in range(20):
            files[f"src/module_{index:02d}.py"] = (
                f"VALUE_{index} = {marker!r}\n".encode()
            )
        return files
    if topology == "T3_MONOREPO":
        files = {
            "src/feature.py": f"def recovered():\n    return {marker!r}\n".encode(),
            "workspace.json": canonical({"packages": ["api", "core", "db", "web"]}),
        }
        for package in ("api", "core", "db", "web"):
            files[f"packages/{package}/index.py"] = (
                f"PACKAGE = {package!r}\nMARKER = {marker!r}\n".encode()
            )
            files[f"packages/{package}/contract.json"] = canonical(
                {"package": package, "depends_on": "core" if package != "core" else None}
            )
        return files
    if topology == "T4_MIXED_LANGUAGE":
        return {
            "src/feature.py": f"def recovered():\n    return {marker!r}\n".encode(),
            "web/feature.ts": f"export const marker = '{marker}';\n".encode(),
            "db/001.sql": f"-- {marker}\nSELECT 1;\n".encode(),
            "config/feature.json": canonical({"marker": marker, "enabled": True}),
            "docs/contract.md": f"# Mixed contract\n\n{marker}\n".encode(),
            "state/uncommitted.txt": f"mixed work {marker}\n".encode(),
        }
    raise ValueError("TOPOLOGY_UNSUPPORTED")


class Scenario:
    def __init__(self, root: Path, case: dict[str, Any]) -> None:
        self.root = root
        self.case = case
        self.seed = bytes.fromhex(case["case_seed_hex"])
        self.operation, _, self.operation_value = case["operation"].partition(":")
        self.workspace = root / "workspace"
        self.representations = root / "representations"
        self.custody = root / "custody"
        self.output = root / "output"
        for item in (self.workspace, self.representations, self.custody, self.output):
            item.mkdir(parents=True)
        self.request_path = root / "request.json"
        self.files = _base_files(case["topology"], self.seed)
        self.test_path = "src/feature.py"
        self._apply_size_shape()
        self.lost_paths = sorted(self.files)
        if self.operation == "partial-promote" or self.operation == "replay-partial":
            self.lost_paths = sorted(
                path for path in self.files if path == self.test_path or path.endswith("uncommitted.txt")
            )
            if len(self.lost_paths) == 1:
                self.lost_paths.append(sorted(path for path in self.files if path != self.test_path)[0])
            self.lost_paths.sort()
        self.ids = self._ids()
        self.manifest = self._manifest()
        self.trajectory = self._trajectory()
        self.context = self._context()
        self.candidates = self._candidates()
        self.decision = p7.select_candidate(self.candidates, self.context) if self._context_valid() else None
        self.warrant = self._warrant()
        self.loss_receipt = self._loss_receipt()
        self.request = self._request()
        self._write_request()
        self._write_representations()
        self._write_surviving_workspace()

    def _ids(self) -> dict[str, str]:
        suffix = digest(self.seed)[:16]
        return {
            "task": f"g7-task-{suffix}",
            "manifest": f"g7-manifest-{suffix}",
            "trajectory": f"g7-trajectory-{suffix}",
            "request": f"g7-request-{suffix}",
            "loss": f"g7-loss-{suffix}",
            "warrant": f"g7-warrant-{suffix}",
        }

    def _apply_size_shape(self) -> None:
        if self.operation == "file-boundary":
            size = int(self.operation_value)
            self.files = {self.test_path: deterministic_bytes(self.seed, self.test_path, size)}
        elif self.operation in {"aggregate-boundary", "oversized-aggregate"}:
            total = int(self.operation_value) if self.operation_value else surface.MAX_AGGREGATE_BYTES + 1
            files: dict[str, bytes] = {}
            remaining = total
            index = 0
            while remaining:
                size = min(surface.MAX_FILE_BYTES, remaining)
                path = self.test_path if index == 0 else f"chunks/part-{index:03d}.bin"
                files[path] = deterministic_bytes(self.seed, path, size)
                remaining -= size
                index += 1
            self.files = files
        elif self.operation == "near-boundary-stale-decoy":
            total = surface.MAX_AGGREGATE_BYTES - 65_536
            files = {}
            remaining = total
            index = 0
            while remaining:
                size = min(surface.MAX_FILE_BYTES, remaining)
                path = self.test_path if index == 0 else f"near/part-{index:03d}.bin"
                files[path] = deterministic_bytes(self.seed, path, size)
                remaining -= size
                index += 1
            self.files = files

    def _manifest(self) -> dict[str, Any]:
        return {
            "version": p7.VERSION,
            "manifest_id": self.ids["manifest"],
            "task_id": self.ids["task"],
            "files": [
                {
                    "path": path,
                    "content_hash": digest(raw),
                    "executable": False,
                    "is_symlink": False,
                }
                for path, raw in sorted(self.files.items())
            ],
        }

    def _trajectory(self) -> dict[str, Any]:
        labels = ("committed", "tracked-uncommitted", "untracked", "human-saved", "captured")
        events = [
            {
                "sequence": index,
                "event": label,
                "event_hash": digest(self.seed + label.encode("utf-8")),
            }
            for index, label in enumerate(labels)
        ]
        if self.operation == "out-of-order":
            events[1]["sequence"], events[2]["sequence"] = 2, 1
        previous = ""
        for event in events:
            previous = p7.sha256_hex({"previous": previous, "event": event})
        return {
            "version": p7.VERSION,
            "receipt_id": self.ids["trajectory"],
            "task_id": self.ids["task"],
            "manifest_hash": p7.sha256_hex(self.manifest),
            "events": events,
            "trajectory_hash": previous,
        }

    def _context(self) -> dict[str, Any]:
        quorum = {"decision": "PROMOTE"}
        return {
            "manifest": self.manifest,
            "trajectory_receipt": self.trajectory,
            "policy_version": "policy-g7-r2",
            "quorum_decision_hash": p7.sha256_hex(quorum),
        }

    def _context_valid(self) -> bool:
        try:
            p7.validate_context(self.context)
            return True
        except p7.RecoveryError:
            return False

    def _candidate(
        self,
        label: str,
        *,
        prefix: int | None = None,
        stale: bool = False,
        veto: bool = False,
        tampered: bool = False,
        unsupported: bool = False,
        test_passed: bool = True,
    ) -> dict[str, Any]:
        events = self.trajectory["events"]
        prefix_length = len(events) if prefix is None else prefix
        return {
            "version": "p7-v2" if unsupported else p7.VERSION,
            "candidate_id": f"g7-{label}-{digest(self.seed + label.encode())[:12]}",
            "task_id": self.ids["task"],
            "provenance": {"source": "synthetic-gate7-r2"},
            "source_receipt_hash": (
                "f" * 64 if tampered else p7.sha256_hex(self.trajectory)
            ),
            "policy_version": "policy-stale" if stale else self.context["policy_version"],
            "policy_veto": veto,
            "tampered": tampered,
            "quorum_decision": {"decision": "PROMOTE"},
            "prefix_length": prefix_length,
            "integrity_hash": p7.trajectory_integrity_hash(events, prefix_length),
            "declared_paths": sorted(self.files),
            "file_hashes": {path: digest(raw) for path, raw in sorted(self.files.items())},
            "executable_test": {
                "test_id": f"g7-test-{digest(self.seed)[:12]}",
                "path": self.test_path,
                "feature_hash": digest(self.files[self.test_path]),
                "passed": test_passed,
            },
        }

    def _candidates(self) -> list[dict[str, Any]]:
        op = self.operation
        if op == "missing-history":
            return []
        if op == "stale":
            return [self._candidate("stale", stale=True)]
        if op == "conflict-safe":
            return [
                self._candidate("stale-strong", stale=True),
                self._candidate("safe-weak", prefix=3),
            ]
        if op == "conflict-no-safe":
            return [self._candidate("veto-a", veto=True), self._candidate("stale-b", stale=True)]
        if op == "tampered-stale":
            return [self._candidate("tampered-stale", stale=True, tampered=True)]
        if op == "veto-strong-valid-weak":
            return [self._candidate("veto-strong", veto=True), self._candidate("safe-weak", prefix=3)]
        if op == "unsupported-missing":
            return [self._candidate("unsupported", unsupported=True)]
        if op in {"near-boundary-stale-decoy", "delayed-stale"}:
            return [self._candidate("stale-newer", stale=True), self._candidate("safe", prefix=3)]
        return [self._candidate("primary")]

    def _warrant(self) -> dict[str, Any] | None:
        if not self._context_valid() or self.decision is None or self.decision["decision"] != "PROMOTE":
            return None
        return p7.make_warrant(
            self.ids["warrant"],
            self.ids["task"],
            self.decision["candidate_id"],
            self.decision,
        )

    def _loss_receipt(self) -> dict[str, Any]:
        return {
            "version": p7.VERSION,
            "receipt_id": self.ids["loss"],
            "task_id": self.ids["task"],
            "manifest_hash": p7.sha256_hex(self.manifest),
            "lost_paths": self.lost_paths,
            "absence_hash": p7.sha256_hex(
                {"lost_paths": self.lost_paths, "observed": "absent"}
            ),
        }

    def _request(self) -> dict[str, Any]:
        return {
            "version": surface.REQUEST_VERSION,
            "request_id": self.ids["request"],
            "context": self.context,
            "loss_receipt": self.loss_receipt,
            "candidates": self.candidates,
            "warrant": self.warrant,
        }

    def _write_request(self) -> None:
        if self.operation == "raw-oversized-malformed":
            self.request_path.write_bytes(b"{" + b"x" * surface.MAX_RECORD_BYTES)
            return
        self.request_path.write_bytes(surface.canonical_json(self.request))

    def _selected_candidate(self) -> dict[str, Any] | None:
        if self.decision is None or self.decision["decision"] != "PROMOTE":
            return None
        return next(
            candidate for candidate in self.candidates
            if candidate["candidate_id"] == self.decision["candidate_id"]
        )

    def _write_representations(self) -> None:
        for candidate in self.candidates:
            candidate_root = self.representations / candidate["candidate_id"]
            for path, raw in self.files.items():
                if self.operation == "missing-test" and path == self.test_path:
                    continue
                target = candidate_root.joinpath(*path.split("/"))
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)

    def _write_surviving_workspace(self) -> None:
        for path, raw in self.files.items():
            if path in self.lost_paths:
                continue
            target = self.workspace.joinpath(*path.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)

    def kwargs(self, output: Path | None = None) -> dict[str, Any]:
        return {
            "request_path": self.request_path,
            "sandbox_root": self.root,
            "workspace": self.workspace,
            "representation_root": self.representations,
            "custody_root": self.custody,
            "output_root": output or self.output,
        }

    def new_output(self, label: str) -> Path:
        output = self.root / label
        output.mkdir()
        return output

    def expected_workspace(self) -> dict[str, str]:
        return {path: digest(raw) for path, raw in sorted(self.files.items())}


def normalize_call(scenario: Scenario, *, output: Path | None = None, fault: str | None = None) -> dict[str, Any]:
    try:
        status, summary = surface.execute_recovery(**scenario.kwargs(output), fault=fault)
        return {"exit": status, "summary": summary}
    except surface.SurfaceError as exc:
        return {
            "exit": exc.exit_code,
            "summary": {
                "version": "ck-recovery-error-v1",
                "verdict": exc.verdict,
                "reason": exc.reason,
                "action_taken": exc.action_taken,
            },
        }
    except (OSError, p7.RecoveryError, RuntimeError) as exc:
        return {
            "exit": 2,
            "summary": {
                "version": "ck-recovery-error-v1",
                "verdict": "INVALID",
                "reason": str(exc) or "DEPENDENCY_UNAVAILABLE",
                "action_taken": "NONE",
            },
        }


def _concurrent_child(scenario: Scenario, output: Path, result_path: Path) -> None:
    result = normalize_call(scenario, output=output)
    result_path.write_bytes(canonical(result))


def _run_concurrent(scenario: Scenario) -> tuple[dict[str, Any], dict[str, Any]]:
    outputs = [scenario.output, scenario.new_output("output-peer")]
    result_paths = [scenario.root / "peer-a.json", scenario.root / "peer-b.json"]
    context = multiprocessing.get_context("fork")
    processes = [
        context.Process(target=_concurrent_child, args=(scenario, output, result_path))
        for output, result_path in zip(outputs, result_paths)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(30)
        if process.exitcode != 0:
            raise RuntimeError("CONCURRENT_CHILD_FAILED")
    results = [json.loads(path.read_bytes()) for path in result_paths]
    promotions = [result for result in results if result["summary"]["verdict"] == "PROMOTE"]
    refusals = [result for result in results if result["summary"]["verdict"] == "REFUSE"]
    if len(promotions) != 1 or len(refusals) != 1:
        raise RuntimeError("CONCURRENT_SINGLE_CONSUMER_INVARIANT_FAILED")
    return promotions[0], refusals[0]


def execute_surface_case(root: Path, case: dict[str, Any]) -> dict[str, Any]:
    scenario = Scenario(root, case)
    workspace_initial = tree(scenario.workspace)
    representation_initial = tree(scenario.representations)
    custody_initial = tree(scenario.custody)
    operation = scenario.operation
    history: list[dict[str, Any]] = []
    terminal_before = workspace_initial
    authorized_prior_mutation = False

    if operation in {"replay-partial", "receipt-restart", "duplicate-delivery"}:
        first = normalize_call(scenario)
        history.append(first)
        if first["summary"]["verdict"] != "PROMOTE":
            raise RuntimeError("PRIOR_PROMOTION_FAILED")
        authorized_prior_mutation = True
        terminal_before = tree(scenario.workspace)
        terminal = normalize_call(scenario, output=scenario.new_output("output-replay"))
    elif operation in {"fault-after-consume", "interrupt-duplicate"}:
        interrupted = normalize_call(scenario, fault="after-consume")
        history.append(interrupted)
        if interrupted["summary"]["reason"] != "PROMOTION_INTERRUPTED":
            raise RuntimeError("INTERRUPTION_NOT_OBSERVED")
        terminal_before = tree(scenario.workspace)
        terminal = normalize_call(scenario, output=scenario.new_output("output-replay"))
    elif operation == "concurrent-claim":
        promotion, terminal = _run_concurrent(scenario)
        history.append(promotion)
        authorized_prior_mutation = True
        terminal_before = tree(scenario.workspace)
    else:
        terminal = normalize_call(scenario)

    workspace_final = tree(scenario.workspace)
    representation_final = tree(scenario.representations)
    custody_final = tree(scenario.custody)
    summary = terminal["summary"]
    expected_workspace = scenario.expected_workspace()
    actual_workspace_files = {
        path: value["sha256"]
        for path, value in workspace_final.items() if value["kind"] == "file"
    }
    # Internal stage files are forbidden residue and are deliberately retained in
    # this comparison if present.
    manifest_match = actual_workspace_files == expected_workspace
    test_hash = actual_workspace_files.get(scenario.test_path)
    acceptance_passed = test_hash == digest(scenario.files[scenario.test_path])
    terminal_mutated = workspace_final != terminal_before
    return {
        "observed_exit": terminal["exit"],
        "observed_verdict": summary.get("verdict"),
        "observed_reason": summary.get("reason"),
        "action_taken": summary.get("action_taken", "NONE"),
        "summary_sha256": digest(summary),
        "workspace_initial_sha256": digest(workspace_initial),
        "workspace_final_sha256": digest(workspace_final),
        "representation_sha256": digest(representation_final),
        "representations_unchanged": representation_initial == representation_final,
        "custody_initial_sha256": digest(custody_initial),
        "custody_final_sha256": digest(custody_final),
        "terminal_invocation_mutated": terminal_mutated,
        "authorized_prior_mutation": authorized_prior_mutation,
        "manifest_exact_match": manifest_match,
        "acceptance_passed": acceptance_passed,
        "manifest_file_count": len(scenario.files),
        "manifest_bytes": sum(len(raw) for raw in scenario.files.values()),
        "lost_path_count": len(scenario.lost_paths),
        "history": history,
    }
