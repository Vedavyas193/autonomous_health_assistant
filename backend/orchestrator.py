from fastapi import FastAPI
from schemas import PatientRequest, TriageResponse
import xgboost as xgb
import joblib
import json
import numpy as np
from llm import ExplanationAgent

app = FastAPI(title="Offline Rural Health Triage")

# --- 1. LOAD ML ASSETS IN MEMORY (Run once on startup) ---
print("Initializing Orchestrator...")
xgb_model = xgb.XGBClassifier()
xgb_model.load_model("disease_classifier.json")
label_encoder = joblib.load("label_encoder.pkl")

with open("symptom_columns.json", "r") as f:
    symptom_columns = json.load(f)

# --- 2. LOAD LLM ---
llm_agent = ExplanationAgent()

# --- 3. HELPER AGENTS (Functions) ---
def risk_assessment_agent(disease, symptoms, temp):
    critical_symptoms = ["chest_pain", "breathlessness", "loss_of_balance"]
    if temp and temp > 39.5:
        return "CRITICAL"
    if any(sym in symptoms for sym in critical_symptoms):
        return "CRITICAL"
    return "ROUTINE"

def referral_agent(disease):
    specialists = {
        "Fungal infection": "Dermatologist",
        "Heart attack": "Cardiologist",
        "Diabetes ": "Endocrinologist",
        "Malaria": "General Physician / Infectious Disease"
    }
    return specialists.get(disease, "General Physician")

# --- 4. MAIN PIPELINE ---
@app.post("/triage", response_model=TriageResponse)
def run_triage(patient: PatientRequest):
    # Step A: Intake Agent (Normalize vector)
    input_vector = np.zeros(len(symptom_columns))
    for symptom in patient.symptoms:
        if symptom in symptom_columns:
            idx = symptom_columns.index(symptom)
            input_vector[idx] = 1

    # Step B: ML Classifier Agent
    probabilities = xgb_model.predict_proba([input_vector])[0]
    top_class_index = np.argmax(probabilities)
    predicted_disease = label_encoder.inverse_transform([top_class_index])[0]
    confidence = round(probabilities[top_class_index] * 100, 2)

    # Step C: Decision Layer
    risk = risk_assessment_agent(predicted_disease, patient.symptoms, patient.temperature_c)
    specialist = referral_agent(predicted_disease)

    # Step D: LLM Explanation Agent
    explanation = llm_agent.generate_explanation(predicted_disease, confidence, patient.symptoms)

    return TriageResponse(
        predicted_disease=predicted_disease,
        probability=confidence,
        risk_level=risk,
        recommended_specialist=specialist,
        llm_explanation=explanation
    )