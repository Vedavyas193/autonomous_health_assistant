from __future__ import annotations

import asyncio
import json
import time
import uuid
from contextlib import asynccontextmanager

import faiss
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

from agents.complexity_agent import ComplexityAssessmentAgent
from agents.collaborative_agents import CollaborativeDiagnosticPipeline
from agents.referral_agent import ReferralAgent
from agents.testing_agent import TestingAgent
from diagnostic_engine import DiagnosticEngine, IntakeAgent
from llm import ExplanationAgent
from schemas import (
    ComplexityOut, DiagnoseResponse, HealthResponse,
    ReferralOut, SymptomAnalysisOut, SymptomPayload,
    TestingResultOut, TestRecommendationOut, DifferentialTestOut,
    TreatmentPlanOut,
)
from security import DiagnosticContext, assess_risk, sign_context

# ── Globals ───────────────────────────────────────────────────────────────────
engine:           DiagnosticEngine | None = None
intake:           IntakeAgent | None = None
llm_agent:        ExplanationAgent | None = None
rag_encoder:      SentenceTransformer | None = None
rag_index:        faiss.IndexFlatIP | None = None
rag_corpus:       list[dict] | None = None
complexity_agent: ComplexityAssessmentAgent | None = None
collab_pipeline:  CollaborativeDiagnosticPipeline | None = None
referral_agent:   ReferralAgent | None = None
testing_agent:    TestingAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine, intake, llm_agent, rag_encoder, rag_index, rag_corpus
    global complexity_agent, collab_pipeline, referral_agent, testing_agent

    print("[STARTUP] Loading ensemble classifier...")
    engine = DiagnosticEngine(model_dir="models/")
    intake = IntakeAgent(symptom_cols=engine.symptom_cols)

    print("[STARTUP] Loading RAG index...")
    rag_encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    rag_index   = faiss.read_index("data/medical.faiss")
    with open("data/medical_corpus.json") as f:
        rag_corpus = json.load(f)

    print("[STARTUP] Loading agents...")
    complexity_agent = ComplexityAssessmentAgent(severity_csv="Symptom-severity.csv")
    collab_pipeline  = CollaborativeDiagnosticPipeline()
    referral_agent   = ReferralAgent()
    testing_agent    = TestingAgent()

    print("[STARTUP] Loading TinyLlama...")
    llm_agent = ExplanationAgent(model_dir="models/")

    print("[STARTUP] All components ready.")
    yield


app = FastAPI(
    title="Autonomous Health Assistant API",
    version="2.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def rag_retrieve(top_disease: str, symptoms: list[str], top_k: int = 3) -> list[dict]:
    query = (
        f"Disease: {top_disease}. "
        f"Symptoms: {', '.join(symptoms[:10])}. "
        "Precautions and recommended treatment."
    )
    embedding = rag_encoder.encode(
        [query], convert_to_numpy=True, normalize_embeddings=True
    ).astype(np.float32)
    scores, indices = rag_index.search(embedding, top_k)
    return [
        {**rag_corpus[int(idx)], "score": float(round(scores[0][rank], 4))}
        for rank, idx in enumerate(indices[0])
        if idx != -1
    ]


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        models_loaded=all([engine, llm_agent, rag_index]),
        pipeline_version="2.0.0",
    )


