"""Canonical diagnostic context serialization and HMAC-SHA256 integrity for the triage chain."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Mapping

JsonDict = dict[str, Any]


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(dict(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")


def context_sha256(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def sign_diagnostic_context(payload: Mapping[str, Any], secret_key: bytes) -> str:
    msg = canonical_json_bytes(payload)
    return hmac.new(secret_key, msg, hashlib.sha256).hexdigest()


def verify_diagnostic_context(
    payload: Mapping[str, Any],
    secret_key: bytes,
    signature_hex: str,
) -> bool:
    expected = sign_diagnostic_context(payload, secret_key)
    return hmac.compare_digest(expected, signature_hex)


def build_audit_payload(
    *,
    intake: JsonDict,
    ml_top_k: list[JsonDict],
    rag: JsonDict,
    explanation: JsonDict,
    risk_level: str,
    recommended_specialist: str,
) -> JsonDict:
    """Single object signed before SQLite write (Risk + Referral included after LLM)."""
    return {
        "intake": intake,
        "ml": {"top_k": ml_top_k},
        "rag": rag,
        "explanation": explanation,
        "risk_level": risk_level,
        "recommended_specialist": recommended_specialist,
    }
