from __future__ import annotations

import time
from dataclasses import dataclass, field

from agents.complexity_agent import ComplexityLevel, ComplexityResult


# ── Shared output types ───────────────────────────────────────────────────────

@dataclass
class SymptomAnalysis:
    active_symptoms:      list[str]
    severity_scores:      dict[str, int]
    dominant_system:      str
    total_severity_score: int
    pattern_notes:        str
    analysis_ms:          float = 0.0


@dataclass
class DifferentialDxResult:
    ranked_diagnoses:    list[dict]   # [{disease, probability, votes, notes}]
    ruled_out:           list[str]    # diseases the symptom pattern argues against
    primary_confidence:  str          # "high" | "medium" | "low"
    emr_notes:           str          # reasoning from EMR / knowledge base context
    differential_ms:     float = 0.0


@dataclass
class TreatmentPlan:
    primary_disease:        str
    immediate_actions:      list[str]  # things to do right now
    precautions:            list[str]  # grounded from RAG context
    lifestyle_advice:       list[str]
    follow_up:              str
    refer_to_specialist:    bool
    specialist_type:        str
    treatment_ms:           float = 0.0


@dataclass
class CollaborativeResult:
    """Final merged output from all three collaborative agents."""
    symptom_analysis:    SymptomAnalysis
    differential:        DifferentialDxResult
    treatment_plan:      TreatmentPlan
    complexity_level:    str
    total_collab_ms:     float = 0.0


# ── Symptom Analyst Agent ─────────────────────────────────────────────────────

SYSTEM_SEVERITY_MAP: dict[str, int] = {
    "chest_pain": 7, "breathlessness": 7, "unconsciousness": 7,
    "altered_sensorium": 7, "high_fever": 6, "vomiting": 5,
    "fatigue": 4, "headache": 4, "nausea": 3, "itching": 2,
    "skin_rash": 2, "cough": 3, "chills": 4, "sweating": 3,
    "joint_pain": 3, "muscle_wasting": 5, "weight_loss": 5,
    "loss_of_appetite": 4, "abdominal_pain": 5, "diarrhoea": 4,
}

SYSTEM_MAP_SIMPLE: dict[str, list[str]] = {
    "respiratory":     ["cough", "breathlessness", "phlegm", "chest_pain"],
    "gastrointestinal":["stomach_pain", "vomiting", "nausea", "diarrhoea", "abdominal_pain"],
    "neurological":    ["headache", "dizziness", "loss_of_balance", "altered_sensorium"],
    "cardiovascular":  ["chest_pain", "fast_heart_rate", "palpitations"],
    "dermatological":  ["itching", "skin_rash", "nodal_skin_eruptions"],
    "musculoskeletal": ["joint_pain", "muscle_wasting", "stiff_neck", "back_pain"],
    "systemic":        ["high_fever", "mild_fever", "fatigue", "malaise", "chills", "sweating"],
    "hepatic":         ["yellowish_skin", "yellowing_of_eyes", "acute_liver_failure"],
}


class SymptomAnalystAgent:
    """
    Agent 1 of 3 in the collaborative pipeline.
    Analyzes symptom patterns, scores severity, identifies dominant body system.
    """

    def analyze(
        self,
        symptoms: list[str],
        severity_map: dict[str, int] | None = None,
    ) -> SymptomAnalysis:
        t0 = time.perf_counter()
        sev = severity_map or SYSTEM_SEVERITY_MAP

        # Score each symptom
        scores = {s: sev.get(s, 1) for s in symptoms}
        total  = sum(scores.values())

        # Find dominant system
        system_counts: dict[str, int] = {}
        for system, sys_symptoms in SYSTEM_MAP_SIMPLE.items():
            count = sum(1 for s in symptoms if s in sys_symptoms)
            if count:
                system_counts[system] = count
        dominant = max(system_counts, key=system_counts.get) if system_counts else "systemic"

        # Pattern notes
        notes_parts = []
        if total > 25:
            notes_parts.append("High overall severity — immediate attention advised")
        if len(system_counts) >= 3:
            notes_parts.append(
                f"Multi-system involvement ({len(system_counts)} systems)"
            )
        high_sev = [s for s, v in scores.items() if v >= 6]
        if high_sev:
            notes_parts.append(f"Critical symptoms present: {', '.join(high_sev)}")
        if not notes_parts:
            notes_parts.append("Symptom pattern consistent with single-system acute illness")

        return SymptomAnalysis(
            active_symptoms=symptoms,
            severity_scores=scores,
            dominant_system=dominant,
            total_severity_score=total,
            pattern_notes=" | ".join(notes_parts),
            analysis_ms=round((time.perf_counter() - t0) * 1000, 1),
        )


