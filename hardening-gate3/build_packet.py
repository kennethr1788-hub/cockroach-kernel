#!/usr/bin/env python3
"""Build the sanitized byte-complete independent Gate 3 judge packet."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CUSTODY = REPO / ".hardening-runtime/gate3-real-workflow/custody-r1"
OUTPUT = REPO / "HARDENING_GATE3_FINAL_GLM_PACKET_R1.md"


def section(title: str, body: str) -> str:
    return f"\n## {title}\n\n{body.rstrip()}\n"


def main() -> None:
    parts = ["""# Hardening Gate 3 Independent Judge Packet R1

You are the independent non-authoring judge. Do not praise the work and do not
suggest code. Find blockers. You have no tools, shell, browser, filesystem,
credential, deployment, implementation, or public-action authority.

Decision requested: Does this single-operator real-workflow trace meet
`HARDENING_3_REAL_WORKFLOW_GREEN` as an honest, complete evidence trace?

Review criteria:

1. all ten required workflow steps are directly evidenced;
2. the three declared work units are genuinely retained after declared loss;
3. the cloud output remains advisory and local deterministic policy is sole
   promotion/refusal authority;
4. overwrite refusal, unchanged original bytes, fresh-root behavior, replay
   refusal, executable checks, and residue assertions are coherent;
5. destructive scope, credential boundary, live-row retention, and cleanup are
   safe and honestly described;
6. limitations are narrow enough that the gate claim remains valid;
7. hashes and cross-record linkages are internally consistent.

Return exactly:

- `SERVED_MODEL: <provider model identity>`
- `PACKET_SHA256: <the supplied packet hash>`
- `VERDICT: GREEN | NOT_GREEN | INSUFFICIENT_EVIDENCE`
- `BLOCKERS:` numbered list or `none`
- `NON_BLOCKING_RISKS:` numbered list or `none`
- `EVIDENCE_BASIS:` concise references to packet sections

GREEN means no blocker remains for Gate 3 evidence integrity. Do not judge
later hardening gates, release readiness, benchmark superiority, or submission
readiness.
"""]
    for title, relative in (
        ("Task contract", "HARDENING_GATE3_TASK_CONTRACT_R1.md"),
        ("Human edit receipt", "HARDENING_GATE3_HUMAN_EDIT_RECEIPT_R1.md"),
        ("Pre-loss checkpoint", "HARDENING_GATE3_PRELOSS_CHECKPOINT_R1.md"),
        ("Final report", "HARDENING_GATE3_REAL_WORKFLOW_REPORT_R1.md"),
        ("Trace harness source", "hardening-gate3/trace.py"),
    ):
        parts.append(section(title, (REPO / relative).read_text(encoding="utf-8")))
    for name in (
        "manifest.json", "trajectory.json", "candidate.json", "context.json",
        "decision.json", "warrant.json", "capture-receipt.json",
        "live-receipt.json", "loss-receipt.json", "continuation-receipt.json",
        "promotion-receipt.json", "unrecovered-ledger.json",
        "residue-receipt.json", "evidence-manifest.json",
    ):
        value = json.loads((CUSTODY / name).read_bytes())
        parts.append(section("Evidence: " + name,
                             "```json\n" + json.dumps(value, sort_keys=True,
                                                        separators=(",", ":")) + "\n```"))
    manifest = json.loads((CUSTODY / "manifest.json").read_bytes())
    objects = {item["path"]: item["content_hash"] for item in manifest["files"]}
    for relative in ("cockroach_kernel/cli.py", "cockroach_kernel/test_cli.py"):
        source = (CUSTODY / "objects" / objects[relative]).read_text(encoding="utf-8")
        parts.append(section("Recovered source: " + relative,
                             "```python\n" + source + "\n```"))
    body = "".join(parts)
    if "/Users/" in body or "AWS_ACCESS_KEY_ID=" in body or "AWS_SECRET_ACCESS_KEY=" in body:
        raise RuntimeError("PACKET_SANITIZATION_FAILED")
    OUTPUT.write_text(body, encoding="utf-8")
    print(hashlib.sha256(OUTPUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
