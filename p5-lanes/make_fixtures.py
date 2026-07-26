"""Generate the deterministic synthetic P5 fixtures under fixtures/.

All inputs are synthetic and non-sensitive. Regenerate with:
    python3 make_fixtures.py
Output is strict canonical UTF-8 JSON (sorted keys, no insignificant
whitespace), so regeneration is byte-for-byte reproducible.
"""
from __future__ import annotations

import os

from manifest import LANES, VERSION, canonical_json, sha256_hex

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
POLICY_VERSION = "policy-p5-v1"

PERSONA_SOURCE_HASHES = {
    "persona-athena": "07909c80216efd8c9b666a51f1a25289b4814f0fa9f4172502a01fd355cea1db",
    "persona-daedalus": "935694c3e765a5492929f6c028037ed24fc21657e67e83dba76f823b6b04c802",
    "persona-argos-panoptes": "75fa8f30e2a6c173d3cabef78e0d58f211740773055abce556bca69ec0251b42",
}

TRAIT_SPECS = {
    "syntax_structure": [
        ("trait-grammar-strict", "persona-daedalus", {"name": "grammar-strict",
                                  "description": "Flags malformed syntax and structure only."}),
        ("trait-format-consistency", "persona-argos-panoptes", {"name": "format-consistency",
                                      "description": "Notes inconsistent formatting patterns."}),
    ],
    "security_policy": [
        ("trait-policy-literal", "persona-athena", {"name": "policy-literal",
                                  "description": "Reads policy text literally; advisory only."}),
    ],
    "logic_coherence": [
        ("trait-contradiction-scan", "persona-athena", {"name": "contradiction-scan",
                                      "description": "Flags internal contradictions in output."}),
        ("trait-premise-check", "persona-daedalus", {"name": "premise-check",
                                 "description": "Checks stated premises against conclusions."}),
    ],
    "contextual_fit": [
        ("trait-context-match", "persona-daedalus", {"name": "context-match",
                                 "description": "Compares output against the prompt context."}),
    ],
    "trajectory_alignment": [
        ("trait-trajectory-drift", "persona-argos-panoptes", {"name": "trajectory-drift",
                                    "description": "Flags drift from the recorded trajectory."}),
        ("trait-step-order", "persona-argos-panoptes", {"name": "step-order",
                              "description": "Checks event ordering against the ledger."}),
        ("trait-replay-watch", "persona-athena", {"name": "replay-watch",
                                "description": "Notes replayed or repeated steps."}),
    ],
}

FINDING_SPECS = {
    "syntax_structure": [
        {"code": "SYN-001", "severity": "LOW", "message": "Minor indentation inconsistency."},
    ],
    "security_policy": [
        {"code": "SEC-001", "severity": "INFO", "message": "Policy version matches declaration."},
    ],
    "logic_coherence": [
        {"code": "LOG-001", "severity": "MEDIUM", "message": "Conclusion restates one premise."},
    ],
    "contextual_fit": [
        {"code": "CTX-001", "severity": "INFO", "message": "Output stays within prompt scope."},
    ],
    "trajectory_alignment": [
        {"code": "TRA-001", "severity": "LOW", "message": "Step order matches the trajectory."},
    ],
}

DISSENT_SPECS = {
    "logic_coherence": ["Minority view: the restated premise is intentional emphasis."],
}


def build_manifest(lane: str) -> dict:
    traits = []
    for trait_id, source_id, payload in TRAIT_SPECS[lane]:
        traits.append({"trait_id": trait_id, "trait_hash": sha256_hex(payload),
                       "source_id": source_id,
                       "source_file_hash": PERSONA_SOURCE_HASHES[source_id],
                       "payload": payload})
    return {"version": VERSION, "manifest_id": "manifest-" + lane, "lane": lane,
            "traits": traits, "policy_version": POLICY_VERSION,
            "provenance": {"source": "p5-synthetic-fixture"}}


def build_result(lane: str, manifest: dict) -> dict:
    dissent = list(DISSENT_SPECS.get(lane, []))
    prompt = {"text": "synthetic prompt for " + lane, "context": "synthetic"}
    output = {"summary": "synthetic advisory summary for " + lane,
              "annotations": ["synthetic-annotation"]}
    provenance = {
        "task_id": "task-p5-synthetic",
        "trajectory_hash": sha256_hex({"trajectory": lane, "synthetic": True}),
        "candidate_id": "cand-p5-synthetic",
        "policy_version": POLICY_VERSION,
        "prompt_hash": sha256_hex(prompt),
        "route": "synthetic-route/kimi",
        "served_model": "kimi-synthetic-served-model",
        "output_hash": sha256_hex(output),
        "retry_count": 0,
        "timeout_ms": 5000,
        "dissent": bool(dissent),
        "receipt_hash": sha256_hex({"receipt": lane, "synthetic": True}),
    }
    return {"version": VERSION, "result_id": "result-" + lane, "lane": lane,
            "manifest_id": manifest["manifest_id"],
            "manifest_hash": sha256_hex(manifest),
            "prompt": prompt, "output": output, "verdict": "ADVISORY",
            "findings": [dict(f) for f in FINDING_SPECS[lane]],
            "dissent": dissent, "provenance": provenance}


def main() -> None:
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    written = []
    for lane in LANES:
        manifest = build_manifest(lane)
        result = build_result(lane, manifest)
        for name, record in (("manifest_" + lane + ".json", manifest),
                             ("result_" + lane + ".json", result)):
            path = os.path.join(FIXTURE_DIR, name)
            with open(path, "wb") as handle:
                handle.write(canonical_json(record))
            written.append(name)
    for name in written:
        print(name)


if __name__ == "__main__":
    main()