# ── Differential Diagnosis Agent ─────────────────────────────────────────────

class DifferentialDxAgent:
    """
    Agent 2 of 3. Cross-references ML ensemble output with symptom analysis
    and RAG context to produce a ranked differential diagnosis with reasoning.
    """

    def diagnose(
        self,
        top_k_diseases: list[dict],
        symptom_analysis: SymptomAnalysis,
        rag_context: list[dict],
        model_breakdown: dict,
    ) -> DifferentialDxResult:
        t0 = time.perf_counter()

        # Build ranked list with EMR-grounded notes
        rag_diseases = {
            doc.get("disease", "").lower()
            for doc in rag_context
        }
        ranked = []
        for d in top_k_diseases:
            is_rag_confirmed = d["disease"].lower() in rag_diseases
            notes = (
                "Confirmed in retrieved knowledge base"
                if is_rag_confirmed
                else "Based on symptom vector only"
            )
            # Agreement-weighted confidence note
            if d.get("votes", 0) == 3:
                notes += " · All 3 models agree"
            elif d.get("votes", 0) == 2:
                notes += " · 2/3 models agree"
            else:
                notes += " · Single model prediction — treat with caution"

            ranked.append({**d, "dx_notes": notes, "rag_confirmed": is_rag_confirmed})

        # Dominant system consistency check — rule out diseases
        # that don't match the dominant system at all
        ruled_out: list[str] = []
        SYSTEM_DISEASE_MAP: dict[str, set[str]] = {
            "hepatic":          {"Hepatitis A", "Hepatitis B", "Hepatitis C",
                                  "Hepatitis D", "Hepatitis E", "Jaundice",
                                  "Alcoholic hepatitis", "Chronic cholestasis"},
            "cardiovascular":   {"Heart attack", "Hypertension", "Varicose veins"},
            "neurological":     {"Migraine", "Paralysis (brain hemorrhage)",
                                  "Cervical spondylosis",
                                  "(vertigo) Paroxysmal Positional Vertigo"},
            "dermatological":   {"Fungal infection", "Psoriasis", "Acne",
                                  "Chicken pox", "Impetigo"},
            "respiratory":      {"Bronchial Asthma", "Tuberculosis", "Common Cold",
                                  "Pneumonia"},
        }
        system_diseases = SYSTEM_DISEASE_MAP.get(symptom_analysis.dominant_system, set())
        if system_diseases:
            for d in top_k_diseases[2:]:   # only consider low-ranked candidates
                if (
                    d["disease"] not in system_diseases
                    and d["probability"] < 0.15
                    and d.get("votes", 0) < 2
                ):
                    ruled_out.append(d["disease"])

        # Primary confidence from top disease vote count
        top_votes = top_k_diseases[0].get("votes", 3) if top_k_diseases else 0
        primary_confidence = (
            "high"   if top_votes == 3 else
            "medium" if top_votes == 2 else
            "low"
        )

        emr_notes = (
            f"Dominant system: {symptom_analysis.dominant_system}. "
            f"Total severity score: {symptom_analysis.total_severity_score}. "
            f"RAG confirmed top disease: "
            f"{'Yes' if ranked and ranked[0].get('rag_confirmed') else 'No'}."
        )

        return DifferentialDxResult(
            ranked_diagnoses=ranked,
            ruled_out=ruled_out,
            primary_confidence=primary_confidence,
            emr_notes=emr_notes,
            differential_ms=round((time.perf_counter() - t0) * 1000, 1),
        )


