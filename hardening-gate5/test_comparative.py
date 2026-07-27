#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest

import comparative
import heldout_contract


class ComparativeContractTests(unittest.TestCase):
    def test_all_eighteen_scenario_seeds_are_reproducible(self):
        hashes = set()
        for scenario in comparative.SCENARIO_CLASSES:
            for repetition in (1, 2, 3):
                first = comparative.generate_scenario(scenario, repetition)
                second = comparative.generate_scenario(scenario, repetition)
                self.assertEqual(comparative.canonical(first), comparative.canonical(second))
                hashes.add(first["source_bundle_hash"])
        self.assertEqual(len(hashes), 18)

    def test_isolated_environment_drops_cloud_and_credential_state(self):
        with tempfile.TemporaryDirectory(prefix="gate5-env-") as temporary:
            root = Path(temporary)
            env = comparative.isolated_env(root)
            self.assertEqual(set(env), {
                "HOME", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL",
                "GIT_TERMINAL_PROMPT", "LANG", "LC_ALL", "TZ", "PATH",
                "NO_PROXY", "no_proxy",
            })
            for forbidden in ("AWS_PROFILE", "AWS_ACCESS_KEY_ID", "PGPASSWORD",
                              "SSH_AUTH_SOCK", "HTTP_PROXY", "HTTPS_PROXY"):
                self.assertNotIn(forbidden, env)
            self.assertEqual(Path(env["HOME"]).parent, root)

    def test_product_authority_source_and_pass_refuse_semantics_are_unchanged(self):
        path = comparative.BASE / "p4-verifier/verifier.py"
        self.assertEqual(
            comparative.digest(path.read_bytes()),
            "a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40",
        )
        verifier = comparative.load_verifier()
        payload = {"checkpoint": "FINAL_PRELOSS", "manifest": {}}
        base = {
            "version": "p4-v1", "candidate_id": "gate5-proof",
            "source_receipt_hash": "a" * 64, "payload": payload,
            "payload_hash": verifier.digest(payload), "schema_version": "p4-v1",
            "provenance": {"source": "gate5-test"}, "supported": True,
            "one_use_state": "ISSUED", "quarantined": False,
            "policy_veto": False, "requested_paths": [], "declared_paths": [],
        }
        self.assertEqual([verifier.verify(base) for _ in range(5)],
                         [("PROMOTE", "VERIFIED")] * 5)
        refused = dict(base, policy_veto=True)
        self.assertEqual([verifier.verify(refused) for _ in range(5)],
                         [("REFUSE", "POLICY_VETO")] * 5)

    def test_frozen_binary_provenance_matches_local_tools(self):
        git = Path("/usr/bin/git")
        restic_path = shutil.which("restic")
        self.assertIsNotNone(restic_path)
        restic = Path(restic_path or "")
        self.assertEqual(comparative.digest(git.read_bytes()),
                         "179301dcb41ea78accc3fa0048a7e6f6710d891945a751a34addd622020c1818")
        self.assertEqual(comparative.digest(restic.read_bytes()),
                         "f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd")

    def test_heldout_contract_has_two_known_and_twenty_one_postfreeze_vectors(self):
        known = heldout_contract.known_preflight_vectors()
        self.assertEqual(len(known), 2)
        self.assertEqual(len({item["vector_hash"] for item in known}), 2)
        salt = bytes.fromhex("7e" * 32)
        vectors = [heldout_contract.derive("2" * 40, salt, name, variant)
                   for name in heldout_contract.CLASSES for variant in (1, 2, 3)]
        self.assertEqual(len(vectors), 21)
        self.assertEqual(len({item["vector_hash"] for item in vectors}), 21)


if __name__ == "__main__":
    unittest.main()
