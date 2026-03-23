from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


class SymptomPayload(BaseModel):
    patient_id: str = Field(..., description="Unique patient identifier")
    symptoms: list[str] = Field(
        ...,
        min_items=1,
        max_items=132,
        description="List of symptom strings (natural language or canonical names)",
    )


class DiseaseScore(BaseModel):
    disease: str
    probability: float
    rank: int
    votes: int
    ensemble_winner: Optional[str] = None


class ModelBreakdown(BaseModel):
    svm_model_prediction: str
    naive_bayes_prediction: str
    rf_model_prediction: str
    final_prediction: str


class DiagnoseResponse(BaseModel):
    patient_id: str
    primary_disease: str
    confidence_level: str
    model_agreement: int
    diagnosis_summary: str
    suggested_precautions: list[str]
    red_flags: list[str]
    top_k_diseases: list[DiseaseScore]
    model_breakdown: ModelBreakdown
    risk_level: str
    is_emergency: bool
    hmac_valid: bool
    unknown_symptoms: list[str]
    pipeline_version: str
    total_ms: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    pipeline_version: str