#!/usr/bin/env python3
"""Two fresh-root declared-loss and CockroachDB recovery trials."""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

import fresh_context as fc
import make_fixtures as fx
import records as rec

BASE = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
BIN = next(path for path in BASE.glob("p2-cleanroom/vendor/**/cockroach")
           if "darwin" in str(path))
P3_MIGRATION = BASE / "p3-ledger/migrations/001_ledger.sql"
P7_MIGRATION = HERE / "migrations/001_recovery.sql"
FIXTURES = HERE / "fixtures"


def quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def sql(port: int, statement: str, database: str | None = None,
        expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    args = [str(BIN), "sql", "--insecure", f"--host=127.0.0.1:{port}"]
    if database:
        args.append(f"--database={database}")
    args += ["-e", statement]
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False)
    if expect_ok and result.returncode != 0:
        raise RuntimeError(result.stdout)
    return result


def apply_file(port: int, database: str, path: Path) -> None:
    subprocess.run(
        [str(BIN), "sql", "--insecure", f"--host=127.0.0.1:{port}",
         f"--database={database}", f"--file={path}"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def fixture(name: str):
    return rec.load_canonical(str(FIXTURES / (name + ".json")))


def safe_target(root: Path, relative: str) -> Path:
    rec.validate_relative_path(relative)
    target = root.joinpath(*relative.split("/"))
    if root.resolve() not in target.resolve(strict=False).parents:
        raise rec.RecoveryError(rec.UNSAFE_PATH)
    return target


def write_bytes(root: Path, relative: str, payload: bytes) -> None:
    target = safe_target(root, relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        raise rec.RecoveryError(rec.UNSAFE_PATH)
    with target.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def tree_files(root: Path) -> list[str]:
    files = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise rec.RecoveryError(rec.UNSAFE_PATH)
        if path.is_file():
            files.append(path.relative_to(root).as_posix())
    return sorted(files)


def verify_active(root: Path, manifest: dict) -> None:
    expected = rec.declared_paths(manifest)
    if tree_files(root) != expected:
        raise rec.RecoveryError("MANIFEST_DRIFT")
    expected_hashes = {entry["path"]: entry["content_hash"]
                       for entry in manifest["files"]}
    for relative in expected:
        target = safe_target(root, relative)
        if target.is_symlink() or rec.sha256_hex(target.read_bytes()) != expected_hashes[relative]:
            raise rec.RecoveryError("MANIFEST_DRIFT")


def stop_owned(process: subprocess.Popen[str]) -> None:
    process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    if process.returncode is None:
        raise RuntimeError("owned process did not stop")


def observe_loss(active: Path, manifest: dict,
                 owned: subprocess.Popen[str]) -> dict:
    verify_active(active, manifest)
    stop_owned(owned)
    for relative in rec.declared_paths(manifest):
        target = safe_target(active, relative)
        if target.is_symlink() or not target.is_file():
            raise rec.RecoveryError("MANIFEST_DRIFT")
        target.unlink()
    if tree_files(active):
        raise rec.RecoveryError("LOSS_RESIDUE")
    receipt = fixture("loss-receipt")
    rec.validate_loss_receipt(receipt, manifest)
    return receipt


def last_data(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def trial(label: str, port: int, http_port: int) -> dict[str, object]:
    root = Path(tempfile.mkdtemp(prefix=f"{label}.", dir=HERE))
    active = root / "active"
    surviving = root / "surviving"
    successor = root / "successor"
    evidence = root / "evidence"
    fake_home = root / "empty-home"
    for path in (active, surviving, successor, evidence, fake_home):
        path.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(fake_home)
    log_handle = None
    database_process = None
    owned_process = None
    try:
        manifest = fixture("manifest")
        for relative, payload in fx.FILE_CONTENTS.items():
            write_bytes(active, relative, payload)

        alpha = fixture("candidate-alpha")
        beta = fixture("candidate-beta")
        for relative, content_hash in alpha["file_hashes"].items():
            payload = fx.FILE_CONTENTS[relative]
            if rec.sha256_hex(payload) != content_hash:
                raise rec.RecoveryError(rec.TAMPERED_EVIDENCE)
            write_bytes(surviving, "objects/" + content_hash, payload)

        owned_process = subprocess.Popen(
            ["/usr/bin/env", "python3", "-c", "import time; time.sleep(300)"],
            cwd=active, env=env, text=True, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

        log_handle = (root / "cockroach.log").open("w", encoding="utf-8")
        database_process = subprocess.Popen(
            [str(BIN), "start-single-node", "--insecure", f"--store={root / 'store'}",
             f"--listen-addr=127.0.0.1:{port}",
             f"--http-addr=127.0.0.1:{http_port}"],
            stdout=log_handle, stderr=subprocess.STDOUT, env=env, text=True)
        for _ in range(30):
            if sql(port, "SELECT 1", expect_ok=False).returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("CockroachDB did not become ready")

        database = "p7recovery"
        sql(port, f"CREATE DATABASE {database}")
        apply_file(port, database, P3_MIGRATION)
        apply_file(port, database, P7_MIGRATION)

        declared = {"scope": "synthetic-p7", "state": "declared-loss"}
        sql(port,
            "INSERT INTO tasks VALUES "
            "('task-p7-synthetic-001','p7-v1',decode(%s,'hex'),%s::JSONB,"
            "'2026-07-26 00:00:00+00')" %
            (quote(rec.sha256_hex(declared)), quote(json.dumps(declared))), database)

        loss = observe_loss(active, manifest, owned_process)
        owned_process = None
        (evidence / "loss-receipt.json").write_bytes(rec.canonical_json(loss))

        context = fx.build_context(manifest, fixture("trajectory-receipt"),
                                   fixture("quorum-decision"))
        decision = rec.select_candidate([beta, alpha], context)
        if decision != fixture("decision-promote"):
            raise rec.RecoveryError("DECISION_DRIFT")
        warrant = fixture("warrant-issued")
        promotion = fixture("promotion-receipt")
        ledger = fixture("unrecovered-ledger")

        sql(port, "INSERT INTO p7_manifests VALUES (%s,%s,%s::JSONB,decode(%s,'hex'))" % (
            quote(manifest["manifest_id"]), quote(manifest["task_id"]),
            quote(json.dumps(manifest)), quote(rec.sha256_hex(manifest))), database)
        sql(port, "INSERT INTO p7_loss_receipts VALUES (%s,%s,%s,%s::JSONB,decode(%s,'hex'))" % (
            quote(loss["receipt_id"]), quote(loss["task_id"]),
            quote(manifest["manifest_id"]), quote(json.dumps(loss)),
            quote(rec.sha256_hex(loss))), database)
        for candidate in (alpha, beta):
            sql(port, "INSERT INTO p7_recovery_candidates VALUES "
                "(%s,%s,decode(%s,'hex'),%s::JSONB,decode(%s,'hex'))" % (
                    quote(candidate["candidate_id"]), quote(candidate["task_id"]),
                    quote(rec.sha256_hex(loss)), quote(json.dumps(candidate)),
                    quote(rec.sha256_hex(candidate))), database)
        sql(port, "INSERT INTO p7_warrants VALUES (%s,%s,%s,decode(%s,'hex'),%s,%s::JSONB)" % (
            quote(warrant["warrant_id"]), quote(warrant["task_id"]),
            quote(warrant["candidate_id"]), quote(warrant["decision_hash"]),
            quote(warrant["state"]), quote(json.dumps(warrant))), database)

        interrupt_id = "warrant-p7-interrupt"
        interrupt = dict(warrant, warrant_id=interrupt_id)
        sql(port, "INSERT INTO p7_warrants VALUES (%s,%s,%s,decode(%s,'hex'),'ISSUED',%s::JSONB)" % (
            quote(interrupt_id), quote(warrant["task_id"]), quote(warrant["candidate_id"]),
            quote(warrant["decision_hash"]), quote(json.dumps(interrupt))), database)
        consumed_interrupt = sql(
            port, "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
            "UPDATE p7_warrants SET state='CONSUMED' WHERE warrant_id=%s AND state='ISSUED' "
            "RETURNING state;COMMIT;" % quote(interrupt_id), database).stdout
        replay_interrupt = sql(
            port, "UPDATE p7_warrants SET state='CONSUMED' WHERE warrant_id=%s "
            "AND state='ISSUED' RETURNING state" % quote(interrupt_id), database).stdout

        consumed = sql(
            port, "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
            "UPDATE p7_warrants SET state='CONSUMED' WHERE warrant_id=%s AND state='ISSUED' "
            "RETURNING state;COMMIT;" % quote(warrant["warrant_id"]), database).stdout

        for relative, content_hash in alpha["file_hashes"].items():
            blob = safe_target(surviving, "objects/" + content_hash)
            payload = blob.read_bytes()
            if rec.sha256_hex(payload) != content_hash:
                raise rec.RecoveryError(rec.TAMPERED_EVIDENCE)
            write_bytes(successor, relative, payload)

        for relative, content_hash in alpha["file_hashes"].items():
            if rec.sha256_hex(safe_target(successor, relative).read_bytes()) != content_hash:
                raise rec.RecoveryError(rec.TAMPERED_EVIDENCE)

        fresh = subprocess.run(
            ["/usr/bin/env", "python3", str(HERE / "fresh_context.py"),
             str(FIXTURES / "decision-promote.json"),
             str(FIXTURES / "candidate-alpha.json"), str(successor)],
            cwd=HERE, env=env, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=False)
        if fresh.returncode != 0 or '"ok": true' not in fresh.stdout:
            raise rec.RecoveryError("FRESH_CONTEXT_FAILED")

        sql(port,
            "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
            "INSERT INTO p7_recoveries VALUES "
            "('recovery-p7-001',%s,%s,%s,%s::JSONB,decode(%s,'hex'));"
            "INSERT INTO p7_recovery_receipts VALUES "
            "(%s,'recovery-p7-001',%s::JSONB,decode(%s,'hex'));COMMIT;" % (
                quote(decision["task_id"]), quote(decision["candidate_id"]),
                quote(warrant["warrant_id"]), quote(json.dumps(decision)),
                quote(rec.sha256_hex(decision)), quote(promotion["receipt_id"]),
                quote(json.dumps(promotion)), quote(promotion["receipt_hash"])), database)
        sql(port, "INSERT INTO p7_unrecovered_ledgers VALUES "
            "(%s,%s,%s::JSONB,decode(%s,'hex'))" % (
                quote(ledger["ledger_id"]), quote(ledger["task_id"]),
                quote(json.dumps(ledger)), quote(rec.sha256_hex(ledger))), database)

        replay_main = sql(
            port, "UPDATE p7_warrants SET state='CONSUMED' WHERE warrant_id=%s "
            "AND state='ISSUED' RETURNING state" % quote(warrant["warrant_id"]), database).stdout
        counts = last_data(sql(port,
            "SELECT (SELECT count(*) FROM p7_manifests),"
            "(SELECT count(*) FROM p7_loss_receipts),"
            "(SELECT count(*) FROM p7_recovery_candidates),"
            "(SELECT count(*) FROM p7_warrants),"
            "(SELECT count(*) FROM p7_recoveries),"
            "(SELECT count(*) FROM p7_recovery_receipts),"
            "(SELECT count(*) FROM p7_unrecovered_ledgers)", database).stdout)
        interrupt_state = last_data(sql(
            port, "SELECT state FROM p7_warrants WHERE warrant_id=%s" %
            quote(interrupt_id), database).stdout)
        interrupt_recoveries = last_data(sql(
            port, "SELECT count(*) FROM p7_recoveries WHERE warrant_id=%s" %
            quote(interrupt_id), database).stdout)
        main_state = last_data(sql(
            port, "SELECT state FROM p7_warrants WHERE warrant_id=%s" %
            quote(warrant["warrant_id"]), database).stdout)
        sql(port, f"DROP DATABASE {database} CASCADE")

        return {
            "label": label,
            "active_files_after_loss": tree_files(active),
            "successor_files": tree_files(successor),
            "selected_candidate": decision["candidate_id"],
            "fresh_context": json.loads(fresh.stdout),
            "consume_main": "CONSUMED" in consumed,
            "consume_interrupt": "CONSUMED" in consumed_interrupt,
            "replay_main_empty": "CONSUMED" not in replay_main,
            "replay_interrupt_empty": "CONSUMED" not in replay_interrupt,
            "main_state": main_state,
            "interrupt_state": interrupt_state,
            "interrupt_recoveries": interrupt_recoveries,
            "counts": counts,
            "unrecovered": ledger["unrecovered_items"],
        }
    finally:
        if owned_process is not None and owned_process.poll() is None:
            stop_owned(owned_process)
        if database_process is not None:
            database_process.terminate()
            try:
                database_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                database_process.kill()
                database_process.wait(timeout=5)
        if log_handle is not None:
            log_handle.close()
        shutil.rmtree(root)


if __name__ == "__main__":
    outputs = [trial("p7-trial-a", 29267, 8391),
               trial("p7-trial-b", 29268, 8392)]
    comparable = [{key: value for key, value in item.items() if key != "label"}
                  for item in outputs]
    assert comparable[0] == comparable[1], comparable
    assert all(
        item["active_files_after_loss"] == []
        and item["successor_files"] == ["docs/notes.md", "src/feature.py"]
        and item["selected_candidate"] == "cand-p7-alpha"
        and item["fresh_context"] == {"ok": True, "reason": "FRESH_CONTEXT_PASS"}
        and item["consume_main"] and item["consume_interrupt"]
        and item["replay_main_empty"] and item["replay_interrupt_empty"]
        and item["main_state"] == "CONSUMED"
        and item["interrupt_state"] == "CONSUMED"
        and item["interrupt_recoveries"] == "0"
        and item["counts"] == "1\t1\t2\t2\t1\t1\t1"
        for item in outputs), outputs
    print(json.dumps(outputs, sort_keys=True, separators=(",", ":")))
