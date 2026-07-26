"""Offline tests for the P9 canonical request/response records schema."""
from __future__ import annotations

import copy
import unittest

import records as r

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


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


def make_response(request=None, observations=None):
    request = request if request is not None else make_request()
    if observations is None:
        observations = [{
            "code": "EVALUATION_COMPLETE",
            "severity": "INFO",
            "message": "advisory evaluation complete",
        }]
    return r.make_response(request, observations)


class TestCanonicalJson(unittest.TestCase):
    def test_byte_exact_encoding(self):
        self.assertEqual(r.canonical_json({"b": 1, "a": 2}), b'{"a":2,"b":1}')

    def test_utf8_sorted_and_compact(self):
        encoded = r.canonical_json({"z": "é", "a": [1, 2]})
        self.assertEqual(encoded, '{"a":[1,2],"z":"é"}'.encode("utf-8"))

    def test_nan_rejected(self):
        with self.assertRaisesRegex(r.CloudError, "MALFORMED_RECORD"):
            r.canonical_json({"x": float("nan")})

    def test_size_cap_enforced(self):
        with self.assertRaisesRegex(r.CloudError, "RECORD_TOO_LARGE"):
            r.canonical_json({"pad": "x" * r.MAX_MESSAGE_BYTES})

    def test_sha256_hex_is_deterministic(self):
        self.assertEqual(r.sha256_hex({"a": 1}), r.sha256_hex({"a": 1}))
        self.assertRegex(r.sha256_hex({"a": 1}), r"^[0-9a-f]{64}$")


class TestRequestValidation(unittest.TestCase):
    def test_happy_path(self):
        request = make_request()
        r.validate_request(request)
        self.assertEqual(request["version"], r.VERSION)
        self.assertRegex(request["request_hash"], r"^[0-9a-f]{64}$")

    def test_request_hash_binding_is_exact(self):
        request = make_request()
        self.assertEqual(request["request_hash"], r.sha256_hex(r.request_body(request)))

    def test_deterministic_rebuild_is_idempotent(self):
        first = make_request()
        second = make_request()
        self.assertEqual(r.canonical_json(first), r.canonical_json(second))
        self.assertEqual(first["request_hash"], second["request_hash"])

    def test_unknown_field_rejected(self):
        bad = dict(make_request(), hidden=True)
        with self.assertRaisesRegex(r.CloudError, "UNKNOWN_FIELD"):
            r.validate_request(bad)

    def test_missing_field_rejected(self):
        bad = make_request()
        del bad["task_id"]
        with self.assertRaisesRegex(r.CloudError, "MISSING_FIELD"):
            r.validate_request(bad)

    def test_non_dict_rejected(self):
        with self.assertRaisesRegex(r.CloudError, "MALFORMED_RECORD"):
            r.validate_request(["not", "a", "dict"])

    def test_wrong_version_rejected(self):
        bad = dict(make_request(), version="p9-v0")
        bad["request_hash"] = r.sha256_hex(r.request_body(bad))
        with self.assertRaisesRegex(r.CloudError, "UNSUPPORTED_SCHEMA"):
            r.validate_request(bad)

    def test_bad_ids_rejected(self):
        for bad_id in ("", "has space", "x" * 65, 42, "-leading-dash"):
            with self.subTest(bad_id=bad_id):
                with self.assertRaisesRegex(r.CloudError, "INVALID_ID"):
                    make_request(request_id=bad_id)

    def test_bad_hashes_rejected(self):
        for bad_hash in ("a" * 63, "A" * 64, "g" * 64, 7):
            with self.subTest(bad_hash=bad_hash):
                with self.assertRaisesRegex(r.CloudError, "INVALID_HASH"):
                    make_request(trajectory_hash=bad_hash)

    def test_stale_request_hash_rejected(self):
        bad = make_request()
        bad["features"]["event_count"] = 99  # tamper after hashing
        with self.assertRaisesRegex(r.CloudError, "STALE_HASH"):
            r.validate_request(bad)

    def test_stale_request_hash_not_hex_rejected(self):
        bad = make_request()
        bad["request_hash"] = "z" * 64
        with self.assertRaisesRegex(r.CloudError, "INVALID_HASH"):
            r.validate_request(bad)


class TestFeatureValidation(unittest.TestCase):
    def test_missing_feature_key_rejected(self):
        features = make_features()
        del features["quorum_met"]
        with self.assertRaisesRegex(r.CloudError, "MISSING_FIELD"):
            make_request(features=features)

    def test_unknown_feature_key_rejected(self):
        features = make_features(extra_signal=True)
        with self.assertRaisesRegex(r.CloudError, "UNKNOWN_FIELD"):
            make_request(features=features)

    def test_bool_where_int_expected_rejected(self):
        with self.assertRaisesRegex(r.CloudError, "WRONG_TYPE"):
            make_request(features=make_features(event_count=True))

    def test_int_where_bool_expected_rejected(self):
        with self.assertRaisesRegex(r.CloudError, "WRONG_TYPE"):
            make_request(features=make_features(quorum_met=1))

    def test_string_where_float_expected_rejected(self):
        with self.assertRaisesRegex(r.CloudError, "WRONG_TYPE"):
            make_request(features=make_features(context_relevance="0.5"))

    def test_nan_and_infinite_float_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(r.CloudError, "WRONG_TYPE"):
                    make_request(features=make_features(context_relevance=bad))

    def test_out_of_range_rejected(self):
        with self.assertRaisesRegex(r.CloudError, "OUT_OF_RANGE"):
            make_request(features=make_features(event_count=-1))
        with self.assertRaisesRegex(r.CloudError, "OUT_OF_RANGE"):
            make_request(features=make_features(context_relevance=1.5))

    def test_boundary_values_accepted(self):
        features = make_features(event_count=0, approvals=1000,
                                 refusals=1000, context_relevance=1.0)
        r.validate_features(features)

    def test_int_accepted_for_float_kind(self):
        r.validate_features(make_features(context_relevance=0))


