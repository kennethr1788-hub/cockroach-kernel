from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from cockroach_kernel import recovery_surface as surface
from p7_runtime import records as p7


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): digest(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


class Scenario:
    def __init__(
        self,
        files: dict[str, bytes] | None = None,
        lost_paths: list[str] | None = None,
        *,
        no_loss: bool = False,
        request_id: str = "request-r3-001",
    ) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="ck-r3-test-")
        self.root = Path(self._temporary.name).resolve()
        self.workspace = self.root / "workspace"
        self.representations = self.root / "representations"
        self.custody = self.root / "custody"
        self.output = self.root / "output"
        for path in (self.workspace, self.representations, self.custody, self.output):
            path.mkdir()
        self.request_path = self.root / "request.json"
        self.files = files or {
            "notes/human.md": b"independently saved edit\n",
            "src/feature.py": b"def recovered():\n    return 'working'\n",
            "state/uncommitted.txt": b"uncommitted useful work\n",
        }
        self.lost_paths = sorted(self.files if lost_paths is None else lost_paths)
        entries = [
            {
                "path": path,
                "content_hash": digest(raw),
                "executable": False,
                "is_symlink": False,
            }
            for path, raw in sorted(self.files.items())
        ]
        self.manifest = {
            "version": p7.VERSION,
            "manifest_id": "manifest-r3-001",
            "task_id": "task-r3-001",
            "files": entries,
        }
        events = [
            {
                "sequence": index,
                "event": label,
                "event_hash": digest(label.encode("utf-8")),
            }
            for index, label in enumerate(("committed", "uncommitted", "human-saved"))
        ]
        previous = ""
        for event in events:
            previous = p7.sha256_hex({"previous": previous, "event": event})
        self.trajectory = {
            "version": p7.VERSION,
            "receipt_id": "trajectory-r3-001",
            "task_id": "task-r3-001",
            "manifest_hash": p7.sha256_hex(self.manifest),
            "events": events,
            "trajectory_hash": previous,
        }
        self.quorum = {"decision": "PROMOTE"}
        self.context = {
            "manifest": self.manifest,
            "trajectory_receipt": self.trajectory,
            "policy_version": "policy-r3-v1",
            "quorum_decision_hash": p7.sha256_hex(self.quorum),
        }
        self.candidate = self.make_candidate("candidate-r3-strong", len(events))
        self.decision = p7.select_candidate([self.candidate], self.context)
        self.warrant = p7.make_warrant(
            "warrant-r3-001",
            self.manifest["task_id"],
            self.candidate["candidate_id"],
            self.decision,
        )
        self.loss_receipt = {
            "version": p7.VERSION,
            "receipt_id": "loss-r3-001",
            "task_id": self.manifest["task_id"],
            "manifest_hash": p7.sha256_hex(self.manifest),
            "lost_paths": self.lost_paths,
            "absence_hash": p7.sha256_hex(
                {"lost_paths": self.lost_paths, "observed": "absent"}
            ),
        }
        self.request = {
            "version": surface.REQUEST_VERSION,
            "request_id": request_id,
            "context": self.context,
            "loss_receipt": None if no_loss else self.loss_receipt,
            "candidates": [self.candidate],
            "warrant": self.warrant,
        }
        self.write_request()
        self.write_representations(self.candidate)
        for path, raw in self.files.items():
            if path not in self.lost_paths:
                target = self.workspace.joinpath(*path.split("/"))
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)

    def cleanup(self) -> None:
        self._temporary.cleanup()

    def make_candidate(self, candidate_id: str, prefix_length: int) -> dict:
        test_path = "src/feature.py" if "src/feature.py" in self.files else sorted(self.files)[0]
        return {
            "version": p7.VERSION,
            "candidate_id": candidate_id,
            "task_id": self.manifest["task_id"],
            "provenance": {"source": "synthetic-public-fixture"},
            "source_receipt_hash": p7.sha256_hex(self.trajectory),
            "policy_version": self.context["policy_version"],
            "policy_veto": False,
            "tampered": False,
            "quorum_decision": self.quorum,
            "prefix_length": prefix_length,
            "integrity_hash": p7.trajectory_integrity_hash(
                self.trajectory["events"], prefix_length
            ),
            "declared_paths": sorted(self.files),
            "file_hashes": {path: digest(raw) for path, raw in sorted(self.files.items())},
            "executable_test": {
                "test_id": "test-r3-001",
                "path": test_path,
                "feature_hash": digest(self.files[test_path]),
                "passed": True,
            },
        }

    def write_request(self) -> None:
        self.request_path.write_bytes(surface.canonical_json(self.request))

    def write_representations(self, candidate: dict) -> None:
        base = self.representations / candidate["candidate_id"]
        for path, raw in self.files.items():
            target = base.joinpath(*path.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)

    def new_output(self, name: str) -> Path:
        path = self.root / name
        path.mkdir()
        return path

    def kwargs(self, output: Path | None = None) -> dict:
        return {
            "request_path": self.request_path,
            "sandbox_root": self.root,
            "workspace": self.workspace,
            "representation_root": self.representations,
            "custody_root": self.custody,
            "output_root": output or self.output,
        }

    def cli(self, output: Path) -> list[str]:
        return [
            sys.executable,
            "-m",
            "cockroach_kernel.cli",
            "recover",
            "--request",
            str(self.request_path),
            "--sandbox-root",
            str(self.root),
            "--workspace",
            str(self.workspace),
            "--representation-root",
            str(self.representations),
            "--custody-root",
            str(self.custody),
            "--output-root",
            str(output),
        ]


class RecoverySurfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenarios: list[Scenario] = []

    def tearDown(self) -> None:
        for scenario in self.scenarios:
            scenario.cleanup()

    def scenario(self, *args, **kwargs) -> Scenario:
        value = Scenario(*args, **kwargs)
        self.scenarios.append(value)
        return value

    def test_complete_loss_promotes_committed_uncommitted_and_human_saved_bytes(self):
        scenario = self.scenario()
        status, summary = surface.execute_recovery(**scenario.kwargs())
        self.assertEqual(status, 0)
        self.assertEqual(summary["verdict"], "PROMOTE")
        self.assertTrue(summary["fresh_context_continued"])
        self.assertEqual(tree(scenario.workspace), {
            path: digest(raw) for path, raw in sorted(scenario.files.items())
        })
        receipt = json.loads((scenario.output / "promotion-receipt.json").read_bytes())
        self.assertEqual(receipt["promoted_paths"], sorted(scenario.files))

    def test_partial_loss_selects_strongest_candidate_and_preserves_survivor(self):
        scenario = self.scenario(lost_paths=["src/feature.py"])
        weak = scenario.make_candidate("candidate-r3-weak", 1)
        scenario.request["candidates"] = [weak, scenario.candidate]
        scenario.decision = p7.select_candidate(scenario.request["candidates"], scenario.context)
        scenario.warrant = p7.make_warrant(
            "warrant-r3-001",
            scenario.manifest["task_id"],
            scenario.candidate["candidate_id"],
            scenario.decision,
        )
        scenario.request["warrant"] = scenario.warrant
        scenario.write_request()
        survivor_before = (scenario.workspace / "notes/human.md").read_bytes()
        status, summary = surface.execute_recovery(**scenario.kwargs())
        self.assertEqual(status, 0)
        self.assertEqual(summary["verdict"], "PROMOTE")
        self.assertEqual(
            json.loads((scenario.output / "decision.json").read_bytes())["candidate_id"],
            "candidate-r3-strong",
        )
        self.assertEqual((scenario.workspace / "notes/human.md").read_bytes(), survivor_before)

    def test_preservation_proof_is_recorded_in_mutation_manifest(self):
        scenario = self.scenario(lost_paths=["src/feature.py"])
        status, summary = surface.execute_recovery(**scenario.kwargs())
        self.assertEqual(status, 0)
        mutation = json.loads((scenario.output / "mutation-manifest.json").read_bytes())
        self.assertTrue(mutation["preservation"]["verified"])
        self.assertIn("notes/human.md", mutation["preservation"]["preserved_paths"])
        self.assertEqual(mutation["preservation"]["changed_paths"], [])

    def test_preservation_mismatch_fails_closed_after_promotion(self):
        scenario = self.scenario(lost_paths=["src/feature.py"])
        original = surface._promote_staged

        def mutate_after_promotion(*args, **kwargs):
            promoted = original(*args, **kwargs)
            (scenario.workspace / "notes/human.md").write_bytes(b"changed\n")
            return promoted

        with mock.patch.object(surface, "_promote_staged", mutate_after_promotion):
            with self.assertRaisesRegex(surface.SurfaceError, "PRESERVATION_PROOF_FAILED"):
                surface.execute_recovery(**scenario.kwargs())

    def test_clean_no_loss_is_no_action_and_does_not_consume_warrant(self):
        scenario = self.scenario(no_loss=True)
        before = tree(scenario.workspace)
        status, summary = surface.execute_recovery(**scenario.kwargs())
        self.assertEqual(status, 0)
        self.assertEqual(summary["verdict"], "NO_ACTION")
        self.assertEqual(before, tree(scenario.workspace))
        self.assertFalse((scenario.custody / "warrants").exists())

    def test_representation_hash_tamper_is_invalid_with_zero_workspace_mutation(self):
        scenario = self.scenario()
        before = tree(scenario.workspace)
        target = scenario.representations / scenario.candidate["candidate_id"] / "src/feature.py"
        target.write_bytes(b"tampered\n")
        with self.assertRaisesRegex(surface.SurfaceError, "REPRESENTATION_HASH_MISMATCH"):
            surface.execute_recovery(**scenario.kwargs())
        self.assertEqual(before, tree(scenario.workspace))

    def test_tampered_candidate_refuses_with_zero_workspace_mutation(self):
        scenario = self.scenario()
        scenario.request["candidates"][0]["tampered"] = True
        scenario.write_request()
        before = tree(scenario.workspace)
        status, summary = surface.execute_recovery(**scenario.kwargs())
        self.assertEqual(status, 1)
        self.assertEqual(summary["reason"], p7.NO_SURVIVING_CANDIDATE)
        self.assertEqual(before, tree(scenario.workspace))

    def test_replay_is_refused_across_fresh_process(self):
        scenario = self.scenario()
        first = subprocess.run(
            scenario.cli(scenario.output), capture_output=True, text=True, check=False
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        first_tree = tree(scenario.workspace)
        second_output = scenario.new_output("output-replay")
        second = subprocess.run(
            scenario.cli(second_output), capture_output=True, text=True, check=False
        )
        self.assertEqual(second.returncode, 1, second.stderr)
        self.assertEqual(json.loads(second.stdout)["reason"], p7.WARRANT_REPLAY)
        self.assertEqual(first_tree, tree(scenario.workspace))

    def test_interruption_after_consumption_remains_consumed_and_unreplayable(self):
        scenario = self.scenario()
        with self.assertRaisesRegex(surface.SurfaceError, "PROMOTION_INTERRUPTED"):
            surface.execute_recovery(**scenario.kwargs(), fault="after-consume")
        sidecar = json.loads(
            (scenario.custody / "warrants" / "warrant-r3-001.json").read_bytes()
        )
        self.assertEqual(sidecar["state"], "CONSUMED")
        replay_output = scenario.new_output("output-replay")
        status, summary = surface.execute_recovery(**scenario.kwargs(replay_output))
        self.assertEqual(status, 1)
        self.assertEqual(summary["reason"], p7.WARRANT_REPLAY)
        self.assertEqual(tree(scenario.workspace), {})

    def test_malformed_unknown_and_unsupported_requests_fail_before_mutation(self):
        cases = (
            (lambda request: request.update({"unknown": True}), "MALFORMED_RECORD"),
            (lambda request: request.update({"version": "future-v9"}), p7.UNSUPPORTED_SCHEMA),
            (
                lambda request: request["context"]["manifest"]["files"][0].update(
                    {"path": "../escape"}
                ),
                p7.UNSAFE_PATH,
            ),
        )
        for mutate, reason in cases:
            scenario = self.scenario()
            before = tree(scenario.workspace)
            mutate(scenario.request)
            scenario.write_request()
            with self.subTest(reason=reason), self.assertRaisesRegex(
                surface.SurfaceError, reason
            ):
                surface.execute_recovery(**scenario.kwargs())
            self.assertEqual(before, tree(scenario.workspace))

    def test_noncanonical_json_and_duplicate_keys_are_rejected(self):
        for raw in (b'{"version": "x"}', b'{"a":1,"a":2}'):
            scenario = self.scenario()
            scenario.request_path.write_bytes(raw)
            with self.subTest(raw=raw), self.assertRaisesRegex(
                surface.SurfaceError, "REQUEST_NOT_CANONICAL"
            ):
                surface.execute_recovery(**scenario.kwargs())

    def test_symlink_executable_and_root_overlap_are_rejected(self):
        scenario = self.scenario()
        represented = (
            scenario.representations / scenario.candidate["candidate_id"] / "src/feature.py"
        )
        represented.unlink()
        represented.symlink_to(scenario.request_path)
        with self.assertRaisesRegex(surface.SurfaceError, "REPRESENTATION_UNSAFE"):
            surface.execute_recovery(**scenario.kwargs())

        executable = self.scenario()
        executable_file = (
            executable.representations
            / executable.candidate["candidate_id"]
            / "src/feature.py"
        )
        executable_file.chmod(0o700)
        with self.assertRaisesRegex(surface.SurfaceError, "REPRESENTATION_UNSAFE"):
            surface.execute_recovery(**executable.kwargs())

        overlap = self.scenario()
        with self.assertRaisesRegex(surface.SurfaceError, "ROOT_TOPOLOGY_UNSAFE"):
            surface.execute_recovery(**overlap.kwargs(overlap.workspace))

        workspace_link = self.scenario()
        (workspace_link.workspace / "src").symlink_to(workspace_link.output)
        with self.assertRaisesRegex(surface.SurfaceError, "ROOT_TOPOLOGY_UNSAFE"):
            surface.execute_recovery(**workspace_link.kwargs())

    def test_home_and_request_root_overlap_are_rejected_without_mutation(self):
        with self.assertRaisesRegex(surface.SurfaceError, "ROOT_TOPOLOGY_UNSAFE"):
            surface.validate_roots(
                Path(__file__),
                Path.home(),
                Path.home(),
                Path.home(),
                Path.home(),
                Path.home(),
            )
        scenario = self.scenario()
        nested_request = scenario.representations / "request.json"
        nested_request.write_bytes(scenario.request_path.read_bytes())
        with self.assertRaisesRegex(surface.SurfaceError, "ROOT_TOPOLOGY_UNSAFE"):
            surface.execute_recovery(
                **dict(scenario.kwargs(), request_path=nested_request)
            )

    def test_absolute_backslash_nul_and_executable_record_paths_reject(self):
        values = ("/absolute", "dir\\file", "nul\x00file")
        for value in values:
            scenario = self.scenario()
            scenario.request["context"]["manifest"]["files"][0]["path"] = value
            scenario.write_request()
            with self.subTest(value=value), self.assertRaisesRegex(
                surface.SurfaceError, p7.UNSAFE_PATH
            ):
                surface.execute_recovery(**scenario.kwargs())
        scenario = self.scenario()
        scenario.request["context"]["manifest"]["files"][0]["executable"] = True
        scenario.write_request()
        with self.assertRaisesRegex(surface.SurfaceError, p7.UNSAFE_PATH):
            surface.execute_recovery(**scenario.kwargs())

    def test_missing_representation_is_recorded_without_inventing_bytes(self):
        scenario = self.scenario()
        missing = "notes/human.md"
        (scenario.representations / scenario.candidate["candidate_id"] / missing).unlink()
        status, summary = surface.execute_recovery(**scenario.kwargs())
        self.assertEqual(status, 0)
        self.assertEqual(summary["verdict"], "PROMOTE")
        ledger = json.loads((scenario.output / "unrecovered-ledger.json").read_bytes())
        self.assertIn(
            {"path": missing, "reason": "NO_PROVEN_REPRESENTATION"},
            ledger["unrecovered_items"],
        )
        self.assertFalse((scenario.workspace / missing).exists())

    def test_file_and_aggregate_representation_limits_fail_closed(self):
        too_large = self.scenario(
            files={"src/feature.py": b"x" * (surface.MAX_FILE_BYTES + 1)}
        )
        before = tree(too_large.workspace)
        with self.assertRaisesRegex(surface.SurfaceError, "AGGREGATE_LIMIT_EXCEEDED"):
            surface.execute_recovery(**too_large.kwargs())
        self.assertEqual(before, tree(too_large.workspace))

        many_files = {
            f"src/file-{index:02d}.txt": bytes([65 + index]) * surface.MAX_FILE_BYTES
            for index in range(17)
        }
        aggregate = self.scenario(files=many_files)
        before = tree(aggregate.workspace)
        with self.assertRaisesRegex(surface.SurfaceError, "AGGREGATE_LIMIT_EXCEEDED"):
            surface.execute_recovery(**aggregate.kwargs())
        self.assertEqual(before, tree(aggregate.workspace))

    def test_semantic_outputs_are_identical_across_fresh_roots(self):
        first = self.scenario()
        second = self.scenario()
        status_a, _ = surface.execute_recovery(**first.kwargs())
        status_b, _ = surface.execute_recovery(**second.kwargs())
        self.assertEqual((status_a, status_b), (0, 0))
        self.assertEqual(tree(first.output), tree(second.output))

    def test_atomic_interruption_consumes_warrant_and_never_overwrites(self):
        scenario = self.scenario()
        with self.assertRaisesRegex(surface.SurfaceError, "PROMOTION_INTERRUPTED"):
            surface.execute_recovery(**scenario.kwargs(), fault="after-first-file")
        sidecar = json.loads(
            (scenario.custody / "warrants" / "warrant-r3-001.json").read_bytes()
        )
        self.assertEqual(sidecar["state"], "CONSUMED")
        self.assertEqual(len(tree(scenario.workspace)), 1)
        replay_output = scenario.new_output("output-atomic-replay")
        status, summary = surface.execute_recovery(**scenario.kwargs(replay_output))
        self.assertEqual(status, 1)
        self.assertEqual(summary["reason"], p7.WARRANT_REPLAY)

    def test_existing_lost_path_refuses_without_overwrite(self):
        scenario = self.scenario()
        target = scenario.workspace / "src/feature.py"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"independent survivor\n")
        before = tree(scenario.workspace)
        status, summary = surface.execute_recovery(**scenario.kwargs())
        self.assertEqual(status, 1)
        self.assertEqual(summary["reason"], "WORKSPACE_PATH_CONFLICT")
        self.assertEqual(before, tree(scenario.workspace))

    def test_help_exposes_typed_surface_without_test_fault_control(self):
        result = subprocess.run(
            [sys.executable, "-m", "cockroach_kernel.cli", "recover", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        for flag in (
            "--request",
            "--sandbox-root",
            "--workspace",
            "--representation-root",
            "--custody-root",
            "--output-root",
        ):
            self.assertIn(flag, result.stdout)
        self.assertNotIn("fault", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
