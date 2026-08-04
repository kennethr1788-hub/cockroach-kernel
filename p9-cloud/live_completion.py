#!/usr/bin/env python3
"""Deterministic P9 live-evidence preparation and reconciliation.

This adapter never opens a network connection and never reads credentials. It
prepares code-owned SQL and canonical payloads for the separately controlled
CockroachDB and Lambda surfaces, then validates returned Lambda evidence before
preparing the remaining immutable rows. Cloud output stays advisory; the P4
local verifier is the only verdict authority.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any

import context_vector
import coordinator
import records
import run_offline

BASE = Path(__file__).resolve().parents[1]
TRIALS = (coordinator.PROMOTE_TRIAL_ID, coordinator.REFUSE_TRIAL_ID)
AWS_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9-]{8,64}$")


def _load_verifier():
    # Clean-clone/installed builds expose the authority under the declared
    # package name. Prefer that stable package boundary over a source-tree
    # path, while retaining the fallback for local development checkouts.
    try:
        return importlib.import_module("verifier_runtime.verifier")
    except (ImportError, ModuleNotFoundError):
        pass
    path = BASE / "p4-verifier" / "verifier.py"
    spec = importlib.util.spec_from_file_location("p4_live_authority", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("P4_VERIFIER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, value: Any) -> None:
    path.write_bytes(records.canonical_json(value) + b"\n")


def _read(path: Path) -> Any:
    raw = path.read_bytes()
    if len(raw) > records.MAX_MESSAGE_BYTES + 1:
        raise RuntimeError("EVIDENCE_FILE_TOO_LARGE")
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("EVIDENCE_JSON_INVALID") from exc


def _sql_string(value: str) -> str:
    if not isinstance(value, str) or "\x00" in value:
        raise RuntimeError("SQL_VALUE_INVALID")
    return "'" + value.replace("'", "''") + "'"


def _json_text(value: Any) -> str:
    return records.canonical_json(value).decode("utf-8")


def _hex(value: str) -> str:
    return records.require_hash(value)


def _vector_text(value: list[float]) -> str:
    if len(value) != context_vector.DIMENSIONS:
        raise RuntimeError("VECTOR_DIMENSION_INVALID")
    return "[" + ",".join(format(component, ".6f") for component in value) + "]"


def _features(refuse: bool) -> dict[str, Any]:
    return {
        "event_count": 3 if not refuse else 4,
        "approvals": 2 if not refuse else 1,
        "refusals": 0 if not refuse else 2,
        "context_relevance": 0.875 if not refuse else 0.25,
        "quorum_met": not refuse,
        "policy_veto": refuse,
        "tampered": refuse,
        "unsafe": refuse,
        "warrant_consumed": False,
    }


def _candidate(trial_id: str, receipt_hash: str, refuse: bool) -> dict[str, Any]:
    verifier = _load_verifier()
    branch = "refuse" if refuse else "promote"
    payload = {
        "path": "src/trajectory.py",
        "content_hash": records.sha256_hex({"trial": trial_id, "content": branch}),
    }
    candidate = {
        "version": "p4-v1",
        "candidate_id": f"ck-p9-live-{branch}-candidate-r1",
        "source_receipt_hash": receipt_hash,
        "payload": payload,
        "payload_hash": verifier.digest(payload),
        "schema_version": "p4-v1",
        "provenance": {"source": "p9-live-cockroach-receipt"},
        "supported": True,
        "one_use_state": "ISSUED",
        "quarantined": False,
        "policy_veto": False,
        "requested_paths": ["src/trajectory.py"],
        "declared_paths": ["src/trajectory.py"],
    }
    if refuse:
        candidate["payload"]["content_hash"] = records.sha256_hex(
            {"trial": trial_id, "content": "tampered"}
        )
    return candidate


def prepared_trial(trial_id: str) -> dict[str, Any]:
    if trial_id not in TRIALS:
        raise RuntimeError("TRIAL_ID_INVALID")
    refuse = trial_id == coordinator.REFUSE_TRIAL_ID
    branch = "refuse" if refuse else "promote"
    task_id = trial_id
    event_id = f"{trial_id}-event-r1"
    request_id = f"ck-p9-live-{branch}-request-r1"
    task_json = {"kind": "task", "trial": trial_id}
    task_hash = records.sha256_hex(task_json)
    state_hash = records.sha256_hex({"declared_state": branch, "trial": trial_id})
    event_json = {"kind": "event", "trial": trial_id}
    event_hash = records.sha256_hex(event_json)
    receipt_json = {"kind": "receipt", "trial": trial_id}
    receipt_hash = records.sha256_hex(receipt_json)
    vector = context_vector.context_vector(
        f"continue {branch} synthetic trajectory after session loss", "ck-p9-completion"
    )
    vector_digest = context_vector.vector_digest(vector)
    candidate = _candidate(trial_id, receipt_hash, refuse)
    candidate_hash = records.sha256_hex(candidate)
    request = records.make_request(
        request_id,
        task_id,
        candidate["candidate_id"],
        event_hash,
        candidate_hash,
        records.sha256_hex({"policy": "p8-golden", "trial": trial_id}),
        _features(refuse),
    )
    payloads = (
        {
            "task_id": task_id,
            "event_id": event_id,
            "receipt_hash": receipt_hash,
            "task_hash": task_hash,
            "event_hash": event_hash,
            "state_hash": state_hash,
        },
        {
            "vector_id": f"{trial_id}-vector-r1",
            "task_id": task_id,
            "event_hash": event_hash,
            "namespace": "ck-p9-completion",
            "vector_digest": vector_digest,
        },
        {
            "task_id": task_id,
            "namespace": "ck-p9-completion",
            "limit": coordinator.MAX_VECTOR_ROWS,
            "query_digest": records.sha256_hex(
                {"task_id": task_id, "namespace": "ck-p9-completion", "vector": vector}
            ),
        },
        {
            "request_id": request_id,
            "task_id": task_id,
            "candidate_id": candidate["candidate_id"],
            "request_hash": request["request_hash"],
        },
    )
    instance = coordinator.Coordinator(trial_id)
    commands = []
    for operation, payload in zip(coordinator.ORDER[:4], payloads):
        command = coordinator.make_command(
            trial_id, instance.next_sequence, instance.last_hash, operation, payload
        )
        instance.accept(records.canonical_json(command))
        commands.append(command)
    return {
        "version": "p9-live-prepared-v1",
        "campaign_id": coordinator.CAMPAIGN_ID,
        "trial_id": trial_id,
        "branch": branch,
        "task_id": task_id,
        "event_id": event_id,
        "task_json": task_json,
        "task_hash": task_hash,
        "state_hash": state_hash,
        "event_json": event_json,
        "event_hash": event_hash,
        "receipt_json": receipt_json,
        "receipt_hash": receipt_hash,
        "vector_id": f"{trial_id}-vector-r1",
        "namespace": "ck-p9-completion",
        "vector": vector,
        "vector_digest": vector_digest,
        "candidate": candidate,
        "candidate_hash": candidate_hash,
        "request": request,
        "commands": commands,
        "coordinator_snapshot": json.loads(instance.snapshot()),
    }


def seed_sql(trial: dict[str, Any]) -> str:
    values = {
        "task_id": _sql_string(trial["task_id"]),
        "campaign": _sql_string(coordinator.CAMPAIGN_ID),
        "task_json": _sql_string(_json_text(trial["task_json"])),
        "task_hash": _sql_string(_hex(trial["task_hash"])),
        "state_hash": _sql_string(_hex(trial["state_hash"])),
        "event_id": _sql_string(trial["event_id"]),
        "event_json": _sql_string(_json_text(trial["event_json"])),
        "event_hash": _sql_string(_hex(trial["event_hash"])),
        "receipt_json": _sql_string(_json_text(trial["receipt_json"])),
        "receipt_hash": _sql_string(_hex(trial["receipt_hash"])),
        "vector_id": _sql_string(trial["vector_id"]),
        "namespace": _sql_string(trial["namespace"]),
        "vector": _sql_string(_vector_text(trial["vector"])),
        "vector_digest": _sql_string(_hex(trial["vector_digest"])),
    }
    return f"""BEGIN;
