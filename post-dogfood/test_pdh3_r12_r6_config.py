from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_r6_config_tested", HERE / "pdh3_r12_r6_config.py"
)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class R6ConfigTests(unittest.TestCase):
    def test_rejects_lifetime_over_ten_hours(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            files = {}
            for name in ("runpodctl", "packet", "amendment", "envelope", "judge", "archive", "receipt"):
                path = root / name
                path.write_bytes(name.encode())
                files[name] = path
            now = datetime.now(timezone.utc).replace(microsecond=0)
            body = {
                "version": "ck-pdh3-r12-r6-config-v2",
                "root": str(root), "runtime": str(root / "runtime"),
                "runpodctl": str(files["runpodctl"]),
                "runpodctl_sha256": module.sha256(files["runpodctl"]),
                "packet": str(files["packet"]),
                "packet_sha256": module.sha256(files["packet"]),
                "platform_amendment": str(files["amendment"]),
                "platform_amendment_sha256": module.sha256(files["amendment"]),
                "authorization_envelope": str(files["envelope"]),
                "authorization_envelope_sha256": module.sha256(files["envelope"]),
                "judge_raw": str(files["judge"]),
                "judge_raw_sha256": module.sha256(files["judge"]),
                "campaign_id": "ck-pdh3-r12-preflight-r6-test",
                "launch_mode": "FIXED_WINDOW",
                "image": "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
                "launch_start_utc": now.isoformat().replace("+00:00", "Z"),
                "launch_end_utc": (now + timedelta(minutes=45)).isoformat().replace("+00:00", "Z"),
                "stop_utc": (now + timedelta(hours=9)).isoformat().replace("+00:00", "Z"),
                "terminate_utc": (now + timedelta(hours=10, seconds=1)).isoformat().replace("+00:00", "Z"),
                "max_attempts": 1, "rate_ceiling_usd_per_hour": 0.99,
                "aggregate_cost_ceiling_usd": 12.0,
                "archive": str(files["archive"]),
                "archive_sha256": module.sha256(files["archive"]),
                "bundle_receipt": str(files["receipt"]),
                "bundle_receipt_sha256": module.sha256(files["receipt"]),
                "tracer_binary_sha256": "a" * 64,
            }
            config = root / "config.json"
            config.write_text(json.dumps(body))
            with self.assertRaisesRegex(module.R6ConfigError, "PAID_LIFETIME_TOO_LONG"):
                module.load(config)

            body["terminate_utc"] = (now + timedelta(hours=9, minutes=30)).isoformat().replace("+00:00", "Z")
            body["max_attempts"] = 3
            retry_config = root / "retry-config.json"
            retry_config.write_text(json.dumps(body))
            with self.assertRaisesRegex(module.R6ConfigError, "MAX_ATTEMPTS_INVALID"):
                module.load(retry_config)

            body["version"] = "ck-pdh3-r12-r6-config-v3"
            body["data_center_ids"] = ["US-MO-1"]
            accepted = root / "accepted-retry-config.json"
            accepted.write_text(json.dumps(body))
            self.assertEqual(module.load(accepted)["max_attempts"], 3)

            body["data_center_ids"] = ["US-NC-1"]
            wrong_dc = root / "wrong-dc-config.json"
            wrong_dc.write_text(json.dumps(body))
            with self.assertRaisesRegex(module.R6ConfigError, "DATA_CENTER_IDS_INVALID"):
                module.load(wrong_dc)

            body["version"] = "ck-pdh3-r12-r6-config-v4"
            body["data_center_ids"] = [
                "EU-NL-1", "EUR-IS-2", "US-IL-1", "US-MO-1", "US-NC-1",
                "US-TX-3", "US-TX-4",
            ]
            body["graphql_url"] = "https://api.runpod.io/graphql"
            body["min_vcpu_count"] = 24
            graphql_config = root / "graphql-config.json"
            graphql_config.write_text(json.dumps(body))
            loaded = module.load(graphql_config)
            self.assertEqual(loaded["min_vcpu_count"], 24)

            body["min_vcpu_count"] = 16
            weak = root / "weak-graphql-config.json"
            weak.write_text(json.dumps(body))
            with self.assertRaisesRegex(module.R6ConfigError, "MIN_VCPU_COUNT_INVALID"):
                module.load(weak)

    def test_runtime_file_accepts_nested_receipt_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary) / "runtime"
            target = runtime / "attempt-01" / "ssh-config"
            target.parent.mkdir(parents=True)
            target.write_text("Host worker\n", encoding="utf-8")
            self.assertEqual(
                module.require_runtime_file(runtime, str(target), "SSH_CONFIG"),
                target.resolve(),
            )

    def test_runtime_file_rejects_outside_path_and_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = root / "runtime"
            runtime.mkdir()
            outside = root / "outside"
            outside.write_text("outside\n", encoding="utf-8")
            with self.assertRaisesRegex(
                module.R6ConfigError, "SSH_CONFIG_OUTSIDE_RUNTIME"
            ):
                module.require_runtime_file(runtime, str(outside), "SSH_CONFIG")
            link = runtime / "ssh-config"
            link.symlink_to(outside)
            with self.assertRaisesRegex(
                module.R6ConfigError, "SSH_CONFIG_FILE_INVALID"
            ):
                module.require_runtime_file(runtime, str(link), "SSH_CONFIG")

    def test_remote_smoke_receipt_validates_hash_archive_and_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "remote-smoke.json"
            check = {
                "path": "synthetic", "status": "PASS", "returncode": 0,
                "timeout_seconds": None, "stdout_bytes": 0,
                "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "stdout_tail": "", "stderr_bytes": 0,
                "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "stderr_tail": "",
            }
            body = {
                "version": "ck-pdh3-extracted-bundle-smoke-v3",
                "archive_sha256": "a" * 64,
                "compile": check,
                "tests": [dict(check, path=f"synthetic-{index}") for index in range(13)],
                "failed_checks": [],
                "diagnostic_tail_bytes_max": 4096,
                "green": True,
            }
            body["smoke_sha256"] = hashlib.sha256(
                json.dumps(
                    body,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                ).encode()
            ).hexdigest()
            path.write_text(json.dumps(body), encoding="utf-8")
            self.assertTrue(module.validate_remote_smoke_receipt(path, "a" * 64)["green"])
            tampered = json.loads(path.read_text())
            tampered["green"] = False
            path.write_text(json.dumps(tampered))
            with self.assertRaisesRegex(module.R6ConfigError, "HASH_INVALID"):
                module.validate_remote_smoke_receipt(path, "a" * 64)


if __name__ == "__main__":
    unittest.main()
