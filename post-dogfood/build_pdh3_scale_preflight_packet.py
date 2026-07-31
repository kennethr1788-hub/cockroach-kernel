#!/usr/bin/env python3
"""Build the sanitized, byte-complete PDH-3 RunPod preflight packet."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".pdh3-runtime" / "preflight-r4"
PACKET = ROOT / "PDH_3_SCALE_RUNPOD_PREFLIGHT_PACKET_R4.md"
BINDINGS = ROOT / "PDH_3_SCALE_RUNPOD_PREFLIGHT_BINDINGS_R4.json"

LAUNCH_WINDOW_START = "2026-07-31T04:00:00Z"
LAUNCH_WINDOW_END = "2026-07-31T05:00:00Z"
STOP_AFTER = "2026-08-01T07:45:00Z"
TERMINATE_AFTER = "2026-08-01T08:00:00Z"
STOP_EPOCH = 1_785_570_300
TERMINATE_EPOCH = 1_785_571_200

SOURCES = (
    "post-dogfood/pdh3_scale_contract.py",
    "post-dogfood/run_pdh3_scale_campaign.py",
    "post-dogfood/build_pdh3_scale_bundle.py",
    "s2-soak/lifecycle_guard.py",
)

RECEIPTS = (
    "PDH_3_SCALE_AUTHORIZATION_RECEIPT_R1.md",
    "PDH_3_SCALE_LOCAL_SMOKE_PACKET_R1.md",
    "PDH_3_SCALE_LOCAL_SMOKE_REPORT_R1.md",
    "PDH_3_SCALE_BUNDLE_SCAN_RECEIPT_R4.md",
    "PDH_3_SCALE_RUNPOD_ATTEMPT_01_RECEIPT.md",
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_binding(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    raw = path.read_bytes()
    return {"path": relative, "bytes": len(raw), "sha256": digest(raw)}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fenced(relative: str) -> str:
    language = "python" if relative.endswith(".py") else "text"
    return f"### `{relative}`\n\n```{language}\n{(ROOT / relative).read_text(encoding='utf-8')}\n```"


def main() -> int:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    authorization = digest((ROOT / RECEIPTS[0]).read_bytes())
    bundle = read_json(RUNTIME / "bundle-receipt.json")
    active = read_json(RUNTIME / "runpod-active-before.json")
    gpu_inventory = read_json(RUNTIME / "runpod-gpu-inventory.json")
    l40s = [item for item in gpu_inventory if item.get("gpuId") == "NVIDIA L40S"]
    template = read_json(ROOT / ".pdh3-runtime" / "preflight-r2" / "runpod-template.json")
    guard_proof = read_json(
        ROOT / ".pdh3-runtime" / "preflight-r1" / "lifecycle-guard-proof.json"
    )
    extracted = read_json(RUNTIME / "extracted-smoke" / "verifier" / "aggregate.json")
    bindings: dict[str, Any] = {
        "version": "ck-pdh3-scale-preflight-bindings-v1",
        "parent_commit": head,
        "product_candidate": "1c483b1930e629c9ecb6d73418b9554897dc08ad",
        "plan_sha256": "bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24",
        "authorization_sha256": authorization,
        "source_files": [file_binding(name) for name in SOURCES],
        "receipt_files": [file_binding(name) for name in RECEIPTS],
        "bundle": {
            "archive_sha256": bundle["archive_sha256"],
            "archive_bytes": bundle["archive_bytes"],
            "receipt_sha256": bundle["receipt_sha256"],
            "source_set_sha256": bundle["manifest"]["source_set_sha256"],
            "manifest_sha256": bundle["manifest"]["manifest_sha256"],
        },
        "runpodctl": {
            "version": "2.7.2-309512b",
            "sha256": "a016e442fdf12e4642ad3425ea6d624a40882d77accdfa043b5e40a4fd08d037",
        },
        "provider_state": {
            "active_inventory": active,
            "l40s_offer": l40s,
            "official_template": template,
            "official_secure_l40s_compute_usd_hour": 0.99,
            "container_disk_usd_gb_month": 0.10,
        },
        "local_smoke": {
            "campaign": "ck-pdh3-scale-local-r4",
            "result_sha256": "14895d952dec265a3348b9a5320fc4e48a7931dfce10a3a1efad3c0ed64f2688",
            "manifest_sha256": "19feefd9ce5d8371a1a3af3b44b6fee7aa45951b5576e81231c15c2e40b80f00",
            "teardown_sha256": "41c8ec39e13a46bc13e774b2559e29e1f5a32f621fb9faa305b1498e1ec133a0",
        },
        "extracted_bundle_smoke": {
            "green": extracted["green"],
            "executions": extracted["measured_executions"],
            "aggregate_sha256": extracted["aggregate_sha256"],
        },
        "lifecycle_guard_proof": {
            "status": guard_proof["status"],
            "bound": guard_proof["bound"],
            "teardown": guard_proof["teardown"],
            "state_absent": guard_proof["state_absent"],
            "terminal_hash": guard_proof["terminal_hash"],
        },
        "launch_window": {
            "start": LAUNCH_WINDOW_START,
            "end": LAUNCH_WINDOW_END,
            "stop_after": STOP_AFTER,
            "terminate_after": TERMINATE_AFTER,
            "stop_epoch": STOP_EPOCH,
            "terminate_epoch": TERMINATE_EPOCH,
        },
    }
    bindings["bindings_sha256"] = digest(canonical(bindings))
    BINDINGS.write_bytes(canonical(bindings))

    packet = f"""# PDH-3 Production-Shaped Scale RunPod Preflight Packet R4

