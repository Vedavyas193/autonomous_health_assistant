"""FAISS + MiniLM semantic retrieval for grounded medical snippets."""

from __future__ import annotations

import json
import os
from typing import List, Optional, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class RAGRetrievalAgent:
    def __init__(
        self,
        index_path: Optional[str] = None,
        meta_path: Optional[str] = None,
        base_dir: Optional[str] = None,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        if base_dir is not None:
            index_path = os.path.join(base_dir, "medical_knowledge.index")
            meta_path = os.path.join(base_dir, "rag_metadata.json")
        if index_path is None or meta_path is None:
            raise ValueError("Provide index_path and meta_path, or base_dir")

        print("Loading RAG Retrieval Agent...")
        self.embedder = SentenceTransformer(model_name)
        self.index = faiss.read_index(index_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            self.documents: List[str] = json.load(f)

    def _search(self, query: str, top_k: int) -> Tuple[List[str], List[int]]:
        q = self.embedder.encode([query], convert_to_numpy=True).astype("float32")
        distances, indices = self.index.search(np.array(q), k=min(top_k, len(self.documents)))
        idx_row = indices[0]
        texts: List[str] = []
        kept_idx: List[int] = []
        for j in idx_row:
            if j != -1 and j < len(self.documents):
                texts.append(self.documents[j])
                kept_idx.append(int(j))
        return texts, kept_idx

    def retrieve_for_disease(self, predicted_disease: str, top_k: int = 3) -> dict:
        """Top-K precaution/snippet chunks biased toward the ML disease label."""
        query = (
            f"Recommended precautions and clinical summary for disease: {predicted_disease}"
        )
        chunks, _ = self._search(query, top_k)
        return {
            "chunks": chunks,
            "retrieval_query": query,
        }

    def retrieve_context(self, symptoms_list: List[str], top_k: int = 3) -> dict:
        """Semantic search from symptom text (legacy / hybrid use)."""
        query = "Patient symptoms: " + ", ".join(symptoms_list)
        chunks, _ = self._search(query, top_k)
        return {
            "chunks": chunks,
            "retrieval_query": query,
        }
