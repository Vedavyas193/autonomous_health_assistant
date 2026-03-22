from pydantic import BaseModel, Field
from typing import List, Optional, Union


class TopKDisease(BaseModel):
    disease: str
    probability: float


class PatientRequest(BaseModel):
    name: str
    age: int
    gender: str
    symptoms: Union[str, List[str]]
    heart_rate: Optional[float] = None
    oxygen: Optional[float] = None
    glucose: Optional[float] = None
    temperature_c: Optional[float] = None


class TriageResponse(BaseModel):
    predicted_disease: str
    probability: float
    risk_level: str
    recommended_specialist: str
    llm_explanation: str
    diagnosis_summary: str = ""
    confidence_level: str = "low"
    suggested_precautions: List[str] = Field(default_factory=list)
    top_k_predictions: List[TopKDisease] = Field(default_factory=list)
    integrity_verified: bool = False
