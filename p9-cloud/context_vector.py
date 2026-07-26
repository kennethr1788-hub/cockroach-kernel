"""P9 deterministic 64-dimensional context vectors.

Synthetic, deterministic, standard library only. A context vector here is a
bounded token-feature hash projection with stable L2 normalization. It is
reproducible and keyless: the same (namespace, text) always yields the same
vector, and no secret key, model, training, or network is involved.

This is honest deterministic context retrieval. It is NOT a neural embedding
and claims no semantic understanding; it is a stable hash-projection index used
only for bounded retrieval linkage in the offline vertical slice.

No network, filesystem, credential, model, random, or time access.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Any

from records import CloudError, canonical_json, require_id, sha256_hex

DIMENSIONS = 64
MAX_TOKENS = 256          # bound on tokens consumed per projection
MAX_TOKEN_BYTES = 32      # bound on bytes per token
MAX_INPUT_BYTES = 16384   # 16 KiB bound on input text
NORMALIZED_DECIMALS = 6   # fixed precision for byte-stable output

TOKEN_RE = re.compile(r"[a-z0-9]+")

DESCRIPTION = (
    "Deterministic 64-dimensional bounded token-feature hash projection with "
    "stable L2 normalization. Reproducible and keyless. Not a neural "
    "embedding: no model, training, or semantic understanding is involved."
)


def tokenize(text: Any) -> list[str]:
    """Bounded lowercase alphanumeric tokens; capped count and per-token bytes."""
    if not isinstance(text, str):
        raise CloudError("WRONG_TYPE")
    raw = text.encode("utf-8")
    if len(raw) > MAX_INPUT_BYTES:
        raise CloudError("RECORD_TOO_LARGE")
    tokens = []
    for match in TOKEN_RE.finditer(text.lower()):
        token = match.group(0).encode("utf-8")[:MAX_TOKEN_BYTES].decode("utf-8", "ignore")
        if token:
            tokens.append(token)
        if len(tokens) >= MAX_TOKENS:
            break
    return tokens


def _feature_value(namespace: str, token: str) -> tuple[int, float]:
    """Map one token to a (dimension, signed bounded weight) via keyless SHA-256."""
    digest = hashlib.sha256(namespace.encode("utf-8") + b"\x00" + token.encode("utf-8")).digest()
    dimension = int.from_bytes(digest[0:4], "big") % DIMENSIONS
    sign = 1.0 if digest[4] & 1 else -1.0
    weight = 1.0 + digest[5] / 255.0  # bounded magnitude in [1.0, 2.0]
    return dimension, sign * weight


def project(tokens: list[str], namespace: str) -> list[float]:
    """Accumulate bounded token-feature contributions into 64 dimensions."""
    require_id(namespace)
    vector = [0.0] * DIMENSIONS
    for token in tokens:
        dimension, value = _feature_value(namespace, token)
        vector[dimension] += value
    return vector


def normalize(vector: list[float]) -> list[float]:
    """Stable L2 normalization with a defined zero vector and fixed precision."""
    norm = math.sqrt(sum(component * component for component in vector))
    if norm == 0.0:
        return [0.0] * DIMENSIONS
    normalized = [round(component / norm, NORMALIZED_DECIMALS) for component in vector]
    # Round-half-even can yield -0.0; collapse to 0.0 for byte stability.
    return [0.0 if component == 0 else component for component in normalized]


def context_vector(text: Any, namespace: str) -> list[float]:
    """Full deterministic pipeline: tokenize -> project -> normalize.

    Returns a 64-component list of finite floats. The empty token set yields the
    defined all-zero vector. Identical (namespace, text) always yields the
    identical vector; a different namespace isolates the projection.
    """
    require_id(namespace)
    return normalize(project(tokenize(text), namespace))


def vector_digest(vector: list[float]) -> str:
    """SHA-256 binding of a context vector for authoritative storage linkage."""
    if not isinstance(vector, list) or len(vector) != DIMENSIONS:
        raise CloudError("MALFORMED_RECORD")
    for component in vector:
        if isinstance(component, bool) or not isinstance(component, (int, float)):
            raise CloudError("WRONG_TYPE")
        if component != component or component in (float("inf"), float("-inf")):
            raise CloudError("WRONG_TYPE")
    return sha256_hex(canonical_json(vector))


def describe() -> dict[str, Any]:
    """Honest self-description of the projection; never claims a neural model."""
    return {
        "kind": "deterministic_token_feature_hash_projection",
        "dimensions": DIMENSIONS,
        "normalization": "l2",
        "keyless": True,
        "neural_embedding": False,
        "description": DESCRIPTION,
    }
