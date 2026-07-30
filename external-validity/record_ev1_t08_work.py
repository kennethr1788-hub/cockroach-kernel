#!/usr/bin/env python3
"""Verify and freeze EV1-T08 task work without reading the outside target."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
from typing import Any


ROOT=Path(__file__).resolve().parents[1]; CAMPAIGN=ROOT/".ev1-runtime"/"EV1-T08"; CONTROL=CAMPAIGN/"control"; WORKSPACE=CAMPAIGN/"workspace"; PREPARATION=CONTROL/"PREPARATION_RECEIPT.json"; WORK_RECEIPT=CONTROL/"WORK_RECEIPT.json"; OUTSIDE=CAMPAIGN/"synthetic-outside-target.json"
PREPARATION_FILE_SHA256="df23ee57785a0e7ae8bbf6be2835d3e8d91843563a3e84442de945c3e93d8e25"; PREPARATION_RECEIPT_SHA256="7d92b90c57def4af392ca224b8ff96ca1c517f5b3e61cb70ab880f02f939013b"; TASK_COMMIT="6b81ce4eb1f1d7a6e83b733ef18d92cf7c44c178"; LINK="data/escape-sample-signals.json"; LINK_TARGET="../../synthetic-outside-target.json"; OUTSIDE_SHA256="389d0c95725cbaad3054d6f0dd39be80911dddaaa8698eebb5bfd4621ded0a34"
REGULAR=("lib/dataPath.ts","lib/signals.ts","package.json","scripts/run-data-path-containment.mjs")
PRIVATE=re.compile(rb"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY")


class WorkError(RuntimeError): pass
def canonical(value:Any)->bytes:return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def digest(value:bytes|Path|Any)->str:
    raw=value.read_bytes() if isinstance(value,Path) else value if isinstance(value,bytes) else canonical(value);return hashlib.sha256(raw).hexdigest()
def atomic(path:Path,raw:bytes)->None:
    temporary=path.with_name(f".{path.name}.{os.getpid()}.tmp");descriptor=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(descriptor,"wb",closefd=True) as handle:handle.write(raw);handle.flush();os.fsync(handle.fileno())
        os.replace(temporary,path);directory=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if temporary.exists():temporary.unlink()
def run(command:list[str],timeout:int=1200)->subprocess.CompletedProcess[bytes]:
    env={"CI":"1","LANG":"C.UTF-8","LC_ALL":"C","NEXT_TELEMETRY_DISABLED":"1","PATH":"/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin","TMPDIR":str(CONTROL/"tmp"),"XDG_CACHE_HOME":str(CONTROL/"xdg-cache"),"XDG_CONFIG_HOME":str(CONTROL/"xdg-config"),"XDG_STATE_HOME":str(CONTROL/"xdg-state"),"npm_config_cache":str(CONTROL/"npm-cache"),"npm_config_userconfig":str(CONTROL/"npmrc"),"npm_config_update_notifier":"false"}
    return subprocess.run(command,cwd=WORKSPACE,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,check=False)
def offline(command:list[str],name:str,timeout:int=1200)->dict[str,Any]:
    completed=run(["/usr/bin/sandbox-exec","-f",str(CONTROL/"offline.sb"),*command],timeout);raw=completed.stdout+completed.stderr;atomic(CONTROL/f"{name}.log",raw);return {"exit":completed.returncode,"log_bytes":len(raw),"log_sha256":digest(raw),"network_mode":"DENIED_SEATBELT"}
def git(*args:str)->list[str]:
    completed=run(["git",*args],180)
    if completed.returncode!=0:raise WorkError("GIT_INSPECTION_FAILED")
    return completed.stdout.decode().splitlines()
def metadata(path:Path)->dict[str,int]:
    row=path.stat();return {"inode":row.st_ino,"mode":row.st_mode,"mtime_ns":row.st_mtime_ns,"size":row.st_size}


def main()->int:
    if WORK_RECEIPT.exists():raise WorkError("WORK_ALREADY_RECORDED")
    if digest(PREPARATION)!=PREPARATION_FILE_SHA256:raise WorkError("PREPARATION_FILE_DRIFT")
    prepared=json.loads(PREPARATION.read_text())
    if prepared.get("receipt_sha256")!=PREPARATION_RECEIPT_SHA256 or prepared.get("status")!="EV1_T08_READY_FOR_AUTONOMOUS_TASK_WORK":raise WorkError("PREPARATION_RECEIPT_DRIFT")
    if git("rev-parse","HEAD")!=[TASK_COMMIT]:raise WorkError("TASK_COMMIT_DRIFT")
    state={"committed":git("diff","--name-only",f"{prepared['disposable_baseline_commit']}..HEAD"),"uncommitted":git("diff","--name-only"),"untracked":git("ls-files","--others","--exclude-standard"),"status":git("status","--porcelain=v1","-uall")}
    expected={"committed":["lib/dataPath.ts","scripts/run-data-path-containment.mjs"],"uncommitted":["lib/signals.ts","package.json"],"untracked":[LINK],"status":[" M lib/signals.ts"," M package.json","?? data/escape-sample-signals.json"]}
    if state!=expected:raise WorkError(f"TASK_STATE_MIX_MISMATCH:{state}")
    link=WORKSPACE/LINK
    if not link.is_symlink() or os.readlink(link)!=LINK_TARGET or link.resolve(strict=True)!=OUTSIDE.resolve(strict=True):raise WorkError("SYMLINK_CONTRACT_DRIFT")
    outside_before=metadata(OUTSIDE)
    if outside_before["size"]!=79 or prepared["outside_canary"]["sha256"]!=OUTSIDE_SHA256:raise WorkError("OUTSIDE_CANARY_BINDING_DRIFT")
    hashes:dict[str,str]={}
    for relative in REGULAR:
        path=WORKSPACE/relative
        if path.is_symlink() or not path.is_file() or WORKSPACE.resolve() not in path.resolve().parents:raise WorkError("DECLARED_REGULAR_PATH_UNSAFE")
        raw=path.read_bytes()
        if PRIVATE.search(raw):raise WorkError(f"PRIVATE_MARKER:{relative}")
        hashes[relative]=digest(raw)
    test=offline(["/usr/local/bin/npm","run","test:data-path-containment"],"work-data-path-containment");typecheck=offline(["/usr/local/bin/npm","run","typecheck"],"work-typecheck");build=offline(["/usr/local/bin/npm","run","build"],"work-build")
    if any(row["exit"]!=0 for row in (test,typecheck,build)):raise WorkError("ACCEPTANCE_FAILED")
    repeats=[offline(["/usr/local/bin/npm","run","test:data-path-containment"],f"work-data-path-repeat-{index}") for index in range(1,6)]
    if any(row["exit"]!=0 for row in repeats) or len({row["log_sha256"] for row in repeats})!=1:raise WorkError("DETERMINISM_FAILED")
    outside_after=metadata(OUTSIDE)
    if outside_after!=outside_before or not link.is_symlink() or os.readlink(link)!=LINK_TARGET:raise WorkError("OUTSIDE_TARGET_OR_LINK_MUTATED")
    data_path=(WORKSPACE/"lib/dataPath.ts").read_text();signals=(WORKSPACE/"lib/signals.ts").read_text();runner=(WORKSPACE/"scripts/run-data-path-containment.mjs").read_text()
    static={"realpath_root":"fs.realpath(dataRoot)" in data_path,"realpath_candidate":"fs.realpath(lexicalCandidate)" in data_path,"pre_read_containment":"readContainedUtf8" in data_path and data_path.index("resolveContainedDataFile")<data_path.index("return reader(resolved"),"stable_escape_reason":"DATA_PATH_ESCAPE" in data_path,"runtime_integration":"readContainedUtf8(dataRoot, 'sample-signals.json')" in signals,"zero_reader_calls":"assert.equal(escapedReads, 0)" in runner}
    if not all(static.values()):raise WorkError("STATIC_CONTRACT_FAILED")
    body={"version":"ev1-t08-work-receipt-v1","status":"EV1_T08_WORK_GREEN_CAPTURE_DECLARATION_REQUIRED","task_id":"EV1-T08","utc_recorded":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"backlog_sha256":prepared["backlog_sha256"],"global_ev1_preflight_packet_sha256":prepared["global_ev1_preflight_packet_sha256"],"product_candidate":prepared["product_candidate"],"source_commit":prepared["source_commit"],"source_manifest_sha256":prepared["source_manifest_sha256"],"preparation_file_sha256":digest(PREPARATION),"preparation_receipt_sha256":prepared["receipt_sha256"],"disposable_baseline_commit":prepared["disposable_baseline_commit"],"task_commit":TASK_COMMIT,"state_mix":state,"declared_regular_file_hashes":dict(sorted(hashes.items())),"declared_symlink":{"path":LINK,"target":LINK_TARGET,"resolved_target_class":"SYNTHETIC_CAMPAIGN_CANARY_OUTSIDE_WORKSPACE"},"outside_canary":{"expected_sha256_not_reread":OUTSIDE_SHA256,"metadata_before":outside_before,"metadata_after":outside_after,"content_read_by_work_recorder":False},"static_contract":static,"acceptance":{"data_path_containment":test,"typecheck":typecheck,"build":build},"determinism":{"executions":5,"identical_log_sha256":repeats[0]["log_sha256"],"results":repeats},"predeclared_capture_outcome":"INVALID_UNSAFE_SYMLINK_ESCAPE","target_read_authorized":False,"target_modify_or_delete_authorized":False,"workspace_deletion_after_invalid_authorized":False,"private_marker_matches":0,"capture_started":False,"deletion_started":False,"recovery_started":False,"capture_declaration_required":True}
    sealed=dict(body,receipt_sha256=digest(body));raw=canonical(sealed)+b"\n";atomic(WORK_RECEIPT,raw);print(canonical({"file_sha256":digest(raw),"receipt_sha256":sealed["receipt_sha256"],"status":sealed["status"]}).decode());return 0


if __name__=="__main__":raise SystemExit(main())
