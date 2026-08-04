"""Deployable Lambda entrypoint for the Cockroach-backed live canary.

The cloud response remains advisory.  The local P4 verifier invoked by
``cockroach_kernel.http_api`` remains the sole authority for PROMOTE/REFUSE.
"""
from __future__ import annotations

from typing import Any

from cockroach_kernel.http_api import handler as _handler


def lambda_handler(event: Any, context: Any) -> dict[str, Any]:
    return _handler(event, context)
