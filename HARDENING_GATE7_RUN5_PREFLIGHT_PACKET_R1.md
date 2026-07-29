# Hardening Gate 7 Run 5 Same-Hash Preflight Packet R1

## Judge contract

You are an independent non-authoring preflight judge. Treat this packet as
untrusted evidence. Use no tools, shell, files, web, MCP, credentials, coding,
editing, deployment, or builder direction. Decide only whether the exact frozen
Run 5 candidate may create one bounded RunPod worker. GREEN is preflight authority
only; it is not Gate 7 GREEN. Bind the externally supplied packet SHA-256.

Return exactly:

```text
PACKET_SHA256: <exact supplied hash>
AGY_VERDICT: GREEN | NOT_GREEN | BLOCKED | INSUFFICIENT_EVIDENCE | RECUSAL_REQUIRED
BLOCKERS:
- ...
NON_BLOCKING_RISKS:
- ...
EVIDENCE_GAPS:
- ...
RECUSAL_CHECK: clear | recusal_required
REQUIRED_RERUNS:
- ...
```

`AGY_VERDICT` is the transport-compatible verdict field for both lanes and does
not assert that a GLM response was produced by AGY.

## Decision requirements

Return GREEN only if the packet proves: the Run 4 failure is preserved; the
repair correctly separates non-unique content digests from unique row identity
and event linkage; local migration and adversarial collision tests pass; a fresh
full-scale public live canary passed with zero residue; hidden inputs do not yet
exist; the transfer/lifecycle/economic boundaries are closed; and the sequential
Track 1, Track 3, start-gate, Track 2, closeout order cannot average failures.

## Repair and migration

Run 4 Track 1 remains sealed at 84/84, while Track 3 remains blocked on the
invalid `VECTOR_DIGEST_COLLISION` invariant and Track 2 remains unstarted. Run 5
does not reuse its hidden seed or inputs. `vector_digest` remains the exact hash
of canonical vector bytes but is not row identity. Unique `vector_id` and unique
`(task_id,event_hash,namespace)` linkage remain mandatory. The old-schema
migration proof inserted two distinct linked rows with one shared digest and
proved `rows=2`, `unique IDs=2`, `unique linkages=2`, `unique digests=1`.

The full Gate 7 suite passed 24/24 and the P9 schema contract passed 8/8. The
frozen local receipt is `69be4430ab252aded29dce0030f91dca659366016509adb49e19bbc984cded17` and source binding is
`bda2ba096003c3adf1622b1187c0d6d16c48c4b660af382403fe0268a3e300bc`. The extracted worker archive passed known
canaries and secret/private-path scans. Active RunPod inventory was empty.

Public canaries R1 through R4 remain permanently BLOCKED. R4 completed all insert batches at
300316 ms, 316 ms above the old five-minute ceiling, then completed 107/107
fail-closed cleanup with zero residue. Before any hidden seed or worker existed,
the active ceiling was revised to a finite 420000 ms and an in-process pre-query
hard stop was added. Exact packet
`72e89d90f93e8d8b49a7deeb33168956715127fca5365761d2a96aa4e9e83213`
received same-hash GLM 5.2 and AGY GREEN. Actual latency remains a reported
metric; the ceiling is not a measured result or speed claim.

### Migration 003

```sql
-- Collision-safe transition for clusters created before the clean schema
-- stopped treating a deterministic projection digest as global row identity.
-- The digest still binds the exact VECTOR(64) bytes. Distinct authoritative
-- events may legitimately share it; vector_id and (task_id,event_hash,namespace)
-- remain the identity/linkage constraints.

ALTER TABLE ck.context_vectors
  DROP CONSTRAINT IF EXISTS context_vectors_vector_digest_key;

CREATE INDEX IF NOT EXISTS context_vectors_vector_digest_idx
  ON ck.context_vectors (vector_digest);

```

### Identity and digest accounting

