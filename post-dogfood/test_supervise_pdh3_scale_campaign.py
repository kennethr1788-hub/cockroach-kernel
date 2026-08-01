from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_supervisor_tested", HERE / "supervise_pdh3_scale_campaign.py"
)
assert SPEC is not None and SPEC.loader is not None
supervisor = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = supervisor
SPEC.loader.exec_module(supervisor)

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CONTROLLER_SPEC = importlib.util.spec_from_file_location(
    "pdh3_actual_writer_tested",
    HERE / "run_pdh3_scale_campaign.py",
)
assert CONTROLLER_SPEC is not None and CONTROLLER_SPEC.loader is not None
controller = importlib.util.module_from_spec(CONTROLLER_SPEC)
sys.modules[CONTROLLER_SPEC.name] = controller
CONTROLLER_SPEC.loader.exec_module(controller)


CAMPAIGN_ID = "ck-pdh3-scale-r1"
PACKET_SHA256 = "a" * 64
TRACE_TOOL_SHA256 = "b" * 64
TRACE_COMMAND_SHA256 = "c" * 64


def signed(body: dict[str, object], field: str) -> dict[str, object]:
    return {**body, field: supervisor.digest(body)}


def add_bytes(archive: tarfile.TarFile, name: str, raw: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(raw)
    info.mode = 0o600
    archive.addfile(info, io.BytesIO(raw))


def build_archive(
    root: Path,
    state: str,
    *,
    corrupt_manifest: bool = False,
    result_updates: dict[str, object] | None = None,
    network_updates: dict[str, object] | None = None,
) -> tuple[Path, Path]:
    contract = supervisor.CONTRACT
    expected_counts = [
        contract.TASKS,
        contract.TASKS * contract.EVENTS_PER_TASK,
        contract.TASKS * contract.RECEIPTS_PER_TASK,
        contract.VECTORS,
    ]
    teardown = signed(
        {
            "version": "ck-pdh3-scale-teardown-v2",
            "campaign_id": CAMPAIGN_ID,
            "nodes_stopped": True,
            "ports_closed": True,
            "generated_root_removed": True,
            "database_dropped": state == supervisor.GREEN_PENDING_FINAL_GATE,
            "open_ports": [],
            "green": True,
        },
        "receipt_sha256",
    )
    setup = signed(
        {
            "version": "ck-pdh3-scale-setup-v4",
            "campaign_id": CAMPAIGN_ID,
            "expected_counts": expected_counts,
            "actual_counts": expected_counts,
            "dataset_counts": expected_counts,
            "reconciliations": {
                label: {"state": "EXACT"}
                for label in ("tasks", "events", "receipts", "vectors")
            },
            "mismatch_counts": {
                label: 0
                for label in ("tasks", "events", "receipts", "vectors")
            },
            "wrong_task_vector_links": 0,
            "vector_index_preseed": {
                "green": True,
                "mode": "PRECREATED_ON_EMPTY_TABLE",
                "vector_rows": 0,
                "metadata": {"green": True},
            },
            "vector_index_postseed": {
                "green": True,
                "mode": "INCREMENTALLY_MAINTAINED_DURING_SEED",
                "queryable": True,
                "metadata": {"green": True},
                "coverage": {"green": True},
            },
            "query_targets": {
                "green": True,
                "id_width": 6,
                "vector_rows": 20,
                "expected_vector_rows": 20,
                "receipt_rows": 10,
                "expected_receipt_rows": 10,
            },
            "setup_elapsed_seconds": 5_000.0,
            "setup_deadline_seconds": contract.SETUP_TIMEOUT_SECONDS,
            "deadline_met": True,
            "green": True,
        },
        "setup_sha256",
    )
    failure = signed(
        {
            "version": "ck-pdh3-scale-failure-v1",
            "campaign_id": CAMPAIGN_ID,
            "exception_type": "CampaignError",
            "reason": "TEST_BLOCK",
        },
        "failure_sha256",
    )
    green = state == supervisor.GREEN_PENDING_FINAL_GATE
    trace_raw = b"1234 connect(127.0.0.1)\n"
    network_body: dict[str, object] = {
        "version": "ck-pdh3-process-tree-egress-observer-v2",
        "status": "GREEN" if green else "BLOCKED",
        "authoritative": True,
        "packet_sha256": PACKET_SHA256,
        "tool_sha256": TRACE_TOOL_SHA256,
        "strace_sha256": contract.STRACE_BINARY_SHA256,
        "command_sha256": TRACE_COMMAND_SHA256,
        "green": green,
        "claim": (
            "PROCESS_TREE_OBSERVED_ZERO_EXTERNAL_EGRESS"
            if green
            else "PROCESS_TREE_OBSERVATION_BLOCKED"
        ),
        "child_exit": 0 if green else 1,
        "trace_stream_mode": "SINGLE_FILE_PID_PREFIXED_STRACE_F",
        "external_or_unparseable_count": 0,
        "violations": [],
        "observer_error": None,
        "trace_files": [
            {
                "name": "network-trace",
                "bytes": len(trace_raw),
                "sha256": hashlib.sha256(trace_raw).hexdigest(),
                "hash_complete": True,
            }
        ],
        "trace_file_count": 1,
        "trace_bytes": len(trace_raw),
        "maximum_trace_bytes": 2 * 1024**3,
    }
    if network_updates:
        network_body.update(network_updates)
    network = signed(network_body, "receipt_sha256")
    evidence: dict[str, bytes] = {
        "teardown.json": supervisor.canonical(teardown),
        "journal.ndjson": b"{}\n",
    }
    terminal: dict[str, bytes] = {}
    final_state: dict[str, object] = {
        "version": "ck-pdh3-closeout-summary-v2",
        "network-receipt.json": network,
        "evidence/result.json": None,
        "evidence/MEASURED_CAMPAIGN_GREEN": None,
        "evidence/failure.json": None,
        "evidence/setup.json": None,
        "evidence/teardown.json": teardown,
    }
    if state == supervisor.GREEN_PENDING_FINAL_GATE:
        evidence["setup.json"] = supervisor.canonical(setup)
        final_state["evidence/setup.json"] = setup
    elif state == supervisor.BLOCKED_COMPLETE:
        evidence["failure.json"] = supervisor.canonical(failure)
        final_state["evidence/failure.json"] = failure
    elif state == "BOTH":
        evidence["failure.json"] = supervisor.canonical(failure)
        evidence["setup.json"] = supervisor.canonical(setup)
        final_state["evidence/failure.json"] = failure
        final_state["evidence/setup.json"] = setup

    def resources() -> dict[str, object]:
        return {
            "nodes": [
                {
                    "node": index,
                    "pid": 1_000 + index,
                    "alive": True,
                    "rss_kb": 1_024,
                    "descriptors": 64,
                }
                for index in range(1, 4)
            ],
            "database_bytes": 1_000_000,
            "evidence_bytes": 1_000_000,
            "disk_total_bytes": 10_000_000,
            "disk_used_bytes": 1_000_000,
            "disk_used_fraction": 0.1,
        }

    def readiness(epoch: int) -> dict[str, object]:
        return {
            "nodes": [
                {
                    "node": index,
                    "pid": 30_000 + epoch * 10 + index,
                    "alive": True,
                    "sql_ready": True,
                }
                for index in range(1, 4)
            ],
            "green": True,
        }

    def fault(node: int, controls: list[int], epoch: int) -> dict[str, object]:
        return {
            "node": node,
            "signal": "SIGKILL",
            "returncode": -9,
            "old_pid": 10_000 + node,
            "new_pid": 20_000 + node,
            "before": expected_counts,
            "during": expected_counts,
            "after": expected_counts,
            "controls_before": controls,
            "controls_during": controls,
            "controls_after": controls,
            "cluster_readiness": readiness(epoch),
            "green": True,
        }

    def verifier_summary(
        lane: str, manifests: list[str], receipt_hashes: set[str]
    ) -> dict[str, object]:
        return {
            "lane": lane,
            "batch_count": len(manifests),
            "receipt_count": len(receipt_hashes),
            "unique_receipt_hashes": len(receipt_hashes),
            "manifest_set_sha256": supervisor.digest(manifests),
            "green": True,
        }

    failure_classes = (
        "tampered-receipt", "replayed-warrant", "malformed-record",
        "unsupported-value", "quarantined-candidate", "incomplete-evidence",
        "interrupted-consumption",
    )

    def add_verifier_batch(
        lane: str, epoch: int, raw_files: dict[str, bytes]
    ) -> tuple[dict[str, object], str, set[str]]:
        salt = hashlib.sha256(f"{lane}:{epoch}".encode()).digest()
        failures: list[dict[str, object]] = []
        for class_index, class_name in enumerate(failure_classes):
            for variant in (1, 2, 3):
                verdict = (
                    "INVALID" if variant == 3 and class_index > 0 else "REFUSE"
                )
                body: dict[str, object] = {
                    "version": "test-failure-vector-v1",
                    "class": class_name,
                    "variant": variant,
                    "seed_hash": supervisor.digest(
                        salt + f"failure:{class_index}:{variant}".encode()
                    ),
                    "expected_verdict": verdict,
                    "expected_reason": f"{verdict}_{class_index}_{variant}",
                }
                failures.append({**body, "vector_hash": supervisor.digest(body)})
        controls: list[dict[str, object]] = []
        for variant, class_name in enumerate(failure_classes, start=1):
            body = {
                "version": "gate7-heldout-control-v1",
                "class": "valid-control-" + class_name,
                "variant": variant,
                "seed_hash": supervisor.digest(
                    salt + f"control:{variant}".encode()
                ),
                "expected_verdict": "PROMOTE",
                "expected_reason": "VERIFIED",
            }
            controls.append({**body, "vector_hash": supervisor.digest(body)})
        vector_body = {
            "version": "hardening-gate7-vector-set-v1",
            "candidate_commit": contract.PRODUCT_CANDIDATE,
            "salt_sha256": supervisor.digest(salt),
            "failure_vectors": failures,
            "valid_controls": controls,
        }
        vector_set = {**vector_body, "set_hash": supervisor.digest(vector_body)}
        raw_files["verifier/public-salt.bin"] = salt
        raw_files["verifier/public-vectors.json"] = supervisor.canonical(vector_set)
        ordered = [*failures, *controls]
        executions: list[tuple[str, dict[str, object]]] = [
            (f"trial-{index:03d}", vector)
            for index, vector in enumerate(ordered, start=1)
        ]
        selected = [
            controls[0],
            next(row for row in failures if row["expected_verdict"] == "REFUSE"),
            next(row for row in failures if row["expected_verdict"] == "INVALID"),
        ]
        for vector in selected:
            verdict_label = str(vector["expected_verdict"]).lower()
            executions.extend(
                (f"det-{verdict_label}-{repetition:02d}", vector)
                for repetition in range(1, 6)
            )
        prefix = "verifier/verifier-campaign/"
        receipts: list[dict[str, object]] = []
        inner_files: dict[str, str] = {}
        for execution_id, vector in executions:
            body = {
                "version": "hardening-gate7-trial-receipt-v1",
                "candidate_commit": contract.PRODUCT_CANDIDATE,
                "execution_id": execution_id,
                "vector_hash": vector["vector_hash"],
                "vector_class": vector["class"],
                "variant": vector["variant"],
                "expected_verdict": vector["expected_verdict"],
                "expected_reason": vector["expected_reason"],
                "observed_verdict": vector["expected_verdict"],
                "observed_reason": vector["expected_reason"],
                "mutation_performed": False,
                "details": {"fixture": True},
                "passed": True,
            }
            receipt = {**body, "receipt_hash": supervisor.digest(body)}
            relative = f"receipts/{execution_id}.json"
            raw = supervisor.canonical(receipt)
            raw_files[prefix + relative] = raw
            inner_files[relative] = hashlib.sha256(raw).hexdigest()
            receipts.append(receipt)
        sizes = [len(supervisor.canonical(row)) for row in receipts]
        groups = {
            str(row["vector_class"])
            for row in receipts
            if str(row["execution_id"]).startswith("det-")
        }
        aggregate_body = {
            "version": "hardening-gate7-aggregate-v1",
            "campaign_id": f"{CAMPAIGN_ID}-{lane}-v{epoch:04d}-verifier",
            "candidate_commit": contract.PRODUCT_CANDIDATE,
            "vector_set_hash": vector_set["set_hash"],
            "measured_executions": 43, "failure_trials": 21,
            "valid_controls": 7, "determinism_executions": 15,
            "false_promotions": 0, "mutation_after_refusal": 0,
            "correct_stable_reason_count": 43, "canonical_receipt_count": 43,
            "valid_control_continuation_count": 12,
            "hidden_session_state_dependencies": 0,
            "trial_teardown_count": 43, "residue_count": 0,
            "output_schema_compliance_count": 43,
            "determinism_group_count": len(groups),
            "determinism_stable_group_count": len(groups),
            "receipt_bytes_total": sum(sizes),
            "receipt_bytes_p50": supervisor.percentile(sizes, 50),
            "receipt_bytes_p95": supervisor.percentile(sizes, 95),
            "receipt_bytes_p99": supervisor.percentile(sizes, 99),
            "receipt_hashes": [row["receipt_hash"] for row in receipts],
            "limitations": ["SYNTHETIC_HELD_OUT_FAILURES", "NOT_LIVE_MEMORY_WORKLOAD",
                            "NOT_PRODUCTION_SCALE", "NOT_PUBLIC_USER_EVIDENCE"],
            "green": True,
        }
        aggregate = {**aggregate_body, "aggregate_sha256": supervisor.digest(aggregate_body)}
        aggregate_raw = supervisor.canonical(aggregate)
        raw_files[prefix + "aggregate.json"] = aggregate_raw
        inner_files["aggregate.json"] = hashlib.sha256(aggregate_raw).hexdigest()
        inner_body = {
            "version": "hardening-gate7-evidence-manifest-v1",
            "campaign_id": aggregate["campaign_id"],
            "candidate_commit": contract.PRODUCT_CANDIDATE,
            "vector_set_hash": vector_set["set_hash"],
            "aggregate_sha256": aggregate["aggregate_sha256"],
            "files": inner_files,
        }
        inner = {**inner_body, "manifest_sha256": supervisor.digest(inner_body)}
        raw_files[prefix + "manifest.json"] = supervisor.canonical(inner)
        checkpoint = {
            "aggregate_sha256": aggregate["aggregate_sha256"],
            "aggregate_file_sha256": inner_files["aggregate.json"],
            "measured_executions": 43, "false_promotions": 0,
            "mutation_after_refusal": 0, "correct_stable_reason_count": 43,
            "valid_control_continuation_count": 12, "trial_teardown_count": 43,
            "residue_count": 0,
        }
        return checkpoint, str(inner["manifest_sha256"]), {
            str(row["receipt_hash"]) for row in receipts
        }

    def add_lane(
        lane: str,
        count: int,
        verifier_batches: int,
        fault_epochs: set[int],
        concurrency: list[int],
    ) -> tuple[list[dict[str, object]], dict[str, object]]:
        listed: list[dict[str, object]] = []
        fault_number = 0
        acknowledged = 0
        counter = 0
        total_operations = 0
        manifests: list[str] = []
        receipt_hashes: set[str] = set()
        boundary_base = 1_000_000_000_000_000_000 + (0 if lane == "preflight" else 1_000_000_000_000_000)
        for epoch in range(1, count + 1):
            raw_root = f"raw/{lane}/epoch-{epoch:04d}"
            raw_files: dict[str, bytes] = {}
            verifier: dict[str, object] | None = None
            stage_operations: dict[str, int] = {}
            workloads: dict[str, object] = {}
            for kind in ("read_mix", "ack_write", "contended_update", "replay"):
                minimum = (max(2_000, concurrency[epoch - 1] * 10)
                           if kind == "ack_write" else max(1_000, concurrency[epoch - 1] * 5))
                operations = 2_500 if kind == "read_mix" else minimum
                prefix = f"querybench-c{concurrency[epoch - 1]}-{kind}"
                stdout = f"{kind} complete\n".encode()
                stderr = b""
                histogram = supervisor.canonical({"Name": kind, "Hist": {"Counts": [operations]}}) + b"\n"
                raw_files[prefix + ".stdout.log"] = stdout
                raw_files[prefix + ".stderr.log"] = stderr
                raw_files[prefix + ".histograms.json"] = histogram
                boundary = ({"mode": "FIXED_DURATION", "duration_seconds": contract.QUERY_DURATION_SECONDS,
                             "target_operations": None} if kind == "read_mix" else
                            {"mode": "BOUNDED_FIXED_OPERATIONS", "duration_seconds": None,
                             "minimum_operations": minimum,
                             "maximum_operations": minimum + concurrency[epoch - 1] - 1,
                             "querybench_soft_cap": minimum})
                workloads[kind] = {
                    "kind": kind, "execution_boundary": boundary,
                    "summary": {"elapsed_seconds": 1.0, "errors": 0,
                                "operations": operations, "operations_per_second": float(operations),
                                "latency_ms": {"avg": 1.0, "p50": 1.0, "p95": 2.0,
                                               "p99": 3.0, "max": 4.0}},
                    "histogram_count": operations, "histogram_accounts_for_operations": True,
                    "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
                    "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
                    "histograms_sha256": hashlib.sha256(histogram).hexdigest(),
                }
                stage_operations[kind] = operations
            acknowledged += stage_operations["ack_write"]
            counter += stage_operations["contended_update"]
            stage_total = sum(stage_operations.values())
            total_operations += stage_total
            checks = {"zero_errors": True, "minimum_operations": True,
                      "histograms_account_for_operations": True,
                      "bounded_operation_targets_respected": True,
                      "acknowledged_writes_exact": True, "contended_updates_exact": True,
                      "replay_idempotent": True, "p99_within_limit": True,
                      "pmax_within_limit": True}
            stage = {"concurrency": concurrency[epoch - 1], "workloads": workloads,
                     "total_operations": stage_total,
                     "maximum_latency_ms": {"p99": 3.0, "max": 4.0},
                     "acknowledged_write_delta": stage_operations["ack_write"],
                     "contended_update_delta": stage_operations["contended_update"],
                     "replay_rows": 1, "checks": checks, "green": True}
            if epoch <= verifier_batches:
                verifier, inner_manifest, batch_hashes = add_verifier_batch(lane, epoch, raw_files)
                manifests.append(inner_manifest)
                if receipt_hashes & batch_hashes:
                    raise AssertionError("fixture verifier hashes are not unique")
                receipt_hashes.update(batch_hashes)
            for relative, raw in raw_files.items():
                evidence[f"{raw_root}/{relative}"] = raw
            raw_hashes = {
                relative: hashlib.sha256(raw).hexdigest()
                for relative, raw in raw_files.items()
            }
            raw_body = {
                "version": "ck-pdh3-raw-epoch-manifest-v1",
                "lane": lane,
                "epoch": epoch,
                "files": raw_hashes,
                "file_count": len(raw_hashes),
                "file_set_sha256": supervisor.digest(raw_hashes),
            }
            raw_manifest = {
                **raw_body,
                "manifest_sha256": supervisor.digest(raw_body),
            }
            evidence[f"{raw_root}/raw-epoch-manifest.json"] = supervisor.canonical(
                raw_manifest
            )
            current_fault = None
            if epoch in fault_epochs:
                current_fault = fault((fault_number % 3) + 1, [acknowledged, counter, 1], epoch)
                fault_number += 1
            boundary_ns = boundary_base + epoch * contract.CHECKPOINT_SECONDS * 1_000_000_000
            checkpoint_body = {
                "version": "ck-pdh3-scale-checkpoint-v2",
                "lane": lane,
                "epoch": epoch,
                "concurrency": concurrency[epoch - 1],
                "stage": stage,
                "cleanup_probe": {"task_id_hash": hashlib.sha256(f"{lane}:{epoch}".encode()).hexdigest(), "residue": 0},
                "dependency_matrix": {"statuses": ["ADVISORY", "TIMEOUT", "THROTTLED", "MALFORMED", "STALE"], "rows": 5},
                "verifier": verifier,
                "fault": current_fault,
                "counts": expected_counts,
                "control_counts": [acknowledged, counter, 1],
                "wrong_task_vector_links": 0,
                "cluster_readiness_before_boundary": readiness(epoch),
                "resources_at_boundary": resources(),
                "boundary_monotonic_ns": boundary_ns,
                "snapshot_monotonic_ns": boundary_ns,
                "boundary_drift_ns": 0,
                "raw_evidence": {
                    "path": raw_root,
                    "manifest_sha256": raw_manifest["manifest_sha256"],
                    "file_count": len(raw_hashes),
                },
            }
            checkpoint = {
                **checkpoint_body,
                "checkpoint_sha256": supervisor.digest(checkpoint_body),
            }
            name = (
                f"checkpoint-{epoch:04d}.json"
                if lane == "measured"
                else f"preflight-checkpoint-{epoch:04d}.json"
            )
            evidence[name] = supervisor.canonical(checkpoint)
            listed.append(
                {
                    "epoch": epoch,
                    "checkpoint_sha256": checkpoint["checkpoint_sha256"],
                }
            )
        return listed, {"manifests": manifests, "receipt_hashes": receipt_hashes,
                        "control_counts": [acknowledged, counter, 1],
                        "total_operations": total_operations,
                        "measured_seconds": count * contract.CHECKPOINT_SECONDS}

    if state == supervisor.GREEN_PENDING_FINAL_GATE:
        preflight_checkpoints, preflight_metrics = add_lane(
            "preflight",
            contract.REMOTE_PREFLIGHT_EPOCHS,
            contract.REMOTE_PREFLIGHT_EPOCHS,
            set(range(1, contract.REMOTE_PREFLIGHT_EPOCHS + 1)),
            [contract.REMOTE_PREFLIGHT_CONCURRENCY]
            * contract.REMOTE_PREFLIGHT_EPOCHS,
        )
        schedule = contract.expected_schedule()
        measured_checkpoints, measured_metrics = add_lane(
            "measured",
            contract.REQUIRED_CHECKPOINTS,
            contract.VERIFIER_BATCHES,
            set(schedule["fault_epochs"]),
            schedule["concurrency"],
        )
        trace_progress_body = {
            "version": "ck-pdh3-process-tree-egress-observer-v2",
            "authoritative": False,
            "status": "IN_PROGRESS",
            "trace_stream_count": 1,
            "maximum_trace_bytes": contract.TRACE_BYTES_LIMIT,
            "trace_bytes": 1_000,
            "projected_trace_bytes_24h_conservative": 2_000,
            "projected_cap_exceeded": False,
            "scan_count": 1,
        }
        trace_progress = {
            **trace_progress_body,
            "progress_receipt_sha256": supervisor.digest(trace_progress_body),
        }
        evidence["preflight-trace-progress.json"] = supervisor.canonical(trace_progress)
        trace_checks = {
            "version": True, "hash": True, "non_authoritative": True,
            "in_progress": True, "one_trace_stream": True,
            "maximum_bytes": True, "current_bytes": True, "projection": True,
            "cap_not_exceeded": True, "scan_progress": True,
        }
        reset_body = {
            "version": "ck-pdh3-preflight-control-reset-v1",
            "before": preflight_metrics["control_counts"],
            "after": [0, 0, 0],
            "preflight_advice_rows": 0,
            "green": True,
        }
        reset = {**reset_body, "reset_sha256": supervisor.digest(reset_body)}
        query_targets = {"id_width": 6, "vector_rows": 20,
                         "expected_vector_rows": 20, "receipt_rows": 10,
                         "expected_receipt_rows": 10, "green": True}
        preflight_body = {
            "version": "ck-pdh3-remote-preflight-v1",
            "epoch_count": contract.REMOTE_PREFLIGHT_EPOCHS,
            "concurrency": contract.REMOTE_PREFLIGHT_CONCURRENCY,
            "fault_count": contract.REMOTE_PREFLIGHT_FAULTS,
            "checkpoints": preflight_checkpoints,
            "verifier_evidence": verifier_summary(
                "preflight", preflight_metrics["manifests"],
                preflight_metrics["receipt_hashes"]),
            "trace_progress": {
                "receipt_sha256": trace_progress["progress_receipt_sha256"],
                "file_sha256": hashlib.sha256(
                    evidence["preflight-trace-progress.json"]
                ).hexdigest(),
                "age_seconds": 1.0,
                "checks": trace_checks,
                "green": True,
            },
            "control_reset": reset,
            "static_counts_after_reset": expected_counts,
            "query_targets_after_reset": query_targets,
            "green": True,
        }
        preflight = {
            **preflight_body,
            "preflight_sha256": supervisor.digest(preflight_body),
        }
        evidence["remote-preflight.json"] = supervisor.canonical(preflight)

        files_before_terminal = {
            name: hashlib.sha256(raw).hexdigest()
            for name, raw in evidence.items()
        }
        premanifest_body = {
            "version": "ck-pdh3-scale-evidence-manifest-v1",
            "files": files_before_terminal,
            "file_count": len(files_before_terminal),
            "file_set_sha256": supervisor.digest(files_before_terminal),
        }
        premanifest = {
            **premanifest_body,
            "manifest_sha256": supervisor.digest(premanifest_body),
        }
        result_body: dict[str, object] = {
            "version": "ck-pdh3-production-scale-result-v1",
            "status": "GREEN",
            "production_mode": True,
            "product_candidate": contract.PRODUCT_CANDIDATE,
            "plan_sha256": contract.PLAN_SHA256,
            "packet_sha256": PACKET_SHA256,
            "contract_sha256": contract.production_contract()["contract_sha256"],
            "campaign_id": CAMPAIGN_ID,
            "synthetic_only": True,
            "credentials_used": False,
            "external_cloud_calls": 0,
            "cluster_topology": "THREE_NODES_ONE_SECURE_RUNPOD_HOST",
            "measured_seconds": measured_metrics["measured_seconds"],
            "remote_preflight": {
                "required": True,
                "preflight_sha256": preflight["preflight_sha256"],
            },
            "dataset_counts": expected_counts,
            "control_counts": measured_metrics["control_counts"],
            "expected_control_counts": measured_metrics["control_counts"],
            "wrong_task_vector_links": 0,
            "checkpoints": measured_checkpoints,
            "checkpoint_count": contract.REQUIRED_CHECKPOINTS,
            "total_measured_operations": measured_metrics["total_operations"],
            "verifier_executions": contract.VERIFIER_EXECUTIONS,
            "verifier_evidence": verifier_summary(
                "measured", measured_metrics["manifests"],
                measured_metrics["receipt_hashes"],
            ),
            "fault_cycles": len(schedule["fault_epochs"]),
            "maximum_p99_ms": 3.0,
            "maximum_latency_ms": 4.0,
            "limitations": [
                "SYNTHETIC_ONLY", "SINGLE_RUNPOD_HOST", "NOT_MULTI_REGION",
                "NOT_PRODUCTION_TRAFFIC",
                "LAMBDA_FAILURES_ARE_FROZEN_LOCAL_ADVICE_STATES",
                "GPU_NOT_USED_BY_CPU_BOUND_PROTOCOL",
            ],
            "local_teardown": {
                "green": True,
                "receipt_sha256": teardown["receipt_sha256"],
            },
            "precommit_manifest_sha256": premanifest["manifest_sha256"],
            "green_checks": {
                label: True
                for label in (
                    "checkpoint_count",
                    "verifier_execution_count",
                    "dataset_counts",
                    "control_counts",
                    "cross_task_vector_links",
                    "false_promotions",
                    "latency",
                    "fault_cycles",
                )
            },
        }
        if result_updates:
            result_body.update(result_updates)
        with tempfile.TemporaryDirectory(
            prefix="actual-pdh3-writer-order.",
            dir=root,
        ) as writer_temporary:
            writer_root = Path(writer_temporary)
            (writer_root / "manifest.json").write_bytes(
                supervisor.canonical(premanifest)
            )
            (writer_root / "teardown.json").write_bytes(
                supervisor.canonical(teardown)
            )
            result = controller.commit_success_evidence(
                writer_root,
                result_body,
                teardown,
            )
            marker = json.loads(
                (writer_root / "MEASURED_CAMPAIGN_GREEN").read_bytes()
            )
            terminal["result.json"] = (writer_root / "result.json").read_bytes()
            terminal["MEASURED_CAMPAIGN_GREEN"] = (
                writer_root / "MEASURED_CAMPAIGN_GREEN"
            ).read_bytes()
        final_state["evidence/result.json"] = result
        final_state["evidence/MEASURED_CAMPAIGN_GREEN"] = marker
    else:
        files_before_terminal = {
            name: hashlib.sha256(raw).hexdigest()
            for name, raw in evidence.items()
        }
        premanifest_body = {
            "version": "ck-pdh3-scale-evidence-manifest-v1",
            "files": files_before_terminal,
            "file_count": len(files_before_terminal),
            "file_set_sha256": supervisor.digest(files_before_terminal),
        }
        premanifest = {
            **premanifest_body,
            "manifest_sha256": supervisor.digest(premanifest_body),
        }
        if state == "BOTH":
            result_body = {
                "version": "ck-pdh3-production-scale-result-v1",
                "campaign_id": CAMPAIGN_ID,
                "status": "GREEN",
            }
            result = {
                **result_body,
                "result_sha256": supervisor.digest(result_body),
            }
            terminal["result.json"] = supervisor.canonical(result)
            final_state["evidence/result.json"] = result

    if corrupt_manifest:
        premanifest["manifest_sha256"] = "0" * 64

    archive_path = root / f"{state}.tgz"
    final_state_path = root / f"{state}.json"
    final_state_raw = supervisor.canonical(final_state)
    final_state_path.write_bytes(final_state_raw)
    with tarfile.open(archive_path, "w:gz") as archive:
        for name, raw in evidence.items():
            add_bytes(archive, "evidence/" + name, raw)
        add_bytes(
            archive,
            "evidence/manifest.json",
            supervisor.canonical(premanifest),
        )
        for name, raw in terminal.items():
            add_bytes(archive, "evidence/" + name, raw)
        add_bytes(archive, "network-receipt.json", supervisor.canonical(network))
        add_bytes(archive, "network-trace", trace_raw)
        add_bytes(archive, "production.log", b"complete\n")
        add_bytes(archive, "production.pid", b"123\n")
        add_bytes(archive, "final-state.json", final_state_raw)
    return archive_path, final_state_path


class SupervisorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.production_temporary = tempfile.TemporaryDirectory(
            prefix="pdh3-supervisor-production-fixture."
        )
        root = Path(cls.production_temporary.name)
        cls.production_archive, cls.production_final_state = build_archive(
            root,
            supervisor.GREEN_PENDING_FINAL_GATE,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.production_temporary.cleanup()

    def make_config(self, root: Path, label: str = "case") -> supervisor.Config:
        cli = root / "runpodctl"
        if not cli.exists():
            cli.write_bytes(b"#!/bin/sh\nexit 0\n")
            cli.chmod(0o700)
        return supervisor.Config(
            runpodctl=cli,
            runpodctl_sha256=supervisor.sha256_file(cli),
            pod_id="pod-123",
            pod_name="ck-pdh3-scale-r1-worker",
            campaign_prefix="ck-pdh3-scale-r1",
            ssh_config=root / "ssh-config",
            ssh_alias="pdh3-worker",
            remote_root="/tmp/ck-pdh3-scale-r1",
            retrieval=root / (label + "-retrieval"),
            log=root / (label + "-supervisor.ndjson"),
            packet_sha256=PACKET_SHA256,
            trace_tool_sha256=TRACE_TOOL_SHA256,
            trace_command_sha256=TRACE_COMMAND_SHA256,
            closeout_deadline_epoch=time.time() + 3_600,
            poll_seconds=1,
            command_timeout_seconds=5,
            transfer_timeout_seconds=30,
            teardown_reserve_seconds=5,
        )

    def test_archive_semantic_terminal_states(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdh3-supervisor-test.") as temporary:
            root = Path(temporary)
            for expected in (
                supervisor.GREEN_PENDING_FINAL_GATE,
                supervisor.BLOCKED_COMPLETE,
                supervisor.ABSENT_RESULT,
            ):
                with self.subTest(expected=expected):
                    if expected == supervisor.GREEN_PENDING_FINAL_GATE:
                        archive = self.production_archive
                        final_state = self.production_final_state
                    else:
                        archive, final_state = build_archive(root, expected)
                    config = self.make_config(root, "semantic-" + expected)
                    observed, _ = supervisor.validate_archive(
                        archive,
                        final_state,
                        config,
                    )
                    self.assertEqual(observed, expected)

    def test_actual_writer_order_manifest_result_marker_is_valid(self) -> None:
        with tarfile.open(self.production_archive, "r:gz") as archive:
            names = archive.getnames()
        self.assertLess(
            names.index("evidence/manifest.json"),
            names.index("evidence/result.json"),
        )
        self.assertLess(
            names.index("evidence/result.json"),
            names.index("evidence/MEASURED_CAMPAIGN_GREEN"),
        )
        root = Path(self.production_temporary.name)
        config = self.make_config(root, "actual-writer-order")
        observed, details = supervisor.validate_archive(
            self.production_archive,
            self.production_final_state,
            config,
        )
        self.assertEqual(observed, supervisor.GREEN_PENDING_FINAL_GATE)
        self.assertRegex(details["manifest_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(details["marker_sha256"], r"^[0-9a-f]{64}$")

    def test_reduced_or_fabricated_production_result_is_rejected(self) -> None:
        root = Path(self.production_temporary.name)
        config = self.make_config(root, "production-negative")
        with tarfile.open(self.production_archive, "r:gz") as archive:
            names = set(archive.getnames())
            manifest, _ = supervisor.validate_manifest(archive, names)
            result = supervisor.read_member_json(archive, "evidence/result.json")
            marker = supervisor.read_member_json(
                archive,
                "evidence/MEASURED_CAMPAIGN_GREEN",
            )
            setup = supervisor.read_member_json(archive, "evidence/setup.json")
            teardown = supervisor.read_member_json(archive, "evidence/teardown.json")
            cases = {
                "reduced-duration": {"measured_seconds": 60},
                "reduced-dataset": {"dataset_counts": [1, 10, 2, 1]},
                "wrong-packet": {"packet_sha256": "d" * 64},
                "wrong-product": {"product_candidate": "d" * 40},
                "wrong-plan": {"plan_sha256": "d" * 64},
                "wrong-contract": {"contract_sha256": "d" * 64},
                "reduced-checkpoints": {"checkpoint_count": 1},
                "reduced-verifier": {"verifier_executions": 43},
                "reduced-faults": {"fault_cycles": 0},
                "stale-manifest": {"precommit_manifest_sha256": "e" * 64},
            }
            for label, updates in cases.items():
                with self.subTest(label=label):
                    altered = copy.deepcopy(result)
                    altered.update(updates)
                    with self.assertRaises(supervisor.ArchiveFailure):
                        supervisor.validate_production_result(
                            archive,
                            manifest,
                            altered,
                            marker,
                            setup,
                            teardown,
                            config,
                        )
            altered = copy.deepcopy(result)
            altered["remote_preflight"] = {
                "required": True,
                "preflight_sha256": "f" * 64,
            }
            with self.assertRaises(supervisor.ArchiveFailure):
                supervisor.validate_production_result(
                    archive,
                    manifest,
                    altered,
                    marker,
                    setup,
                    teardown,
                    config,
                )
            marker_body = {
                key: value
                for key, value in marker.items()
                if key != "marker_sha256"
            }
            marker_body["result_sha256"] = "9" * 64
            altered_marker = {
                **marker_body,
                "marker_sha256": supervisor.digest(marker_body),
            }
            with self.assertRaises(supervisor.ArchiveFailure):
                supervisor.validate_production_result(
                    archive,
                    manifest,
                    result,
                    altered_marker,
                    setup,
                    teardown,
                    config,
                )
            reduced_setup = copy.deepcopy(setup)
            reduced_setup["dataset_counts"] = [1, 10, 2, 1]
            with self.assertRaises(supervisor.ArchiveFailure):
                supervisor.validate_production_result(
                    archive,
                    manifest,
                    result,
                    marker,
                    reduced_setup,
                    teardown,
                    config,
                )

    def test_trace_provenance_bindings_are_fail_closed(self) -> None:
        root = Path(self.production_temporary.name)
        config = self.make_config(root, "trace-negative")
        with tarfile.open(self.production_archive, "r:gz") as archive:
            names = set(archive.getnames())
            network = supervisor.read_member_json(archive, "network-receipt.json")
            for field, bad in (
                ("authoritative", False),
                ("version", "ck-pdh3-process-tree-egress-observer-v1"),
                ("packet_sha256", "d" * 64),
                ("tool_sha256", "e" * 64),
                ("strace_sha256", "f" * 64),
                ("command_sha256", "1" * 64),
                ("claim", "ZERO_EGRESS"),
            ):
                with self.subTest(field=field):
                    altered = copy.deepcopy(network)
                    altered[field] = bad
                    with self.assertRaises(supervisor.ArchiveFailure):
                        supervisor.validate_trace_evidence(
                            archive,
                            names,
                            altered,
                            config,
                        )

    def test_minimal_checkpoint_and_verifier_evidence_are_rejected(self) -> None:
        root = Path(self.production_temporary.name)
        with tarfile.open(self.production_archive, "r:gz") as archive:
            names = set(archive.getnames())
            manifest, _ = supervisor.validate_manifest(archive, names)
            checkpoint = supervisor.read_member_json(
                archive, "evidence/preflight-checkpoint-0001.json"
            )
            raw_manifest = supervisor.read_member_json(
                archive,
                "evidence/raw/preflight/epoch-0001/raw-epoch-manifest.json",
            )
            with self.assertRaises(supervisor.ArchiveFailure):
                supervisor.validate_stage(
                    archive,
                    raw_manifest,
                    {"green": True, "checks": {"zero_errors": True}},
                    concurrency=supervisor.CONTRACT.REMOTE_PREFLIGHT_CONCURRENCY,
                    raw_root="raw/preflight/epoch-0001",
                    label="MINIMAL",
                )
            altered_stage = copy.deepcopy(checkpoint["stage"])
            altered_stage["total_operations"] += 1
            with self.assertRaises(supervisor.ArchiveFailure):
                supervisor.validate_stage(
                    archive,
                    raw_manifest,
                    altered_stage,
                    concurrency=supervisor.CONTRACT.REMOTE_PREFLIGHT_CONCURRENCY,
                    raw_root="raw/preflight/epoch-0001",
                    label="FABRICATED",
                )
            original_reader = supervisor.read_member_json

            def stale_receipt_hash(
                opened: tarfile.TarFile, name: str
            ) -> dict[str, object]:
                value = original_reader(opened, name)
                if name.endswith("/receipts/det-invalid-01.json"):
                    value = copy.deepcopy(value)
                    value["passed"] = False
                return value

            with (
                mock.patch.object(
                    supervisor,
                    "read_member_json",
                    side_effect=stale_receipt_hash,
                ),
                self.assertRaises(supervisor.ArchiveFailure),
            ):
                supervisor.validate_verifier_batch(
                    archive,
                    manifest,
                    raw_manifest,
                    checkpoint["verifier"],
                    lane="preflight",
                    epoch=1,
                    campaign_id=CAMPAIGN_ID,
                    label="FABRICATED",
                )
            with self.assertRaises(supervisor.ArchiveFailure):
                supervisor.validate_trace_progress(
                    archive,
                    manifest,
                    {"green": True, "checks": {"projection": True}},
                )

    def test_result_and_failure_are_never_green(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdh3-supervisor-test.") as temporary:
            archive, final_state = build_archive(Path(temporary), "BOTH")
            config = self.make_config(Path(temporary), "both")
            observed, details = supervisor.validate_archive(
                archive,
                final_state,
                config,
            )
            self.assertEqual(observed, supervisor.PARTIAL_ARCHIVE)
            self.assertIn("RESULT_FAILURE_NOT_EXCLUSIVE", details["reason"])

    def test_corrupt_manifest_is_partial_archive(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdh3-supervisor-test.") as temporary:
            archive, final_state = build_archive(
                Path(temporary),
                supervisor.BLOCKED_COMPLETE,
                corrupt_manifest=True,
            )
            config = self.make_config(Path(temporary), "corrupt")
            observed, details = supervisor.validate_archive(
                archive,
                final_state,
                config,
            )
            self.assertEqual(observed, supervisor.PARTIAL_ARCHIVE)
            self.assertIn("MANIFEST_HASH_INVALID", details["reason"])

    def test_mocked_supervise_state_matrix_and_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdh3-supervisor-test.") as temporary:
            root = Path(temporary)
            campaign_states = (
                supervisor.GREEN_PENDING_FINAL_GATE,
                supervisor.BLOCKED_COMPLETE,
                supervisor.PARTIAL_ARCHIVE,
            )
            for index, campaign_state in enumerate(campaign_states):
                with self.subTest(campaign_state=campaign_state):
                    config = self.make_config(root, f"matrix-{index}")
                    with (
                        mock.patch.object(supervisor, "wait_for_terminal", return_value=True),
                        mock.patch.object(supervisor, "package_remote"),
                        mock.patch.object(supervisor, "retrieve", return_value=(root / "a", root / "s")),
                        mock.patch.object(
                            supervisor,
                            "validate_archive",
                            return_value=(campaign_state, {"tested": True}),
                        ),
                        mock.patch.object(
                            supervisor,
                            "delete_exact_worker",
                            return_value={"exact_id_absent": True, "campaign_active": []},
                        ),
                    ):
                        observed, exit_code = supervisor.supervise(config)
                    self.assertEqual(observed, campaign_state)
                    self.assertEqual(exit_code, supervisor.EXIT_CODES[campaign_state])

            config = self.make_config(root, "matrix-absent")
            with (
                mock.patch.object(supervisor, "wait_for_terminal", return_value=False),
                mock.patch.object(supervisor, "delete_exact_worker", return_value={}),
            ):
                observed, exit_code = supervisor.supervise(config)
            self.assertEqual(observed, supervisor.ABSENT_RESULT)
            self.assertEqual(exit_code, supervisor.EXIT_CODES[supervisor.ABSENT_RESULT])

            config = self.make_config(root, "matrix-transport")
            with (
                mock.patch.object(supervisor, "wait_for_terminal", return_value=True),
                mock.patch.object(
                    supervisor,
                    "package_remote",
                    side_effect=supervisor.TransportFailure("SSH_DOWN"),
                ),
                mock.patch.object(supervisor, "delete_exact_worker", return_value={}),
            ):
                observed, exit_code = supervisor.supervise(config)
            self.assertEqual(observed, supervisor.TRANSPORT_FAILURE)
            self.assertEqual(exit_code, supervisor.EXIT_CODES[supervisor.TRANSPORT_FAILURE])

            config = self.make_config(root, "matrix-teardown")
            with (
                mock.patch.object(supervisor, "wait_for_terminal", return_value=False),
                mock.patch.object(
                    supervisor,
                    "delete_exact_worker",
                    side_effect=supervisor.SupervisorFailure("NO_ABSENCE_PROOF"),
                ),
            ):
                observed, exit_code = supervisor.supervise(config)
            self.assertEqual(observed, supervisor.TEARDOWN_UNPROVEN)
            self.assertEqual(exit_code, supervisor.EXIT_CODES[supervisor.TEARDOWN_UNPROVEN])
            self.assertNotEqual(supervisor.EXIT_CODES[supervisor.BLOCKED_COMPLETE], 0)

    def test_retrieve_file_is_atomic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdh3-supervisor-test.") as temporary:
            root = Path(temporary)
            config = self.make_config(root, "atomic")

            def copy_to_partial(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                destination = Path(command[-1])
                self.assertTrue(destination.name.endswith(".part"))
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"payload")
                return subprocess.CompletedProcess(command, 0, "", "")

            with mock.patch.object(supervisor, "run_command", side_effect=copy_to_partial):
                destination = supervisor.retrieve_file(config, "final-state.json")
            self.assertEqual(destination.read_bytes(), b"payload")
            self.assertFalse(destination.with_name(destination.name + ".part").exists())

    def test_teardown_requires_exact_404_and_all_inventory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdh3-supervisor-test.") as temporary:
            root = Path(temporary)
            config = self.make_config(root, "delete")
            log = supervisor.ChainLog(config.log)
            responses = [
                subprocess.CompletedProcess([], 0, "{}", ""),
                subprocess.CompletedProcess(
                    [],
                    1,
                    '{"status":404,"message":"Pod not found"}',
                    "",
                ),
                subprocess.CompletedProcess([], 0, "[]", ""),
            ]
            calls: list[list[str]] = []

            def provider(_: supervisor.Config, arguments: list[str]) -> subprocess.CompletedProcess[str]:
                calls.append(arguments)
                return responses.pop(0)

            with mock.patch.object(supervisor, "provider_command", side_effect=provider):
                proof = supervisor.delete_exact_worker(config, log)
            self.assertTrue(proof["exact_id_absent"])
            self.assertEqual(calls[2], ["pod", "list", "--all", "--output", "json"])
            vague = subprocess.CompletedProcess([], 1, "", "pod not found")
            self.assertFalse(supervisor.explicit_not_found(vague))
            arbitrary = subprocess.CompletedProcess(
                [],
                1,
                "upstream 404; retry later",
                '{"status":404,"message":"Billing invoice not found"}',
            )
            self.assertFalse(supervisor.explicit_not_found(arbitrary))
            string_code = subprocess.CompletedProcess(
                [],
                1,
                '{"status":"404","message":"Pod not found"}',
                "",
            )
            self.assertFalse(supervisor.explicit_not_found(string_code))
            mixed_streams = subprocess.CompletedProcess(
                [],
                1,
                '{"status":404,"message":"Pod not found"}',
                "provider warning",
            )
            self.assertFalse(supervisor.explicit_not_found(mixed_streams))
            runpodctl_v272 = subprocess.CompletedProcess(
                [],
                1,
                "",
                (
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
            )
            self.assertTrue(supervisor.explicit_not_found(runpodctl_v272))

    def test_command_timeout_is_transport_failure(self) -> None:
        with mock.patch.object(
            supervisor.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["ssh"], 1),
        ):
            with self.assertRaises(supervisor.TransportFailure):
                supervisor.run_command(["ssh"], timeout=1)


if __name__ == "__main__":
    unittest.main()