## Judge task

Act only as an independent, non-authoring preflight judge. Evaluate whether the
exact bounded campaign below is safe, internally consistent, evidence-capable,
and ready for one paid worker. Do not write code, redesign the product, invoke
tools, request credentials, or treat missing future measured results as a
preflight defect.

Return one JSON object. A single Markdown `json` fence around that object is
accepted only because the current verified GLM wrapper emits that presentation;
the fence is mechanically stripped and the enclosed bytes must parse exactly:

```json
{{"verdict":"GREEN|NOT_GREEN|BLOCKED","candidate_immutability":"GREEN|NOT_GREEN","workload_and_thresholds":"GREEN|NOT_GREEN","credential_and_data_boundary":"GREEN|NOT_GREEN","lifecycle_and_cost":"GREEN|NOT_GREEN","evidence_and_teardown":"GREEN|NOT_GREEN","blockers":[],"limitations":[]}}
```

`GREEN` is valid only when every named dimension is GREEN and blockers is empty.

## Current authority

- parent evidence commit: `{head}`
- immutable product candidate:
  `1c483b1930e629c9ecb6d73418b9554897dc08ad`
- active plan SHA-256:
  `bbda0c8d5d6273de93977000c9fbb6a4be61602686bc53617d43758fede48c24`
- operator authorization SHA-256: `{authorization}`
- preflight bindings SHA-256: `{bindings["bindings_sha256"]}`
- active paid RunPod inventory before launch: `{json.dumps(active, sort_keys=True)}`

The candidate product commit is frozen. This packet introduces only the
campaign controller, validation, bundle builder, tests, receipts, and lifecycle
evidence. It does not modify the product candidate.

## Stated goal and kill line

Goal: obtain one final production-shaped scale/reliability data point for the
frozen product by running a credential-free, synthetic, 24-hour workload
against a three-node local CockroachDB cluster inside one disposable Secure
Cloud L40S worker.

Kill line: stop and delete the worker on any identity, rate, image, disk,
volume, hash, namespace, evidence, checkpoint, latency, growth, determinism,
cross-task isolation, retry, crash-recovery, cleanup, credential, private-data,
or lifecycle mismatch. No replacement is allowed after the measured workload
begins.

## Exact provider and economic envelope

- RunPod Secure Cloud; one `NVIDIA L40S`; one GPU;
- accepted returned host range: exactly 16 vCPU, 94 through 188 GB RAM,
  and 48 GB VRAM;
