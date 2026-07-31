from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_bundle_tested", HERE / "build_pdh3_scale_bundle.py"
)
assert SPEC is not None and SPEC.loader is not None
bundle = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bundle
SPEC.loader.exec_module(bundle)


class BundleTests(unittest.TestCase):
    def test_paths_are_relative_and_unique(self) -> None:
        self.assertEqual(len(bundle.FILES), len(set(bundle.FILES)))
        for name in bundle.FILES:
            bundle.validate_relative(name)

    def test_deterministic_archive_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdh3-bundle-test.") as temporary:
            root = Path(temporary)
            one = bundle.build(root / "one.tgz", root / "one.json")
            two = bundle.build(root / "two.tgz", root / "two.json")
            self.assertEqual(one["archive_sha256"], two["archive_sha256"])
            with tarfile.open(fileobj=io.BytesIO((root / "one.tgz").read_bytes()), mode="r:gz") as archive:
                names = archive.getnames()
                self.assertEqual(len(names), len(set(names)))
                self.assertIn("PDH3_BUNDLE_MANIFEST.json", names)
                manifest = json.load(archive.extractfile("PDH3_BUNDLE_MANIFEST.json"))
                self.assertTrue(manifest["credential_free"])
                self.assertTrue(manifest["synthetic_only"])


if __name__ == "__main__":
    unittest.main()
