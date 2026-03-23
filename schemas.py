from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


class SymptomPayload(BaseModel):
    patient_id: str = Field(..., description="Unique patient identifier")
    symptoms: list[str] = Field(..., min_length=1, max_length=132)


class DiseaseScore(BaseModel):
    disease: str
    probability: float
    rank: int
    votes: int
    ensemble_winner: Optional[str] = None
    dx_notes: Optional[str] = None
    rag_confirmed: Optional[bool] = None


class ModelBreakdown(BaseModel):
    svm_model_prediction: str
    naive_bayes_prediction: str
    rf_model_prediction: str
    final_prediction: str


class SymptomAnalysisOut(BaseModel):
    dominant_system: str
    total_severity_score: int
    pattern_notes: str
    systems_involved: Optional[list[str]] = None


class TreatmentPlanOut(BaseModel):
    immediate_actions: list[str]
    precautions: list[str]
    lifestyle_advice: list[str]
    follow_up: str
    refer_to_specialist: bool
    specialist_type: str


class ReferralOut(BaseModel):
    specialist: str
    urgency: str
    referral_note: str
    contact_advice: str


class ComplexityOut(BaseModel):
    level: str
    score: int
    systems_involved: list[str]
    reasoning: str


class TestRecommendationOut(BaseModel):
    test_name: str
    reason: str
    urgency: str
    test_type: str


class DifferentialTestOut(BaseModel):
    disease: str
    probability: float
    tests: list[dict]


class TestingResultOut(BaseModel):
    primary_disease: str
    requires_testing: bool
    tests: list[TestRecommendationOut]
    differential_tests: list[DifferentialTestOut]
    testing_rationale: str


class DiagnoseResponse(BaseModel):
    patient_id: str
    primary_disease: str
    confidence_level: str
    model_agreement: int
    diagnosis_summary: str
    complexity: Optional[ComplexityOut] = None
    symptom_analysis: Optional[SymptomAnalysisOut] = None
    treatment_plan: Optional[TreatmentPlanOut] = None
    testing: Optional[TestingResultOut] = None
    suggested_precautions: list[str]
    red_flags: list[str]
    top_k_diseases: list[DiseaseScore]
    model_breakdown: ModelBreakdown
    referral: Optional[ReferralOut] = None
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