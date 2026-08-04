"""Deterministic replay, receipt inspection, and typed recovery CLI."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Sequence


MAX_RECEIPT_BYTES = 65_536
RECEIPT_VERSION = "ck-cli-receipt-v1"
RECEIPT_FIELDS = {
    "version",
    "replay_label",
    "branch",
    "verdict",
    "reason",
    "provable_state",
    "action_taken",
    "next_safe_action",
    "source_result_hash",
    "source_receipt_hash",
    "fresh_context_continued",
    "fresh_context_reason",
    "receipt_hash",
}


def _runtime() -> Any:
    """Import the packaged P9 runtime without changing its authority logic."""
    try:
        import p9_runtime

        runtime_path = Path(p9_runtime.__file__).resolve().parent
    except ModuleNotFoundError:
        runtime_path = Path(__file__).resolve().parents[1] / "p9-cloud"
        if not runtime_path.is_dir():
            raise RuntimeError("P9_RUNTIME_UNAVAILABLE")
    runtime_dir = str(runtime_path)
    if runtime_dir not in sys.path:
        sys.path.insert(0, runtime_dir)
    import run_offline

    return run_offline


def canonical_json(value: Any) -> bytes:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("RECEIPT_MALFORMED") from exc
    if len(raw) > MAX_RECEIPT_BYTES:
        raise ValueError("RECEIPT_TOO_LARGE")
    return raw


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
    return hashlib.sha256(raw).hexdigest()


def _receipt_body(result: dict[str, Any], branch: str) -> dict[str, Any]:
    if branch == "promote":
        verdict = result["local_verdict"]
        reason = result["local_reason"]
        continued = result["fresh_context"]
        fresh_reason = result["fresh_context_reason"]
        action = "VERIFIED_CONTINUATION_RECONSTRUCTED"
        next_action = "Inspect the canonical receipt or continue from the verified capsule."
        state = {
            "capsule_hash": result["capsule_hash"],
            "declared_hash": result["declared_hash"],
            "projection_state": result["projection_state"],
            "task_id": result["task_id"],
        }
    elif branch == "refuse":
        verdict = result["tampered_verdict"]
        reason = result["tampered_reason"]
        continued = False
        fresh_reason = "CAPSULE_NOT_PROMOTED"
        action = "NONE"
        next_action = "Inspect the receipt and provide an untampered declared candidate."
        state = {
            "declared_hash": result["declared_hash"],
            "rejected_candidate": "tampered_replay_vector",
            "task_id": result["task_id"],
        }
    else:
        raise ValueError("BRANCH_INVALID")
    return {
        "version": RECEIPT_VERSION,
        "replay_label": "KEYLESS_LOCAL_REPLAY",
        "branch": branch,
        "verdict": verdict,
        "reason": reason,
        "provable_state": state,
        "action_taken": action,
        "next_safe_action": next_action,
        "source_result_hash": result["result_hash"],
        "source_receipt_hash": result["receipt_hash"],
        "fresh_context_continued": continued,
        "fresh_context_reason": fresh_reason,
    }


def make_receipt(result: dict[str, Any], branch: str) -> dict[str, Any]:
    body = _receipt_body(result, branch)
    receipt = dict(body, receipt_hash=digest(body))
    validate_receipt(receipt)
    return receipt


def validate_receipt(receipt: Any) -> dict[str, Any]:
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_FIELDS:
        raise ValueError("RECEIPT_FIELDS_INVALID")
    if receipt["version"] != RECEIPT_VERSION:
        raise ValueError("RECEIPT_VERSION_UNSUPPORTED")
    if receipt["replay_label"] != "KEYLESS_LOCAL_REPLAY":
        raise ValueError("REPLAY_LABEL_INVALID")
    if receipt["branch"] not in {"promote", "refuse"}:
        raise ValueError("RECEIPT_BRANCH_INVALID")
    if receipt["verdict"] not in {"PROMOTE", "REFUSE", "INVALID"}:
        raise ValueError("RECEIPT_VERDICT_INVALID")
    expected = "PROMOTE" if receipt["branch"] == "promote" else "REFUSE"
    if receipt["verdict"] != expected:
        raise ValueError("RECEIPT_BRANCH_VERDICT_MISMATCH")
    if not isinstance(receipt["reason"], str) or not receipt["reason"]:
        raise ValueError("RECEIPT_REASON_INVALID")
    if not isinstance(receipt["provable_state"], dict):
        raise ValueError("RECEIPT_STATE_INVALID")
    if receipt["branch"] == "refuse" and receipt["action_taken"] != "NONE":
        raise ValueError("REFUSAL_ACTION_INVALID")
    for key in ("source_result_hash", "source_receipt_hash", "receipt_hash"):
        value = receipt[key]
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError("RECEIPT_HASH_INVALID")
        try:
            int(value, 16)
        except ValueError as exc:
            raise ValueError("RECEIPT_HASH_INVALID") from exc
    body = {key: receipt[key] for key in receipt if key != "receipt_hash"}
    if receipt["receipt_hash"] != digest(body):
        raise ValueError("RECEIPT_HASH_MISMATCH")
    canonical_json(receipt)
    return receipt


def _atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink() or (path.exists() and path.is_symlink()):
        raise ValueError("OUTPUT_SYMLINK_REFUSED")
    raw = canonical_json(value) + b"\n"
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def run_demo(output_root: Path) -> dict[str, Any]:
    result = _runtime().run()
    promotion = make_receipt(result, "promote")
    refusal = make_receipt(result, "refuse")
    _atomic_write(output_root / "promotion-receipt.json", promotion)
    _atomic_write(output_root / "refusal-receipt.json", refusal)
    summary = {
        "version": "ck-cli-demo-v1",
        "replay_label": "KEYLESS_LOCAL_REPLAY",
        "network_used": False,
        "credentials_used": False,
        "promotion": promotion,
        "promotion_receipt": "promotion-receipt.json",
        "refusal": refusal,
        "refusal_receipt": "refusal-receipt.json",
        "source_result_hash": result["result_hash"],
    }
    summary["summary_hash"] = digest(summary)
    return summary


def _format_block(label: str, receipt: dict[str, Any], receipt_path: str) -> list[str]:
    state = canonical_json(receipt["provable_state"]).decode("utf-8")
    return [
        label,
        f"VERDICT: {receipt['verdict']}",
        f"REASON: {receipt['reason']}",
        f"PROVABLE_STATE: {state}",
        f"ACTION_TAKEN: {receipt['action_taken']}",
        f"NEXT_SAFE_ACTION: {receipt['next_safe_action']}",
        f"RECEIPT: {receipt_path}",
    ]


def _demo_command(args: argparse.Namespace) -> int:
    output_root = Path(args.output_root).resolve()
    summary = run_demo(output_root)
    if args.json:
        print(canonical_json(summary).decode("utf-8"))
        return 0
    lines = ["MODE: KEYLESS_LOCAL_REPLAY"]
    lines.extend(
        _format_block(
            "PROMOTION",
            summary["promotion"],
            str(output_root / summary["promotion_receipt"]),
        )
    )
    lines.extend(
        _format_block(
            "REFUSAL",
            summary["refusal"],
            str(output_root / summary["refusal_receipt"]),
        )
    )
    if args.explain:
        lines.extend(
            [
                "AUTHORITY: deterministic local P4 verifier",
                "CLOUD_ROLE: captured advisory evidence only",
                "NETWORK_USED: false",
                "CREDENTIALS_USED: false",
                f"SOURCE_RESULT_HASH: {summary['source_result_hash']}",
                f"SUMMARY_HASH: {summary['summary_hash']}",
            ]
        )
    print("\n".join(lines))
    return 0


def _inspect_command(args: argparse.Namespace) -> int:
    path = Path(args.receipt)
    if path.is_symlink() or not path.is_file():
        raise ValueError("RECEIPT_PATH_INVALID")
    raw = path.read_bytes()
    if len(raw) > MAX_RECEIPT_BYTES + 1:
        raise ValueError("RECEIPT_TOO_LARGE")
    if not raw.endswith(b"\n"):
        raise ValueError("RECEIPT_NOT_CANONICAL")
    try:
        receipt = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("RECEIPT_JSON_INVALID") from exc
    validate_receipt(receipt)
    if raw != canonical_json(receipt) + b"\n":
        raise ValueError("RECEIPT_NOT_CANONICAL")
    print(canonical_json(receipt).decode("utf-8"))
    return 0


def _recover_command(args: argparse.Namespace) -> int:
    from cockroach_kernel.recovery_surface import run_cli

    return run_cli(args)


def _preview_command(args: argparse.Namespace) -> int:
    from cockroach_kernel.recovery_preview import preview_recovery

    report = preview_recovery(
        request_path=args.request,
        sandbox_root=args.sandbox_root,
        workspace=args.workspace,
        representation_root=args.representation_root,
        custody_root=args.custody_root,
        output_root=args.output_root,
    )
    print(canonical_json(report).decode("utf-8"))
    return 0


def _inspect_memory_command(args: argparse.Namespace) -> int:
    from cockroach_kernel.memory_skill import inspect_snapshot

    path = Path(args.input)
    if path.is_symlink() or not path.is_file():
        raise ValueError("SNAPSHOT_PATH_INVALID")
    raw = path.read_bytes()
    if len(raw) > 65_536:
        raise ValueError("SNAPSHOT_TOO_LARGE")
    try:
        snapshot = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("SNAPSHOT_JSON_INVALID") from exc
    print(canonical_json(inspect_snapshot(snapshot)).decode("utf-8"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cockroach-kernel")
    subcommands = parser.add_subparsers(dest="command", required=True)
    demo = subcommands.add_parser("demo", help="run the deterministic keyless replay")
    format_group = demo.add_mutually_exclusive_group()
    format_group.add_argument("--explain", action="store_true")
    format_group.add_argument("--json", action="store_true")
    demo.add_argument("--output-root", default="cockroach-kernel-evidence")
    demo.set_defaults(handler=_demo_command)
    inspect = subcommands.add_parser("inspect", help="validate a canonical receipt")
    inspect.add_argument("receipt")
    inspect.set_defaults(handler=_inspect_command)
    recover = subcommands.add_parser(
        "recover",
        help="recover exact bytes from a declared surviving representation",
    )
    recover.add_argument("--request", required=True, help="canonical typed recovery request")
    recover.add_argument(
        "--sandbox-root",
        required=True,
        help="existing disposable envelope containing every declared root",
    )
    recover.add_argument("--workspace", required=True, help="existing successor workspace")
    recover.add_argument(
        "--representation-root",
        required=True,
        help="existing root containing hash-bound surviving representations",
    )
    recover.add_argument(
        "--custody-root",
        required=True,
        help="existing root for persistent one-use warrant state",
    )
    recover.add_argument(
        "--output-root",
        required=True,
        help="existing empty root for canonical result records",
    )
    recover.set_defaults(handler=_recover_command)
    preview = subcommands.add_parser(
        "preview",
        help="project recovery outcome without consuming custody or mutating the workspace",
    )
    preview.add_argument("--request", required=True, help="canonical typed recovery request")
    preview.add_argument("--sandbox-root", required=True)
    preview.add_argument("--workspace", required=True)
    preview.add_argument("--representation-root", required=True)
    preview.add_argument("--custody-root", required=True)
    preview.add_argument("--output-root", required=True)
    preview.set_defaults(handler=_preview_command)
    inspect_memory = subcommands.add_parser(
        "inspect-memory",
        help="inspect a bounded Cockroach receipt/vector snapshot without authority",
    )
    inspect_memory.add_argument("--input", required=True, help="bounded JSON snapshot")
    inspect_memory.set_defaults(handler=_inspect_memory_command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, ValueError, RuntimeError) as exc:
        code = str(exc) or exc.__class__.__name__
        print(f"VERDICT: INVALID\nREASON: {code}\nACTION_TAKEN: NONE", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
