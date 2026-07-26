"""Focused P7 record, selection, warrant, and fresh-context tests."""
from __future__ import annotations

import copy
import os
import tempfile
import unittest
from pathlib import Path

import fresh_context as fc
import make_fixtures as fx
import records as rec

FIXTURES = fx.FIXTURE_DIR


def load(name: str):
    return rec.load_canonical(os.path.join(FIXTURES, name + ".json"))


def context():
    manifest = load("manifest")
    trajectory = load("trajectory-receipt")
    quorum = load("quorum-decision")
    return fx.build_context(manifest, trajectory, quorum)


class TestCanonicalAndPaths(unittest.TestCase):
    def test_canonical_sorted_compact(self):
        self.assertEqual(rec.canonical_json({"b": 1, "a": 2}), b'{"a":2,"b":1}')

    def test_record_cap(self):
        with self.assertRaisesRegex(rec.RecoveryError, "RECORD_TOO_LARGE"):
            rec.canonical_json({"pad": "x" * rec.MAX_RECORD_BYTES})

    def test_fixtures_are_canonical(self):
        for name in os.listdir(FIXTURES):
            self.assertIsNotNone(rec.load_canonical(os.path.join(FIXTURES, name)))

    def test_unknown_field(self):
        value = load("candidate-alpha")
        value["hidden"] = True
        with self.assertRaisesRegex(rec.RecoveryError, "UNKNOWN_FIELD"):
            rec.validate_candidate(value)

    def test_unsafe_path_classes(self):
        for path in ("", "/abs", "a//b", "a/./b", "a/../b", "a\\b", "a\x00b"):
            with self.subTest(path=repr(path)):
                with self.assertRaisesRegex(rec.RecoveryError, rec.UNSAFE_PATH):
                    rec.validate_relative_path(path)

    def test_symlink_and_executable_flags(self):
        for field in ("is_symlink", "executable"):
            entry = copy.deepcopy(load("manifest")["files"][0])
            entry[field] = True
            with self.assertRaisesRegex(rec.RecoveryError, rec.UNSAFE_PATH):
                rec.validate_file_entry(entry)

    def test_loss_receipt_exact_manifest_link(self):
        rec.validate_loss_receipt(load("loss-receipt"), load("manifest"))
        bad = load("loss-receipt")
        bad["lost_paths"] = bad["lost_paths"][:-1]
        with self.assertRaisesRegex(rec.RecoveryError, "STALE_HASH|LOSS_MANIFEST_MISMATCH"):
            rec.validate_loss_receipt(bad, load("manifest"))


class TestSelection(unittest.TestCase):
    def test_maximum_prefix_wins(self):
        result = rec.select_candidate([load("candidate-beta"), load("candidate-alpha")], context())
        self.assertEqual((result["decision"], result["candidate_id"]),
                         ("PROMOTE", "cand-p7-alpha"))

    def test_order_independent(self):
        a = load("candidate-alpha")
        b = load("candidate-beta")
        self.assertEqual(rec.canonical_json(rec.select_candidate([a, b], context())),
                         rec.canonical_json(rec.select_candidate([b, a], context())))

    def test_canonical_id_tiebreak(self):
        a = load("candidate-alpha")
        z = copy.deepcopy(a)
        z["candidate_id"] = "cand-p7-zeta"
        z["executable_test"]["test_id"] = "exectest-cand-p7-zeta"
        result = rec.select_candidate([z, a], context())
        self.assertEqual(result["candidate_id"], "cand-p7-alpha")

    def test_no_candidate_refuses(self):
        result = rec.select_candidate([], context())
        self.assertEqual((result["decision"], result["reason"]),
                         ("REFUSE", rec.NO_SURVIVING_CANDIDATE))

    def test_each_refusal_vector(self):
        expected = {
            "candidate-policy-veto": rec.POLICY_VETO,
            "candidate-tampered": rec.TAMPERED_EVIDENCE,
            "candidate-unsupported-schema": rec.UNSUPPORTED_SCHEMA,
            "candidate-stale-policy": rec.STALE_POLICY,
            "candidate-missing-quorum": rec.MISSING_QUORUM,
            "candidate-failed-exec-test": rec.EXECUTABLE_TEST_FAILED,
            "candidate-unsafe-path": rec.UNSAFE_PATH,
        }
        for name, reason in expected.items():
            with self.subTest(name=name):
                self.assertEqual(rec.check_eligibility(load(name), context()), reason)
                result = rec.select_candidate([load(name)], context())
                self.assertEqual(result["reason"], rec.NO_SURVIVING_CANDIDATE)

    def test_malformed_candidate_refuses(self):
        bad = load("candidate-alpha")
        del bad["provenance"]
        self.assertEqual(rec.check_eligibility(bad, context()), rec.MALFORMED_RECORD)

    def test_malformed_context_fails_closed(self):
        self.assertEqual(rec.check_eligibility(load("candidate-alpha"), {}),
                         rec.MALFORMED_RECORD)
        with self.assertRaisesRegex(rec.RecoveryError, rec.MALFORMED_RECORD):
            rec.select_candidate([load("candidate-alpha")], {})

    def test_stale_source_receipt_refuses(self):
        bad = load("candidate-alpha")
        bad["source_receipt_hash"] = "0" * 64
        self.assertEqual(rec.check_eligibility(bad, context()), rec.TAMPERED_EVIDENCE)

    def test_surviving_content_hash_drift_refuses(self):
        bad = load("candidate-alpha")
        bad["file_hashes"]["src/feature.py"] = "0" * 64
        bad["executable_test"]["feature_hash"] = "0" * 64
        self.assertEqual(rec.check_eligibility(bad, context()), rec.TAMPERED_EVIDENCE)

    def test_five_repeat_semantics(self):
        candidates = [load("candidate-beta"), load("candidate-alpha")]
        runs = [rec.canonical_json(rec.select_candidate(candidates, context())) for _ in range(5)]
        self.assertEqual(len(set(runs)), 1)


