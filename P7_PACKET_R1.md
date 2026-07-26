# P7 Exact Judge Packet R1

- `PHASE`: `P7`
- `TARGET_GATE`: `CK_P7_RECOVERY_GREEN`
- `IMPLEMENTATION_COMMIT`: `08de647c4f910cdd22905980511702bd20eeffb1`
- `EVIDENCE_COMMIT`: `e43bf23dee6903451f770d87bd2d526a6999af48`
- `GIT_STATUS_AT_FREEZE`: clean before packet creation
- `PACKET_REVISION`: `R1`
- `REQUIRED_JUDGES`: Claude runtime/recovery semantics and AGY Wall-7/destructive-boundary review

## Review question

Return GREEN only if the embedded implementation and evidence prove the frozen
P7 contract: guarded declared loss inside a disposable root; exact surviving
byte reconstruction only; deterministic maximum-provable selection; one-use
warrant consumption before promotion; fail-closed interruption and replay;
strict tamper, malformed, unsafe, unsupported, stale-policy, missing-quorum,
failed-test, and no-survivor refusal; actual successor-byte verification in a
fresh child process; two identical CockroachDB trials; and clean teardown.
A persuasive summary is not evidence. Any concrete safety, correctness, or
boundary gap is NOT_GREEN.

The judge must not propose code, patches, implementation steps, replacement
architecture, deployment actions, or builder direction. It may report verdict,
failed criteria, concrete failure mechanism, missing proof, and non-blocking
risks only.

## Disclosed limitations and non-claims

- This is declared-state reconstruction from surviving authorized, hash-bound
  representations, not filesystem undelete, forensic recovery, whole-home
  recovery, prediction, identity continuity, or recovery of unavailable bytes.
- Promotion consists of consumed-warrant state followed by exact byte writes
  and a separate recovery-receipt transaction. An interruption after consume
  is intentionally fail-closed and cannot be retried with the same warrant.
- The executable test is a deterministic feature-file byte binding in this
  phase harness; it is not a general-purpose arbitrary-code test runner.
- The integration harness uses an insecure loopback-only disposable local
  CockroachDB node with synthetic data; it is not a production deployment.
- `detect-secrets` flags synthetic SHA-256 fixture values as unverified high
  entropy. Gitleaks reports no leaks, and no credential detector verifies any
  secret.

## Required verdict schema

```text
ROLE:
ARTIFACT: P7_PACKET_R1.md
BUILDER_AND_INFLUENCE_DISCLOSURE:
PACKET_SHA256: <exact hash supplied out-of-band>
VERDICT: GREEN | BLOCKED | NOT_GREEN | INSUFFICIENT_EVIDENCE | RECUSAL_REQUIRED
FAILED_CRITERIA:
EVIDENCE:
FAILURE_MECHANISM:
MISSING_PROOF:
NON_BLOCKING_RISKS:
RECUSAL_CHECK:
```


## Embedded file: P7_CONTRACT.md

```markdown
# P7 Frozen Contract

- `PHASE`: `P7`
- `PARENT_GATE`: `CK_P6_QUORUM_GREEN`
- `START_COMMIT`: `54437edb45af91424713f9fa3facd20f84c8f5e3`
- `TARGET_GATE`: `CK_P7_RECOVERY_GREEN`
- `STATUS`: `FROZEN_BEFORE_IMPLEMENTATION`
- `UTC_FROZEN`: `2026-07-26T00:57:11Z`

Implement declared-loss recovery only inside a generated project-local
disposable root. This phase reconstructs only bytes present in surviving,
authorized, hash-bound representations. It does not perform filesystem
undelete and makes no claim about unavailable bytes, whole-home recovery,
prediction, consciousness, identity, or forensic erasure.

## Fixed records and authority

Canonical UTF-8 JSON records are strict, size-bounded, reject unknown fields,
and bind all referenced content by SHA-256:

- declared-state manifest and trajectory receipt;
- loss receipt naming the exact declared paths and observed absence;
- surviving candidate with provenance, policy, quorum, integrity, executable
  test, prefix, and source-receipt bindings;
- one-use recovery warrant;
- recovery decision, promotion/refusal receipt, and unrecovered-item ledger.

The deterministic selector admits only candidates whose schema, provenance,
source receipt, policy version, P6 quorum decision, integrity hash, declared
path set, and executable-test declaration all validate. Among admitted
candidates it selects the longest contiguous proven trajectory prefix; ties
break by canonical candidate ID. The selector does not invent or merge bytes.

One authoritative CockroachDB serializable transaction changes an `ISSUED`
warrant to `CONSUMED` before recording promotion. An interruption after
consumption leaves the warrant consumed or invalid and never replayable. A
second use, stale policy, stale receipt, tamper, malformed/unknown fields,
unsafe path, unsupported schema, missing quorum, or failed executable test
refuses with a stable reason code.

## Filesystem boundary

- Every mutable path is a normalized relative POSIX path under a generated
  `p7-recovery/p7-trial-*` root.
- Absolute paths, empty/dot segments, `..`, NUL, backslashes, symlinks,
  undeclared paths, executable content, and manifest drift fail before any
  deletion or write.
- Loss stops only the sandbox-owned synthetic child process, unlinks only
  manifest-owned files, and proves the declared active workspace is empty.
- Surviving representations live outside the disposable active workspace but
  inside the same generated trial root and are read-only inputs to recovery.
- Cleanup removes the entire generated trial root and proves no child process,
  socket, symlink, or residue remains.

## Required vectors

- valid maximum-provable promotion with a shorter valid competing candidate;
- fresh-context continuation whose executable test passes without hidden
  session state or task restatement;
- policy veto, tamper, replay, malformed, unsafe path, unsupported schema,
  stale policy, missing quorum, failed executable test, and no surviving
  candidate refusal;
- interrupted recovery after warrant consumption;
- exact loss/manifest/source/promotion receipt linkage;
- five-repeat deterministic candidate selection and verdict semantics;
- two fresh-root CockroachDB integration trials with clean teardown.

Required contributors:

- Kimi: non-authoritative surviving-state adapters, fixtures, and
  fresh-context harness plumbing.
- Vibe: interruption, replay, tamper, unsafe-input, failed-recovery, and
  repeated-cycle fault review.
- Devstral: disposable path controls, manifest fixtures, residue scans,
  process teardown, and clean-state boundary review.
- Codex: deletion boundary, maximum-provable selection, one-use authority,
  CockroachDB integration, reconciliation, evidence, and packet.

Required judges after mechanical evidence: Claude plus AGY on one exact packet
hash. Neither builder nor any model output can close the gate.

Kill line: any path escape, false recovery, invented byte, replay acceptance,
unconsumed promotion, policy/quorum bypass, hidden-state dependency,
non-determinism, process/residue leak, private-data egress, or required-judge
failure leaves `CK_P7_BLOCKED`.
```

## Embedded file: P7_BUILDER_ASSIGNMENTS.md

```markdown
# P7 Builder Assignments

All inputs are synthetic and non-sensitive. No contributor may access
credentials, HOME runtime, live memory, client data, deployment, AWS, RunPod,
or later phases.

- Kimi works only in an isolated P7 worktree and proposes
  `p7-recovery/` adapters, fixtures, and focused tests. It has no deletion,
  promotion, policy, or gate authority.
- Vibe performs a bounded read-only adversarial review of the accepted P7
  candidate. Codex applies any accepted corrections.
- Devstral receives only the sanitized contract for a no-tool path,
  manifest, teardown, and clean-state boundary review.
- Codex owns guarded deletion, deterministic selection, one-use authority,
  real CockroachDB transaction proof, integration, evidence, and packet.

Every contribution records route, model, scope, output, accepted/rejected
findings, tests, and limitations.
```

## Embedded file: P7_PERSONA_SOURCE_RECEIPT.md

```markdown
# P7 Persona Source Receipt

- `UTC_CREATED`: `2026-07-26T00:57:11Z`
- `MODE`: inert, sanitized, hash-pinned planning/testing lenses only
- `RUNTIME_PERSONA_LOADING`: `NO`
- `TOOLS_MEMORY_OR_ROUTING_IMPORTED`: `NO`

| Role | Local source SHA-256 |
|---|---|
| Curator | `48dfbb22583869a25dbee922f9940d526450f222d1948384a79ee2747090e3a9` |
| Soteria | `a19bfa83b88e0d7d5f0620720b57600684fc7cb904eca0588ab964f6a0998589` |
| Vault-Recall | `556eb3698c66977d6f01662c031ce393971d9c8c08e77dbef144bd148613a528` |
| Mythos | `7cee25885aa2e772c1838d680b942428e3a3b7dd4971625ad7d765dc8486defa` |
| Talos | `d7041d64f13b9f5fadee50d1e70061f4d7f75f32319bd4479966f6b9c423f4b1` |
| Themis | `3a67013092b2109a5d8dcaf603e0acd64e3302e048db4fa8ebafbd194d4538e8` |

The raw persona files remain outside the project. They are treated as local
planning references, not copied into runtime records, model prompts, or the
judge packet. Their names grant no authority.
```

## Embedded file: P7_BUILDER_CONTRIBUTIONS.md

```markdown
# P7 Builder Contributions

- `UTC_UPDATED`: `2026-07-26T01:23:38Z`
- `IMPLEMENTATION_COMMIT`: `08de647c4f910cdd22905980511702bd20eeffb1`
- `DATA_CLASS`: synthetic and non-sensitive only

## Kimi

- Route requested: the current official OAuth `kimi-code/k3` headless route in
  an isolated worktree.
- The managed `kimi-codex-worker` preflight rejected stale effort metadata and
  made no project or HOME mutation.
- One direct OAuth attempt ran for the bounded 600-second window, exited `142`,
  and produced an incomplete worktree proposal. It did not close any gate.
- Accepted after Codex review: the strict record/fixture direction and the
  initial fresh-context adapter structure.
- Rejected/replaced: the incomplete test rewrite, any implied authority, and
  every unverified or inconsistent fragment. Codex rewrote the integrated
  tests and retained authority over selection, warrants, filesystem loss, SQL,
  integration, and evidence.
- Kimi version: `0.27.0`.
- Kimi binary SHA-256:
  `550bca0ba6e474f4e0faeadfae03a9294c7c25688670f38ff488ab8cf176d817`.
- Headless wrapper SHA-256:
  `fa900e8233648e712d972b96b7b818b02d81ad74183f94521204e863c1fdd95f`.

## Devstral

- Scope: sanitized, no-tool boundary review; no repository, HOME, credential,
  network, deletion, promotion, or judge authority.
- The exact served-model sentinel passed for `mistral-medium-3-5`.
- The first high-reasoning attempt returned an empty final response and exit
  `45`; it was rejected.
- The bounded no-reasoning retry returned five usable boundary observations:
  normalized path controls; pre-write manifest/hash checks; owned teardown;
  empty active state; and fail-closed one-use warrants.
- Codex independently implemented and tested those boundaries.
- Wrapper SHA-256:
  `7fba7da72e8899633e0a916ad6ac792d3bade1c36bc003f32c29f1e76f0678f3`.

## Vibe

- Version: `2.21.0`.
- Binary SHA-256:
  `49eda5eccca6991033113b0cf30ea7b740078d222d4a74a97d667db14e3da4a4`.
- Scope: read-only adversarial review of the accepted candidate; no edits or
  commands.
- It independently classified all eleven declared P7 vectors as covered and
  found one concrete gap: malformed context dictionaries could surface a raw
  `KeyError` instead of a stable refusal.
- Codex accepted that finding, added fail-closed `validate_context`, and added
  a regression test. No Vibe-authored code entered the implementation.

## Codex

- Authored and owns the integrated strict canonical records, file-byte
  bindings, deterministic maximum-prefix selector, one-use warrant behavior,
  guarded declared-loss harness, CockroachDB schema and serializable state
  transitions, fresh-context byte verification, tests, evidence, and packet.
- Reviewed every external contribution as untrusted; accepted findings are
  represented only through Codex-owned implementation and tests.
- Final mechanical result before packet freeze: 29/29 unit tests and two of
  two fresh-root CockroachDB integration trials passed.

No contributor was used as a judge. Claude and AGY have not authored or shaped
this implementation and remain eligible for the P7 gate.
```

## Embedded file: P7_EVIDENCE_MANIFEST.md

