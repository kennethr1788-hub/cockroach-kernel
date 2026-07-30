#!/usr/bin/env python3
"""R4 offline T11 runtime canary with exact pnpm topology reconstruction."""
from __future__ import annotations

import json
import os
from pathlib import Path

import canary_ev1_t11_runtime_r3 as prior


def declared_links(workspace: Path) -> list[dict[str, str]]:
    packages = prior.workspace_packages(workspace)
    root_modules = workspace / "node_modules"
    virtual_hoist = root_modules / ".pnpm" / "node_modules"
    rows: list[dict[str, str]] = []
    for importer_name, importer in sorted(packages.items()):
        if importer == workspace:
            continue
        package = json.loads((importer / "package.json").read_text())
        declarations: dict[str, str] = {}
        for field in ("dependencies", "devDependencies", "optionalDependencies"):
            value = package.get(field, {})
            if not isinstance(value, dict):
                raise prior.CanaryError("WORKSPACE_DEPENDENCY_MAP_INVALID")
            for dependency, specifier in value.items():
                if dependency in declarations and declarations[dependency] != specifier:
                    raise prior.CanaryError("WORKSPACE_DEPENDENCY_SPECIFIER_CONFLICT")
                declarations[dependency] = specifier
        for dependency, specifier in sorted(declarations.items()):
            relative_name = Path(*dependency.split("/"))
            if dependency in packages:
                if not isinstance(specifier, str) or not specifier.startswith("workspace:"):
                    raise prior.CanaryError("LOCAL_DEPENDENCY_NOT_WORKSPACE_BOUND")
                target = packages[dependency]
                source = "workspace"
            elif (root_modules / relative_name).exists():
                target = root_modules / relative_name
                source = "root-direct"
            else:
                target = virtual_hoist / relative_name
                source = "virtual-hoist"
            if not target.exists():
                raise prior.CanaryError(f"DECLARED_DEPENDENCY_TARGET_MISSING:{importer_name}:{dependency}")
            link = importer / "node_modules" / relative_name
            link.parent.mkdir(parents=True, exist_ok=True)
            if link.exists() or link.is_symlink():
                raise prior.CanaryError("DECLARED_DEPENDENCY_LINK_ALREADY_EXISTS")
            relative = os.path.relpath(target, link.parent)
            os.symlink(relative, link)
            rows.append(
                {
                    "dependency": dependency,
                    "importer": importer.relative_to(workspace).as_posix() or ".",
                    "link": link.relative_to(workspace).as_posix(),
                    "source": source,
                    "specifier": str(specifier),
                    "target": relative,
                }
            )
    return rows


def main() -> int:
    prior.CAMPAIGN = prior.ROOT / ".ev1-runtime" / "EV1-T11" / "canary-r4"
    prior.declared_links = declared_links
    code = prior.main()
    receipt = prior.CAMPAIGN / "CANARY_RECEIPT.json"
    raw_r3_engine = receipt.read_bytes()
    prior.atomic(prior.CAMPAIGN / "CANARY_RECEIPT_R3_ENGINE.json", raw_r3_engine)
    body = json.loads(raw_r3_engine)
    body.pop("receipt_sha256", None)
    body["version"] = "ev1-t11-runtime-canary-v4"
    body["status"] = body["status"].replace("CANARY_R3_", "CANARY_R4_")
    body["r3_engine_receipt_file_sha256"] = prior.digest(raw_r3_engine)
    body["topology_resolution"] = ["workspace", "root-direct", "virtual-hoist"]
    receipt_hash = prior.digest(body)
    raw = prior.canonical(dict(body, receipt_sha256=receipt_hash)) + b"\n"
    prior.atomic(receipt, raw)
    print(
        prior.canonical(
            {
                "file_sha256": prior.digest(raw),
                "receipt_sha256": receipt_hash,
                "status": body["status"],
            }
        ).decode()
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
