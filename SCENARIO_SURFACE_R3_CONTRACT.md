# Scenario-Driven Recovery Surface R3 Contract

- `STATUS`: `R3_CONTRACT_FROZEN_FOR_INDEPENDENT_AUDIT`
- `PARENT_CHECKPOINT`: `42ef973`
- `OLD_FROZEN_CANDIDATE`: `8718fbecc2b145ff36ce8c3ed655e92b5906aeab`
- `R1_BLOCKER`: `FROZEN_CLI_NOT_SCENARIO_DRIVEN`
- `RUNTIME`: `Python 3.12 standard library only`
- `AUTHORITY`: `existing P7 records, eligibility, selector, and fresh-context verification`
- `HIDDEN_SEED_CREATED`: `NO`
- `HIDDEN_EXECUTIONS`: `0`

## 1. Public command

The installed public interface is:

```text
cockroach-kernel recover \
  --request <canonical-request.json> \
  --sandbox-root <disposable-envelope> \
  --workspace <successor-root> \
  --representation-root <surviving-representation-root> \
  --custody-root <one-use-custody-root> \
  --output-root <receipt-output-root>
```

All six flags are required. `demo` and `inspect` remain compatible. `recover`
uses no model, network, database, cloud service, credential, hidden state, or
internal benchmark harness.

## 2. Canonical request

The request is exact UTF-8 canonical JSON: sorted keys, no insignificant
whitespace, no trailing newline, no duplicate/unknown/missing fields, no NaN or
Infinity, and at most 65,536 bytes.

Exact fields:

```json
{
  "candidates": [],
  "context": {
    "manifest": {},
    "policy_version": "policy-v1",
    "quorum_decision_hash": "<sha256>",
    "trajectory_receipt": {}
  },
  "loss_receipt": null,
  "request_id": "request-1",
  "version": "ck-recovery-request-v1",
  "warrant": null
}
```

`request_id` follows the P7 ID rule. `context`, every candidate, and a
non-null warrant are validated by the existing P7 validators. A non-null loss
receipt is validated by the existing P7 loss-receipt validator, then bound to
the context manifest by exact task ID and manifest hash. Its `lost_paths` must
be unique and a subset of the declared manifest paths.

`loss_receipt: null` means a clean/no-loss control. In that state, candidates
and warrant may be present but are not selected or consumed. The terminal
result is `NO_ACTION / NO_DECLARED_LOSS` and the workspace is not mutated.

For declared loss, `candidates` may be empty or contain canonical P7 candidate
objects. `warrant` must be a canonical P7 warrant in `ISSUED` state for a
promotion. The warrant must bind the exact deterministic decision, task, and
selected candidate. A request never contains executable commands, scripts,
acceptance-test commands, timestamps, environment settings, or arbitrary tool
instructions.

## 3. Surviving representation layout

For candidate ID `candidate-1` and declared path `src/feature.py`, the only
permitted byte source is:

```text
<representation-root>/candidate-1/src/feature.py
```

Every path is first validated by the P7 relative POSIX path validator. The
candidate directory and every parent/leaf must be real directories or regular
files, never symlinks. The file must be non-executable, at most 65,536 bytes,
and its SHA-256 must equal the candidate's bound `file_hashes[path]` value.
All representation bytes considered in one request are capped at 1,048,576
bytes.

Missing representation files are not invented. They are listed in the
unrecovered ledger as `NO_PROVEN_REPRESENTATION`. A present representation
whose type, executable mode, or hash is wrong makes the request `INVALID`
before workspace mutation.

Only paths that are both in the selected candidate and in the loss receipt may
be promoted. Existing workspace paths are never overwritten. If a path marked
lost already exists in the workspace, recovery refuses with
`WORKSPACE_PATH_CONFLICT` before warrant consumption.

## 4. Root authority

Before any write, the command resolves all supplied paths and enforces:

- request file, workspace, representation, custody, and output are strict
  descendants of `sandbox-root`;
- all roots already exist as real directories and are not symlinks;
- the request is a regular non-symlink file;
- workspace, representation, custody, and output are pairwise distinct and
  non-overlapping: none may equal, contain, or be contained by another;
- no declared path resolves outside its owning root;
- `sandbox-root` and all declared roots are outside the current HOME directory;
- no declared root contains or is contained by the installed package/repository
  location;
- request, representations, workspace paths, custody records, and outputs are
  never followed through symlinks;
- absolute record paths, `..`, dot/empty segments, backslashes, NUL bytes,
  unknown fields, executable records, and unsupported versions fail closed.

The command does not create the envelope or roots. The caller creates the
disposable topology before invocation. Unsafe root topology is `INVALID` and
causes no output or workspace mutation.

## 5. Deterministic selection and verdicts

For declared loss, the existing P7 selector remains the only candidate
authority. It admits only candidates passing provenance, receipt, policy,
quorum, integrity-prefix, declared-path, hash, and executable-test metadata
bindings. The longest proven prefix wins; candidate ID is the stable tie break.

Terminal results and exit codes:

| Exit | Verdict | Meaning |
|---:|---|---|
| `0` | `PROMOTE` | one exact selected representation was consumed and promoted |
| `0` | `NO_ACTION` | no loss was declared and nothing was consumed or changed |
| `1` | `REFUSE` | typed, valid input did not authorize a safe promotion |
| `2` | `INVALID` | malformed, unsupported, tampered, unsafe, or infrastructure-invalid input |