PREPARE p9_task (STRING, STRING, JSONB, BYTES, BYTES) AS
  INSERT INTO ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash)
  VALUES ($1,$2,$3,$4,$5);
EXECUTE p9_task({values['task_id']},{values['campaign']},{values['task_json']},decode({values['task_hash']},'hex'),decode({values['state_hash']},'hex'));
DEALLOCATE p9_task;
PREPARE p9_event (STRING, STRING, INT8, BYTES, BYTES, JSONB, BYTES) AS
  INSERT INTO ck.trajectory_events(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash)
  VALUES ($1,$2,$3,$4,$5,$6,$7);
EXECUTE p9_event({values['event_id']},{values['task_id']},0,decode('{coordinator.GENESIS_HASH}','hex'),decode({values['state_hash']},'hex'),{values['event_json']},decode({values['event_hash']},'hex'));
DEALLOCATE p9_event;
PREPARE p9_receipt (BYTES, STRING, BYTES, STRING, JSONB) AS
  INSERT INTO ck.receipts(receipt_hash,task_id,event_hash,status,receipt_json)
  VALUES ($1,$2,$3,$4,$5);
EXECUTE p9_receipt(decode({values['receipt_hash']},'hex'),{values['task_id']},decode({values['event_hash']},'hex'),'SEALED',{values['receipt_json']});
DEALLOCATE p9_receipt;
PREPARE p9_vector (STRING, STRING, BYTES, STRING, VECTOR(64), BYTES) AS
  INSERT INTO ck.context_vectors(vector_id,task_id,event_hash,namespace,vector,vector_digest)
  VALUES ($1,$2,$3,$4,$5,$6);
