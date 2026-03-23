"""
Run once before starting the server:
    python setup_rag.py

Reads symptom_precaution.csv and symptom_Description.csv from repo root,
builds a FAISS index + corpus JSON under data/.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
INDEX_PATH = "data/medical.faiss"
CORPUS_PATH = "data/medical_corpus.json"


def build_knowledge_base() -> list[dict]:
    """
    Merges symptom_precaution.csv and symptom_Description.csv into a
    flat list of {disease, text, source} dicts for FAISS indexing.
    """
    records = []

    # ── Precautions (4 per disease) ──────────────────────────────────────────
    prec_df = pd.read_csv("symptom_precaution.csv")
    prec_df.columns = prec_df.columns.str.strip()
    prec_cols = [c for c in prec_df.columns if c.lower().startswith("precaution")]

    for _, row in prec_df.iterrows():
        disease = str(row.get("Disease", row.iloc[0])).strip()
        precautions = [
            str(row[c]).strip()
            for c in prec_cols
            if pd.notna(row[c]) and str(row[c]).strip()
        ]
        if precautions:
            combined = f"Disease: {disease}. Precautions: {'. '.join(precautions)}."
            records.append({"disease": disease, "text": combined, "source": "precaution_db"})
            # Also add each precaution as a standalone chunk for finer retrieval
            for p in precautions:
                records.append(
                    {
                        "disease": disease,
                        "text": f"For {disease}: {p}.",
                        "source": "precaution_db",
                    }
                )

    # ── Descriptions ─────────────────────────────────────────────────────────
    try:
        desc_df = pd.read_csv("symptom_Description.csv")
        desc_df.columns = desc_df.columns.str.strip()
        desc_col = [c for c in desc_df.columns if c.lower() in ("description", "desc")][0]
        dis_col = [c for c in desc_df.columns if c.lower() in ("disease", "prognosis")][0]

        for _, row in desc_df.iterrows():
            disease = str(row[dis_col]).strip()
            desc = str(row[desc_col]).strip()
            if desc and desc.lower() != "nan":
                records.append(
                    {
                        "disease": disease,
                        "text": f"{disease}: {desc}",
                        "source": "description_db",
                    }
                )
    except Exception as e:
        print(f"[WARN] Could not load symptom_Description.csv: {e}")

    print(f"[RAG] Built {len(records)} knowledge chunks from {len(prec_df)} diseases.")
    return records


def build_index() -> None:
    Path("data").mkdir(exist_ok=True)

    knowledge_base = build_knowledge_base()
    encoder = SentenceTransformer(EMBEDDING_MODEL)

    texts = [entry["text"] for entry in knowledge_base]
    print(f"[RAG] Encoding {len(texts)} documents with {EMBEDDING_MODEL}...")

    embeddings = encoder.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)

    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)

    with open(CORPUS_PATH, "w") as f:
        json.dump(knowledge_base, f, indent=2)

    print(f"[RAG] Index saved to {INDEX_PATH} ({index.ntotal} vectors)")
    print(f"[RAG] Corpus saved to {CORPUS_PATH}")


if __name__ == "__main__":
    build_index()