```markdown
# P7 Evidence Manifest

- `UTC_CREATED`: `2026-07-26T01:23:38Z`
- `IMPLEMENTATION_COMMIT`: `08de647c4f910cdd22905980511702bd20eeffb1`
- `PARENT_GATE`: `CK_P6_QUORUM_GREEN`
- `TARGET_GATE`: `CK_P7_RECOVERY_GREEN`

## Mechanical evidence

Commands:

```text
python3 p7-recovery/make_fixtures.py
python3 -m py_compile p7-recovery/*.py
(cd p7-recovery && PYTHONWARNINGS=error python3 -m unittest -v)
python3 p7-recovery/run_integration.py
```

Results:

- 20 canonical fixtures regenerated deterministically.
- Python compilation passed.
- Unit tests: 29/29 PASS in 0.012 seconds.
- CockroachDB integration: two independent fresh roots PASS with identical
  verdict semantics.
- Both trials observed an empty active workspace after declared loss.
- Both selected `cand-p7-alpha`, reconstructed only `docs/notes.md` and
  `src/feature.py`, and verified their actual bytes in a fresh child process.
- Both left the primary and interrupted warrants `CONSUMED`; replay returned
  no update; the interrupted warrant produced zero recovery rows.
- Both retained `data/state.json` as `NO_PROVEN_REPRESENTATION`.
- Both recorded table counts `1 1 2 2 1 1 1` and then dropped the disposable
  database and removed the generated root.

Canonical integration output:

```json
[{"active_files_after_loss":[],"consume_interrupt":true,"consume_main":true,"counts":"1\t1\t2\t2\t1\t1\t1","fresh_context":{"ok":true,"reason":"FRESH_CONTEXT_PASS"},"interrupt_recoveries":"0","interrupt_state":"CONSUMED","label":"p7-trial-a","main_state":"CONSUMED","replay_interrupt_empty":true,"replay_main_empty":true,"selected_candidate":"cand-p7-alpha","successor_files":["docs/notes.md","src/feature.py"],"unrecovered":[{"path":"data/state.json","reason":"NO_PROVEN_REPRESENTATION"}]},{"active_files_after_loss":[],"consume_interrupt":true,"consume_main":true,"counts":"1\t1\t2\t2\t1\t1\t1","fresh_context":{"ok":true,"reason":"FRESH_CONTEXT_PASS"},"interrupt_recoveries":"0","interrupt_state":"CONSUMED","label":"p7-trial-b","main_state":"CONSUMED","replay_interrupt_empty":true,"replay_main_empty":true,"selected_candidate":"cand-p7-alpha","successor_files":["docs/notes.md","src/feature.py"],"unrecovered":[{"path":"data/state.json","reason":"NO_PROVEN_REPRESENTATION"}]}]
```

## Runtime

- CockroachDB version: `v26.2.3`, Darwin arm64.
- CockroachDB binary SHA-256:
  `9e6448bfb19c5811ea565020fc84bf7e1ed8fc0c8236ab8512a48e141018aa5c`.
- Runtime is the already-vendored, checksum-verified P2 binary. P7 performed no
  package installation and used no cloud service or credential.

## Safety and residue

- `gitleaks detect --no-git --source p7-recovery`: exit 0, no leaks found.
- `detect-secrets scan p7-recovery --all-files`: exit 0. Its findings are the
  intentional synthetic SHA-256 fields in canonical fixtures; no credential
  detector produced a verified secret.
- Private-path/content `rg` scan: empty.
- Generated `p7-trial-*` roots after both trials: none.
- Symlinks under `p7-recovery`: none.
- `git diff --check`: clean.
- No HOME, live memory, Qdrant, StateV2, launchd, RunPod, AWS, production data,
  client data, public repository, or later-phase surface was accessed.

## Source hash ledger

```text
13091a711cdafaf4cff3c5a803b992ed81e89c44cf03969384c89c5e03c75573  p7-recovery/fresh_context.py
933592eea49b59679bf2805d5352af6ef071ed7a967311a8531fba1ade69a3b3  p7-recovery/make_fixtures.py
97971f48852e94ada7ecabb7dd0390442b4bde11f38fbdb069b10d396355fd34  p7-recovery/records.py
de6d5d5e80c54714bf990b602345cc21884daaec75fba29b54ff1aa10634503e  p7-recovery/run_integration.py
2833522ee337b0a5c9be9dcc6c0285daf744c4334cdec09aaa112c6a6d2c27a2  p7-recovery/test_records.py
2c70db1248f41344c293a5055f0cedfe33979da341a76dfb6575ddb42a842c52  p7-recovery/migrations/001_recovery.sql
```

The 20 fixture hashes are included in the exact judge packet. The packet also
embeds the complete contract, contribution ledger, source, migration, tests,
fixtures, and raw result summary. No claim is made that unavailable bytes were
recovered or that this is filesystem undelete.
```

## Embedded file: p7-recovery/records.py

```python
"""P7 declared-loss recovery records and non-authoritative in-memory harness.

Synthetic, deterministic, standard library only. This layer implements strict
canonical JSON records (declared manifest, trajectory/loss receipts, surviving
candidates, one-use warrant, recovery decision, promotion/refusal receipt,
unrecovered ledger), normalized relative POSIX path validation, deterministic
candidate eligibility and maximum-proven-prefix selection, and a one-use
in-memory warrant harness in which consumption precedes promotion.

This module has NO deletion, promotion, policy, or gate authority. It performs
no filesystem undelete, no process control, no CockroachDB SQL, no network,
and no credential or HOME access. It reconstructs nothing; it only validates
hash-bound synthetic representations and records deterministic verdicts.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

VERSION = "p7-v1"
MAX_RECORD_BYTES = 65536  # 64 KiB cap on every canonical record

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

WARRANT_STATES = ("ISSUED", "CONSUMED", "INVALID")
DECISIONS = ("PROMOTE", "REFUSE")

# Stable refusal / decision reason codes.
POLICY_VETO = "POLICY_VETO"
TAMPERED_EVIDENCE = "TAMPERED_EVIDENCE"
WARRANT_REPLAY = "WARRANT_REPLAY"
MALFORMED_RECORD = "MALFORMED_RECORD"
UNSAFE_PATH = "UNSAFE_PATH"
UNSUPPORTED_SCHEMA = "UNSUPPORTED_SCHEMA"
STALE_POLICY = "STALE_POLICY"
MISSING_QUORUM = "MISSING_QUORUM"
EXECUTABLE_TEST_FAILED = "EXECUTABLE_TEST_FAILED"
NO_SURVIVING_CANDIDATE = "NO_SURVIVING_CANDIDATE"
MAX_PROVEN_PREFIX = "MAX_PROVEN_PREFIX"

FILE_ENTRY_FIELDS = {"path", "content_hash", "executable", "is_symlink"}
MANIFEST_FIELDS = {"version", "manifest_id", "task_id", "files"}
TRAJECTORY_RECEIPT_FIELDS = {"version", "receipt_id", "task_id", "manifest_hash",
                             "events", "trajectory_hash"}
LOSS_RECEIPT_FIELDS = {"version", "receipt_id", "task_id", "manifest_hash",
                       "lost_paths", "absence_hash"}
CANDIDATE_FIELDS = {"version", "candidate_id", "task_id", "provenance",
                    "source_receipt_hash", "policy_version", "policy_veto",
                    "tampered", "quorum_decision", "prefix_length",
                    "integrity_hash", "declared_paths", "file_hashes",
                    "executable_test"}
EXECUTABLE_TEST_FIELDS = {"test_id", "path", "feature_hash", "passed"}
WARRANT_FIELDS = {"version", "warrant_id", "task_id", "candidate_id",
                  "decision_hash", "state"}
DECISION_FIELDS = {"version", "task_id", "decision", "reason", "candidate_id",
                   "candidates_hash"}
PROMOTION_RECEIPT_FIELDS = {"version", "receipt_id", "task_id", "candidate_id",
                            "warrant_id", "decision_hash", "promoted_paths",
                            "receipt_hash"}
REFUSAL_RECEIPT_FIELDS = {"version", "receipt_id", "task_id", "decision_hash",
                          "reason", "receipt_hash"}
UNRECOVERED_ITEM_FIELDS = {"path", "reason"}
LEDGER_FIELDS = {"version", "ledger_id", "task_id", "manifest_hash",
                 "recovered_paths", "unrecovered_items"}

_MALFORMED_STRUCTURAL = {"UNKNOWN_FIELD", "MISSING_FIELD", "MALFORMED_RECORD",
                         "INVALID_ID", "INVALID_HASH", "RECORD_TOO_LARGE",
                         "NON_CANONICAL_ENCODING"}


class RecoveryError(ValueError):
    """Raised on any closed-failure validation or harness fault."""


class RecoveryInterrupted(RecoveryError):
    """Simulated crash after warrant consumption, before promotion records."""


# ---------------------------------------------------------------------------
# Canonical primitives
# ---------------------------------------------------------------------------

def canonical_json(value: Any) -> bytes:
    """Canonical UTF-8 JSON: sorted keys, no whitespace, 64 KiB cap."""
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise RecoveryError("MALFORMED_RECORD") from exc
    if len(encoded) > MAX_RECORD_BYTES:
        raise RecoveryError("RECORD_TOO_LARGE")
    return encoded


def sha256_hex(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
    return hashlib.sha256(raw).hexdigest()


def require_id(value: Any) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise RecoveryError("INVALID_ID")
    return value


def require_hash(value: Any) -> str:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
        raise RecoveryError("INVALID_HASH")
    return value


def validate_object(record: Any, fields: set[str]) -> None:
    if not isinstance(record, dict):
        raise RecoveryError("MALFORMED_RECORD")
    if set(record) - fields:
        raise RecoveryError("UNKNOWN_FIELD")
    if fields - set(record):
        raise RecoveryError("MISSING_FIELD")


def _require_bool(value: Any) -> bool:
    if not isinstance(value, bool):
        raise RecoveryError("MALFORMED_RECORD")
    return value


def load_canonical(path: str) -> Any:
    """Load a JSON record that must be stored in exact canonical form."""
    with open(path, "rb") as handle:
        raw = handle.read()
    if len(raw) > MAX_RECORD_BYTES:
        raise RecoveryError("RECORD_TOO_LARGE")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RecoveryError("MALFORMED_RECORD") from exc
    if canonical_json(value) != raw:
        raise RecoveryError("NON_CANONICAL_ENCODING")
    return value


# ---------------------------------------------------------------------------
# Normalized relative POSIX path validation
# ---------------------------------------------------------------------------

def validate_relative_path(path: Any) -> str:
    """Accept only normalized relative POSIX paths.

    Rejects absolute paths, empty segments, dot segments, ``..``, NUL bytes,
    and backslashes. This is a pure lexical check; it touches no filesystem.
    """
    if not isinstance(path, str) or not path:
        raise RecoveryError(UNSAFE_PATH)
    if "\x00" in path or "\\" in path:
        raise RecoveryError(UNSAFE_PATH)
    if path.startswith("/"):
        raise RecoveryError(UNSAFE_PATH)
    for segment in path.split("/"):
        if segment in ("", ".", ".."):
            raise RecoveryError(UNSAFE_PATH)
    return path


def validate_file_entry(entry: Any) -> None:
    validate_object(entry, FILE_ENTRY_FIELDS)
    validate_relative_path(entry["path"])
    require_hash(entry["content_hash"])
    # Symlinks and executable content are represented by explicit record
    # flags; either flag set fails closed before any write could be imagined.
    if _require_bool(entry["is_symlink"]) is not False:
        raise RecoveryError(UNSAFE_PATH)
    if _require_bool(entry["executable"]) is not False:
        raise RecoveryError(UNSAFE_PATH)


def declared_paths(manifest: dict[str, Any]) -> list[str]:
    """Sorted declared path set of a validated manifest."""
    validate_manifest(manifest)
    return sorted(entry["path"] for entry in manifest["files"])


# ---------------------------------------------------------------------------
# Record validators
# ---------------------------------------------------------------------------

def validate_manifest(manifest: Any) -> None:
    validate_object(manifest, MANIFEST_FIELDS)
    if manifest["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(manifest["manifest_id"])
    require_id(manifest["task_id"])
    if not isinstance(manifest["files"], list):
        raise RecoveryError("MALFORMED_RECORD")
    seen: set[str] = set()
    for entry in manifest["files"]:
        validate_file_entry(entry)
        if entry["path"] in seen:
            raise RecoveryError("MALFORMED_RECORD")
        seen.add(entry["path"])


def validate_trajectory_receipt(receipt: Any) -> None:
    validate_object(receipt, TRAJECTORY_RECEIPT_FIELDS)
    if receipt["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(receipt["receipt_id"])
    require_id(receipt["task_id"])
    require_hash(receipt["manifest_hash"])
    require_hash(receipt["trajectory_hash"])
    if not isinstance(receipt["events"], list):
        raise RecoveryError("MALFORMED_RECORD")
    previous = ""
    for index, event in enumerate(receipt["events"]):
        validate_object(event, {"sequence", "event", "event_hash"})
        if (isinstance(event["sequence"], bool)
                or not isinstance(event["sequence"], int)
                or event["sequence"] != index):
            raise RecoveryError("NON_CONTIGUOUS_TRAJECTORY")
        if not isinstance(event["event"], str) or not event["event"]:
            raise RecoveryError("MALFORMED_RECORD")
        require_hash(event["event_hash"])
        previous = sha256_hex({"previous": previous, "event": event})
    if previous != receipt["trajectory_hash"]:
        raise RecoveryError("STALE_HASH")


def trajectory_integrity_hash(events: list[dict[str, Any]], prefix_length: int) -> str:
    """Hash binding exactly the contiguous proven prefix of trajectory events."""
    return sha256_hex(events[:prefix_length])


def validate_loss_receipt(receipt: Any, manifest: dict[str, Any] | None = None) -> None:
    validate_object(receipt, LOSS_RECEIPT_FIELDS)
    if receipt["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(receipt["receipt_id"])
    require_id(receipt["task_id"])
    require_hash(receipt["manifest_hash"])
    require_hash(receipt["absence_hash"])
    if not isinstance(receipt["lost_paths"], list):
        raise RecoveryError("MALFORMED_RECORD")
    for path in receipt["lost_paths"]:
        validate_relative_path(path)
    if receipt["absence_hash"] != sha256_hex({"lost_paths": sorted(receipt["lost_paths"]),
                                              "observed": "absent"}):
        raise RecoveryError("STALE_HASH")
    if manifest is not None:
        validate_manifest(manifest)
        if receipt["task_id"] != manifest["task_id"]:
            raise RecoveryError("LOSS_MANIFEST_MISMATCH")
        if receipt["manifest_hash"] != sha256_hex(manifest):
            raise RecoveryError("LOSS_MANIFEST_MISMATCH")
        if sorted(receipt["lost_paths"]) != declared_paths(manifest):
            raise RecoveryError("LOSS_MANIFEST_MISMATCH")


def validate_candidate(candidate: Any) -> None:
    validate_object(candidate, CANDIDATE_FIELDS)
    if candidate["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(candidate["candidate_id"])
    require_id(candidate["task_id"])
    provenance = candidate["provenance"]
    if not isinstance(provenance, dict) or not provenance.get("source"):
        raise RecoveryError("MALFORMED_RECORD")
    if not isinstance(provenance["source"], str):
        raise RecoveryError("MALFORMED_RECORD")
    require_hash(candidate["source_receipt_hash"])
    if not isinstance(candidate["policy_version"], str) or not candidate["policy_version"]:
        raise RecoveryError("MALFORMED_RECORD")
    _require_bool(candidate["policy_veto"])
    _require_bool(candidate["tampered"])
    quorum = candidate["quorum_decision"]
    if not isinstance(quorum, dict):
        raise RecoveryError("MALFORMED_RECORD")
    if quorum.get("decision") not in DECISIONS:
        raise RecoveryError("MALFORMED_RECORD")
    if (isinstance(candidate["prefix_length"], bool)
            or not isinstance(candidate["prefix_length"], int)
            or candidate["prefix_length"] < 0):
        raise RecoveryError("MALFORMED_RECORD")
    require_hash(candidate["integrity_hash"])
    if not isinstance(candidate["declared_paths"], list):
        raise RecoveryError("MALFORMED_RECORD")
    for path in candidate["declared_paths"]:
        validate_relative_path(path)
    if not isinstance(candidate["file_hashes"], dict):
        raise RecoveryError("MALFORMED_RECORD")
    for path, content_hash in candidate["file_hashes"].items():
        validate_relative_path(path)
        require_hash(content_hash)
    if set(candidate["file_hashes"]) != set(candidate["declared_paths"]):
        raise RecoveryError("MALFORMED_RECORD")
    test = candidate["executable_test"]
    validate_object(test, EXECUTABLE_TEST_FIELDS)
    require_id(test["test_id"])
    validate_relative_path(test["path"])
    require_hash(test["feature_hash"])
    _require_bool(test["passed"])


def validate_warrant(warrant: Any) -> None:
    validate_object(warrant, WARRANT_FIELDS)
    if warrant["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(warrant["warrant_id"])
    require_id(warrant["task_id"])
    require_id(warrant["candidate_id"])
    require_hash(warrant["decision_hash"])
    if warrant["state"] not in WARRANT_STATES:
        raise RecoveryError("MALFORMED_RECORD")


def validate_recovery_decision(decision: Any) -> None:
    validate_object(decision, DECISION_FIELDS)
    if decision["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(decision["task_id"])
    if decision["decision"] not in DECISIONS:
        raise RecoveryError("MALFORMED_RECORD")
    if not isinstance(decision["reason"], str) or not decision["reason"]:
        raise RecoveryError("MALFORMED_RECORD")
    if decision["candidate_id"] is not None:
        require_id(decision["candidate_id"])
    if decision["decision"] == "PROMOTE" and decision["candidate_id"] is None:
        raise RecoveryError("MALFORMED_RECORD")
    require_hash(decision["candidates_hash"])


def validate_promotion_receipt(receipt: Any) -> None:
    validate_object(receipt, PROMOTION_RECEIPT_FIELDS)
    if receipt["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(receipt["receipt_id"])
    require_id(receipt["task_id"])
    require_id(receipt["candidate_id"])
    require_id(receipt["warrant_id"])
    require_hash(receipt["decision_hash"])
    require_hash(receipt["receipt_hash"])
    if not isinstance(receipt["promoted_paths"], list):
        raise RecoveryError("MALFORMED_RECORD")
    for path in receipt["promoted_paths"]:
        validate_relative_path(path)


def validate_refusal_receipt(receipt: Any) -> None:
    validate_object(receipt, REFUSAL_RECEIPT_FIELDS)
    if receipt["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(receipt["receipt_id"])
    require_id(receipt["task_id"])
    require_hash(receipt["decision_hash"])
    require_hash(receipt["receipt_hash"])
    if not isinstance(receipt["reason"], str) or not receipt["reason"]:
        raise RecoveryError("MALFORMED_RECORD")


def validate_unrecovered_ledger(ledger: Any) -> None:
    validate_object(ledger, LEDGER_FIELDS)
    if ledger["version"] != VERSION:
        raise RecoveryError(UNSUPPORTED_SCHEMA)
    require_id(ledger["ledger_id"])
    require_id(ledger["task_id"])
    require_hash(ledger["manifest_hash"])
    if not isinstance(ledger["recovered_paths"], list):
        raise RecoveryError("MALFORMED_RECORD")
    for path in ledger["recovered_paths"]:
        validate_relative_path(path)
    if not isinstance(ledger["unrecovered_items"], list):
        raise RecoveryError("MALFORMED_RECORD")
    for item in ledger["unrecovered_items"]:
        validate_object(item, UNRECOVERED_ITEM_FIELDS)
        validate_relative_path(item["path"])
        if not isinstance(item["reason"], str) or not item["reason"]:
            raise RecoveryError("MALFORMED_RECORD")


# ---------------------------------------------------------------------------
# Deterministic eligibility and selection
# ---------------------------------------------------------------------------

def _structural_code(exc: RecoveryError) -> str:
    code = str(exc)
    if code == UNSUPPORTED_SCHEMA:
        return UNSUPPORTED_SCHEMA
    if code == UNSAFE_PATH:
        return UNSAFE_PATH
    return MALFORMED_RECORD


def validate_context(context: Any) -> None:
    try:
        validate_object(context, {"manifest", "trajectory_receipt",
                                  "policy_version", "quorum_decision_hash"})
        validate_manifest(context["manifest"])
        validate_trajectory_receipt(context["trajectory_receipt"])
        if (not isinstance(context["policy_version"], str)
                or not context["policy_version"]):
            raise RecoveryError(MALFORMED_RECORD)
        require_hash(context["quorum_decision_hash"])
    except (RecoveryError, KeyError, TypeError) as exc:
        raise RecoveryError(MALFORMED_RECORD) from exc


def check_eligibility(candidate: Any, context: dict[str, Any]) -> str | None:
    """Return None if the candidate is admissible, else a stable reason code.

    Checks, in fixed order: exact schema/structure, provenance, source receipt
    binding, explicit policy veto, policy version, tamper flag, P6 quorum
    decision binding, contiguous-prefix integrity binding, declared-path set
    binding, and the executable-test declaration. Pure and deterministic.
    """
    try:
        validate_context(context)
        validate_candidate(candidate)
        canonical_json(candidate)  # enforce the 64 KiB record cap
    except RecoveryError as exc:
        return _structural_code(exc)

    manifest = context["manifest"]
    trajectory = context["trajectory_receipt"]

    if candidate["task_id"] != manifest["task_id"]:
        return TAMPERED_EVIDENCE
    if candidate["source_receipt_hash"] != sha256_hex(trajectory):
        return TAMPERED_EVIDENCE
    if candidate["policy_veto"]:
        return POLICY_VETO
    if candidate["policy_version"] != context["policy_version"]:
        return STALE_POLICY
    if candidate["tampered"]:
        return TAMPERED_EVIDENCE
    quorum = candidate["quorum_decision"]
    if quorum["decision"] != "PROMOTE":
        return MISSING_QUORUM
    if sha256_hex(quorum) != context["quorum_decision_hash"]:
        return MISSING_QUORUM
    events = trajectory["events"]
    if candidate["prefix_length"] > len(events):
        return TAMPERED_EVIDENCE
    if candidate["integrity_hash"] != trajectory_integrity_hash(events,
                                                                candidate["prefix_length"]):
        return TAMPERED_EVIDENCE
    declared = set(declared_paths(manifest))
    if any(path not in declared for path in candidate["declared_paths"]):
        return UNSAFE_PATH
    manifest_hashes = {entry["path"]: entry["content_hash"]
                       for entry in manifest["files"]}
    if any(candidate["file_hashes"][path] != manifest_hashes[path]
           for path in candidate["declared_paths"]):
        return TAMPERED_EVIDENCE
    test_path = candidate["executable_test"]["path"]
    if (test_path not in candidate["file_hashes"]
            or candidate["executable_test"]["feature_hash"]
            != candidate["file_hashes"][test_path]):
        return EXECUTABLE_TEST_FAILED
    if candidate["executable_test"]["passed"] is not True:
        return EXECUTABLE_TEST_FAILED
    return None


def _candidates_hash(candidates: list[Any]) -> str:
    """Order-independent hash over every canonically serializable candidate."""
    hashes = []
    for candidate in candidates:
        try:
            hashes.append(sha256_hex(candidate))
        except RecoveryError:
            continue
    return sha256_hex(sorted(hashes))


def make_decision(task_id: str, decision: str, reason: str,
                  candidate_id: str | None, candidates: list[Any]) -> dict[str, Any]:
    record = {
        "version": VERSION,
        "task_id": task_id,
        "decision": decision,
        "reason": reason,
        "candidate_id": candidate_id,
        "candidates_hash": _candidates_hash(candidates),
    }
    validate_recovery_decision(record)
    canonical_json(record)
    return record


def select_candidate(candidates: list[Any], context: dict[str, Any]) -> dict[str, Any]:
    """Deterministically select the longest contiguous proven prefix.

    Only candidates passing every eligibility binding are admitted. Among
    admitted candidates the longest ``prefix_length`` wins; ties break by
    canonical candidate ID (lexicographic minimum). The selector never
    invents or merges bytes. Returns a recovery decision record.
    """
    if not isinstance(candidates, list):
        raise RecoveryError("MALFORMED_RECORD")
    validate_context(context)
    task_id = context["manifest"]["task_id"]
    admitted = [candidate for candidate in candidates
                if check_eligibility(candidate, context) is None]
    if not admitted:
        return make_decision(task_id, "REFUSE", NO_SURVIVING_CANDIDATE, None, candidates)
    chosen = sorted(admitted,
                    key=lambda c: (-c["prefix_length"], c["candidate_id"]))[0]
    return make_decision(task_id, "PROMOTE", MAX_PROVEN_PREFIX,
                         chosen["candidate_id"], candidates)


# ---------------------------------------------------------------------------
# One-use warrant + non-authoritative in-memory harness
# ---------------------------------------------------------------------------

def make_warrant(warrant_id: str, task_id: str, candidate_id: str,
                 decision: dict[str, Any]) -> dict[str, Any]:
    """Issue a one-use warrant bound to an exact recovery decision."""
    validate_recovery_decision(decision)
    warrant = {
        "version": VERSION,
        "warrant_id": warrant_id,
        "task_id": task_id,
        "candidate_id": candidate_id,
        "decision_hash": sha256_hex(decision),
        "state": "ISSUED",
    }
    validate_warrant(warrant)
    canonical_json(warrant)
    return warrant


def _seal_receipt(body: dict[str, Any], fields: set[str]) -> dict[str, Any]:
    receipt_hash = sha256_hex(body)
    receipt = dict(body)
    receipt["receipt_id"] = "rcpt-" + receipt_hash[:32]
    receipt["receipt_hash"] = receipt_hash
    validate_object(receipt, fields)
    canonical_json(receipt)
    return receipt


def build_promotion_receipt(decision: dict[str, Any], warrant: dict[str, Any],
                            promoted_paths: list[str]) -> dict[str, Any]:
    validate_recovery_decision(decision)
    validate_warrant(warrant)
    body = {
        "version": VERSION,
        "task_id": decision["task_id"],
        "candidate_id": warrant["candidate_id"],
        "warrant_id": warrant["warrant_id"],
        "decision_hash": sha256_hex(decision),
        "promoted_paths": sorted(promoted_paths),
    }
    receipt = _seal_receipt(body, PROMOTION_RECEIPT_FIELDS)
    validate_promotion_receipt(receipt)
    return receipt


def build_refusal_receipt(decision: dict[str, Any]) -> dict[str, Any]:
    validate_recovery_decision(decision)
    body = {
        "version": VERSION,
        "task_id": decision["task_id"],
        "decision_hash": sha256_hex(decision),
        "reason": decision["reason"],
    }
    receipt = _seal_receipt(body, REFUSAL_RECEIPT_FIELDS)
    validate_refusal_receipt(receipt)
    return receipt


def make_unrecovered_ledger(ledger_id: str, manifest: dict[str, Any],
                            recovered_paths: list[str]) -> dict[str, Any]:
    """Ledger of declared paths no surviving authorized representation covers."""
    validate_manifest(manifest)
    declared = set(declared_paths(manifest))
    recovered = sorted(recovered_paths)
    for path in recovered:
        validate_relative_path(path)
        if path not in declared:
            raise RecoveryError(UNSAFE_PATH)
    ledger = {
        "version": VERSION,
        "ledger_id": ledger_id,
        "task_id": manifest["task_id"],
        "manifest_hash": sha256_hex(manifest),
        "recovered_paths": recovered,
        "unrecovered_items": [
            {"path": path, "reason": "NO_PROVEN_REPRESENTATION"}
            for path in sorted(declared - set(recovered))
        ],
    }
    validate_unrecovered_ledger(ledger)
    canonical_json(ledger)
    return ledger


class RecoveryHarness:
    """Non-authoritative in-memory one-use warrant harness.

    Consumption precedes promotion: an ISSUED warrant is marked CONSUMED
    before the promotion receipt is recorded. An interruption after
    consumption leaves the warrant CONSUMED (never replayable) and records
    no promotion. A second use refuses with WARRANT_REPLAY. This models the
    serializable consume-then-promote contract without any database, process,
    or filesystem authority.
    """

    def __init__(self) -> None:
        self._warrants: dict[str, dict[str, Any]] = {}
        self._promotions: dict[str, dict[str, Any]] = {}
        self._refusals: list[dict[str, Any]] = []

    def register_warrant(self, warrant: dict[str, Any]) -> None:
        validate_warrant(warrant)
        canonical_json(warrant)
        if warrant["warrant_id"] in self._warrants:
            raise RecoveryError(WARRANT_REPLAY)
        self._warrants[warrant["warrant_id"]] = json.loads(canonical_json(warrant))

    def warrant_state(self, warrant_id: str) -> str | None:
        warrant = self._warrants.get(warrant_id)
        return warrant["state"] if warrant else None

    def promotion(self, task_id: str) -> dict[str, Any] | None:
        return self._promotions.get(task_id)

    def refusals(self) -> list[dict[str, Any]]:
        return list(self._refusals)

    def recover(self, decision: dict[str, Any], warrant_id: str,
                promoted_paths: list[str] | None = None,
                fault: str | None = None) -> dict[str, Any]:
        """Apply a recovery decision against a one-use warrant.

        REFUSE decisions never touch the warrant. PROMOTE decisions consume
        the warrant first; fault="interrupt" raises RecoveryInterrupted after
        consumption with no promotion recorded. Returns the promotion or
        refusal receipt.
        """
        validate_recovery_decision(decision)
        canonical_json(decision)
        if decision["decision"] == "REFUSE":
            receipt = build_refusal_receipt(decision)
            self._refusals.append(receipt)
            return receipt

        warrant = self._warrants.get(warrant_id)
        if warrant is None:
            raise RecoveryError("UNKNOWN_WARRANT")
        if warrant["state"] != "ISSUED":
            receipt = build_refusal_receipt(make_decision(
                decision["task_id"], "REFUSE", WARRANT_REPLAY, None, []))
            self._refusals.append(receipt)
            return receipt
        if (warrant["task_id"] != decision["task_id"]
                or warrant["candidate_id"] != decision["candidate_id"]
                or warrant["decision_hash"] != sha256_hex(decision)):
            receipt = build_refusal_receipt(make_decision(
                decision["task_id"], "REFUSE", TAMPERED_EVIDENCE, None, []))
            self._refusals.append(receipt)
            return receipt

        # Consumption strictly precedes promotion.
        warrant["state"] = "CONSUMED"
        if fault == "interrupt":
            raise RecoveryInterrupted("RECOVERY_INTERRUPTED")
        if fault is not None:
            raise RecoveryError("UNKNOWN_FAULT")

        receipt = build_promotion_receipt(decision, warrant,
                                          promoted_paths or [])
        self._promotions[decision["task_id"]] = receipt
        return receipt
```

## Embedded file: p7-recovery/make_fixtures.py

```python
"""Generate deterministic synthetic P7 fixtures into p7-recovery/fixtures/.

All contents are synthetic and non-sensitive. Re-running this script always
produces byte-identical canonical JSON files.
"""
from __future__ import annotations

import copy
import os

import records as rc

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

TASK_ID = "task-p7-synthetic-001"
POLICY_VERSION = "policy-v1"
ALPHA_ID = "cand-p7-alpha"
BETA_ID = "cand-p7-beta"

# Synthetic declared workspace contents (never written to disk).
FILE_CONTENTS = {
    "data/state.json": b'{"synthetic":"state"}',
    "docs/notes.md": b"# synthetic notes\n",
    "src/feature.py": b"# synthetic feature\n",
}


def build_manifest() -> dict:
    return {
        "version": rc.VERSION,
        "manifest_id": "manifest-p7-001",
        "task_id": TASK_ID,
        "files": [
            {"path": path, "content_hash": rc.sha256_hex(content),
             "executable": False, "is_symlink": False}
            for path, content in sorted(FILE_CONTENTS.items())
        ],
    }


def build_events() -> list[dict]:
    names = ["DECLARE", "RECORD", "EVALUATE"]
    return [
        {"sequence": index, "event": name,
         "event_hash": rc.sha256_hex({"sequence": index, "event": name})}
        for index, name in enumerate(names)
    ]


def build_trajectory_receipt(manifest: dict, events: list[dict]) -> dict:
    previous = ""
    for event in events:
        previous = rc.sha256_hex({"previous": previous, "event": event})
    return {
        "version": rc.VERSION,
        "receipt_id": "rcpt-trajectory-p7-001",
        "task_id": TASK_ID,
        "manifest_hash": rc.sha256_hex(manifest),
        "events": events,
        "trajectory_hash": previous,
    }


def build_loss_receipt(manifest: dict) -> dict:
    lost = rc.declared_paths(manifest)
    return {
        "version": rc.VERSION,
        "receipt_id": "rcpt-loss-p7-001",
        "task_id": TASK_ID,
        "manifest_hash": rc.sha256_hex(manifest),
        "lost_paths": lost,
        "absence_hash": rc.sha256_hex({"lost_paths": sorted(lost),
                                       "observed": "absent"}),
    }


def build_quorum_decision() -> dict:
    """Synthetic P6-style quorum decision record (PROMOTE, 3 of 5 lanes)."""
    votes_hash = rc.sha256_hex([rc.sha256_hex("vote-%d" % idx) for idx in range(5)])
    return {
        "version": "p6-v1",
        "task_id": TASK_ID,
        "candidate_id": "cand-p6-synthetic-001",
        "critical": False,
        "threshold": 3,
        "approvals": 3,
        "refusals": 2,
        "decision": "PROMOTE",
        "reason": "QUORUM_PASS",
        "dissent": [],
        "votes_hash": votes_hash,
    }


def build_candidate(candidate_id: str, prefix_length: int,
                    declared: list[str], events: list[dict],
                    trajectory: dict, quorum: dict) -> dict:
    file_hashes = {path: rc.sha256_hex(FILE_CONTENTS[path]) for path in declared}
    candidate = {
        "version": rc.VERSION,
        "candidate_id": candidate_id,
        "task_id": TASK_ID,
        "provenance": {"source": "p6-quorum-synthetic", "builder": "kimi"},
        "source_receipt_hash": rc.sha256_hex(trajectory),
        "policy_version": POLICY_VERSION,
        "policy_veto": False,
        "tampered": False,
        "quorum_decision": quorum,
        "prefix_length": prefix_length,
        "integrity_hash": rc.trajectory_integrity_hash(events, prefix_length),
        "declared_paths": declared,
        "file_hashes": file_hashes,
        "executable_test": {
            "test_id": "exectest-" + candidate_id,
            "path": "src/feature.py",
            "feature_hash": file_hashes["src/feature.py"],
            "passed": True,
        },
    }
    rc.validate_candidate(candidate)
    return candidate


def refusal_candidates(alpha: dict) -> dict[str, dict]:
    """One fixture candidate per refusal vector, each drifting exactly one binding."""
    variants = {}

    vetoed = copy.deepcopy(alpha)
    vetoed["candidate_id"] = "cand-p7-veto"
    vetoed["policy_veto"] = True
    variants["policy-veto"] = vetoed

    tampered = copy.deepcopy(alpha)
    tampered["candidate_id"] = "cand-p7-tampered"
    tampered["tampered"] = True
    variants["tampered"] = tampered

    bad_schema = copy.deepcopy(alpha)
    bad_schema["candidate_id"] = "cand-p7-badschema"
    bad_schema["version"] = "p7-v0"
    variants["unsupported-schema"] = bad_schema

    stale = copy.deepcopy(alpha)
    stale["candidate_id"] = "cand-p7-stalepolicy"
    stale["policy_version"] = "policy-v0"
    variants["stale-policy"] = stale

    no_quorum = copy.deepcopy(alpha)
    no_quorum["candidate_id"] = "cand-p7-noquorum"
    no_quorum["quorum_decision"] = dict(no_quorum["quorum_decision"],
                                        decision="REFUSE", reason="QUORUM_MISSING")
    variants["missing-quorum"] = no_quorum

    failed_test = copy.deepcopy(alpha)
    failed_test["candidate_id"] = "cand-p7-failedtest"
    failed_test["executable_test"] = dict(failed_test["executable_test"],
                                          passed=False)
    variants["failed-exec-test"] = failed_test

    unsafe = copy.deepcopy(alpha)
    unsafe["candidate_id"] = "cand-p7-unsafepath"
    unsafe["declared_paths"] = list(unsafe["declared_paths"]) + ["secret/undeclared.txt"]
    unsafe["file_hashes"]["secret/undeclared.txt"] = rc.sha256_hex(
        b"synthetic undeclared bytes")
    variants["unsafe-path"] = unsafe

    return variants


def write_fixture(name: str, value) -> None:
    path = os.path.join(FIXTURE_DIR, name + ".json")
    with open(path, "wb") as handle:
        handle.write(rc.canonical_json(value))


def build_context(manifest: dict, trajectory: dict, quorum: dict) -> dict:
    return {
        "manifest": manifest,
        "trajectory_receipt": trajectory,
        "policy_version": POLICY_VERSION,
        "quorum_decision_hash": rc.sha256_hex(quorum),
    }


def main() -> None:
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    manifest = build_manifest()
    events = build_events()
    trajectory = build_trajectory_receipt(manifest, events)
    loss = build_loss_receipt(manifest)
    quorum = build_quorum_decision()
    context = build_context(manifest, trajectory, quorum)

    alpha = build_candidate(ALPHA_ID, 3, ["docs/notes.md", "src/feature.py"],
                            events, trajectory, quorum)
    beta = build_candidate(BETA_ID, 2, ["src/feature.py"],
                           events, trajectory, quorum)

    write_fixture("manifest", manifest)
    write_fixture("trajectory-receipt", trajectory)
    write_fixture("loss-receipt", loss)
    write_fixture("quorum-decision", quorum)
    write_fixture("candidate-alpha", alpha)
    write_fixture("candidate-beta", beta)
    for name, candidate in refusal_candidates(alpha).items():
        write_fixture("candidate-" + name, candidate)

    decision_promote = rc.select_candidate([alpha, beta], context)
    write_fixture("decision-promote", decision_promote)

    refusing = list(refusal_candidates(alpha).values())
    decision_refuse = rc.select_candidate(refusing, context)
    write_fixture("decision-no-surviving", decision_refuse)

    warrant = rc.make_warrant("warrant-p7-001", TASK_ID, ALPHA_ID, decision_promote)
    write_fixture("warrant-issued", warrant)

    harness = rc.RecoveryHarness()
    harness.register_warrant(warrant)
    promotion = harness.recover(decision_promote, "warrant-p7-001",
                                promoted_paths=alpha["declared_paths"])
    write_fixture("promotion-receipt", promotion)
    write_fixture("refusal-receipt-no-surviving", rc.build_refusal_receipt(decision_refuse))

    ledger = rc.make_unrecovered_ledger("ledger-p7-001", manifest,
                                        alpha["declared_paths"])
    write_fixture("unrecovered-ledger", ledger)
    write_fixture("feature-file", {
        "path": "src/feature.py",
        "content_hash": rc.sha256_hex(FILE_CONTENTS["src/feature.py"]),
    })

    print("wrote %d fixtures to %s" % (len(os.listdir(FIXTURE_DIR)), FIXTURE_DIR))


if __name__ == "__main__":
    main()
```

## Embedded file: p7-recovery/fresh_context.py

```python
"""P7 fresh-context continuation harness plumbing.

Accepts only a canonical recovery decision record plus the promoted surviving
candidate record, and deterministically verifies the expected synthetic
feature file binding. There is no hidden session state: the expected feature
content is a pure function of (task_id, candidate_id) already bound inside
the two input records, and verification recomputes it from those inputs
alone. Standard library only; no filesystem writes, no network, no authority.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from records import (
    RecoveryError, load_canonical, sha256_hex, validate_candidate,
    validate_recovery_decision,
)

def verify_continuation(decision: Any, candidate: Any) -> tuple[bool, str]:
    """Verify a fresh-context continuation against only the two inputs.

    Returns (ok, stable_reason). Fails closed on any malformed input,
    non-promotion decision, record mismatch, or feature binding drift.
    """
    try:
        validate_recovery_decision(decision)
        validate_candidate(candidate)
    except RecoveryError as exc:
        return False, str(exc)
    if decision["decision"] != "PROMOTE":
        return False, "NOT_A_PROMOTION"
    if decision["task_id"] != candidate["task_id"]:
        return False, "TASK_MISMATCH"
    if decision["candidate_id"] != candidate["candidate_id"]:
        return False, "CANDIDATE_MISMATCH"
    test = candidate["executable_test"]
    if test["passed"] is not True:
        return False, "EXECUTABLE_TEST_FAILED"
    if test["path"] not in candidate["file_hashes"]:
        return False, "FEATURE_MISMATCH"
    if test["feature_hash"] != candidate["file_hashes"][test["path"]]:
        return False, "FEATURE_MISMATCH"
    return True, "FRESH_CONTEXT_PASS"


def verify_workspace(decision: Any, candidate: Any,
                     workspace: str | Path) -> tuple[bool, str]:
    """Verify the actual successor bytes from explicit record + workspace inputs."""
    ok, reason = verify_continuation(decision, candidate)
    if not ok:
        return ok, reason
    root = Path(workspace).resolve()
    test_path = candidate["executable_test"]["path"]
    target = root.joinpath(*test_path.split("/"))
    try:
        resolved = target.resolve(strict=True)
    except (FileNotFoundError, RuntimeError, OSError):
        return False, "FEATURE_MISSING"
    if root not in resolved.parents or target.is_symlink() or not target.is_file():
        return False, "UNSAFE_PATH"
    if sha256_hex(target.read_bytes()) != candidate["executable_test"]["feature_hash"]:
        return False, "FEATURE_MISMATCH"
    return True, "FRESH_CONTEXT_PASS"


def main(argv: list[str] | None = None) -> int:
    """CLI: fresh_context.py <decision.json> <candidate.json> <workspace>.

    Both files must be stored in exact canonical form; anything else is
    rejected before verification. Prints a deterministic verdict line.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 3:
        print("usage: fresh_context.py <decision.json> <candidate.json> <workspace>")
        return 2
    try:
        decision = load_canonical(args[0])
        candidate = load_canonical(args[1])
    except RecoveryError as exc:
        print(json.dumps({"ok": False, "reason": str(exc)}, sort_keys=True))
        return 1
    ok, reason = verify_workspace(decision, candidate, args[2])
    print(json.dumps({"ok": ok, "reason": reason}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

## Embedded file: p7-recovery/run_integration.py

```python
#!/usr/bin/env python3
"""Two fresh-root declared-loss and CockroachDB recovery trials."""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

import fresh_context as fc
import make_fixtures as fx
import records as rec

BASE = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
BIN = next(path for path in BASE.glob("p2-cleanroom/vendor/**/cockroach")
           if "darwin" in str(path))
