import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "backend", "app"))
sys.path.append(os.path.join(BASE_DIR, "backend", "app", "agents"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from diagnostic_context import build_audit_payload, sign_diagnostic_context
from ml_classifier import TriageMLClassifier
from schemas import PatientRequest, TriageResponse, TopKDisease

try:
    from llm import ExplanationAgent
    from risk_agent import RiskAssessmentAgent
    from rag_agent import RAGRetrievalAgent
    from referral_agent import ReferralAgent
    from record_agent import RecordStorageAgent
    from intake_agent import IntakeAgent
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

app = FastAPI(title="Autonomous Rural Health Triage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HMAC_SECRET = os.environ.get("TRIAGE_HMAC_SECRET", "dev-hmac-secret-change-me").encode("utf-8")

print("Booting hybrid AI architecture...")

try:
    ml_engine = TriageMLClassifier(BASE_DIR)
except Exception as e:
    print(f"Warning: ML engine failed to load: {e}")
    ml_engine = None

rag_agent = RAGRetrievalAgent(base_dir=BASE_DIR)
risk_agent = RiskAssessmentAgent(os.path.join(BASE_DIR, "Symptom-severity.csv"))
referral_agent = ReferralAgent()
intake_agent = IntakeAgent()
storage_agent = RecordStorageAgent(
    db_name=os.path.join(BASE_DIR, "patient_records.db"),
    hmac_secret=HMAC_SECRET,
)

model_file_path = os.path.join(BASE_DIR, "models", "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
llm_agent = ExplanationAgent(model_file_path)

print("System ready.")


def _explanation_for_audit(expl: dict) -> dict:
    return {
        "diagnosis_summary": expl.get("diagnosis_summary", ""),
        "confidence_level": expl.get("confidence_level", "low"),
        "suggested_precautions": expl.get("suggested_precautions", []),
    }


def _format_llm_text(expl: dict) -> str:
    parts = [expl.get("diagnosis_summary", "")]
    precs = expl.get("suggested_precautions") or []
    if precs:
        parts.append("Precautions: " + "; ".join(str(p) for p in precs))
    return "\n\n".join(p for p in parts if p).strip()


@app.post("/api/v1/triage", response_model=TriageResponse)
def run_triage_pipeline(patient: PatientRequest):
    if ml_engine is None:
        raise HTTPException(status_code=503, detail="ML classifier not loaded")

    try:
        # Intake — normalize and clean symptom tokens
        intake_ctx = intake_agent.process(patient.symptoms)
        symptoms_list = intake_ctx["normalized_symptoms"]

        # ML — Top-K
        predicted_disease, confidence, top_k = ml_engine.predict_top_k(symptoms_list, k=5)
        top_k_models = [
            TopKDisease(disease=d, probability=p) for d, p in top_k
        ]

        # RAG — grounded snippets for primary prediction
        rag_out = rag_agent.retrieve_for_disease(predicted_disease, top_k=3)
        chunks = rag_out.get("chunks", [])

        # Explanation LLM (structured JSON)
        expl = llm_agent.generate_explanation(
            disease=predicted_disease,
            probability=confidence,
            symptoms=symptoms_list,
            top_k=top_k,
            rag_chunks=chunks,
        )
        expl_audit = _explanation_for_audit(expl)

        # Risk & referral (after ML + context; emergency overrides)
        risk_level = risk_agent.calculate_risk(symptoms_list)
        if patient.temperature_c is not None and patient.temperature_c > 39.5:
            risk_level = "CRITICAL EMERGENCY"
        specialist = referral_agent.get_specialist(predicted_disease, risk_level)

        intake_block = {
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "normalized_symptoms": symptoms_list,
            "temperature_c": patient.temperature_c,
            "oxygen": patient.oxygen,
            "heart_rate": patient.heart_rate,
            "glucose": patient.glucose,
        }

        audit_payload = build_audit_payload(
            intake=intake_block,
            ml_top_k=[{"disease": d, "probability": p} for d, p in top_k],
            rag=rag_out,
            explanation=expl_audit,
            risk_level=risk_level,
            recommended_specialist=specialist,
        )
        signature = sign_diagnostic_context(audit_payload, HMAC_SECRET)

        llm_text = _format_llm_text(expl)

        saved = storage_agent.save_record(
            symptoms=symptoms_list,
            disease=predicted_disease,
            confidence=confidence,
            risk_level=risk_level,
            specialist=specialist,
            explanation_text=llm_text,
            explanation_struct=expl,
            audit_payload=audit_payload,
            signature_hex=signature,
        )

        return TriageResponse(
            predicted_disease=predicted_disease,
            probability=confidence,
            risk_level=risk_level,
            recommended_specialist=specialist,
            llm_explanation=llm_text,
            diagnosis_summary=expl_audit.get("diagnosis_summary", ""),
            confidence_level=expl_audit.get("confidence_level", "low"),
            suggested_precautions=list(expl_audit.get("suggested_precautions", [])),
            top_k_predictions=top_k_models,
            integrity_verified=bool(saved),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
