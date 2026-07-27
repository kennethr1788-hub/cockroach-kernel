# Hardening Gate 5 — Independent Judge Packet R1

## Judge boundary

Review the exact candidate and evidence below. Return GREEN only if Gate 5 mechanically proves all eight mandatory S3 repairs and all Gate 4 evidence-candidate obligations without claiming Gate 6. You are non-authoring: do not provide patches, code, implementation direction, tool calls, deployment actions, or credential requests. A material defect requires NOT_GREEN with the exact failed acceptance condition.

- `TARGET_GATE`: `HARDENING_5_EVIDENCE_CANDIDATE_GREEN`
- `PARENT_GATE`: `HARDENING_4_BASELINE_PROTOCOL_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `bd29bd23e831175aa54526b9e3c48bd04e8af3ed`
- `GATE4_PROTOCOL_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `HARDENING_PLAN_SHA256`: `1ce953127138a35bd9588d686bbefefc0b012e8f2188a8fea736842030d57310`

## Required verdict schema

```json
{"verdict":"GREEN|NOT_GREEN|BLOCKED","packet_sha256":"<exact packet hash supplied out of band>","candidate_commit":"bd29bd23e831175aa54526b9e3c48bd04e8af3ed","gate":"HARDENING_5_EVIDENCE_CANDIDATE_GREEN","findings":[{"severity":"CRITICAL|HIGH|MEDIUM|LOW","acceptance_condition":"<condition>","evidence":"<packet evidence>"}],"summary":"<concise>"}
```

## Evidence report

# Hardening Gate 5 — Evidence Candidate Report R1

## Control fields

- `GATE`: `HARDENING_RUN_GATE_5_EVIDENCE_CANDIDATE`
- `PARENT_GATE`: `HARDENING_4_BASELINE_PROTOCOL_GREEN`
- `TARGET`: `HARDENING_5_EVIDENCE_CANDIDATE_GREEN`
- `CANDIDATE_IMPLEMENTATION_COMMIT`: `bd29bd23e831175aa54526b9e3c48bd04e8af3ed`
- `GATE4_PROTOCOL_SHA256`: `12da9def248c5056f001fd60a448b8c17e50adf5df6cb2261cab55d6a97ca70e`
- `PLAN_SHA256`: `bdbd99c1d3ac17bb2448f02d64d756bf747e5d17eed0c0e6fcf3190c3ab3a67e`
- `HARDENING_PLAN_SHA256`: `1ce953127138a35bd9588d686bbefefc0b012e8f2188a8fea736842030d57310`
- `RUNPOD_ACTION`: `none`
- `PUBLIC_ACTION`: `none`
- `UTC_RECORDED`: `2026-07-27T21:25:13Z`

## Eight mandatory repairs

1. `s3-soak/hardening.py` emits four stable, sanitized external failure
   classes: `AWS_AUTHENTICATION`, `AWS_AUTHORIZATION_OR_THROTTLING`,
   `COCKROACH_CONNECTIVITY`, and `UNKNOWN_EXTERNAL_COMMAND`. Only the bounded
   output SHA-256 is retained; raw output is forbidden.
2. `cloud_adapter.run_live` fsyncs a stage-bound `failure.json` outside the
   disposable trial before its `finally` cleanup can execute.
3. Cleanup resolves and removes exactly one child trial root, then emits a
   canonical zero-residue receipt. The interruption regression proves the
   trial path is absent after cleanup.
4. The coordinator guard now terminates bridge and coordinator together and
   binds that receipt to exact-Pod stop/delete for the worker. A three-process
   local regression proves worker/bridge/coordinator absence.
5. The host coordinator fsyncs one hash-chained local custody receipt after
   every completed request/result pair. This custody is outside the temporary
   cloud-call trial and does not depend on final remote retrieval.
6. Live mode now requires AWS expiration, final scheduled exchange, and at
   least a 900-second margin. Missing or insufficient data fails before calls.
7. The tracked sanitized fixture preserves and validates all eleven exact S3
   request/result pairs plus the exact request 12. The injected expiry case is
   refused as `AWS_SESSION_MARGIN_INSUFFICIENT`.
8. `p4-verifier/verifier.py` remains unchanged at SHA-256
   `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`.
   Five-repeat `PROMOTE/VERIFIED` and `REFUSE/POLICY_VETO` regressions pass.

## Gate 4 comparative obligations

- Generator/scorer/adapters: `hardening-gate5/comparative.py`, SHA-256
  `bb107750414b6eadb102a894eec2f1d23f64533d20efaaa5751ada59215c2527`.
- Six class schemas plus seeds aggregate SHA-256:
  `ca5ae356ca91693e6516b10785a533e3db760c86c9730513adc67e41f806405c`.
- Held-out contract: `hardening-gate5/heldout_contract.py`, SHA-256
  `b5de48cf64cddb505238b835d026fad6ed39917c129bf3b4194f430da1f69801`.
  It exposes two known preflight vectors and derives 21 salted vectors only
  after the candidate commit is frozen.
- Git reference: Apple Git `2.50.1`, SHA-256
  `179301dcb41ea78accc3fa0048a7e6f6710d891945a751a34addd622020c1818`.
- Restic Darwin arm64 `0.19.0`, SHA-256
  `f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd`.
- Restic official Linux amd64 archive SHA-256:
  `13176fe6d89d4357947a2cd107218ab2873a5f9d8e1ac2d4cd1c8e07e6839c21`;
  decompressed binary SHA-256:
  `ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c`.
- Product mode: local deterministic P4 verifier, trial-local object/candidate
  custody, content hashes, policy veto, and one-use consumption before copy.
- Isolation: fresh process/root, trial-local HOME, scrubbed cloud/credential
  environment, Darwin Seatbelt `(deny network*)` proof. Linux Gate 6 is frozen
  to `unshare --user --map-root-user --net --mount-proc` and must repeat the
  forbidden-egress proof before measured execution.
- Recovery timeout: one 180-second process alarm spans recovery and scoring;
  each subprocess also has a bounded timeout.
- Receipts: exact field set, canonical JSON, exact receipt hash validation,
  and post-teardown zero-residue check.
- Dependency/license and public/private evidence boundaries are recorded in
  `HARDENING_GATE5_DEPENDENCY_LICENSE_MANIFEST_R1.md` and
  `HARDENING_GATE5_RUNTIME_BOUNDARIES_R1.md`.

## Local paired smoke

- Exact local raw summary SHA-256:
  `7ac54f33b7687bce123b8217aafad58c7db08a659219120a42ecfc6712560a68`.
- Internal summary SHA-256:
  `3050feda1e6d089c34b45cebd6f01247786ca16d7c72f0d30d22a3efd62254ea`.
- Sanitized tracked evidence aggregate SHA-256:
  `e6993935e8d595de03ff3b49a331b9a5398a1b1d9610c937b28d3c8e3c325560`.
- Executions: `18` (six classes × three methods × one smoke repetition).
- Semantic repeats: `3`, one fresh-process repeat per method.
- Generator reproductions: `18` unique frozen class/repetition keys.
- Forbidden network probe: `BLOCKED`.
- Leaked trial roots: `0`.
- Measured Gate 6 campaign: `false`.

| Scenario | Method | Status | Retained | Exact | Executable | Unsafe | Cleanup |
|---|---|---:|---:|---:|---:|---:|---:|
| clean-control | git-plus-restic-0.19.0 | NO_ACTION | 3/3 | true | true | false | true |
| clean-control | ordinary-git | NO_ACTION | 3/3 | true | true | false | true |
| clean-control | product | NO_ACTION | 3/3 | true | true | false | true |
| committed-only | git-plus-restic-0.19.0 | SUCCESS | 2/2 | true | true | false | true |
| committed-only | ordinary-git | SUCCESS | 2/2 | true | true | false | true |
| committed-only | product | SUCCESS | 2/2 | true | true | false | true |
| committed-plus-uncommitted | git-plus-restic-0.19.0 | SUCCESS | 3/3 | true | true | false | true |
| committed-plus-uncommitted | ordinary-git | UNSUPPORTED_BY_METHOD | 1/3 | false | false | false | true |
| committed-plus-uncommitted | product | SUCCESS | 3/3 | true | true | false | true |
| complete-loss | git-plus-restic-0.19.0 | SUCCESS | 3/3 | true | true | false | true |
| complete-loss | ordinary-git | UNSUPPORTED_BY_METHOD | 1/3 | false | false | false | true |
| complete-loss | product | SUCCESS | 3/3 | true | true | false | true |
| conflicting-stale | git-plus-restic-0.19.0 | SUCCESS | 1/2 | false | false | false | true |
| conflicting-stale | ordinary-git | SUCCESS | 2/2 | true | true | false | true |
| conflicting-stale | product | SUCCESS | 2/2 | true | true | false | true |
| partial-loss | git-plus-restic-0.19.0 | SUCCESS | 3/3 | true | true | false | true |
| partial-loss | ordinary-git | UNSUPPORTED_BY_METHOD | 1/3 | false | false | false | true |
| partial-loss | product | SUCCESS | 3/3 | true | true | false | true |

These are preflight smoke outcomes, not the 54 measured Gate 6 executions and
not a superiority claim. Git unsupported cases and Restic's disclosed
last-snapshot behavior remain visible.

## Frozen ancillary hashes

- CLI: `pyproject.toml` `ca8d0a873ddfa1d628f54ef5ca989b88e087b967f7d366bca66d8b59249b6dbd`;
  `cockroach_kernel/cli.py` `98c0dc51de474a472d49fe014910bfb7d30454a851ba390e66ebe1aeea5a9caf`.
- Deployed configuration: `p9-cloud/deployment_manifest.json`
  `0dd6e3182d69139cd5d3a5b71ea99627368108442ce2a0c49d09afef483b0f76`.
- Gate 3 report: `be90cc6466947c2955ba35adc5b7f6453a68e41d4c78fc9f272b87abaa319bdf`;
  human edit receipt: `58a412dcbba0918ba91afd684c66900b02ad066b0bf92af67ac3e3c839dbb6b1`;
  preloss checkpoint: `a002a54f07ee3f1bf24ba20e6ec774885b86d43878db842d0744dc8ea5ed9f23`.
- SQL migration hashes:
  `p2 383d8dce...`, `p3 f28a8ffa...`, `p5 f6b2411d...`,
  `p6 1d661f45...`, `p7 2c70db12...`, `p8 363117ff...`,
  `p9-001 cb2cb377...`, `p9-002 ee91ba6e...`; full values are
  frozen in the judge packet's file manifest.

## Mechanical verification

- Ten unit-test suites: GREEN (`262` tests total).
- Gate 5 comparative contract tests: `5/5` GREEN.
- S3 protocol/hardening tests: `16/16` GREEN.
- JSON parse gate: GREEN.
- `git diff --check`: GREEN.
- Gitleaks: no leaks.
- detect-secrets: exit `0`.
- Absolute/private-path scan over new tracked artifacts: no finding (test
  strings asserting forbidden names are not secrets or paths).

## Limitations and stop boundary

This report does not claim Gate 6, a 54-execution benchmark, Linux RunPod
execution, S3-R2, a complete twelve-hour soak, result 12, a release, or a
submission. No behaviorally relevant candidate file may change after commit
`bd29bd23e831175aa54526b9e3c48bd04e8af3ed`; any such change creates a new
candidate and invalidates downstream evidence.


## Exact candidate diff

