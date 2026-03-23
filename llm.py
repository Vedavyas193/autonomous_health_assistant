from __future__ import annotations
import json
import time
from pathlib import Path

from llama_cpp import Llama

SYSTEM_PROMPT = """You are a clinical triage assistant in an offline rural medical system.

Synthesize a diagnostic report from the symptoms and classifier results provided.

You MUST respond with ONLY a valid JSON object in exactly this format, no other text:
{
  "diagnosis_summary": "2-3 sentence clinical summary here",
  "confidence_level": "high",
  "primary_disease": "Disease Name Here",
  "model_agreement": 3,
  "suggested_precautions": ["precaution 1", "precaution 2", "precaution 3"],
  "red_flags": []
}

Rules:
- confidence_level must be exactly "high", "medium", or "low"
- model_agreement must be a number 1, 2, or 3
- suggested_precautions must use only information from the retrieved context
- red_flags lists emergency symptoms if present, otherwise empty list []
- Output ONLY the JSON object. No markdown. No explanation. No preamble."""


def build_user_prompt(
    symptoms: list[str],
    top_k_diseases: list[dict],
    rag_context: list[dict],
    model_detail: dict,
) -> str:
    top_disease = top_k_diseases[0]["disease"] if top_k_diseases else "Unknown"
    agreement = top_k_diseases[0].get("votes", 3) if top_k_diseases else 3

    disease_block = "\n".join(
        f"  {d['rank']}. {d['disease']} — {d['probability']:.1%} ({d.get('votes','?')}/3 models)"
        for d in top_k_diseases[:5]
    )
    context_block = "\n\n".join(
        f"[Source: {r.get('source', 'KB')}]\n{r['text']}"
        for r in rag_context[:3]
    )
    model_block = (
        f"SVM={model_detail.get('svm_model_prediction','?')} | "
        f"NaiveBayes={model_detail.get('naive_bayes_prediction','?')} | "
        f"RandomForest={model_detail.get('rf_model_prediction','?')} → "
        f"Ensemble={model_detail.get('final_prediction','?')}"
    )

    return f"""SYMPTOMS ({len(symptoms)} active): {', '.join(symptoms[:15])}

ENSEMBLE: {model_block}

TOP DISEASES:
{disease_block}

RETRIEVED CONTEXT:
{context_block}

Generate the JSON diagnostic report for: {top_disease} (agreement: {agreement}/3)"""


def _extract_json(text: str) -> dict:
    """Try multiple strategies to extract valid JSON from LLM output."""
    text = text.strip()

    # Strategy 1: direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Strategy 2: find first { ... } block
    try:
        start = text.index('{')
        end   = text.rindex('}') + 1
        return json.loads(text[start:end])
    except Exception:
        pass

    # Strategy 3: strip markdown fences
    try:
        cleaned = text.replace('```json', '').replace('```', '').strip()
        start = cleaned.index('{')
        end   = cleaned.rindex('}') + 1
        return json.loads(cleaned[start:end])
    except Exception:
        pass

    return {}


def _fallback_response(top_k_diseases: list[dict], rag_context: list[dict]) -> dict:
    """
    Returns a safe structured response when LLM output is unparseable.
    Uses the ML ensemble result directly so the pipeline never breaks.
    """
    top = top_k_diseases[0] if top_k_diseases else {}
    disease = top.get("disease", "Unknown")
    votes   = top.get("votes", 0)

    # Pull precautions directly from RAG context
    precautions = []
    for doc in rag_context:
        text = doc.get("text", "")
        if disease.lower() in text.lower():
            sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
            precautions.extend(sentences[:2])
    if not precautions:
        precautions = [
            "Consult a healthcare provider promptly",
            "Monitor symptoms and seek medical attention if worsening",
            "Maintain adequate hydration and rest",
        ]

    confidence = "high" if votes == 3 else "medium" if votes == 2 else "low"

    return {
        "diagnosis_summary": (
            f"Based on the symptom profile, the most likely diagnosis is {disease}. "
            f"This assessment is supported by {votes}/3 ensemble models. "
            "Please consult a qualified healthcare provider for confirmation."
        ),
        "confidence_level": confidence,
        "primary_disease": disease,
        "model_agreement": votes,
        "suggested_precautions": precautions[:4],
        "red_flags": [],
        "llm_inference_ms": 0,
        "_fallback": True,
    }


class ExplanationAgent:
    def __init__(self, model_dir: str = "models/", n_gpu_layers: int = 0, n_ctx: int = 2048):
        gguf_files = list(Path(model_dir).glob("*.gguf"))
        if not gguf_files:
            raise FileNotFoundError(f"No .gguf file found in {model_dir}")
        model_path = str(gguf_files[0])
        print(f"[LLM] Loading {model_path}")

        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,  # 0 = CPU only (safe default)
            n_ctx=n_ctx,
            n_threads=4,
            verbose=False,
        )
        print("[LLM] TinyLlama ready.")

    def synthesize(
        self,
        symptoms: list[str],
        top_k_diseases: list[dict],
        rag_context: list[dict],
        model_detail: dict,
    ) -> dict:
        user_prompt = build_user_prompt(symptoms, top_k_diseases, rag_context, model_detail)

        t0 = time.perf_counter()
        try:
            response = self.llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
                max_tokens=600,
                temperature=0.1,
                top_p=0.9,
                repeat_penalty=1.1,
                # No grammar constraint — simpler and more reliable
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000
            raw = response["choices"][0]["message"]["content"]
            print(f"[LLM] Raw output ({len(raw)} chars): {raw[:200]}")

            result = _extract_json(raw)

            if not result or "primary_disease" not in result:
                print("[LLM] JSON extraction failed — using fallback")
                result = _fallback_response(top_k_diseases, rag_context)

        except Exception as e:
            print(f"[LLM] Error during inference: {e} — using fallback")
            elapsed_ms = (time.perf_counter() - t0) * 1000
            result = _fallback_response(top_k_diseases, rag_context)

        result["llm_inference_ms"] = round(elapsed_ms, 1)
        return result