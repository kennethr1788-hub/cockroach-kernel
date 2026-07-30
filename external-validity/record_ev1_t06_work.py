#!/usr/bin/env python3
"""Verify and freeze EV1-T06 task work before capture."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / ".ev1-runtime" / "EV1-T06"
CONTROL = CAMPAIGN / "control"
WORKSPACE = CAMPAIGN / "workspace"
PREPARATION = CONTROL / "PREPARATION_RECEIPT.json"
WORK_RECEIPT = CONTROL / "WORK_RECEIPT.json"
PREPARATION_FILE_SHA256 = "01b4f7b60ee02ce518b3f2df5f00f3b186b43f9d97c5702305a9c8b1cd1b1a4a"
PREPARATION_RECEIPT_SHA256 = "1a5caffc5e89e5cc3a1f4ef6583ae408e13b10387fcabed6f3e7edf4c0bfd3bb"
TASK_COMMIT = "a3e5cd8f7dda19dd04df5904b5671f955a5c7adb"
DECLARED = ("lib/ranking.ts", "lib/signals.ts", "package.json", "scripts/run-stable-ranking.mjs", "scripts/stable-ranking-cases.cjs")
PRIVATE = re.compile(rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY")


class WorkError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: bytes | Path | Any) -> str:
    raw = value.read_bytes() if isinstance(value, Path) else value if isinstance(value, bytes) else canonical(value)
    return hashlib.sha256(raw).hexdigest()


def atomic_write(path: Path, raw: bytes) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        if temporary.exists(): temporary.unlink()


def run(command: list[str], timeout: int = 1200) -> subprocess.CompletedProcess[bytes]:
    env = {"CI":"1", "LANG":"C.UTF-8", "LC_ALL":"C", "NEXT_TELEMETRY_DISABLED":"1", "PATH":"/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin", "TMPDIR":str(CONTROL/"tmp"), "XDG_CACHE_HOME":str(CONTROL/"xdg-cache"), "XDG_CONFIG_HOME":str(CONTROL/"xdg-config"), "XDG_STATE_HOME":str(CONTROL/"xdg-state"), "npm_config_cache":str(CONTROL/"npm-cache"), "npm_config_userconfig":str(CONTROL/"npmrc"), "npm_config_update_notifier":"false"}
    return subprocess.run(command, cwd=WORKSPACE, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)


def offline(command: list[str], name: str, timeout: int = 1200) -> dict[str, Any]:
    completed = run(["/usr/bin/sandbox-exec", "-f", str(CONTROL/"offline.sb"), *command], timeout)
    raw = completed.stdout + completed.stderr
    atomic_write(CONTROL/f"{name}.log", raw)
    return {"exit":completed.returncode, "log_bytes":len(raw), "log_sha256":digest(raw), "network_mode":"DENIED_SEATBELT"}


def git(*args: str) -> list[str]:
    completed = run(["git", *args], 180)
    if completed.returncode != 0: raise WorkError("GIT_INSPECTION_FAILED")
    return completed.stdout.decode().splitlines()


def main() -> int:
    if WORK_RECEIPT.exists(): raise WorkError("WORK_ALREADY_RECORDED")
    if digest(PREPARATION) != PREPARATION_FILE_SHA256: raise WorkError("PREPARATION_FILE_DRIFT")
    prepared = json.loads(PREPARATION.read_text())
    if prepared.get("receipt_sha256") != PREPARATION_RECEIPT_SHA256 or prepared.get("status") != "EV1_T06_READY_FOR_AUTONOMOUS_TASK_WORK": raise WorkError("PREPARATION_RECEIPT_DRIFT")
    if git("rev-parse", "HEAD") != [TASK_COMMIT]: raise WorkError("TASK_COMMIT_DRIFT")
    state = {"committed":git("diff","--name-only",f"{prepared['disposable_baseline_commit']}..HEAD"), "uncommitted":git("diff","--name-only"), "untracked":git("ls-files","--others","--exclude-standard"), "status":git("status","--porcelain=v1","-uall")}
    expected = {"committed":["lib/ranking.ts","scripts/run-stable-ranking.mjs"], "uncommitted":["lib/signals.ts","package.json"], "untracked":["scripts/stable-ranking-cases.cjs"], "status":[" M lib/signals.ts"," M package.json","?? scripts/stable-ranking-cases.cjs"]}
    if state != expected: raise WorkError(f"TASK_STATE_MIX_MISMATCH:{state}")

    hashes: dict[str,str] = {}
    total = 0
    for relative in DECLARED:
        path = WORKSPACE/relative
        if path.is_symlink() or not path.is_file() or WORKSPACE.resolve() not in path.resolve().parents: raise WorkError("DECLARED_PATH_UNSAFE")
        raw = path.read_bytes()
        if PRIVATE.search(raw): raise WorkError(f"PRIVATE_MARKER:{relative}")
        hashes[relative] = digest(raw); total += len(raw)
    ranking = (WORKSPACE/"lib/ranking.ts").read_text()
    signals = (WORKSPACE/"lib/signals.ts").read_text()
    static = {"pure_copy_before_sort":"[...signals].sort(compareAnalyzedSignals)" in ranking, "score_order":"right.relevance_score - left.relevance_score" in ranking, "publication_tiebreak":"rightTimestamp - leftTimestamp" in ranking, "id_tiebreak":"compareText(left.id, right.id)" in ranking, "integration":"return rankAnalyzedSignals(analyzed)" in signals}
    if not all(static.values()): raise WorkError("STATIC_CONTRACT_FAILED")

    test = offline(["/usr/local/bin/npm","run","test:stable-ranking"], "work-stable-ranking")
    typecheck = offline(["/usr/local/bin/npm","run","typecheck"], "work-typecheck")
    build = offline(["/usr/local/bin/npm","run","build"], "work-build")
    if any(row["exit"] != 0 for row in (test,typecheck,build)): raise WorkError("ACCEPTANCE_FAILED")
    repeats = [offline(["/usr/local/bin/npm","run","test:stable-ranking"], f"work-stable-ranking-repeat-{index}") for index in range(1,6)]
    if any(row["exit"] != 0 for row in repeats) or len({row["log_sha256"] for row in repeats}) != 1: raise WorkError("DETERMINISM_FAILED")

    body = {"version":"ev1-t06-work-receipt-v1", "status":"EV1_T06_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED", "task_id":"EV1-T06", "utc_recorded":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()), "backlog_sha256":prepared["backlog_sha256"], "preflight_packet_sha256":prepared["preflight_packet_sha256"], "product_candidate":prepared["product_candidate"], "source_commit":prepared["source_commit"], "source_manifest_sha256":prepared["source_manifest_sha256"], "preparation_file_sha256":digest(PREPARATION), "preparation_receipt_sha256":prepared["receipt_sha256"], "disposable_baseline_commit":prepared["disposable_baseline_commit"], "task_commit":TASK_COMMIT, "state_mix":state, "declared_paths":sorted(DECLARED), "declared_file_hashes":dict(sorted(hashes.items())), "declared_aggregate_bytes":total, "static_contract":static, "acceptance":{"stable_ranking":test,"typecheck":typecheck,"build":build}, "determinism":{"executions":5,"identical_log_sha256":repeats[0]["log_sha256"],"results":repeats}, "ranking_cases":5, "repeat_proofs_per_case":5, "offline_profile_sha256":digest(CONTROL/"offline.sb"), "dependency_lock_sha256":prepared["dependency_setup"]["lockfile_sha256"], "private_marker_matches":0, "capture_started":False, "deletion_started":False, "recovery_started":False, "capture_declaration_required":True}
    sealed = dict(body, receipt_sha256=digest(body))
    raw = canonical(sealed)+b"\n"; atomic_write(WORK_RECEIPT,raw)
    print(canonical({"file_sha256":digest(raw),"receipt_sha256":sealed["receipt_sha256"],"status":sealed["status"]}).decode())
    return 0


if __name__ == "__main__": raise SystemExit(main())
