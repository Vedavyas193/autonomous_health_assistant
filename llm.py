"""
TinyLlama 1.1B-Chat GGUF — Explanation Agent.
Model file lives in models/ folder (your existing setup).
"""

from __future__ import annotations
import json
import time
from pathlib import Path

from llama_cpp import Llama, LlamaGrammar

DIAGNOSTIC_GRAMMAR = r"""
root   ::= object
object ::= "{" ws
  "\"diagnosis_summary\""     ":" ws string "," ws
  "\"confidence_level\""      ":" ws confidence "," ws
  "\"primary_disease\""       ":" ws string "," ws
  "\"model_agreement\""       ":" ws number "," ws
  "\"suggested_precautions\"" ":" ws string-list "," ws
  "\"red_flags\""             ":" ws string-list
  ws "}"
confidence  ::= "\"high\"" | "\"medium\"" | "\"low\""
string-list ::= "[" ws (string ("," ws string)*)? ws "]"
string      ::= "\"" ([^"\\] | "\\" .)* "\""
number      ::= [0-9]+
ws          ::= [ \t\n\r]*
"""

SYSTEM_PROMPT = """You are a clinical triage assistant in an offline rural medical system.

Synthesize a structured diagnostic report from:
1. A normalized symptom list
2. Top-K disease predictions from a validated 3-model ensemble (SVM + Naive Bayes + Random Forest)
3. Retrieved precaution context from a verified offline medical knowledge base

STRICT RULES:
- diagnosis_summary: 2-3 sentences referencing only the top-ranked disease
- suggested_precautions: paraphrase ONLY from the retrieved context — never invent treatments
- confidence_level: "high" if model_agreement=3, "medium" if 2, "low" if 1
- red_flags: list emergency symptoms present (chest_pain, breathlessness, loss_of_balance, unconsciousness). Empty list [] if none.
- Output ONLY the JSON object. No preamble, no markdown, no disclaimers."""


def build_user_prompt(
    symptoms: list[str],
    top_k_diseases: list[dict],
    rag_context: list[dict],
    model_detail: dict,
) -> str:
    top_disease = top_k_diseases[0]["disease"]
    agreement = top_k_diseases[0].get("votes", 3)

    disease_block = "\n".join(
        f"  {d['rank']}. {d['disease']} — {d['probability']:.1%} ({d.get('votes','?')}/3 models)"
        for d in top_k_diseases[:5]
    )
    context_block = "\n\n".join(
        f"[Relevance: {r.get('score', 0):.3f} | Source: {r.get('source', 'KB')}]\n{r['text']}"
        for r in rag_context
    )
    model_block = (
        f"SVM={model_detail['svm_model_prediction']} | "
        f"NaiveBayes={model_detail['naive_bayes_prediction']} | "
        f"RandomForest={model_detail['rf_model_prediction']} → "
        f"Ensemble={model_detail['final_prediction']}"
    )

    return f"""SYMPTOMS ({len(symptoms)} active): {', '.join(symptoms)}

ENSEMBLE BREAKDOWN: {model_block}

TOP-5 DISEASE PROBABILITIES:
{disease_block}

RETRIEVED MEDICAL CONTEXT (precautions must come from here only):
{context_block}

Generate diagnostic JSON for: {top_disease} (agreement: {agreement}/3)."""


class ExplanationAgent:
    def __init__(self, model_dir: str = "models/", n_gpu_layers: int = 35, n_ctx: int = 2048):
        # Find the GGUF file automatically inside models/
        gguf_files = list(Path(model_dir).glob("*.gguf"))
        if not gguf_files:
            raise FileNotFoundError(f"No .gguf file found in {model_dir}")
        model_path = str(gguf_files[0])
        print(f"[LLM] Loading {model_path}")

        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=n_ctx,
            n_threads=4,
            verbose=False,
        )
        self.grammar = LlamaGrammar.from_string(DIAGNOSTIC_GRAMMAR)
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
        response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            grammar=self.grammar,
            max_tokens=512,
            temperature=0.1,
            top_p=0.9,
            repeat_penalty=1.1,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000
        raw = response["choices"][0]["message"]["content"]
        result = json.loads(raw)
        result["llm_inference_ms"] = round(elapsed_ms, 1)
        return result