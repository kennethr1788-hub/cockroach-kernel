#!/usr/bin/env python3
"""Gate 6 R3 seccomp-isolated measured campaign and evidence aggregator."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import socket
import sys


HERE = Path(__file__).resolve().parent


def load_r2():
    path = HERE / "run_campaign.py"
    spec = importlib.util.spec_from_file_location("gate6_campaign_r2_base", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("R2_BASE_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_r2()
R2_VALIDATE_MANIFEST = base.validate_manifest


def file_hash(path: Path) -> str:
    return base.file_hash(path)


def proc_status() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key] = value.strip()
    return values


def validate_isolation() -> dict[str, object]:
    if os.getuid() == 0 or os.geteuid() == 0:
        raise base.CampaignError("HOST_USER_MUST_BE_UNPRIVILEGED")
    status = proc_status()
    if int(status.get("CapEff", "-1"), 16) != 0:
        raise base.CampaignError("EFFECTIVE_CAPABILITIES_NOT_ZERO")
    if status.get("NoNewPrivs") != "1" or status.get("Seccomp") != "2":
        raise base.CampaignError("SECCOMP_KERNEL_STATE_INVALID")
    path_text = os.environ.get("CK_GATE6_ISOLATION_ATTESTATION", "")
    claimed = os.environ.get("CK_GATE6_ISOLATION_ATTESTATION_SHA256", "")
    path = Path(path_text)
    if not path.is_absolute() or not path.is_file() or file_hash(path) != claimed:
        raise base.CampaignError("ISOLATION_ATTESTATION_BINDING_INVALID")
    record = json.loads(path.read_bytes())
    body = {key: value for key, value in record.items()
            if key != "attestation_sha256"}
    if (record.get("attestation_sha256") != base.digest(body) or
            record.get("attestation_sha256") != claimed or
            record.get("uid") == 0 or record.get("euid") == 0 or
            int(record.get("cap_eff", "-1"), 16) != 0 or
            record.get("no_new_privs") != 1 or
            record.get("seccomp_mode") != 2 or
            record.get("network_socket_probe_result") != "DENIED_EPERM" or
            record.get("exec_canary") != "PASS" or
            record.get("inherited_socket_fds") != []):
        raise base.CampaignError("ISOLATION_ATTESTATION_CONTENT_INVALID")
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError as error:
        if error.errno != 1:
            raise base.CampaignError("NETWORK_DENIAL_WRONG_ERRNO") from error
    else:
        raise base.CampaignError("NETWORK_DENIAL_NOT_ENFORCED")
    return record


def validate_manifest_r3(manifest: object):
    if not isinstance(manifest, dict):
        raise base.CampaignError("MANIFEST_TYPE_INVALID")
    if manifest.get("execution_revision") != "R3":
        raise base.CampaignError("MANIFEST_REVISION_INVALID")
    translated = dict(manifest)
    translated["execution_revision"] = "R2"
    translated_body = {key: value for key, value in translated.items()
                       if key != "manifest_sha256"}
    translated["manifest_sha256"] = base.digest(translated_body)
    rows = R2_VALIDATE_MANIFEST(translated)
    original_body = {key: value for key, value in manifest.items()
                     if key != "manifest_sha256"}
    if manifest.get("manifest_sha256") != base.digest(original_body):
        raise base.CampaignError("MANIFEST_HASH_MISMATCH")
    return rows


def main() -> int:
    # The R2 engine remains byte-preserved; only its R2 revision check and
    # unshare wrapper are replaced. Every child inherits this process's filter.
    original_validate = base.validate_manifest
    original_run = base.subprocess.run
    original_aggregate = base.aggregate

    def validate(manifest: object):
        return validate_manifest_r3(manifest)

    def inherited_run(command, *args, **kwargs):
        if isinstance(command, list) and command and str(command[0]).endswith("unshare"):
            command = command[5:]
        return original_run(command, *args, **kwargs)

    def aggregate(receipts, raw_sizes, manifest, final_checkpoint):
        translated = dict(manifest)
        translated["execution_revision"] = "R2"
        translated_body = {key: value for key, value in translated.items()
                           if key != "manifest_sha256"}
        translated["manifest_sha256"] = base.digest(translated_body)
        result = original_aggregate(receipts, raw_sizes, translated,
                                    final_checkpoint)
        result["execution_revision"] = "R3"
        result["campaign_id"] = manifest["campaign_id"]
        result["manifest_sha256"] = manifest["manifest_sha256"]
        result["limitations"].append(
            "KERNEL_SECCOMP_NETWORK_DENIAL_NOT_NETWORK_NAMESPACE"
        )
        result["aggregate_sha256"] = base.digest({
            key: value for key, value in result.items()
            if key != "aggregate_sha256"
        })
        return result

    if "--validate-only" not in sys.argv[1:]:
        validate_isolation()
    base.validate_manifest = validate
    base.subprocess.run = inherited_run
    base.aggregate = aggregate
    original_argv = sys.argv
    try:
        sys.argv = [str(HERE / "run_campaign.py"), *sys.argv[1:]]
        return base.main()
    finally:
        sys.argv = original_argv
        base.validate_manifest = original_validate
        base.subprocess.run = original_run
        base.aggregate = original_aggregate


if __name__ == "__main__":
    raise SystemExit(main())