EXECUTE p9_vector({values['vector_id']},{values['task_id']},decode({values['event_hash']},'hex'),{values['namespace']},{values['vector']}::VECTOR(64),decode({values['vector_digest']},'hex'));
DEALLOCATE p9_vector;
COMMIT;
"""


def vector_query_sql(trial: dict[str, Any]) -> str:
    return f"""PREPARE p9_vector_query (VECTOR(64), STRING, STRING, INT8) AS
SELECT vector_id, encode(event_hash,'hex') AS event_hash,
       encode(vector_digest,'hex') AS vector_digest,
       vector <-> $1 AS distance
FROM ck.context_vectors
WHERE task_id = $2 AND namespace = $3
ORDER BY vector <-> $1
LIMIT $4;
EXECUTE p9_vector_query({_sql_string(_vector_text(trial['vector']))}::VECTOR(64),{_sql_string(trial['task_id'])},{_sql_string(trial['namespace'])},8);
DEALLOCATE p9_vector_query;
"""


def prepare(out: Path) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=False)
    manifests = []
    for trial_id in TRIALS:
        trial = prepared_trial(trial_id)
        branch = trial["branch"]
        _write(out / f"{branch}-prepared.json", trial)
        _write(out / f"{branch}-request.json", trial["request"])
        _write(out / f"{branch}-candidate.json", trial["candidate"])
        (out / f"{branch}-seed.sql").write_text(seed_sql(trial), encoding="utf-8")
        (out / f"{branch}-vector-query.sql").write_text(
            vector_query_sql(trial), encoding="utf-8"
        )
        manifests.append({
            "trial_id": trial_id,
            "branch": branch,
            "prepared_hash": records.sha256_hex(trial),
            "request_hash": trial["request"]["request_hash"],
            "candidate_hash": trial["candidate_hash"],
        })
    manifest = {
        "version": "p9-live-prepare-manifest-v1",
        "campaign_id": coordinator.CAMPAIGN_ID,
        "trials": manifests,
    }
    manifest["manifest_hash"] = records.sha256_hex(manifest)
    _write(out / "prepare-manifest.json", manifest)
    return manifest


def _capsule(trial: dict[str, Any], verdict: str) -> dict[str, Any]:
    body = {
        "version": "p9-resume-v1",
        "task_id": trial["task_id"],
        "receipt_hash": trial["receipt_hash"],
        "candidate_id": trial["candidate"]["candidate_id"],
        "verdict": verdict,
    }
    return dict(body, capsule_hash=records.sha256_hex(body))


def reconcile_trial(out: Path, branch: str) -> tuple[dict[str, Any], str]:
    trial = _read(out / f"{branch}-prepared.json")
    response = _read(out / f"{branch}-lambda-response.json")
    meta = _read(out / f"{branch}-lambda-meta.json")
    records.validate_request(trial["request"])
    records.validate_response(response)
    if not records.response_matches_request(trial["request"], response):
        raise RuntimeError("LAMBDA_RESPONSE_LINKAGE_FAILED")
    aws_request_id = meta.get("aws_request_id")
    if not isinstance(aws_request_id, str) or not AWS_REQUEST_ID_RE.fullmatch(aws_request_id):
        raise RuntimeError("AWS_REQUEST_ID_INVALID")
    if meta.get("status_code") != 200 or meta.get("function_error") not in (None, ""):
        raise RuntimeError("LAMBDA_INVOCATION_FAILED")
    verifier = _load_verifier()
    verdicts = [verifier.verify(trial["candidate"]) for _ in range(5)]
    if len(set(verdicts)) != 1:
        raise RuntimeError("LOCAL_VERDICT_NONDETERMINISTIC")
    verdict, reason = verdicts[0]
    expected = "PROMOTE" if branch == "promote" else "REFUSE"
    if verdict != expected:
        raise RuntimeError("LOCAL_VERDICT_UNEXPECTED")
    result_json = {
        "version": "p9-live-worker-result-v1",
        "request_id": trial["request"]["request_id"],
        "request_hash": trial["request"]["request_hash"],
        "response_hash": response["response_hash"],
        "aws_request_id_hash": records.sha256_hex(aws_request_id.encode("utf-8")),
        "status": response["status"],
    }
    result_hash = records.sha256_hex(result_json)
    projection_json = {
        "version": "p9-live-projection-v1",
        "request_id": trial["request"]["request_id"],
        "result_hash": result_hash,
        "receipt_hash": trial["receipt_hash"],
    }
    projection_hash = records.sha256_hex(projection_json)
    instance = coordinator.Coordinator.restore(records.canonical_json(trial["coordinator_snapshot"]))
    remaining = (
        {
            "request_id": trial["request"]["request_id"],
            "task_id": trial["task_id"],
            "result_hash": result_hash,
            "response_hash": response["response_hash"],
            "receipt_hash": trial["receipt_hash"],
            "attempt": 1,
        },
        {
            "request_id": trial["request"]["request_id"],
            "projection_id": f"{trial['trial_id']}-projection-r1",
            "receipt_hash": trial["receipt_hash"],
            "cursor": 1,
            "projection_hash": projection_hash,
        },
        {
            "projection_id": f"{trial['trial_id']}-projection-r1",
            "cursor": 1,
            "resume_hash": records.sha256_hex({"trial": trial["trial_id"], "resume": 1}),
        },
        {
            "candidate_id": trial["candidate"]["candidate_id"],
            "receipt_hash": trial["receipt_hash"],
            "candidate_hash": trial["candidate_hash"],
            "tampered": branch == "refuse",
            "unsafe": branch == "refuse",
        },
        {
            "task_id": trial["task_id"],
            "receipt_hash": trial["receipt_hash"],
            "capsule_hash": records.sha256_hex({"trial": trial["trial_id"], "capsule": verdict}),
        },
        {
            "task_id": trial["task_id"],
            "replay_hash": records.sha256_hex({"trial": trial["trial_id"], "replay": verdict}),
            "expected_verdict": verdict,
        },
        {
            "task_id": trial["task_id"],
            "receipt_hash": trial["receipt_hash"],
            "event_hash": trial["event_hash"],
            "limit": coordinator.MAX_MCP_ROWS,
        },
    )
    commands = list(trial["commands"])
    for operation, payload in zip(coordinator.ORDER[4:11], remaining):
        command = coordinator.make_command(
            trial["trial_id"], instance.next_sequence, instance.last_hash, operation, payload
        )
        instance.accept(records.canonical_json(command))
        commands.append(command)
    capsule = _capsule(trial, verdict)
    result = {
        "version": "p9-live-reconciled-v1",
        "trial_id": trial["trial_id"],
        "branch": branch,
        "request_hash": trial["request"]["request_hash"],
        "response_hash": response["response_hash"],
        "aws_request_id_hash": result_json["aws_request_id_hash"],
        "result_json": result_json,
        "result_hash": result_hash,
        "projection_json": projection_json,
        "projection_hash": projection_hash,
        "verdicts": [{"verdict": item[0], "reason": item[1]} for item in verdicts],
        "capsule": capsule,
        "commands": commands,
        "coordinator_snapshot": json.loads(instance.snapshot()),
    }
    result["result_receipt_hash"] = records.sha256_hex(result)
    return result, finalize_sql(trial, result)


def finalize_sql(trial: dict[str, Any], result: dict[str, Any]) -> str:
    request = trial["request"]
    response = _read(Path("/dev/null")) if False else None  # keeps data flow explicit
    del response
    result_json = result["result_json"]
    projection_json = result["projection_json"]
    return f"""BEGIN;
