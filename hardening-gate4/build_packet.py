from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "HARDENING_GATE4_BASELINE_PROTOCOL_R1.md"
RESEARCH = ROOT / "HARDENING_GATE4_RESEARCH_RECEIPT_R1.md"
OUTPUT = ROOT / "HARDENING_GATE4_JUDGE_PACKET_R1.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    protocol = PROTOCOL.read_text(encoding="utf-8")
    research = RESEARCH.read_text(encoding="utf-8")
    header = f"""# Hardening Gate 4 — Same-Hash Independent Judge Packet R1

## Packet control

- `TARGET_GATE`: `HARDENING_4_BASELINE_PROTOCOL_GREEN`
- `PARENT_GATE`: `HARDENING_3_REAL_WORKFLOW_GREEN`
- `TARGET_PROTOCOL_SHA256`: `{sha256(PROTOCOL)}`
- `RESEARCH_RECEIPT_SHA256`: `{sha256(RESEARCH)}`
- `PACKET_SHA256`: supplied externally from the exact packet bytes
- `AUTHORING_AUTHORITY`: none for judges
- `TOOL_AUTHORITY`: none for judges
- `PUBLIC_ACTION_AUTHORITY`: none for judges

## Required judge output

Return exactly one JSON object and no Markdown with these keys:

```text
verdict
packet_sha256
model
review_scope
material_findings
evidence_assessment
```

`verdict` must be `GREEN`, `NOT_GREEN`, or `BLOCKED`. `packet_sha256` must
exactly equal the SHA-256 supplied by the caller outside this packet. Judges
must not write code, propose implementation tickets, edit artifacts, use tools,
or assume missing evidence. A material fairness, information-symmetry,
baseline-comparability, lifecycle, schema, statistics, or construct-validity
defect requires `NOT_GREEN`. Gate 4 is protocol qualification only: absence of
future Gate 5 implementation or Gate 6 results is not itself a defect.

## GLM review scope

Review fairness, information symmetry, scenario pairing, outcome taxonomy,
statistics, canonical receipt schema, construct validity, bias disclosures,
and whether unsupported baseline capabilities are separated from actual
failures.

## Claude Opus 4.8 review scope

Review harness and lifecycle semantics, checkpoint timing, storage/custody
symmetry, exact-artifact selection, recovery timing, teardown, conventional
baseline strength, and product/baseline comparability.

<TARGET_PROTOCOL>
{protocol}</TARGET_PROTOCOL>

<RESEARCH_RECEIPT>
{research}</RESEARCH_RECEIPT>
"""
    OUTPUT.write_text(header, encoding="utf-8")


if __name__ == "__main__":
    main()