P3_MIGRATION = BASE / "p3-ledger/migrations/001_ledger.sql"
P7_MIGRATION = HERE / "migrations/001_recovery.sql"
FIXTURES = HERE / "fixtures"


def quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def sql(port: int, statement: str, database: str | None = None,
        expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    args = [str(BIN), "sql", "--insecure", f"--host=127.0.0.1:{port}"]
    if database:
        args.append(f"--database={database}")
    args += ["-e", statement]
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False)
    if expect_ok and result.returncode != 0:
        raise RuntimeError(result.stdout)
    return result


def apply_file(port: int, database: str, path: Path) -> None:
    subprocess.run(
        [str(BIN), "sql", "--insecure", f"--host=127.0.0.1:{port}",
         f"--database={database}", f"--file={path}"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def fixture(name: str):
    return rec.load_canonical(str(FIXTURES / (name + ".json")))


def safe_target(root: Path, relative: str) -> Path:
    rec.validate_relative_path(relative)
    target = root.joinpath(*relative.split("/"))
    if root.resolve() not in target.resolve(strict=False).parents:
        raise rec.RecoveryError(rec.UNSAFE_PATH)
    return target


def write_bytes(root: Path, relative: str, payload: bytes) -> None:
    target = safe_target(root, relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        raise rec.RecoveryError(rec.UNSAFE_PATH)
    with target.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def tree_files(root: Path) -> list[str]:
    files = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise rec.RecoveryError(rec.UNSAFE_PATH)
        if path.is_file():
            files.append(path.relative_to(root).as_posix())
    return sorted(files)


def verify_active(root: Path, manifest: dict) -> None:
    expected = rec.declared_paths(manifest)
    if tree_files(root) != expected:
        raise rec.RecoveryError("MANIFEST_DRIFT")
    expected_hashes = {entry["path"]: entry["content_hash"]
                       for entry in manifest["files"]}
    for relative in expected:
        target = safe_target(root, relative)
        if target.is_symlink() or rec.sha256_hex(target.read_bytes()) != expected_hashes[relative]:
            raise rec.RecoveryError("MANIFEST_DRIFT")


def stop_owned(process: subprocess.Popen[str]) -> None:
    process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    if process.returncode is None:
        raise RuntimeError("owned process did not stop")


def observe_loss(active: Path, manifest: dict,
                 owned: subprocess.Popen[str]) -> dict:
    verify_active(active, manifest)
    stop_owned(owned)
    for relative in rec.declared_paths(manifest):
        target = safe_target(active, relative)
        if target.is_symlink() or not target.is_file():
            raise rec.RecoveryError("MANIFEST_DRIFT")
        target.unlink()
    if tree_files(active):
        raise rec.RecoveryError("LOSS_RESIDUE")
    receipt = fixture("loss-receipt")
    rec.validate_loss_receipt(receipt, manifest)
    return receipt


def last_data(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def trial(label: str, port: int, http_port: int) -> dict[str, object]:
    root = Path(tempfile.mkdtemp(prefix=f"{label}.", dir=HERE))
    active = root / "active"
    surviving = root / "surviving"
    successor = root / "successor"
    evidence = root / "evidence"
    fake_home = root / "empty-home"
    for path in (active, surviving, successor, evidence, fake_home):
        path.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(fake_home)
    log_handle = None
    database_process = None
    owned_process = None
    try:
        manifest = fixture("manifest")
        for relative, payload in fx.FILE_CONTENTS.items():
            write_bytes(active, relative, payload)

        alpha = fixture("candidate-alpha")
        beta = fixture("candidate-beta")
        for relative, content_hash in alpha["file_hashes"].items():
            payload = fx.FILE_CONTENTS[relative]
            if rec.sha256_hex(payload) != content_hash:
                raise rec.RecoveryError(rec.TAMPERED_EVIDENCE)
            write_bytes(surviving, "objects/" + content_hash, payload)

        owned_process = subprocess.Popen(
            ["/usr/bin/env", "python3", "-c", "import time; time.sleep(300)"],
            cwd=active, env=env, text=True, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

        log_handle = (root / "cockroach.log").open("w", encoding="utf-8")
        database_process = subprocess.Popen(
            [str(BIN), "start-single-node", "--insecure", f"--store={root / 'store'}",
             f"--listen-addr=127.0.0.1:{port}",
             f"--http-addr=127.0.0.1:{http_port}"],
            stdout=log_handle, stderr=subprocess.STDOUT, env=env, text=True)
        for _ in range(30):
            if sql(port, "SELECT 1", expect_ok=False).returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("CockroachDB did not become ready")

        database = "p7recovery"
        sql(port, f"CREATE DATABASE {database}")
        apply_file(port, database, P3_MIGRATION)
        apply_file(port, database, P7_MIGRATION)

        declared = {"scope": "synthetic-p7", "state": "declared-loss"}
        sql(port,
            "INSERT INTO tasks VALUES "
            "('task-p7-synthetic-001','p7-v1',decode(%s,'hex'),%s::JSONB,"
            "'2026-07-26 00:00:00+00')" %
            (quote(rec.sha256_hex(declared)), quote(json.dumps(declared))), database)

        loss = observe_loss(active, manifest, owned_process)
        owned_process = None
        (evidence / "loss-receipt.json").write_bytes(rec.canonical_json(loss))

        context = fx.build_context(manifest, fixture("trajectory-receipt"),
                                   fixture("quorum-decision"))
        decision = rec.select_candidate([beta, alpha], context)
        if decision != fixture("decision-promote"):
            raise rec.RecoveryError("DECISION_DRIFT")
        warrant = fixture("warrant-issued")
        promotion = fixture("promotion-receipt")
        ledger = fixture("unrecovered-ledger")

        sql(port, "INSERT INTO p7_manifests VALUES (%s,%s,%s::JSONB,decode(%s,'hex'))" % (
            quote(manifest["manifest_id"]), quote(manifest["task_id"]),
            quote(json.dumps(manifest)), quote(rec.sha256_hex(manifest))), database)
        sql(port, "INSERT INTO p7_loss_receipts VALUES (%s,%s,%s,%s::JSONB,decode(%s,'hex'))" % (
            quote(loss["receipt_id"]), quote(loss["task_id"]),
            quote(manifest["manifest_id"]), quote(json.dumps(loss)),
            quote(rec.sha256_hex(loss))), database)
        for candidate in (alpha, beta):
            sql(port, "INSERT INTO p7_recovery_candidates VALUES "
                "(%s,%s,decode(%s,'hex'),%s::JSONB,decode(%s,'hex'))" % (
                    quote(candidate["candidate_id"]), quote(candidate["task_id"]),
                    quote(rec.sha256_hex(loss)), quote(json.dumps(candidate)),
                    quote(rec.sha256_hex(candidate))), database)
        sql(port, "INSERT INTO p7_warrants VALUES (%s,%s,%s,decode(%s,'hex'),%s,%s::JSONB)" % (
            quote(warrant["warrant_id"]), quote(warrant["task_id"]),
            quote(warrant["candidate_id"]), quote(warrant["decision_hash"]),
            quote(warrant["state"]), quote(json.dumps(warrant))), database)

        interrupt_id = "warrant-p7-interrupt"
        interrupt = dict(warrant, warrant_id=interrupt_id)
        sql(port, "INSERT INTO p7_warrants VALUES (%s,%s,%s,decode(%s,'hex'),'ISSUED',%s::JSONB)" % (
            quote(interrupt_id), quote(warrant["task_id"]), quote(warrant["candidate_id"]),
            quote(warrant["decision_hash"]), quote(json.dumps(interrupt))), database)
        consumed_interrupt = sql(
            port, "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
            "UPDATE p7_warrants SET state='CONSUMED' WHERE warrant_id=%s AND state='ISSUED' "
            "RETURNING state;COMMIT;" % quote(interrupt_id), database).stdout
        replay_interrupt = sql(
            port, "UPDATE p7_warrants SET state='CONSUMED' WHERE warrant_id=%s "
            "AND state='ISSUED' RETURNING state" % quote(interrupt_id), database).stdout

        consumed = sql(
            port, "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
            "UPDATE p7_warrants SET state='CONSUMED' WHERE warrant_id=%s AND state='ISSUED' "
            "RETURNING state;COMMIT;" % quote(warrant["warrant_id"]), database).stdout

        for relative, content_hash in alpha["file_hashes"].items():
            blob = safe_target(surviving, "objects/" + content_hash)
            payload = blob.read_bytes()
            if rec.sha256_hex(payload) != content_hash:
                raise rec.RecoveryError(rec.TAMPERED_EVIDENCE)
            write_bytes(successor, relative, payload)

        for relative, content_hash in alpha["file_hashes"].items():
            if rec.sha256_hex(safe_target(successor, relative).read_bytes()) != content_hash:
                raise rec.RecoveryError(rec.TAMPERED_EVIDENCE)

        fresh = subprocess.run(
            ["/usr/bin/env", "python3", str(HERE / "fresh_context.py"),
             str(FIXTURES / "decision-promote.json"),
             str(FIXTURES / "candidate-alpha.json"), str(successor)],
            cwd=HERE, env=env, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=False)
        if fresh.returncode != 0 or '"ok": true' not in fresh.stdout:
            raise rec.RecoveryError("FRESH_CONTEXT_FAILED")

        sql(port,
            "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
            "INSERT INTO p7_recoveries VALUES "
            "('recovery-p7-001',%s,%s,%s,%s::JSONB,decode(%s,'hex'));"
            "INSERT INTO p7_recovery_receipts VALUES "
            "(%s,'recovery-p7-001',%s::JSONB,decode(%s,'hex'));COMMIT;" % (
                quote(decision["task_id"]), quote(decision["candidate_id"]),
                quote(warrant["warrant_id"]), quote(json.dumps(decision)),
                quote(rec.sha256_hex(decision)), quote(promotion["receipt_id"]),
                quote(json.dumps(promotion)), quote(promotion["receipt_hash"])), database)
        sql(port, "INSERT INTO p7_unrecovered_ledgers VALUES "
            "(%s,%s,%s::JSONB,decode(%s,'hex'))" % (
                quote(ledger["ledger_id"]), quote(ledger["task_id"]),
                quote(json.dumps(ledger)), quote(rec.sha256_hex(ledger))), database)

        replay_main = sql(
            port, "UPDATE p7_warrants SET state='CONSUMED' WHERE warrant_id=%s "
            "AND state='ISSUED' RETURNING state" % quote(warrant["warrant_id"]), database).stdout
        counts = last_data(sql(port,
            "SELECT (SELECT count(*) FROM p7_manifests),"
            "(SELECT count(*) FROM p7_loss_receipts),"
            "(SELECT count(*) FROM p7_recovery_candidates),"
            "(SELECT count(*) FROM p7_warrants),"
            "(SELECT count(*) FROM p7_recoveries),"
            "(SELECT count(*) FROM p7_recovery_receipts),"
            "(SELECT count(*) FROM p7_unrecovered_ledgers)", database).stdout)
        interrupt_state = last_data(sql(
            port, "SELECT state FROM p7_warrants WHERE warrant_id=%s" %
            quote(interrupt_id), database).stdout)
        interrupt_recoveries = last_data(sql(
            port, "SELECT count(*) FROM p7_recoveries WHERE warrant_id=%s" %
            quote(interrupt_id), database).stdout)
        main_state = last_data(sql(
            port, "SELECT state FROM p7_warrants WHERE warrant_id=%s" %
            quote(warrant["warrant_id"]), database).stdout)
        sql(port, f"DROP DATABASE {database} CASCADE")

        return {
            "label": label,
            "active_files_after_loss": tree_files(active),
            "successor_files": tree_files(successor),
            "selected_candidate": decision["candidate_id"],
            "fresh_context": json.loads(fresh.stdout),
            "consume_main": "CONSUMED" in consumed,
            "consume_interrupt": "CONSUMED" in consumed_interrupt,
            "replay_main_empty": "CONSUMED" not in replay_main,
            "replay_interrupt_empty": "CONSUMED" not in replay_interrupt,
            "main_state": main_state,
            "interrupt_state": interrupt_state,
            "interrupt_recoveries": interrupt_recoveries,
            "counts": counts,
            "unrecovered": ledger["unrecovered_items"],
        }
    finally:
        if owned_process is not None and owned_process.poll() is None:
            stop_owned(owned_process)
        if database_process is not None:
            database_process.terminate()
            try:
                database_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                database_process.kill()
                database_process.wait(timeout=5)
        if log_handle is not None:
            log_handle.close()
        shutil.rmtree(root)


if __name__ == "__main__":
    outputs = [trial("p7-trial-a", 29267, 8391),
               trial("p7-trial-b", 29268, 8392)]
    comparable = [{key: value for key, value in item.items() if key != "label"}
                  for item in outputs]
    assert comparable[0] == comparable[1], comparable
    assert all(
        item["active_files_after_loss"] == []
        and item["successor_files"] == ["docs/notes.md", "src/feature.py"]
        and item["selected_candidate"] == "cand-p7-alpha"
        and item["fresh_context"] == {"ok": True, "reason": "FRESH_CONTEXT_PASS"}
        and item["consume_main"] and item["consume_interrupt"]
        and item["replay_main_empty"] and item["replay_interrupt_empty"]
        and item["main_state"] == "CONSUMED"
        and item["interrupt_state"] == "CONSUMED"
        and item["interrupt_recoveries"] == "0"
        and item["counts"] == "1\t1\t2\t2\t1\t1\t1"
        for item in outputs), outputs
    print(json.dumps(outputs, sort_keys=True, separators=(",", ":")))
```

## Embedded file: p7-recovery/test_records.py

```python
"""Focused P7 record, selection, warrant, and fresh-context tests."""
from __future__ import annotations

import copy
import os
import tempfile
import unittest
from pathlib import Path

import fresh_context as fc
import make_fixtures as fx
import records as rec

FIXTURES = fx.FIXTURE_DIR


def load(name: str):
    return rec.load_canonical(os.path.join(FIXTURES, name + ".json"))


def context():
    manifest = load("manifest")
    trajectory = load("trajectory-receipt")
    quorum = load("quorum-decision")
    return fx.build_context(manifest, trajectory, quorum)


class TestCanonicalAndPaths(unittest.TestCase):
    def test_canonical_sorted_compact(self):
        self.assertEqual(rec.canonical_json({"b": 1, "a": 2}), b'{"a":2,"b":1}')

    def test_record_cap(self):
        with self.assertRaisesRegex(rec.RecoveryError, "RECORD_TOO_LARGE"):
            rec.canonical_json({"pad": "x" * rec.MAX_RECORD_BYTES})

    def test_fixtures_are_canonical(self):
        for name in os.listdir(FIXTURES):
            self.assertIsNotNone(rec.load_canonical(os.path.join(FIXTURES, name)))

    def test_unknown_field(self):
        value = load("candidate-alpha")
        value["hidden"] = True
        with self.assertRaisesRegex(rec.RecoveryError, "UNKNOWN_FIELD"):
            rec.validate_candidate(value)

    def test_unsafe_path_classes(self):
        for path in ("", "/abs", "a//b", "a/./b", "a/../b", "a\\b", "a\x00b"):
            with self.subTest(path=repr(path)):
                with self.assertRaisesRegex(rec.RecoveryError, rec.UNSAFE_PATH):
                    rec.validate_relative_path(path)

    def test_symlink_and_executable_flags(self):
        for field in ("is_symlink", "executable"):
            entry = copy.deepcopy(load("manifest")["files"][0])
            entry[field] = True
            with self.assertRaisesRegex(rec.RecoveryError, rec.UNSAFE_PATH):
                rec.validate_file_entry(entry)

    def test_loss_receipt_exact_manifest_link(self):
        rec.validate_loss_receipt(load("loss-receipt"), load("manifest"))
        bad = load("loss-receipt")
        bad["lost_paths"] = bad["lost_paths"][:-1]
        with self.assertRaisesRegex(rec.RecoveryError, "STALE_HASH|LOSS_MANIFEST_MISMATCH"):
            rec.validate_loss_receipt(bad, load("manifest"))


class TestSelection(unittest.TestCase):
    def test_maximum_prefix_wins(self):
        result = rec.select_candidate([load("candidate-beta"), load("candidate-alpha")], context())
        self.assertEqual((result["decision"], result["candidate_id"]),
                         ("PROMOTE", "cand-p7-alpha"))

    def test_order_independent(self):
        a = load("candidate-alpha")
        b = load("candidate-beta")
        self.assertEqual(rec.canonical_json(rec.select_candidate([a, b], context())),
                         rec.canonical_json(rec.select_candidate([b, a], context())))

    def test_canonical_id_tiebreak(self):
        a = load("candidate-alpha")
        z = copy.deepcopy(a)
        z["candidate_id"] = "cand-p7-zeta"
        z["executable_test"]["test_id"] = "exectest-cand-p7-zeta"
        result = rec.select_candidate([z, a], context())
        self.assertEqual(result["candidate_id"], "cand-p7-alpha")

    def test_no_candidate_refuses(self):
        result = rec.select_candidate([], context())
        self.assertEqual((result["decision"], result["reason"]),
                         ("REFUSE", rec.NO_SURVIVING_CANDIDATE))

    def test_each_refusal_vector(self):
        expected = {
            "candidate-policy-veto": rec.POLICY_VETO,
            "candidate-tampered": rec.TAMPERED_EVIDENCE,
            "candidate-unsupported-schema": rec.UNSUPPORTED_SCHEMA,
            "candidate-stale-policy": rec.STALE_POLICY,
            "candidate-missing-quorum": rec.MISSING_QUORUM,
            "candidate-failed-exec-test": rec.EXECUTABLE_TEST_FAILED,
            "candidate-unsafe-path": rec.UNSAFE_PATH,
        }
        for name, reason in expected.items():
            with self.subTest(name=name):
                self.assertEqual(rec.check_eligibility(load(name), context()), reason)
                result = rec.select_candidate([load(name)], context())
                self.assertEqual(result["reason"], rec.NO_SURVIVING_CANDIDATE)

    def test_malformed_candidate_refuses(self):
        bad = load("candidate-alpha")
        del bad["provenance"]
        self.assertEqual(rec.check_eligibility(bad, context()), rec.MALFORMED_RECORD)

    def test_malformed_context_fails_closed(self):
        self.assertEqual(rec.check_eligibility(load("candidate-alpha"), {}),
                         rec.MALFORMED_RECORD)
        with self.assertRaisesRegex(rec.RecoveryError, rec.MALFORMED_RECORD):
            rec.select_candidate([load("candidate-alpha")], {})

    def test_stale_source_receipt_refuses(self):
        bad = load("candidate-alpha")
        bad["source_receipt_hash"] = "0" * 64
        self.assertEqual(rec.check_eligibility(bad, context()), rec.TAMPERED_EVIDENCE)

    def test_surviving_content_hash_drift_refuses(self):
        bad = load("candidate-alpha")
        bad["file_hashes"]["src/feature.py"] = "0" * 64
        bad["executable_test"]["feature_hash"] = "0" * 64
        self.assertEqual(rec.check_eligibility(bad, context()), rec.TAMPERED_EVIDENCE)

    def test_five_repeat_semantics(self):
        candidates = [load("candidate-beta"), load("candidate-alpha")]
        runs = [rec.canonical_json(rec.select_candidate(candidates, context())) for _ in range(5)]
        self.assertEqual(len(set(runs)), 1)


class TestWarrant(unittest.TestCase):
    def setUp(self):
        self.decision = load("decision-promote")
        self.warrant = load("warrant-issued")
        self.harness = rec.RecoveryHarness()
        self.harness.register_warrant(self.warrant)

    def test_consumption_precedes_promotion(self):
        receipt = self.harness.recover(
            self.decision, self.warrant["warrant_id"],
            load("candidate-alpha")["declared_paths"])
        self.assertEqual(self.harness.warrant_state(self.warrant["warrant_id"]), "CONSUMED")
        self.assertEqual(receipt, load("promotion-receipt"))

    def test_replay_refuses(self):
        self.harness.recover(self.decision, self.warrant["warrant_id"])
        refusal = self.harness.recover(self.decision, self.warrant["warrant_id"])
        self.assertEqual(refusal["reason"], rec.WARRANT_REPLAY)

    def test_interrupt_consumes_without_promotion(self):
        with self.assertRaises(rec.RecoveryInterrupted):
            self.harness.recover(self.decision, self.warrant["warrant_id"],
                                 fault="interrupt")
        self.assertEqual(self.harness.warrant_state(self.warrant["warrant_id"]), "CONSUMED")
        self.assertIsNone(self.harness.promotion(self.decision["task_id"]))
        refusal = self.harness.recover(self.decision, self.warrant["warrant_id"])
        self.assertEqual(refusal["reason"], rec.WARRANT_REPLAY)

    def test_tampered_decision_does_not_consume(self):
        bad = copy.deepcopy(self.decision)
        bad["reason"] = "FORGED"
        refusal = self.harness.recover(bad, self.warrant["warrant_id"])
        self.assertEqual(refusal["reason"], rec.TAMPERED_EVIDENCE)
        self.assertEqual(self.harness.warrant_state(self.warrant["warrant_id"]), "ISSUED")

    def test_duplicate_warrant_rejected(self):
        with self.assertRaisesRegex(rec.RecoveryError, rec.WARRANT_REPLAY):
            self.harness.register_warrant(self.warrant)


class TestLinkageAndFreshContext(unittest.TestCase):
    def test_exact_receipt_chain(self):
        manifest = load("manifest")
        trajectory = load("trajectory-receipt")
        candidate = load("candidate-alpha")
        decision = load("decision-promote")
        warrant = load("warrant-issued")
        promotion = load("promotion-receipt")
        self.assertEqual(trajectory["manifest_hash"], rec.sha256_hex(manifest))
        self.assertEqual(candidate["source_receipt_hash"], rec.sha256_hex(trajectory))
        self.assertEqual(warrant["decision_hash"], rec.sha256_hex(decision))
        self.assertEqual(promotion["decision_hash"], rec.sha256_hex(decision))
        self.assertEqual(promotion["warrant_id"], warrant["warrant_id"])

    def test_unrecovered_items_are_explicit(self):
        ledger = load("unrecovered-ledger")
        self.assertEqual(ledger["unrecovered_items"],
                         [{"path": "data/state.json", "reason": "NO_PROVEN_REPRESENTATION"}])

    def test_fresh_context_passes_without_hidden_state(self):
        self.assertEqual(fc.verify_continuation(load("decision-promote"),
                                                load("candidate-alpha")),
                         (True, "FRESH_CONTEXT_PASS"))

    def test_fresh_context_refuses_wrong_candidate(self):
        self.assertEqual(fc.verify_continuation(load("decision-promote"),
                                                load("candidate-beta")),
                         (False, "CANDIDATE_MISMATCH"))

    def test_fresh_context_refuses_feature_drift(self):
        bad = load("candidate-alpha")
        bad["executable_test"]["feature_hash"] = "0" * 64
        self.assertEqual(fc.verify_continuation(load("decision-promote"), bad),
                         (False, "FEATURE_MISMATCH"))

    def test_five_repeat_fresh_context(self):
        runs = [fc.verify_continuation(load("decision-promote"),
                                       load("candidate-alpha")) for _ in range(5)]
        self.assertEqual(len(set(runs)), 1)

    def test_fresh_process_workspace_bytes(self):
        candidate = load("candidate-alpha")
        with tempfile.TemporaryDirectory(dir=FIXTURES) as root:
            target = Path(root) / candidate["executable_test"]["path"]
            target.parent.mkdir(parents=True)
            target.write_bytes(fx.FILE_CONTENTS[candidate["executable_test"]["path"]])
            self.assertEqual(fc.verify_workspace(load("decision-promote"),
                                                 candidate, root),
                             (True, "FRESH_CONTEXT_PASS"))
            target.write_bytes(b"tampered")
            self.assertEqual(fc.verify_workspace(load("decision-promote"),
                                                 candidate, root),
                             (False, "FEATURE_MISMATCH"))


if __name__ == "__main__":
    unittest.main()
```

## Embedded file: p7-recovery/migrations/001_recovery.sql

```sql
-- P7 declared-loss, surviving-candidate, one-use warrant, and recovery ledger.
CREATE TABLE IF NOT EXISTS p7_manifests (
  manifest_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  manifest_json JSONB NOT NULL,
  manifest_hash BYTES NOT NULL CHECK (length(manifest_hash) = 32)
);

CREATE TABLE IF NOT EXISTS p7_loss_receipts (
  receipt_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  manifest_id STRING NOT NULL REFERENCES p7_manifests (manifest_id),
  receipt_json JSONB NOT NULL,
  receipt_hash BYTES NOT NULL CHECK (length(receipt_hash) = 32)
);

CREATE TABLE IF NOT EXISTS p7_recovery_candidates (
  candidate_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  loss_receipt_hash BYTES NOT NULL CHECK (length(loss_receipt_hash) = 32),
  candidate_json JSONB NOT NULL,
  candidate_hash BYTES NOT NULL CHECK (length(candidate_hash) = 32)
);

CREATE TABLE IF NOT EXISTS p7_warrants (
  warrant_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  candidate_id STRING NOT NULL REFERENCES p7_recovery_candidates (candidate_id),
  decision_hash BYTES NOT NULL CHECK (length(decision_hash) = 32),
  state STRING NOT NULL CHECK (state IN ('ISSUED', 'CONSUMED', 'INVALID')),
  warrant_json JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS p7_recoveries (
  recovery_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  candidate_id STRING NOT NULL REFERENCES p7_recovery_candidates (candidate_id),
  warrant_id STRING NOT NULL UNIQUE REFERENCES p7_warrants (warrant_id),
  decision_json JSONB NOT NULL,
  decision_hash BYTES NOT NULL CHECK (length(decision_hash) = 32)
);

CREATE TABLE IF NOT EXISTS p7_recovery_receipts (
  receipt_id STRING PRIMARY KEY,
  recovery_id STRING NOT NULL UNIQUE REFERENCES p7_recoveries (recovery_id),
  receipt_json JSONB NOT NULL,
  receipt_hash BYTES NOT NULL CHECK (length(receipt_hash) = 32)
);

CREATE TABLE IF NOT EXISTS p7_unrecovered_ledgers (
  ledger_id STRING PRIMARY KEY,
  task_id STRING NOT NULL REFERENCES tasks (task_id),
  ledger_json JSONB NOT NULL,
  ledger_hash BYTES NOT NULL CHECK (length(ledger_hash) = 32)
);
```

## Embedded file: p7-recovery/fixtures/candidate-alpha.json

```json
{"candidate_id":"cand-p7-alpha","declared_paths":["docs/notes.md","src/feature.py"],"executable_test":{"feature_hash":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0","passed":true,"path":"src/feature.py","test_id":"exectest-cand-p7-alpha"},"file_hashes":{"docs/notes.md":"ced9ac1144edd85dba013f26d3e40c1657c8c6ad29c406bee799cf0433132a0d","src/feature.py":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0"},"integrity_hash":"4ea04138b865ea1c04c7d0b9995713a609c2ed6c39ce15fa89302532f17888ba","policy_version":"policy-v1","policy_veto":false,"prefix_length":3,"provenance":{"builder":"kimi","source":"p6-quorum-synthetic"},"quorum_decision":{"approvals":3,"candidate_id":"cand-p6-synthetic-001","critical":false,"decision":"PROMOTE","dissent":[],"reason":"QUORUM_PASS","refusals":2,"task_id":"task-p7-synthetic-001","threshold":3,"version":"p6-v1","votes_hash":"74d252a4567da0a3c8289fb78ef766f170550f5bce68832d6a51652eebf87649"},"source_receipt_hash":"2c9f70bc2deb2066c085c1460bf905aa4f3a8a482b301bb4ffb209e501169f7c","tampered":false,"task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/candidate-beta.json

```json
{"candidate_id":"cand-p7-beta","declared_paths":["src/feature.py"],"executable_test":{"feature_hash":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0","passed":true,"path":"src/feature.py","test_id":"exectest-cand-p7-beta"},"file_hashes":{"src/feature.py":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0"},"integrity_hash":"01768e54aeabcd1c10e47203243eee94014e2335de05690f80b8299b37cb4540","policy_version":"policy-v1","policy_veto":false,"prefix_length":2,"provenance":{"builder":"kimi","source":"p6-quorum-synthetic"},"quorum_decision":{"approvals":3,"candidate_id":"cand-p6-synthetic-001","critical":false,"decision":"PROMOTE","dissent":[],"reason":"QUORUM_PASS","refusals":2,"task_id":"task-p7-synthetic-001","threshold":3,"version":"p6-v1","votes_hash":"74d252a4567da0a3c8289fb78ef766f170550f5bce68832d6a51652eebf87649"},"source_receipt_hash":"2c9f70bc2deb2066c085c1460bf905aa4f3a8a482b301bb4ffb209e501169f7c","tampered":false,"task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/candidate-failed-exec-test.json

```json
{"candidate_id":"cand-p7-failedtest","declared_paths":["docs/notes.md","src/feature.py"],"executable_test":{"feature_hash":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0","passed":false,"path":"src/feature.py","test_id":"exectest-cand-p7-alpha"},"file_hashes":{"docs/notes.md":"ced9ac1144edd85dba013f26d3e40c1657c8c6ad29c406bee799cf0433132a0d","src/feature.py":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0"},"integrity_hash":"4ea04138b865ea1c04c7d0b9995713a609c2ed6c39ce15fa89302532f17888ba","policy_version":"policy-v1","policy_veto":false,"prefix_length":3,"provenance":{"builder":"kimi","source":"p6-quorum-synthetic"},"quorum_decision":{"approvals":3,"candidate_id":"cand-p6-synthetic-001","critical":false,"decision":"PROMOTE","dissent":[],"reason":"QUORUM_PASS","refusals":2,"task_id":"task-p7-synthetic-001","threshold":3,"version":"p6-v1","votes_hash":"74d252a4567da0a3c8289fb78ef766f170550f5bce68832d6a51652eebf87649"},"source_receipt_hash":"2c9f70bc2deb2066c085c1460bf905aa4f3a8a482b301bb4ffb209e501169f7c","tampered":false,"task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/candidate-missing-quorum.json

```json
{"candidate_id":"cand-p7-noquorum","declared_paths":["docs/notes.md","src/feature.py"],"executable_test":{"feature_hash":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0","passed":true,"path":"src/feature.py","test_id":"exectest-cand-p7-alpha"},"file_hashes":{"docs/notes.md":"ced9ac1144edd85dba013f26d3e40c1657c8c6ad29c406bee799cf0433132a0d","src/feature.py":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0"},"integrity_hash":"4ea04138b865ea1c04c7d0b9995713a609c2ed6c39ce15fa89302532f17888ba","policy_version":"policy-v1","policy_veto":false,"prefix_length":3,"provenance":{"builder":"kimi","source":"p6-quorum-synthetic"},"quorum_decision":{"approvals":3,"candidate_id":"cand-p6-synthetic-001","critical":false,"decision":"REFUSE","dissent":[],"reason":"QUORUM_MISSING","refusals":2,"task_id":"task-p7-synthetic-001","threshold":3,"version":"p6-v1","votes_hash":"74d252a4567da0a3c8289fb78ef766f170550f5bce68832d6a51652eebf87649"},"source_receipt_hash":"2c9f70bc2deb2066c085c1460bf905aa4f3a8a482b301bb4ffb209e501169f7c","tampered":false,"task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/candidate-policy-veto.json

```json
{"candidate_id":"cand-p7-veto","declared_paths":["docs/notes.md","src/feature.py"],"executable_test":{"feature_hash":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0","passed":true,"path":"src/feature.py","test_id":"exectest-cand-p7-alpha"},"file_hashes":{"docs/notes.md":"ced9ac1144edd85dba013f26d3e40c1657c8c6ad29c406bee799cf0433132a0d","src/feature.py":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0"},"integrity_hash":"4ea04138b865ea1c04c7d0b9995713a609c2ed6c39ce15fa89302532f17888ba","policy_version":"policy-v1","policy_veto":true,"prefix_length":3,"provenance":{"builder":"kimi","source":"p6-quorum-synthetic"},"quorum_decision":{"approvals":3,"candidate_id":"cand-p6-synthetic-001","critical":false,"decision":"PROMOTE","dissent":[],"reason":"QUORUM_PASS","refusals":2,"task_id":"task-p7-synthetic-001","threshold":3,"version":"p6-v1","votes_hash":"74d252a4567da0a3c8289fb78ef766f170550f5bce68832d6a51652eebf87649"},"source_receipt_hash":"2c9f70bc2deb2066c085c1460bf905aa4f3a8a482b301bb4ffb209e501169f7c","tampered":false,"task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/candidate-stale-policy.json

```json
{"candidate_id":"cand-p7-stalepolicy","declared_paths":["docs/notes.md","src/feature.py"],"executable_test":{"feature_hash":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0","passed":true,"path":"src/feature.py","test_id":"exectest-cand-p7-alpha"},"file_hashes":{"docs/notes.md":"ced9ac1144edd85dba013f26d3e40c1657c8c6ad29c406bee799cf0433132a0d","src/feature.py":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0"},"integrity_hash":"4ea04138b865ea1c04c7d0b9995713a609c2ed6c39ce15fa89302532f17888ba","policy_version":"policy-v0","policy_veto":false,"prefix_length":3,"provenance":{"builder":"kimi","source":"p6-quorum-synthetic"},"quorum_decision":{"approvals":3,"candidate_id":"cand-p6-synthetic-001","critical":false,"decision":"PROMOTE","dissent":[],"reason":"QUORUM_PASS","refusals":2,"task_id":"task-p7-synthetic-001","threshold":3,"version":"p6-v1","votes_hash":"74d252a4567da0a3c8289fb78ef766f170550f5bce68832d6a51652eebf87649"},"source_receipt_hash":"2c9f70bc2deb2066c085c1460bf905aa4f3a8a482b301bb4ffb209e501169f7c","tampered":false,"task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/candidate-tampered.json

```json
{"candidate_id":"cand-p7-tampered","declared_paths":["docs/notes.md","src/feature.py"],"executable_test":{"feature_hash":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0","passed":true,"path":"src/feature.py","test_id":"exectest-cand-p7-alpha"},"file_hashes":{"docs/notes.md":"ced9ac1144edd85dba013f26d3e40c1657c8c6ad29c406bee799cf0433132a0d","src/feature.py":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0"},"integrity_hash":"4ea04138b865ea1c04c7d0b9995713a609c2ed6c39ce15fa89302532f17888ba","policy_version":"policy-v1","policy_veto":false,"prefix_length":3,"provenance":{"builder":"kimi","source":"p6-quorum-synthetic"},"quorum_decision":{"approvals":3,"candidate_id":"cand-p6-synthetic-001","critical":false,"decision":"PROMOTE","dissent":[],"reason":"QUORUM_PASS","refusals":2,"task_id":"task-p7-synthetic-001","threshold":3,"version":"p6-v1","votes_hash":"74d252a4567da0a3c8289fb78ef766f170550f5bce68832d6a51652eebf87649"},"source_receipt_hash":"2c9f70bc2deb2066c085c1460bf905aa4f3a8a482b301bb4ffb209e501169f7c","tampered":true,"task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/candidate-unsafe-path.json

```json
{"candidate_id":"cand-p7-unsafepath","declared_paths":["docs/notes.md","src/feature.py","secret/undeclared.txt"],"executable_test":{"feature_hash":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0","passed":true,"path":"src/feature.py","test_id":"exectest-cand-p7-alpha"},"file_hashes":{"docs/notes.md":"ced9ac1144edd85dba013f26d3e40c1657c8c6ad29c406bee799cf0433132a0d","secret/undeclared.txt":"2eaa481dd530759fd2f4accb04cf80460e4cf5dceacba825d0195fcfcfe27bf0","src/feature.py":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0"},"integrity_hash":"4ea04138b865ea1c04c7d0b9995713a609c2ed6c39ce15fa89302532f17888ba","policy_version":"policy-v1","policy_veto":false,"prefix_length":3,"provenance":{"builder":"kimi","source":"p6-quorum-synthetic"},"quorum_decision":{"approvals":3,"candidate_id":"cand-p6-synthetic-001","critical":false,"decision":"PROMOTE","dissent":[],"reason":"QUORUM_PASS","refusals":2,"task_id":"task-p7-synthetic-001","threshold":3,"version":"p6-v1","votes_hash":"74d252a4567da0a3c8289fb78ef766f170550f5bce68832d6a51652eebf87649"},"source_receipt_hash":"2c9f70bc2deb2066c085c1460bf905aa4f3a8a482b301bb4ffb209e501169f7c","tampered":false,"task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/candidate-unsupported-schema.json

```json
{"candidate_id":"cand-p7-badschema","declared_paths":["docs/notes.md","src/feature.py"],"executable_test":{"feature_hash":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0","passed":true,"path":"src/feature.py","test_id":"exectest-cand-p7-alpha"},"file_hashes":{"docs/notes.md":"ced9ac1144edd85dba013f26d3e40c1657c8c6ad29c406bee799cf0433132a0d","src/feature.py":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0"},"integrity_hash":"4ea04138b865ea1c04c7d0b9995713a609c2ed6c39ce15fa89302532f17888ba","policy_version":"policy-v1","policy_veto":false,"prefix_length":3,"provenance":{"builder":"kimi","source":"p6-quorum-synthetic"},"quorum_decision":{"approvals":3,"candidate_id":"cand-p6-synthetic-001","critical":false,"decision":"PROMOTE","dissent":[],"reason":"QUORUM_PASS","refusals":2,"task_id":"task-p7-synthetic-001","threshold":3,"version":"p6-v1","votes_hash":"74d252a4567da0a3c8289fb78ef766f170550f5bce68832d6a51652eebf87649"},"source_receipt_hash":"2c9f70bc2deb2066c085c1460bf905aa4f3a8a482b301bb4ffb209e501169f7c","tampered":false,"task_id":"task-p7-synthetic-001","version":"p7-v0"}
```

## Embedded file: p7-recovery/fixtures/decision-no-surviving.json

```json
{"candidate_id":null,"candidates_hash":"87cef5cdcf155b6034f82192c75542b54f95042d3984919c27fe00aa2fbfe08d","decision":"REFUSE","reason":"NO_SURVIVING_CANDIDATE","task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/decision-promote.json

```json
{"candidate_id":"cand-p7-alpha","candidates_hash":"28649c9bad8646e4124e810fb36e10a2e4aa78ab270cabe9d36df791ef415f6a","decision":"PROMOTE","reason":"MAX_PROVEN_PREFIX","task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/feature-file.json

```json
{"content_hash":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0","path":"src/feature.py"}
```

## Embedded file: p7-recovery/fixtures/loss-receipt.json

```json
{"absence_hash":"5114cb13359b66d1442ba675d5b9a750a2f081afaf99b9f38c6492c9a241ee99","lost_paths":["data/state.json","docs/notes.md","src/feature.py"],"manifest_hash":"ea9f1ed27acf518cba7b39518cdf4ae99b9a12ff2fc51a8c8fa63c345497417e","receipt_id":"rcpt-loss-p7-001","task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/manifest.json

```json
{"files":[{"content_hash":"0f6dfbe5b01d28c779a605bda76b1986e8fb2d7d750ee5ba3c9a13b09a6e8dde","executable":false,"is_symlink":false,"path":"data/state.json"},{"content_hash":"ced9ac1144edd85dba013f26d3e40c1657c8c6ad29c406bee799cf0433132a0d","executable":false,"is_symlink":false,"path":"docs/notes.md"},{"content_hash":"1c585c55db654f11145692cb23e49ff3b2fb911de49115a584528ff7916a94d0","executable":false,"is_symlink":false,"path":"src/feature.py"}],"manifest_id":"manifest-p7-001","task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/promotion-receipt.json

```json
{"candidate_id":"cand-p7-alpha","decision_hash":"f25cfc46abff16e8420afb484f298eec4a380c09101856bbdce4f8c3462baeb8","promoted_paths":["docs/notes.md","src/feature.py"],"receipt_hash":"c82c28314da0b65177e38b1d856d8b4751360c7e4c5d38c59a803c973a45ee94","receipt_id":"rcpt-c82c28314da0b65177e38b1d856d8b47","task_id":"task-p7-synthetic-001","version":"p7-v1","warrant_id":"warrant-p7-001"}
```

## Embedded file: p7-recovery/fixtures/quorum-decision.json

```json
{"approvals":3,"candidate_id":"cand-p6-synthetic-001","critical":false,"decision":"PROMOTE","dissent":[],"reason":"QUORUM_PASS","refusals":2,"task_id":"task-p7-synthetic-001","threshold":3,"version":"p6-v1","votes_hash":"74d252a4567da0a3c8289fb78ef766f170550f5bce68832d6a51652eebf87649"}
```

## Embedded file: p7-recovery/fixtures/refusal-receipt-no-surviving.json

```json
{"decision_hash":"c0db960086d2a26497b875f4d415ea97d9d9ca2beb8e99b2a345dc3b590631c9","reason":"NO_SURVIVING_CANDIDATE","receipt_hash":"a158ea76c6ae611b42a4cb6b60d937a89bf8e4f673a30ebbac7817854a3ca789","receipt_id":"rcpt-a158ea76c6ae611b42a4cb6b60d937a8","task_id":"task-p7-synthetic-001","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/trajectory-receipt.json

```json
{"events":[{"event":"DECLARE","event_hash":"26799ee33234fea72fec1524f2b287921402e111c7861f8bc3e62bd941c087a6","sequence":0},{"event":"RECORD","event_hash":"5e930f9d3d7ee7dacd2e65e0e6da73d73ffd541ac53f04278d30da28455540fa","sequence":1},{"event":"EVALUATE","event_hash":"d39c7c1704d9fa0742c3c5919f9b3649b2c25bafd8426eaa8d74b86195072762","sequence":2}],"manifest_hash":"ea9f1ed27acf518cba7b39518cdf4ae99b9a12ff2fc51a8c8fa63c345497417e","receipt_id":"rcpt-trajectory-p7-001","task_id":"task-p7-synthetic-001","trajectory_hash":"e1284725f69c974d7854f9888dfc87fa391eb2a1313a2d351e09d4ac07c35fcc","version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/unrecovered-ledger.json

```json
{"ledger_id":"ledger-p7-001","manifest_hash":"ea9f1ed27acf518cba7b39518cdf4ae99b9a12ff2fc51a8c8fa63c345497417e","recovered_paths":["docs/notes.md","src/feature.py"],"task_id":"task-p7-synthetic-001","unrecovered_items":[{"path":"data/state.json","reason":"NO_PROVEN_REPRESENTATION"}],"version":"p7-v1"}
```

## Embedded file: p7-recovery/fixtures/warrant-issued.json

```json
{"candidate_id":"cand-p7-alpha","decision_hash":"f25cfc46abff16e8420afb484f298eec4a380c09101856bbdce4f8c3462baeb8","state":"ISSUED","task_id":"task-p7-synthetic-001","version":"p7-v1","warrant_id":"warrant-p7-001"}
```
