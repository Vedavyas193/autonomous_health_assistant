"""XGBoost triage classifier: 132-symptom binary vector and Top-K disease probabilities."""

from __future__ import annotations

import json
import os
from typing import List, Tuple

import joblib
import numpy as np
import xgboost as xgb


class TriageMLClassifier:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self._model = xgb.XGBClassifier()
        model_path = os.path.join(base_dir, "disease_classifier.json")
        self._model.load_model(model_path)
        self._label_encoder = joblib.load(os.path.join(base_dir, "label_encoder.pkl"))
        with open(os.path.join(base_dir, "symptom_columns.json"), encoding="utf-8") as f:
            self.symptom_columns: List[str] = json.load(f)

    def symptoms_to_vector(self, symptoms: List[str]) -> np.ndarray:
        vec = np.zeros(len(self.symptom_columns), dtype=np.float32)
        for symptom in symptoms:
            clean = symptom.replace(" ", "_").lower().strip()
            if clean in self.symptom_columns:
                idx = self.symptom_columns.index(clean)
                vec[idx] = 1.0
        return vec

    def predict_top_k(self, symptoms: List[str], k: int = 5) -> Tuple[str, float, List[Tuple[str, float]]]:
        """
        Returns (top_disease, top_probability_0_100, [(disease, prob_0_100), ...]).
        """
        input_vector = self.symptoms_to_vector(symptoms).reshape(1, -1)
        proba = self._model.predict_proba(input_vector)[0]
        order = np.argsort(-proba)
        k = min(k, len(order))
        top: List[Tuple[str, float]] = []
        for i in range(k):
            idx = int(order[i])
            name = str(self._label_encoder.inverse_transform([idx])[0])
            p = round(float(proba[idx]) * 100, 4)
            top.append((name, p))
        top_disease, top_p = top[0]
        return top_disease, top_p, top