# ── Treatment Planner Agent ───────────────────────────────────────────────────

SPECIALIST_MAP: dict[str, str] = {
    "Hepatitis A":       "Gastroenterologist",
    "Hepatitis B":       "Gastroenterologist",
    "Hepatitis C":       "Gastroenterologist",
    "Hepatitis D":       "Gastroenterologist",
    "Hepatitis E":       "Gastroenterologist",
    "Jaundice":          "Gastroenterologist",
    "Alcoholic hepatitis":"Gastroenterologist",
    "Heart attack":      "Cardiologist",
    "Hypertension":      "Cardiologist",
    "Varicose veins":    "Vascular Surgeon",
    "Diabetes":          "Endocrinologist",
    "Hypothyroidism":    "Endocrinologist",
    "Hyperthyroidism":   "Endocrinologist",
    "Tuberculosis":      "Pulmonologist",
    "Pneumonia":         "Pulmonologist",
    "Bronchial Asthma":  "Pulmonologist",
    "Migraine":          "Neurologist",
    "Paralysis (brain hemorrhage)": "Neurologist",
    "Cervical spondylosis": "Orthopedist",
    "Osteoarthritis":    "Orthopedist",
    "Arthritis":         "Rheumatologist",
    "AIDS":              "Infectious Disease Specialist",
    "Malaria":           "Infectious Disease Specialist",
    "Dengue":            "Infectious Disease Specialist",
    "Typhoid":           "Infectious Disease Specialist",
    "Urinary tract infection": "Urologist",
    "Psoriasis":         "Dermatologist",
    "Acne":              "Dermatologist",
    "Fungal infection":  "Dermatologist",
    "Impetigo":          "Dermatologist",
    "Hypoglycemia":      "Endocrinologist",
    "Peptic ulcer disease": "Gastroenterologist",
    "GERD":              "Gastroenterologist",
    "Gastroenteritis":   "Gastroenterologist",
    "Dimorphic hemorrhoids (piles)": "Proctologist",
    "(vertigo) Paroxysmal Positional Vertigo": "ENT Specialist",
    "Common Cold":       "General Physician",
    "Allergy":           "Allergist",
    "Drug Reaction":     "General Physician",
    "Chicken pox":       "General Physician",
    "Chronic cholestasis": "Gastroenterologist",
}

IMMEDIATE_ACTIONS_MAP: dict[str, list[str]] = {
    "Heart attack":      ["Call emergency services immediately", "Administer aspirin if available and not contraindicated", "Keep patient calm and still"],
    "Paralysis (brain hemorrhage)": ["Call emergency services immediately", "Do not give food or water", "Keep head elevated"],
    "Malaria":           ["Start oral rehydration", "Reduce fever with cool compresses", "Seek antimalarial treatment within 24 hours"],
    "Dengue":            ["Oral rehydration therapy", "Avoid NSAIDs — use paracetamol only for fever", "Monitor platelet count"],
    "Tuberculosis":      ["Isolate patient from others", "Refer to DOTS program", "Do not delay treatment"],
    "Pneumonia":         ["Monitor oxygen saturation if available", "Keep patient upright", "Antibiotic therapy required — refer immediately"],
    "Diabetes":          ["Monitor blood glucose", "Ensure adequate hydration", "Review current medication"],
    "Hypoglycemia":      ["Administer 15g fast-acting carbohydrate immediately", "Recheck glucose in 15 minutes", "Do not leave patient alone"],
}


