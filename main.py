from __future__ import annotations

import asyncio
import time
import uuid
from contextlib import asynccontextmanager

import numpy as np
import faiss
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

from diagnostic_engine import DiagnosticEngine, IntakeAgent
from llm import ExplanationAgent
from schemas import DiagnoseResponse, HealthResponse, SymptomPayload
from security import DiagnosticContext, assess_risk, sign_context

# ── Globals (loaded once at startup) ─────────────────────────────────────────
engine: DiagnosticEngine | None = None
intake: IntakeAgent | None = None
llm_agent: ExplanationAgent | None = None
rag_encoder: SentenceTransformer | None = None
rag_index: faiss.IndexFlatIP | None = None
rag_corpus: list[dict] | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine, intake, llm_agent, rag_encoder, rag_index, rag_corpus

    print("[STARTUP] Loading ensemble classifier...")
    engine = DiagnosticEngine(model_dir="models/")
    intake = IntakeAgent(symptom_cols=engine.symptom_cols)

    print("[STARTUP] Loading RAG index...")
    rag_encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    rag_index = faiss.read_index("data/medical.faiss")
    with open("data/medical_corpus.json") as f:
        rag_corpus = json.load(f)

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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── RAG retrieval helper ──────────────────────────────────────────────────────

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


# ── Endpoints ─────────────────────────────────────────────────────────────────

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

    # 1. Intake normalization
    t0 = time.perf_counter()
    symptoms, unknown = intake.normalize(payload.symptoms)
    if not symptoms:
        raise HTTPException(
            status_code=422,
            detail=f"No recognizable symptoms found. Unknown: {unknown}",
        )
    intake_ms = (time.perf_counter() - t0) * 1000

    # 2. ML ensemble + RAG (run concurrently)
    t0 = time.perf_counter()
    vector = engine.build_symptom_vector(symptoms)
    top_k = engine.predict_top_k(vector, top_k=5)
    detail = engine.predict_single(vector)
    classifier_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    rag_ctx = await asyncio.get_event_loop().run_in_executor(
        None, rag_retrieve, top_k[0]["disease"], symptoms
    )
    rag_ms = (time.perf_counter() - t0) * 1000

    # 3. LLM synthesis
    t0 = time.perf_counter()
    synthesis = await asyncio.get_event_loop().run_in_executor(
        None, llm_agent.synthesize, symptoms, top_k, rag_ctx, detail
    )
    llm_ms = (time.perf_counter() - t0) * 1000

    # 4. Build context object, sign, assess risk, log
    ctx = DiagnosticContext(
        patient_id=payload.patient_id or str(uuid.uuid4()),
        raw_symptoms=payload.symptoms,
        normalized_symptoms=symptoms,
        unknown_symptoms=unknown,
        symptom_vector=vector.tolist(),
        intake_ms=round(intake_ms, 1),
        top_k_diseases=top_k,
        model_breakdown=detail,
        classifier_ms=round(classifier_ms, 1),
        retrieved_context=rag_ctx,
        rag_ms=round(rag_ms, 1),
        diagnosis_summary=synthesis.get("diagnosis_summary", ""),
        confidence_level=synthesis.get("confidence_level", "low"),
        primary_disease=synthesis.get("primary_disease", top_k[0]["disease"]),
        model_agreement=synthesis.get("model_agreement", top_k[0].get("votes", 0)),
        suggested_precautions=synthesis.get("suggested_precautions", []),
        red_flags=synthesis.get("red_flags", []),
        llm_ms=round(llm_ms, 1),
    )

    ctx = sign_context(ctx)
    risk = assess_risk(ctx)  # verifies HMAC then writes to SQLite

    total_ms = round((time.perf_counter() - t_start) * 1000, 1)
    print(f"[PIPELINE] {ctx.patient_id} complete in {total_ms}ms | "
          f"Risk: {risk['risk_level']} | Disease: {ctx.primary_disease}")

    return DiagnoseResponse(
        patient_id=ctx.patient_id,
        primary_disease=ctx.primary_disease,
        confidence_level=ctx.confidence_level,
        model_agreement=ctx.model_agreement,
        diagnosis_summary=ctx.diagnosis_summary,
        suggested_precautions=ctx.suggested_precautions,
        red_flags=ctx.red_flags,
        top_k_diseases=top_k,
        model_breakdown=detail,
        risk_level=risk["risk_level"],
        is_emergency=risk["is_emergency"],
        hmac_valid=risk["hmac_valid"],
        unknown_symptoms=unknown,
        pipeline_version=ctx.pipeline_version,
        total_ms=total_ms,
    )