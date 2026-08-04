"""Offline structural tests for P9 deployment and least-privilege artifacts."""
from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent


def load_json(name):
    with (ROOT / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


class TestIamTemplate(unittest.TestCase):
    def test_execution_role_has_exact_log_and_secret_actions(self):
        policy = load_json("iam_execution_role_template.json")
        self.assertEqual(policy["Version"], "2012-10-17")
        self.assertEqual(len(policy["Statement"]), 2)
        statement = policy["Statement"][0]
        self.assertEqual(statement["Effect"], "Allow")
        self.assertEqual(
            set(statement["Action"]),
            {"logs:CreateLogStream", "logs:PutLogEvents"},
        )
        self.assertNotIn("*", statement["Action"])
        self.assertEqual(
            statement["Resource"],
            "arn:aws:logs:us-west-2:${AWS_ACCOUNT_ID}:log-group:/aws/lambda/ck-p9-evaluator:*",
        )
        self.assertEqual(statement["Resource"].count("*"), 1)
        secret = policy["Statement"][1]
        self.assertEqual(secret["Action"], ["secretsmanager:GetSecretValue"])
        self.assertEqual(
            secret["Resource"],
            "arn:aws:secretsmanager:us-west-2:${AWS_ACCOUNT_ID}:secret:ck-p9-cockroach-runtime-*",
        )

    def test_no_global_or_cross_resource_wildcard(self):
        serialized = json.dumps(load_json("iam_execution_role_template.json"), sort_keys=True)
        self.assertNotIn('"Resource": "*"', serialized)
        self.assertNotRegex(serialized, r'"Action":\s*"[^"]*\*')
        self.assertNotIn("arn:aws:iam", serialized)
        self.assertNotIn("arn:aws:s3", serialized)
        self.assertNotIn("arn:aws:lambda", serialized)

    def test_trust_policy_is_lambda_service_only(self):
        policy = load_json("lambda_trust_policy.json")
        statement = policy["Statement"]
        self.assertEqual(len(statement), 1)
        self.assertEqual(statement[0]["Principal"], {"Service": "lambda.amazonaws.com"})
        self.assertEqual(statement[0]["Action"], "sts:AssumeRole")


class TestDeploymentManifest(unittest.TestCase):
    def test_fixed_resource_and_cost_bounds(self):
        manifest = load_json("deployment_manifest.json")
        self.assertEqual(manifest["status"], "PREMUTATION_APPROVED")
        self.assertEqual(manifest["region"], "us-west-2")
        self.assertEqual(manifest["function"]["name"], "ck-p9-evaluator")
        self.assertEqual(manifest["function"]["memory_mib"], 128)
        self.assertEqual(manifest["function"]["timeout_seconds"], 10)
        self.assertEqual(
            manifest["function"]["handler"], "live_lambda_handler.lambda_handler"
        )
        self.assertEqual(manifest["function"]["reserved_concurrency"], 2)
        self.assertEqual(
            manifest["function"]["effective_account_concurrency_ceiling"], 10
        )
        self.assertEqual(manifest["function"]["max_coordinator_in_flight"], 1)
        self.assertEqual(manifest["function"]["request_budget_ms"], 8000)
        self.assertEqual(manifest["function"]["provisioned_concurrency"], 0)
        self.assertFalse(manifest["function"]["function_url"])
        self.assertFalse(manifest["function"]["network_calls"])
        self.assertEqual(manifest["logs"]["retention_days"], 14)
        self.assertEqual(manifest["limits"]["max_invocations"], 1000)
        self.assertEqual(manifest["limits"]["incremental_aws_cost_usd"], 5)

    def test_mcp_is_oauth_read_only_single_view(self):
        mcp = load_json("deployment_manifest.json")["managed_mcp"]
        self.assertEqual(mcp["authentication"], "OAUTH")
        self.assertEqual(mcp["cluster_scope"], "cockroach-kernel")
        self.assertEqual(mcp["access"], "READ_ONLY")
        self.assertEqual(mcp["view"], "ck.mcp_receipt_view")
        self.assertLessEqual(mcp["max_rows"], 64)


class TestRuntimeGrantTemplate(unittest.TestCase):
    def test_vector_digest_is_collision_safe_and_row_identity_is_separate(self):
        schema = (ROOT / "migrations" / "001_cloud.sql").read_text(encoding="utf-8").lower()
        transition = (
            ROOT / "migrations" / "003_collision_safe_vector_digest.sql"
        ).read_text(encoding="utf-8").lower()
        self.assertIn("vector_digest bytes not null check", schema)
        self.assertNotIn("vector_digest bytes not null unique", schema)
        self.assertIn("unique (task_id, event_hash, namespace)", schema)
        self.assertIn("receipts_task_id_idx", schema)
        self.assertIn("create table if not exists ck.recovery_checkpoints", schema)
        self.assertIn("drop constraint if exists context_vectors_vector_digest_key", transition)
        self.assertIn("create index if not exists context_vectors_vector_digest_idx", transition)

    def test_no_identity_or_cluster_mutation(self):
        sql = (ROOT / "migrations" / "002_runtime_grants.sql").read_text(encoding="utf-8")
        stripped = re.sub(r"--[^\n]*", "", sql).lower()
        for forbidden in (
            "create user", "create role", "alter user", "alter role",
            "set cluster setting", "grant admin", "drop database", "create database",
        ):
            self.assertNotIn(forbidden, stripped)

    def test_grants_are_exact_schema_tables_view_and_changefeed(self):
        sql = (ROOT / "migrations" / "002_runtime_grants.sql").read_text(encoding="utf-8").lower()
        self.assertIn("grant usage on schema ck to ck_runtime", sql)
        self.assertIn("grant select, insert on table", sql)
        self.assertIn("grant select on table ck.mcp_receipt_view to ck_runtime", sql)
        self.assertIn("grant changefeed on table ck.worker_results to ck_runtime", sql)
        self.assertIn("ck.recovery_checkpoints", sql)
        self.assertNotIn("update", sql)
        self.assertNotIn("delete", sql)
        self.assertNotIn("all privileges", sql)


if __name__ == "__main__":
    unittest.main()