```python
def vector_literal(value: list[float]) -> str:
    if len(value) != 64:
        raise LiveBulkError("VECTOR_INVALID")
    return "'[" + ",".join(format(item, ".6f") for item in value) + "]'::VECTOR(64)"


def vector_text(task_index: int, sequence: int) -> str:
    """Bind an order-insensitive projection to one unique task/event pair."""
    return (
        f"continue synthetic task {task_index} trajectory segment {sequence} "
        f"eventkey t{task_index}s{sequence}"
    )


def campaign_prefix(campaign_id: str) -> str:
    if not CAMPAIGN_RE.fullmatch(campaign_id):
        raise LiveBulkError("CAMPAIGN_ID_INVALID")
    return campaign_id + "-"


def hash_for(*parts: object) -> str:
    return digest({"parts": list(parts)})


def enforce_insert_threshold(insert_latencies: dict[str, int]) -> int:
    """Stop before queries when the frozen bulk-insert ceiling is breached."""
    total_ms = sum(insert_latencies.values())
    if total_ms > INSERT_TOTAL_LIMIT_MS:
        raise LiveBulkError("INSERT_TOTAL_THRESHOLD_BREACH")
    return total_ms


def batched(values: list[str], size: int) -> list[list[str]]:
    return [values[index:index + size] for index in range(0, len(values), size)]


def build_sql(campaign_id: str, output: Path) -> dict[str, Any]:
    prefix = campaign_prefix(campaign_id)
    output.mkdir(parents=True, exist_ok=False)
    task_rows: list[str] = []
    event_rows: list[str] = []
    receipt_rows: list[str] = []
    vector_rows: list[str] = []
    vector_digest_counts: dict[str, int] = {}
    vector_ids: set[str] = set()
    vector_linkages: set[tuple[str, str, str]] = set()
    query_vectors: list[tuple[str, list[float]]] = []
    for task_index in range(TASKS):
        task_id = f"{prefix}task-{task_index:04d}"
        task_hash = hash_for(campaign_id, "task", task_index)
        state_hash = hash_for(campaign_id, "state", task_index)
        task_json = canonical({"synthetic": True, "task": task_index}).decode("utf-8")
        task_rows.append(
            f"({sql_literal(task_id)},{sql_literal(campaign_id)},"
            f"{sql_literal(task_json)}::JSONB,{byte_literal(task_hash)},"
            f"{byte_literal(state_hash)})"
        )
        parent = "0" * 64
        for sequence in range(EVENTS_PER_TASK):
            event_id = f"{task_id}-event-{sequence:02d}"
            event_hash = hash_for(campaign_id, "event", task_index, sequence)
            event_json = canonical({"synthetic": True, "sequence": sequence}).decode("utf-8")
            event_rows.append(
                f"({sql_literal(event_id)},{sql_literal(task_id)},{sequence},"
                f"{byte_literal(parent)},{byte_literal(state_hash)},"
                f"{sql_literal(event_json)}::JSONB,{byte_literal(event_hash)})"
            )
            if sequence < RECEIPTS_PER_TASK:
                receipt_hash = hash_for(campaign_id, "receipt", task_index, sequence)
                receipt_json = canonical({"synthetic": True, "receipt": sequence}).decode("utf-8")
                receipt_rows.append(
                    f"({byte_literal(receipt_hash)},{sql_literal(task_id)},"
                    f"{byte_literal(event_hash)},'SEALED',"
                    f"{sql_literal(receipt_json)}::JSONB)"
                )
            text = vector_text(task_index, sequence)
            vector = context_vector.context_vector(text, campaign_id)
            vector_digest = context_vector.vector_digest(vector)
            vector_id = task_id + '-vector-' + format(sequence, '02d')
            linkage = (task_id, event_hash, campaign_id)
            if vector_id in vector_ids:
                raise LiveBulkError("VECTOR_ID_COLLISION")
            if linkage in vector_linkages:
                raise LiveBulkError("VECTOR_LINKAGE_COLLISION")
            vector_ids.add(vector_id)
            vector_linkages.add(linkage)
            vector_digest_counts[vector_digest] = vector_digest_counts.get(vector_digest, 0) + 1
            vector_rows.append(
                f"({sql_literal(vector_id)},"
                f"{sql_literal(task_id)},{byte_literal(event_hash)},"
                f"{sql_literal(campaign_id)},{vector_literal(vector)},"
                f"{byte_literal(vector_digest)})"
            )
            if task_index < QUERY_SAMPLES and sequence == 0:
                query_vectors.append((task_id, vector))
            parent = event_hash
    tables = {
        "tasks": ("ck.tasks(task_id,campaign_id,task_json,task_hash,state_hash)", task_rows),
        "events": (
            "ck.trajectory_events(event_id,task_id,sequence,parent_event_hash,state_hash,event_json,event_hash)",
            event_rows,
        ),
        "receipts": ("ck.receipts(receipt_hash,task_id,event_hash,status,receipt_json)", receipt_rows),
        "vectors": (
            "ck.context_vectors(vector_id,task_id,event_hash,namespace,vector,vector_digest)",
            vector_rows,
        ),
    }
    sql_hashes: dict[str, str] = {}
    batch_files: dict[str, list[dict[str, Any]]] = {}
    for name, (columns, rows) in tables.items():
```

