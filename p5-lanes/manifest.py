"""P5 advisory lane manifests, results, and deterministic aggregation.

Five advisory lanes only: syntax_structure, security_policy, logic_coherence,
contextual_fit, trajectory_alignment. Lanes are advisory: no lane, persona
trait, or aggregate may use tools, mutate authority, change policy, call
another agent, or decide promotion/refusal. All failures fail closed with a
stable reason code. Runtime uses only the Python standard library.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
VERSION = "p5-v1"
MAX_RECORD_BYTES = 65536
MAX_RETRY_COUNT = 3
MAX_TIMEOUT_MS = 60000

LANES = (
    "syntax_structure",
    "security_policy",
    "logic_coherence",
    "contextual_fit",
    "trajectory_alignment",
)

MANIFEST_FIELDS = {"version", "manifest_id", "lane", "traits", "policy_version", "provenance"}
TRAIT_FIELDS = {"trait_id", "trait_hash", "source_id", "source_file_hash", "payload"}
TRAIT_PAYLOAD_FIELDS = {"name", "description"}
RESULT_FIELDS = {"version", "result_id", "lane", "manifest_id", "manifest_hash",
                 "prompt", "output", "verdict", "findings", "dissent", "provenance"}
FINDING_FIELDS = {"code", "severity", "message"}
OUTPUT_FIELDS = {"summary", "annotations"}
PROMPT_FIELDS = {"text", "context"}
PROVENANCE_FIELDS = {"task_id", "trajectory_hash", "candidate_id", "policy_version",
                     "prompt_hash", "route", "served_model", "output_hash",
                     "retry_count", "timeout_ms", "dissent", "receipt_hash"}
SEVERITIES = {"INFO", "LOW", "MEDIUM", "HIGH"}
ADVISORY_VERDICT = "ADVISORY"

# Structural tool/authority/injection request markers. Any of these keys or
# string markers inside a trait payload, finding, or dissent note fails closed.
FORBIDDEN_KEYS = {
    "tool", "tools", "tool_call", "tool_request", "authority", "promote",
    "promotion", "refuse", "refusal", "escalate", "delegate", "call_agent",
    "policy_change", "execute", "shell", "command",
}
INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore all previous",
    "disregard all previous",
    "disregard previous",
    "you are now",
    "system prompt",
)


class ManifestError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    """Canonical UTF-8 JSON; sorted keys, no insignificant whitespace, 64 KiB cap."""
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ManifestError("MALFORMED_RECORD") from exc
    if len(encoded) > MAX_RECORD_BYTES:
        raise ManifestError("RECORD_TOO_LARGE")
    return encoded


def sha256_hex(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
    return hashlib.sha256(raw).hexdigest()


def require_id(value: Any) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise ManifestError("INVALID_ID")
    return value


def require_hash(value: Any) -> str:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
        raise ManifestError("INVALID_HASH")
    return value


def validate_object(record: Any, required: set[str], allowed: set[str]) -> None:
    if not isinstance(record, dict):
        raise ManifestError("MALFORMED_RECORD")
    unknown = set(record) - allowed
    missing = required - set(record)
    if unknown:
        raise ManifestError("UNKNOWN_FIELD")
    if missing:
        raise ManifestError("MISSING_FIELD")


def contains_forbidden_request(value: Any) -> bool:
    """Detect injection, tool, or authority requests in nested content."""
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str) and key.lower() in FORBIDDEN_KEYS:
                return True
            if contains_forbidden_request(item):
                return True
        return False
    if isinstance(value, list):
        return any(contains_forbidden_request(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return any(marker in lowered for marker in INJECTION_MARKERS)
    return False


def load_canonical(path: str) -> Any:
    """Load a JSON record that must be stored in exact canonical form."""
    with open(path, "rb") as handle:
        raw = handle.read()
    if len(raw) > MAX_RECORD_BYTES:
        raise ManifestError("RECORD_TOO_LARGE")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestError("MALFORMED_RECORD") from exc
    if canonical_json(value) != raw:
        raise ManifestError("NON_CANONICAL_ENCODING")
    return value


def validate_trait(trait: Any) -> None:
    validate_object(trait, TRAIT_FIELDS, TRAIT_FIELDS)
    require_id(trait["trait_id"])
    require_hash(trait["trait_hash"])
    require_id(trait["source_id"])
    require_hash(trait["source_file_hash"])
    validate_object(trait["payload"], TRAIT_PAYLOAD_FIELDS, TRAIT_PAYLOAD_FIELDS)
    if not isinstance(trait["payload"]["name"], str) or not trait["payload"]["name"]:
        raise ManifestError("MALFORMED_RECORD")
    if not isinstance(trait["payload"]["description"], str):
        raise ManifestError("MALFORMED_RECORD")
    if sha256_hex(trait["payload"]) != trait["trait_hash"]:
        raise ManifestError("STALE_HASH")
    if contains_forbidden_request(trait["payload"]):
        raise ManifestError("FORBIDDEN_REQUEST")


def validate_manifest(manifest: Any) -> None:
    """Strict lane manifest: 1-3 unique hash-pinned inert persona traits."""
    validate_object(manifest, MANIFEST_FIELDS, MANIFEST_FIELDS)
    if manifest["version"] != VERSION:
        raise ManifestError("UNSUPPORTED_SCHEMA")
    require_id(manifest["manifest_id"])
    if manifest["lane"] not in LANES:
        raise ManifestError("UNKNOWN_LANE")
    if not isinstance(manifest["policy_version"], str) or not manifest["policy_version"]:
        raise ManifestError("MISSING_PROVENANCE")
    traits = manifest["traits"]
    if not isinstance(traits, list) or not 1 <= len(traits) <= 3:
        raise ManifestError("TRAIT_LIMIT_VIOLATION")
    trait_ids = []
    for trait in traits:
        validate_trait(trait)
        trait_ids.append(trait["trait_id"])
    if len(set(trait_ids)) != len(trait_ids):
        raise ManifestError("TRAIT_LIMIT_VIOLATION")
    provenance = manifest["provenance"]
    try:
        validate_object(provenance, {"source"}, {"source"})
    except ManifestError as exc:
        raise ManifestError("MISSING_PROVENANCE") from exc
    if not isinstance(provenance["source"], str) or not provenance["source"]:
        raise ManifestError("MISSING_PROVENANCE")


def validate_provenance(provenance: Any) -> None:
    if not isinstance(provenance, dict) or set(provenance) - PROVENANCE_FIELDS:
        raise ManifestError("MISSING_PROVENANCE")
    if not PROVENANCE_FIELDS.issubset(provenance):
        raise ManifestError("MISSING_PROVENANCE")
    require_id(provenance["task_id"])
    require_id(provenance["candidate_id"])
    for key in ("trajectory_hash", "prompt_hash", "output_hash", "receipt_hash"):
        require_hash(provenance[key])
    if not isinstance(provenance["route"], str) or not provenance["route"]:
        raise ManifestError("MISSING_PROVENANCE")
    if not isinstance(provenance["served_model"], str) or not provenance["served_model"]:
        raise ManifestError("MISSING_PROVENANCE")
    if not isinstance(provenance["policy_version"], str) or not provenance["policy_version"]:
        raise ManifestError("MISSING_PROVENANCE")
    if (isinstance(provenance["retry_count"], bool) or
            not isinstance(provenance["retry_count"], int) or
            not 0 <= provenance["retry_count"] <= MAX_RETRY_COUNT):
        raise ManifestError("MISSING_PROVENANCE")
    if (isinstance(provenance["timeout_ms"], bool) or
            not isinstance(provenance["timeout_ms"], int) or
            not 1 <= provenance["timeout_ms"] <= MAX_TIMEOUT_MS):
        raise ManifestError("MISSING_PROVENANCE")
    if not isinstance(provenance["dissent"], bool):
        raise ManifestError("MISSING_PROVENANCE")


def validate_finding(finding: Any) -> None:
    validate_object(finding, FINDING_FIELDS, FINDING_FIELDS)
    if finding["severity"] not in SEVERITIES:
        raise ManifestError("MALFORMED_OUTPUT")
    if not isinstance(finding["code"], str) or not finding["code"]:
        raise ManifestError("MALFORMED_OUTPUT")
    if not isinstance(finding["message"], str):
        raise ManifestError("MALFORMED_OUTPUT")
    if contains_forbidden_request(finding):
        raise ManifestError("FORBIDDEN_REQUEST")


def validate_result(result: Any, manifest: dict[str, Any]) -> None:
    """Strict lane result bound to its manifest, with full provenance linkage."""
    validate_object(result, RESULT_FIELDS - {"provenance"}, RESULT_FIELDS)
    if "provenance" not in result:
        raise ManifestError("MISSING_PROVENANCE")
    if result["version"] != VERSION:
        raise ManifestError("UNSUPPORTED_SCHEMA")
    require_id(result["result_id"])
    if result["lane"] not in LANES:
        raise ManifestError("UNKNOWN_LANE")
    if result["lane"] != manifest["lane"]:
        raise ManifestError("MISSING_LANE")
    if result["manifest_id"] != manifest["manifest_id"]:
        raise ManifestError("STALE_HASH")
    require_hash(result["manifest_hash"])
    if sha256_hex(manifest) != result["manifest_hash"]:
        raise ManifestError("STALE_HASH")
    if result["verdict"] != ADVISORY_VERDICT:
        raise ManifestError("AUTHORITY_REQUEST")
    if not isinstance(result["output"], dict):
        raise ManifestError("MALFORMED_OUTPUT")
    validate_object(result["output"], OUTPUT_FIELDS, OUTPUT_FIELDS)
    if not isinstance(result["output"]["summary"], str):
        raise ManifestError("MALFORMED_OUTPUT")
    if not isinstance(result["output"]["annotations"], list):
        raise ManifestError("MALFORMED_OUTPUT")
    if not all(isinstance(item, str) for item in result["output"]["annotations"]):
        raise ManifestError("MALFORMED_OUTPUT")
    if contains_forbidden_request(result["output"]):
        raise ManifestError("FORBIDDEN_REQUEST")
    try:
        validate_object(result["prompt"], PROMPT_FIELDS, PROMPT_FIELDS)
    except ManifestError as exc:
        raise ManifestError("MALFORMED_OUTPUT") from exc
    if not all(isinstance(result["prompt"][key], str) for key in PROMPT_FIELDS):
        raise ManifestError("MALFORMED_OUTPUT")
    if contains_forbidden_request(result["prompt"]):
        raise ManifestError("FORBIDDEN_REQUEST")
    if not isinstance(result["findings"], list):
        raise ManifestError("MALFORMED_OUTPUT")
    for finding in result["findings"]:
        validate_finding(finding)
    if not isinstance(result["dissent"], list):
        raise ManifestError("MALFORMED_OUTPUT")
    for note in result["dissent"]:
        if not isinstance(note, str):
            raise ManifestError("MALFORMED_OUTPUT")
        if contains_forbidden_request(note):
            raise ManifestError("FORBIDDEN_REQUEST")
    validate_provenance(result["provenance"])
    provenance = result["provenance"]
    if provenance["policy_version"] != manifest["policy_version"]:
        raise ManifestError("STALE_HASH")
    if provenance["prompt_hash"] != sha256_hex(result["prompt"]):
        raise ManifestError("STALE_HASH")
    if provenance["output_hash"] != sha256_hex(result["output"]):
        raise ManifestError("STALE_HASH")
    if provenance["dissent"] != bool(result["dissent"]):
        raise ManifestError("MALFORMED_OUTPUT")


def _fail(reason: str) -> tuple[None, str]:
    return None, reason


def aggregate(results: Any, manifests: Any) -> tuple[dict[str, Any] | None, str]:
    """Deterministically aggregate exactly five lane results.

    Returns (record, "OK") or (None, reason). The record is advisory only:
    it carries findings and dissent and has no promotion/refusal authority.
    """
    if not isinstance(results, list) or not isinstance(manifests, dict):
        return _fail("MALFORMED_RECORD")

    seen: dict[str, dict[str, Any]] = {}
    for result in results:
        if not isinstance(result, dict) or not isinstance(result.get("lane"), str):
            return _fail("MALFORMED_OUTPUT")
        lane = result["lane"]
        if lane not in LANES:
            return _fail("UNKNOWN_LANE")
        if lane in seen:
            return _fail("DUPLICATE_RESULT")
        seen[lane] = result
    missing = [lane for lane in LANES if lane not in seen]
    if missing:
        return _fail("MISSING_LANE")

    lane_results: dict[str, str] = {}
    findings: list[dict[str, Any]] = []
    dissent: list[dict[str, str]] = []
    try:
        for lane in LANES:
            manifest = manifests.get(lane)
            if manifest is None:
                return _fail("MISSING_LANE")
            validate_manifest(manifest)
            result = seen[lane]
            validate_result(result, manifest)
            canonical_json(result)  # enforce the 64 KiB record cap
            lane_results[lane] = sha256_hex(result)
            for finding in result["findings"]:
                findings.append({"lane": lane, "code": finding["code"],
                                 "severity": finding["severity"],
                                 "message": finding["message"]})
            for note in result["dissent"]:
                dissent.append({"lane": lane, "note": note})
    except ManifestError as exc:
        return _fail(str(exc))

    findings.sort(key=lambda f: (f["lane"], f["code"], f["message"]))
    dissent.sort(key=lambda d: (d["lane"], d["note"]))
    core = {"version": VERSION, "status": "ADVISORY_COMPLETE",
            "lanes": list(LANES), "lane_results": lane_results,
            "findings": findings, "dissent": dissent}
    record = dict(core)
    record["aggregate_id"] = "agg-" + sha256_hex(core)[:32]
    try:
        canonical_json(record)
    except ManifestError:
        return _fail("RECORD_TOO_LARGE")
    return record, "OK"
