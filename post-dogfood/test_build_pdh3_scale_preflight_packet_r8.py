from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_preflight_r8_tested", HERE / "build_pdh3_scale_preflight_packet_r8.py"
)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


NOW = datetime(2026, 8, 1, 0, 0, tzinfo=timezone.utc)


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def finalize_manifest(body: dict[str, object]) -> dict[str, object]:
    return {**body, "manifest_sha256": sha(canonical(body))}


def finalize_record(body: dict[str, object], hash_field: str) -> dict[str, object]:
    return {**body, hash_field: sha(canonical(body))}


class R8PreflightPacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="pdh3-preflight-r8-test.")
        self.root = Path(self.temporary.name)
        self.runtime = self.root / ".runtime-r8"
        self.runtime.mkdir()

        for relative in builder.MANDATORY_SOURCES:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative == "post-dogfood/pdh3_scale_contract.py":
                shutil.copyfile(HERE / "pdh3_scale_contract.py", path)
            elif relative == "PDH_3_R8_VALIDATION_BOUNDARY_DISCLOSURE.md":
                shutil.copyfile(HERE.parent / relative, path)
            else:
                symbols = sorted(
                    {
                        symbol
                        for _gate, _state, implementation, tests, _pointers
                        in builder.CHECKLIST_EVIDENCE
                        for source, symbol in implementation + tests
                        if source == relative
                    }
                )
                prefix = "MAX_TOKENS = 256\n\n" if relative == "p9-cloud/context_vector.py" else ""
                path.write_text(
                    prefix
                    + f"# deterministic fixture for {relative}\n"
                    + "".join(f"def {symbol}():\n    pass\n\n" for symbol in symbols),
                    encoding="utf-8",
                )

        self.vendor_fixtures = {
            (
                "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
                "cockroach-v26.2.3.linux-amd64/cockroach"
            ): b"fixture-cockroach-binary",
            (
                "p2-cleanroom/vendor/ubuntu-noble-strace/"
                "strace_6.8-0ubuntu2_amd64.deb"
            ): b"fixture-strace-deb",
            (
                "p2-cleanroom/vendor/ubuntu-noble-strace/"
                "libunwind8_1.6.2-3build1_amd64.deb"
            ): b"fixture-libunwind-deb",
        }
        for relative, raw in self.vendor_fixtures.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        contract_fixture = self.root / "post-dogfood/pdh3_scale_contract.py"
        with contract_fixture.open("a", encoding="utf-8") as handle:
            handle.write(
                "\nSTRACE_DEB_SHA256 = "
                + repr(sha(self.vendor_fixtures[next(
                    key for key in self.vendor_fixtures if key.endswith("strace_6.8-0ubuntu2_amd64.deb")
                )]))
                + "\nLIBUNWIND8_DEB_SHA256 = "
                + repr(sha(self.vendor_fixtures[next(
                    key for key in self.vendor_fixtures if key.endswith("libunwind8_1.6.2-3build1_amd64.deb")
                )]))
                + "\nSTRACE_BINARY_SHA256 = "
                + repr(sha(b"fixture-extracted-strace-binary"))
                + "\n"
            )

        local_artifact = self.runtime / "local" / "result.json"
        local_artifact.parent.mkdir()
        local_artifact.write_bytes(canonical({"status": "GREEN", "checks": 42}))
        local_body = {
            "version": "fixture-local-tests-v1",
            "status": "GREEN",
            "reduced_scale": True,
            "tests_passed": 42,
            "isolated_smoke_contract": {
                "packet": {
                    "path": local_artifact.relative_to(self.root).as_posix(),
                    "bytes": local_artifact.stat().st_size,
                    "sha256": sha(local_artifact.read_bytes()),
                },
                "fresh_generated_root_required": True,
                "isolated_home_required": True,
                "diagnostic_reporting_disabled_required": True,
            },
            "isolated_smoke_observed_result": {
                "status": "GREEN",
                "synthetic_only": True,
                "credentials_used": False,
                "external_cloud_calls": 0,
                "cluster_topology": "THREE_LOCAL_LOOPBACK_NODES_DISPOSABLE_ROOT",
                "measured_seconds": 60.0,
                "generated_root_removed": True,
                "nodes_stopped": True,
                "ports_closed": True,
                "open_ports": [],
            },
            "files": [
                {
                    "path": local_artifact.relative_to(self.root).as_posix(),
                    "bytes": local_artifact.stat().st_size,
                    "sha256": sha(local_artifact.read_bytes()),
                }
            ],
        }
        self.local_manifest = finalize_manifest(local_body)
        self.local_manifest_path = self.runtime / "local-test-manifest.json"
        self.local_manifest_path.write_bytes(canonical(self.local_manifest))

        history_entries = []
        paid_seconds = (319, 663, 865, 572, 43, 38, 3_184)
        for number in range(1, 8):
            artifact = self.runtime / "history" / f"attempt-{number:02d}.json"
            artifact.parent.mkdir(exist_ok=True)
            artifact.write_bytes(
                canonical({"attempt": number, "status": "BLOCKED", "pod_deleted": True})
            )
            history_entries.append(
                {
                    "attempts": [number],
                    "classification": "final_state" if number == 7 else "summary_receipt",
                    "path": artifact.relative_to(self.root).as_posix(),
                    "bytes": artifact.stat().st_size,
                    "sha256": sha(artifact.read_bytes()),
                }
            )
        final_archive = self.runtime / "history" / "attempt-07-evidence.tgz"
        final_archive.write_bytes(b"failed-attempt-07-evidence")
        history_entries.append(
            {
                "attempts": [7],
                "classification": "final_evidence_archive",
                "path": final_archive.relative_to(self.root).as_posix(),
                "bytes": final_archive.stat().st_size,
                "sha256": sha(final_archive.read_bytes()),
            }
        )
        disk_rate = 0.10
        active_rate = 0.99 + 250 * disk_rate / (30 * 24)
        prior_cost = sum(paid_seconds) / 3600 * active_rate
        replacement_cost = 28 * active_rate
        aggregate_cost = prior_cost + replacement_cost
        aggregate_ceiling = 35.0
        cost_artifact = self.runtime / "history" / "cost-envelope.md"
        cost_artifact.write_text(
            "# Fixture cost envelope\n\n"
            "- `STATUS`: `CONSERVATIVE_UPPER_BOUND_NOT_PROVIDER_INVOICE`\n"
            f"- `DISK_RATE_USD_GB_30_DAY_MONTH`: `{disk_rate}`\n"
            f"- `TOTAL_ACTIVE_RATE_UPPER_USD_HOUR`: `{active_rate}`\n"
            f"- `PRIOR_ACTIVE_SECONDS_UPPER`: `{sum(paid_seconds)}`\n"
            f"- `PRIOR_COST_UPPER_USD`: `{prior_cost}`\n"
            f"- `REPLACEMENT_28_HOUR_COST_UPPER_USD`: `{replacement_cost}`\n"
            f"- `AGGREGATE_COST_UPPER_USD`: `{aggregate_cost}`\n"
            f"- `AUTHORIZED_AGGREGATE_CEILING_USD`: `{aggregate_ceiling}`\n"
            f"- `MINIMUM_REMAINING_HEADROOM_USD`: `{aggregate_ceiling - aggregate_cost}`\n",
            encoding="utf-8",
        )
        history_entries.append(
            {
                "attempts": list(range(1, 8)),
                "classification": "prior_attempt_cost_envelope",
                "path": cost_artifact.relative_to(self.root).as_posix(),
                "bytes": cost_artifact.stat().st_size,
                "sha256": sha(cost_artifact.read_bytes()),
            }
        )
        history_entries.sort(
            key=lambda row: (row["attempts"], row["classification"], row["path"])
        )
        final_state_entry = next(
            row for row in history_entries if row["classification"] == "final_state"
        )
        final_archive_entry = next(
            row
            for row in history_entries
            if row["classification"] == "final_evidence_archive"
        )
        history_body = {
            "version": "ck-pdh3-attempt-history-manifest-v1",
            "attempts_covered": list(range(1, 8)),
            "binding_only": True,
            "raw_evidence_embedded": False,
            "credential_material_copied": False,
            "entries": history_entries,
            "entry_count": len(history_entries),
            "history_set_sha256": sha(canonical(history_entries)),
            "attempt_07_final_state_sha256": final_state_entry["sha256"],
            "attempt_07_final_evidence_archive_sha256": final_archive_entry["sha256"],
        }
        self.history_manifest = finalize_record(history_body, "history_manifest_sha256")
        self.history_manifest_path = self.runtime / "prior-history-manifest.json"
        self.history_manifest_path.write_bytes(canonical(self.history_manifest))

        attempt_dir = self.runtime / "attempt-08"
        attempt_dir.mkdir()
        attempt_payloads: dict[str, bytes] = {
            "summary_receipt": b"STATUS=BLOCKED_PREMEASUREMENT\nBLOCKER=OUTPUT_ALREADY_EXISTS\n",
            "preflight_packet": b"fixture packet",
            "preflight_bindings": canonical({"fixture": "bindings"}),
            "runtime_commands": canonical({"fixture": "commands"}),
            "final_state": canonical(
                {"version": "ck-pdh3-closeout-summary-v2", "result.json": None}
            ),
            "final_evidence_archive": b"fixture archive",
            "final_evidence_sidecar": b"fixture archive hash",
            "supervisor_log": b'{"event":"DELETE_ATTEMPT"}\n',
            "lifecycle_log": b'{"event":"PROVIDER_RETRY"}\n',
            "provider_exact_absence": canonical(
                {
                    "returncode": 1,
                    "stdout": "",
                    "stderr": (
                        '{"error":"api error: {\\"error\\":\\"pod not found\\",'
                        '\\"status\\":404}\\n (status 404)"}\n'
                        "Usage:\n"
                        "  runpodctl pod get <pod-id> [flags]\n\n"
                        "Flags:\n"
                        "  -h, --help                     help for get\n"
                        "      --include-machine          include machine info\n"
                        "      --include-network-volume   include network volume info\n\n"
                        "Global Flags:\n"
                        "  -o, --output string   output format (json, yaml) (default \"json\")\n\n"
                        '{"error":"failed to get pod: api error: {"error":"pod not found",'
                        '"status":404}\n (status 404)"}\n'
                    ),
                }
            ),
            "provider_campaign_absence": canonical(
                {"returncode": 0, "stdout": "[]", "stderr": ""}
            ),
        }
        attempt_entries: list[dict[str, object]] = []
        for classification, raw in attempt_payloads.items():
            path = attempt_dir / f"{classification}.bin"
            if classification in {"final_state", "provider_exact_absence", "provider_campaign_absence"}:
                path = path.with_suffix(".json")
            path.write_bytes(raw)
            attempt_entries.append(
                {
                    "classification": classification,
                    "path": path.relative_to(self.root).as_posix(),
                    "bytes": len(raw),
                    "sha256": sha(raw),
                }
            )
        attempt_body = {
            "version": "ck-pdh3-attempt-08-manifest-v1",
            "attempt": 8,
            "status": "BLOCKED_PREMEASUREMENT",
            "campaign_id": "ck-pdh3-scale-r8-relaunch",
            "pod_name": "ck-pdh3-scale-r8-relaunch-01",
            "pod_id": "eo9deg7xgys6a8",
            "packet_sha256": "0" * 64,
            "measured_clock_started": False,
            "workload_executed": False,
            "blocker": "OUTPUT_ALREADY_EXISTS",
            "provider_resource_status": "DELETED",
            "frozen_teardown_proof_status": "BLOCKED_PROVIDER_RENDERING_UNSUPPORTED",
            "active_seconds_upper": 349,
            "active_rate_usd_hour_upper": 1.0,
            "attempt_cost_usd_upper": 349 / 3_600,
            "exact_provider_charge_available": False,
            "binding_only": True,
            "raw_evidence_embedded": False,
            "credential_material_copied": False,
            "entries": attempt_entries,
            "entry_count": len(attempt_entries),
            "evidence_set_sha256": sha(canonical(attempt_entries)),
        }
        self.attempt_08_manifest = finalize_manifest(attempt_body)
        self.attempt_08_manifest_path = self.runtime / "attempt-08-manifest.json"
        self.attempt_08_manifest_path.write_bytes(canonical(self.attempt_08_manifest))

        contract_module = builder._load_contract(self.root)
        arguments = {
            "duration_seconds": contract_module.MEASURED_SECONDS,
            "checkpoint_seconds": contract_module.CHECKPOINT_SECONDS,
            "tasks": contract_module.TASKS,
            "events_per_task": contract_module.EVENTS_PER_TASK,
            "receipts_per_task": contract_module.RECEIPTS_PER_TASK,
            "vectors": contract_module.VECTORS,
            "max_concurrency": contract_module.MAX_CONCURRENCY,
            "query_duration_seconds": contract_module.QUERY_DURATION_SECONDS,
            "seed_batch_tasks": contract_module.SEED_BATCH_TASKS,
            "setup_timeout_seconds": contract_module.SETUP_TIMEOUT_SECONDS,
            "fault_every_checkpoints": contract_module.FAULT_EVERY_CHECKPOINTS,
            "disk_used_fraction_limit": contract_module.DISK_USED_FRACTION_LIMIT,
            "cache": contract_module.NODE_CACHE,
            "sql_memory": contract_module.NODE_SQL_MEMORY,
            "store_size": None,
        }
        binary = (
            "p2-cleanroom/vendor/cockroach-v26.2.3-linux/"
            "cockroach-v26.2.3.linux-amd64/cockroach"
        )
        strace_deb = (
            "p2-cleanroom/vendor/ubuntu-noble-strace/"
            "strace_6.8-0ubuntu2_amd64.deb"
        )
        libunwind_deb = (
            "p2-cleanroom/vendor/ubuntu-noble-strace/"
            "libunwind8_1.6.2-3build1_amd64.deb"
        )
        tracer_root = "__TRACER_ROOT__"
        tracer_binary = tracer_root + "/usr/bin/strace"
        tracer_library_path = (
            tracer_root + "/usr/lib/x86_64-linux-gnu:"
            + tracer_root
            + "/lib/x86_64-linux-gnu"
        )
        tracer_setup = [
            ["dpkg-deb", "--extract", libunwind_deb, tracer_root],
            ["dpkg-deb", "--extract", strace_deb, tracer_root],
        ]
        launch_environment = {
            "PDH3_PACKET_SHA256": "__FROZEN_PACKET_SHA256__",
            "LD_LIBRARY_PATH": tracer_library_path,
        }
        controller_argv = [
            "python3",
            "post-dogfood/run_pdh3_scale_campaign.py",
            "--binary",
            binary,
            "--packet",
            "__FROZEN_PACKET__",
            "--output",
            "__REMOTE_EVIDENCE_ROOT__",
            "--campaign-id",
            "__IMMUTABLE_CAMPAIGN_ID__",
            "--production",
            "--duration-seconds",
            str(arguments["duration_seconds"]),
            "--checkpoint-seconds",
            str(arguments["checkpoint_seconds"]),
            "--tasks",
            str(arguments["tasks"]),
            "--events-per-task",
            str(arguments["events_per_task"]),
            "--receipts-per-task",
            str(arguments["receipts_per_task"]),
            "--vectors",
            str(arguments["vectors"]),
            "--max-concurrency",
            str(arguments["max_concurrency"]),
            "--query-duration-seconds",
            str(arguments["query_duration_seconds"]),
            "--seed-batch-tasks",
            str(arguments["seed_batch_tasks"]),
            "--setup-timeout-seconds",
            str(arguments["setup_timeout_seconds"]),
            "--fault-every-checkpoints",
            str(arguments["fault_every_checkpoints"]),
            "--disk-used-fraction-limit",
            str(arguments["disk_used_fraction_limit"]),
            "--cache",
            str(arguments["cache"]),
            "--sql-memory",
            str(arguments["sql_memory"]),
        ]
        traced_argv = [
            "python3",
            "post-dogfood/run_pdh3_traced.py",
            "--trace-prefix",
            "__REMOTE_TRACE_PREFIX__",
            "--receipt",
            "__REMOTE_NETWORK_RECEIPT__",
            "--packet-sha256",
            "__FROZEN_PACKET_SHA256__",
            "--strace",
            tracer_binary,
            "--strace-sha256",
            contract_module.STRACE_BINARY_SHA256,
            "--max-trace-bytes",
            str(contract_module.TRACE_BYTES_LIMIT),
            "--",
            *controller_argv,
        ]
        launch_body = {
            "version": "ck-pdh3-production-launch-binding-v3",
            "argument_bindings": arguments,
            "launch_environment_template": launch_environment,
            "tracer_artifact_bindings": [
                {"path": strace_deb, "sha256": contract_module.STRACE_DEB_SHA256},
                {"path": libunwind_deb, "sha256": contract_module.LIBUNWIND8_DEB_SHA256},
            ],
            "tracer_setup_argv_templates": tracer_setup,
            "tracer_binary_template": tracer_binary,
            "tracer_binary_sha256": contract_module.STRACE_BINARY_SHA256,
            "tracer_library_path_template": tracer_library_path,
            "controller_argv_template": controller_argv,
            "controller_argv_template_sha256": sha(canonical(controller_argv)),
            "traced_argv_template": traced_argv,
            "traced_argv_template_sha256": sha(canonical(traced_argv)),
            "launch_environment_template_sha256": sha(canonical(launch_environment)),
            "tracer_setup_template_sha256": sha(canonical(tracer_setup)),
            "required_remote_setup_order": [
                "VERIFY_BUNDLED_DEB_HASHES",
                "EXTRACT_LIBUNWIND_WITH_DPKG_DEB",
                "EXTRACT_STRACE_WITH_DPKG_DEB",
                "VERIFY_EXTRACTED_STRACE_BINARY_HASH",
                "SET_EXACT_LAUNCH_ENVIRONMENT",
                "EXECUTE_TRACED_ARGV_WITHOUT_SHELL",
            ],
            "store_size_flag": "ABSENT",
            "shell_interpolation": False,
        }
        launch = finalize_record(launch_body, "launch_sha256")
        host_rows = []
        for relative in (
            "post-dogfood/supervise_pdh3_scale_campaign.py",
            "post-dogfood/test_supervise_pdh3_scale_campaign.py",
            "s2-soak/lifecycle_guard.py",
            "s2-soak/test_lifecycle_guard.py",
        ):
            raw = (self.root / relative).read_bytes()
            host_rows.append(
                {"path": relative, "bytes": len(raw), "sha256": sha(raw), "mode": 0o644}
            )
        host_body = {
            "version": "ck-pdh3-host-control-plane-bindings-v1",
            "archive_transfer": False,
            "reason": "HOST_CONTROL_PLANE_NOT_REQUIRED_BY_REMOTE_WORKLOAD",
            "files": host_rows,
            "file_count": len(host_rows),
            "source_set_sha256": sha(canonical(host_rows)),
        }
        host_bindings = finalize_record(host_body, "bindings_sha256")
        self.archive = self.runtime / "pdh3-scale-bundle-r8.tgz"
        self.archive.write_bytes(b"deterministic-r8-archive")
        bundle_rows = []
        for relative in (*builder.REMOTE_BUNDLE_REQUIRED, *self.vendor_fixtures):
            raw = (self.root / relative).read_bytes()
            bundle_rows.append(
                {"path": relative, "bytes": len(raw), "sha256": sha(raw), "mode": 0o644}
            )
        bundle_body = {
            "version": "ck-pdh3-scale-bundle-manifest-v2",
            "credential_free": True,
            "synthetic_only": True,
            "files": bundle_rows,
            "file_count": len(bundle_rows),
            "source_set_sha256": sha(canonical(bundle_rows)),
            "history_member": "PDH3_ATTEMPT_HISTORY_MANIFEST.json",
            "history_manifest_sha256": self.history_manifest["history_manifest_sha256"],
            "history_raw_evidence_embedded": False,
            "host_control_plane_transferred": False,
            "host_only_bindings_sha256": host_bindings["bindings_sha256"],
            "production_launch": launch,
        }
        self.bundle_manifest = finalize_manifest(bundle_body)
        self.bundle_manifest_path = self.runtime / "bundle-manifest.json"
        self.bundle_manifest_path.write_bytes(canonical(self.bundle_manifest))
        duplicate_source = self.runtime / "post-dogfood/pdh3_scale_contract.py"
        duplicate_source.parent.mkdir(parents=True, exist_ok=True)
        duplicate_source.write_bytes(
            (self.root / "post-dogfood/pdh3_scale_contract.py").read_bytes()
        )
        verification_body = {
            "version": "ck-pdh3-extracted-bundle-verification-v2",
            "exact_member_set": True,
            "regular_files_only": True,
            "source_bytes_match_current": True,
            "source_count": len(bundle_rows),
            "member_count": len(bundle_rows) + 2,
            "verified_members_sha256": "0" * 64,
        }
        verification = finalize_record(verification_body, "verification_sha256")
        receipt_body = {
            "version": "ck-pdh3-scale-bundle-receipt-v2",
            "archive": self.archive.name,
            "archive_bytes": self.archive.stat().st_size,
            "archive_sha256": sha(self.archive.read_bytes()),
            "manifest": self.bundle_manifest,
            "history_manifest": self.history_manifest,
            "host_only_bindings": host_bindings,
            "archive_verification": verification,
        }
        self.bundle_receipt = finalize_record(receipt_body, "receipt_sha256")
        self.bundle_receipt_path = self.runtime / "bundle-receipt.json"
        self.bundle_receipt_path.write_bytes(canonical(self.bundle_receipt))

        self.authorization = self.root / "PDH_3_SCALE_AUTHORIZATION_RECEIPT_R1.md"
        self.authorization.write_text(
            "NVIDIA L40S; measured 86,400; paid 100,800; $35.00 replacement; "
            "$38.00 cumulative; $0.99 compute; $1.10 active; 250 GB disposable.\n",
            encoding="utf-8",
        )
        self.runpodctl = self.runtime / "runpodctl"
        self.runpodctl.write_bytes(b"fixture-runpodctl")
        self.runpodctl_version = "fixture-2.7.2"
        self.runpodctl_sha256 = sha(self.runpodctl.read_bytes())
        self.campaign_id = "ck-pdh3-scale-r8"
        self.pod_name = "ck-pdh3-scale-r8-a01"

        observed = "2026-07-31T23:58:00Z"
        self.active_raw_path = self.runtime / "active-raw.json"
        self.active_raw_path.write_bytes(canonical([]))
        active_command = [
            self.runpodctl.resolve().as_posix(),
            "pod",
            "list",
            "--output",
            "json",
        ]
        active_body = {
            "version": "ck-pdh3-runpod-active-inventory-receipt-r8-v1",
            "observed_utc": observed,
            "max_age_seconds": 900,
            "source": "AUTHENTICATED_RUNPODCTL_JSON",
            "command": active_command,
            "command_sha256": sha(canonical(active_command)),
            "runpodctl_version": self.runpodctl_version,
            "runpodctl_sha256": self.runpodctl_sha256,
            "exit_status": 0,
            "shell_interpolation": False,
            "campaign_id": self.campaign_id,
            "raw_response": {
                "path": self.active_raw_path.relative_to(self.root).as_posix(),
                "bytes": self.active_raw_path.stat().st_size,
                "sha256": sha(self.active_raw_path.read_bytes()),
            },
            "parsed_response_sha256": sha(canonical([])),
            "inventory": [],
        }
        self.active_receipt = finalize_record(active_body, "receipt_sha256")
        self.active_path = self.runtime / "active.json"
        self.active_path.write_bytes(canonical(self.active_receipt))

        gpu_raw = [
            {
                "available": True,
                "communityCloud": False,
                "displayName": "L40S",
                "gpuId": "NVIDIA L40S",
                "memoryInGb": 48,
                "secureCloud": True,
                "stockStatus": "High",
            }
        ]
        datacenter_raw = [
            {
                "datacenterId": "fixture-secure",
                "secureCloud": True,
                "availableGpuIds": ["NVIDIA L40S"],
            }
        ]
        self.gpu_raw_path = self.runtime / "gpu-raw.json"
        self.gpu_raw_path.write_bytes(canonical(gpu_raw))
        self.datacenter_raw_path = self.runtime / "datacenter-raw.json"
        self.datacenter_raw_path.write_bytes(canonical(datacenter_raw))
        self.pricing_raw_path = self.runtime / "pricing-raw.txt"
        self.pricing_raw_path.write_text(
            "Official RunPod pricing: L40S, 48 GB VRAM, 94 GB RAM, "
            "16 vCPU, $0.99/hour; container disk $0.10/GB/month.\n",
            encoding="utf-8",
        )
        self.pricing_page_path = self.runtime / "pricing-page.html"
        self.pricing_page_path.write_text(
            "Official RunPod pricing page: L40S, 48 GB VRAM, 94 GB RAM, "
            "16 vCPU, $0.99/hour; container disk $0.10/GB/month.\n",
            encoding="utf-8",
        )
        page_hash = sha(self.pricing_page_path.read_bytes())
        self.pricing_raw_path.write_text(
            self.pricing_raw_path.read_text(encoding="utf-8")
            + "SOURCE_PAGE_SHA256: "
            + page_hash
            + "\n",
            encoding="utf-8",
        )
        gpu_command = [
            self.runpodctl.resolve().as_posix(),
            "gpu",
            "list",
            "--include-unavailable",
            "--output",
            "json",
        ]
        datacenter_command = [
            self.runpodctl.resolve().as_posix(),
            "datacenter",
            "list",
            "--output",
            "json",
        ]
        pricing_fields = {
            "gpu_id": "NVIDIA L40S",
            "cloud": "SECURE",
            "gpu_count": 1,
            "vram_gb": 48,
            "ram_gb": 94,
            "vcpu": 16,
            "compute_rate_usd_hour": 0.99,
            "container_disk_rate_usd_gb_30_day_month": 0.10,
        }
        storage_rate = 250 * 0.10 / 720
        active_rate = 0.99 + storage_rate
        active_rate_body = {
            "formula": (
                "compute_rate + container_disk_gb * "
                "disk_rate_usd_gb_30_day_month / 720"
            ),
            "compute_rate_usd_hour": 0.99,
            "container_disk_gb": 250,
            "disk_rate_usd_gb_30_day_month": 0.10,
            "month_hours": 720,
            "container_disk_rate_usd_hour": storage_rate,
            "active_rate_usd_hour": active_rate,
            "active_rate_ceiling_usd_hour": 1.10,
        }
        active_rate_derivation = {
            **active_rate_body,
            "derived_fields_sha256": sha(canonical(active_rate_body)),
        }
        self.offer = {
            "gpu_id": "NVIDIA L40S",
            "available": True,
            "cloud": "SECURE",
            "gpu_count": 1,
            "vram_gb": 48,
            "vcpu": 16,
            "ram_gb": 94,
            "compute_rate_usd_hour": 0.99,
            "active_rate_usd_hour": active_rate,
            "offer_id": None,
            "region": None,
        }
        gpu_body = {
            "version": "ck-pdh3-runpod-gpu-pricing-receipt-r8-v1",
            "observed_utc": observed,
            "max_age_seconds": 900,
            "source": "RUNPOD_AUTHENTICATED_INVENTORY_AND_OFFICIAL_PRICING",
            "runpodctl_version": self.runpodctl_version,
            "runpodctl_sha256": self.runpodctl_sha256,
            "gpu_inventory": {
                "observed_utc": observed,
                "max_age_seconds": 900,
                "command": gpu_command,
                "command_sha256": sha(canonical(gpu_command)),
                "exit_status": 0,
                "shell_interpolation": False,
                "raw_response": {
                    "path": self.gpu_raw_path.relative_to(self.root).as_posix(),
                    "bytes": self.gpu_raw_path.stat().st_size,
                    "sha256": sha(self.gpu_raw_path.read_bytes()),
                },
                "parsed_response_sha256": sha(canonical(gpu_raw)),
            },
            "datacenter_inventory": {
                "observed_utc": observed,
                "max_age_seconds": 900,
                "command": datacenter_command,
                "command_sha256": sha(canonical(datacenter_command)),
                "exit_status": 0,
                "shell_interpolation": False,
                "raw_response": {
                    "path": self.datacenter_raw_path.relative_to(self.root).as_posix(),
                    "bytes": self.datacenter_raw_path.stat().st_size,
                    "sha256": sha(self.datacenter_raw_path.read_bytes()),
                },
                "parsed_response_sha256": sha(canonical(datacenter_raw)),
            },
            "official_pricing": {
                "url": builder.RUNPOD_PRICING_URL,
                "observed_utc": observed,
                "max_age_seconds": 900,
                "capture_method": "READ_ONLY_OFFICIAL_PRICING_PAGE",
                "raw_response": {
                    "path": self.pricing_raw_path.relative_to(self.root).as_posix(),
                    "bytes": self.pricing_raw_path.stat().st_size,
                    "sha256": sha(self.pricing_raw_path.read_bytes()),
                },
                "source_page": {
                    "path": self.pricing_page_path.relative_to(self.root).as_posix(),
                    "bytes": self.pricing_page_path.stat().st_size,
                    "sha256": page_hash,
                },
                "source_page_sha256": page_hash,
                "extracted_fields": pricing_fields,
                "derived_fields_sha256": sha(canonical(pricing_fields)),
            },
            "active_rate_derivation": active_rate_derivation,
            "derived_offer": self.offer,
            "derived_offer_sha256": sha(canonical(self.offer)),
        }
        self.gpu_receipt = finalize_record(gpu_body, "receipt_sha256")
        self.gpu_path = self.runtime / "gpu.json"
        self.gpu_path.write_bytes(canonical(self.gpu_receipt))

        stop = datetime(2026, 8, 3, 3, 45, tzinfo=timezone.utc)
        terminate = datetime(2026, 8, 3, 4, 0, tzinfo=timezone.utc)
        self.config = builder.BuildConfig(
            root=self.root,
            runtime_dir=self.runtime,
            campaign_id=self.campaign_id,
            pod_name=self.pod_name,
            launch_window_start="2026-08-02T00:00:00Z",
            launch_window_end="2026-08-02T00:15:00Z",
            stop_after="2026-08-03T03:45:00Z",
            terminate_after="2026-08-03T04:00:00Z",
            stop_epoch=int(stop.timestamp()),
            terminate_epoch=int(terminate.timestamp()),
            active_inventory_json=self.active_path,
            gpu_inventory_json=self.gpu_path,
            bundle_archive=self.archive,
            bundle_receipt_json=self.bundle_receipt_path,
            bundle_manifest_json=self.bundle_manifest_path,
            local_test_manifest_json=self.local_manifest_path,
            prior_attempt_history_manifest_json=self.history_manifest_path,
            attempt_08_manifest_json=self.attempt_08_manifest_path,
            authorization_receipt=self.authorization,
            runpodctl_path=self.runpodctl,
            runpodctl_version=self.runpodctl_version,
            runpodctl_sha256=self.runpodctl_sha256,
            sources=tuple(sorted(builder.MANDATORY_SOURCES)),
            output_packet=self.root / "out" / "PDH_3_SCALE_RUNPOD_PREFLIGHT_PACKET_R8.md",
            output_bindings=self.root / "out" / "PDH_3_SCALE_RUNPOD_PREFLIGHT_BINDINGS_R8.json",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _rewrite_history(self, **updates: object) -> None:
        body = {
            key: value
            for key, value in self.history_manifest.items()
            if key != "manifest_sha256"
        }
        body.update(updates)
        self.history_manifest = finalize_manifest(body)
        self.history_manifest_path.write_bytes(canonical(self.history_manifest))

    def _rewrite_attempt_08(self, **updates: object) -> None:
        body = {
            key: value
            for key, value in self.attempt_08_manifest.items()
            if key != "manifest_sha256"
        }
        body.update(updates)
        self.attempt_08_manifest = finalize_manifest(body)
        self.attempt_08_manifest_path.write_bytes(canonical(self.attempt_08_manifest))

    def _rewrite_local(self, **updates: object) -> None:
        body = {
            key: value for key, value in self.local_manifest.items() if key != "manifest_sha256"
        }
        body.update(updates)
        self.local_manifest = finalize_manifest(body)
        self.local_manifest_path.write_bytes(canonical(self.local_manifest))

    def _rewrite_active(self, inventory: object, **updates: object) -> None:
        self.active_raw_path.write_bytes(canonical(inventory))
        body = {
            key: value
            for key, value in self.active_receipt.items()
            if key != "receipt_sha256"
        }
        body.update(
            {
                "raw_response": {
                    "path": self.active_raw_path.relative_to(self.root).as_posix(),
                    "bytes": self.active_raw_path.stat().st_size,
                    "sha256": sha(self.active_raw_path.read_bytes()),
                },
                "parsed_response_sha256": sha(canonical(inventory)),
                "inventory": inventory,
                **updates,
            }
        )
        self.active_receipt = finalize_record(body, "receipt_sha256")
        self.active_path.write_bytes(canonical(self.active_receipt))

    def _rewrite_gpu(self, **updates: object) -> None:
        body = {
            key: value
            for key, value in self.gpu_receipt.items()
            if key != "receipt_sha256"
        }
        body.update(updates)
        self.gpu_receipt = finalize_record(body, "receipt_sha256")
        self.gpu_path.write_bytes(canonical(self.gpu_receipt))

    def test_successful_build_is_canonical_and_transport_safe(self) -> None:
        result = builder.build(self.config, now=NOW)
        packet = self.config.output_packet.read_text(encoding="utf-8")
        bindings = json.loads(self.config.output_bindings.read_bytes())
        self.assertEqual(result["revision"], "R8")
        self.assertEqual(result["packet_sha256"], sha(packet.encode("utf-8")))
        self.assertEqual(bindings["schedule"]["verifier_executions"], 9_976)
        self.assertEqual(bindings["schedule"]["fault_count"], 24)
        self.assertEqual(bindings["premeasurement"]["epochs"], 3)
        self.assertEqual(bindings["premeasurement"]["concurrency"], 500)
        self.assertEqual(bindings["provider"]["selected_offer"]["vcpu"], 16)
        self.assertIsNone(bindings["provider"]["selected_offer"]["offer_id"])
        self.assertEqual(bindings["identity"]["campaign_id"], self.campaign_id)
        self.assertFalse(bindings["commands"]["shell_interpolation"])
        expected_local_runtime = f".pdh3-runtime/r8-campaigns/{self.campaign_id}"
        self.assertEqual(
            bindings["commands"]["local_runtime_root"], expected_local_runtime
        )
        lifecycle = bindings["commands"]["lifecycle_guard_argv_template"]
        supervisor = bindings["commands"]["supervisor_argv_template"]
        self.assertEqual(
            lifecycle[lifecycle.index("--log") + 1],
            expected_local_runtime + "/lifecycle-guard.ndjson",
        )
        self.assertEqual(
            supervisor[supervisor.index("--ssh-config") + 1],
            expected_local_runtime + "/ssh-config",
        )
        self.assertEqual(
            supervisor[supervisor.index("--retrieval") + 1],
            expected_local_runtime + "/retrieval",
        )
        self.assertEqual(
            supervisor[supervisor.index("--log") + 1],
            expected_local_runtime + "/supervisor.ndjson",
        )
        self.assertNotIn(".pdh3-runtime/r8/", canonical(bindings["commands"]).decode())
        traced = bindings["commands"]["traced_argv_runtime_template"]
        self.assertEqual(
            traced[traced.index("--trace-prefix") + 1],
            f"/workspace/{self.campaign_id}/network-trace",
        )
        self.assertEqual(
            traced[traced.index("--receipt") + 1],
            f"/workspace/{self.campaign_id}/network-receipt.json",
        )
        self.assertEqual(
            bindings["commands"]["remote_evidence_root"],
            f"/workspace/{self.campaign_id}/evidence",
        )
        self.assertEqual(
            bindings["commands"]["child_controller_argv_sha256"],
            sha(canonical(bindings["commands"]["child_controller_argv"])),
        )
        self.assertIn("Reduced and mocked tests", packet)
        self.assertIn("Validation-boundary disclosure", packet)
        self.assertIn("AUDIT_SESSION_ZERO_HOME_MUTATION_NOT_CLAIMED", packet)
        self.assertEqual(
            bindings["validation_boundary_disclosure"]["path"],
            "PDH_3_R8_VALIDATION_BOUNDARY_DISCLOSURE.md",
        )
        self.assertIn("All 9,976 distinct raw verifier receipts", packet)
        self.assertLessEqual(len(packet.encode("utf-8")), 262_144)
        self.assertNotIn("MAX_TOKENS =", packet)
        self.assertIn("Hash-bound load-bearing source manifest", packet)
        self.assertEqual(packet.count('"source_files":'), 1)
        for relative in builder.MANDATORY_SOURCES:
            self.assertIn(f'"path":"{relative}"', packet)
        source_rows = bindings["source_files"]
        self.assertEqual(len(source_rows), len(builder.MANDATORY_SOURCES))
        self.assertEqual(bindings["source_set_sha256"], sha(canonical(source_rows)))
        self.assertEqual(bindings["attempt_08_artifacts_verified"], 11)
        self.assertIn("### Failed Attempt 08 manifest", packet)
        self.assertIn('"blocker":"OUTPUT_ALREADY_EXISTS"', packet)
        self.assertEqual(
            [row["id"] for row in bindings["checklist"]],
            [f"R8-{index:02d}" for index in range(1, 24)],
        )
        states = {row["id"]: row["gate_state"] for row in bindings["checklist"]}
        self.assertEqual(states["R8-08"], "REMOTE_GATE")
        self.assertEqual(states["R8-10"], "REMOTE_GATE")
        self.assertEqual(states["R8-22"], "PROCESS_GATE")
        self.assertEqual(states["R8-23"], "PRECREATE_RECHECK")
        for pattern in builder._EXTERNAL_JUDGE_BLOCK_PATTERNS:
            self.assertIsNone(pattern.search(packet))
        context_row = next(
            row for row in source_rows if row["path"] == "p9-cloud/context_vector.py"
        )
        context_fixture = self.root / "p9-cloud/context_vector.py"
        self.assertIn("MAX_TOKENS = 256", context_fixture.read_text(encoding="utf-8"))
        self.assertEqual(context_row["sha256"], sha(context_fixture.read_bytes()))
        contract_row = next(
            row
            for row in source_rows
            if row["path"] == "post-dogfood/pdh3_scale_contract.py"
        )
        self.assertTrue(contract_row["symbols"])
        self.assertRegex(contract_row["symbol_set_sha256"], r"^[0-9a-f]{64}$")

    def test_v2_receipt_can_supply_both_nested_manifests(self) -> None:
        config = replace(
            self.config,
            bundle_manifest_json=self.bundle_receipt_path,
            prior_attempt_history_manifest_json=self.bundle_receipt_path,
        )
        result = builder.build(config, now=NOW)
        self.assertEqual(result["revision"], "R8")

    def test_attempt_08_cost_mismatch_is_blocked(self) -> None:
        self._rewrite_attempt_08(attempt_cost_usd_upper=0.0)
        with self.assertRaisesRegex(builder.PreflightBuildError, "ATTEMPT_08_COST_INVALID"):
            builder.build(self.config, now=NOW)

    def test_additional_attempt_history_cost_is_mechanical(self) -> None:
        rate = 1.0247222222222223
        attempts = [
            {
                "attempt_id": "R3-PREWORKLOAD-01",
                "campaign_id": "ck-pdh3-scale-r8-relaunch-r3",
                "pod_name": "ck-pdh3-scale-r8-relaunch-r3-01",
                "pod_id": "e3it78a0fnn232",
                "status": "DELETED_BEFORE_UPLOAD_OPERATOR_MISCLASSIFICATION",
                "measured_clock_started": False,
                "workload_started": False,
                "blocker": "OPERATOR_WORKER_SHAPE_MISCLASSIFICATION",
                "provider_resource_status": "DELETED",
                "exact_id_absent": True,
                "campaign_active_inventory": [],
                "credential_material_copied": False,
                "exact_provider_charge_available": False,
                "active_interval_start_utc": "2026-07-31T20:47:32Z",
                "absence_proved_utc": "2026-07-31T20:48:11Z",
                "active_seconds_upper": 39,
                "active_rate_usd_hour_upper": rate,
                "attempt_cost_usd_upper": 39 / 3_600 * rate,
            },
            {
                "attempt_id": "R3-SETUP-01",
                "campaign_id": "ck-pdh3-scale-r8-relaunch-r3",
                "pod_name": "ck-pdh3-scale-r8-relaunch-r3-01",
                "pod_id": "rf6f4rcwo9c5wk",
                "status": "BLOCKED_COMPLETE",
                "measured_clock_started": False,
                "workload_started": True,
                "blocker": "SETUP_DEADLINE_RESERVE_EXHAUSTED:reserve_seconds=600",
                "provider_resource_status": "DELETED",
                "exact_id_absent": True,
                "campaign_active_inventory": [],
                "credential_material_copied": False,
                "exact_provider_charge_available": False,
                "active_interval_start_utc": "2026-07-31T20:41:30Z",
                "absence_proved_utc": "2026-07-31T22:18:37Z",
                "active_seconds_upper": 5_827,
                "active_rate_usd_hour_upper": rate,
                "attempt_cost_usd_upper": 5_827 / 3_600 * rate,
            },
            {
                "attempt_id": "R4-SETUP-01",
                "campaign_id": "ck-pdh3-scale-r8-relaunch-r4",
                "pod_name": "ck-pdh3-scale-r8-relaunch-r4-01",
                "pod_id": "yaid5qh19otlwp",
                "status": "BLOCKED_COMPLETE",
                "measured_clock_started": False,
                "workload_started": True,
                "blocker": "VECTOR_INDEX_CREATE_CONNECTION_LOST",
                "failure_sha256": "d9f4c465a9dac360ef12c592e6d7ffdee2c3af5a150882ac58bf6700620204de",
                "final_evidence_archive_sha256": "f1cf48aa3232859f45f0593d23fdb638595f9e25af6b4930a9479ce7df08f4fc",
                "provider_resource_status": "DELETED",
                "exact_id_absent": True,
                "campaign_active_inventory": [],
                "credential_material_copied": False,
                "exact_provider_charge_available": False,
                "active_interval_start_utc": "2026-07-31T23:48:19Z",
                "absence_proved_utc": "2026-08-01T00:17:49Z",
                "active_seconds_upper": 1_770,
                "active_rate_usd_hour_upper": rate,
                "attempt_cost_usd_upper": 1_770 / 3_600 * rate,
            },
            {
                "attempt_id": "R5-SETUP-01",
                "campaign_id": "ck-pdh3-scale-r8-relaunch-r5",
                "pod_name": "ck-pdh3-scale-r8-relaunch-r5-01",
                "pod_id": "iycjyztx6elw0k",
                "status": "BLOCKED_COMPLETE",
                "measured_clock_started": False,
                "workload_started": True,
                "blocker": "VECTOR_INDEX_METADATA_GATEWAY_CONNECTION_REFUSED",
                "failure_sha256": "e56cb2c69eeb7446f610bbd7c98a84d0c02b794e26a806fa240829fc2a5a5802",
                "final_evidence_archive_sha256": "54812ca5e53c382781679efdc8e07197d9216a2d6ec420331a4f782866eb4f3e",
                "provider_resource_status": "DELETED",
                "exact_id_absent": True,
                "campaign_active_inventory": [],
                "credential_material_copied": False,
                "exact_provider_charge_available": False,
                "active_interval_start_utc": "2026-08-01T01:36:27Z",
                "absence_proved_utc": "2026-08-01T02:05:09Z",
                "active_seconds_upper": 1_722,
                "active_rate_usd_hour_upper": rate,
                "attempt_cost_usd_upper": 1_722 / 3_600 * rate,
            },
            {
                "attempt_id": "R6-SETUP-01",
                "campaign_id": "ck-pdh3-scale-r8-relaunch-r6",
                "pod_name": "ck-pdh3-scale-r8-relaunch-r6-01",
                "pod_id": "xnlp690a3j3xum",
                "status": "BLOCKED_COMPLETE",
                "measured_clock_started": False,
                "workload_started": True,
                "blocker": "VECTOR_INDEX_BACKFILL_LOST_CLUSTER_QUORUM",
                "failure_sha256": "9be0fd49ee93f977cbe494b7ccb97ad693182f0130a9483d50616e50c13d2157",
                "final_evidence_archive_sha256": "d6a7da76b9641443380052d7f55bf546b8ca28f9ab656326a6abfca79e4a5a6f",
                "provider_resource_status": "DELETED",
                "exact_id_absent": True,
                "campaign_active_inventory": [],
                "credential_material_copied": False,
                "exact_provider_charge_available": False,
                "active_interval_start_utc": "2026-08-01T05:18:36Z",
                "absence_proved_utc": "2026-08-01T05:44:06Z",
                "active_seconds_upper": 1_530,
                "active_rate_usd_hour_upper": rate,
                "attempt_cost_usd_upper": 1_530 / 3_600 * rate,
            },
            {
                "attempt_id": "R7-PREWORKLOAD-01",
                "campaign_id": "ck-pdh3-scale-r8-relaunch-r7",
                "pod_name": "ck-pdh3-scale-r8-relaunch-r7-01",
                "pod_id": "6rbcu2lxia4p2m",
                "status": "DELETED_BEFORE_UPLOAD_HOST_GUARD_DETACH_CHECK",
                "measured_clock_started": False,
                "workload_started": False,
                "blocker": "HOST_GUARD_DETACH_CHECK",
                "provider_resource_status": "DELETED",
                "exact_id_absent": True,
                "campaign_active_inventory": [],
                "credential_material_copied": False,
                "exact_provider_charge_available": False,
                "active_interval_start_utc": "2026-08-01T07:51:17Z",
                "absence_proved_utc": "2026-08-01T07:51:23Z",
                "active_seconds_upper": 6,
                "active_rate_usd_hour_upper": rate,
                "attempt_cost_usd_upper": 6 / 3_600 * rate,
            },
            {
                "attempt_id": "R7-SETUP-01",
                "campaign_id": "ck-pdh3-scale-r8-relaunch-r7",
                "pod_name": "ck-pdh3-scale-r8-relaunch-r7-01",
                "pod_id": "81y4t6r6t9zmpz",
                "status": "BLOCKED_COMPLETE",
                "measured_clock_started": False,
                "workload_started": True,
                "blocker": "SETUP_DEADLINE_RESERVE_EXHAUSTED:reserve_seconds=2400",
                "failure_sha256": "721daedb4a361880d204d162b6ca49ce8c72044279a1d18143fca7cd4975c304",
                "final_evidence_archive_sha256": "657abfd4a6ee2a4bb880b9e5e2d4588c896f4e0219239b2972122c92e675a2e9",
                "provider_resource_status": "DELETED",
                "exact_id_absent": True,
                "campaign_active_inventory": [],
                "credential_material_copied": False,
                "exact_provider_charge_available": False,
                "active_interval_start_utc": "2026-08-01T07:53:30Z",
                "absence_proved_utc": "2026-08-01T10:18:07Z",
                "active_seconds_upper": 8_677,
                "active_rate_usd_hour_upper": rate,
                "attempt_cost_usd_upper": 8_677 / 3_600 * rate,
            },
            {
                "attempt_id": "R8-SETUP-01",
                "campaign_id": "ck-pdh3-scale-r8-relaunch-r8",
                "pod_name": "ck-pdh3-scale-r8-relaunch-r8-01",
                "pod_id": "klu635c1c1js3g",
                "status": "BLOCKED_COMPLETE",
                "measured_clock_started": False,
                "workload_started": True,
                "blocker": "FULL_CARDINALITY_SETUP_NOT_GREEN",
                "failure_sha256": "b95f79e19ab03f4c16ee7163d59cb4afece581a3b5893382f4c574c37b177bff",
                "final_evidence_archive_sha256": "2c3db6e1f6b509bf8292e2fa4bda199f85de6739f34c2453faac88156b1b4bc7",
                "provider_resource_status": "DELETED",
                "exact_id_absent": True,
                "campaign_active_inventory": [],
                "credential_material_copied": False,
                "exact_provider_charge_available": False,
                "active_interval_start_utc": "2026-08-01T11:23:44Z",
                "absence_proved_utc": "2026-08-01T12:38:14Z",
                "active_seconds_upper": 4_470,
                "active_rate_usd_hour_upper": rate,
                "attempt_cost_usd_upper": 4_470 / 3_600 * rate,
            },
            {
                "attempt_id": "R9-PREFLIGHT-01",
                "campaign_id": "ck-pdh3-scale-r9-relaunch-r1",
                "pod_name": "ck-pdh3-scale-r9-relaunch-r1-01",
                "pod_id": "qza6pmry5rnox4",
                "status": "BLOCKED_COMPLETE",
                "measured_clock_started": False,
                "workload_started": True,
                "blocker": "REMOTE_PREFLIGHT_READ_MIX_COMMAND_FAILED",
                "failure_sha256": "7e529a6ec5ca90ca11ac8a7cadf4ecc72dd2a0b57ca72cf0ef6dbca92f325463",
                "final_evidence_archive_sha256": "c05fe6add4e05661a309163c65543504b935ac259a941f180d6bb86acc793d4c",
                "provider_resource_status": "DELETED",
                "exact_id_absent": True,
                "campaign_active_inventory": [],
                "credential_material_copied": False,
                "exact_provider_charge_available": False,
                "active_interval_start_utc": "2026-08-01T17:04:54Z",
                "absence_proved_utc": "2026-08-01T17:50:20Z",
                "active_seconds_upper": 2_726,
                "active_rate_usd_hour_upper": rate,
                "attempt_cost_usd_upper": 2_726 / 3_600 * rate,
            },
        ]
        history = {
            "version": "ck-pdh3-additional-attempt-history-v1",
            "attempts": attempts,
            "attempt_ids": [row["attempt_id"] for row in attempts],
            "attempt_count": 9,
            "cost_usd_upper": sum(row["attempt_cost_usd_upper"] for row in attempts),
        }
        contract = builder._load_contract(self.root).production_contract()
        expected = sum(row["attempt_cost_usd_upper"] for row in attempts)
        self.assertAlmostEqual(
            builder._additional_attempt_cost_and_validate(history, contract),
            expected,
        )
        history["attempts"][1]["active_seconds_upper"] -= 1
        with self.assertRaisesRegex(
            builder.PreflightBuildError,
            "ADDITIONAL_ATTEMPT_COST_INVALID",
        ):
            builder._additional_attempt_cost_and_validate(history, contract)

    def test_runpodctl_v272_not_found_wrapper_is_strict(self) -> None:
        valid = (
            '{"error":"api error: {\\"error\\":\\"pod not found\\",'
            '\\"status\\":404}\\n (status 404)"}\n'
            "Usage:\n"
            "  runpodctl pod get <pod-id> [flags]\n\n"
            "Flags:\n"
            "  -h, --help                     help for get\n"
            "      --include-machine          include machine info\n"
            "      --include-network-volume   include network volume info\n\n"
            "Global Flags:\n"
            "  -o, --output string   output format (json, yaml) (default \"json\")\n\n"
            '{"error":"failed to get pod: api error: {"error":"pod not found",'
            '"status":404}\n (status 404)"}\n'
        )
        self.assertTrue(builder._runpodctl_v272_not_found(valid))
        self.assertFalse(builder._runpodctl_v272_not_found(valid + "arbitrary trailing text"))

    def test_expired_launch_window_is_blocked(self) -> None:
        with self.assertRaisesRegex(builder.PreflightBuildError, "LAUNCH_WINDOW_EXPIRED"):
            builder.build(self.config, now=datetime(2026, 8, 2, 0, 0, tzinfo=timezone.utc))

    def test_mismatched_lifecycle_epoch_is_blocked(self) -> None:
        bad = replace(self.config, stop_epoch=self.config.stop_epoch + 1)
        with self.assertRaisesRegex(builder.PreflightBuildError, "LIFECYCLE_EPOCH_MISMATCH"):
            builder.build(bad, now=NOW)

    def test_nonempty_active_inventory_is_blocked(self) -> None:
        self._rewrite_active([{"id": "still-paid"}])
        with self.assertRaisesRegex(builder.PreflightBuildError, "ACTIVE_INVENTORY_NOT_EMPTY"):
            builder.build(self.config, now=NOW)

    def test_l40s_shape_outside_contract_is_blocked(self) -> None:
        wrong_shape = {**self.offer, "vcpu": 32}
        self._rewrite_gpu(
            derived_offer=wrong_shape,
            derived_offer_sha256=sha(canonical(wrong_shape)),
        )
        with self.assertRaisesRegex(builder.PreflightBuildError, "DERIVED_L40S_OFFER_INVALID"):
            builder.build(self.config, now=NOW)

    def test_active_rate_derivation_drift_is_blocked(self) -> None:
        derivation = dict(self.gpu_receipt["active_rate_derivation"])
        derivation["active_rate_usd_hour"] = 1.30
        derivation_body = {
            key: value
            for key, value in derivation.items()
            if key != "derived_fields_sha256"
        }
        derivation["derived_fields_sha256"] = sha(canonical(derivation_body))
        self._rewrite_gpu(active_rate_derivation=derivation)
        with self.assertRaisesRegex(builder.PreflightBuildError, "ACTIVE_RATE_DERIVATION_INVALID"):
            builder.build(self.config, now=NOW)

    def test_stale_provider_receipt_is_blocked(self) -> None:
        self._rewrite_active([], observed_utc="2026-07-31T23:00:00Z")
        with self.assertRaisesRegex(builder.PreflightBuildError, "ACTIVE_INVENTORY_STALE"):
            builder.build(self.config, now=NOW)

    def test_provider_raw_response_tamper_is_blocked(self) -> None:
        self.gpu_raw_path.write_bytes(b"[]")
        with self.assertRaisesRegex(builder.PreflightBuildError, "EVIDENCE_HASH_MISMATCH"):
            builder.build(self.config, now=NOW)

    def test_runtime_instantiator_is_no_shell_and_hash_bound(self) -> None:
        builder.build(self.config, now=NOW)
        bindings = json.loads(self.config.output_bindings.read_bytes())
        concrete = builder.instantiate_runtime_commands(
            bindings["commands"],
            packet_sha256="a" * 64,
            provider_pod_id="fixture-pod-id-01",
        )
        self.assertFalse(concrete["shell_interpolation"])
        self.assertNotIn("__FROZEN", canonical(concrete).decode("utf-8"))
        self.assertNotIn("__PROVIDER", canonical(concrete).decode("utf-8"))
        self.assertEqual(
            concrete["hashes"]["child_controller_argv_sha256"],
            bindings["commands"]["child_controller_argv_sha256"],
        )
        with self.assertRaisesRegex(
            builder.PreflightBuildError, "RUNTIME_PROVIDER_POD_ID_INVALID"
        ):
            builder.instantiate_runtime_commands(
                bindings["commands"],
                packet_sha256="a" * 64,
                provider_pod_id="bad; shell",
            )
        tampered = json.loads(canonical(bindings["commands"]))
        tampered["supervisor_argv_template"][-1] = "999"
        with self.assertRaisesRegex(
            builder.PreflightBuildError, "RUNTIME_TEMPLATE_HASH_MISMATCH"
        ):
            builder.instantiate_runtime_commands(
                tampered,
                packet_sha256="a" * 64,
                provider_pod_id="fixture-pod-id-01",
            )

    def test_hash_mismatch_is_blocked(self) -> None:
        artifact_path = self.root / self.local_manifest["files"][0]["path"]
        original = artifact_path.read_bytes()
        with self.subTest("bound artifact"):
            artifact_path.write_bytes(b"tampered-after-manifest")
            with self.assertRaisesRegex(builder.PreflightBuildError, "EVIDENCE_HASH_MISMATCH"):
                builder.build(self.config, now=NOW)
        artifact_path.write_bytes(original)
        with self.subTest("duplicate resolution"):
            duplicate_source = self.runtime / "post-dogfood/pdh3_scale_contract.py"
            duplicate_source.write_bytes(b"different duplicate bytes")
            with self.assertRaisesRegex(
                builder.PreflightBuildError,
                "EVIDENCE_PATH_MISSING_OR_AMBIGUOUS:post-dogfood/pdh3_scale_contract.py",
            ):
                builder.build(self.config, now=NOW)

    def test_local_smoke_topology_is_required(self) -> None:
        observed = json.loads(canonical(self.local_manifest["isolated_smoke_observed_result"]))
        observed.pop("cluster_topology")
        self._rewrite_local(isolated_smoke_observed_result=observed)
        with self.assertRaisesRegex(
            builder.PreflightBuildError,
            "ISOLATED_LOCAL_SMOKE_EVIDENCE_INVALID",
        ):
            builder.build(self.config, now=NOW)

    def test_unsafe_source_and_evidence_are_each_blocked(self) -> None:
        source = self.root / "post-dogfood" / "run_pdh3_local_canary.py"
        original = source.read_bytes()
        with self.subTest("source"):
            unsafe = "/" + "Users" + "/kenneth/private/key"
            source.write_text(f"secret = {unsafe!r}\n", encoding="utf-8")
            with self.assertRaisesRegex(builder.PreflightBuildError, "SOURCE_UNSAFE"):
                builder.build(self.config, now=NOW)
        source.write_bytes(original)
        with self.subTest("evidence"):
            unsafe = "/" + "Users" + "/kenneth/private/result.json"
            self._rewrite_local(summary=unsafe)
            with self.assertRaisesRegex(builder.PreflightBuildError, "LOCAL_TEST_UNSAFE"):
                builder.build(self.config, now=NOW)

    def test_output_is_append_only(self) -> None:
        builder.build(self.config, now=NOW)
        with self.assertRaisesRegex(builder.PreflightBuildError, "OUTPUT_EXISTS"):
            builder.build(self.config, now=NOW)


if __name__ == "__main__":
    unittest.main()