@app.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose(payload: SymptomPayload):
    t_start = time.perf_counter()
    loop    = asyncio.get_event_loop()

    # ── 1. Intake — handle both symptom list and free text ───────────────────
    all_inputs = list(payload.symptoms)
    if payload.free_text and payload.free_text.strip():
        all_inputs.append(payload.free_text.strip())

    if not all_inputs:
        raise HTTPException(
            status_code=422,
            detail="Please select at least one symptom or enter a description.",
        )

    symptoms, unknown = intake.normalize(all_inputs)
    if not symptoms:
        raise HTTPException(
            status_code=422,
            detail=(
                f"No recognizable symptoms found. "
                f"Try selecting from the list or use more specific terms. "
                f"Unmatched: {all_inputs[:3]}"
            ),
        )

    # ── 2. ML ensemble + RAG ──────────────────────────────────────────────────
    vector  = engine.build_symptom_vector(symptoms)
    top_k   = engine.predict_top_k(vector, top_k=5)
    detail  = engine.predict_single(vector)
    rag_ctx = await loop.run_in_executor(
        None, rag_retrieve, top_k[0]["disease"], symptoms
    )

    # ── 3. Confidence ─────────────────────────────────────────────────────────
    votes      = top_k[0].get("votes", 0)
    top_prob   = top_k[0].get("probability", 0)
    n_symptoms = len(symptoms)

    if top_prob >= 0.70 and votes == 3 and n_symptoms >= 5:
        confidence = "high"
    elif top_prob >= 0.45 and votes >= 2 and n_symptoms >= 3:
        confidence = "medium"
    else:
        confidence = "low"

    # ── 4. Complexity assessment ──────────────────────────────────────────────
    complexity = complexity_agent.assess(
        symptoms=symptoms,
        top_k_diseases=top_k,
        model_agreement=votes,
    )

    # ── 5. Testing agent ──────────────────────────────────────────────────────
    testing_result = None
    if confidence in ("low", "medium") or votes < 3:
        testing_result = testing_agent.recommend(
            top_k_diseases=top_k,
            confidence_level=confidence,
            symptoms=symptoms,
        )

    # ── 6. Collaborative agents ───────────────────────────────────────────────
    collab_result = None
    if (
        not complexity.has_emergency_symptoms
        and complexity.level.value != "HIGH"
        and confidence == "high"
    ):
        collab_result = await loop.run_in_executor(
            None,
            collab_pipeline.run,
            symptoms, top_k, rag_ctx, detail, complexity, None,
        )

    # ── 7. LLM synthesis ──────────────────────────────────────────────────────
    effective_rag = rag_ctx
    if complexity.level.value == "HIGH":
        effective_rag = [{
            "disease": top_k[0]["disease"],
            "text": (
                f"URGENT: {top_k[0]['disease']} with emergency symptoms. "
                "Immediate medical attention required."
            ),
            "source": "emergency_protocol",
            "score": 1.0,
        }] + rag_ctx

    synthesis = await loop.run_in_executor(
        None, llm_agent.synthesize, symptoms, top_k, effective_rag, detail
    )

    # ── 8. Referral ───────────────────────────────────────────────────────────
    primary_disease = synthesis.get("primary_disease", top_k[0]["disease"])
    is_emergency    = (
        complexity.has_emergency_symptoms
        or (
            primary_disease in {"Heart attack", "Paralysis (brain hemorrhage)", "AIDS"}
            and confidence == "high"
        )
    )
    referral = referral_agent.refer(primary_disease, is_emergency)

    # ── 9. Sign + audit ───────────────────────────────────────────────────────
    ctx = DiagnosticContext(
        patient_id=payload.patient_id or str(uuid.uuid4()),
        raw_symptoms=payload.symptoms,
        normalized_symptoms=symptoms,
        unknown_symptoms=unknown,
        symptom_vector=vector.tolist(),
        top_k_diseases=top_k,
        model_breakdown=detail,
        retrieved_context=effective_rag,
        diagnosis_summary=synthesis.get("diagnosis_summary", ""),
        confidence_level=confidence,
        primary_disease=primary_disease,
        model_agreement=votes,
        suggested_precautions=synthesis.get("suggested_precautions", []),
        red_flags=synthesis.get("red_flags", []),
    )
    ctx  = sign_context(ctx)
    risk = assess_risk(ctx)

    total_ms = round((time.perf_counter() - t_start) * 1000, 1)
    print(
        f"[DONE] {ctx.patient_id} | {primary_disease} | "
        f"conf={confidence} | {complexity.level.value} | "
        f"testing={'YES' if testing_result else 'NO'} | {total_ms}ms"
    )

    return DiagnoseResponse(
        patient_id=ctx.patient_id,
        primary_disease=ctx.primary_disease,
        confidence_level=confidence,
        model_agreement=votes,
        diagnosis_summary=ctx.diagnosis_summary,
        complexity=ComplexityOut(
            level=complexity.level.value,
            score=complexity.score,
            systems_involved=complexity.systems_involved,
            reasoning=complexity.reasoning,
        ),
        symptom_analysis=SymptomAnalysisOut(
            dominant_system=collab_result.symptom_analysis.dominant_system,
            total_severity_score=collab_result.symptom_analysis.total_severity_score,
            pattern_notes=collab_result.symptom_analysis.pattern_notes,
            systems_involved=complexity.systems_involved,
        ) if collab_result else None,
        treatment_plan=TreatmentPlanOut(
            immediate_actions=collab_result.treatment_plan.immediate_actions,
            precautions=collab_result.treatment_plan.precautions,
            lifestyle_advice=collab_result.treatment_plan.lifestyle_advice,
            follow_up=collab_result.treatment_plan.follow_up,
            refer_to_specialist=collab_result.treatment_plan.refer_to_specialist,
            specialist_type=collab_result.treatment_plan.specialist_type,
        ) if collab_result else None,
        testing=TestingResultOut(
            primary_disease=testing_result.primary_disease,
            requires_testing=testing_result.requires_testing,
            tests=[
                TestRecommendationOut(
                    test_name=t.test_name,
                    reason=t.reason,
                    urgency=t.urgency,
                    test_type=t.test_type,
                )
                for t in testing_result.tests
            ],
            differential_tests=[
                DifferentialTestOut(
                    disease=d["disease"],
                    probability=d["probability"],
                    tests=d["tests"],
                )
                for d in testing_result.differential_tests
            ],
            testing_rationale=testing_result.testing_rationale,
        ) if testing_result else None,
        suggested_precautions=ctx.suggested_precautions,
        red_flags=ctx.red_flags,
        top_k_diseases=top_k,
        model_breakdown=detail,
        referral=ReferralOut(
            specialist=referral.specialist,
            urgency=referral.urgency,
            referral_note=referral.referral_note,
            contact_advice=referral.contact_advice,
        ),
        risk_level=risk["risk_level"],
        is_emergency=risk["is_emergency"],
        hmac_valid=risk["hmac_valid"],
        unknown_symptoms=unknown,
        pipeline_version=ctx.pipeline_version,
        total_ms=total_ms,
    )