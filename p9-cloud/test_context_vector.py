"""Offline tests for deterministic context-vector projection."""
from __future__ import annotations

import math
import unittest

import context_vector as cv
import records as r


class TestContextVector(unittest.TestCase):
    def test_repeat_is_byte_identical(self):
        first = cv.context_vector("fixed task context", "campaign-a")
        second = cv.context_vector("fixed task context", "campaign-a")
        self.assertEqual(r.canonical_json(first), r.canonical_json(second))
        self.assertEqual(cv.vector_digest(first), cv.vector_digest(second))

    def test_exact_dimension_and_finite_norm(self):
        vector = cv.context_vector("alpha beta gamma", "campaign-a")
        self.assertEqual(len(vector), 64)
        self.assertTrue(all(math.isfinite(value) for value in vector))
        self.assertAlmostEqual(math.sqrt(sum(value * value for value in vector)), 1.0, places=5)

    def test_empty_text_has_defined_zero_vector(self):
        self.assertEqual(cv.context_vector("", "campaign-a"), [0.0] * 64)

    def test_namespace_isolation(self):
        text = "same bounded trajectory"
        self.assertNotEqual(
            cv.context_vector(text, "campaign-a"),
            cv.context_vector(text, "campaign-b"),
        )

    def test_wrong_type_and_oversize_fail_closed(self):
        with self.assertRaisesRegex(r.CloudError, "WRONG_TYPE"):
            cv.context_vector(7, "campaign-a")
        with self.assertRaisesRegex(r.CloudError, "RECORD_TOO_LARGE"):
            cv.context_vector("x" * (cv.MAX_INPUT_BYTES + 1), "campaign-a")

    def test_invalid_namespace_fails_closed(self):
        with self.assertRaisesRegex(r.CloudError, "INVALID_ID"):
            cv.context_vector("text", "../escape")

    def test_digest_rejects_wrong_shape_and_nan(self):
        with self.assertRaisesRegex(r.CloudError, "MALFORMED_RECORD"):
            cv.vector_digest([0.0] * 63)
        bad = [0.0] * 64
        bad[0] = float("nan")
        with self.assertRaisesRegex(r.CloudError, "WRONG_TYPE"):
            cv.vector_digest(bad)

    def test_description_is_honest(self):
        description = cv.describe()
        self.assertEqual(description["kind"], "deterministic_token_feature_hash_projection")
        self.assertFalse(description["neural_embedding"])
        self.assertTrue(description["keyless"])


if __name__ == "__main__":
    unittest.main()
