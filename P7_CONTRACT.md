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
