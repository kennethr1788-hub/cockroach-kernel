#!/usr/bin/env python3
"""Terminate one recovery process after durable one-use consumption."""
from __future__ import annotations

import argparse

from cockroach_kernel import recovery_surface


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in (
        "request", "sandbox_root", "workspace", "representation_root",
        "custody_root", "output_root",
    ):
        parser.add_argument("--" + name.replace("_", "-"), required=True)
    args = parser.parse_args()
    try:
        recovery_surface.execute_recovery(
            request_path=args.request,
            sandbox_root=args.sandbox_root,
            workspace=args.workspace,
            representation_root=args.representation_root,
            custody_root=args.custody_root,
            output_root=args.output_root,
            fault="after-consume",
        )
    except recovery_surface.SurfaceError as exc:
        if str(exc) == "PROMOTION_INTERRUPTED":
            return 23
        raise
    return 24


if __name__ == "__main__":
    raise SystemExit(main())
