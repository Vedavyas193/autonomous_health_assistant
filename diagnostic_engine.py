from __future__ import annotations

import json
import pickle
from pathlib import Path
from statistics import mode
from typing import TypedDict

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score


class DiseaseScore(TypedDict):
    disease: str
    probability: float
    rank: int
    votes: int


class DiagnosticEngine:
    def __init__(self, model_dir: str = "models/"):
        pkl_path = Path(model_dir) / "ensemble.pkl"
        if not pkl_path.exists():
            raise FileNotFoundError(
                f"No ensemble found at {pkl_path}. Run train.py first."
            )
        with open(pkl_path, "rb") as f:
            artefacts = pickle.load(f)

        self.svm: SVC = artefacts["svm"]
        self.nb: GaussianNB = artefacts["nb"]
        self.rf: RandomForestClassifier = artefacts["rf"]
        self.encoder: LabelEncoder = artefacts["encoder"]
        self.symptom_cols: list[str] = artefacts["symptom_cols"]
        self.symptom_index: dict[str, int] = {
            sym: idx for idx, sym in enumerate(self.symptom_cols)
        }
        self.disease_labels: list[str] = list(self.encoder.classes_)
        print(
            f"[ENGINE] Loaded {len(self.disease_labels)} disease classes, "
            f"{len(self.symptom_cols)} symptom features."
        )

    def build_symptom_vector(self, symptoms: list[str]) -> np.ndarray:
        vector = np.zeros(len(self.symptom_cols), dtype=np.float32)
        for s in symptoms:
            idx = self.symptom_index.get(s.strip().lower())
            if idx is not None:
                vector[idx] = 1.0
        return vector

    def predict_top_k(
        self, symptom_vector: np.ndarray, top_k: int = 5
    ) -> list[DiseaseScore]:
        if symptom_vector.ndim == 1:
            symptom_vector = symptom_vector.reshape(1, -1)

        svm_pred = self.svm.predict(symptom_vector)[0]
        nb_pred = self.nb.predict(symptom_vector)[0]
        rf_pred = self.rf.predict(symptom_vector)[0]

        vote_counts: dict[int, int] = {}
        for p in [svm_pred, nb_pred, rf_pred]:
            vote_counts[p] = vote_counts.get(p, 0) + 1

        svm_proba = self.svm.predict_proba(symptom_vector)[0]
        nb_proba = self.nb.predict_proba(symptom_vector)[0]
        rf_proba = self.rf.predict_proba(symptom_vector)[0]
        mean_proba = (svm_proba + nb_proba + rf_proba) / 3.0

        top_k_indices = np.argsort(mean_proba)[::-1][:top_k]

        results: list[DiseaseScore] = []
        for rank, idx in enumerate(top_k_indices):
            results.append(
                DiseaseScore(
                    disease=self.disease_labels[idx],
                    probability=float(round(mean_proba[idx], 4)),
                    rank=rank + 1,
                    votes=vote_counts.get(int(idx), 0),
                )
            )
        results[0]["ensemble_winner"] = self.disease_labels[
            mode([svm_pred, nb_pred, rf_pred])
        ]
        return results

    def predict_single(self, symptom_vector: np.ndarray) -> dict:
        if symptom_vector.ndim == 1:
            symptom_vector = symptom_vector.reshape(1, -1)

        svm_pred = self.encoder.inverse_transform(self.svm.predict(symptom_vector))[0]
        nb_pred = self.encoder.inverse_transform(self.nb.predict(symptom_vector))[0]
        rf_pred = self.encoder.inverse_transform(self.rf.predict(symptom_vector))[0]

        encoded = [
            self.encoder.transform([svm_pred])[0],
            self.encoder.transform([nb_pred])[0],
            self.encoder.transform([rf_pred])[0],
        ]
        final = self.encoder.inverse_transform([mode(encoded)])[0]

        return {
            "svm_model_prediction": svm_pred,
            "naive_bayes_prediction": nb_pred,
            "rf_model_prediction": rf_pred,
            "final_prediction": final,
        }


class IntakeAgent:
    ALIAS_MAP: dict[str, str] = {
        "stomach ache": "stomach_pain",
        "high temperature": "high_fever",
        "runny nose": "runny_nose",
        "joint pain": "joint_pain",
        "tired": "fatigue",
        "headache": "headache",
        "throwing up": "vomiting",
        "can't breathe": "breathlessness",
        "itching": "itching",
        "skin rash": "skin_rash",
        "fever": "high_fever",
        "chills": "chills",
        "nausea": "nausea",
        "cough": "cough",
        "diarrhea": "diarrhoea",
    }

    def __init__(self, symptom_cols: list[str]):
        self.valid_symptoms = set(symptom_cols)

    def normalize(self, raw_symptoms: list[str]) -> tuple[list[str], list[str]]:
        normalized, unknown = [], []
        for s in raw_symptoms:
            canonical = s.strip().lower().replace(" ", "_")
            canonical = self.ALIAS_MAP.get(s.strip().lower(), canonical)
            if canonical in self.valid_symptoms:
                normalized.append(canonical)
            else:
                unknown.append(s)
        return normalized, unknown