class TestWarrant(unittest.TestCase):
    def setUp(self):
        self.decision = load("decision-promote")
        self.warrant = load("warrant-issued")
        self.harness = rec.RecoveryHarness()
        self.harness.register_warrant(self.warrant)

    def test_consumption_precedes_promotion(self):
        receipt = self.harness.recover(
            self.decision, self.warrant["warrant_id"],
            load("candidate-alpha")["declared_paths"])
        self.assertEqual(self.harness.warrant_state(self.warrant["warrant_id"]), "CONSUMED")
        self.assertEqual(receipt, load("promotion-receipt"))

    def test_replay_refuses(self):
        self.harness.recover(self.decision, self.warrant["warrant_id"])
        refusal = self.harness.recover(self.decision, self.warrant["warrant_id"])
        self.assertEqual(refusal["reason"], rec.WARRANT_REPLAY)

    def test_interrupt_consumes_without_promotion(self):
        with self.assertRaises(rec.RecoveryInterrupted):
            self.harness.recover(self.decision, self.warrant["warrant_id"],
                                 fault="interrupt")
        self.assertEqual(self.harness.warrant_state(self.warrant["warrant_id"]), "CONSUMED")
        self.assertIsNone(self.harness.promotion(self.decision["task_id"]))
        refusal = self.harness.recover(self.decision, self.warrant["warrant_id"])
        self.assertEqual(refusal["reason"], rec.WARRANT_REPLAY)

    def test_tampered_decision_does_not_consume(self):
        bad = copy.deepcopy(self.decision)
        bad["reason"] = "FORGED"
        refusal = self.harness.recover(bad, self.warrant["warrant_id"])
        self.assertEqual(refusal["reason"], rec.TAMPERED_EVIDENCE)
        self.assertEqual(self.harness.warrant_state(self.warrant["warrant_id"]), "ISSUED")

    def test_duplicate_warrant_rejected(self):
        with self.assertRaisesRegex(rec.RecoveryError, rec.WARRANT_REPLAY):
            self.harness.register_warrant(self.warrant)


class TestLinkageAndFreshContext(unittest.TestCase):
    def test_exact_receipt_chain(self):
        manifest = load("manifest")
        trajectory = load("trajectory-receipt")
        candidate = load("candidate-alpha")
        decision = load("decision-promote")
        warrant = load("warrant-issued")
        promotion = load("promotion-receipt")
        self.assertEqual(trajectory["manifest_hash"], rec.sha256_hex(manifest))
        self.assertEqual(candidate["source_receipt_hash"], rec.sha256_hex(trajectory))
        self.assertEqual(warrant["decision_hash"], rec.sha256_hex(decision))
        self.assertEqual(promotion["decision_hash"], rec.sha256_hex(decision))
        self.assertEqual(promotion["warrant_id"], warrant["warrant_id"])

    def test_unrecovered_items_are_explicit(self):
        ledger = load("unrecovered-ledger")
        self.assertEqual(ledger["unrecovered_items"],
                         [{"path": "data/state.json", "reason": "NO_PROVEN_REPRESENTATION"}])

    def test_fresh_context_passes_without_hidden_state(self):
        self.assertEqual(fc.verify_continuation(load("decision-promote"),
                                                load("candidate-alpha")),
                         (True, "FRESH_CONTEXT_PASS"))

    def test_fresh_context_refuses_wrong_candidate(self):
        self.assertEqual(fc.verify_continuation(load("decision-promote"),
                                                load("candidate-beta")),
                         (False, "CANDIDATE_MISMATCH"))

    def test_fresh_context_refuses_feature_drift(self):
        bad = load("candidate-alpha")
        bad["executable_test"]["feature_hash"] = "0" * 64
        self.assertEqual(fc.verify_continuation(load("decision-promote"), bad),
                         (False, "FEATURE_MISMATCH"))

    def test_five_repeat_fresh_context(self):
        runs = [fc.verify_continuation(load("decision-promote"),
                                       load("candidate-alpha")) for _ in range(5)]
        self.assertEqual(len(set(runs)), 1)

    def test_fresh_process_workspace_bytes(self):
        candidate = load("candidate-alpha")
        with tempfile.TemporaryDirectory(dir=FIXTURES) as root:
            target = Path(root) / candidate["executable_test"]["path"]
            target.parent.mkdir(parents=True)
            target.write_bytes(fx.FILE_CONTENTS[candidate["executable_test"]["path"]])
            self.assertEqual(fc.verify_workspace(load("decision-promote"),
                                                 candidate, root),
                             (True, "FRESH_CONTEXT_PASS"))
            target.write_bytes(b"tampered")
            self.assertEqual(fc.verify_workspace(load("decision-promote"),
                                                 candidate, root),
                             (False, "FEATURE_MISMATCH"))


if __name__ == "__main__":
    unittest.main()
