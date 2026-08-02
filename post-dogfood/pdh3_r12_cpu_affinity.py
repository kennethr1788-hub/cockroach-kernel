#!/usr/bin/env python3
"""Prospective effective-vCPU and Linux CPU-affinity contract for PDH-3 R12."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any, Callable, Iterable


MIN_EFFECTIVE_VCPUS = 16
MIN_PROVIDER_MEMORY_GIB = 94
GIB_PER_EFFECTIVE_VCPU = 4


class AffinityError(RuntimeError):
    """Stable affinity-contract failure."""


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def effective_vcpu_plan(provider_vcpus: int, provider_memory_gib: int) -> dict[str, Any]:
    if (
        isinstance(provider_vcpus, bool)
        or isinstance(provider_memory_gib, bool)
        or not isinstance(provider_vcpus, int)
        or not isinstance(provider_memory_gib, int)
        or provider_vcpus < MIN_EFFECTIVE_VCPUS
        or provider_memory_gib < MIN_PROVIDER_MEMORY_GIB
    ):
        raise AffinityError("PROVIDER_SHAPE_INSUFFICIENT")
    memory_bound = provider_memory_gib // GIB_PER_EFFECTIVE_VCPU
    effective = min(provider_vcpus, memory_bound)
    if effective < MIN_EFFECTIVE_VCPUS:
        raise AffinityError("EFFECTIVE_VCPU_LIMIT_INSUFFICIENT")
    body = {
        "version": "ck-pdh3-r12-effective-vcpu-plan-v1",
        "provider_vcpus": provider_vcpus,
        "provider_memory_gib": provider_memory_gib,
        "gib_per_effective_vcpu": GIB_PER_EFFECTIVE_VCPU,
        "memory_bound_vcpus": memory_bound,
        "effective_vcpu_limit": effective,
        "affinity_cap_required": effective < provider_vcpus,
        "ratio_preserved": provider_memory_gib >= effective * GIB_PER_EFFECTIVE_VCPU,
    }
    return {**body, "plan_sha256": digest(body)}


def _cpu_record(cpus: Iterable[int]) -> dict[str, Any]:
    values = sorted(set(cpus))
    if not values or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in values):
        raise AffinityError("CPU_SET_INVALID")
    return {
        "count": len(values),
        "cpus": values,
        "cpus_sha256": digest(values),
    }


def apply_effective_vcpu_limit(
    expected: int,
    *,
    getter: Callable[[int], set[int]] | None = None,
    setter: Callable[[int, set[int]], None] | None = None,
) -> dict[str, Any]:
    if sys.platform != "linux" or expected < MIN_EFFECTIVE_VCPUS:
        raise AffinityError("LINUX_AFFINITY_REQUIRED")
    get = getter or getattr(os, "sched_getaffinity", None)
    set_value = setter or getattr(os, "sched_setaffinity", None)
    if get is None or set_value is None:
        raise AffinityError("AFFINITY_API_UNAVAILABLE")
    before = _cpu_record(get(0))
    if before["count"] < expected:
        raise AffinityError("AFFINITY_SOURCE_TOO_SMALL")
    target_values = set(before["cpus"][:expected])
    target = _cpu_record(target_values)
    set_value(0, target_values)
    after = _cpu_record(get(0))
    if after["cpus"] != target["cpus"] or after["count"] != expected:
        raise AffinityError("AFFINITY_APPLY_MISMATCH")
    body = {
        "version": "ck-pdh3-r12-affinity-apply-v1",
        "before": before,
        "target": target,
        "after": after,
        "exact": True,
    }
    return {**body, "receipt_sha256": digest(body)}


def verify_current_affinity(
    expected: int,
    *,
    pid: int = 0,
    getter: Callable[[int], set[int]] | None = None,
) -> dict[str, Any]:
    if sys.platform != "linux" or expected < MIN_EFFECTIVE_VCPUS:
        raise AffinityError("LINUX_AFFINITY_REQUIRED")
    get = getter or getattr(os, "sched_getaffinity", None)
    if get is None:
        raise AffinityError("AFFINITY_API_UNAVAILABLE")
    observed = _cpu_record(get(pid))
    if observed["count"] != expected:
        raise AffinityError("AFFINITY_VERIFY_MISMATCH")
    body = {
        "version": "ck-pdh3-r12-affinity-verify-v1",
        "pid": pid,
        "expected": expected,
        "observed": observed,
        "exact": True,
    }
    return {**body, "receipt_sha256": digest(body)}

