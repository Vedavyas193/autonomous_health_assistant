"""TinyLlama (GGUF) explanation agent: structured JSON grounded in ML + RAG."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

from llama_cpp import Llama

SYSTEM_PROMPT = """You are a clinical decision-support assistant for offline rural triage. You do NOT replace a doctor.

You will receive:
1) Normalized symptom list
2) Top-K disease predictions with probabilities from a statistical model (XGBoost)
3) RETRIEVED_CONTEXT: excerpts from an approved local knowledge base only

Rules:
- Base disease names and probabilities on item (2). Do not invent new diseases or change ranks.
- For precautions and self-care advice, use ONLY information present in RETRIEVED_CONTEXT. If a detail is not in RETRIEVED_CONTEXT, omit it or say "not specified in retrieved references."
- Output a single JSON object with exactly these keys:
  - "diagnosis_summary": string, 2-4 sentences, plain language
  - "confidence_level": one of "low" | "medium" | "high", aligned with the top probability (use: high if top >= 50, medium if >= 25, else low)
  - "suggested_precautions": array of 2-5 short strings, each traceable to RETRIEVED_CONTEXT

Do not include markdown fences or text outside the JSON object."""


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


class ExplanationAgent:
    def __init__(self, model_path: str, n_ctx: int = 2048, n_gpu_layers: int = 0):
        print(f"Loading quantized LLM from: {model_path}...")
        if not os.path.exists(model_path):
            print(f"Model file not found at {model_path}")
            self.llm = None
        else:
            try:
                self.llm = Llama(
                    model_path=model_path,
                    n_ctx=n_ctx,
                    verbose=False,
                    n_gpu_layers=n_gpu_layers,
                )
                print("LLM engine initialized.")
            except Exception as e:
                print(f"Failed to load LLM: {e}")
                self.llm = None

    def generate_explanation(
        self,
        disease: str,
        probability: float,
        symptoms: List[str],
        top_k: List[tuple],
        rag_chunks: List[str],
    ) -> Dict[str, Any]:
        """Returns dict with diagnosis_summary, confidence_level, suggested_precautions, and optional raw_text."""
        if self.llm is None:
            return {
                "diagnosis_summary": f"Prediction: {disease} ({probability}%). LLM unavailable.",
                "confidence_level": "low",
                "suggested_precautions": [],
                "raw_text": "",
            }

        sym_text = ", ".join(symptoms)
        top_k_lines = "\n".join(f"  - {d} ({p}%)" for d, p in top_k)
        retrieved = "\n".join(f"  [{i+1}] {c}" for i, c in enumerate(rag_chunks)) or "(none)"

        user_block = f"""Normalized symptoms: {sym_text}

Top-K disease predictions (XGBoost):
{top_k_lines}

Primary label for narrative: {disease} ({probability}%)

RETRIEVED_CONTEXT:
{retrieved}
"""

        prompt = f"""<|system|>
{SYSTEM_PROMPT}
<|user|>
{user_block}
<|assistant|>"""

        try:
            response = self.llm(
                prompt,
                max_tokens=384,
                temperature=0.2,
                stop=["<|user|>", "</s>"],
            )
            raw = response["choices"][0]["text"].strip()
        except Exception as e:
            return {
                "diagnosis_summary": f"The ML model predicts {disease}. (Explanation failed: {e})",
                "confidence_level": "low",
                "suggested_precautions": [],
                "raw_text": "",
            }

        parsed = _extract_json_object(raw)
        if parsed:
            parsed.setdefault("diagnosis_summary", "")
            parsed.setdefault("confidence_level", "low")
            parsed.setdefault("suggested_precautions", [])
            parsed["raw_text"] = raw
            return parsed

        return {
            "diagnosis_summary": raw[:500] if raw else "(empty response)",
            "confidence_level": "low",
            "suggested_precautions": [],
            "raw_text": raw,
            "parse_error": True,
        }
