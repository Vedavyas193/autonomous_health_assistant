from __future__ import annotations

from enum import Enum
from dataclasses import dataclass

import pandas as pd


class ComplexityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# Body systems — symptoms grouped by system for multi-system detection
SYSTEM_MAP: dict[str, list[str]] = {
    "respiratory": [
        "cough", "breathlessness", "mucoid_sputum", "rusty_sputum",
        "phlegm", "throat_irritation", "congestion", "chest_pain",
    ],
    "gastrointestinal": [
        "stomach_pain", "acidity", "vomiting", "nausea", "diarrhoea",
        "constipation", "abdominal_pain", "loss_of_appetite",
        "stomach_bleeding", "distention_of_abdomen",
    ],
    "neurological": [
        "headache", "dizziness", "loss_of_balance", "lack_of_concentration",
        "altered_sensorium", "slurred_speech", "spinning_movements",
        "visual_disturbances", "weakness_of_one_body_side",
    ],
    "cardiovascular": [
        "chest_pain", "fast_heart_rate", "palpitations",
        "prominent_veins_on_calf", "swollen_blood_vessels",
    ],
    "dermatological": [
        "itching", "skin_rash", "nodal_skin_eruptions", "dischromic_patches",
        "skin_peeling", "silver_like_dusting", "blister", "red_sores_around_nose",
        "yellow_crust_ooze",
    ],
    "musculoskeletal": [
        "joint_pain", "muscle_wasting", "muscle_weakness", "stiff_neck",
        "swelling_joints", "movement_stiffness", "painful_walking",
        "back_pain", "neck_pain", "knee_pain", "hip_joint_pain",
    ],
    "systemic": [
        "high_fever", "mild_fever", "fatigue", "malaise", "chills",
        "sweating", "dehydration", "lethargy", "weight_loss",
        "weight_gain", "excessive_hunger", "loss_of_appetite",
    ],
    "urogenital": [
        "burning_micturition", "spotting_urination", "dark_urine",
        "yellow_urine", "polyuria", "continuous_feel_of_urine",
        "irregular_sugar_level", "frequent_urination",
    ],
    "hepatic": [
        "yellowish_skin", "yellowing_of_eyes", "acute_liver_failure",
        "fluid_overload", "swelling_of_stomach", "enlarged_liver",
    ],
}

# Emergency symptoms that immediately push to HIGH regardless of other factors
EMERGENCY_SYMPTOMS: set[str] = {
    "chest_pain",
    "breathlessness",
    "loss_of_balance",
    "unconsciousness",
    "altered_sensorium",
    "slurred_speech",
    "weakness_of_one_body_side",
    "acute_liver_failure",
    "fluid_overload",
}

# High-severity diseases (from Symptom-severity.csv context)
HIGH_SEVERITY_DISEASES: set[str] = {
    "Heart attack",
    "Paralysis (brain hemorrhage)",
    "AIDS",
    "Hepatitis E",
    "Hepatitis D",
    "Tuberculosis",
    "Pneumonia",
}


@dataclass
class ComplexityResult:
    level: ComplexityLevel
    score: int                        # 0-100 internal score
    systems_involved: list[str]       # which body systems are active
    symptom_count: int
    has_emergency_symptoms: bool
    top_disease_is_severe: bool
    reasoning: str                    # human-readable explanation


class ComplexityAssessmentAgent:
    """
    Evaluates case complexity BEFORE routing to collaborative agents.

    Scoring:
      - Each active body system    → +15 points
      - Each emergency symptom     → +25 points
      - Symptom count > 5          → +10 points
      - Symptom count > 10         → +20 points
      - Top disease is high-severity → +20 points
      - Model agreement < 3        → +10 points (uncertainty penalty)

    Thresholds:
      LOW    → score < 30
      MEDIUM → 30 ≤ score < 60
      HIGH   → score ≥ 60
    """

    def __init__(self, severity_csv: str = "Symptom-severity.csv"):
        try:
            sev_df = pd.read_csv(severity_csv)
            sev_df.columns = sev_df.columns.str.strip()
            sym_col = [c for c in sev_df.columns if "symptom" in c.lower()][0]
            wt_col  = [c for c in sev_df.columns if "weight" in c.lower()][0]
            self.severity_map: dict[str, int] = dict(
                zip(
                    sev_df[sym_col].str.strip().str.lower().str.replace(" ", "_"),
                    sev_df[wt_col].astype(int),
                )
            )
        except Exception as e:
            print(f"[COMPLEXITY] Could not load severity CSV: {e}. Using defaults.")
            self.severity_map = {}

    def assess(
        self,
        symptoms: list[str],
        top_k_diseases: list[dict],
        model_agreement: int = 3,
    ) -> ComplexityResult:
        score = 0
        reasoning_parts = []

        # 1. Which body systems are involved
        active_systems = []
        for system, system_symptoms in SYSTEM_MAP.items():
            if any(s in system_symptoms for s in symptoms):
                active_systems.append(system)
        system_score = len(active_systems) * 15
        score += system_score
        if active_systems:
            reasoning_parts.append(
                f"{len(active_systems)} body system(s) involved: {', '.join(active_systems)}"
            )

        # 2. Emergency symptoms
        emergency_present = [s for s in symptoms if s in EMERGENCY_SYMPTOMS]
        emergency_score = len(emergency_present) * 25
        score += emergency_score
        if emergency_present:
            reasoning_parts.append(
                f"Emergency symptoms detected: {', '.join(emergency_present)}"
            )

        # 3. Symptom count penalty
        n = len(symptoms)
        if n > 10:
            score += 20
            reasoning_parts.append(f"High symptom count ({n} > 10)")
        elif n > 5:
            score += 10
            reasoning_parts.append(f"Moderate symptom count ({n} > 5)")

        # 4. Top disease severity
        top_disease = top_k_diseases[0]["disease"] if top_k_diseases else ""
        disease_is_severe = top_disease in HIGH_SEVERITY_DISEASES
        if disease_is_severe:
            score += 20
            reasoning_parts.append(f"Top disease '{top_disease}' is high-severity")

        # 5. Model uncertainty penalty
        if model_agreement < 3:
            score += 10
            reasoning_parts.append(
                f"Model disagreement ({model_agreement}/3 agreed)"
            )

        # 6. Symptom severity weight from CSV
        total_weight = sum(self.severity_map.get(s, 0) for s in symptoms)
        if total_weight > 20:
            score += 10
            reasoning_parts.append(f"High cumulative symptom severity weight ({total_weight})")

        # Clamp to 0-100
        score = min(score, 100)

        if score >= 60 or bool(emergency_present):
            level = ComplexityLevel.HIGH
        elif score >= 30:
            level = ComplexityLevel.MEDIUM
        else:
            level = ComplexityLevel.LOW

        return ComplexityResult(
            level=level,
            score=score,
            systems_involved=active_systems,
            symptom_count=n,
            has_emergency_symptoms=bool(emergency_present),
            top_disease_is_severe=disease_is_severe,
            reasoning=" | ".join(reasoning_parts) if reasoning_parts else "Routine case",
        )