PREPARE p9_worker (STRING,STRING,STRING,BYTES,BYTES,INT8,STRING,STRING,JSONB,BYTES) AS
  INSERT INTO ck.worker_results(request_id,task_id,candidate_id,request_hash,response_hash,attempt,supersedes,status,result_json,result_hash)
  VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10);
EXECUTE p9_worker({_sql_string(request['request_id'])},{_sql_string(trial['task_id'])},{_sql_string(trial['candidate']['candidate_id'])},decode({_sql_string(request['request_hash'])},'hex'),decode({_sql_string(result['response_hash'])},'hex'),1,NULL,'ADVISORY',{_sql_string(_json_text(result_json))},decode({_sql_string(result['result_hash'])},'hex'));
DEALLOCATE p9_worker;
PREPARE p9_projection (STRING,STRING,STRING,BYTES,INT8,JSONB,BYTES) AS
  INSERT INTO ck.projection_events(projection_id,source_table,source_key,receipt_hash,sequence,projected_json,projection_hash)
  VALUES ($1,$2,$3,$4,$5,$6,$7);
EXECUTE p9_projection({_sql_string(trial['trial_id'] + '-projection-r1')},'worker_results',{_sql_string(request['request_id'])},decode({_sql_string(trial['receipt_hash'])},'hex'),1,{_sql_string(_json_text(projection_json))},decode({_sql_string(result['projection_hash'])},'hex'));
DEALLOCATE p9_projection;
COMMIT;
"""


def reconcile(out: Path) -> dict[str, Any]:
    trials = []
    for branch in ("promote", "refuse"):
        result, sql = reconcile_trial(out, branch)
        _write(out / f"{branch}-reconciled.json", result)
        (out / f"{branch}-finalize.sql").write_text(sql, encoding="utf-8")
        trials.append({
            "trial_id": result["trial_id"],
            "branch": branch,
            "result_receipt_hash": result["result_receipt_hash"],
            "request_hash": result["request_hash"],
            "response_hash": result["response_hash"],
            "result_hash": result["result_hash"],
            "projection_hash": result["projection_hash"],
            "verdict": result["verdicts"][0]["verdict"],
            "reason": result["verdicts"][0]["reason"],
        })
    manifest = {
        "version": "p9-live-reconciled-manifest-v1",
        "campaign_id": coordinator.CAMPAIGN_ID,
        "trials": trials,
    }
    manifest["manifest_hash"] = records.sha256_hex(manifest)
    _write(out / "reconciled-manifest.json", manifest)
    return manifest


def close(out: Path) -> dict[str, Any]:
    closed = []
    for branch in ("promote", "refuse"):
        result = _read(out / f"{branch}-reconciled.json")
        trial = _read(out / f"{branch}-prepared.json")
        instance = coordinator.Coordinator.restore(
            records.canonical_json(result["coordinator_snapshot"])
        )
        payload = {
            "task_id": trial["task_id"],
            "cleanup_hash": records.sha256_hex({"trial": trial["trial_id"], "cleanup": True}),
        }
        command = coordinator.make_command(
            trial["trial_id"], instance.next_sequence, instance.last_hash,
            coordinator.Operation.CLEANUP_TRIAL, payload,
        )
        instance.accept(records.canonical_json(command))
        closed.append({
            "trial_id": trial["trial_id"],
            "cleanup_command_hash": command["command_hash"],
            "final_snapshot_hash": json.loads(instance.snapshot())["snapshot_hash"],
            "accepted_operations": instance.next_sequence,
        })
    receipt = {
        "version": "p9-live-close-v1",
        "campaign_id": coordinator.CAMPAIGN_ID,
        "trials": closed,
    }
    receipt["receipt_hash"] = records.sha256_hex(receipt)
    _write(out / "close-receipt.json", receipt)
    return receipt


def fresh_trial(out: Path, branch: str) -> dict[str, Any]:
    """Re-evaluate one frozen trial from canonical files in a fresh process.

    The caller is responsible for starting this mode from a new process/root.
    This function reads only the prepared and reconciled evidence files. It
    does not use a cloud session, database connection, credential, or mutable
    coordinator state.
    """
    if branch not in {"promote", "refuse"}:
        raise RuntimeError("FRESH_TRIAL_BRANCH_INVALID")
    trial = _read(out / f"{branch}-prepared.json")
    reconciled = _read(out / f"{branch}-reconciled.json")
    if trial.get("branch") != branch or reconciled.get("branch") != branch:
        raise RuntimeError("FRESH_TRIAL_LINKAGE_INVALID")
    if trial.get("trial_id") != reconciled.get("trial_id"):
        raise RuntimeError("FRESH_TRIAL_LINKAGE_INVALID")

    verifier = _load_verifier()
    verdicts = [verifier.verify(trial["candidate"]) for _ in range(5)]
    expected_verdict = "PROMOTE" if branch == "promote" else "REFUSE"
    if verdicts != [(expected_verdict, reconciled["verdicts"][0]["reason"])] * 5:
        raise RuntimeError("FRESH_TRIAL_VERDICT_MISMATCH")

    capsule = reconciled["capsule"]
    resumed, resume_reason = run_offline.fresh_resume(records.canonical_json(capsule))
    expected_resume = branch == "promote"
    expected_resume_reason = "FRESH_CONTEXT_PASS" if expected_resume else "CAPSULE_NOT_PROMOTED"
    if resumed != expected_resume or resume_reason != expected_resume_reason:
        raise RuntimeError("FRESH_TRIAL_RESUME_MISMATCH")

    result = {
        "version": "p9-fresh-trial-v1",
        "replay_label": "KEYLESS_LOCAL_REPLAY",
        "branch": branch,
        "trial_id": trial["trial_id"],
        "request_hash": trial["request"]["request_hash"],
        "receipt_hash": trial["receipt_hash"],
        "capsule_hash": capsule["capsule_hash"],
        "cloud_status": reconciled["result_json"]["status"],
        "verdicts": [
            {"verdict": verdict, "reason": reason} for verdict, reason in verdicts
        ],
        "fresh_context_continued": resumed,
        "fresh_context_reason": resume_reason,
        "session_state_inputs": [
            f"{branch}-prepared.json",
            f"{branch}-reconciled.json",
        ],
        "credentials_used": False,
        "network_used": False,
    }
    result["result_hash"] = records.sha256_hex(result)
    return result


def inspect_changefeed(path: Path) -> dict[str, Any]:
    """Decode bounded CockroachDB CLI NDJSON without trusting payload fields."""
    raw = path.read_bytes()
    if len(raw) > 1024 * 1024:
        raise RuntimeError("CHANGEFEED_EVIDENCE_TOO_LARGE")
    request_ids: list[str] = []
    resolved: list[str] = []
    rows = 0
    for line in raw.splitlines():
        if not line:
            continue
        try:
            envelope = json.loads(line)
            value = envelope["value"]
            if not isinstance(value, str) or not value.startswith("\\x"):
                raise ValueError
            decoded = json.loads(bytes.fromhex(value[2:]).decode("utf-8"))
        except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("CHANGEFEED_EVIDENCE_INVALID") from exc
        rows += 1
        if set(decoded) == {"resolved"} and isinstance(decoded["resolved"], str):
            resolved.append(decoded["resolved"])
            continue
        after = decoded.get("after")
        if isinstance(after, dict):
            request_id = after.get("request_id")
            if isinstance(request_id, str):
                records.require_id(request_id)
                request_ids.append(request_id)
    result = {
        "version": "p9-changefeed-inspection-v1",
        "rows": rows,
        "request_ids": request_ids,
        "resolved": resolved,
    }
    result["inspection_hash"] = records.sha256_hex(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", choices=("prepare", "reconcile", "close", "inspect-feed", "fresh-trial")
    )
    parser.add_argument("out")
    parser.add_argument("branch", nargs="?", choices=("promote", "refuse"))
    args = parser.parse_args()
    output = Path(args.out).resolve()
    if args.mode == "prepare":
        result = prepare(output)
    elif args.mode == "reconcile":
        result = reconcile(output)
    elif args.mode == "close":
        result = close(output)
    elif args.mode == "fresh-trial":
        if args.branch is None:
            parser.error("fresh-trial requires branch")
        result = fresh_trial(output, args.branch)
        _write(output / f"{args.branch}-fresh-trial.json", result)
    else:
        result = inspect_changefeed(output)
    print(records.canonical_json(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