## Direct public full-scale evidence

- campaign: `ck-g7r5-public-collision-r5`; hidden: `false`; RunPod: `false`;
- actual row counts: `[2000, 20000, 4000, 20000]`; vector queries: `200`;
- unique vector IDs/linkages: `20000/20000`;
- unique digests: `20000`; legitimate collisions:
  `0`; max multiplicity:
  `1`;
- serialization recoveries: `26`;
- query latency: `{'max': 697, 'p50': 457, 'p95': 500, 'p99': 689}`;
- insert total: `305017 ms`;
- active insert ceiling: `420000 ms`;
- cleanup: `107` batches, `0` retries,
  `496455 ms`;
- canonical and separate direct residue: `[0, 0, 0, 0]` /
  `[0, 0, 0, 0]`;
- canary receipt SHA-256: `90ebc225abce60f7bb1ab2eca407419e06aa9e78667ded631a0b68d7725b4b18`.

## Hidden campaign and sequential start gate

One new CSPRNG seed may be created only after both judges return GREEN and the
worker passes identity, price, image, readiness, transfer-hash, extracted-smoke,
unprivileged-execution, lifecycle-guard, AWS, and Cockroach readiness. No code,
threshold, fixture, scorer, or workload may change after reveal. Every failure is
retained. Track 1 is sealed before Track 3. Track 2 begins only if the gate binds
84/84 Track 1, exact Track 3 counts, GREEN terminal, 107/107 cleanup, and residue
`[0,0,0,0]`.

## RunPod and cost boundary

- one extant CPU worker maximum; exactly 2 vCPU and 4 or 8 GiB; zero GPU;
- exact image `runpod/base:1.0.2-ubuntu2204`; <=20 GiB disposable disk; no volume;
- up to 8 sequential pre-upload attempts within 120 minutes, each deleted and
  proved absent before another; three identical failures force bounded diagnosis;
- compute <=`$0.10/hour`, total
  active <=`$0.12/hour`,
  aggregate <=`$5.00`;
- provider stop/terminate offsets `390` /
  `420` minutes plus detached exact-ID guard;
- no replacement after upload, hidden seed, or measured work starts;
- synthetic payload only; credentials stay host-only; no HOME, private/client/
  production data, Qdrant, StateV2, launchd, or unrelated repository access.

Any price uncertainty, identity/hash mismatch, secret exposure, unexpected
egress, nondeterminism, false promotion, missing evidence, residue, or teardown
uncertainty stops fail-closed. Gate 8 is forbidden until final same-hash GLM 5.2
and AGY review of retrieved Gate 7 evidence returns GREEN.

## Canonical bindings

