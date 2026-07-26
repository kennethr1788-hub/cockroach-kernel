"""Offline tests for the P9 pure standard-library Lambda evaluator."""
from __future__ import annotations

import ast
import os
import unittest

import lambda_handler as lh
import records as r

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_MODULES = ("records", "context_vector", "lambda_handler", "mock_transports")

# Imports that must never appear in any P9 schema/evaluator/mock module:
# network, process, environment, filesystem, persistence, randomness, clock,
# and cloud SDK surfaces.
FORBIDDEN_IMPORTS = frozenset({
    "os", "sys", "socket", "ssl", "urllib", "http", "ftplib", "smtplib",
    "telnetlib", "subprocess", "ctypes", "pathlib", "shutil", "importlib",
    "asyncio", "threading", "multiprocessing", "signal", "time", "datetime",
    "random", "secrets", "tempfile", "glob", "io", "pickle", "shelve",
    "sqlite3", "venv", "getpass", "keyring", "boto3", "botocore", "requests",
    "psycopg", "psycopg2", "pg8000",
})


def make_features(**overrides):
    features = {
        "event_count": 3,
        "approvals": 2,
        "refusals": 0,
        "context_relevance": 0.75,
        "quorum_met": True,
        "policy_veto": False,
        "tampered": False,
        "unsafe": False,
        "warrant_consumed": False,
    }
    features.update(overrides)
    return features


def make_request(**overrides):
    kwargs = dict(
        request_id="p9-camp-001-req-001",
        task_id="p9-camp-001-task-001",
        candidate_id="p9-camp-001-cand-001",
        trajectory_hash=HASH_A,
        candidate_hash=HASH_B,
        policy_hash=HASH_C,
        features=make_features(),
    )
    kwargs.update(overrides)
    return r.make_request(**kwargs)


def module_imports(module_name):
    path = os.path.join(MODULE_DIR, module_name + ".py")
    with open(path, "r", encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module and node.module != "__future__":
                names.add(node.module.split(".")[0])
    return names


class TestEvaluate(unittest.TestCase):
    def test_happy_path_advisory_response(self):
        request = make_request()
        response = lh.evaluate(request)
        r.validate_response(response)
        self.assertEqual(response["status"], "ADVISORY")
        self.assertTrue(r.response_matches_request(request, response))
        codes = [obs["code"] for obs in response["observations"]]
        self.assertEqual(codes, ["EVALUATION_COMPLETE"])

    def test_deterministic_repeat_evaluation(self):
        request = make_request()
        first = lh.evaluate(request)
        second = lh.evaluate(request)
        self.assertEqual(r.canonical_json(first), r.canonical_json(second))

    def test_all_signal_codes_derived(self):
        features = make_features(
            quorum_met=False, policy_veto=True, tampered=True, unsafe=True,
            warrant_consumed=True, context_relevance=0.1,
        )
        response = lh.evaluate(make_request(features=features))
        codes = [obs["code"] for obs in response["observations"]]
        self.assertEqual(codes, [
            "POLICY_VETO_SIGNAL", "TAMPER_SIGNAL", "UNSAFE_SIGNAL",
            "WARRANT_CONSUMED_SIGNAL", "QUORUM_SHORTFALL_SIGNAL",
            "CONTEXT_LOW_SIGNAL", "EVALUATION_COMPLETE",
        ])
        r.validate_response(response)

    def test_context_threshold_boundary(self):
        at_threshold = lh.evaluate(make_request(features=make_features(context_relevance=0.5)))
        self.assertNotIn("CONTEXT_LOW_SIGNAL",
                         [obs["code"] for obs in at_threshold["observations"]])
        below = lh.evaluate(make_request(features=make_features(context_relevance=0.49)))
        self.assertIn("CONTEXT_LOW_SIGNAL",
                      [obs["code"] for obs in below["observations"]])

    def test_response_is_advisory_only(self):
        features = make_features(quorum_met=False, policy_veto=True, tampered=True,
                                 unsafe=True, warrant_consumed=True,
                                 context_relevance=0.0)
        response = lh.evaluate(make_request(features=features))
        self.assertEqual(response["status"], "ADVISORY")
        self.assertFalse(r.contains_authority_marker(response))
        self.assertEqual(set(response), r.RESPONSE_FIELDS)

    def test_context_argument_is_never_read(self):
        request = make_request()
        expected = lh.lambda_handler(request, None)
        for context in (object(), {"aws_request_id": "x"}, 42):
            with self.subTest(context=type(context).__name__):
                self.assertEqual(r.canonical_json(lh.lambda_handler(request, context)),
                                 r.canonical_json(expected))

    def test_event_must_be_a_dict(self):
        with self.assertRaisesRegex(r.CloudError, "MALFORMED_RECORD"):
            lh.lambda_handler(["not-a-dict"], None)

    def test_unknown_field_fails_closed(self):
        bad = dict(make_request(), extra="field")
        with self.assertRaisesRegex(r.CloudError, "UNKNOWN_FIELD"):
            lh.evaluate(bad)

    def test_wrong_type_fails_closed(self):
        bad = make_request()
        bad["features"]["quorum_met"] = "yes"
        bad["request_hash"] = r.sha256_hex(r.request_body(bad))
        with self.assertRaisesRegex(r.CloudError, "WRONG_TYPE"):
            lh.evaluate(bad)

    def test_stale_hash_fails_closed(self):
        bad = make_request()
        bad["features"]["approvals"] = 999
        with self.assertRaisesRegex(r.CloudError, "STALE_HASH"):
            lh.evaluate(bad)

    def test_no_decision_is_ever_emitted(self):
        # Even under maximally damning evidence the output stays advisory.
        features = make_features(quorum_met=False, policy_veto=True, tampered=True,
                                 unsafe=True, warrant_consumed=True,
                                 context_relevance=0.0, refusals=1000)
        response = lh.evaluate(make_request(features=features))
        for key in ("decision", "verdict", "outcome", "action", "promote",
                    "refuse", "invalid"):
            self.assertNotIn(key, response)


class TestForbiddenImports(unittest.TestCase):
    def test_no_forbidden_imports_in_any_module(self):
        for module in SCHEMA_MODULES:
            with self.subTest(module=module):
                imported = module_imports(module)
                self.assertEqual(imported & FORBIDDEN_IMPORTS, set())

    def test_lambda_handler_imports_only_typing_and_records(self):
        self.assertEqual(module_imports("lambda_handler"), {"typing", "records"})

    def test_lambda_handler_namespace_has_no_network_surface(self):
        for name in ("os", "sys", "socket", "urllib", "http", "subprocess",
                     "boto3", "requests"):
            self.assertNotIn(name, vars(lh))

    def test_mock_transport_modules_import_no_forbidden_names(self):
        imported = module_imports("mock_transports")
        self.assertLessEqual(imported,
                             {"copy", "re", "typing", "lambda_handler", "records"})


if __name__ == "__main__":
    unittest.main()