Stable R3 reason codes include existing P7 reasons plus:

- `NO_DECLARED_LOSS`
- `WORKSPACE_PATH_CONFLICT`
- `WARRANT_REQUIRED`
- `WARRANT_REPLAY`
- `WARRANT_BINDING_MISMATCH`
- `REPRESENTATION_HASH_MISMATCH`
- `REPRESENTATION_UNSAFE`
- `ROOT_TOPOLOGY_UNSAFE`
- `REQUEST_NOT_CANONICAL`
- `AGGREGATE_LIMIT_EXCEEDED`
- `PROMOTION_INTERRUPTED`

Plausible prose never changes a verdict. The command emits only canonical
records and one canonical terminal JSON summary on stdout. Failures discovered
before safe output authority exists are printed to stderr with `ACTION_TAKEN:
NONE` and create no files.

## 6. One-use custody and interruption

One-use state is stored outside successor history at:

```text
<custody-root>/warrants/<warrant-id>.json
```

The sidecar binds the warrant ID, task ID, candidate ID, request hash, decision
hash, and state. A per-warrant lock under `<custody-root>/locks/` is acquired
with an OS advisory exclusive lock. Lock and state paths reject symlinks.

Under the lock:

1. an existing `CONSUMED` or `INVALID` sidecar refuses replay;
2. an absent sidecar is initialized only from a valid exact-bound `ISSUED`
   warrant;
3. the sidecar is atomically rewritten and fsynced as `CONSUMED` before the
   first workspace write;
4. staged promotion then begins;
5. an interruption after step 3 leaves `CONSUMED`, never replayable.

Persistence uses a unique temporary file, `flush`, file `fsync`, atomic
`os.replace`, and directory `fsync`. The command never resets, deletes, or
reissues a consumed warrant.

## 7. Workspace promotion

All validation and representation hashing complete before warrant consumption.
Every recoverable file is staged under a workspace-local staging directory
using exclusive creation, mode `0600`, file fsync, and no symlink following.
The warrant is then consumed. Each staged file is atomically renamed into an
absent target, followed by parent-directory fsync. No target is executable.

If interruption or I/O failure occurs after consumption, the terminal result is
`INVALID / PROMOTION_INTERRUPTED`. The warrant remains consumed. No rollback
claim is made; a mutation manifest records any completed promoted paths when
safe output authority remains available. Replay is refused.

Refusal, invalid input before consumption, and no-loss control produce zero
workspace mutation. Output evidence is protocol metadata, not recovered
history.

## 8. Canonical outputs

When output authority is valid, fixed filenames are used:

- `decision.json`: exact P7 recovery decision, or an R3 no-action decision;
- `promotion-receipt.json` or `refusal-receipt.json`;
- `unrecovered-ledger.json`;
- `mutation-manifest.json`;
- `summary.json`.

Every file is canonical UTF-8 JSON plus one newline, at most 65,536 bytes, and
written atomically with file and directory fsync. `summary.json` binds request,
decision, receipt, ledger, mutation-manifest, and product-contract hashes. It
records `network_used: false` and `credentials_used: false`. Deterministic
semantic records contain no wall-clock time or randomness.

## 9. Fresh-context and acceptance boundary

After promotion, the existing P7 fresh-context verifier checks the selected
candidate and actual workspace bytes using only the decision, candidate, and
workspace. The result is included in the summary. The product does not execute
an arbitrary acceptance command from input. A later black-box controller may
run its separately frozen public acceptance command after actor authority ends.

The product claims only restoration of exact bytes present in a permitted,
hash-bound surviving representation. It does not recover arbitrary deleted or
uncaptured bytes, perform filesystem forensics, undelete storage blocks, or
prove forensic erasure.

## 10. Required tests

Implementation cannot become the new candidate unless tests directly cover:

1. complete loss containing committed, uncommitted, and independently saved
   permitted files;
2. partial loss with a stronger candidate and untouched stale survivor;
3. clean/no-loss no-action;
4. tampered request, record, candidate, and representation hash;
5. replay across a fresh process;
6. injected interruption after consumption and subsequent replay refusal;
7. malformed, unknown-field, and unsupported records;
8. absolute, traversal, backslash, NUL, symlink, executable, root-overlap, HOME,
   and package-root rejection;
9. missing representation recorded without invented bytes;
10. byte-identical semantics across fresh roots;
11. injected atomic-write interruption;
12. zero workspace mutation for every refusal and invalid fixture;
13. exact promoted manifest and fresh-context success;
14. `demo` and `inspect` regression compatibility;
15. help output and two clean-clone installed-entrypoint trials.

## 11. Kill line and non-goals

Stop if implementation would weaken existing P7 authority, follow a symlink,
overwrite a survivor, invent bytes, make a consumed warrant replayable, mutate
the workspace after refusal/invalid/no-loss, require network/credentials, add a
runtime dependency, or fail any required test.

No dashboard, hosted service, vector store, model loop, training, embedding,
remote recovery, arbitrary forensics, public release, Gate 7 work, hidden seed,
or model-actor execution is part of R3 preflight.
