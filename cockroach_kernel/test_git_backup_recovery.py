import hashlib
import unittest

from cockroach_kernel.git_backup_recovery import resolve_v5, sha256_value


def manifest(cid, lineage, values, parent=None):
    paths = [{"path": path, "type": "file", "executable": False,
              "sha256": hashlib.sha256(data.encode()).hexdigest()}
             for path, data in sorted(values.items())]
    root = sha256_value(paths)
    body = {"version": 1, "capture_id": cid, "lineage_type": lineage,
            "parent_content_root_sha256": parent, "paths": paths,
            "content_root_sha256": root}
    return dict(body, manifest_sha256=sha256_value(body))


def candidate(cid, lineage, values, parent=None):
    return {"candidate_id": cid, "lineage_type": lineage,
            "manifest": manifest(cid, lineage, values, parent)}


class GitBackupRecoveryTests(unittest.TestCase):
    def test_single_base_promotes(self):
        result = resolve_v5([candidate("base", "GIT_BASE", {"a.txt": "one"})])
        self.assertEqual((result["verdict"], result["reason_code"]), ("PROMOTE", "PROMOTE_SOLE_CANDIDATE"))

    def test_equivalent_backup_collapses(self):
        values = {"a.txt": "one"}
        result = resolve_v5([candidate("base", "GIT_BASE", values), candidate("backup", "INDEPENDENT_BACKUP", values)])
        self.assertEqual(result["reason_code"], "PROMOTE_EQUIVALENT_CANDIDATES")
        self.assertIsNotNone(result["selected_candidate_id"])

    def test_divergent_backup_refuses(self):
        result = resolve_v5([candidate("base", "GIT_BASE", {"a.txt": "one"}),
                             candidate("backup", "INDEPENDENT_BACKUP", {"a.txt": "two"})])
        self.assertEqual(result["reason_code"], "REFUSE_INDEPENDENT_CONTENT_CONFLICT")

    def test_wrong_child_parent_invalidates(self):
        result = resolve_v5([candidate("child", "CAPTURED_CHILD", {"a.txt": "one"}, "f" * 64)], expected_parent="e" * 64)
        self.assertEqual((result["verdict"], result["reason_code"]), ("INVALID", "INVALID_LINEAGE"))

    def test_unsafe_path_precedes_backup_hash(self):
        bad = candidate("backup", "INDEPENDENT_BACKUP", {"a.txt": "one"})
        bad["manifest"]["paths"][0]["path"] = "../escape"
        result = resolve_v5([bad])
        self.assertEqual(result["reason_code"], "REFUSE_UNSAFE_PATH")

    def test_empty_refuses(self):
        self.assertEqual(resolve_v5([])["reason_code"], "REFUSE_NO_SURVIVING_CANDIDATE")


if __name__ == "__main__":
    unittest.main()