- exact image: `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`;
- exposed ports: `22/tcp` only; global networking omitted/disabled;
- 250 GB disposable container disk;
- zero persistent volume and zero network volume;
- official current Secure L40S compute rate ceiling: `$0.99/hour`;
- container disk pricing: `$0.10/GB/month`, approximately `$0.0348/hour`;
- total active-rate ceiling: `$1.10/hour`;
- maximum paid lifetime: 100,800 seconds / 28 hours;
- maximum aggregate campaign charge: `$35.00`;
- conservative 28-hour compute plus container-disk estimate: approximately
  `$28.69`;
- launch window: `{LAUNCH_WINDOW_START}` through `{LAUNCH_WINDOW_END}`;
- provider stop-after: `{STOP_AFTER}`;
- provider terminate-after: `{TERMINATE_AFTER}`;
- local guard stop epoch: `{STOP_EPOCH}`;
- local guard delete epoch: `{TERMINATE_EPOCH}`.

The GPU is not used for model inference. The L40S shape was explicitly selected
and authorized for its current Secure Cloud 16-vCPU/94-GB host allocation and
reliability envelope. The workload is CPU, memory, disk, and database bound.

## Creation command and retry law

For each unique attempt name inside the frozen launch window:

```text
/tmp/runpodctl-v2.7.2-darwin-arm64 pod create
  --cloud-type SECURE
  --compute-type GPU
  --gpu-id "NVIDIA L40S"
  --gpu-count 1
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404
  --name <unique ck-pdh3-scale-r1-aNN name>
  --container-disk-in-gb 250
  --volume-in-gb 0
  --ports 22/tcp
  --stop-after {STOP_AFTER}
  --terminate-after {TERMINATE_AFTER}
  --output json
```

At most eight sequential pre-workload attempts are allowed, with one extant
worker maximum. A failed or mismatched worker must be deleted, followed by
exact-ID absence and empty matching-campaign active inventory, before another
attempt. Three consecutive identical failures stop blind retries. Retry is
allowed only for provider creation/capacity, returned-shape/image/price
mismatch, readiness, SSH, hash-checked transfer, extracted-bundle validation,
or namespace canary failure before measured execution. Any credential/private
data exposure, unbounded price, failed deletion, product/source drift, or
evidence-contract defect ends the campaign. Once measured execution starts,
there is no replacement, restart, extension, or second measured run.

## Worker verification and credential boundary

Before upload, verify exact worker ID/name, Secure Cloud, one L40S, exactly 16
vCPU, RAM between 94 and 188 GB inclusive, one GPU, image, 250 GB container
disk, zero volume/network volume, rate no greater than `$1.10/hour`, and the
frozen stop/terminate request.
Provider deadline readback is recorded if exposed; otherwise retain the exact
creation request/response without claiming readback.

The local exact-ID guard is bound immediately after creation. It hash-pins
runpodctl, checks worker identity on every heartbeat, survives parent-shell
exit, records a hash chain, performs bounded stop/delete retries, and declares
teardown only after exact-ID absence plus empty matching active inventory.

Only the R3 archive and this packet are uploaded. Their hashes are verified
before extraction. No AWS, CockroachDB Cloud, GitHub, package-registry, model,
HOME, client, private, or production credential/data is transferred. SSH is
used only for bounded transfer, start, observation, retrieval, and teardown.
The workload launches in a fresh user/network namespace with loopback enabled
and no external egress. Namespace failure blocks before measured execution.

## Remote canary and measured command

After extraction and hash verification, execute a 60-second reduced canary
through the same controller inside the no-egress namespace. It must prove
three-node startup, seed, workload, 43 verifier executions, one node
crash/restart, exact reconciliation, database drop, closed ports, stopped
processes, and removed generated root.

Only after that canary is GREEN, execute exactly:

```text
PDH3_PACKET_SHA256=<this packet SHA-256>
python3 post-dogfood/run_pdh3_scale_campaign.py
  --binary p2-cleanroom/vendor/cockroach-v26.2.3-linux/cockroach-v26.2.3.linux-amd64/cockroach
  --packet <this exact packet>
  --output /runpod-volume-disabled/ck-pdh3-scale-r1/evidence
  --campaign-id ck-pdh3-scale-r1
  --production
  --duration-seconds 86400
  --checkpoint-seconds 300
  --tasks 500000
  --events-per-task 10
  --receipts-per-task 2
  --vectors 250000
  --max-concurrency 500
  --query-duration-seconds 120
  --seed-batch-tasks 5000
  --setup-timeout-seconds 5400
  --fault-every-checkpoints 12
  --disk-used-fraction-limit 0.70
  --cache 8GiB
  --sql-memory 8GiB
```