class TestResponseValidation(unittest.TestCase):
    def test_happy_path(self):
        request = make_request()
        response = make_response(request)
        r.validate_response(response)
        self.assertEqual(response["status"], r.ADVISORY_STATUS)
        self.assertTrue(r.response_matches_request(request, response))

    def test_response_hash_binding_is_exact(self):
        response = make_response()
        self.assertEqual(response["response_hash"], r.sha256_hex(r.response_body(response)))

    def test_unknown_field_rejected(self):
        bad = dict(make_response(), decision="PROMOTE")
        with self.assertRaisesRegex(r.CloudError, "UNKNOWN_FIELD"):
            r.validate_response(bad)

    def test_missing_field_rejected(self):
        bad = make_response()
        del bad["observations"]
        with self.assertRaisesRegex(r.CloudError, "MISSING_FIELD"):
            r.validate_response(bad)

    def test_non_advisory_status_fails_closed(self):
        for status in ("PROMOTE", "REFUSE", "INVALID", "advisory"):
            with self.subTest(status=status):
                request = make_request()
                body = r.response_body(make_response(request))
                body["status"] = status
                bad = dict(body, response_hash=r.sha256_hex(body))
                with self.assertRaisesRegex(r.CloudError, "AUTHORITY_REQUEST"):
                    r.validate_response(bad)

    def test_unknown_observation_code_rejected(self):
        with self.assertRaisesRegex(r.CloudError, "UNKNOWN_OBSERVATION_CODE"):
            make_response(observations=[{
                "code": "MADE_UP_CODE", "severity": "INFO", "message": "x",
            }])

    def test_unknown_observation_field_rejected(self):
        with self.assertRaisesRegex(r.CloudError, "UNKNOWN_FIELD"):
            make_response(observations=[{
                "code": "EVALUATION_COMPLETE", "severity": "INFO",
                "message": "x", "action": "call_agent",
            }])

    def test_unknown_severity_rejected(self):
        with self.assertRaisesRegex(r.CloudError, "MALFORMED_RECORD"):
            make_response(observations=[{
                "code": "EVALUATION_COMPLETE", "severity": "CRITICAL", "message": "x",
            }])

    def test_message_wrong_type_rejected(self):
        with self.assertRaisesRegex(r.CloudError, "WRONG_TYPE"):
            make_response(observations=[{
                "code": "EVALUATION_COMPLETE", "severity": "INFO", "message": 7,
            }])

    def test_oversized_message_rejected(self):
        with self.assertRaisesRegex(r.CloudError, "RECORD_TOO_LARGE"):
            make_response(observations=[{
                "code": "EVALUATION_COMPLETE", "severity": "INFO",
                "message": "x" * (r.MAX_OBSERVATION_TEXT_BYTES + 1),
            }])

    def test_observation_limit_enforced(self):
        observations = [{
            "code": "EVALUATION_COMPLETE", "severity": "INFO", "message": "x",
        }] * (r.MAX_OBSERVATIONS + 1)
        with self.assertRaisesRegex(r.CloudError, "OBSERVATION_LIMIT_VIOLATION"):
            make_response(observations=observations)

    def test_authority_vocabulary_in_message_fails_closed(self):
        for message in ("promote this candidate", "should REFUSE now",
                        "execute the plan", "invalid input detected"):
            with self.subTest(message=message):
                with self.assertRaisesRegex(r.CloudError, "AUTHORITY_REQUEST"):
                    make_response(observations=[{
                        "code": "EVALUATION_COMPLETE", "severity": "INFO",
                        "message": message,
                    }])

    def test_stale_response_hash_rejected(self):
        bad = make_response()
        bad["observations"] = []
        with self.assertRaisesRegex(r.CloudError, "STALE_HASH"):
            r.validate_response(bad)

    def test_matches_request_detects_stale_binding(self):
        request = make_request()
        other = make_request(candidate_hash=HASH_A)
        response = make_response(other)
        self.assertFalse(r.response_matches_request(request, response))

    def test_duplicate_delivery_is_byte_identical(self):
        request = make_request()
        first = make_response(request)
        second = make_response(request)
        self.assertEqual(r.canonical_json(first), r.canonical_json(second))
        self.assertEqual(first["response_hash"], second["response_hash"])

    def test_every_observation_code_is_emittable(self):
        observations = [
            {"code": code, "severity": "INFO", "message": "bounded signal note"}
            for code in r.OBSERVATION_CODES
        ]
        response = make_response(observations=observations)
        r.validate_response(response)
        self.assertEqual(len(response["observations"]), len(r.OBSERVATION_CODES))


if __name__ == "__main__":
    unittest.main()
