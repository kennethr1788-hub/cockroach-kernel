from __future__ import annotations

import unittest

import pdh3_scale_contract as contract


class ContractTests(unittest.TestCase):
    def test_exact_upper_envelope(self) -> None:
        value = contract.production_contract()
        self.assertEqual(value["workload"]["trajectory_events"], 5_000_000)
        self.assertEqual(value["workload"]["task_bound_vectors"], 250_000)
        self.assertEqual(value["workload"]["verifier_executions"], 9_976)
        self.assertEqual(value["workload"]["checkpoints"], 288)
        self.assertEqual(value["workload"]["setup_success_margin_seconds"], 300)
        self.assertEqual(value["workload"]["setup_timeout_seconds"], 10_800)
        self.assertEqual(
            value["egress_evidence"]["claim"],
            "PROCESS_TREE_OBSERVED_ZERO_EXTERNAL_EGRESS",
        )
        self.assertFalse(value["egress_evidence"]["network_namespace"])
        self.assertEqual(value["workload"]["remote_preflight_epochs"], 3)
        self.assertEqual(value["workload"]["remote_preflight_faults"], 3)
        self.assertEqual(value["workload"]["remote_preflight_concurrency"], 500)
        self.assertEqual(value["workload"]["contended_counter_shards"], 16)
        self.assertLess(
            value["thresholds"]["trace_preflight_projected_bytes"],
            value["thresholds"]["trace_bytes"],
        )
        self.assertEqual(value["thresholds"]["rss_kb_total"], 80 * 1024**2)
        self.assertEqual(value["thresholds"]["file_descriptors_per_node"], 65_536)
        self.assertEqual(value["thresholds"]["live_node_processes"], 3)
        self.assertEqual(value["thresholds"]["process_tree_count"], 64)

    def test_cost_and_lifecycle(self) -> None:
        runpod = contract.RUNPOD
        self.assertEqual(runpod["gpu_id"], "NVIDIA L40S")
        self.assertEqual(runpod["cloud"], "SECURE")
        self.assertEqual(
            runpod["image"],
            "runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404",
        )
        self.assertEqual(runpod["ports"], ["22/tcp"])
        self.assertFalse(runpod["global_networking"])
        self.assertEqual(runpod["vcpu_min"], 16)
        self.assertEqual(runpod["vcpu_max"], 32)
        self.assertEqual(runpod["ram_gb_min"], 94)
        self.assertEqual(runpod["ram_gb_max"], 188)
        self.assertEqual(runpod["volume_gb"], 0)
        self.assertIsNone(runpod["network_volume"])
        self.assertEqual(runpod["replacement_cost_usd_max"], 35)
        self.assertEqual(runpod["aggregate_cost_usd_max"], 39)
        self.assertEqual(runpod["paid_seconds_max"], 28 * 60 * 60)

    def test_production_arguments_fail_closed(self) -> None:
        good = {
            "duration_seconds": contract.MEASURED_SECONDS,
            "checkpoint_seconds": contract.CHECKPOINT_SECONDS,
            "tasks": contract.TASKS,
            "events_per_task": contract.EVENTS_PER_TASK,
            "receipts_per_task": contract.RECEIPTS_PER_TASK,
            "vectors": contract.VECTORS,
            "max_concurrency": contract.MAX_CONCURRENCY,
            "disk_used_fraction_limit": contract.DISK_USED_FRACTION_LIMIT,
            "query_duration_seconds": contract.QUERY_DURATION_SECONDS,
            "seed_batch_tasks": contract.SEED_BATCH_TASKS,
            "setup_timeout_seconds": contract.SETUP_TIMEOUT_SECONDS,
            "fault_every_checkpoints": contract.FAULT_EVERY_CHECKPOINTS,
            "cache": contract.NODE_CACHE,
            "sql_memory": contract.NODE_SQL_MEMORY,
            "store_size": None,
        }
        contract.validate_production_arguments(good)
        bad = dict(good, duration_seconds=60)
        with self.assertRaisesRegex(ValueError, "PRODUCTION_ARGUMENT_MISMATCH"):
            contract.validate_production_arguments(bad)

        reduced_store = dict(good, store_size="2GiB")
        with self.assertRaisesRegex(ValueError, "PRODUCTION_ARGUMENT_MISMATCH"):
            contract.validate_production_arguments(reduced_store)

    def test_exact_schedule(self) -> None:
        schedule = contract.expected_schedule()
        self.assertEqual(schedule["checkpoints"], 288)
        self.assertEqual(
            schedule["concurrency_counts"],
            {"10": 1, "50": 1, "100": 1, "250": 1, "500": 284},
        )
        self.assertEqual(schedule["verifier_batches"], 232)
        self.assertEqual(schedule["verifier_executions"], 9_976)
        self.assertEqual(schedule["fault_count"], 24)
        self.assertEqual(schedule["fault_targets"].count(0), 8)
        self.assertEqual(schedule["fault_targets"].count(1), 8)
        self.assertEqual(schedule["fault_targets"].count(2), 8)


if __name__ == "__main__":
    unittest.main()