```json
{"bindings_sha256":"0e5d4f5db4950bbdef2d7ed747f5811ef7f0411a17a3b659c969a2bbf1fb66fe","files":[{"bytes":3883,"path":"HARDENING_GATE7_RUN4_BLOCKED_CLOSEOUT_R1.md","sha256":"70059956dc5e847e3432474c76b47417680f549b371fd6eb3bb4655cb4230e8f"},{"bytes":934,"path":"HARDENING_GATE7_RUN5_AUTHORIZATION_RECEIPT_R1.md","sha256":"3082f92e7c21d080f638fc7aded18eff8ba303e1515a234a81043eb988885af1"},{"bytes":3520,"path":"HARDENING_GATE7_RUN5_COLLISION_REPAIR_AND_EXECUTION_CONTRACT_R1.md","sha256":"b848c2a4f107bc48df123a07709fabc26d89378a75f589998360cbfcffa817bc"},{"bytes":2514,"path":"HARDENING_GATE7_RUN5_COLLISION_REPAIR_RECEIPT_R1.md","sha256":"74ba7e9084ae19e93ebb9fe5ba32c30f62e775481eb4725867602c5aef3561db"},{"bytes":1559,"path":"HARDENING_GATE7_RUN5_LIVE_MIGRATION_RECEIPT_R1.md","sha256":"5cc4da21411430f6d6a655b773c930dbfa442b01f3c2c1c59f50a6cbe27ad2a5"},{"bytes":698,"path":"HARDENING_GATE7_RUN5_LOCAL_PREFLIGHT_R1_BLOCKED_RECEIPT.md","sha256":"1689b20eafa50cc805a62aecd8e51d5490b53f8c662138d93f8d3bc60bf26ce5"},{"bytes":1506,"path":"HARDENING_GATE7_RUN5_PUBLIC_CANARY_R1_BLOCKED_RECEIPT.md","sha256":"3ea10b67843fa58797a115f70659ec0757c59b23c59f707a7953957a3f880d3d"},{"bytes":1932,"path":"HARDENING_GATE7_RUN5_PUBLIC_CANARY_R2_BLOCKED_RECEIPT.md","sha256":"ce05d2fd8b96fa5c86ab53613599111aff7c304beb87d66a76f2772cf9a09cad"},{"bytes":1613,"path":"HARDENING_GATE7_RUN5_PUBLIC_CANARY_R2_DIAGNOSIS_AMENDMENT.md","sha256":"fc0a0b92fdc6213ca89ecfc4ab9092a7ef966cb2fb9949815fa9d744f1d131d2"},{"bytes":2303,"path":"HARDENING_GATE7_RUN5_PUBLIC_CANARY_R3_BLOCKED_RECEIPT.md","sha256":"654138f8004f0d02956ceaa4fa6624a3ed35cfac2f878a1c86eb2b0c1d070f86"},{"bytes":2651,"path":"HARDENING_GATE7_RUN5_PUBLIC_CANARY_R4_BLOCKED_RECEIPT.md","sha256":"3a2088f2f68f2ba59ecc7a6c6a10ffcb658cddea9522e1ef502b9b1478ac4d74"},{"bytes":2020,"path":"HARDENING_GATE7_RUN5_THRESHOLD_AMENDMENT_R1.md","sha256":"83d208b8ccad0ed8eab7c086c1b916c18fe051660790064121ca66ee960afa8a"},{"bytes":6835,"path":"HARDENING_GATE7_RUN5_THRESHOLD_AMENDMENT_PACKET_R1.md","sha256":"72e89d90f93e8d8b49a7deeb33168956715127fca5365761d2a96aa4e9e83213"},{"bytes":1678,"path":"HARDENING_GATE7_RUN5_THRESHOLD_AMENDMENT_JUDGE_RECEIPT_R1.md","sha256":"71200a94a2faa5d0290ac701b7536d01e73707f8ae8b59ddf8be8a39d841bc9c"},{"bytes":36284,"path":"HARDENING_GATE7_RUN5_LOCAL_PREFLIGHT_RECEIPT_R4.json","sha256":"aafc0f455fb3e232cfd0ac5c5e1d7a395fc59606a20070e955b7665e64ccb914"},{"bytes":6214,"path":"HARDENING_GATE7_RUN5_SOURCE_BINDINGS_R4.json","sha256":"a92a05e513692f41f067ded10cb21181c63651b319d4029c0646b2598ffe342b"},{"bytes":1747,"path":"HARDENING_GATE7_RUN5_PUBLIC_CANARY_GREEN_RECEIPT_R1.json","sha256":"fd920203e54acfd960e0d334d4477a10c931d135d0a1302694fa2526ec3278f0"},{"bytes":2169,"path":"HARDENING_GATE7_RUN5_SCHEDULE_R1.json","sha256":"656738ef2eba7b7e3afa6dba37cac1f6417d6436889e64f1af3ef236961f6f43"},{"bytes":1553,"path":"HARDENING_GATE7_EXPANDED_THRESHOLDS_R1.json","sha256":"3b048cc3ed8411158cad56914f87f906748364f58baba1267cb59902c529165a"},{"bytes":1549,"path":"HARDENING_GATE7_RUN5_THRESHOLDS_R2.json","sha256":"5c29cda7557a90360e42440def1dd34be66977c217c206214545a3870b33deab"},{"bytes":1544,"path":"HARDENING_GATE7_RUN4_VECTOR_TIMEOUT_AMENDMENT_R2.md","sha256":"36e733007976df0b3534a767e66d917a15777cdd8cfab6c3bb19af5744b4995f"},{"bytes":45335,"path":"hardening-gate7/live_bulk_controller.py","sha256":"1007c219258f3bcbe9ca13e01e21c1e84da5f08646bb7294cb1ed9f7fcc89067"},{"bytes":5031,"path":"hardening-gate7/run4_evidence_custody.py","sha256":"4990f41a7f9e4522ee9a8c32fe6f47815cb8da1e4130c7b240fada4a17fd3dee"},{"bytes":6063,"path":"hardening-gate7/run4_track_gate.py","sha256":"5c8abdf600475826317d1fecfeef66dcaa8a423f99e1bcdb9d7522bef3e072c7"},{"bytes":4598,"path":"hardening-gate7/prepare_hidden_campaign.py","sha256":"17f1a70d3565643170c497345210e466e72511b0e77981779c84bd8ceb5908f7"},{"bytes":9034,"path":"hardening-gate7/build_expanded_bundle.py","sha256":"7d5e890889d41e7bb6c9620ecb6c59d90498fe0d98e385785f3586f43b177ee9"},{"bytes":7755,"path":"hardening-gate7/freeze_run5_public_canary.py","sha256":"d8c3351424321b431c0d3c762893bf913512c24ab5e75e77ee038af2ea1c0506"},{"bytes":5826,"path":"p9-cloud/migrations/001_cloud.sql","sha256":"b17d93fe6c7236c4498f85cc0c5012f9967ddd8c384ed61c853b901dba539f59"},{"bytes":553,"path":"p9-cloud/migrations/003_collision_safe_vector_digest.sql","sha256":"d4696b355525454158818d29c4c8d6f3fa317e549a5bd32fb184eb008119d660"}],"packet_parent_commit":"14418bc29682c543fde1abd49affb65e0e29c874","preflight_contract_sha256":"6131faf2b309ec835b618c4f5523fca6dbe431d32c4e3397d07dee9a35a6978e","prior_public_canaries_blocked":4,"product_candidate":"1c483b1930e629c9ecb6d73418b9554897dc08ad","public_canary_receipt_sha256":"90ebc225abce60f7bb1ab2eca407419e06aa9e78667ded631a0b68d7725b4b18","repair_commit":"9f76ece0e1aa98ac5bf037299ce1547c9c534aab","run4_state":"IMMUTABLE_BLOCKED","run5_hidden_seed_exists":false,"run5_worker_created":false,"schedule_sha256":"656738ef2eba7b7e3afa6dba37cac1f6417d6436889e64f1af3ef236961f6f43","source_bindings_sha256":"bda2ba096003c3adf1622b1187c0d6d16c48c4b660af382403fe0268a3e300bc","threshold_amendment_judges":"GLM_5_2_GREEN; AGY_GREEN; SAME_HASH","threshold_amendment_packet_sha256":"72e89d90f93e8d8b49a7deeb33168956715127fca5365761d2a96aa4e9e83213","thresholds_sha256":"5c29cda7557a90360e42440def1dd34be66977c217c206214545a3870b33deab","version":"hardening-gate7-run5-preflight-bindings-v1"}
```
