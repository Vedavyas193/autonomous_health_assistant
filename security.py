import hmac
import hashlib
import json
import os
import sqlite3
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

HMAC_SECRET_KEY: bytes = os.environ.get(
    "TRIAGE_HMAC_SECRET", "change-me-in-production-32chars++"
).encode("utf-8")

DB_PATH = "triage_audit.db"

EMERGENCY_DISEASES = {
    "Heart attack",
    "Paralysis (brain hemorrhage)",
    "Hepatitis E",
    "Hepatitis D",
    "AIDS",
}
EMERGENCY_SYMPTOMS = {
    "chest_pain",
    "breathlessness",
    "loss_of_balance",
    "unconsciousness",
    "altered_sensorium",
}


@dataclass
class DiagnosticContext:
    patient_id: str
    raw_symptoms: list
    normalized_symptoms: list = field(default_factory=list)
    unknown_symptoms: list = field(default_factory=list)
    symptom_vector: list = field(default_factory=list)
    intake_ms: float = 0.0
    top_k_diseases: list = field(default_factory=list)
    model_breakdown: dict = field(default_factory=dict)
    classifier_ms: float = 0.0
    retrieved_context: list = field(default_factory=list)
    rag_ms: float = 0.0
    diagnosis_summary: str = ""
    confidence_level: str = ""
    primary_disease: str = ""
    model_agreement: int = 0
    suggested_precautions: list = field(default_factory=list)
    red_flags: list = field(default_factory=list)
    llm_ms: float = 0.0
    hmac_signature: Optional[str] = None
    pipeline_version: str = "2.0.0"
    timestamp_utc: float = field(default_factory=time.time)


def _canonical_payload(ctx: DiagnosticContext) -> bytes:
    payload = {
        "patient_id": ctx.patient_id,
        "normalized_symptoms": sorted(ctx.normalized_symptoms),
        "top_k_diseases": ctx.top_k_diseases,
        "primary_disease": ctx.primary_disease,
        "diagnosis_summary": ctx.diagnosis_summary,
        "confidence_level": ctx.confidence_level,
        "model_agreement": ctx.model_agreement,
        "suggested_precautions": ctx.suggested_precautions,
        "red_flags": ctx.red_flags,
        "pipeline_version": ctx.pipeline_version,
        "timestamp_utc": ctx.timestamp_utc,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def sign_context(ctx: DiagnosticContext) -> DiagnosticContext:
    payload = _canonical_payload(ctx)
    signature = hmac.new(HMAC_SECRET_KEY, payload, hashlib.sha256).hexdigest()
    ctx.hmac_signature = signature
    return ctx


def verify_context(ctx: DiagnosticContext) -> bool:
    if not ctx.hmac_signature:
        return False
    payload = _canonical_payload(ctx)
    expected = hmac.new(HMAC_SECRET_KEY, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, ctx.hmac_signature)


def assess_risk(ctx: DiagnosticContext) -> dict:
    if not verify_context(ctx):
        raise ValueError(
            f"HMAC verification FAILED for patient {ctx.patient_id}. Record rejected."
        )

    top_disease = ctx.primary_disease
    top_prob = ctx.top_k_diseases[0]["probability"] if ctx.top_k_diseases else 0.0
    active_syms = set(ctx.normalized_symptoms)

    is_emergency = (
        top_disease in EMERGENCY_DISEASES
        or bool(active_syms & EMERGENCY_SYMPTOMS)
        or len(ctx.red_flags) > 0
    )

    risk_level = (
        "EMERGENCY" if is_emergency else
        "HIGH"      if top_prob >= 0.75 else
        "MEDIUM"    if top_prob >= 0.50 else
        "LOW"
    )

    assessment = {
        "risk_level": risk_level,
        "is_emergency": is_emergency,
        "top_disease": top_disease,
        "top_prob": top_prob,
        "agreement": ctx.model_agreement,
        "red_flags": ctx.red_flags,
        "hmac_valid": True,
    }

    _write_to_sqlite(ctx, assessment)
    return assessment


def _init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS diagnostic_log (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id            TEXT    NOT NULL,
            timestamp_utc         REAL    NOT NULL,
            primary_disease       TEXT,
            confidence_level      TEXT,
            model_agreement       INTEGER,
            risk_level            TEXT,
            is_emergency          INTEGER,
            red_flags             TEXT,
            suggested_precautions TEXT,
            hmac_signature        TEXT    NOT NULL,
            pipeline_version      TEXT,
            full_context_json     TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _write_to_sqlite(ctx: DiagnosticContext, assessment: dict) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO diagnostic_log (
            patient_id, timestamp_utc, primary_disease, confidence_level,
            model_agreement, risk_level, is_emergency, red_flags,
            suggested_precautions, hmac_signature, pipeline_version,
            full_context_json
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            ctx.patient_id,
            ctx.timestamp_utc,
            ctx.primary_disease,
            ctx.confidence_level,
            ctx.model_agreement,
            assessment["risk_level"],
            int(assessment["is_emergency"]),
            json.dumps(ctx.red_flags),
            json.dumps(ctx.suggested_precautions),
            ctx.hmac_signature,
            ctx.pipeline_version,
            json.dumps(asdict(ctx)),
        ),
    )
    conn.commit()
    conn.close()


_init_db()