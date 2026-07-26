"""P9 pure standard-library Lambda evaluator for the bounded offline slice.

The handler is a pure function from a validated request to an ADVISORY-only
response. It derives bounded structured observations from declared numeric and
boolean feature evidence. It never emits or decides PROMOTE, REFUSE, or
INVALID, never mutates policy, never chooses a destination or tool, never
executes code, and never invokes another agent or service.

This module performs no network, subprocess, filesystem, environment,
credential, model, randomness, or clock access. It imports only the Python
standard library plus the local strict records schema. Any malformed, unknown,
wrongly-typed, stale, oversized, or non-canonical input fails closed by raising
a CloudError carrying a stable reason code rather than emitting a decision.
"""
from __future__ import annotations

from typing import Any

from records import (
    CloudError,
    make_response,
    validate_request,
)

# Fixed relevance threshold below which a low-context advisory signal is noted.
CONTEXT_LOW_THRESHOLD = 0.5


def derive_observations(request: dict[str, Any]) -> list[dict[str, Any]]:
    """Deterministically derive advisory observations from declared features.

    Observations describe signals present in the evidence. They are advisory
    notes only; none of them is a promotion, refusal, or invalid decision, and
    none directs a policy, destination, or tool action.
    """
    features = request["features"]
    observations: list[dict[str, Any]] = []

    if features["policy_veto"]:
        observations.append({
            "code": "POLICY_VETO_SIGNAL",
            "severity": "HIGH",
            "message": "policy veto signal present in the declared evidence",
        })
    if features["tampered"]:
        observations.append({
            "code": "TAMPER_SIGNAL",
            "severity": "HIGH",
            "message": "tamper signal present in the declared evidence",
        })
    if features["unsafe"]:
        observations.append({
            "code": "UNSAFE_SIGNAL",
            "severity": "HIGH",
            "message": "unsafe signal present in the declared evidence",
        })
    if features["warrant_consumed"]:
        observations.append({
            "code": "WARRANT_CONSUMED_SIGNAL",
            "severity": "MEDIUM",
            "message": "one-use warrant already marked consumed in the evidence",
        })
    if not features["quorum_met"]:
        observations.append({
            "code": "QUORUM_SHORTFALL_SIGNAL",
            "severity": "MEDIUM",
            "message": "declared evidence indicates quorum was not met",
        })
    if features["context_relevance"] < CONTEXT_LOW_THRESHOLD:
        observations.append({
            "code": "CONTEXT_LOW_SIGNAL",
            "severity": "LOW",
            "message": "bounded context relevance below the declared threshold",
        })

    observations.append({
        "code": "EVALUATION_COMPLETE",
        "severity": "INFO",
        "message": (
            "advisory evaluation complete over "
            f"{features['event_count']} events, "
            f"{features['approvals']} approvals, "
            f"{features['refusals']} negative signals"
        ),
    })
    return observations


def evaluate(request: Any) -> dict[str, Any]:
    """Validate the request and return an ADVISORY-only response.

    Fails closed by raising CloudError on any malformed, unknown, stale,
    oversized, or non-canonical input. On success returns a response whose
    status is always ADVISORY and which carries no authority field.
    """
    validate_request(request)
    observations = derive_observations(request)
    return make_response(request, observations)


def lambda_handler(event: Any, context: Any) -> dict[str, Any]:
    """AWS Lambda entry point. The runtime context is accepted but never read.

    The handler is a pure function of the event payload only; it ignores the
    invocation context so that no environment, credential, or invocation
    metadata can influence the deterministic advisory output.
    """
    del context  # intentionally unused: pure function of the event payload
    if not isinstance(event, dict):
        raise CloudError("MALFORMED_RECORD")
    return evaluate(event)
