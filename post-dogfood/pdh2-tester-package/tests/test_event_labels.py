from __future__ import annotations

import unittest

from src.event_labels import normalize_event_label


class NormalizeEventLabelTests(unittest.TestCase):
    def test_normalizes_supported_values(self) -> None:
        cases = {
            " Feature Ready ": "feature-ready",
            "human_saved_EDIT": "human-saved-edit",
            "release---candidate": "release---candidate",
            "event_42": "event-42",
            "a  b___c": "a-b-c",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(normalize_event_label(raw), expected)

    def test_rejects_non_string(self) -> None:
        for value in (None, 42, b"bytes", ["list"]):
            with self.subTest(value=value):
                with self.assertRaises((TypeError, ValueError)):
                    normalize_event_label(value)

    def test_rejects_empty_or_unsupported_values(self) -> None:
        for value in ("", "   ", "contains/slash", "emoji-\N{ROCKET}", "UPPER?"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_event_label(value)


if __name__ == "__main__":
    unittest.main()
