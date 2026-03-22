"""Normalizes raw symptom input for downstream ML and RAG."""

from __future__ import annotations

from typing import List, Union


def normalize_symptoms(symptoms: Union[str, List[str]]) -> List[str]:
    if isinstance(symptoms, str):
        parts = [s.strip() for s in symptoms.split(",")]
    else:
        parts = [str(s).strip() for s in symptoms]
    out: List[str] = []
    for s in parts:
        if not s:
            continue
        clean = s.replace(" ", "_").lower().strip()
        if clean:
            out.append(clean)
    return out


class IntakeAgent:
    """Incremental context: intake-only normalization (orchestrator adds ML/RAG later)."""

    def process(self, symptoms: Union[str, List[str]]) -> dict:
        normalized = normalize_symptoms(symptoms)
        return {
            "normalized_symptoms": normalized,
            "symptom_count": len(normalized),
        }
