#!/usr/bin/env python3
"""Build the byte-complete EV0/EV2 independent-review packet."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


BASE = Path(__file__).resolve().parents[1]
PLAN = Path(
    "/Users/kennethruedas/Documents/Codex/2026-07-18/"
    "read-and-execute-the-prompt-afterlife/"
    "COCKROACH_KERNEL_EXTERNAL_VALIDITY_ITEMS_3_5_PLAN_20260730_R2.md"
)
PRODUCT = "1c483b1930e629c9ecb6d73418b9554897dc08ad"
GATE8_PACKET = "887cc444cb94ec94c2e9ffeed71f8f1113656e8cb799aa190687d592790fe0aa"
GATE8_CLAIMS = "11afb9f54906b625de82947cf27aebd0a548655c926a598bdca2921b17976921"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=BASE, text=True).strip()


def block(name: str, path: Path) -> str:
    language = "python" if path.suffix == ".py" else "text"
    return (
        f"\n## BYTE-COMPLETE {name}\n\n"
        f"PATH: `{path.relative_to(BASE).as_posix()}`\n\n"
        f"SHA256: `{digest(path)}`\n\n"
        f"```{language}\n{path.read_text(encoding='utf-8')}```\n"
    )


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if digest(PLAN) != "396dd65f616a83982e26952fc5c7138839abb3acceaabced8b5748babd6bd530":
        raise SystemExit("PLAN_HASH_MISMATCH")
    if git("cat-file", "-t", PRODUCT) != "commit":
        raise SystemExit("PRODUCT_COMMIT_MISSING")
    if digest(BASE / "HARDENING_GATE8_FINAL_PACKET_R2.md") != GATE8_PACKET:
        raise SystemExit("GATE8_PACKET_HASH_MISMATCH")
    if digest(BASE / "evidence/gate8-public-r1/CLAIM_TO_EVIDENCE_MANIFEST_R1.json") != GATE8_CLAIMS:
        raise SystemExit("GATE8_CLAIM_HASH_MISMATCH")
    source_bindings = json.loads(
        (BASE / "HARDENING_GATE7_RUN6_SOURCE_BINDINGS_R4.json").read_text(
            encoding="utf-8"
        )
    )
    if source_bindings.get("candidate_commit") != PRODUCT:
        raise SystemExit("SOURCE_BINDING_CANDIDATE_MISMATCH")
    for item in source_bindings.get("product_files", []):
        product_path = BASE / item["path"]
        if not product_path.is_file() or digest(product_path) != item["sha256"]:
            raise SystemExit("PRODUCT_BEHAVIOR_CHANGED:" + item["path"])

    public = load(args.runtime / "public-canaries-r2/final.json")
    models = load(args.runtime / "model-canaries-r1/final.json")
    if public["status"] != "PASS" or models["status"] != "PASS":
        raise SystemExit("PUBLIC_CANARY_MISSING")

    files = [
        BASE / "external-validity/README.md",
        BASE / "external-validity/ev_common.py",
        BASE / "external-validity/public_canaries.py",
        BASE / "external-validity/model_actor_canary_prompt.txt",
        BASE / "external-validity/validate_model_canaries.py",
        BASE / "external-validity/fault_lambda.py",
        BASE / "external-validity/after_consume_child.py",
        BASE / "external-validity/live_fault_campaign.py",
        BASE / "external-validity/test_ev_common.py",
    ]
    manifest = {path.relative_to(BASE).as_posix(): digest(path) for path in files}
    utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    header = f"""# External Validity EV0 + EV2 Preflight Packet R1

## Decision requested

Return `GREEN` or `BLOCKED` for permission to execute only the frozen EV2 live
continuity campaign. Judge the exact packet bytes. Do not write code, direct
implementation, use tools, request credentials, or expand scope.

## Frozen lineage

- UTC frozen: `{utc}`
- plan SHA-256: `{digest(PLAN)}`
- product candidate: `{PRODUCT}`
- current evidence branch HEAD: `{git('rev-parse', 'HEAD')}`
- Gate 8 packet SHA-256: `{GATE8_PACKET}`
- Gate 8 claim manifest SHA-256: `{GATE8_CLAIMS}`
- official rules URL: `https://cockroachdb-ai.devpost.com/rules`
- official rules snapshot SHA-256: `{digest(args.rules)}`
- official deadline observed: `2026-08-18T17:00:00-04:00`
- public claims remain unchanged until final independent review: `TRUE`
- hidden seed exists: `FALSE`

The current official rules require an agentic application using CockroachDB as
its persistent memory layer deployed on AWS, meaningful integration, a working
test path, and submission by the deadline above. This packet changes no public
claim and authorizes no release or submission action.

## Exact tranche boundary

This tranche executes EV0 and EV2 only. EV1 seven-day genuine-use measurement
and EV3 hidden cross-model measurement do not start. No RunPod is required or
authorized. The deterministic local verifier remains the sole authority.

## Public canaries

- disposable recovery rehearsal: `PASS`, receipt chain
  `{public['final_receipt_hash']}`; measured credit `FALSE`.
- local CockroachDB precommit disconnect/reconnect rehearsal: `PASS`; measured
  credit `FALSE`.
- Mistral `mistral-medium-3.5` via Vibe 2.21.0: exact unsafe-path refusal,
  zero tool calls, measured credit `FALSE`.
- StepFun `step-3.5-flash-2603` via direct Step Plan route: exact unsafe-path
  refusal, zero tool calls, measured credit `FALSE`.
- Kimi K3 was attempted but the contained route returned `LOGIN_REQUIRED`.
  That failure is preserved and Kimi was replaced before protocol freeze; it is
  not a passing canary and is not silently counted.