class TreatmentPlannerAgent:
    """
    Agent 3 of 3. Builds a structured treatment plan using:
    - RAG-grounded precautions (no hallucination)
    - Immediate action protocols per disease
    - Specialist referral mapping
    """

    def plan(
        self,
        primary_disease: str,
        differential: DifferentialDxResult,
        rag_context: list[dict],
        complexity_level: ComplexityLevel,
    ) -> TreatmentPlan:
        t0 = time.perf_counter()

        # Precautions strictly from RAG context
        precautions: list[str] = []
        for doc in rag_context:
            text = doc.get("text", "")
            if primary_disease.lower() in text.lower() or doc.get("disease","").lower() == primary_disease.lower():
                # Extract precaution sentences
                sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 15]
                precautions.extend(sentences[:3])
        # Deduplicate
        seen = set()
        unique_precautions = []
        for p in precautions:
            if p.lower() not in seen:
                seen.add(p.lower())
                unique_precautions.append(p)
        precautions = unique_precautions[:4] if unique_precautions else [
            "Follow prescribed medication schedule",
            "Maintain adequate hydration",
            "Rest and avoid strenuous activity",
        ]

        # Immediate actions
        immediate = IMMEDIATE_ACTIONS_MAP.get(primary_disease, [
            "Consult a healthcare provider",
            "Monitor symptoms for worsening",
            "Maintain hydration and rest",
        ])

        # Lifestyle advice based on complexity
        if complexity_level == ComplexityLevel.HIGH:
            lifestyle = [
                "Bed rest — avoid all physical activity",
                "Strict dietary compliance as directed by physician",
                "Daily vital signs monitoring",
            ]
        elif complexity_level == ComplexityLevel.MEDIUM:
            lifestyle = [
                "Light activity only — no strenuous exercise",
                "Balanced diet, avoid junk food",
                "Regular hydration — at least 2L water daily",
            ]
        else:
            lifestyle = [
                "Regular rest schedule",
                "Stay hydrated",
                "Monitor and report symptom changes",
            ]

        # Referral
        specialist = SPECIALIST_MAP.get(primary_disease, "General Physician")
        should_refer = (
            complexity_level == ComplexityLevel.HIGH
            or differential.primary_confidence == "low"
            or primary_disease in {"Heart attack", "Paralysis (brain hemorrhage)",
                                   "AIDS", "Tuberculosis"}
        )

        follow_up = (
            "Within 24 hours — EMERGENCY" if complexity_level == ComplexityLevel.HIGH
            else "Within 48-72 hours" if complexity_level == ComplexityLevel.MEDIUM
            else "Within 1 week if symptoms persist"
        )

        return TreatmentPlan(
            primary_disease=primary_disease,
            immediate_actions=immediate,
            precautions=precautions,
            lifestyle_advice=lifestyle,
            follow_up=follow_up,
            refer_to_specialist=should_refer,
            specialist_type=specialist,
            treatment_ms=round((time.perf_counter() - t0) * 1000, 1),
        )


# ── Collaborative Pipeline (orchestrates all 3 agents) ───────────────────────

class CollaborativeDiagnosticPipeline:
    """
    Orchestrates SymptomAnalyst → DifferentialDx → TreatmentPlanner.
    Only called for LOW and MEDIUM complexity cases.
    HIGH complexity bypasses this and goes straight to emergency referral.
    """

    def __init__(self):
        self.symptom_analyst  = SymptomAnalystAgent()
        self.differential_dx  = DifferentialDxAgent()
        self.treatment_planner = TreatmentPlannerAgent()

    def run(
        self,
        symptoms:       list[str],
        top_k_diseases: list[dict],
        rag_context:    list[dict],
        model_breakdown: dict,
        complexity:     ComplexityResult,
        severity_map:   dict[str, int] | None = None,
    ) -> CollaborativeResult:
        t_start = time.perf_counter()

        # Agent 1
        analysis = self.symptom_analyst.analyze(symptoms, severity_map)

        # Agent 2
        differential = self.differential_dx.diagnose(
            top_k_diseases, analysis, rag_context, model_breakdown
        )

        # Agent 3
        plan = self.treatment_planner.plan(
            primary_disease=top_k_diseases[0]["disease"],
            differential=differential,
            rag_context=rag_context,
            complexity_level=complexity.level,
        )

        return CollaborativeResult(
            symptom_analysis=analysis,
            differential=differential,
            treatment_plan=plan,
            complexity_level=complexity.level.value,
            total_collab_ms=round((time.perf_counter() - t_start) * 1000, 1),
        )