#!/usr/bin/env python3
"""Two clean-root CockroachDB trials for P5 advisory persistence."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from manifest import LANES, aggregate, load_canonical, sha256_hex

BASE = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
BIN = next(path for path in BASE.glob("p2-cleanroom/vendor/**/cockroach")
           if "darwin" in str(path))
P3_MIGRATION = BASE / "p3-ledger/migrations/001_ledger.sql"
P5_MIGRATION = HERE / "migrations/001_lanes.sql"
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


def fixtures() -> tuple[dict[str, dict], list[dict]]:
    manifests = {lane: load_canonical(str(FIXTURES / f"manifest_{lane}.json"))
                 for lane in LANES}
    results = [load_canonical(str(FIXTURES / f"result_{lane}.json"))
               for lane in LANES]
    return manifests, results


def trial(label: str, port: int, http_port: int) -> dict[str, object]:
    root = Path(tempfile.mkdtemp(prefix=f"{label}.", dir=HERE))
    fake_home = root / "empty-home"
    fake_home.mkdir()
    log_path = root / "cockroach.log"
    env = os.environ.copy()
    env["HOME"] = str(fake_home)
    log_handle = None
    process = None
    try:
        log_handle = log_path.open("w", encoding="utf-8")
        process = subprocess.Popen(
            [str(BIN), "start-single-node", "--insecure", f"--store={root / 'store'}",
             f"--listen-addr=127.0.0.1:{port}",
             f"--http-addr=127.0.0.1:{http_port}"],
            stdout=log_handle, stderr=subprocess.STDOUT, env=env)
        for _ in range(30):
            if sql(port, "SELECT 1", expect_ok=False).returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("CockroachDB did not become ready")

        database = "p5lanes"
        sql(port, f"CREATE DATABASE {database}")
        apply_file(port, database, P3_MIGRATION)
        apply_file(port, database, P5_MIGRATION)

        declared = {"scope": "synthetic-p5", "state": "advisory-only"}
        state_hash = sha256_hex(declared)
        sql(port,
            "INSERT INTO tasks VALUES "
            "('task-p5-synthetic','p5-v1',decode(%s,'hex'),%s::JSONB,"
            "'2026-07-25 00:00:00+00')" %
            (quote(state_hash), quote(json.dumps(declared))), database)
        prefix = [{"event_id": "synthetic-parent", "sequence": 0}]
        parent_receipt = sha256_hex({"candidate": "cand-p5-synthetic"})
        sql(port,
            "INSERT INTO candidates VALUES "
            "('cand-p5-synthetic','task-p5-synthetic','synthetic-parent',"
            "%s::JSONB,decode(%s,'hex'),decode(%s,'hex'),'policy-p5-v1',"
            "'REFUSE','QUORUM_MISSING','synthetic','2026-07-25 00:00:01+00')" %
            (quote(json.dumps(prefix)), quote(state_hash), quote(parent_receipt)),
            database)

        manifests, results = fixtures()
        advisory, reason = aggregate(results, manifests)
        if reason != "OK" or advisory is None:
            raise RuntimeError(f"fixture aggregate failed: {reason}")

        for offset, lane in enumerate(LANES, start=2):
            manifest = manifests[lane]
            result = next(item for item in results if item["lane"] == lane)
            provenance = result["provenance"]
            sql(port,
                "INSERT INTO p5_lane_manifests VALUES "
                "(%s,%s,%s,%s,%s,%s::JSONB,decode(%s,'hex'),%s)" % (
                    quote(manifest["manifest_id"]), quote(lane),
                    quote(provenance["task_id"]), quote(provenance["candidate_id"]),
                    quote(manifest["policy_version"]), quote(json.dumps(manifest)),
                    quote(sha256_hex(manifest)),
                    quote(f"2026-07-25 00:00:{offset:02d}+00")), database)
            sql(port,
                "INSERT INTO p5_lane_results VALUES "
                "(%s,%s,%s,%s,%s,decode(%s,'hex'),%s,decode(%s,'hex'),%s,%s,"
                "%s::JSONB,decode(%s,'hex'),%d,%d,%s::JSONB,decode(%s,'hex'),"
                "'ADVISORY',%s::JSONB,decode(%s,'hex'),%s)" % (
                    quote(result["result_id"]), quote(result["manifest_id"]),
                    quote(lane), quote(provenance["task_id"]),
                    quote(provenance["candidate_id"]),
                    quote(provenance["trajectory_hash"]),
                    quote(provenance["policy_version"]),
                    quote(provenance["prompt_hash"]), quote(provenance["route"]),
                    quote(provenance["served_model"]), quote(json.dumps(result["output"])),
                    quote(provenance["output_hash"]), provenance["retry_count"],
                    provenance["timeout_ms"], quote(json.dumps(result["dissent"])),
                    quote(provenance["receipt_hash"]), quote(json.dumps(result)),
                    quote(sha256_hex(result)),
                    quote(f"2026-07-25 00:01:{offset:02d}+00")), database)

        duplicate = sql(
            port,
            "INSERT INTO p5_lane_results SELECT 'duplicate-result',manifest_id,"
            "lane_id,task_id,candidate_id,trajectory_hash,policy_version,prompt_hash,"
            "route,served_model,output_json,output_hash,retry_count,timeout_ms,"
            "dissent_json,receipt_hash,advisory_verdict,result_json,result_hash,created_at "
            "FROM p5_lane_results WHERE lane_id='syntax_structure'",
            database, expect_ok=False)
        counts = sql(
            port,
            "SELECT (SELECT count(*) FROM p5_lane_manifests),"
            "(SELECT count(*) FROM p5_lane_results),"
            "(SELECT count(*) FROM p5_lane_results WHERE advisory_verdict='ADVISORY')",
            database).stdout.strip().splitlines()[-1].strip()
        hashes = sql(
            port,
            "SELECT encode(result_hash,'hex') FROM p5_lane_results ORDER BY lane_id",
            database).stdout
        returned_hashes = sorted(line.strip() for line in hashes.splitlines()
                                 if len(line.strip()) == 64)
        expected_hashes = sorted(sha256_hex(item) for item in results)
        sql(port, f"DROP DATABASE {database} CASCADE")
        return {"label": label, "aggregate_hash": sha256_hex(advisory),
                "counts": counts, "duplicate_rejected": duplicate.returncode != 0,
                "hashes_match": returned_hashes == expected_hashes,
                "lanes": list(LANES)}
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if log_handle is not None:
            log_handle.close()
        shutil.rmtree(root)


if __name__ == "__main__":
    outputs = [trial("p5-db-a", 27267, 8191), trial("p5-db-b", 27268, 8192)]
    comparable = [{key: value for key, value in item.items() if key != "label"}
                  for item in outputs]
    assert comparable[0] == comparable[1], comparable
    assert all(item["duplicate_rejected"] and item["hashes_match"]
               for item in outputs), outputs
    print(json.dumps(outputs, sort_keys=True, separators=(",", ":")))