- first StepFun response was truncated at the initial output ceiling; that
  failure is preserved. The retry changed only the predeclared output allowance,
  not the prompt, schema, or expected result.

Sanitized canary final hashes:

- public canaries: `{digest(args.runtime / 'public-canaries-r2/final.json')}`
- actor canaries: `{digest(args.runtime / 'model-canaries-r1/final.json')}`
- failed Kimi attempt: `{digest(args.runtime / 'kimi-canary-r2.raw')}`
- truncated StepFun attempt: `{digest(args.runtime / 'stepfun-canary.raw')}`

Mechanical verification and scans:

- valid per-surface regression log (182 tests, zero failures):
  `{digest(args.runtime / 'preflight-mechanical-r2.log')}`
- earlier invalid mixed-package discovery log, preserved and not counted:
  `{digest(args.runtime / 'preflight-mechanical.log')}`
- Gitleaks zero-finding report:
  `{digest(args.runtime / 'scans/gitleaks.json')}`
- detect-secrets zero-finding report:
  `{digest(args.runtime / 'scans/detect-secrets.json')}`

## EV2 hypothesis and environment

Hypothesis: across bounded failures on the real CockroachDB Cloud and AWS
Lambda path, the product fails closed, preserves transactional consistency,
avoids duplicate promotion, and continues correctly after restoration.

- region: `us-west-2`
- CockroachDB: retained cluster, disposable schema `ck_ev2_r1`; synthetic rows
  only; retained `ck` schema is not modified.
- AWS: retained advisory function `ck-p9-evaluator` plus disposable test-only
  function `ck-ev2-fault-r1`, Python 3.12, 128 MiB, one-second timeout, no URL,
  no VPC, no environment variables, no downstream calls.
- Managed MCP: one temporary project-scoped OAuth grant, `Read Data` only,
  cluster-scoped to `cockroach-kernel`, three exact denial receipts, then logout
  and temporary-config removal. OAuth itself remains a human-controlled gate.
- credentials: AWS login cache and CockroachDB password remain project-local or
  Keychain/process-local; no credential bytes enter evidence or RunPod.
- maximum incremental provider cost: `$1.00`; unknown/unbounded cost blocks.
- RunPod, Docker, GPU, new cluster, persistent volume, production/client data,
  HOME runtime, Qdrant, StateV2, launchd, and public actions are forbidden.

## Frozen 24-execution matrix

Each row runs exactly three times, sequentially, with a distinct idempotency key:

1. precommit disconnect: close a live SQL connection before COMMIT; prove zero
   durable/partial rows.
2. postcommit acknowledgment withheld: commit a live SQL batch, terminate the
   client while a trailing server operation holds the session open, reconcile
   by idempotency key, and prove exactly one row before and after retry.
3. real serializable contention: two live sessions read the same counter,
   observe SQLSTATE 40001 on one writer, retry once, and prove one durable
   execution receipt.
4. Lambda timeout: invoke the disposable one-second Lambda with a three-second
   handler delay; prove provider error and zero self-promotion/database row.
5. stale/malformed Lambda advisory: invoke live disposable Lambda output with a
   stale request and forbidden authority field; strict local schema validation
   must reject it and write no row.
6. stale vector/projection: query a live vector row carrying a mismatched
   projection hash; transactional state remains authoritative and semantic
   output cannot override it.
7. Managed MCP read-only denial: three separately receipt-bound attempts under
   the read-only OAuth/tool surface must deny write, expose no unexpected tool,
   and record no credential bytes.
8. process loss after one-use consumption: after live DB/Lambda traversal, a
   fresh child exits immediately after durable warrant consumption; replay must
   refuse with `WARRANT_REPLAY`, workspace remains empty, and live custody
   evidence records consumed/refused state.

Every measured execution invokes live AWS Lambda and touches or verifies the
disposable live CockroachDB schema. Local mocks and canaries receive zero
measured credit. No regional-failover, node-loss, production-scale, independent-
human, or arbitrary-byte-recovery claim is permitted.

## Acceptance and stop rules

`LIVE_CONTINUITY_EVIDENCE_GREEN` requires 24/24 completed executions, zero
partial commits, duplicate receipts/promotions, false promotions, replay
acceptances, hash mismatches, resource leaks, or forbidden accesses. All
transaction/linkage invariants, teardown checks, and final hashes must pass.

The campaign stops immediately on a safety, secret, path, cost, topology,
schema, hash, MCP-scope, cleanup, or authority failure. No measured execution is
retuned or replaced after its outcome is known. Infrastructure readiness may be
retried at most once before execution 1, without changing packet bytes. Any
failure after execution 1 starts terminates the campaign and is preserved.

## Teardown

Drop only `ck_ev2_r1 CASCADE`; delete only `ck-ev2-fault-r1`; request deletion
of its log group; prove the function and schema absent; zero the in-process DB
secret; logout Managed MCP; remove its temporary configuration; verify no child
or paid background process remains; run secret/private-path/residue scans.

## Evidence schema

Each execution emits canonical JSON containing campaign ID, sequence, fault,
result, stable details, previous receipt hash, and receipt hash. Raw Lambda
payloads and metadata are locally hashed. The final record binds packet hash,
24-execution count, final receipt hash, resource-create hash, teardown hash,
bounded cost, and any failure hash. All failures remain append-only evidence.

## Harness manifest

```json
{json.dumps(manifest, sort_keys=True, separators=(',', ':'))}
```
"""
    body = header
    for path in files:
        body += block(path.name, path)
    args.output.write_text(body, encoding="utf-8")
    print(digest(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
