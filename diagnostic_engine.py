from __future__ import annotations

import json
import pickle
from pathlib import Path
from statistics import mode
from typing import TypedDict

import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder


class DiseaseScore(TypedDict):
    disease: str
    probability: float
    rank: int
    votes: int


class DiagnosticEngine:
    def __init__(self, model_dir: str = "models/"):
        pkl_path = Path(model_dir) / "ensemble.pkl"
        if not pkl_path.exists():
            raise FileNotFoundError(f"No ensemble found at {pkl_path}. Run train.py first.")
        with open(pkl_path, "rb") as f:
            artefacts = pickle.load(f)

        self.rf:      RandomForestClassifier     = artefacts["rf"]
        self.gb:      GradientBoostingClassifier = artefacts["gb"]
        self.nb:      GaussianNB                 = artefacts["nb"]
        self.encoder: LabelEncoder               = artefacts["encoder"]
        self.symptom_cols: list[str]             = artefacts["symptom_cols"]
        self.symptom_index: dict[str, int]       = {
            sym: idx for idx, sym in enumerate(self.symptom_cols)
        }
        self.disease_labels: list[str] = list(self.encoder.classes_)
        print(f"[ENGINE] Loaded {len(self.disease_labels)} diseases, {len(self.symptom_cols)} symptoms.")

    def build_symptom_vector(self, symptoms: list[str]) -> np.ndarray:
        vector = np.zeros(len(self.symptom_cols), dtype=np.float32)
        for s in symptoms:
            idx = self.symptom_index.get(s.strip().lower())
            if idx is not None:
                vector[idx] = 1.0
        return vector

    def get_confidence_from_probability(self, top_k: list, symptoms: list[str]) -> str:
        if not top_k:
            return "low"
        top_prob    = top_k[0]["probability"]
        votes       = top_k[0].get("votes", 0)
        n_symptoms  = len(symptoms)
        if top_prob >= 0.70 and votes == 3 and n_symptoms >= 5:
            return "high"
        elif top_prob >= 0.45 and votes >= 2 and n_symptoms >= 3:
            return "medium"
        return "low"

    def predict_top_k(self, symptom_vector: np.ndarray, top_k: int = 5) -> list[DiseaseScore]:
        if symptom_vector.ndim == 1:
            symptom_vector = symptom_vector.reshape(1, -1)

        rf_pred = self.rf.predict(symptom_vector)[0]
        gb_pred = self.gb.predict(symptom_vector)[0]
        nb_pred = self.nb.predict(symptom_vector)[0]

        vote_counts: dict[int, int] = {}
        for p in [rf_pred, gb_pred, nb_pred]:
            vote_counts[p] = vote_counts.get(p, 0) + 1

        rf_proba = self.rf.predict_proba(symptom_vector)[0]
        gb_proba = self.gb.predict_proba(symptom_vector)[0]
        nb_proba = self.nb.predict_proba(symptom_vector)[0]
        mean_proba = (rf_proba + gb_proba + nb_proba) / 3.0

        top_k_indices = np.argsort(mean_proba)[::-1][:top_k]
        results: list[DiseaseScore] = []
        for rank, idx in enumerate(top_k_indices):
            results.append(DiseaseScore(
                disease=self.disease_labels[idx],
                probability=float(round(mean_proba[idx], 4)),
                rank=rank + 1,
                votes=vote_counts.get(int(idx), 0),
            ))
        results[0]["ensemble_winner"] = self.disease_labels[mode([rf_pred, gb_pred, nb_pred])]
        return results

    def predict_single(self, symptom_vector: np.ndarray) -> dict:
        if symptom_vector.ndim == 1:
            symptom_vector = symptom_vector.reshape(1, -1)

        rf_pred = self.encoder.inverse_transform(self.rf.predict(symptom_vector))[0]
        gb_pred = self.encoder.inverse_transform(self.gb.predict(symptom_vector))[0]
        nb_pred = self.encoder.inverse_transform(self.nb.predict(symptom_vector))[0]

        encoded = [
            self.encoder.transform([rf_pred])[0],
            self.encoder.transform([gb_pred])[0],
            self.encoder.transform([nb_pred])[0],
        ]
        final = self.encoder.inverse_transform([mode(encoded)])[0]

        return {
            "svm_model_prediction":   rf_pred,   # key kept for frontend compat
            "naive_bayes_prediction": nb_pred,
            "rf_model_prediction":    gb_pred,
            "final_prediction":       final,
        }


class IntakeAgent:
    """Uses TextNormalizerAgent for free text + canonical name matching."""

    def __init__(self, symptom_cols: list[str]):
        self.valid_symptoms = set(symptom_cols)
        from agents.nlp_agent import TextNormalizerAgent
        self.nlp_agent = TextNormalizerAgent()

    def normalize(self, raw_symptoms: list[str]) -> tuple[list[str], list[str]]:
        result = self.nlp_agent.normalize_list(raw_symptoms)
        normalized = [s for s in result.extracted_symptoms if s in self.valid_symptoms]
        unknown    = [s for s in result.extracted_symptoms if s not in self.valid_symptoms]
        # Also check any inputs that were already canonical names
        for item in raw_symptoms:
            clean = item.strip().lower().replace(" ", "_")
            if clean in self.valid_symptoms and clean not in normalized:
                normalized.append(clean)
        print(f"[INTAKE] {len(raw_symptoms)} inputs → {len(normalized)} matched")
        return normalized, unknown