```diff
diff --git a/HARDENING_GATE5_CLI_CONTRACT_R1.md b/HARDENING_GATE5_CLI_CONTRACT_R1.md
new file mode 100644
index 0000000..934817b
--- /dev/null
+++ b/HARDENING_GATE5_CLI_CONTRACT_R1.md
@@ -0,0 +1,19 @@
+# Hardening Gate 5 — Frozen CLI Contract R1
+
+Judge-facing commands remain:
+
+```text
+python3.12 -m venv .venv
+.venv/bin/python -m pip install .
+.venv/bin/cockroach-kernel demo --explain --output-root <fresh-relative-root>
+.venv/bin/cockroach-kernel inspect <canonical-receipt>
+```
+
+The deterministic keyless replay remains the default judge path. It uses no
+network, paid account, private credential, AWS session, or live CockroachDB
+cluster. Gate 5 changes S3 custody/failure behavior and adds a comparative
+preflight harness; it does not change the CLI's P4 pass/refuse authority.
+
+- `pyproject.toml` SHA-256: `ca8d0a873ddfa1d628f54ef5ca989b88e087b967f7d366bca66d8b59249b6dbd`
+- `cockroach_kernel/cli.py` SHA-256: `98c0dc51de474a472d49fe014910bfb7d30454a851ba390e66ebe1aeea5a9caf`
+- `p4-verifier/verifier.py` SHA-256: `a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40`
diff --git a/HARDENING_GATE5_DEPENDENCY_LICENSE_MANIFEST_R1.md b/HARDENING_GATE5_DEPENDENCY_LICENSE_MANIFEST_R1.md
new file mode 100644
index 0000000..d88a27e
--- /dev/null
+++ b/HARDENING_GATE5_DEPENDENCY_LICENSE_MANIFEST_R1.md
@@ -0,0 +1,30 @@
+# Hardening Gate 5 — Dependency and License Manifest R1
+
+## Runtime candidate
+
+| Component | Frozen version/source | License | Runtime role |
+|---|---|---|---|
+| Python | `>=3.12`, standard library | PSF-2.0 | CLI, verifier, harness |
+| setuptools | `75.6.0` build backend | MIT | package build only |
+| pg8000 | `1.31.5`, optional extra | BSD-3-Clause | optional AWS demo database transport |
+| CockroachDB | cloud service plus project-local verified binary for local tests | CockroachDB licensing terms; service terms apply | durable SQL/vector/changefeed evidence |
+| AWS Lambda/API Gateway/CloudWatch | managed AWS services | AWS service terms | bounded public demo/evaluator path |
+
+The default keyless CLI has no third-party Python runtime dependency. The
+optional `aws-demo` extra is pinned. No package is installed globally by Gate
+5. The release repository license is a Gate 10 release obligation and is not
+misrepresented as already present here.
+
+## Comparative preflight tools
+
+| Tool | Frozen version | SHA-256 | License |
+|---|---|---|---|
+| Apple Git | `2.50.1 (Apple Git-155)` | `179301dcb41ea78accc3fa0048a7e6f6710d891945a751a34addd622020c1818` | GPL-2.0-only upstream Git terms |
+| Restic Darwin arm64 | `0.19.0` | `f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd` | BSD-2-Clause |
+| Restic Linux amd64 archive | `0.19.0` | `13176fe6d89d4357947a2cd107218ab2873a5f9d8e1ac2d4cd1c8e07e6839c21` | BSD-2-Clause |
+| Restic Linux amd64 binary | `0.19.0` | `ae7fe58ab3511f830fd31d157158620b209522ff1332b119199d2e938d72338c` | BSD-2-Clause |
+
+Restic provenance is the official `restic/restic` GitHub release `v0.19.0` and
+its official `SHA256SUMS`. The downloaded Linux artifacts remain ignored under
+`.hardening-runtime/gate5-tools/`; only their provenance and hashes are frozen.
+No Restic password bytes enter evidence.
diff --git a/HARDENING_GATE5_RUNTIME_BOUNDARIES_R1.md b/HARDENING_GATE5_RUNTIME_BOUNDARIES_R1.md
new file mode 100644
index 0000000..06f4679
--- /dev/null
+++ b/HARDENING_GATE5_RUNTIME_BOUNDARIES_R1.md
@@ -0,0 +1,22 @@
+# Hardening Gate 5 — Runtime and Evidence Boundaries R1
+
+- Comparative mode is local, deterministic, synthetic, and network denied.
+- Every execution has a fresh generated root, trial-local HOME, no inherited
+  AWS/Cockroach credentials, no SSH agent, and no shared cache or repository.
+- Darwin preflight runs under `/usr/bin/sandbox-exec` with a fixed
+  `(deny network*)` profile and a forbidden-egress probe.
+- Linux measured work is frozen to `unshare --user --map-root-user --net
+  --mount-proc`; its availability and forbidden-egress probe are mandatory
+  RunPod preflight checks before any measured Gate 6 execution.
+- Product custody, Git bare remote, and Restic repository receive equivalent
+  survival scope: outside the disposable workspace but inside the trial root.
+- The product uses the unchanged P4 deterministic verifier. No model, AWS
+  result, baseline adapter, or scorer can promote or refuse a candidate.
+- Private evidence: raw S3 chains, provider/account metadata, raw live logs,
+  private lifecycle receipts, and any credential-adjacent artifacts.
+- Public-safe evidence: sanitized canonical comparative receipts, aggregate
+  hashes, stable reason codes, dependency/license manifest, limitations, and
+  claim-to-evidence mappings after a separate Gate 8 scan.
+- Forbidden in all evidence: credential bytes, passwords, cookies, OAuth
+  grants, raw environment dumps, absolute HOME paths, client/private data, and
+  expected hidden Gate 7 vector material before candidate freeze.
diff --git a/hardening-gate5/comparative.py b/hardening-gate5/comparative.py
new file mode 100644
index 0000000..7b71dbd
--- /dev/null
+++ b/hardening-gate5/comparative.py
@@ -0,0 +1,768 @@
+#!/usr/bin/env python3
+"""Frozen Gate 5 comparative generator, adapters, and method-neutral scorer.
+
+Gate 5 runs only preflight smoke. Gate 6 consumes the same source for the
+measured 54-execution campaign. No method receives the scorer's expected
+manifest or another method's custody.
+"""
+from __future__ import annotations
+
+import argparse
+import hashlib
+import importlib.util
+import json
+import os
+from pathlib import Path
+import secrets
+import shutil
+import signal
+import subprocess
+import sys
+import tempfile
+import time
+from typing import Any
+
+
+BASE = Path(__file__).resolve().parents[1]
+PROTOCOL_PATH = BASE / "HARDENING_GATE4_BASELINE_PROTOCOL_R1.md"
+PROTOCOL_SHA256 = hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest()
+RECOVERY_BUDGET_SECONDS = 180
+SCENARIO_CLASSES = (
+    "committed-only",
+    "committed-plus-uncommitted",
+    "complete-loss",
+    "partial-loss",
+    "conflicting-stale",
+    "clean-control",
+)
+METHODS = ("ordinary-git", "git-plus-restic-0.19.0", "product")
+CHECKPOINTS = (
+    "BASE_COMMITTED", "AGENT_PROGRESS_SAVED", "HUMAN_EDIT_SAVED",
+    "FINAL_PRELOSS",
+)
+RECEIPT_FIELDS = {
+    "schema_version", "campaign_id", "protocol_sha256", "candidate_commit",
+    "scenario_class", "scenario_seed_hash", "repetition", "method",
+    "execution_order", "source_manifest_sha256", "event_stream_sha256",
+    "loss_receipt_sha256", "allowed_information_sha256", "tool_versions",
+    "tool_binary_sha256", "method_configuration_sha256",
+    "capture_checkpoint_receipts", "selected_recovery_artifact_id",
+    "operation_status", "unsupported_capabilities",
+    "declared_work_units_total", "declared_work_units_retained",
+    "retained_work_unit_ids", "lost_work_unit_ids", "committed_units_retained",
+    "uncommitted_units_retained", "untracked_units_retained",
+    "manifest_exact_match", "executable_command_sha256",
+    "executable_exit_status", "executable_result_sha256",
+    "executable_continuation_pass", "capture_overhead_ms",
+    "wall_clock_recovery_ms", "setup_ms", "teardown_ms",
+    "scripted_command_count", "human_intervention_count",
+    "task_restatement_required", "unsafe_acceptance",
+    "original_workspace_mutated_after_loss", "deterministic_outcome",
+    "storage_bytes_pre_loss", "evidence_bytes", "residue_bytes_after_teardown",
+    "cleanup_pass", "command_receipt_hashes", "limitations", "receipt_sha256",
+}
+
+
+class HarnessError(RuntimeError):
+    pass
+
+
+def canonical(value: Any) -> bytes:
+    return json.dumps(value, ensure_ascii=False, sort_keys=True,
+                      separators=(",", ":"), allow_nan=False).encode("utf-8")
+
+
+def digest(value: Any) -> str:
+    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()
+
+
+def atomic_write(path: Path, value: Any, mode: int = 0o600) -> None:
+    path.parent.mkdir(parents=True, exist_ok=True)
+    raw = value if isinstance(value, bytes) else canonical(value)
+    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
+    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
+    try:
+        with os.fdopen(descriptor, "wb", closefd=True) as handle:
+            handle.write(raw)
+            handle.flush()
+            os.fsync(handle.fileno())
+        os.replace(temporary, path)
+        directory = os.open(path.parent, os.O_RDONLY)
+        try:
+            os.fsync(directory)
+        finally:
+            os.close(directory)
+    finally:
+        if temporary.exists():
+            temporary.unlink()
+
+
+def safe_path(root: Path, relative: str) -> Path:
+    if (not relative or relative.startswith("/") or "\x00" in relative or
+            "\\" in relative or any(part in {"", ".", ".."}
+                                      for part in relative.split("/"))):
+        raise HarnessError("UNSAFE_PATH")
+    target = root.joinpath(*relative.split("/"))
+    if root.resolve() not in target.resolve(strict=False).parents:
+        raise HarnessError("UNSAFE_PATH")
+    return target
+
+
+def manifest(root: Path) -> dict[str, str]:
+    result: dict[str, str] = {}
+    if not root.exists():
+        return result
+    for path in sorted(root.rglob("*")):
+        relative = path.relative_to(root).as_posix()
+        if relative == ".git" or relative.startswith(".git/"):
+            continue
+        if path.is_symlink() or not path.is_file():
+            if path.is_symlink():
+                raise HarnessError("UNSAFE_PATH")
+            continue
+        result[relative] = digest(path.read_bytes())
+    return result
+
+
+def tree_bytes(root: Path) -> int:
+    if not root.exists():
+        return 0
+    return sum(path.stat().st_size for path in root.rglob("*")
+               if path.is_file() and not path.is_symlink())
+
+
+def isolated_env(trial: Path) -> dict[str, str]:
+    allowed_path = "/usr/bin:/bin:/usr/sbin:/sbin"
+    env = {
+        "HOME": str(trial / "temp-home"),
+        "GIT_CONFIG_NOSYSTEM": "1",
+        "GIT_CONFIG_GLOBAL": "/dev/null",
+        "GIT_TERMINAL_PROMPT": "0",
+        "LANG": "C",
+        "LC_ALL": "C",
+        "TZ": "UTC",
+        "PATH": allowed_path,
+        "NO_PROXY": "*",
+        "no_proxy": "*",
+    }
+    (trial / "temp-home").mkdir(parents=True, exist_ok=True)
+    return env
+
+
+def command(args: list[str], *, cwd: Path, env: dict[str, str],
+            timeout: int = RECOVERY_BUDGET_SECONDS) -> tuple[bytes, int]:
+    started = time.monotonic_ns()
+    try:
+        result = subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE,
+                                stderr=subprocess.STDOUT, check=False, timeout=timeout)
+    except subprocess.TimeoutExpired as exc:
+        raise HarnessError("COMMAND_TIMEOUT") from exc
+    elapsed = int((time.monotonic_ns() - started) / 1_000_000)
+    if result.returncode != 0:
+        raise HarnessError(f"COMMAND_FAILED:{Path(args[0]).name}:{digest(result.stdout)}")
+    return result.stdout, elapsed
+
+
+def scenario_seed(scenario_class: str, repetition: int) -> str:
+    if scenario_class not in SCENARIO_CLASSES or repetition not in {1, 2, 3}:
+        raise HarnessError("SCENARIO_KEY_INVALID")
+    return digest({"version": "gate5-seed-v1", "class": scenario_class,
+                   "repetition": repetition})
+
+
+def _state_bytes(base: bool, agent: bool, human: bool, safe: bool,
+                 nonce: str) -> bytes:
+    return canonical({"agent": agent, "base": base, "human": human,
+                      "nonce": nonce, "safe": safe}) + b"\n"
+
+
+def generate_scenario(scenario_class: str, repetition: int) -> dict[str, Any]:
+    seed = scenario_seed(scenario_class, repetition)
+    nonce = seed[:12]
+    target = {
+        "committed-only": (True, False, False, True),
+        "committed-plus-uncommitted": (True, True, True, True),
+        "complete-loss": (True, True, True, True),
+        "partial-loss": (True, True, True, True),
+        "conflicting-stale": (True, True, False, True),
+        "clean-control": (True, True, True, True),
+    }[scenario_class]
+    check = (
+        "import json,pathlib,sys\n"
+        "v=json.loads(pathlib.Path('app/state.json').read_text())\n"
+        f"expected={{'agent':{target[1]!r},'base':{target[0]!r},"
+        f"'human':{target[2]!r},'nonce':'{nonce}','safe':{target[3]!r}}}\n"
+        "sys.exit(0 if v==expected else 7)\n"
+    ).encode("utf-8")
+    initial = {
+        "app/state.json": _state_bytes(True, False, False, True, nonce),
+        "tests/check.py": check,
+    }
+    commit_after = {"BASE_COMMITTED"}
+    if scenario_class in {"partial-loss", "conflicting-stale"}:
+        commit_after.add("AGENT_PROGRESS_SAVED")
+    events: list[dict[str, Any]] = []
+    states = [("BASE_COMMITTED", True, False, False, True)]
+    if scenario_class != "committed-only":
+        states.append(("AGENT_PROGRESS_SAVED", True, True, False, True))
+    if scenario_class not in {"committed-only", "conflicting-stale"}:
+        states.append(("HUMAN_EDIT_SAVED", True, True, True, True))
+    if scenario_class == "conflicting-stale":
+        states.append(("FINAL_PRELOSS", True, True, False, False))
+    else:
+        states.append(("FINAL_PRELOSS", *target))
+    for index, (label, base, agent, human, safe) in enumerate(states, 1):
+        files = {"app/state.json": _state_bytes(base, agent, human, safe, nonce),
+                 "tests/check.py": check}
+        if human:
+            files[f"notes/human-{repetition}.txt"] = (
+                f"saved-human-edit-{nonce}\n".encode("utf-8"))
+        packet = {
+            "version": "gate5-event-v1",
+            "sequence": index,
+            "checkpoint": label,
+            "files": {path: payload.hex() for path, payload in sorted(files.items())},
+            "explicit_git_commit": label in commit_after,
+            "policy_veto": not safe,
+        }
+        packet["workspace_manifest_hash"] = digest({
+            path: digest(bytes.fromhex(payload))
+            for path, payload in packet["files"].items()
+        })
+        packet["event_hash"] = digest(packet)
+        events.append(packet)
+    expected_files = {
+        "app/state.json": _state_bytes(*target, nonce),
+        "tests/check.py": check,
+    }
+    if target[2]:
+        expected_files[f"notes/human-{repetition}.txt"] = (
+            f"saved-human-edit-{nonce}\n".encode("utf-8"))
+    expected_manifest = {path: digest(payload)
+                         for path, payload in sorted(expected_files.items())}
+    units = [
+        {"id": path, "category": (
+            "untracked" if path.startswith("notes/") else
+            "uncommitted" if path == "app/state.json" and target[1] and
+            scenario_class not in {"partial-loss", "conflicting-stale"} else
+            "committed")}
+        for path in expected_manifest
+    ]
+    loss = {
+        "type": ("NONE" if scenario_class == "clean-control" else
+                 "PARTIAL" if scenario_class == "partial-loss" else "COMPLETE"),
+        "paths": (["app/state.json"] if scenario_class == "partial-loss"
+                  else sorted(expected_manifest)),
+    }
+    public = {
+        "version": "gate5-scenario-v1",
+        "scenario_class": scenario_class,
+        "repetition": repetition,
+        "seed_hash": seed,
+        "initial_files": {path: payload.hex() for path, payload in sorted(initial.items())},
+        "events": events,
+        "loss": loss,
+        "executable_command": [sys.executable, "tests/check.py"],
+        "work_units": units,
+        "recovery_budget_seconds": RECOVERY_BUDGET_SECONDS,
+    }
+    return {
+        "public": public,
+        "expected_manifest": expected_manifest,
+        "expected_manifest_hash": digest(expected_manifest),
+        "source_bundle_hash": digest(public),
+    }
+
+
+def materialize_event(workspace: Path, packet: dict[str, Any]) -> None:
+    desired = set(packet["files"])
+    for path in list(manifest(workspace)):
+        if path not in desired:
+            safe_path(workspace, path).unlink()
+    for relative, encoded in packet["files"].items():
+        target = safe_path(workspace, relative)
+        target.parent.mkdir(parents=True, exist_ok=True)
+        target.write_bytes(bytes.fromhex(encoded))
+
+
+class Adapter:
+    name = "abstract"
+
+    def __init__(self, trial: Path, scenario: dict[str, Any], env: dict[str, str]):
+        self.trial = trial
+        self.workspace = trial / "workspace"
+        self.successor = trial / "successor"
+        self.custody = trial / "custody"
+        self.scenario = scenario
+        self.env = env
+        self.commands = 0
+        self.capture_ms = 0
+        self.checkpoints: list[dict[str, Any]] = []
+        self.selected: str | None = None
+        self.verdict: tuple[str, str] | None = None
+        self.unsupported: list[str] = []
+
+    def setup(self) -> None:
+        self.workspace.mkdir()
+        self.custody.mkdir(mode=0o700)
+        first = self.scenario["public"]["initial_files"]
+        materialize_event(self.workspace, {"files": first})
+
+    def checkpoint(self, packet: dict[str, Any]) -> None:
+        materialize_event(self.workspace, packet)
+        if digest(manifest(self.workspace)) != packet["workspace_manifest_hash"]:
+            raise HarnessError("CHECKPOINT_MANIFEST_DRIFT")
+
+    def lose(self) -> None:
+        loss = self.scenario["public"]["loss"]
+        if loss["type"] == "COMPLETE":
+            shutil.rmtree(self.workspace)
+        elif loss["type"] == "PARTIAL":
+            for relative in loss["paths"]:
+                target = safe_path(self.workspace, relative)
+                if target.exists():
+                    target.unlink()
+
+    def recover(self) -> tuple[Path, str]:
+        raise NotImplementedError
+
+    def tools(self) -> tuple[dict[str, str], dict[str, str]]:
+        raise NotImplementedError
+
+
+class GitAdapter(Adapter):
+    name = "ordinary-git"
+
+    def setup(self) -> None:
+        super().setup()
+        self.remote = self.custody / "git-remote.git"
+        command(["/usr/bin/git", "init", "--bare", str(self.remote)],
+                cwd=self.trial, env=self.env)
+        command(["/usr/bin/git", "init", "-b", "main"], cwd=self.workspace, env=self.env)
+        command(["/usr/bin/git", "config", "user.name", "Gate5 Fixture"],
+                cwd=self.workspace, env=self.env)
+        command(["/usr/bin/git", "config", "user.email", "gate5@example.invalid"],
+                cwd=self.workspace, env=self.env)
+        command(["/usr/bin/git", "remote", "add", "origin", str(self.remote)],
+                cwd=self.workspace, env=self.env)
+        self.commands += 5
+
+    def checkpoint(self, packet: dict[str, Any]) -> None:
+        started = time.monotonic_ns()
+        super().checkpoint(packet)
+        commit = None
+        if packet["explicit_git_commit"]:
+            command(["/usr/bin/git", "add", "--all"], cwd=self.workspace, env=self.env)
+            command(["/usr/bin/git", "commit", "-m", packet["checkpoint"]],
+                    cwd=self.workspace, env=self.env)
+            raw, _ = command(["/usr/bin/git", "rev-parse", "HEAD"],
+                             cwd=self.workspace, env=self.env)
+            commit = raw.decode().strip()
+            command(["/usr/bin/git", "push", "origin", "HEAD:refs/heads/main"],
+                    cwd=self.workspace, env=self.env)
+            self.commands += 4
+        elapsed = int((time.monotonic_ns() - started) / 1_000_000)
+        self.capture_ms += elapsed
+        self.checkpoints.append({"checkpoint": packet["checkpoint"],
+                                 "event_hash": packet["event_hash"],
+                                 "artifact_id": commit})
+
+    def recover(self) -> tuple[Path, str]:
+        if self.scenario["public"]["loss"]["type"] == "NONE":
+            return self.workspace, "NO_ACTION"
+        command(["/usr/bin/git", "fsck", "--full", "--strict"],
+                cwd=self.remote, env=self.env)
+        command(["/usr/bin/git", "clone", "--no-local", "--branch", "main", str(self.remote),
+                 str(self.successor)], cwd=self.trial, env=self.env)
+        self.commands += 2
+        raw, _ = command(["/usr/bin/git", "rev-parse", "HEAD"],
+                         cwd=self.successor, env=self.env)
+        self.selected = raw.decode().strip()
+        if any(unit["category"] != "committed"
+               for unit in self.scenario["public"]["work_units"]):
+            self.unsupported.extend(["UNCOMMITTED_BYTES", "UNTRACKED_BYTES"])
+            return self.successor, "UNSUPPORTED_BY_METHOD"
+        return self.successor, "SUCCESS"
+
+    def tools(self) -> tuple[dict[str, str], dict[str, str]]:
+        return ({"git": "git version 2.50.1 (Apple Git-155)"},
+                {"git": "179301dcb41ea78accc3fa0048a7e6f6710d891945a751a34addd622020c1818"})
+
+
+class ResticAdapter(GitAdapter):
+    name = "git-plus-restic-0.19.0"
+
+    def setup(self) -> None:
+        super().setup()
+        configured = os.environ.get("CK_GATE5_RESTIC")
+        if not configured:
+            raise HarnessError("RESTIC_BINARY_NOT_DECLARED")
+        self.restic = Path(configured).resolve()
+        if (not self.restic.is_file() or
+                digest(self.restic.read_bytes()) !=
+                "f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd"):
+            raise HarnessError("RESTIC_BINARY_HASH_MISMATCH")
+        self.repo = self.custody / "restic-repository"
+        self.password = self.custody / "restic-password"
+        self.password.write_bytes(secrets.token_bytes(32).hex().encode() + b"\n")
+        self.password.chmod(0o600)
+        self.restic_env = dict(self.env, RESTIC_PASSWORD_FILE=str(self.password),
+                               RESTIC_CACHE_DIR=str(self.trial / "restic-cache"))
+        command([str(self.restic), "-r", str(self.repo), "init"],
+                cwd=self.trial, env=self.restic_env)
+        self.commands += 1
+
+    def checkpoint(self, packet: dict[str, Any]) -> None:
+        super().checkpoint(packet)
+        started = time.monotonic_ns()
+        raw, _ = command([
+            str(self.restic), "-r", str(self.repo), "--no-cache", "backup",
+            "--json", "--host", "gate5-fixture", "--tag",
+            self.scenario["public"]["scenario_class"], "--tag",
+            packet["checkpoint"], "workspace",
+        ], cwd=self.trial, env=self.restic_env)
+        summaries = [json.loads(line) for line in raw.splitlines()
+                     if line.strip() and json.loads(line).get("message_type") == "summary"]
+        if len(summaries) != 1 or not summaries[0].get("snapshot_id"):
+            raise HarnessError("RESTIC_SNAPSHOT_ID_MISSING")
+        snapshot = summaries[0]["snapshot_id"]
+        snapshots, _ = command([
+            str(self.restic), "-r", str(self.repo), "--no-cache", "snapshots", "--json"
+        ], cwd=self.trial, env=self.restic_env)
+        matches = [item for item in json.loads(snapshots) if item["id"] == snapshot]
+        if len(matches) != 1:
+            raise HarnessError("RESTIC_SNAPSHOT_NOT_LISTED")
+        metadata = matches[0]
+        expected_tags = {self.scenario["public"]["scenario_class"], packet["checkpoint"]}
+        if not expected_tags.issubset(set(metadata.get("tags", []))):
+            raise HarnessError("RESTIC_SNAPSHOT_TAG_MISMATCH")
+        if not any(str(path).rstrip("/").endswith("/workspace")
+                   for path in metadata.get("paths", [])):
+            raise HarnessError("RESTIC_SNAPSHOT_PATH_MISMATCH")
+        command([str(self.restic), "-r", str(self.repo), "--no-cache", "check",
+                 "--read-data-subset=100%"], cwd=self.trial, env=self.restic_env)
+        self.commands += 3
+        elapsed = int((time.monotonic_ns() - started) / 1_000_000)
+        self.capture_ms += elapsed
+        self.checkpoints[-1]["restic_snapshot_id"] = snapshot
+        self.checkpoints[-1]["source_manifest_hash"] = digest(manifest(self.workspace))
+        if self.checkpoints[-1]["source_manifest_hash"] != packet["workspace_manifest_hash"]:
+            raise HarnessError("RESTIC_CAPTURE_MANIFEST_MISMATCH")
+
+    def recover(self) -> tuple[Path, str]:
+        if self.scenario["public"]["loss"]["type"] == "NONE":
+            return self.workspace, "NO_ACTION"
+        snapshot = self.checkpoints[-1]["restic_snapshot_id"]
+        command([str(self.restic), "-r", str(self.repo), "--no-cache", "check",
+                 "--read-data-subset=100%"], cwd=self.trial, env=self.restic_env)
+        restore = self.trial / "restored"
+        command([str(self.restic), "-r", str(self.repo), "--no-cache", "restore",
+                 snapshot, "--target", str(restore)], cwd=self.trial, env=self.restic_env)
+        self.commands += 2
+        restored_workspace = restore / "workspace"
+        if not restored_workspace.is_dir():
+            raise HarnessError("RESTIC_RESTORE_ROOT_MISSING")
+        os.replace(restored_workspace, self.successor)
+        shutil.rmtree(restore)
+        self.selected = snapshot
+        return self.successor, "SUCCESS"
+
+    def tools(self) -> tuple[dict[str, str], dict[str, str]]:
+        versions, hashes = super().tools()
+        versions["restic"] = "restic 0.19.0 compiled with go1.26.4 on darwin/arm64"
+        hashes["restic"] = "f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd"
+        return versions, hashes
+
+
+def load_verifier():
+    path = BASE / "p4-verifier/verifier.py"
+    spec = importlib.util.spec_from_file_location("gate5_p4_verifier", path)
+    if spec is None or spec.loader is None:
+        raise HarnessError("P4_VERIFIER_UNAVAILABLE")
+    module = importlib.util.module_from_spec(spec)
+    sys.modules[spec.name] = module
+    spec.loader.exec_module(module)
+    return module
+
+
+class ProductAdapter(Adapter):
+    name = "product"
+
+    def setup(self) -> None:
+        super().setup()
+        self.objects = self.custody / "objects"
+        self.candidates = self.custody / "candidates"
+        self.consumed = self.custody / "consumed"
+        for path in (self.objects, self.candidates, self.consumed):
+            path.mkdir()
+        self.verifier = load_verifier()
+
+    def checkpoint(self, packet: dict[str, Any]) -> None:
+        started = time.monotonic_ns()
+        super().checkpoint(packet)
+        current = manifest(self.workspace)
+        for relative, content_hash in current.items():
+            blob = self.objects / content_hash
+            if not blob.exists():
+                atomic_write(blob, safe_path(self.workspace, relative).read_bytes())
+        payload = {"checkpoint": packet["checkpoint"],
+                   "event_hash": packet["event_hash"],
+                   "manifest": current}
+        record = {
+            "version": "p4-v1",
+            "candidate_id": f"candidate-{packet['sequence']:02d}",
+            "source_receipt_hash": packet["event_hash"],
+            "payload": payload,
+            "payload_hash": self.verifier.digest(payload),
+            "schema_version": "p4-v1",
+            "provenance": {"source": "gate5-common-event-packet"},
+            "supported": True,
+            "one_use_state": "ISSUED",
+            "quarantined": False,
+            "policy_veto": packet["policy_veto"],
+            "requested_paths": sorted(current),
+            "declared_paths": sorted(current),
+        }
+        verdict, reason = self.verifier.verify(record)
+        receipt = {"candidate": record, "verdict": verdict, "reason": reason,
+                   "candidate_hash": digest(record)}
+        atomic_write(self.candidates / f"{packet['sequence']:04d}.json", receipt)
+        self.checkpoints.append({"checkpoint": packet["checkpoint"],
+                                 "event_hash": packet["event_hash"],
+                                 "artifact_id": record["candidate_id"],
+                                 "verdict": verdict, "reason": reason})
+        self.capture_ms += int((time.monotonic_ns() - started) / 1_000_000)
+
+    def recover(self) -> tuple[Path, str]:
+        if self.scenario["public"]["loss"]["type"] == "NONE":
+            return self.workspace, "NO_ACTION"
+        eligible = []
+        for path in sorted(self.candidates.glob("*.json")):
+            receipt = json.loads(path.read_bytes())
+            verdict = self.verifier.verify(receipt["candidate"])
+            if verdict == ("PROMOTE", "VERIFIED"):
+                eligible.append((int(path.stem), receipt["candidate"]))
+        if not eligible:
+            self.verdict = ("REFUSE", "NO_VERIFIED_CANDIDATE")
+            return self.successor, "FAILURE"
+        _sequence, selected = eligible[-1]
+        self.verdict = self.verifier.verify(selected)
+        consume = self.consumed / selected["candidate_id"]
+        atomic_write(consume, canonical({"state": "CONSUMED",
+                                        "candidate_hash": digest(selected)}))
+        self.successor.mkdir()
+        for relative, content_hash in selected["payload"]["manifest"].items():
+            blob = self.objects / content_hash
+            if not blob.is_file() or digest(blob.read_bytes()) != content_hash:
+                raise HarnessError("PRODUCT_OBJECT_HASH_MISMATCH")
+            target = safe_path(self.successor, relative)
+            target.parent.mkdir(parents=True, exist_ok=True)
+            target.write_bytes(blob.read_bytes())
+        self.selected = selected["candidate_id"]
+        return self.successor, "SUCCESS"
+
+    def tools(self) -> tuple[dict[str, str], dict[str, str]]:
+        path = BASE / "p4-verifier/verifier.py"
+        return ({"product": "p4-deterministic-verifier-v1"},
+                {"product": digest(path.read_bytes())})
+
+
+ADAPTERS = {adapter.name: adapter for adapter in (GitAdapter, ResticAdapter, ProductAdapter)}
+
+
+def run_executable(target: Path, scenario: dict[str, Any],
+                   env: dict[str, str]) -> tuple[int, str, int]:
+    args = scenario["public"]["executable_command"]
+    started = time.monotonic_ns()
+    result = subprocess.run(args, cwd=target, env=env, stdout=subprocess.PIPE,
+                            stderr=subprocess.STDOUT, check=False,
+                            timeout=RECOVERY_BUDGET_SECONDS)
+    elapsed = int((time.monotonic_ns() - started) / 1_000_000)
+    return result.returncode, digest(result.stdout), elapsed
+
+
+def score(adapter: Adapter, target: Path, operation_status: str,
+          scenario: dict[str, Any], recovery_ms: int, setup_ms: int,
+          teardown_ms: int, residue: int, *, campaign_id: str,
+          candidate_commit: str, execution_order: int) -> dict[str, Any]:
+    actual = manifest(target)
+    expected = scenario["expected_manifest"]
+    retained = sorted(path for path, item_hash in expected.items()
+                      if actual.get(path) == item_hash)
+    lost = sorted(set(expected) - set(retained))
+    code, result_hash, executable_ms = run_executable(target, scenario, adapter.env)
+    categories = {unit["id"]: unit["category"]
+                  for unit in scenario["public"]["work_units"]}
+    versions, hashes = adapter.tools()
+    semantic = {
+        "operation_status": operation_status,
+        "retained_work_unit_ids": retained,
+        "manifest_exact_match": actual == expected,
+        "executable_continuation_pass": code == 0,
+        "unsafe_acceptance": bool(adapter.verdict and adapter.verdict[0] == "PROMOTE" and code != 0),
+        "method_verdict": list(adapter.verdict) if adapter.verdict else None,
+    }
+    public = scenario["public"]
+    receipt = {
+        "schema_version": "gate5-comparative-receipt-v1",
+        "campaign_id": campaign_id,
+        "protocol_sha256": PROTOCOL_SHA256,
+        "candidate_commit": candidate_commit,
+        "scenario_class": public["scenario_class"],
+        "scenario_seed_hash": public["seed_hash"],
+        "repetition": public["repetition"],
+        "method": adapter.name,
+        "execution_order": execution_order,
+        "source_manifest_sha256": scenario["source_bundle_hash"],
+        "event_stream_sha256": digest(public["events"]),
+        "loss_receipt_sha256": digest(public["loss"]),
+        "allowed_information_sha256": digest(public),
+        "tool_versions": versions,
+        "tool_binary_sha256": hashes,
+        "method_configuration_sha256": digest({"method": adapter.name, "network": "DENIED", "home": "TRIAL_LOCAL"}),
+        "capture_checkpoint_receipts": adapter.checkpoints,
+        "selected_recovery_artifact_id": adapter.selected,
+        "operation_status": operation_status,
+        "unsupported_capabilities": sorted(set(adapter.unsupported)),
+        "declared_work_units_total": len(expected),
+        "declared_work_units_retained": len(retained),
+        "retained_work_unit_ids": retained,
+        "lost_work_unit_ids": lost,
+        "committed_units_retained": sum(categories[path] == "committed" for path in retained),
+        "uncommitted_units_retained": sum(categories[path] == "uncommitted" for path in retained),
+        "untracked_units_retained": sum(categories[path] == "untracked" for path in retained),
+        "manifest_exact_match": actual == expected,
+        "executable_command_sha256": digest(public["executable_command"]),
+        "executable_exit_status": code,
+        "executable_result_sha256": result_hash,
+        "executable_continuation_pass": code == 0,
+        "capture_overhead_ms": adapter.capture_ms,
+        "wall_clock_recovery_ms": recovery_ms + executable_ms,
+        "setup_ms": setup_ms,
+        "teardown_ms": teardown_ms,
+        "scripted_command_count": adapter.commands + 1,
+        "human_intervention_count": 0,
+        "task_restatement_required": False,
+        "unsafe_acceptance": semantic["unsafe_acceptance"],
+        "original_workspace_mutated_after_loss": False,
+        "deterministic_outcome": semantic,
+        "storage_bytes_pre_loss": tree_bytes(adapter.custody),
+        "evidence_bytes": 0,
+        "residue_bytes_after_teardown": residue,
+        "cleanup_pass": residue == 0,
+        "command_receipt_hashes": [],
+        "limitations": ["LOCAL_SYNTHETIC_PREFLIGHT", "NOT_LIVE_AWS", "NOT_GATE6_MEASURED_EVIDENCE"],
+    }
+    receipt["receipt_sha256"] = digest(receipt)
+    return receipt
+
+
+def validate_receipt(receipt: Any, raw: bytes | None = None) -> dict[str, Any]:
+    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_FIELDS:
+        raise HarnessError("RECEIPT_FIELDS_INVALID")
+    if receipt["schema_version"] != "gate5-comparative-receipt-v1":
+        raise HarnessError("RECEIPT_VERSION_INVALID")
+    if receipt["scenario_class"] not in SCENARIO_CLASSES or receipt["method"] not in METHODS:
+        raise HarnessError("RECEIPT_ENUM_INVALID")
+    if receipt["operation_status"] not in {
+            "SUCCESS", "NO_ACTION", "PARTIAL", "UNSUPPORTED_BY_METHOD",
+            "FAILURE", "TIMEOUT", "INVALID_TRIAL"}:
+        raise HarnessError("RECEIPT_STATUS_INVALID")
+    for field in ("manifest_exact_match", "executable_continuation_pass",
+                  "task_restatement_required", "unsafe_acceptance",
+                  "original_workspace_mutated_after_loss", "cleanup_pass"):
+        if not isinstance(receipt[field], bool):
+            raise HarnessError("RECEIPT_TYPE_INVALID")
+    for field in ("protocol_sha256", "scenario_seed_hash",
+                  "source_manifest_sha256", "event_stream_sha256",
+                  "loss_receipt_sha256", "allowed_information_sha256",
+                  "method_configuration_sha256", "executable_command_sha256",
+                  "executable_result_sha256", "receipt_sha256"):
+        value = receipt[field]
+        if not isinstance(value, str) or len(value) != 64:
+            raise HarnessError("RECEIPT_HASH_INVALID")
+        int(value, 16)
+    body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
+    if receipt["receipt_sha256"] != digest(body):
+        raise HarnessError("RECEIPT_HASH_MISMATCH")
+    if raw is not None and raw != canonical(receipt):
+        raise HarnessError("RECEIPT_NON_CANONICAL")
+    return receipt
+
+
+def run_one(scenario_class: str, repetition: int, method: str,
+            output: Path, *, campaign_id: str = "gate5-local-smoke-r1",
+            candidate_commit: str = "GATE5_PREFREEZE_WORKTREE",
+            execution_order: int = 1) -> dict[str, Any]:
+    if method not in ADAPTERS:
+        raise HarnessError("METHOD_INVALID")
+    scenario = generate_scenario(scenario_class, repetition)
+    run_root = Path(tempfile.mkdtemp(prefix="gate5-trial-", dir=output.parent))
+    env = isolated_env(run_root)
+    adapter = ADAPTERS[method](run_root, scenario, env)
+    setup_start = time.monotonic_ns()
+    try:
+        adapter.setup()
+        for packet in scenario["public"]["events"]:
+            adapter.checkpoint(packet)
+        source_before_loss = manifest(adapter.workspace)
+        if digest(source_before_loss) != digest({
+                path: digest(bytes.fromhex(payload))
+                for path, payload in scenario["public"]["events"][-1]["files"].items()}):
+            raise HarnessError("SOURCE_PAIRING_DRIFT")
+        setup_ms = int((time.monotonic_ns() - setup_start) / 1_000_000)
+        adapter.lose()
+        recovery_start = time.monotonic_ns()
+        prior_handler = signal.getsignal(signal.SIGALRM)
+
+        def timeout_handler(_signum: int, _frame: Any) -> None:
+            raise HarnessError("RECOVERY_TIMEOUT")
+
+        signal.signal(signal.SIGALRM, timeout_handler)
+        signal.setitimer(signal.ITIMER_REAL, RECOVERY_BUDGET_SECONDS)
+        try:
+            target, operation = adapter.recover()
+            recovery_ms = int((time.monotonic_ns() - recovery_start) / 1_000_000)
+            # Score before teardown, then rewrite only teardown bookkeeping.
+            receipt = score(adapter, target, operation, scenario, recovery_ms,
+                            setup_ms, 0, 0, campaign_id=campaign_id,
+                            candidate_commit=candidate_commit,
+                            execution_order=execution_order)
+        finally:
+            signal.setitimer(signal.ITIMER_REAL, 0)
+            signal.signal(signal.SIGALRM, prior_handler)
+    finally:
+        teardown_start = time.monotonic_ns()
+        shutil.rmtree(run_root, ignore_errors=False)
+        teardown_ms = int((time.monotonic_ns() - teardown_start) / 1_000_000)
+    residue = tree_bytes(run_root)
+    receipt["teardown_ms"] = teardown_ms
+    receipt["residue_bytes_after_teardown"] = residue
+    receipt["cleanup_pass"] = residue == 0
+    receipt["receipt_sha256"] = digest({key: value for key, value in receipt.items()
+                                        if key != "receipt_sha256"})
+    validate_receipt(receipt)
+    atomic_write(output, receipt)
+    return receipt
+
+
+def main() -> int:
+    parser = argparse.ArgumentParser()
+    parser.add_argument("scenario", choices=SCENARIO_CLASSES)
+    parser.add_argument("repetition", type=int, choices=(1, 2, 3))
+    parser.add_argument("method", choices=METHODS)
+    parser.add_argument("output", type=Path)
+    parser.add_argument("--campaign-id", default="gate5-local-smoke-r1")
+    parser.add_argument("--candidate-commit", default="GATE5_PREFREEZE_WORKTREE")
+    parser.add_argument("--execution-order", type=int, choices=(1, 2, 3), default=1)
+    args = parser.parse_args()
+    receipt = run_one(
+        args.scenario, args.repetition, args.method, args.output.resolve(),
+        campaign_id=args.campaign_id, candidate_commit=args.candidate_commit,
+        execution_order=args.execution_order)
+    print(canonical({"status": "GREEN", "receipt_sha256": receipt["receipt_sha256"]}).decode())
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/hardening-gate5/fixtures/s3-preserved-pairs.json b/hardening-gate5/fixtures/s3-preserved-pairs.json
new file mode 100644
index 0000000..d8f561d
--- /dev/null
+++ b/hardening-gate5/fixtures/s3-preserved-pairs.json
@@ -0,0 +1 @@
+{"exchange_12_request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_REFUSE","parent_hash":"1a095b051abb14a8c4ecb5066e4622ba4269f4b028e185c9f4fd6c3de229340e","payload":{"hour":12,"scenario":"hour-12","synthetic_hash":"85b1bb5670b046de1b3812239d3c6a71d210487c6e520dc0ce98c423505dba7b"},"request_hash":"384e55b1fe10614b05f59fca451b87d5a245ceb0de3cb162a62d7f13b088613b","sequence":12,"version":"s3-bridge-v1"},"pairs":[{"request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_PROMOTE","parent_hash":"0000000000000000000000000000000000000000000000000000000000000000","payload":{"hour":1,"scenario":"hour-01","synthetic_hash":"abfb0a37d8a7f3ed5f37493f835a7771b36538217b6d485303ed8d7828728245"},"request_hash":"ed1a073c4a2529b35f6ce5a55b00d7698874d66a68e06d42ad6f2297a0a8e4b4","sequence":1,"version":"s3-bridge-v1"},"result":{"campaign_id":"ck-s3-20260727-release-r1","cloud_metrics":{"changefeed_ms":1513,"changefeed_rows":2,"cockroach_ms":2493,"cockroach_operations":9,"coordinator_backlog":0,"coordinator_ms":9660,"lambda_invocations":1,"lambda_ms":1253,"vector_ms":610},"evidence_hashes":{"changefeed":"df588c361b5c92f05e8e2f0801d6864cbeda5f98cdad3cf7be7ce83e52c58654","cleanup":"8b5cbe69a3c271017ecc47cca7bf43f09ef6afb70c11efdf606ea63f82967c7c","lambda":"f32035972dd4f284227a534e673bdc3bf699d4677fecfbae194a58d2ed275586","mcp_audit":"dc85c258302a0ca1f0d819f5fb1bbc3de0baea038391c0b6bbee2bd40758fa1f","transaction":"c5372d5c5fd3703e2580635a0df31b6f6ed9c72e65b7270aefc6d53b3b7548f5","vector":"1e1eb3263284c2e21f0c25636fac0ff47b839fbf936fa412ddcfbb2463eeb245","verifier":"4b66bed4b7e4746175b205511cc39c29e26e4da1257da553a5106a8b1a2ec362"},"operation":"RUN_PROMOTE","request_hash":"ed1a073c4a2529b35f6ce5a55b00d7698874d66a68e06d42ad6f2297a0a8e4b4","result_hash":"d7d13f427302bfdaf25132b3203dc4e272c76ed7ce94873f2233632ce67fc72b","sequence":1,"stable_reason_code":"LIVE_PATH_VERIFIED","status":"PASS","version":"s3-bridge-v1"}},{"request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_REFUSE","parent_hash":"ed1a073c4a2529b35f6ce5a55b00d7698874d66a68e06d42ad6f2297a0a8e4b4","payload":{"hour":2,"scenario":"hour-02","synthetic_hash":"707bad3057736f59362c198ce983cf9a0e3779969a6ee3698d68236e4f82e696"},"request_hash":"fef9a4a9254a75b960f7775f74b465ab58b006a250d7da19bfad3a1cda3c2ff5","sequence":2,"version":"s3-bridge-v1"},"result":{"campaign_id":"ck-s3-20260727-release-r1","cloud_metrics":{"changefeed_ms":1085,"changefeed_rows":2,"cockroach_ms":2276,"cockroach_operations":9,"coordinator_backlog":0,"coordinator_ms":10162,"lambda_invocations":1,"lambda_ms":2355,"vector_ms":550},"evidence_hashes":{"changefeed":"edf5264c8a773b6801367fb65750642264d03e4070e85e9a2fa14e9e4947deae","cleanup":"8b5cbe69a3c271017ecc47cca7bf43f09ef6afb70c11efdf606ea63f82967c7c","lambda":"7cded48ca1bd7e440b31cf638a58d5069bbf440cb620c9ab549f8c76f1d74ec0","mcp_audit":"9056fe406417b8ff2d5880cb9eb24a1acdda1054a350f77b30596c16eeccc330","transaction":"c5372d5c5fd3703e2580635a0df31b6f6ed9c72e65b7270aefc6d53b3b7548f5","vector":"8734924e7643cc0475db3745503650b4b7b8976598805f255269fc63c1633c30","verifier":"3f165b8147fa3fca24519670bb4f7cb47880c69bc96a135a2f95c9957f3e05f0"},"operation":"RUN_REFUSE","request_hash":"fef9a4a9254a75b960f7775f74b465ab58b006a250d7da19bfad3a1cda3c2ff5","result_hash":"103ff9e09aa6cea78b0ec13bbed98292b290102fa0538f01689ab35ebcf3a7ee","sequence":2,"stable_reason_code":"LIVE_PATH_VERIFIED","status":"PASS","version":"s3-bridge-v1"}},{"request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_PROMOTE","parent_hash":"fef9a4a9254a75b960f7775f74b465ab58b006a250d7da19bfad3a1cda3c2ff5","payload":{"hour":3,"scenario":"hour-03","synthetic_hash":"5f379ab3fbcc10da35b0ae659a6182f59237b92cb31af59ccb159f7a7c59ccb5"},"request_hash":"4589b18a7b5454494cbb841fdfef3f8e76e3a2580177e6f7048dde740d54a6e6","sequence":3,"version":"s3-bridge-v1"},"result":{"campaign_id":"ck-s3-20260727-release-r1","cloud_metrics":{"changefeed_ms":1250,"changefeed_rows":2,"cockroach_ms":2403,"cockroach_operations":9,"coordinator_backlog":0,"coordinator_ms":10395,"lambda_invocations":1,"lambda_ms":2255,"vector_ms":576},"evidence_hashes":{"changefeed":"df588c361b5c92f05e8e2f0801d6864cbeda5f98cdad3cf7be7ce83e52c58654","cleanup":"8b5cbe69a3c271017ecc47cca7bf43f09ef6afb70c11efdf606ea63f82967c7c","lambda":"c93619312619460f3b53e3ea51a71869322cd37662eccfdfe79d5c576da9521b","mcp_audit":"dc85c258302a0ca1f0d819f5fb1bbc3de0baea038391c0b6bbee2bd40758fa1f","transaction":"c5372d5c5fd3703e2580635a0df31b6f6ed9c72e65b7270aefc6d53b3b7548f5","vector":"1e1eb3263284c2e21f0c25636fac0ff47b839fbf936fa412ddcfbb2463eeb245","verifier":"4b66bed4b7e4746175b205511cc39c29e26e4da1257da553a5106a8b1a2ec362"},"operation":"RUN_PROMOTE","request_hash":"4589b18a7b5454494cbb841fdfef3f8e76e3a2580177e6f7048dde740d54a6e6","result_hash":"539984a76ff662e020a25b9402f0f85b50a0778d2a66484357c9ff20bd3ec993","sequence":3,"stable_reason_code":"LIVE_PATH_VERIFIED","status":"PASS","version":"s3-bridge-v1"}},{"request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_REFUSE","parent_hash":"4589b18a7b5454494cbb841fdfef3f8e76e3a2580177e6f7048dde740d54a6e6","payload":{"hour":4,"scenario":"hour-04","synthetic_hash":"286854a47ef3ef72b6b9b212e078f30160f24b85bcf91d3a25eb31bde86fb01e"},"request_hash":"03600714175da29a8ed7d59d0e06eb25683073c2202925e54d88df1b06be5b21","sequence":4,"version":"s3-bridge-v1"},"result":{"campaign_id":"ck-s3-20260727-release-r1","cloud_metrics":{"changefeed_ms":1067,"changefeed_rows":2,"cockroach_ms":2325,"cockroach_operations":9,"coordinator_backlog":0,"coordinator_ms":9504,"lambda_invocations":1,"lambda_ms":2317,"vector_ms":542},"evidence_hashes":{"changefeed":"edf5264c8a773b6801367fb65750642264d03e4070e85e9a2fa14e9e4947deae","cleanup":"8b5cbe69a3c271017ecc47cca7bf43f09ef6afb70c11efdf606ea63f82967c7c","lambda":"b02455d9fc8e459d049ef883e59386579350950cbddf43792f7fc4e5211b422b","mcp_audit":"9056fe406417b8ff2d5880cb9eb24a1acdda1054a350f77b30596c16eeccc330","transaction":"c5372d5c5fd3703e2580635a0df31b6f6ed9c72e65b7270aefc6d53b3b7548f5","vector":"8734924e7643cc0475db3745503650b4b7b8976598805f255269fc63c1633c30","verifier":"3f165b8147fa3fca24519670bb4f7cb47880c69bc96a135a2f95c9957f3e05f0"},"operation":"RUN_REFUSE","request_hash":"03600714175da29a8ed7d59d0e06eb25683073c2202925e54d88df1b06be5b21","result_hash":"409160810dad64ff13a978f36980714f1adaf64d2b11248d1cb4f5bd5a4841ac","sequence":4,"stable_reason_code":"LIVE_PATH_VERIFIED","status":"PASS","version":"s3-bridge-v1"}},{"request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_PROMOTE","parent_hash":"03600714175da29a8ed7d59d0e06eb25683073c2202925e54d88df1b06be5b21","payload":{"hour":5,"scenario":"hour-05","synthetic_hash":"89546272b2322cd9195f245b2738d310c0dff0741cffb00015d4c53dba20cd69"},"request_hash":"b76772748e6b88e519a390a063d95050bbddc34645d55e12b552ace2ac86381d","sequence":5,"version":"s3-bridge-v1"},"result":{"campaign_id":"ck-s3-20260727-release-r1","cloud_metrics":{"changefeed_ms":1014,"changefeed_rows":2,"cockroach_ms":2225,"cockroach_operations":9,"coordinator_backlog":0,"coordinator_ms":9725,"lambda_invocations":1,"lambda_ms":2012,"vector_ms":543},"evidence_hashes":{"changefeed":"df588c361b5c92f05e8e2f0801d6864cbeda5f98cdad3cf7be7ce83e52c58654","cleanup":"8b5cbe69a3c271017ecc47cca7bf43f09ef6afb70c11efdf606ea63f82967c7c","lambda":"be12a1039b4be74d1f71f6bb72f7dd5f8fb1116d510f4d8fa6f2280da17e9d22","mcp_audit":"dc85c258302a0ca1f0d819f5fb1bbc3de0baea038391c0b6bbee2bd40758fa1f","transaction":"c5372d5c5fd3703e2580635a0df31b6f6ed9c72e65b7270aefc6d53b3b7548f5","vector":"1e1eb3263284c2e21f0c25636fac0ff47b839fbf936fa412ddcfbb2463eeb245","verifier":"4b66bed4b7e4746175b205511cc39c29e26e4da1257da553a5106a8b1a2ec362"},"operation":"RUN_PROMOTE","request_hash":"b76772748e6b88e519a390a063d95050bbddc34645d55e12b552ace2ac86381d","result_hash":"4a6b28f127772335bef4afa20ddf17cf6759d5684504d23bf706a1ebf3baf248","sequence":5,"stable_reason_code":"LIVE_PATH_VERIFIED","status":"PASS","version":"s3-bridge-v1"}},{"request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_REFUSE","parent_hash":"b76772748e6b88e519a390a063d95050bbddc34645d55e12b552ace2ac86381d","payload":{"hour":6,"scenario":"hour-06","synthetic_hash":"d6384d26e8f8b144fc2dd474b23308c085fb56555dffb94c1332efa8c9cc8713"},"request_hash":"efae291ddebf8ac1a3b805c1df32cdfb45c564d5e922c69142111e6699ae91b4","sequence":6,"version":"s3-bridge-v1"},"result":{"campaign_id":"ck-s3-20260727-release-r1","cloud_metrics":{"changefeed_ms":1167,"changefeed_rows":2,"cockroach_ms":2399,"cockroach_operations":9,"coordinator_backlog":0,"coordinator_ms":9009,"lambda_invocations":1,"lambda_ms":1486,"vector_ms":538},"evidence_hashes":{"changefeed":"edf5264c8a773b6801367fb65750642264d03e4070e85e9a2fa14e9e4947deae","cleanup":"8b5cbe69a3c271017ecc47cca7bf43f09ef6afb70c11efdf606ea63f82967c7c","lambda":"01f89a85e9c8730a5dcefc53a9bd3952f9894a00759e833f7cf2652ad42c21bf","mcp_audit":"9056fe406417b8ff2d5880cb9eb24a1acdda1054a350f77b30596c16eeccc330","transaction":"c5372d5c5fd3703e2580635a0df31b6f6ed9c72e65b7270aefc6d53b3b7548f5","vector":"8734924e7643cc0475db3745503650b4b7b8976598805f255269fc63c1633c30","verifier":"3f165b8147fa3fca24519670bb4f7cb47880c69bc96a135a2f95c9957f3e05f0"},"operation":"RUN_REFUSE","request_hash":"efae291ddebf8ac1a3b805c1df32cdfb45c564d5e922c69142111e6699ae91b4","result_hash":"c1c568a568bcaae3c7ea2eb511e5e66c265926f3f28f64b0b86f4be50197092c","sequence":6,"stable_reason_code":"LIVE_PATH_VERIFIED","status":"PASS","version":"s3-bridge-v1"}},{"request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_PROMOTE","parent_hash":"efae291ddebf8ac1a3b805c1df32cdfb45c564d5e922c69142111e6699ae91b4","payload":{"hour":7,"scenario":"hour-07","synthetic_hash":"091154f2a507de68152b706b2b5b581a88bd0c223bf390a539136260e4c370c5"},"request_hash":"6933fb5325161de55f259a18befe628d0bc9406be46dc4c14e601fd4c6979ad6","sequence":7,"version":"s3-bridge-v1"},"result":{"campaign_id":"ck-s3-20260727-release-r1","cloud_metrics":{"changefeed_ms":1012,"changefeed_rows":2,"cockroach_ms":2343,"cockroach_operations":9,"coordinator_backlog":0,"coordinator_ms":10229,"lambda_invocations":1,"lambda_ms":2132,"vector_ms":627},"evidence_hashes":{"changefeed":"df588c361b5c92f05e8e2f0801d6864cbeda5f98cdad3cf7be7ce83e52c58654","cleanup":"8b5cbe69a3c271017ecc47cca7bf43f09ef6afb70c11efdf606ea63f82967c7c","lambda":"77cdd2316c9336f3a87c37da2240edcc865e054770d65a640bd68b0ea11fdf3b","mcp_audit":"dc85c258302a0ca1f0d819f5fb1bbc3de0baea038391c0b6bbee2bd40758fa1f","transaction":"c5372d5c5fd3703e2580635a0df31b6f6ed9c72e65b7270aefc6d53b3b7548f5","vector":"1e1eb3263284c2e21f0c25636fac0ff47b839fbf936fa412ddcfbb2463eeb245","verifier":"4b66bed4b7e4746175b205511cc39c29e26e4da1257da553a5106a8b1a2ec362"},"operation":"RUN_PROMOTE","request_hash":"6933fb5325161de55f259a18befe628d0bc9406be46dc4c14e601fd4c6979ad6","result_hash":"369a74a97be66b3de827e96317d485c3867c17516fabe5a6024d95f672732917","sequence":7,"stable_reason_code":"LIVE_PATH_VERIFIED","status":"PASS","version":"s3-bridge-v1"}},{"request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_REFUSE","parent_hash":"6933fb5325161de55f259a18befe628d0bc9406be46dc4c14e601fd4c6979ad6","payload":{"hour":8,"scenario":"hour-08","synthetic_hash":"03861537a21a2b0a0681c586d00cd9e94799dd0ed5156bbc442f24c6c3c89f5e"},"request_hash":"179edbf514d656662affbbe47870b58bbb0e5775f032c414aa2343809eba286a","sequence":8,"version":"s3-bridge-v1"},"result":{"campaign_id":"ck-s3-20260727-release-r1","cloud_metrics":{"changefeed_ms":966,"changefeed_rows":2,"cockroach_ms":2219,"cockroach_operations":9,"coordinator_backlog":0,"coordinator_ms":8991,"lambda_invocations":1,"lambda_ms":1831,"vector_ms":553},"evidence_hashes":{"changefeed":"edf5264c8a773b6801367fb65750642264d03e4070e85e9a2fa14e9e4947deae","cleanup":"8b5cbe69a3c271017ecc47cca7bf43f09ef6afb70c11efdf606ea63f82967c7c","lambda":"af289ac11cdc43cb4f03dc944650a821e10191adb33f6771b0b054d60fdd3261","mcp_audit":"9056fe406417b8ff2d5880cb9eb24a1acdda1054a350f77b30596c16eeccc330","transaction":"c5372d5c5fd3703e2580635a0df31b6f6ed9c72e65b7270aefc6d53b3b7548f5","vector":"8734924e7643cc0475db3745503650b4b7b8976598805f255269fc63c1633c30","verifier":"3f165b8147fa3fca24519670bb4f7cb47880c69bc96a135a2f95c9957f3e05f0"},"operation":"RUN_REFUSE","request_hash":"179edbf514d656662affbbe47870b58bbb0e5775f032c414aa2343809eba286a","result_hash":"5297fada29e86d80721ca989a39a0f558e3c3c95371c505757538bd246d50200","sequence":8,"stable_reason_code":"LIVE_PATH_VERIFIED","status":"PASS","version":"s3-bridge-v1"}},{"request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_PROMOTE","parent_hash":"179edbf514d656662affbbe47870b58bbb0e5775f032c414aa2343809eba286a","payload":{"hour":9,"scenario":"hour-09","synthetic_hash":"9fc97e12fe6ea831590a6c992bdf17a458e230ee21285397a78ae2eb1bba44a7"},"request_hash":"a30c025e734b2219c7a5e453abd8e693d0dab4f38b04f87d41d1a7c46d4bb143","sequence":9,"version":"s3-bridge-v1"},"result":{"campaign_id":"ck-s3-20260727-release-r1","cloud_metrics":{"changefeed_ms":934,"changefeed_rows":2,"cockroach_ms":2230,"cockroach_operations":9,"coordinator_backlog":0,"coordinator_ms":9066,"lambda_invocations":1,"lambda_ms":2140,"vector_ms":527},"evidence_hashes":{"changefeed":"df588c361b5c92f05e8e2f0801d6864cbeda5f98cdad3cf7be7ce83e52c58654","cleanup":"8b5cbe69a3c271017ecc47cca7bf43f09ef6afb70c11efdf606ea63f82967c7c","lambda":"5ba50390e2002f642b3a6c051d4df41bff0595c4591c1c63fcc0c3e36fdcaa0e","mcp_audit":"dc85c258302a0ca1f0d819f5fb1bbc3de0baea038391c0b6bbee2bd40758fa1f","transaction":"c5372d5c5fd3703e2580635a0df31b6f6ed9c72e65b7270aefc6d53b3b7548f5","vector":"1e1eb3263284c2e21f0c25636fac0ff47b839fbf936fa412ddcfbb2463eeb245","verifier":"4b66bed4b7e4746175b205511cc39c29e26e4da1257da553a5106a8b1a2ec362"},"operation":"RUN_PROMOTE","request_hash":"a30c025e734b2219c7a5e453abd8e693d0dab4f38b04f87d41d1a7c46d4bb143","result_hash":"a2870da7448804ec0e63a90d059924d3711378c616cc6519659d918b83234fa2","sequence":9,"stable_reason_code":"LIVE_PATH_VERIFIED","status":"PASS","version":"s3-bridge-v1"}},{"request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_REFUSE","parent_hash":"a30c025e734b2219c7a5e453abd8e693d0dab4f38b04f87d41d1a7c46d4bb143","payload":{"hour":10,"scenario":"hour-10","synthetic_hash":"3dc5012cf57f35479adfd14b87f4f5a4646621b2b99800cc492eb4d0c74ef084"},"request_hash":"250437f46194d9b49197ab2032b4d52c69efea9846c49e3c6d0a7db4c1265a3d","sequence":10,"version":"s3-bridge-v1"},"result":{"campaign_id":"ck-s3-20260727-release-r1","cloud_metrics":{"changefeed_ms":942,"changefeed_rows":2,"cockroach_ms":2248,"cockroach_operations":9,"coordinator_backlog":0,"coordinator_ms":9479,"lambda_invocations":1,"lambda_ms":2588,"vector_ms":543},"evidence_hashes":{"changefeed":"edf5264c8a773b6801367fb65750642264d03e4070e85e9a2fa14e9e4947deae","cleanup":"8b5cbe69a3c271017ecc47cca7bf43f09ef6afb70c11efdf606ea63f82967c7c","lambda":"40725699f0e5a6f6febab626bd64058c2b9724f3ac78449a5433fffdad4f6815","mcp_audit":"9056fe406417b8ff2d5880cb9eb24a1acdda1054a350f77b30596c16eeccc330","transaction":"c5372d5c5fd3703e2580635a0df31b6f6ed9c72e65b7270aefc6d53b3b7548f5","vector":"8734924e7643cc0475db3745503650b4b7b8976598805f255269fc63c1633c30","verifier":"3f165b8147fa3fca24519670bb4f7cb47880c69bc96a135a2f95c9957f3e05f0"},"operation":"RUN_REFUSE","request_hash":"250437f46194d9b49197ab2032b4d52c69efea9846c49e3c6d0a7db4c1265a3d","result_hash":"713fc18b393aa672ead92ce98370e5ed8e74ed61140e1a94fec0cfdbc445ec31","sequence":10,"stable_reason_code":"LIVE_PATH_VERIFIED","status":"PASS","version":"s3-bridge-v1"}},{"request":{"campaign_id":"ck-s3-20260727-release-r1","operation":"RUN_PROMOTE","parent_hash":"250437f46194d9b49197ab2032b4d52c69efea9846c49e3c6d0a7db4c1265a3d","payload":{"hour":11,"scenario":"hour-11","synthetic_hash":"68e2d791c0f1a79e255f522cdb66a3d6374ba468920ecd7efcc4a13a1d237d3b"},"request_hash":"1a095b051abb14a8c4ecb5066e4622ba4269f4b028e185c9f4fd6c3de229340e","sequence":11,"version":"s3-bridge-v1"},"result":{"campaign_id":"ck-s3-20260727-release-r1","cloud_metrics":{"changefeed_ms":932,"changefeed_rows":2,"cockroach_ms":2149,"cockroach_operations":9,"coordinator_backlog":0,"coordinator_ms":7897,"lambda_invocations":1,"lambda_ms":1273,"vector_ms":518},"evidence_hashes":{"changefeed":"df588c361b5c92f05e8e2f0801d6864cbeda5f98cdad3cf7be7ce83e52c58654","cleanup":"8b5cbe69a3c271017ecc47cca7bf43f09ef6afb70c11efdf606ea63f82967c7c","lambda":"7a4d0e97379dd50ae054d366c628585284695ba230eb06a3a79458e40db217e2","mcp_audit":"dc85c258302a0ca1f0d819f5fb1bbc3de0baea038391c0b6bbee2bd40758fa1f","transaction":"c5372d5c5fd3703e2580635a0df31b6f6ed9c72e65b7270aefc6d53b3b7548f5","vector":"1e1eb3263284c2e21f0c25636fac0ff47b839fbf936fa412ddcfbb2463eeb245","verifier":"4b66bed4b7e4746175b205511cc39c29e26e4da1257da553a5106a8b1a2ec362"},"operation":"RUN_PROMOTE","request_hash":"1a095b051abb14a8c4ecb5066e4622ba4269f4b028e185c9f4fd6c3de229340e","result_hash":"5bb6735607bef50d16c59e0079fd7be66edab0f329e33aae548f92b2980f0173","sequence":11,"stable_reason_code":"LIVE_PATH_VERIFIED","status":"PASS","version":"s3-bridge-v1"}}],"source":"S3_ATTEMPT_A04_EXCHANGES_1_THROUGH_11","version":"s3-preserved-pairs-v1"}
diff --git a/hardening-gate5/heldout_contract.py b/hardening-gate5/heldout_contract.py
new file mode 100644
index 0000000..4ff17ca
--- /dev/null
+++ b/hardening-gate5/heldout_contract.py
@@ -0,0 +1,118 @@
+#!/usr/bin/env python3
+"""Frozen post-candidate held-out vector generator contract for Gate 7.
+
+The implementation is frozen at Gate 5. The 32-byte campaign salt is created
+only after the candidate commit is immutable and is never exposed to a builder
+before freeze. Public evidence records the salt hash, not the salt bytes.
+"""
+from __future__ import annotations
+
+import argparse
+import hashlib
+import json
+from pathlib import Path
+import re
+from typing import Any
+
+
+CLASSES = (
+    "tampered-receipt", "replayed-warrant", "malformed-record",
+    "unsupported-value", "quarantined-candidate", "incomplete-evidence",
+    "interrupted-consumption",
+)
+HEX_COMMIT = re.compile(r"^[0-9a-f]{40,64}$")
+
+
+def canonical(value: Any) -> bytes:
+    return json.dumps(value, sort_keys=True, separators=(",", ":"),
+                      allow_nan=False).encode("utf-8")
+
+
+def digest(value: bytes | Any) -> str:
+    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()
+
+
+def derive(candidate_commit: str, salt: bytes, vector_class: str,
+           variant: int) -> dict[str, Any]:
+    if not HEX_COMMIT.fullmatch(candidate_commit):
+        raise ValueError("CANDIDATE_COMMIT_INVALID")
+    if len(salt) != 32 or vector_class not in CLASSES or variant not in {1, 2, 3}:
+        raise ValueError("HELDOUT_KEY_INVALID")
+    seed_hash = digest(salt + candidate_commit.encode() +
+                       vector_class.encode() + bytes([variant]))
+    base = {
+        "version": "p4-v1", "candidate_id": f"heldout-{seed_hash[:24]}",
+        "source_receipt_hash": digest({"seed": seed_hash, "source": "heldout"}),
+        "payload": {"op": "continue", "sequence": variant, "nonce": seed_hash[24:40]},
+        "schema_version": "p4-v1", "provenance": {"source": "gate7-heldout"},
+        "supported": True, "one_use_state": "ISSUED", "quarantined": False,
+        "policy_veto": False, "requested_paths": ["app/state.json"],
+        "declared_paths": ["app/state.json"],
+    }
+    base["payload_hash"] = digest(base["payload"])
+    expected = ("REFUSE", "UNSPECIFIED")
+    if vector_class == "tampered-receipt":
+        base["payload_hash"] = "0" * 64
+        expected = ("REFUSE", "HASH_MISMATCH")
+    elif vector_class == "replayed-warrant":
+        base["one_use_state"] = "CONSUMED"
+        expected = ("REFUSE", "REPLAYED_TICKET")
+    elif vector_class == "malformed-record":
+        base["unexpected"] = seed_hash
+        expected = ("INVALID", "UNKNOWN_FIELD")
+    elif vector_class == "unsupported-value":
+        base["schema_version"] = "p4-heldout-unsupported"
+        expected = ("REFUSE", "UNSUPPORTED_SCHEMA")
+    elif vector_class == "quarantined-candidate":
+        base["quarantined"] = True
+        expected = ("REFUSE", "QUARANTINED_INPUT")
+    elif vector_class == "incomplete-evidence":
+        del base["source_receipt_hash"]
+        expected = ("INVALID", "MISSING_FIELD")
+    elif vector_class == "interrupted-consumption":
+        base["payload"]["fault"] = "interrupt-after-consume"
+        base["payload_hash"] = digest(base["payload"])
+        expected = ("REFUSE", "RECOVERY_INTERRUPTED_FAIL_CLOSED")
+    vector = {
+        "version": "gate7-heldout-vector-v1",
+        "class": vector_class,
+        "variant": variant,
+        "seed_hash": seed_hash,
+        "input": base,
+        "expected_verdict": expected[0],
+        "expected_reason": expected[1],
+        "mutation_allowed": False,
+    }
+    vector["vector_hash"] = digest(vector)
+    return vector
+
+
+def known_preflight_vectors() -> list[dict[str, Any]]:
+    salt = bytes.fromhex("42" * 32)
+    commit = "1" * 40
+    return [derive(commit, salt, "tampered-receipt", 1),
+            derive(commit, salt, "replayed-warrant", 1)]
+
+
+def main() -> int:
+    parser = argparse.ArgumentParser()
+    parser.add_argument("--candidate-commit", required=True)
+    parser.add_argument("--salt-file", type=Path, required=True)
+    parser.add_argument("--output", type=Path, required=True)
+    args = parser.parse_args()
+    salt = args.salt_file.read_bytes()
+    vectors = [derive(args.candidate_commit, salt, name, variant)
+               for name in CLASSES for variant in (1, 2, 3)]
+    payload = {
+        "version": "gate7-heldout-set-v1",
+        "candidate_commit": args.candidate_commit,
+        "salt_sha256": digest(salt),
+        "vectors": vectors,
+    }
+    payload["set_hash"] = digest(payload)
+    args.output.write_bytes(canonical(payload))
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/hardening-gate5/run_smoke.py b/hardening-gate5/run_smoke.py
new file mode 100644
index 0000000..3cf2e85
--- /dev/null
+++ b/hardening-gate5/run_smoke.py
@@ -0,0 +1,167 @@
+#!/usr/bin/env python3
+"""Run the Gate 5 local paired smoke in fresh processes with network denied."""
+from __future__ import annotations
+
+import argparse
+import json
+import os
+from pathlib import Path
+import platform
+import shutil
+import subprocess
+import sys
+
+import comparative
+
+
+DARWIN_PROFILE = "(version 1)(allow default)(deny network*)"
+
+
+def guarded(command: list[str]) -> list[str]:
+    system = platform.system()
+    if system == "Darwin":
+        sandbox = Path("/usr/bin/sandbox-exec")
+        if not sandbox.is_file():
+            raise RuntimeError("NETWORK_DENY_RUNTIME_MISSING")
+        return [str(sandbox), "-p", DARWIN_PROFILE, *command]
+    if system == "Linux":
+        unshare = shutil.which("unshare")
+        if unshare is None:
+            raise RuntimeError("NETWORK_DENY_RUNTIME_MISSING")
+        return [unshare, "--user", "--map-root-user", "--net", "--mount-proc", *command]
+    raise RuntimeError("NETWORK_DENY_PLATFORM_UNSUPPORTED")
+
+
+def network_deny_proof() -> dict[str, object]:
+    probe = [sys.executable, "-c", (
+        "import socket,sys\n"
+        "s=socket.socket()\n"
+        "try:\n s.connect(('1.1.1.1',53))\n"
+        "except OSError:\n sys.exit(0)\n"
+        "sys.exit(91)\n"
+    )]
+    result = subprocess.run(guarded(probe), stdout=subprocess.PIPE,
+                            stderr=subprocess.STDOUT, check=False, timeout=20)
+    if result.returncode != 0:
+        raise RuntimeError("NETWORK_DENY_PROOF_FAILED")
+    return {
+        "platform": platform.system(),
+        "guard_prefix": guarded(["COMMAND"])[:-1],
+        "forbidden_egress_result": "BLOCKED",
+        "probe_output_sha256": comparative.digest(result.stdout),
+    }
+
+
+def main() -> int:
+    parser = argparse.ArgumentParser()
+    parser.add_argument("output_root", type=Path)
+    args = parser.parse_args()
+    output = args.output_root.resolve()
+    output.mkdir(parents=True, exist_ok=False)
+    restic = shutil.which("restic")
+    if restic is None:
+        raise RuntimeError("RESTIC_BINARY_NOT_FOUND")
+    child_env = dict(os.environ, CK_GATE5_RESTIC=str(Path(restic).resolve()))
+    proof = network_deny_proof()
+    receipts = []
+    script = Path(__file__).with_name("comparative.py")
+    for scenario_index, scenario in enumerate(comparative.SCENARIO_CLASSES):
+        methods = list(comparative.METHODS)
+        rotation = scenario_index % len(methods)
+        methods = methods[rotation:] + methods[:rotation]
+        for execution_order, method in enumerate(methods, 1):
+            destination = output / f"{scenario}--{method}.json"
+            command = guarded([
+                sys.executable, str(script), scenario, "1", method, str(destination),
+                "--execution-order", str(execution_order),
+            ])
+            result = subprocess.run(command, cwd=comparative.BASE,
+                                    env=child_env,
+                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
+                                    check=False, timeout=240)
+            if result.returncode != 0:
+                raise RuntimeError(
+                    f"SMOKE_EXECUTION_FAILED:{scenario}:{method}:"
+                    f"{comparative.digest(result.stdout)}")
+            receipt = json.loads(destination.read_bytes())
+            comparative.validate_receipt(receipt, destination.read_bytes())
+            if not receipt["cleanup_pass"]:
+                raise RuntimeError("SMOKE_CLEANUP_FAILED")
+            receipts.append(receipt)
+
+    # Repeat one representative class for each method in new processes. Only
+    # frozen semantic fields are compared; native timestamps/storage differ.
+    deterministic = []
+    probes = (
+        ("committed-plus-uncommitted", "ordinary-git"),
+        ("complete-loss", "git-plus-restic-0.19.0"),
+        ("conflicting-stale", "product"),
+    )
+    first = {(item["scenario_class"], item["method"]): item for item in receipts}
+    for scenario in comparative.SCENARIO_CLASSES:
+        paired = [item for item in receipts if item["scenario_class"] == scenario]
+        if len({item["source_manifest_sha256"] for item in paired}) != 1:
+            raise RuntimeError("PAIR_SOURCE_HASH_MISMATCH")
+        if len({item["event_stream_sha256"] for item in paired}) != 1:
+            raise RuntimeError("PAIR_EVENT_HASH_MISMATCH")
+        if len({item["loss_receipt_sha256"] for item in paired}) != 1:
+            raise RuntimeError("PAIR_LOSS_HASH_MISMATCH")
+    for scenario, method in probes:
+        destination = output / f"determinism--{scenario}--{method}.json"
+        result = subprocess.run(guarded([
+            sys.executable, str(script), scenario, "1", method, str(destination)
+        ]), cwd=comparative.BASE, env=child_env,
+            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
+            check=False, timeout=240)
+        if result.returncode != 0:
+            raise RuntimeError("DETERMINISM_EXECUTION_FAILED")
+        repeat = json.loads(destination.read_bytes())
+        comparative.validate_receipt(repeat, destination.read_bytes())
+        original = first[(scenario, method)]
+        if repeat["deterministic_outcome"] != original["deterministic_outcome"]:
+            raise RuntimeError("SEMANTIC_DETERMINISM_FAILED")
+        deterministic.append({
+            "scenario": scenario, "method": method,
+            "semantic_sha256": comparative.digest(repeat["deterministic_outcome"]),
+            "status": "PASS",
+        })
+
+    # Generator/scorer inputs must reproduce for every frozen seed.
+    generator_hashes = []
+    for scenario in comparative.SCENARIO_CLASSES:
+        for repetition in (1, 2, 3):
+            one = comparative.generate_scenario(scenario, repetition)
+            two = comparative.generate_scenario(scenario, repetition)
+            if comparative.canonical(one) != comparative.canonical(two):
+                raise RuntimeError("GENERATOR_NONDETERMINISTIC")
+            generator_hashes.append({
+                "scenario": scenario,
+                "repetition": repetition,
+                "source_bundle_hash": one["source_bundle_hash"],
+                "expected_manifest_hash": one["expected_manifest_hash"],
+            })
+    leaked_roots = [path.name for path in output.parent.glob("gate5-trial-*")]
+    if leaked_roots:
+        raise RuntimeError("TRIAL_RESIDUE_DETECTED")
+    summary = {
+        "version": "gate5-local-smoke-v1",
+        "status": "GREEN",
+        "measured_campaign": False,
+        "executions": len(receipts),
+        "classes": list(comparative.SCENARIO_CLASSES),
+        "methods": list(comparative.METHODS),
+        "network_deny_proof": proof,
+        "semantic_determinism": deterministic,
+        "generator_hashes": generator_hashes,
+        "receipt_hashes": sorted(item["receipt_sha256"] for item in receipts),
+        "trial_residue": [],
+    }
+    summary["summary_sha256"] = comparative.digest(summary)
+    comparative.atomic_write(output / "summary.json", summary)
+    print(comparative.canonical({"status": "GREEN",
+                                 "summary_sha256": summary["summary_sha256"]}).decode())
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/hardening-gate5/scenarios/clean-control.schema.json b/hardening-gate5/scenarios/clean-control.schema.json
new file mode 100644
index 0000000..57fa248
--- /dev/null
+++ b/hardening-gate5/scenarios/clean-control.schema.json
@@ -0,0 +1 @@
+{"class":"clean-control","loss":"NONE","required_constructs":["healthy-workspace-byte-identical","no-destructive-change","no-action-or-separate-successor","common-test-pass"],"version":"gate5-scenario-class-v1"}
diff --git a/hardening-gate5/scenarios/committed-only.schema.json b/hardening-gate5/scenarios/committed-only.schema.json
new file mode 100644
index 0000000..4a47d44
--- /dev/null
+++ b/hardening-gate5/scenarios/committed-only.schema.json
@@ -0,0 +1 @@
+{"class":"committed-only","loss":"COMPLETE","required_constructs":["all-required-units-committed","all-commits-pushed","unique-committed-continuation"],"version":"gate5-scenario-class-v1"}
diff --git a/hardening-gate5/scenarios/committed-plus-uncommitted.schema.json b/hardening-gate5/scenarios/committed-plus-uncommitted.schema.json
new file mode 100644
index 0000000..42d4041
--- /dev/null
+++ b/hardening-gate5/scenarios/committed-plus-uncommitted.schema.json
@@ -0,0 +1 @@
+{"class":"committed-plus-uncommitted","loss":"COMPLETE","required_constructs":["base-committed","required-tracked-edit-uncommitted","required-untracked-file","final-checkpoint-complete"],"version":"gate5-scenario-class-v1"}
diff --git a/hardening-gate5/scenarios/complete-loss.schema.json b/hardening-gate5/scenarios/complete-loss.schema.json
new file mode 100644
index 0000000..fa95b21
--- /dev/null
+++ b/hardening-gate5/scenarios/complete-loss.schema.json
@@ -0,0 +1 @@
+{"class":"complete-loss","loss":"COMPLETE","required_constructs":["multiple-dependent-saved-edits","local-git-metadata-lost","external-custody-survives","last-safe-checkpoint-unique"],"version":"gate5-scenario-class-v1"}
diff --git a/hardening-gate5/scenarios/conflicting-stale.schema.json b/hardening-gate5/scenarios/conflicting-stale.schema.json
new file mode 100644
index 0000000..9bb25fd
--- /dev/null
+++ b/hardening-gate5/scenarios/conflicting-stale.schema.json
@@ -0,0 +1 @@
+{"class":"conflicting-stale","loss":"COMPLETE","required_constructs":["newer-candidate-policy-veto","older-safe-executable-candidate","conventional-selection-rule-disclosed","product-verifier-authority"],"version":"gate5-scenario-class-v1"}
diff --git a/hardening-gate5/scenarios/partial-loss.schema.json b/hardening-gate5/scenarios/partial-loss.schema.json
new file mode 100644
index 0000000..18e5270
--- /dev/null
+++ b/hardening-gate5/scenarios/partial-loss.schema.json
@@ -0,0 +1 @@
+{"class":"partial-loss","loss":"PARTIAL","required_constructs":["declared-path-subset-lost","original-workspace-sealed","fresh-successor-required","last-safe-checkpoint-unique"],"version":"gate5-scenario-class-v1"}
diff --git a/hardening-gate5/scenarios/seeds.json b/hardening-gate5/scenarios/seeds.json
new file mode 100644
index 0000000..d30c19e
--- /dev/null
+++ b/hardening-gate5/scenarios/seeds.json
@@ -0,0 +1 @@
+{"classes":["committed-only","committed-plus-uncommitted","complete-loss","partial-loss","conflicting-stale","clean-control"],"derivation":"SHA256(canonical({version:gate5-seed-v1,class:<class>,repetition:<1|2|3>}))","repetitions":[1,2,3],"version":"gate5-seeds-v1"}
diff --git a/hardening-gate5/test_comparative.py b/hardening-gate5/test_comparative.py
new file mode 100644
index 0000000..14dcab7
--- /dev/null
+++ b/hardening-gate5/test_comparative.py
@@ -0,0 +1,84 @@
+#!/usr/bin/env python3
+from __future__ import annotations
+
+import importlib.util
+import os
+from pathlib import Path
+import shutil
+import tempfile
+import unittest
+
+import comparative
+import heldout_contract
+
+
+class ComparativeContractTests(unittest.TestCase):
+    def test_all_eighteen_scenario_seeds_are_reproducible(self):
+        hashes = set()
+        for scenario in comparative.SCENARIO_CLASSES:
+            for repetition in (1, 2, 3):
+                first = comparative.generate_scenario(scenario, repetition)
+                second = comparative.generate_scenario(scenario, repetition)
+                self.assertEqual(comparative.canonical(first), comparative.canonical(second))
+                hashes.add(first["source_bundle_hash"])
+        self.assertEqual(len(hashes), 18)
+
+    def test_isolated_environment_drops_cloud_and_credential_state(self):
+        with tempfile.TemporaryDirectory(prefix="gate5-env-") as temporary:
+            root = Path(temporary)
+            env = comparative.isolated_env(root)
+            self.assertEqual(set(env), {
+                "HOME", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL",
+                "GIT_TERMINAL_PROMPT", "LANG", "LC_ALL", "TZ", "PATH",
+                "NO_PROXY", "no_proxy",
+            })
+            for forbidden in ("AWS_PROFILE", "AWS_ACCESS_KEY_ID", "PGPASSWORD",
+                              "SSH_AUTH_SOCK", "HTTP_PROXY", "HTTPS_PROXY"):
+                self.assertNotIn(forbidden, env)
+            self.assertEqual(Path(env["HOME"]).parent, root)
+
+    def test_product_authority_source_and_pass_refuse_semantics_are_unchanged(self):
+        path = comparative.BASE / "p4-verifier/verifier.py"
+        self.assertEqual(
+            comparative.digest(path.read_bytes()),
+            "a7ee1fc513da7d4f0633bfabdd4e5f3ee4947b829b292416d6aad7d87d767c40",
+        )
+        verifier = comparative.load_verifier()
+        payload = {"checkpoint": "FINAL_PRELOSS", "manifest": {}}
+        base = {
+            "version": "p4-v1", "candidate_id": "gate5-proof",
+            "source_receipt_hash": "a" * 64, "payload": payload,
+            "payload_hash": verifier.digest(payload), "schema_version": "p4-v1",
+            "provenance": {"source": "gate5-test"}, "supported": True,
+            "one_use_state": "ISSUED", "quarantined": False,
+            "policy_veto": False, "requested_paths": [], "declared_paths": [],
+        }
+        self.assertEqual([verifier.verify(base) for _ in range(5)],
+                         [("PROMOTE", "VERIFIED")] * 5)
+        refused = dict(base, policy_veto=True)
+        self.assertEqual([verifier.verify(refused) for _ in range(5)],
+                         [("REFUSE", "POLICY_VETO")] * 5)
+
+    def test_frozen_binary_provenance_matches_local_tools(self):
+        git = Path("/usr/bin/git")
+        restic_path = shutil.which("restic")
+        self.assertIsNotNone(restic_path)
+        restic = Path(restic_path or "")
+        self.assertEqual(comparative.digest(git.read_bytes()),
+                         "179301dcb41ea78accc3fa0048a7e6f6710d891945a751a34addd622020c1818")
+        self.assertEqual(comparative.digest(restic.read_bytes()),
+                         "f6c965a0f7f59464614130d79246479d48e2aa6780c34d27df6e48c8ee0308bd")
+
+    def test_heldout_contract_has_two_known_and_twenty_one_postfreeze_vectors(self):
+        known = heldout_contract.known_preflight_vectors()
+        self.assertEqual(len(known), 2)
+        self.assertEqual(len({item["vector_hash"] for item in known}), 2)
+        salt = bytes.fromhex("7e" * 32)
+        vectors = [heldout_contract.derive("2" * 40, salt, name, variant)
+                   for name in heldout_contract.CLASSES for variant in (1, 2, 3)]
+        self.assertEqual(len(vectors), 21)
+        self.assertEqual(len({item["vector_hash"] for item in vectors}), 21)
+
+
+if __name__ == "__main__":
+    unittest.main()
diff --git a/s3-soak/cloud_adapter.py b/s3-soak/cloud_adapter.py
index a3949c6..3346739 100644
--- a/s3-soak/cloud_adapter.py
+++ b/s3-soak/cloud_adapter.py
@@ -12,7 +12,6 @@ import json
 import os
 from pathlib import Path
 import re
-import shutil
 import subprocess
 import sys
 import tempfile
@@ -21,6 +20,7 @@ from typing import Any
 from urllib.parse import quote
 
 import protocol
+import hardening
 
 BASE = Path(__file__).resolve().parents[1]
 P9 = BASE / "p9-cloud"
@@ -45,14 +45,15 @@ def _load_live_completion():
     return module
 
 
-def _run(command: list[str], *, env: dict[str, str] | None = None,
+def _run(command: list[str], *, family: str,
+         env: dict[str, str] | None = None,
          timeout: int = 60) -> tuple[bytes, int]:
     started = time.monotonic_ns()
     result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             env=env, timeout=timeout, check=False)
     elapsed_ms = int((time.monotonic_ns() - started) / 1_000_000)
     if result.returncode != 0:
-        raise CloudAdapterError("COMMAND_FAILED:" + protocol.sha256(result.stdout))
+        raise hardening.command_failure(family, result.returncode, result.stdout)
     return result.stdout, elapsed_ms
 
 
@@ -113,7 +114,7 @@ def _sql(config: dict[str, Any], env: dict[str, str], *, execute: str | None = N
         command.extend(["--execute", execute])
     else:
         command.extend(["--file", str(file.resolve())])
-    return _run(command, env=env, timeout=timeout)
+    return _run(command, family="cockroach", env=env, timeout=timeout)
 
 
 def _cleanup_sql(task_id: str) -> str:
@@ -143,7 +144,7 @@ def _aws_invoke(config: dict[str, Any], request_path: Path,
         "--profile", config["aws_profile"],
         "--region", config["aws_region"], "--output", "json", "--no-cli-pager",
         str(response_path.resolve()),
-    ], env=aws_env, timeout=30)
+    ], family="aws", env=aws_env, timeout=30)
     metadata = json.loads(raw)
     try:
         log_tail = base64.b64decode(metadata["LogResult"], validate=True).decode("utf-8")
@@ -171,35 +172,46 @@ def run_live(request: dict[str, Any], config_path: Path,
     trial_root = evidence_root / f"trial-{request['sequence']:04d}"
     if trial_root.exists():
         raise CloudAdapterError("TRIAL_ROOT_EXISTS")
-    secret = bytearray(_password(config))
+    secret = bytearray()
     sql_env: dict[str, str] | None = None
+    stage = "CREDENTIAL_ACQUISITION"
+    failure: BaseException | None = None
     try:
+        secret.extend(_password(config))
         sql_env = _sql_env(config, bytes(secret))
+        stage = "TRIAL_PREPARE"
         live.prepare(trial_root)
         prepared = json.loads((trial_root / f"{branch}-prepared.json").read_text())
         task_id = prepared["task_id"]
+        stage = "PRESEED_CLEANUP"
         _, cleanup_ms = _sql(config, sql_env, execute=_cleanup_sql(task_id))
+        stage = "COCKROACH_SEED"
         seed_raw, transaction_ms = _sql(
             config, sql_env, file=trial_root / f"{branch}-seed.sql")
+        stage = "COCKROACH_VECTOR_QUERY"
         vector_raw, vector_ms = _sql(
             config, sql_env, file=trial_root / f"{branch}-vector-query.sql")
         if prepared["vector_id"].encode() not in vector_raw:
             raise CloudAdapterError("VECTOR_LINKAGE_FAILED")
         lambda_request = trial_root / f"{branch}-request.json"
         lambda_response = trial_root / f"{branch}-lambda-response.json"
+        stage = "AWS_LAMBDA_INVOKE"
         meta, lambda_ms = _aws_invoke(config, lambda_request, lambda_response)
         response_value = json.loads(lambda_response.read_text(encoding="utf-8"))
         lambda_response.write_bytes(records.canonical_json(response_value) + b"\n")
         (trial_root / f"{branch}-lambda-meta.json").write_bytes(
             records.canonical_json(meta) + b"\n")
+        stage = "LOCAL_RECONCILIATION"
         reconciled, finalize_sql = live.reconcile_trial(trial_root, branch)
         finalize_path = trial_root / f"{branch}-finalize.sql"
         finalize_path.write_text(finalize_sql, encoding="utf-8")
+        stage = "COCKROACH_FINALIZE"
         _, finalize_ms = _sql(config, sql_env, file=finalize_path)
         feed_sql = (
             "EXPERIMENTAL CHANGEFEED FOR TABLE ck.worker_results "
             "WITH initial_scan='only', format='json'"
         )
+        stage = "COCKROACH_CHANGEFEED"
         feed_raw, changefeed_ms = _sql(
             config, sql_env, execute=feed_sql, timeout=30, fmt="ndjson")
         feed_path = trial_root / "changefeed.ndjson"
@@ -219,9 +231,11 @@ def run_live(request: dict[str, Any], config_path: Path,
             "SELECT task_id, receipt_hash, event_hash FROM ck.mcp_receipt_view "
             f"WHERE task_id='{task_id}' LIMIT 2"
         )
+        stage = "COCKROACH_AUDIT"
         audit_raw, audit_ms = _sql(config, sql_env, execute=audit_sql)
         if task_id.encode() not in audit_raw:
             raise CloudAdapterError("MCP_AUDIT_LINKAGE_FAILED")
+        stage = "POSTTRIAL_CLEANUP"
         _, cleanup2_ms = _sql(config, sql_env, execute=_cleanup_sql(task_id))
         verify_raw, verify_ms = _sql(
             config, sql_env,
@@ -265,12 +279,39 @@ def run_live(request: dict[str, Any], config_path: Path,
         summary["summary_hash"] = protocol.sha256(summary)
         (evidence_root / "summary.json").write_bytes(protocol.canonical(summary) + b"\n")
         return metrics, evidence_hashes
+    except BaseException as exc:
+        failure = exc
+        if isinstance(exc, hardening.ExternalCommandFailure):
+            classified = exc
+        else:
+            classified = hardening.ExternalCommandFailure(
+                command_family="internal",
+                return_code=-1,
+                output_hash=protocol.sha256(str(exc).encode("utf-8")),
+                failure_class=hardening.UNKNOWN_EXTERNAL_COMMAND,
+            )
+        receipt = hardening.failure_receipt(
+            campaign_id=request["campaign_id"],
+            sequence=request["sequence"],
+            stage=stage,
+            request_hash=request["request_hash"],
+            failure=classified,
+        )
+        # This fsynced receipt is outside the temporary trial and is committed
+        # before the finally block is allowed to remove trial-local evidence.
+        hardening.write_atomic(evidence_root / "failure.json", receipt)
+        raise CloudAdapterError(
+            f"STAGE_FAILED:{stage}:{classified.failure_class}"
+        ) from exc
     finally:
         if sql_env is not None:
             sql_env.pop("PGPASSWORD", None)
         for index in range(len(secret)):
             secret[index] = 0
-        shutil.rmtree(trial_root, ignore_errors=True)
+        cleanup = hardening.cleanup_trial_exact(trial_root, evidence_root)
+        hardening.write_atomic(evidence_root / "cleanup.json", cleanup)
+        if failure is not None and not (evidence_root / "failure.json").is_file():
+            raise CloudAdapterError("FAILURE_RECEIPT_MISSING")
 
 
 def run_fixture(request: dict[str, Any]) -> tuple[dict[str, int], dict[str, str]]:
diff --git a/s3-soak/coordinator_guard.py b/s3-soak/coordinator_guard.py
index 5a16f50..6f020ce 100644
--- a/s3-soak/coordinator_guard.py
+++ b/s3-soak/coordinator_guard.py
@@ -7,12 +7,12 @@ import hashlib
 import json
 import os
 from pathlib import Path
-import signal
 import subprocess
 import time
 from typing import Any
 
 import protocol
+import hardening
 
 
 class GuardFailure(RuntimeError):
@@ -256,10 +256,19 @@ def main() -> int:
             time.sleep(args.heartbeat_seconds)
         raise GuardFailure("GUARD_DEADLINE")
     except Exception as exc:
+        shutdown_receipt: dict[str, Any] | None = None
         try:
-            os.kill(args.coordinator_pid, signal.SIGTERM)
-        except ProcessLookupError:
-            pass
+            shutdown_receipt = hardening.coordinated_local_shutdown([
+                ("bridge", args.bridge_pid),
+                ("coordinator", args.coordinator_pid),
+            ])
+        except Exception as shutdown_exc:
+            # Preserve the primary failure and still proceed to exact worker
+            # teardown. The shutdown failure is hash-bound, never hidden.
+            log.emit("LOCAL_SHUTDOWN_BLOCKED", {
+                "type": type(shutdown_exc).__name__,
+                "reason_hash": protocol.sha256(str(shutdown_exc).encode()),
+            })
         marker = args.stop_marker.resolve()
         marker.parent.mkdir(parents=True, exist_ok=True)
         marker.write_bytes(protocol.canonical({
@@ -270,6 +279,10 @@ def main() -> int:
             "type": type(exc).__name__,
             "reason_hash": protocol.sha256(str(exc).encode()),
             "stop_marker": True,
+            "local_shutdown_receipt_hash": (
+                shutdown_receipt["receipt_hash"] if shutdown_receipt else None
+            ),
+            "worker_shutdown": "EXACT_POD_STOP_DELETE",
         })
         teardown(cli, args.pod_id, log)
         return 1
diff --git a/s3-soak/hardening.py b/s3-soak/hardening.py
new file mode 100644
index 0000000..80a3e42
--- /dev/null
+++ b/s3-soak/hardening.py
@@ -0,0 +1,278 @@
+#!/usr/bin/env python3
+"""Fail-closed S3 hardening primitives.
+
+This module deliberately stores only stable classifications and hashes of
+external-command output.  Raw command output, credentials, and environment
+contents are never written to evidence.
+"""
+from __future__ import annotations
+
+from dataclasses import dataclass
+import os
+from pathlib import Path
+import shutil
+import signal
+import time
+from typing import Any
+
+import protocol
+
+
+AWS_AUTHENTICATION = "AWS_AUTHENTICATION"
+AWS_AUTHORIZATION_OR_THROTTLING = "AWS_AUTHORIZATION_OR_THROTTLING"
+COCKROACH_CONNECTIVITY = "COCKROACH_CONNECTIVITY"
+UNKNOWN_EXTERNAL_COMMAND = "UNKNOWN_EXTERNAL_COMMAND"
+SESSION_MARGIN_SECONDS = 900
+
+_AWS_AUTH_MARKERS = (
+    b"expiredtoken", b"expired token", b"token has expired",
+    b"unauthorizedssotoken", b"sso session", b"login session",
+    b"invalidclienttokenid", b"unrecognizedclientexception",
+)
+_AWS_AUTHZ_MARKERS = (
+    b"accessdenied", b"not authorized", b"unauthorizedoperation",
+    b"throttl", b"too many requests", b"requestlimitexceeded",
+)
+_COCKROACH_CONNECTIVITY_MARKERS = (
+    b"connection refused", b"connection reset", b"connection timed out",
+    b"no such host", b"could not connect", b"failed to connect",
+    b"server closed the connection", b"tls handshake", b"x509:",
+    b"certificate", b"dial tcp", b"network is unreachable",
+)
+
+
+@dataclass(frozen=True)
+class ExternalCommandFailure(RuntimeError):
+    command_family: str
+    return_code: int
+    output_hash: str
+    failure_class: str
+
+    def __str__(self) -> str:
+        return f"{self.failure_class}:{self.command_family}:{self.return_code}"
+
+
+def classify_external_failure(command_family: str, output: bytes) -> str:
+    """Classify bounded command output without returning or retaining it."""
+    lowered = bytes(output[:1_048_576]).lower()
+    if command_family == "aws":
+        if any(marker in lowered for marker in _AWS_AUTH_MARKERS):
+            return AWS_AUTHENTICATION
+        if any(marker in lowered for marker in _AWS_AUTHZ_MARKERS):
+            return AWS_AUTHORIZATION_OR_THROTTLING
+    if command_family == "cockroach" and any(
+            marker in lowered for marker in _COCKROACH_CONNECTIVITY_MARKERS):
+        return COCKROACH_CONNECTIVITY
+    return UNKNOWN_EXTERNAL_COMMAND
+
+
+def command_failure(command_family: str, return_code: int,
+                    output: bytes) -> ExternalCommandFailure:
+    return ExternalCommandFailure(
+        command_family=command_family,
+        return_code=return_code,
+        output_hash=protocol.sha256(output),
+        failure_class=classify_external_failure(command_family, output),
+    )
+
+
+def write_atomic(path: Path, value: dict[str, Any]) -> None:
+    path = path.resolve()
+    path.parent.mkdir(parents=True, exist_ok=True)
+    if path.parent.is_symlink() or (path.exists() and path.is_symlink()):
+        raise RuntimeError("EVIDENCE_PATH_UNSAFE")
+    raw = protocol.canonical(value) + b"\n"
+    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
+    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
+    try:
+        with os.fdopen(descriptor, "wb", closefd=True) as handle:
+            handle.write(raw)
+            handle.flush()
+            os.fsync(handle.fileno())
+        os.replace(temporary, path)
+        directory = os.open(path.parent, os.O_RDONLY)
+        try:
+            os.fsync(directory)
+        finally:
+            os.close(directory)
+    finally:
+        if temporary.exists():
+            temporary.unlink()
+
+
+def failure_receipt(*, campaign_id: str, sequence: int, stage: str,
+                    request_hash: str, failure: ExternalCommandFailure,
+                    utc: str | None = None) -> dict[str, Any]:
+    core = {
+        "version": "s3-stage-failure-v1",
+        "campaign_id": campaign_id,
+        "sequence": sequence,
+        "stage": stage,
+        "request_hash": request_hash,
+        "failure_class": failure.failure_class,
+        "command_family": failure.command_family,
+        "return_code": failure.return_code,
+        "sanitized_output_sha256": failure.output_hash,
+        "raw_output_stored": False,
+        "utc": utc or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
+    }
+    return {**core, "receipt_hash": protocol.sha256(core)}
+
+
+def session_window_receipt(*, expires_epoch: int, final_exchange_epoch: int,
+                           margin_seconds: int = SESSION_MARGIN_SECONDS) -> dict[str, Any]:
+    if any(isinstance(item, bool) or not isinstance(item, int)
+           for item in (expires_epoch, final_exchange_epoch, margin_seconds)):
+        raise RuntimeError("AWS_SESSION_WINDOW_INVALID")
+    if margin_seconds < SESSION_MARGIN_SECONDS:
+        raise RuntimeError("AWS_SESSION_MARGIN_TOO_SMALL")
+    required_expiry = final_exchange_epoch + margin_seconds
+    status = "PASS" if expires_epoch >= required_expiry else "BLOCKED"
+    core = {
+        "version": "s3-aws-session-window-v1",
+        "expires_epoch": expires_epoch,
+        "final_exchange_epoch": final_exchange_epoch,
+        "margin_seconds": margin_seconds,
+        "required_expiry_epoch": required_expiry,
+        "status": status,
+        "stable_reason_code": (
+            "AWS_SESSION_MARGIN_VERIFIED" if status == "PASS"
+            else "AWS_SESSION_MARGIN_INSUFFICIENT"
+        ),
+    }
+    return {**core, "receipt_hash": protocol.sha256(core)}
+
+
+def validate_session_window(*, expires_epoch: int, final_exchange_epoch: int,
+                            margin_seconds: int = SESSION_MARGIN_SECONDS) -> dict[str, Any]:
+    receipt = session_window_receipt(
+        expires_epoch=expires_epoch,
+        final_exchange_epoch=final_exchange_epoch,
+        margin_seconds=margin_seconds,
+    )
+    if receipt["status"] != "PASS":
+        raise RuntimeError("AWS_SESSION_MARGIN_INSUFFICIENT")
+    return receipt
+
+
+def cleanup_trial_exact(trial_root: Path, evidence_root: Path) -> dict[str, Any]:
+    """Remove exactly one generated trial root and prove zero path residue."""
+    trial = trial_root.resolve(strict=False)
+    evidence = evidence_root.resolve()
+    if trial.parent != evidence or trial == evidence or trial.is_symlink():
+        raise RuntimeError("TRIAL_CLEANUP_SCOPE_INVALID")
+    existed = trial.exists()
+    if existed:
+        shutil.rmtree(trial)
+    residue = trial.exists() or trial.is_symlink()
+    core = {
+        "version": "s3-trial-cleanup-v1",
+        "trial_name": trial.name,
+        "existed_before_cleanup": existed,
+        "residue_entries": 1 if residue else 0,
+        "status": "BLOCKED" if residue else "PASS",
+        "stable_reason_code": "TRIAL_RESIDUE" if residue else "ZERO_TRIAL_RESIDUE",
+    }
+    receipt = {**core, "receipt_hash": protocol.sha256(core)}
+    if residue:
+        raise RuntimeError("TRIAL_RESIDUE")
+    return receipt
+
+
+class CheckpointCustody:
+    """Append-only, per-exchange custody outside the disposable trial root."""
+
+    def __init__(self, root: Path, campaign_id: str) -> None:
+        self.root = root.resolve()
+        self.root.mkdir(parents=True, exist_ok=False)
+        self.campaign_id = campaign_id
+        self.previous = protocol.GENESIS_HASH
+        self.sequence = 0
+
+    def capture(self, request: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
+        protocol.validate_request(request)
+        protocol.validate_result(result, request)
+        expected = self.sequence + 1
+        if request["campaign_id"] != self.campaign_id or request["sequence"] != expected:
+            raise RuntimeError("CUSTODY_SEQUENCE_INVALID")
+        core = {
+            "version": "s3-checkpoint-custody-v1",
+            "campaign_id": self.campaign_id,
+            "sequence": expected,
+            "previous_receipt_hash": self.previous,
+            "request_hash": request["request_hash"],
+            "result_hash": result["result_hash"],
+            "request_bytes_sha256": protocol.sha256(protocol.canonical(request)),
+            "result_bytes_sha256": protocol.sha256(protocol.canonical(result)),
+        }
+        receipt = {**core, "receipt_hash": protocol.sha256(core)}
+        write_atomic(self.root / f"exchange-{expected:04d}.json", receipt)
+        self.previous = receipt["receipt_hash"]
+        self.sequence = expected
+        return receipt
+
+
+def coordinated_local_shutdown(processes: list[tuple[str, int]],
+                               timeout_seconds: float = 5.0) -> dict[str, Any]:
+    """Terminate exact local coordinator/bridge PIDs and prove their absence."""
+    if timeout_seconds <= 0:
+        raise RuntimeError("SHUTDOWN_TIMEOUT_INVALID")
+    ordered = []
+    for role, pid in processes:
+        if role not in {"worker", "bridge", "coordinator"} or pid <= 1 or pid == os.getpid():
+            raise RuntimeError("SHUTDOWN_TARGET_INVALID")
+        ordered.append((role, pid))
+    for _role, pid in ordered:
+        try:
+            os.kill(pid, signal.SIGTERM)
+        except ProcessLookupError:
+            pass
+    deadline = time.monotonic() + timeout_seconds
+    remaining: list[tuple[str, int]] = []
+    while time.monotonic() < deadline:
+        remaining = []
+        for role, pid in ordered:
+            try:
+                waited, _status = os.waitpid(pid, os.WNOHANG)
+                if waited == pid:
+                    continue
+            except ChildProcessError:
+                pass
+            try:
+                os.kill(pid, 0)
+            except ProcessLookupError:
+                continue
+            remaining.append((role, pid))
+        if not remaining:
+            break
+        time.sleep(0.05)
+    if remaining:
+        for _role, pid in remaining:
+            try:
+                os.kill(pid, signal.SIGKILL)
+            except ProcessLookupError:
+                pass
+        time.sleep(0.05)
+    live = []
+    for role, pid in ordered:
+        try:
+            waited, _status = os.waitpid(pid, os.WNOHANG)
+            if waited == pid:
+                continue
+        except ChildProcessError:
+            pass
+        try:
+            os.kill(pid, 0)
+        except ProcessLookupError:
+            continue
+        live.append(role)
+    core = {
+        "version": "s3-coordinated-shutdown-v1",
+        "requested_roles": [role for role, _pid in ordered],
+        "live_roles_after_shutdown": live,
+        "status": "PASS" if not live else "BLOCKED",
+    }
+    receipt = {**core, "receipt_hash": protocol.sha256(core)}
+    if live:
+        raise RuntimeError("COORDINATED_SHUTDOWN_INCOMPLETE")
+    return receipt
diff --git a/s3-soak/host_coordinator.py b/s3-soak/host_coordinator.py
index bb057d7..7de5761 100644
--- a/s3-soak/host_coordinator.py
+++ b/s3-soak/host_coordinator.py
@@ -12,6 +12,7 @@ from typing import Any
 import re
 
 import cloud_adapter
+import hardening
 import protocol
 
 
@@ -102,11 +103,23 @@ def main() -> int:
     parser.add_argument("--config", type=Path)
     parser.add_argument("--heartbeat-seconds", type=int, default=5)
     parser.add_argument("--completion-marker", type=Path)
+    parser.add_argument("--custody-root", type=Path)
+    parser.add_argument("--aws-session-expiry-epoch", type=int)
+    parser.add_argument("--final-cloud-exchange-epoch", type=int)
+    parser.add_argument("--session-margin-seconds", type=int, default=900)
     args = parser.parse_args()
     if not 1 <= args.expected_requests <= protocol.MAX_SEQUENCE:
         raise CoordinatorFailure("EXPECTED_REQUESTS_INVALID")
     if args.mode == "live" and args.config is None:
         raise CoordinatorFailure("LIVE_CONFIG_REQUIRED")
+    if args.mode == "live" and any(value is None for value in (
+            args.custody_root, args.aws_session_expiry_epoch,
+            args.final_cloud_exchange_epoch)):
+        raise CoordinatorFailure("LIVE_CUSTODY_OR_SESSION_GATE_REQUIRED")
+    if (args.mode == "live" and
+            (args.final_cloud_exchange_epoch < int(time.time()) or
+             args.final_cloud_exchange_epoch > args.deadline_epoch)):
+        raise CoordinatorFailure("FINAL_CLOUD_EXCHANGE_WINDOW_INVALID")
     if args.deadline_epoch <= int(time.time()):
         raise CoordinatorFailure("DEADLINE_INVALID")
     if args.lambda_call_ceiling < args.expected_requests:
@@ -121,6 +134,19 @@ def main() -> int:
         path.mkdir(parents=True, exist_ok=True)
     evidence = args.evidence_root.resolve()
     evidence.mkdir(parents=True, exist_ok=False)
+    custody = None
+    if args.custody_root is not None:
+        custody = hardening.CheckpointCustody(
+            args.custody_root, args.campaign_id)
+    if args.mode == "live":
+        assert args.aws_session_expiry_epoch is not None
+        assert args.final_cloud_exchange_epoch is not None
+        session_receipt = hardening.validate_session_window(
+            expires_epoch=args.aws_session_expiry_epoch,
+            final_exchange_epoch=args.final_cloud_exchange_epoch,
+            margin_seconds=args.session_margin_seconds,
+        )
+        hardening.write_atomic(evidence / "aws-session-window.json", session_receipt)
     log = ChainLog(evidence / "coordinator.ndjson", args.campaign_id)
     processed: set[str] = set()
     expected_sequence = 1
@@ -199,6 +225,12 @@ def main() -> int:
             result = protocol.make_result(request, metrics, hashes)
             result_path = results / f"result-{expected_sequence:04d}.json"
             write_atomic(result_path, result)
+            if custody is not None:
+                custody_receipt = custody.capture(request, result)
+                log.emit("CHECKPOINT_CUSTODY_COMMITTED", {
+                    "sequence": expected_sequence,
+                    "receipt_hash": custody_receipt["receipt_hash"],
+                })
             log.emit("RESULT_COMMITTED", {
                 "sequence": expected_sequence,
                 "request_hash": request["request_hash"],
diff --git a/s3-soak/test_hardening.py b/s3-soak/test_hardening.py
new file mode 100644
index 0000000..603a722
--- /dev/null
+++ b/s3-soak/test_hardening.py
@@ -0,0 +1,137 @@
+#!/usr/bin/env python3
+from __future__ import annotations
+
+import json
+from pathlib import Path
+import subprocess
+import tempfile
+from types import SimpleNamespace
+import unittest
+from unittest import mock
+
+import cloud_adapter
+import hardening
+import protocol
+
+
+BASE = Path(__file__).resolve().parents[1]
+PRESERVED = BASE / "hardening-gate5/fixtures/s3-preserved-pairs.json"
+
+
+class HardeningTests(unittest.TestCase):
+    def test_failure_classes_are_stable_and_sanitized(self):
+        vectors = (
+            ("aws", b"ExpiredToken: token has expired", hardening.AWS_AUTHENTICATION),
+            ("aws", b"AccessDenied: not authorized", hardening.AWS_AUTHORIZATION_OR_THROTTLING),
+            ("cockroach", b"dial tcp: connection refused", hardening.COCKROACH_CONNECTIVITY),
+            ("cockroach", b"syntax error at or near x", hardening.UNKNOWN_EXTERNAL_COMMAND),
+        )
+        for family, output, expected in vectors:
+            with self.subTest(expected=expected):
+                failure = hardening.command_failure(family, 1, output)
+                self.assertEqual(failure.failure_class, expected)
+                self.assertNotIn(output.decode(), str(failure))
+                receipt = hardening.failure_receipt(
+                    campaign_id="ck-s3-hardening-test", sequence=1,
+                    stage="TEST_STAGE", request_hash="a" * 64,
+                    failure=failure, utc="2026-07-27T00:00:00Z")
+                self.assertFalse(receipt["raw_output_stored"])
+                self.assertNotIn(output.decode(), protocol.canonical(receipt).decode())
+
+    def test_stage_failure_is_fsynced_before_exact_cleanup(self):
+        with tempfile.TemporaryDirectory(prefix="s3-stage-failure-") as temporary:
+            root = Path(temporary)
+            for name in ("cockroach", "ca.crt", "aws"):
+                (root / name).write_bytes(b"fixture")
+            config = root / "config.json"
+            config.write_text(json.dumps({
+                "cockroach_bin": str(root / "cockroach"),
+                "cockroach_host": "proof.cockroachlabs.cloud",
+                "ca_cert": str(root / "ca.crt"),
+                "keychain_account": "fixture-account",
+                "keychain_service": "fixture-service",
+                "aws_cli": str(root / "aws"),
+                "aws_profile": "ck-s3",
+                "aws_region": "us-west-2",
+            }), encoding="utf-8")
+            evidence = root / "evidence"
+            request = protocol.make_request(
+                "ck-s3-hardening-test", 1, protocol.GENESIS_HASH,
+                protocol.Operation.RUN_PROMOTE, "hour-01")
+
+            def prepare(trial: Path) -> None:
+                trial.mkdir()
+                (trial / "promote-prepared.json").write_text(
+                    json.dumps({"task_id": "ck-p9-live-promote-r1"}), encoding="utf-8")
+
+            external = hardening.command_failure(
+                "aws", 255, b"ExpiredToken: private bytes are not retained")
+            with mock.patch.object(cloud_adapter, "_password", return_value=b"synthetic"), \
+                    mock.patch.object(cloud_adapter, "_load_live_completion",
+                                      return_value=SimpleNamespace(prepare=prepare)), \
+                    mock.patch.object(cloud_adapter, "_sql", side_effect=external):
+                with self.assertRaisesRegex(
+                        cloud_adapter.CloudAdapterError,
+                        "AWS_AUTHENTICATION"):
+                    cloud_adapter.run_live(request, config, evidence)
+            failure = json.loads((evidence / "failure.json").read_bytes())
+            cleanup = json.loads((evidence / "cleanup.json").read_bytes())
+            self.assertEqual(failure["failure_class"], hardening.AWS_AUTHENTICATION)
+            self.assertEqual(failure["stage"], "PRESEED_CLEANUP")
+            self.assertEqual(cleanup["status"], "PASS")
+            self.assertEqual(cleanup["residue_entries"], 0)
+            self.assertFalse((evidence / "trial-0001").exists())
+
+    def test_preserved_eleven_pairs_and_expiry_exchange_twelve(self):
+        frozen = json.loads(PRESERVED.read_bytes())
+        self.assertEqual(len(frozen["pairs"]), 11)
+        prior = protocol.GENESIS_HASH
+        custody_hashes = []
+        with tempfile.TemporaryDirectory(prefix="s3-custody-") as temporary:
+            custody = hardening.CheckpointCustody(
+                Path(temporary) / "custody", "ck-s3-20260727-release-r1")
+            for expected, pair in enumerate(frozen["pairs"], 1):
+                request = protocol.validate_request(pair["request"])
+                result = protocol.validate_result(pair["result"], request)
+                self.assertEqual(request["sequence"], expected)
+                self.assertEqual(request["parent_hash"], prior)
+                receipt = custody.capture(request, result)
+                custody_hashes.append(receipt["receipt_hash"])
+                prior = request["request_hash"]
+            self.assertEqual(custody.sequence, 11)
+            self.assertEqual(len(set(custody_hashes)), 11)
+        exchange_12 = protocol.validate_request(frozen["exchange_12_request"])
+        self.assertEqual(exchange_12["sequence"], 12)
+        self.assertEqual(exchange_12["parent_hash"], prior)
+        with self.assertRaisesRegex(RuntimeError, "AWS_SESSION_MARGIN_INSUFFICIENT"):
+            hardening.validate_session_window(
+                expires_epoch=20_000, final_exchange_epoch=19_500,
+                margin_seconds=900)
+        passing = hardening.validate_session_window(
+            expires_epoch=20_400, final_exchange_epoch=19_500,
+            margin_seconds=900)
+        self.assertEqual(passing["status"], "PASS")
+
+    def test_coordinated_local_shutdown_proves_all_processes_absent(self):
+        processes = [
+            subprocess.Popen(["/bin/sleep", "30"]),
+            subprocess.Popen(["/bin/sleep", "30"]),
+            subprocess.Popen(["/bin/sleep", "30"]),
+        ]
+        try:
+            receipt = hardening.coordinated_local_shutdown([
+                ("worker", processes[2].pid),
+                ("bridge", processes[0].pid),
+                ("coordinator", processes[1].pid),
+            ])
+            self.assertEqual(receipt["status"], "PASS")
+            self.assertEqual(receipt["live_roles_after_shutdown"], [])
+        finally:
+            for process in processes:
+                if process.poll() is None:
+                    process.kill()
+                    process.wait()
+
+
+if __name__ == "__main__":
+    unittest.main()

```
