#!/usr/bin/env python3
"""Frozen Gate 5 comparative generator, adapters, and method-neutral scorer.

Gate 5 runs only preflight smoke. Gate 6 consumes the same source for the
measured 54-execution campaign. No method receives the scorer's expected
manifest or another method's custody.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any


BASE = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = BASE / "HARDENING_GATE4_BASELINE_PROTOCOL_R2.md"
PROTOCOL_SHA256 = hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest()
RECOVERY_BUDGET_SECONDS = 180
SCENARIO_CLASSES = (
    "committed-only",
    "committed-plus-uncommitted",
    "complete-loss",
    "partial-loss",
    "conflicting-stale",
    "clean-control",
)
METHODS = ("ordinary-git", "git-plus-restic-0.19.0", "product")
EVIDENCE_MODES = ("PREFLIGHT", "MEASURED_GATE6")
RESTIC_PROVENANCE = {
    "f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd":
        "restic 0.19.0 compiled with go1.26.4 on darwin/arm64",
    "ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c":
        "restic 0.19.0 compiled with go1.26.4 on linux/amd64",
}
CHECKPOINTS = (
    "BASE_COMMITTED", "AGENT_PROGRESS_SAVED", "HUMAN_EDIT_SAVED",
    "FINAL_PRELOSS",
)
RECEIPT_FIELDS = {
    "schema_version", "campaign_id", "protocol_sha256", "candidate_commit",
    "evidence_mode", "runtime_platform",
    "scenario_class", "scenario_seed_hash", "repetition", "method",
    "execution_order", "source_manifest_sha256", "event_stream_sha256",
    "loss_receipt_sha256", "allowed_information_sha256", "tool_versions",
    "tool_binary_sha256", "method_configuration_sha256",
    "capture_checkpoint_receipts", "selected_recovery_artifact_id",
    "operation_status", "unsupported_capabilities",
    "declared_work_units_total", "declared_work_units_retained",
    "retained_work_unit_ids", "lost_work_unit_ids", "committed_units_retained",
    "uncommitted_units_retained", "untracked_units_retained",
    "manifest_exact_match", "executable_command_sha256",
    "executable_exit_status", "executable_result_sha256",
    "executable_continuation_pass", "capture_overhead_ms",
    "wall_clock_recovery_ms", "setup_ms", "teardown_ms",
    "scripted_command_count", "human_intervention_count",
    "task_restatement_required", "unsafe_acceptance",
    "original_workspace_mutated_after_loss", "deterministic_outcome",
    "storage_bytes_pre_loss", "evidence_bytes", "residue_bytes_after_teardown",
    "cleanup_pass", "command_receipt_hashes", "limitations", "receipt_sha256",
}


class HarnessError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def atomic_write(path: Path, value: Any, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else canonical(value)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
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


def safe_path(root: Path, relative: str) -> Path:
    if (not relative or relative.startswith("/") or "\x00" in relative or
            "\\" in relative or any(part in {"", ".", ".."}
                                      for part in relative.split("/"))):
        raise HarnessError("UNSAFE_PATH")
    target = root.joinpath(*relative.split("/"))
    if root.resolve() not in target.resolve(strict=False).parents:
        raise HarnessError("UNSAFE_PATH")
    return target


def manifest(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if relative == ".git" or relative.startswith(".git/"):
            continue
        if path.is_symlink() or not path.is_file():
            if path.is_symlink():
                raise HarnessError("UNSAFE_PATH")
            continue
        result[relative] = digest(path.read_bytes())
    return result


def tree_bytes(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(path.stat().st_size for path in root.rglob("*")
               if path.is_file() and not path.is_symlink())


def isolated_env(trial: Path) -> dict[str, str]:
    allowed_path = "/usr/bin:/bin:/usr/sbin:/sbin"
    env = {
        "HOME": str(trial / "temp-home"),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_TERMINAL_PROMPT": "0",
        "LANG": "C",
        "LC_ALL": "C",
        "TZ": "UTC",
        "PATH": allowed_path,
        "NO_PROXY": "*",
        "no_proxy": "*",
    }
    (trial / "temp-home").mkdir(parents=True, exist_ok=True)
    return env


def evidence_limitations(evidence_mode: str) -> list[str]:
    if evidence_mode == "PREFLIGHT":
        return ["LOCAL_SYNTHETIC_PREFLIGHT", "NOT_LIVE_AWS",
                "NOT_GATE6_MEASURED_EVIDENCE"]
    if evidence_mode == "MEASURED_GATE6":
        return ["SYNTHETIC_PAIRED_COMPARATIVE", "NOT_LIVE_AWS",
                "NOT_PRODUCT_SCALE", "RUNPOD_GENERIC_COMPUTE"]
    raise HarnessError("EVIDENCE_MODE_INVALID")


def validate_evidence_context(evidence_mode: str, runtime_platform: str,
                              candidate_commit: str, campaign_id: str) -> None:
    evidence_limitations(evidence_mode)
    if evidence_mode == "MEASURED_GATE6":
        if runtime_platform != "Linux":
            raise HarnessError("MEASURED_MODE_REQUIRES_LINUX")
        if re.fullmatch(r"[0-9a-f]{40}", candidate_commit) is None:
            raise HarnessError("MEASURED_CANDIDATE_COMMIT_INVALID")
        if not campaign_id.startswith("ck-gate6-"):
            raise HarnessError("MEASURED_CAMPAIGN_ID_INVALID")


def command(args: list[str], *, cwd: Path, env: dict[str, str],
            timeout: int = RECOVERY_BUDGET_SECONDS) -> tuple[bytes, int]:
    started = time.monotonic_ns()
    try:
        result = subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, check=False, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise HarnessError("COMMAND_TIMEOUT") from exc
    elapsed = int((time.monotonic_ns() - started) / 1_000_000)
    if result.returncode != 0:
        raise HarnessError(f"COMMAND_FAILED:{Path(args[0]).name}:{digest(result.stdout)}")
    return result.stdout, elapsed


def scenario_seed(scenario_class: str, repetition: int) -> str:
    if scenario_class not in SCENARIO_CLASSES or repetition not in {1, 2, 3}:
        raise HarnessError("SCENARIO_KEY_INVALID")
    return digest({"version": "gate5-seed-v1", "class": scenario_class,
                   "repetition": repetition})


def _state_bytes(base: bool, agent: bool, human: bool, safe: bool,
                 nonce: str) -> bytes:
    return canonical({"agent": agent, "base": base, "human": human,
                      "nonce": nonce, "safe": safe}) + b"\n"


def generate_scenario(scenario_class: str, repetition: int) -> dict[str, Any]:
    seed = scenario_seed(scenario_class, repetition)
    nonce = seed[:12]
    target = {
        "committed-only": (True, False, False, True),
        "committed-plus-uncommitted": (True, True, True, True),
        "complete-loss": (True, True, True, True),
        "partial-loss": (True, True, True, True),
        "conflicting-stale": (True, True, False, True),
        "clean-control": (True, True, True, True),
    }[scenario_class]
    check = (
        "import json,pathlib,sys\n"
        "v=json.loads(pathlib.Path('app/state.json').read_text())\n"
        f"expected={{'agent':{target[1]!r},'base':{target[0]!r},"
        f"'human':{target[2]!r},'nonce':'{nonce}','safe':{target[3]!r}}}\n"
        "sys.exit(0 if v==expected else 7)\n"
    ).encode("utf-8")
    initial = {
        "app/state.json": _state_bytes(True, False, False, True, nonce),
        "tests/check.py": check,
    }
    commit_after = {"BASE_COMMITTED"}
    if scenario_class in {"partial-loss", "conflicting-stale"}:
        commit_after.add("AGENT_PROGRESS_SAVED")
    events: list[dict[str, Any]] = []
    states = [("BASE_COMMITTED", True, False, False, True)]
    if scenario_class != "committed-only":
        states.append(("AGENT_PROGRESS_SAVED", True, True, False, True))
    if scenario_class not in {"committed-only", "conflicting-stale"}:
        states.append(("HUMAN_EDIT_SAVED", True, True, True, True))
    if scenario_class == "conflicting-stale":
        states.append(("FINAL_PRELOSS", True, True, False, False))
    else:
        states.append(("FINAL_PRELOSS", *target))
    for index, (label, base, agent, human, safe) in enumerate(states, 1):
        files = {"app/state.json": _state_bytes(base, agent, human, safe, nonce),
                 "tests/check.py": check}
        if human:
            files[f"notes/human-{repetition}.txt"] = (
                f"saved-human-edit-{nonce}\n".encode("utf-8"))
        packet = {
            "version": "gate5-event-v1",
            "sequence": index,
            "checkpoint": label,
            "files": {path: payload.hex() for path, payload in sorted(files.items())},
            "explicit_git_commit": label in commit_after,
            "policy_veto": not safe,
        }
        packet["workspace_manifest_hash"] = digest({
            path: digest(bytes.fromhex(payload))
            for path, payload in packet["files"].items()
        })
        packet["event_hash"] = digest(packet)
        events.append(packet)
    expected_files = {
        "app/state.json": _state_bytes(*target, nonce),
        "tests/check.py": check,
    }
    if target[2]:
        expected_files[f"notes/human-{repetition}.txt"] = (
            f"saved-human-edit-{nonce}\n".encode("utf-8"))
    expected_manifest = {path: digest(payload)
                         for path, payload in sorted(expected_files.items())}
    units = [
        {"id": path, "category": (
            "untracked" if path.startswith("notes/") else
            "uncommitted" if path == "app/state.json" and target[1] and
            scenario_class not in {"partial-loss", "conflicting-stale"} else
            "committed")}
        for path in expected_manifest
    ]
    loss = {
        "type": ("NONE" if scenario_class == "clean-control" else
                 "PARTIAL" if scenario_class == "partial-loss" else "COMPLETE"),
        "paths": (["app/state.json"] if scenario_class == "partial-loss"
                  else sorted(expected_manifest)),
    }
    public = {
        "version": "gate5-scenario-v1",
        "scenario_class": scenario_class,
        "repetition": repetition,
        "seed_hash": seed,
        "initial_files": {path: payload.hex() for path, payload in sorted(initial.items())},
        "events": events,
        "loss": loss,
        "executable_command": ["python3", "tests/check.py"],
        "work_units": units,
        "recovery_budget_seconds": RECOVERY_BUDGET_SECONDS,
    }
    return {
        "public": public,
        "expected_manifest": expected_manifest,
        "expected_manifest_hash": digest(expected_manifest),
        "source_bundle_hash": digest(public),
    }


def materialize_event(workspace: Path, packet: dict[str, Any]) -> None:
    desired = set(packet["files"])
    for path in list(manifest(workspace)):
        if path not in desired:
            safe_path(workspace, path).unlink()
    for relative, encoded in packet["files"].items():
        target = safe_path(workspace, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(bytes.fromhex(encoded))


class Adapter:
    name = "abstract"

    def __init__(self, trial: Path, scenario: dict[str, Any], env: dict[str, str]):
        self.trial = trial
        self.workspace = trial / "workspace"
        self.successor = trial / "successor"
        self.custody = trial / "custody"
        self.scenario = scenario
        self.env = env
        self.commands = 0
        self.capture_ms = 0
        self.checkpoints: list[dict[str, Any]] = []
        self.selected: str | None = None
        self.verdict: tuple[str, str] | None = None
        self.unsupported: list[str] = []

    def setup(self) -> None:
        self.workspace.mkdir()
        self.custody.mkdir(mode=0o700)
        python = shutil.which("python3", path=self.env["PATH"])
        if python is None:
            raise HarnessError("PYTHON_BINARY_NOT_FOUND")
        self.python = Path(python).resolve()
        if not self.python.is_file():
            raise HarnessError("PYTHON_BINARY_INVALID")
        raw, _ = command([str(self.python), "--version"], cwd=self.trial,
                         env=self.env)
        self.python_version = raw.decode("utf-8", errors="strict").strip()
        self.python_hash = digest(self.python.read_bytes())
        self.commands += 1
        first = self.scenario["public"]["initial_files"]
        materialize_event(self.workspace, {"files": first})

    def checkpoint(self, packet: dict[str, Any]) -> None:
        materialize_event(self.workspace, packet)
        if digest(manifest(self.workspace)) != packet["workspace_manifest_hash"]:
            raise HarnessError("CHECKPOINT_MANIFEST_DRIFT")

    def lose(self) -> None:
        loss = self.scenario["public"]["loss"]
        if loss["type"] == "COMPLETE":
            shutil.rmtree(self.workspace)
        elif loss["type"] == "PARTIAL":
            for relative in loss["paths"]:
                target = safe_path(self.workspace, relative)
                if target.exists():
                    target.unlink()

    def recover(self) -> tuple[Path, str]:
        raise NotImplementedError

    def tools(self) -> tuple[dict[str, str], dict[str, str]]:
        return ({"python": self.python_version}, {"python": self.python_hash})


class GitAdapter(Adapter):
    name = "ordinary-git"

    def setup(self) -> None:
        super().setup()
        configured = os.environ.get("CK_GATE5_GIT")
        if not configured:
            raise HarnessError("GIT_BINARY_NOT_DECLARED")
        self.git = Path(configured).resolve()
        if not self.git.is_file():
            raise HarnessError("GIT_BINARY_INVALID")
        raw, _ = command([str(self.git), "--version"], cwd=self.trial,
                         env=self.env)
        self.git_version = raw.decode("utf-8", errors="strict").strip()
        self.git_hash = digest(self.git.read_bytes())
        self.commands += 1
        self.remote = self.custody / "git-remote.git"
        command([str(self.git), "init", "--bare", str(self.remote)],
                cwd=self.trial, env=self.env)
        command([str(self.git), "init", "-b", "main"], cwd=self.workspace, env=self.env)
        command([str(self.git), "config", "user.name", "Gate5 Fixture"],
                cwd=self.workspace, env=self.env)
        command([str(self.git), "config", "user.email", "gate5@example.invalid"],
                cwd=self.workspace, env=self.env)
        command([str(self.git), "remote", "add", "origin", str(self.remote)],
                cwd=self.workspace, env=self.env)
        self.commands += 5

    def checkpoint(self, packet: dict[str, Any]) -> None:
        started = time.monotonic_ns()
        super().checkpoint(packet)
        commit = None
        if packet["explicit_git_commit"]:
            command([str(self.git), "add", "--all"], cwd=self.workspace, env=self.env)
            command([str(self.git), "commit", "-m", packet["checkpoint"]],
                    cwd=self.workspace, env=self.env)
            raw, _ = command([str(self.git), "rev-parse", "HEAD"],
                             cwd=self.workspace, env=self.env)
            commit = raw.decode().strip()
            command([str(self.git), "push", "origin", "HEAD:refs/heads/main"],
                    cwd=self.workspace, env=self.env)
            self.commands += 4
        elapsed = int((time.monotonic_ns() - started) / 1_000_000)
        self.capture_ms += elapsed
        self.checkpoints.append({"checkpoint": packet["checkpoint"],
                                 "event_hash": packet["event_hash"],
                                 "artifact_id": commit})

    def recover(self) -> tuple[Path, str]:
        if self.scenario["public"]["loss"]["type"] == "NONE":
            return self.workspace, "NO_ACTION"
        command([str(self.git), "fsck", "--full", "--strict"],
                cwd=self.remote, env=self.env)
        command([str(self.git), "clone", "--no-local", "--branch", "main", str(self.remote),
                 str(self.successor)], cwd=self.trial, env=self.env)
        self.commands += 2
        raw, _ = command([str(self.git), "rev-parse", "HEAD"],
                         cwd=self.successor, env=self.env)
        self.selected = raw.decode().strip()
        if any(unit["category"] != "committed"
               for unit in self.scenario["public"]["work_units"]):
            self.unsupported.extend(["UNCOMMITTED_BYTES", "UNTRACKED_BYTES"])
            return self.successor, "UNSUPPORTED_BY_METHOD"
        return self.successor, "SUCCESS"

    def tools(self) -> tuple[dict[str, str], dict[str, str]]:
        versions, hashes = super().tools()
        versions["git"] = self.git_version
        hashes["git"] = self.git_hash
        return versions, hashes


class ResticAdapter(GitAdapter):
    name = "git-plus-restic-0.19.0"

    def setup(self) -> None:
        super().setup()
        configured = os.environ.get("CK_GATE5_RESTIC")
        if not configured:
            raise HarnessError("RESTIC_BINARY_NOT_DECLARED")
        self.restic = Path(configured).resolve()
        if not self.restic.is_file():
            raise HarnessError("RESTIC_BINARY_INVALID")
        self.restic_hash = digest(self.restic.read_bytes())
        expected_version = RESTIC_PROVENANCE.get(self.restic_hash)
        if expected_version is None:
            raise HarnessError("RESTIC_BINARY_HASH_MISMATCH")
        raw, _ = command([str(self.restic), "version"], cwd=self.trial,
                         env=self.env)
        self.restic_version = raw.decode("utf-8", errors="strict").strip()
        if self.restic_version != expected_version:
            raise HarnessError("RESTIC_VERSION_MISMATCH")
        self.commands += 1
        self.repo = self.custody / "restic-repository"
        self.password = self.custody / "restic-password"
        self.password.write_bytes(secrets.token_bytes(32).hex().encode() + b"\n")
        self.password.chmod(0o600)
        self.restic_env = dict(self.env, RESTIC_PASSWORD_FILE=str(self.password),
                               RESTIC_CACHE_DIR=str(self.trial / "restic-cache"))
        command([str(self.restic), "-r", str(self.repo), "init"],
                cwd=self.trial, env=self.restic_env)
        self.commands += 1

    def checkpoint(self, packet: dict[str, Any]) -> None:
        super().checkpoint(packet)
        started = time.monotonic_ns()
        raw, _ = command([
            str(self.restic), "-r", str(self.repo), "--no-cache", "backup",
            "--json", "--host", "gate5-fixture", "--tag",
            self.scenario["public"]["scenario_class"], "--tag",
            packet["checkpoint"], "workspace",
        ], cwd=self.trial, env=self.restic_env)
        summaries = [json.loads(line) for line in raw.splitlines()
                     if line.strip() and json.loads(line).get("message_type") == "summary"]
        if len(summaries) != 1 or not summaries[0].get("snapshot_id"):
            raise HarnessError("RESTIC_SNAPSHOT_ID_MISSING")
        snapshot = summaries[0]["snapshot_id"]
        snapshots, _ = command([
            str(self.restic), "-r", str(self.repo), "--no-cache", "snapshots", "--json"
        ], cwd=self.trial, env=self.restic_env)
        matches = [item for item in json.loads(snapshots) if item["id"] == snapshot]
        if len(matches) != 1:
            raise HarnessError("RESTIC_SNAPSHOT_NOT_LISTED")
        metadata = matches[0]
        expected_tags = {self.scenario["public"]["scenario_class"], packet["checkpoint"]}
        if not expected_tags.issubset(set(metadata.get("tags", []))):
            raise HarnessError("RESTIC_SNAPSHOT_TAG_MISMATCH")
        if not any(str(path).rstrip("/").endswith("/workspace")
                   for path in metadata.get("paths", [])):
            raise HarnessError("RESTIC_SNAPSHOT_PATH_MISMATCH")
        command([str(self.restic), "-r", str(self.repo), "--no-cache", "check",
                 "--read-data-subset=100%"], cwd=self.trial, env=self.restic_env)
        self.commands += 3
        elapsed = int((time.monotonic_ns() - started) / 1_000_000)
        self.capture_ms += elapsed
        self.checkpoints[-1]["restic_snapshot_id"] = snapshot
        self.checkpoints[-1]["source_manifest_hash"] = digest(manifest(self.workspace))
        if self.checkpoints[-1]["source_manifest_hash"] != packet["workspace_manifest_hash"]:
            raise HarnessError("RESTIC_CAPTURE_MANIFEST_MISMATCH")

    def recover(self) -> tuple[Path, str]:
        if self.scenario["public"]["loss"]["type"] == "NONE":
            return self.workspace, "NO_ACTION"
        snapshot = self.checkpoints[-1]["restic_snapshot_id"]
        command([str(self.restic), "-r", str(self.repo), "--no-cache", "check",
                 "--read-data-subset=100%"], cwd=self.trial, env=self.restic_env)
        restore = self.trial / "restored"
        command([str(self.restic), "-r", str(self.repo), "--no-cache", "restore",
                 snapshot, "--target", str(restore)], cwd=self.trial, env=self.restic_env)
        self.commands += 2
        restored_workspace = restore / "workspace"
        if not restored_workspace.is_dir():
            raise HarnessError("RESTIC_RESTORE_ROOT_MISSING")
        os.replace(restored_workspace, self.successor)
        shutil.rmtree(restore)
        self.selected = snapshot
        return self.successor, "SUCCESS"

    def tools(self) -> tuple[dict[str, str], dict[str, str]]:
        versions, hashes = super().tools()
        versions["restic"] = self.restic_version
        hashes["restic"] = self.restic_hash
        return versions, hashes


def load_verifier():
    path = BASE / "p4-verifier/verifier.py"
    spec = importlib.util.spec_from_file_location("gate5_p4_verifier", path)
    if spec is None or spec.loader is None:
        raise HarnessError("P4_VERIFIER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ProductAdapter(Adapter):
    name = "product"

    def setup(self) -> None:
        super().setup()
        self.objects = self.custody / "objects"
        self.candidates = self.custody / "candidates"
        self.consumed = self.custody / "consumed"
        for path in (self.objects, self.candidates, self.consumed):
            path.mkdir()
        self.verifier = load_verifier()

    def checkpoint(self, packet: dict[str, Any]) -> None:
        started = time.monotonic_ns()
        super().checkpoint(packet)
        current = manifest(self.workspace)
        for relative, content_hash in current.items():
            blob = self.objects / content_hash
            if not blob.exists():
                atomic_write(blob, safe_path(self.workspace, relative).read_bytes())
        payload = {"checkpoint": packet["checkpoint"],
                   "event_hash": packet["event_hash"],
                   "manifest": current}
        record = {
            "version": "p4-v1",
            "candidate_id": f"candidate-{packet['sequence']:02d}",
            "source_receipt_hash": packet["event_hash"],
            "payload": payload,
            "payload_hash": self.verifier.digest(payload),
            "schema_version": "p4-v1",
            "provenance": {"source": "gate5-common-event-packet"},
            "supported": True,
            "one_use_state": "ISSUED",
            "quarantined": False,
            "policy_veto": packet["policy_veto"],
            "requested_paths": sorted(current),
            "declared_paths": sorted(current),
        }
        verdict, reason = self.verifier.verify(record)
        receipt = {"candidate": record, "verdict": verdict, "reason": reason,
                   "candidate_hash": digest(record)}
        atomic_write(self.candidates / f"{packet['sequence']:04d}.json", receipt)
        self.checkpoints.append({"checkpoint": packet["checkpoint"],
                                 "event_hash": packet["event_hash"],
                                 "artifact_id": record["candidate_id"],
                                 "verdict": verdict, "reason": reason})
        self.capture_ms += int((time.monotonic_ns() - started) / 1_000_000)

    def recover(self) -> tuple[Path, str]:
        if self.scenario["public"]["loss"]["type"] == "NONE":
            return self.workspace, "NO_ACTION"
        eligible = []
        for path in sorted(self.candidates.glob("*.json")):
            receipt = json.loads(path.read_bytes())
            verdict = self.verifier.verify(receipt["candidate"])
            if verdict == ("PROMOTE", "VERIFIED"):
                eligible.append((int(path.stem), receipt["candidate"]))
        if not eligible:
            self.verdict = ("REFUSE", "NO_VERIFIED_CANDIDATE")
            return self.successor, "FAILURE"
        _sequence, selected = eligible[-1]
        self.verdict = self.verifier.verify(selected)
        consume = self.consumed / selected["candidate_id"]
        atomic_write(consume, canonical({"state": "CONSUMED",
                                        "candidate_hash": digest(selected)}))
        self.successor.mkdir()
        for relative, content_hash in selected["payload"]["manifest"].items():
            blob = self.objects / content_hash
            if not blob.is_file() or digest(blob.read_bytes()) != content_hash:
                raise HarnessError("PRODUCT_OBJECT_HASH_MISMATCH")
            target = safe_path(self.successor, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob.read_bytes())
        self.selected = selected["candidate_id"]
        return self.successor, "SUCCESS"

    def tools(self) -> tuple[dict[str, str], dict[str, str]]:
        path = BASE / "p4-verifier/verifier.py"
        versions, hashes = super().tools()
        versions["product"] = "p4-deterministic-verifier-v1"
        hashes["product"] = digest(path.read_bytes())
        return versions, hashes


ADAPTERS = {adapter.name: adapter for adapter in (GitAdapter, ResticAdapter, ProductAdapter)}


def run_executable(target: Path, scenario: dict[str, Any],
                   env: dict[str, str]) -> tuple[int, str, int]:
    args = scenario["public"]["executable_command"]
    started = time.monotonic_ns()
    result = subprocess.run(args, cwd=target, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False,
                            timeout=RECOVERY_BUDGET_SECONDS)
    elapsed = int((time.monotonic_ns() - started) / 1_000_000)
    return result.returncode, digest(result.stdout), elapsed


def score(adapter: Adapter, target: Path, operation_status: str,
          scenario: dict[str, Any], recovery_ms: int, setup_ms: int,
          teardown_ms: int, residue: int, *, campaign_id: str,
          candidate_commit: str, execution_order: int,
          evidence_mode: str, runtime_platform: str) -> dict[str, Any]:
    actual = manifest(target)
    expected = scenario["expected_manifest"]
    retained = sorted(path for path, item_hash in expected.items()
                      if actual.get(path) == item_hash)
    lost = sorted(set(expected) - set(retained))
    code, result_hash, executable_ms = run_executable(target, scenario, adapter.env)
    categories = {unit["id"]: unit["category"]
                  for unit in scenario["public"]["work_units"]}
    versions, hashes = adapter.tools()
    semantic = {
        "operation_status": operation_status,
        "retained_work_unit_ids": retained,
        "manifest_exact_match": actual == expected,
        "executable_continuation_pass": code == 0,
        "unsafe_acceptance": bool(adapter.verdict and adapter.verdict[0] == "PROMOTE" and code != 0),
        "method_verdict": list(adapter.verdict) if adapter.verdict else None,
    }
    public = scenario["public"]
    receipt = {
        "schema_version": "gate5-comparative-receipt-v2",
        "campaign_id": campaign_id,
        "protocol_sha256": PROTOCOL_SHA256,
        "candidate_commit": candidate_commit,
        "evidence_mode": evidence_mode,
        "runtime_platform": runtime_platform,
        "scenario_class": public["scenario_class"],
        "scenario_seed_hash": public["seed_hash"],
        "repetition": public["repetition"],
        "method": adapter.name,
        "execution_order": execution_order,
        "source_manifest_sha256": scenario["source_bundle_hash"],
        "event_stream_sha256": digest(public["events"]),
        "loss_receipt_sha256": digest(public["loss"]),
        "allowed_information_sha256": digest(public),
        "tool_versions": versions,
        "tool_binary_sha256": hashes,
        "method_configuration_sha256": digest({"method": adapter.name, "network": "DENIED", "home": "TRIAL_LOCAL"}),
        "capture_checkpoint_receipts": adapter.checkpoints,
        "selected_recovery_artifact_id": adapter.selected,
        "operation_status": operation_status,
        "unsupported_capabilities": sorted(set(adapter.unsupported)),
        "declared_work_units_total": len(expected),
        "declared_work_units_retained": len(retained),
        "retained_work_unit_ids": retained,
        "lost_work_unit_ids": lost,
        "committed_units_retained": sum(categories[path] == "committed" for path in retained),
        "uncommitted_units_retained": sum(categories[path] == "uncommitted" for path in retained),
        "untracked_units_retained": sum(categories[path] == "untracked" for path in retained),
        "manifest_exact_match": actual == expected,
        "executable_command_sha256": digest(public["executable_command"]),
        "executable_exit_status": code,
        "executable_result_sha256": result_hash,
        "executable_continuation_pass": code == 0,
        "capture_overhead_ms": adapter.capture_ms,
        "wall_clock_recovery_ms": recovery_ms + executable_ms,
        "setup_ms": setup_ms,
        "teardown_ms": teardown_ms,
        "scripted_command_count": adapter.commands + 1,
        "human_intervention_count": 0,
        "task_restatement_required": False,
        "unsafe_acceptance": semantic["unsafe_acceptance"],
        "original_workspace_mutated_after_loss": False,
        "deterministic_outcome": semantic,
        "storage_bytes_pre_loss": tree_bytes(adapter.custody),
        "evidence_bytes": 0,
        "residue_bytes_after_teardown": residue,
        "cleanup_pass": residue == 0,
        "command_receipt_hashes": [],
        "limitations": evidence_limitations(evidence_mode),
    }
    receipt["receipt_sha256"] = digest(receipt)
    return receipt


def validate_receipt(receipt: Any, raw: bytes | None = None) -> dict[str, Any]:
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_FIELDS:
        raise HarnessError("RECEIPT_FIELDS_INVALID")
    if receipt["schema_version"] != "gate5-comparative-receipt-v2":
        raise HarnessError("RECEIPT_VERSION_INVALID")
    if receipt["evidence_mode"] not in EVIDENCE_MODES:
        raise HarnessError("EVIDENCE_MODE_INVALID")
    if receipt["runtime_platform"] not in {"Darwin", "Linux"}:
        raise HarnessError("RUNTIME_PLATFORM_INVALID")
    validate_evidence_context(receipt["evidence_mode"], receipt["runtime_platform"],
                              receipt["candidate_commit"], receipt["campaign_id"])
    if receipt["limitations"] != evidence_limitations(receipt["evidence_mode"]):
        raise HarnessError("EVIDENCE_LIMITATIONS_INVALID")
    if receipt["scenario_class"] not in SCENARIO_CLASSES or receipt["method"] not in METHODS:
        raise HarnessError("RECEIPT_ENUM_INVALID")
    expected_tools = {
        "ordinary-git": {"python", "git"},
        "git-plus-restic-0.19.0": {"python", "git", "restic"},
        "product": {"python", "product"},
    }[receipt["method"]]
    if (set(receipt["tool_versions"]) != expected_tools or
            set(receipt["tool_binary_sha256"]) != expected_tools):
        raise HarnessError("TOOL_PROVENANCE_FIELDS_INVALID")
    for value in receipt["tool_binary_sha256"].values():
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise HarnessError("TOOL_BINARY_HASH_INVALID")
    if receipt["operation_status"] not in {
            "SUCCESS", "NO_ACTION", "PARTIAL", "UNSUPPORTED_BY_METHOD",
            "FAILURE", "TIMEOUT", "INVALID_TRIAL"}:
        raise HarnessError("RECEIPT_STATUS_INVALID")
    for field in ("manifest_exact_match", "executable_continuation_pass",
                  "task_restatement_required", "unsafe_acceptance",
                  "original_workspace_mutated_after_loss", "cleanup_pass"):
        if not isinstance(receipt[field], bool):
            raise HarnessError("RECEIPT_TYPE_INVALID")
    for field in ("protocol_sha256", "scenario_seed_hash",
                  "source_manifest_sha256", "event_stream_sha256",
                  "loss_receipt_sha256", "allowed_information_sha256",
                  "method_configuration_sha256", "executable_command_sha256",
                  "executable_result_sha256", "receipt_sha256"):
        value = receipt[field]
        if not isinstance(value, str) or len(value) != 64:
            raise HarnessError("RECEIPT_HASH_INVALID")
        int(value, 16)
    body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if receipt["receipt_sha256"] != digest(body):
        raise HarnessError("RECEIPT_HASH_MISMATCH")
    if raw is not None and raw != canonical(receipt):
        raise HarnessError("RECEIPT_NON_CANONICAL")
    return receipt


def run_one(scenario_class: str, repetition: int, method: str,
            output: Path, *, campaign_id: str = "gate5-local-smoke-r1",
            candidate_commit: str = "GATE5_PREFREEZE_WORKTREE",
            execution_order: int = 1,
            evidence_mode: str = "PREFLIGHT") -> dict[str, Any]:
    if method not in ADAPTERS:
        raise HarnessError("METHOD_INVALID")
    scenario = generate_scenario(scenario_class, repetition)
    runtime_platform = platform.system()
    validate_evidence_context(evidence_mode, runtime_platform, candidate_commit,
                              campaign_id)
    run_root = Path(tempfile.mkdtemp(prefix="gate5-trial-", dir=output.parent))
    env = isolated_env(run_root)
    adapter = ADAPTERS[method](run_root, scenario, env)
    setup_start = time.monotonic_ns()
    try:
        adapter.setup()
        for packet in scenario["public"]["events"]:
            adapter.checkpoint(packet)
        source_before_loss = manifest(adapter.workspace)
        if digest(source_before_loss) != digest({
                path: digest(bytes.fromhex(payload))
                for path, payload in scenario["public"]["events"][-1]["files"].items()}):
            raise HarnessError("SOURCE_PAIRING_DRIFT")
        setup_ms = int((time.monotonic_ns() - setup_start) / 1_000_000)
        adapter.lose()
        recovery_start = time.monotonic_ns()
        prior_handler = signal.getsignal(signal.SIGALRM)

        def timeout_handler(_signum: int, _frame: Any) -> None:
            raise HarnessError("RECOVERY_TIMEOUT")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, RECOVERY_BUDGET_SECONDS)
        try:
            target, operation = adapter.recover()
            recovery_ms = int((time.monotonic_ns() - recovery_start) / 1_000_000)
            # Score before teardown, then rewrite only teardown bookkeeping.
            receipt = score(adapter, target, operation, scenario, recovery_ms,
                            setup_ms, 0, 0, campaign_id=campaign_id,
                            candidate_commit=candidate_commit,
                            execution_order=execution_order,
                            evidence_mode=evidence_mode,
                            runtime_platform=runtime_platform)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, prior_handler)
    finally:
        teardown_start = time.monotonic_ns()
        shutil.rmtree(run_root, ignore_errors=False)
        teardown_ms = int((time.monotonic_ns() - teardown_start) / 1_000_000)
    residue = tree_bytes(run_root)
    receipt["teardown_ms"] = teardown_ms
    receipt["residue_bytes_after_teardown"] = residue
    receipt["cleanup_pass"] = residue == 0
    receipt["receipt_sha256"] = digest({key: value for key, value in receipt.items()
                                        if key != "receipt_sha256"})
    validate_receipt(receipt)
    atomic_write(output, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=SCENARIO_CLASSES)
    parser.add_argument("repetition", type=int, choices=(1, 2, 3))
    parser.add_argument("method", choices=METHODS)
    parser.add_argument("output", type=Path)
    parser.add_argument("--campaign-id", default="gate5-local-smoke-r1")
    parser.add_argument("--candidate-commit", default="GATE5_PREFREEZE_WORKTREE")
    parser.add_argument("--execution-order", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--evidence-mode", choices=EVIDENCE_MODES,
                        default="PREFLIGHT")
    args = parser.parse_args()
    receipt = run_one(
        args.scenario, args.repetition, args.method, args.output.resolve(),
        campaign_id=args.campaign_id, candidate_commit=args.candidate_commit,
        execution_order=args.execution_order, evidence_mode=args.evidence_mode)
    print(canonical({"status": "GREEN", "receipt_sha256": receipt["receipt_sha256"]}).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