The displayed remote path is a disposable container path name only; no RunPod
volume or network volume is attached.

## Workload and direct acceptance thresholds

- three CockroachDB v26.2.3 nodes;
- 500,000 task rows;
- 5,000,000 trajectory-event rows;
- 1,000,000 receipt rows;
- 250,000 task-bound vector rows;
- exactly 9,976 fresh-process verifier executions in 232 batches of 43;
- concurrency stages 10, 50, 100, 250, and 500;
- exactly 288 five-minute checkpoints over 86,400 measured seconds;
- 24 rotating node `SIGKILL`/surviving-query/restart/reconciliation cycles;
- duplicate/idempotency, SQLSTATE 40001 retry, rollback, deterministic verdict,
  quarantine exclusion, stale/malformed/throttled/timeout advice states, and a
  concurrent create/delete cleanup probe;
- zero false promotions, zero cross-task vector links, zero acknowledged write
  loss, zero accepted replays, and zero cleanup residue;
- p99 no greater than 5,000 ms and maximum latency no greater than 10,000 ms;
- database bytes no greater than 100 GiB;
- evidence bytes no greater than 20 GiB;
- container disk occupancy no greater than 70%;
- every canonical checkpoint, journal event, result, manifest, and teardown
  receipt hash-linked and fsynced.

All failures are retained. Results cannot be pooled with prior campaigns and
there is no post-result tuning. A completed command is not success unless every
threshold and teardown check is directly GREEN.

## Closeout

Stop the workload; flush/fsync evidence; archive it; retrieve logs, evidence,
hashes, canary, system inventory, and provider records; verify local hashes
against remote hashes; stop/delete the worker; prove exact-ID absence and empty
campaign active inventory; prove no guard/SSH/transfer/database/watchdog
process remains; reconcile provider billing as available; and write the final
receipt. Exact billing must never be fabricated. A delayed provider billing
record is a disclosed reconciliation limitation, not permission to exceed the
authorized rate/lifetime/cost envelope.

The measured campaign cannot claim GREEN until one final independent GLM
review over the exact frozen final evidence packet is GREEN. This preflight
only authorizes worker creation.

## Evidence already obtained

{(ROOT / "PDH_3_SCALE_AUTHORIZATION_RECEIPT_R1.md").read_text(encoding="utf-8")}

{(ROOT / "PDH_3_SCALE_LOCAL_SMOKE_REPORT_R1.md").read_text(encoding="utf-8")}

{(ROOT / "PDH_3_SCALE_BUNDLE_SCAN_RECEIPT_R4.md").read_text(encoding="utf-8")}

{(ROOT / "PDH_3_SCALE_RUNPOD_ATTEMPT_01_RECEIPT.md").read_text(encoding="utf-8")}

The local smoke used the final controller source but preceded two
contract-only hardenings that pinned production scheduling parameters and the
exact remote image/port boundary. Those hardenings do not alter controller
behavior; they are directly covered by the eight passing unit tests, the
deterministic R3 archive, compile checks, secret scans, and the extracted R3
43-execution verifier smoke.

The detached guard proof is GREEN:

```json
{json.dumps(guard_proof, sort_keys=True)}
```

## Canonical bindings

```json
{canonical(bindings).decode("utf-8")}
```

## Load-bearing source

{chr(10).join(fenced(name) for name in SOURCES)}

## Expected evidence gap

The paid worker, 24-hour result, provider-returned rate/shape, retrieved remote
evidence, teardown, and final audit do not yet exist. That is expected at
preflight. They remain mandatory for the final gate and must not be inferred.
"""
    PACKET.write_text(packet, encoding="utf-8")
    print(
        json.dumps(
            {
                "packet": PACKET.name,
                "packet_sha256": digest(PACKET.read_bytes()),
                "packet_bytes": PACKET.stat().st_size,
                "bindings": BINDINGS.name,
                "bindings_sha256": bindings["bindings_sha256"],
                "parent_commit": head,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
