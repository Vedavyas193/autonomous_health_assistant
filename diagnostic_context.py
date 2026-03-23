from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import time


@dataclass
class DiagnosticContext:
    """
    Canonical context object passed incrementally through the pipeline.
    Each agent receives this, enriches it, and returns the updated version.
    No agent mutates a prior agent's fields.
    """

    # ── Intake ────────────────────────────────────────────────────────────────
    patient_id: str
    raw_symptoms: list[str]
    normalized_symptoms: list[str] = field(default_factory=list)
    unknown_symptoms: list[str] = field(default_factory=list)
    symptom_vector: list[float] = field(default_factory=list)
    intake_ms: float = 0.0

    # ── ML Classifier (ensemble) ──────────────────────────────────────────────
    top_k_diseases: list[dict] = field(default_factory=list)
    model_breakdown: dict = field(default_factory=dict)
    classifier_ms: float = 0.0

    # ── RAG Retrieval ─────────────────────────────────────────────────────────
    retrieved_context: list[dict] = field(default_factory=list)
    rag_ms: float = 0.0

    # ── LLM Synthesis ─────────────────────────────────────────────────────────
    diagnosis_summary: str = ""
    confidence_level: str = ""
    primary_disease: str = ""
    model_agreement: int = 0
    suggested_precautions: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    llm_ms: float = 0.0

    # ── Security & Audit ──────────────────────────────────────────────────────
    hmac_signature: Optional[str] = None
    pipeline_version: str = "2.0.0"
    timestamp_utc: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)