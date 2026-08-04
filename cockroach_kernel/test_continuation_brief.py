import unittest

from cockroach_kernel.continuation_brief import BriefError, build_brief, digest, validate_brief


def result(**extra):
    base = {"receipt_hash": "b" * 64, "local_verdict": "PROMOTE",
            "fresh_context": True, "value": "declared"}
    base.update(extra)
    base["result_hash"] = digest({k: v for k, v in base.items() if k != "result_hash"})
    return base


class ContinuationBriefTests(unittest.TestCase):
    def test_deterministic_and_generated_time_is_metadata(self):
        a = build_brief(result(), [{"trajectory_id": "t1", "content_hash": "c" * 64}], generated_at="a")
        b = build_brief(result(), [{"trajectory_id": "t1", "content_hash": "c" * 64}], generated_at="b")
        self.assertEqual(a["brief_id"], b["brief_id"])
        self.assertNotEqual(a["generated_at"], b["generated_at"])

    def test_tampered_maps_to_tampered_and_never_allows_execution(self):
        brief = build_brief(result(local_verdict="REFUSE", tampered_verdict="REFUSE"),
                            [{"trajectory_id": "t1", "content_hash": "c" * 64}])
        self.assertEqual(brief["recovery_state"]["primary"], "TAMPERED")
        self.assertIn("EXECUTE_SIDE_EFFECTS", brief["continuation"]["blocked_next"])

    def test_missing_provenance_and_bad_action_fail_closed(self):
        with self.assertRaises(BriefError):
            build_brief(result(), [{"trajectory_id": "t1", "content_hash": "bad"}])
        brief = build_brief(result(), [{"trajectory_id": "t1", "content_hash": "c" * 64}])
        brief["continuation"]["allowed_next"] = ["rm -rf workspace"]
        with self.assertRaises(BriefError):
            validate_brief(brief)

    def test_unknown_fact_requires_unknown_support(self):
        brief = build_brief(result(), [{"trajectory_id": "t1", "content_hash": "c" * 64}])
        brief["facts"][2]["value"] = "UNKNOWN"
        with self.assertRaises(BriefError):
            validate_brief(brief)


if __name__ == "__main__":
    unittest.main()
