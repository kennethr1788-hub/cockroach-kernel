from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pdh3_r12_cpu_affinity_tested", HERE / "pdh3_r12_cpu_affinity.py"
)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class AffinityContractTests(unittest.TestCase):
    def test_32_vcpu_125_gib_is_prospectively_capped_to_31(self) -> None:
        plan = module.effective_vcpu_plan(32, 125)
        self.assertEqual(plan["effective_vcpu_limit"], 31)
        self.assertTrue(plan["affinity_cap_required"])
        self.assertTrue(plan["ratio_preserved"])

    def test_16_vcpu_188_gib_keeps_all_vcpus(self) -> None:
        plan = module.effective_vcpu_plan(16, 188)
        self.assertEqual(plan["effective_vcpu_limit"], 16)
        self.assertFalse(plan["affinity_cap_required"])

    def test_shape_below_frozen_minimum_is_rejected(self) -> None:
        with self.assertRaisesRegex(module.AffinityError, "PROVIDER_SHAPE_INSUFFICIENT"):
            module.effective_vcpu_plan(15, 188)
        with self.assertRaisesRegex(module.AffinityError, "PROVIDER_SHAPE_INSUFFICIENT"):
            module.effective_vcpu_plan(32, 93)

    def test_apply_uses_an_exact_deterministic_subset(self) -> None:
        state = {"value": set(range(32))}

        def get(_: int) -> set[int]:
            return set(state["value"])

        def set_value(_: int, cpus: set[int]) -> None:
            state["value"] = set(cpus)

        with mock.patch.object(module.sys, "platform", "linux"):
            receipt = module.apply_effective_vcpu_limit(31, getter=get, setter=set_value)
        self.assertEqual(receipt["before"]["count"], 32)
        self.assertEqual(receipt["after"]["count"], 31)
        self.assertEqual(receipt["after"]["cpus"], list(range(31)))
        self.assertTrue(receipt["exact"])

    def test_apply_fails_closed_when_kernel_does_not_apply_target(self) -> None:
        state = set(range(32))
        with (
            mock.patch.object(module.sys, "platform", "linux"),
            self.assertRaisesRegex(module.AffinityError, "AFFINITY_APPLY_MISMATCH"),
        ):
            module.apply_effective_vcpu_limit(
                31,
                getter=lambda _: set(state),
                setter=lambda _pid, _cpus: None,
            )

    def test_process_verification_rejects_wrong_inherited_count(self) -> None:
        with (
            mock.patch.object(module.sys, "platform", "linux"),
            self.assertRaisesRegex(module.AffinityError, "AFFINITY_VERIFY_MISMATCH"),
        ):
            module.verify_current_affinity(31, pid=42, getter=lambda _: set(range(32)))


if __name__ == "__main__":
    unittest.main()
