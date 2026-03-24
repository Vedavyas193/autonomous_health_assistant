"""
TextNormalizerAgent — converts free text patient input into
canonical symptom names from the master symptom list.

Fully offline. No external APIs. Uses:
1. Direct keyword matching
2. Fuzzy matching (RapidFuzz)
3. Medical phrase patterns (spaCy)
4. Alias expansion
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import spacy
from rapidfuzz import process, fuzz

# ── Master symptom list (180 symptoms) ───────────────────────────────────────
# These must match exactly what the model was trained on
CANONICAL_SYMPTOMS: list[str] = [
    "high_fever", "mild_fever", "low_grade_fever", "chills", "rigors",
    "night_sweats", "sweating", "fatigue", "malaise", "lethargy",
    "weakness", "weight_loss", "weight_gain", "loss_of_appetite",
    "increased_appetite", "excessive_thirst", "dehydration",
    "headache", "severe_headache", "chest_pain", "abdominal_pain",
    "stomach_pain", "back_pain", "neck_pain", "joint_pain", "muscle_pain",
    "bone_pain", "knee_pain", "hip_joint_pain", "throat_pain",
    "pain_behind_eyes", "ear_pain", "pelvic_pain",
    "cough", "dry_cough", "productive_cough", "breathlessness",
    "wheezing", "chest_tightness", "rapid_breathing", "noisy_breathing",
    "runny_nose", "nasal_congestion", "sneezing", "sore_throat",
    "hoarseness", "blood_in_sputum", "phlegm", "mucoid_sputum",
    "nausea", "vomiting", "diarrhoea", "bloody_diarrhoea", "constipation",
    "bloating", "indigestion", "acidity", "heartburn", "regurgitation",
    "difficulty_swallowing", "loss_of_smell", "loss_of_taste",
    "stomach_bleeding", "black_tarry_stool", "bloody_stool",
    "mucus_in_stool", "abdominal_distension", "passage_of_gases",
    "jaundice", "yellowish_skin", "yellowing_of_eyes", "dark_urine",
    "pale_stool", "palpitations", "fast_heart_rate", "irregular_heartbeat",
    "chest_pressure", "ankle_swelling", "leg_swelling",
    "swollen_blood_vessels", "prominent_veins_on_calf", "cold_extremities",
    "dizziness", "vertigo", "loss_of_balance", "fainting", "seizures",
    "confusion", "altered_consciousness", "memory_loss", "slurred_speech",
    "facial_drooping", "limb_weakness", "numbness", "tingling",
    "visual_disturbances", "double_vision", "blurred_vision",
    "sensitivity_to_light", "sensitivity_to_sound", "stiff_neck",
    "neck_rigidity", "burning_urination", "frequent_urination",
    "painful_urination", "blood_in_urine", "cloudy_urine",
    "reduced_urine_output", "polyuria", "incontinence",
    "skin_rash", "itching", "hives", "blisters", "skin_peeling",
    "redness", "swelling", "nodules", "pustules", "dry_skin",
    "oily_skin", "hair_loss", "nail_changes", "bruising",
    "bleeding_tendency", "petechiae", "red_eyes", "watery_eyes",
    "eye_discharge", "ear_discharge", "hearing_loss", "ringing_in_ears",
    "mouth_ulcers", "swollen_lymph_nodes", "enlarged_tonsils",
    "excessive_hunger", "irregular_periods", "missed_period",
    "hot_flushes", "cold_intolerance", "heat_intolerance",
    "tremors", "enlarged_thyroid", "puffiness",
    "anxiety", "depression_symptoms", "irritability", "mood_swings",
    "sleep_disturbance", "restlessness", "poor_concentration",
    "muscle_cramps", "muscle_stiffness", "joint_stiffness",
    "reduced_mobility", "difficulty_walking", "falls",
]

# ── Comprehensive alias map ───────────────────────────────────────────────────
# Maps natural language phrases → canonical symptom names
ALIAS_MAP: dict[str, str] = {
    # Fever variants
    "fever":                    "high_fever",
    "high temperature":         "high_fever",
    "temperature":              "high_fever",
    "running a fever":          "high_fever",
    "burning up":               "high_fever",
    "slight fever":             "mild_fever",
    "low fever":                "mild_fever",
    "low grade fever":          "low_grade_fever",
    "feeling cold":             "chills",
    "feeling chilly":           "chills",
    "shivering":                "chills",
    "shaking":                  "rigors",
    "shaking with cold":        "rigors",
    "drenching sweats":         "night_sweats",
    "sweating at night":        "night_sweats",
    "sweaty":                   "sweating",

    # Fatigue
    "tired":                    "fatigue",
    "tiredness":                "fatigue",
    "exhausted":                "fatigue",
    "exhaustion":               "fatigue",
    "no energy":                "fatigue",
    "weak":                     "weakness",
    "feeling weak":             "weakness",
    "body weakness":            "weakness",
    "drowsy":                   "lethargy",
    "sluggish":                 "lethargy",

    # Weight
    "losing weight":            "weight_loss",
    "lost weight":              "weight_loss",
    "gaining weight":           "weight_gain",
    "put on weight":            "weight_gain",
    "not hungry":               "loss_of_appetite",
    "no appetite":              "loss_of_appetite",
    "dont feel like eating":    "loss_of_appetite",
    "always hungry":            "increased_appetite",
    "eating too much":          "increased_appetite",
    "very thirsty":             "excessive_thirst",
    "thirst":                   "excessive_thirst",
    "drinking a lot":           "excessive_thirst",

    # Head / Pain
    "headache":                 "headache",
    "head pain":                "headache",
    "head hurts":               "headache",
    "migraine":                 "severe_headache",
    "bad headache":             "severe_headache",
    "splitting headache":       "severe_headache",
    "chest pain":               "chest_pain",
    "chest hurts":              "chest_pain",
    "tightness in chest":       "chest_tightness",
    "stomach ache":             "stomach_pain",
    "tummy ache":               "stomach_pain",
    "stomach hurts":            "stomach_pain",
    "belly pain":               "abdominal_pain",
    "belly ache":               "abdominal_pain",
    "lower back pain":          "back_pain",
    "backache":                 "back_pain",
    "neck pain":                "neck_pain",
    "stiff neck":               "stiff_neck",
    "neck stiffness":           "neck_rigidity",
    "joint aches":              "joint_pain",
    "aching joints":            "joint_pain",
    "muscle aches":             "muscle_pain",
    "body aches":               "muscle_pain",
    "body pain":                "muscle_pain",
    "sore muscles":             "muscle_pain",
    "pain behind eyes":         "pain_behind_eyes",
    "eyes hurt":                "pain_behind_eyes",
    "sore throat":              "sore_throat",
    "throat pain":              "throat_pain",
    "throat hurts":             "sore_throat",

    # Respiratory
    "cough":                    "cough",
    "coughing":                 "cough",
    "dry cough":                "dry_cough",
    "wet cough":                "productive_cough",
    "coughing up phlegm":       "productive_cough",
    "coughing blood":           "blood_in_sputum",
    "coughing up blood":        "blood_in_sputum",
    "can't breathe":            "breathlessness",
    "difficulty breathing":     "breathlessness",
    "short of breath":          "breathlessness",
    "shortness of breath":      "breathlessness",
    "breathing difficulty":     "breathlessness",
    "wheezing":                 "wheezing",
    "wheeze":                   "wheezing",
    "breathing fast":           "rapid_breathing",
    "noisy breathing":          "noisy_breathing",
    "runny nose":               "runny_nose",
    "blocked nose":             "nasal_congestion",
    "stuffy nose":              "nasal_congestion",
    "sneezing":                 "sneezing",
    "hoarse voice":             "hoarseness",
    "lost voice":               "hoarseness",
    "mucus":                    "phlegm",
    "sputum":                   "phlegm",

    # Gastrointestinal
    "nausea":                   "nausea",
    "feeling sick":             "nausea",
    "feel like vomiting":       "nausea",
    "vomiting":                 "vomiting",
    "throwing up":              "vomiting",
    "puking":                   "vomiting",
    "loose motion":             "diarrhoea",
    "loose stool":              "diarrhoea",
    "loose motions":            "diarrhoea",
    "watery stool":             "diarrhoea",
    "runny stool":              "diarrhoea",
    "blood in stool":           "bloody_stool",
    "black stool":              "black_tarry_stool",
    "tarry stool":              "black_tarry_stool",
    "constipated":              "constipation",
    "can't pass stool":         "constipation",
    "bloated":                  "bloating",
    "gas":                      "passage_of_gases",
    "flatulence":               "passage_of_gases",
    "burping":                  "indigestion",
    "acid reflux":              "acidity",
    "burning in chest":         "heartburn",
    "trouble swallowing":       "difficulty_swallowing",
    "can't swallow":            "difficulty_swallowing",
    "yellow eyes":              "yellowing_of_eyes",
    "yellow skin":              "yellowish_skin",
    "yellow urine":             "dark_urine",
    "dark urine":               "dark_urine",
    "swollen stomach":          "abdominal_distension",

    # Cardiovascular
    "heart racing":             "palpitations",
    "heart pounding":           "palpitations",
    "heart beating fast":       "fast_heart_rate",
    "rapid heartbeat":          "fast_heart_rate",
    "irregular heartbeat":      "irregular_heartbeat",
    "swollen ankles":           "ankle_swelling",
    "swollen feet":             "ankle_swelling",
    "swollen legs":             "leg_swelling",
    "cold hands":               "cold_extremities",
    "cold feet":                "cold_extremities",

    # Neurological
    "dizzy":                    "dizziness",
    "dizziness":                "dizziness",
    "spinning":                 "vertigo",
    "room spinning":            "vertigo",
    "unsteady":                 "loss_of_balance",
    "falling":                  "loss_of_balance",
    "blackout":                 "fainting",
    "passed out":               "fainting",
    "fits":                     "seizures",
    "fit":                      "seizures",
    "convulsions":              "seizures",
    "confused":                 "confusion",
    "disoriented":              "confusion",
    "unconscious":              "altered_consciousness",
    "forgetful":                "memory_loss",
    "forgetting things":        "memory_loss",
    "slurred speech":           "slurred_speech",
    "can't speak properly":     "slurred_speech",
    "face drooping":            "facial_drooping",
    "arm weakness":             "limb_weakness",
    "leg weakness":             "limb_weakness",
    "numb":                     "numbness",
    "pins and needles":         "tingling",
    "can't see clearly":        "blurred_vision",
    "seeing double":            "double_vision",
    "light hurts eyes":         "sensitivity_to_light",
    "sound hurts":              "sensitivity_to_sound",

    # Urinary
    "burning when urinating":   "burning_urination",
    "pain when urinating":      "painful_urination",
    "peeing a lot":             "frequent_urination",
    "blood in urine":           "blood_in_urine",
    "cloudy urine":             "cloudy_urine",
    "passing urine frequently": "frequent_urination",
    "urinating frequently":     "frequent_urination",

    # Skin
    "rash":                     "skin_rash",
    "skin rash":                "skin_rash",
    "itchy":                    "itching",
    "itchy skin":               "itching",
    "hives":                    "hives",
    "blisters":                 "blisters",
    "skin peeling":             "skin_peeling",
    "peeling skin":             "skin_peeling",
    "red skin":                 "redness",
    "skin redness":             "redness",
    "swollen":                  "swelling",
    "lump":                     "nodules",
    "pimples":                  "pustules",
    "dry skin":                 "dry_skin",
    "hair falling":             "hair_loss",
    "hair fall":                "hair_loss",
    "bruise":                   "bruising",
    "bruises":                  "bruising",

    # Eyes / ENT
    "red eyes":                 "red_eyes",
    "watery eyes":              "watery_eyes",
    "eye discharge":            "eye_discharge",
    "ear pain":                 "ear_pain",
    "ear discharge":            "ear_discharge",
    "hearing loss":             "hearing_loss",
    "ringing in ears":          "ringing_in_ears",
    "mouth sore":               "mouth_ulcers",
    "mouth ulcer":              "mouth_ulcers",
    "glands swollen":           "swollen_lymph_nodes",
    "swollen glands":           "swollen_lymph_nodes",

    # Endocrine
    "always hungry":            "excessive_hunger",
    "missed period":            "missed_period",
    "irregular period":         "irregular_periods",
    "hot flashes":              "hot_flushes",
    "feeling hot":              "hot_flushes",
    "intolerant to cold":       "cold_intolerance",
    "intolerant to heat":       "heat_intolerance",
    "shaking hands":            "tremors",
    "hand tremors":             "tremors",
    "swollen neck":             "enlarged_thyroid",
    "puffy face":               "puffiness",
    "face swollen":             "puffiness",

    # Psychological
    "anxious":                  "anxiety",
    "worried":                  "anxiety",
    "feeling low":              "depression_symptoms",
    "sad":                      "depression_symptoms",
    "moody":                    "mood_swings",
    "mood swings":              "mood_swings",
    "can't sleep":              "sleep_disturbance",
    "insomnia":                 "sleep_disturbance",
    "restless":                 "restlessness",
    "can't concentrate":        "poor_concentration",
    "difficulty concentrating": "poor_concentration",

    # Musculoskeletal
    "cramps":                   "muscle_cramps",
    "muscle cramps":            "muscle_cramps",
    "stiff muscles":            "muscle_stiffness",
    "stiff joints":             "joint_stiffness",
    "can't move properly":      "reduced_mobility",
    "difficulty walking":       "difficulty_walking",
    "keep falling":             "falls",
}


@dataclass
class NLPResult:
    original_text: str
    extracted_symptoms: list[str]
    unmatched_phrases: list[str]
    match_method: dict[str, str]  # symptom → how it was matched


class TextNormalizerAgent:
    """
    Converts free-text patient descriptions into canonical symptom names.

    Pipeline:
    1. Clean and tokenize text
    2. Direct alias map lookup
    3. Canonical name direct match
    4. Fuzzy matching with RapidFuzz (threshold 80)
    5. spaCy NER for body parts and medical entities

    Fully offline — no external APIs.
    """

    FUZZY_THRESHOLD = 78  # minimum similarity score for fuzzy match

    def __init__(self):
        # Build reverse lookup: display name → canonical
        self.canonical_set = set(CANONICAL_SYMPTOMS)

        # Build readable versions for fuzzy matching
        # e.g. "high_fever" → "high fever"
        self.readable_map: dict[str, str] = {
            sym.replace("_", " "): sym
            for sym in CANONICAL_SYMPTOMS
        }

        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self._spacy_available = True
        except OSError:
            self._spacy_available = False
            print("[NLP] spaCy model not found — running without NER")

    def normalize(self, text: str) -> NLPResult:
        """
        Main entry point. Accepts any free text and returns
        a list of canonical symptom names.
        """
        original = text
        found: dict[str, str] = {}   # symptom → match method
        unmatched: list[str] = []

        # ── Step 1: Clean text ─────────────────────────────────────────────
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        # ── Step 2: Try multi-word alias matches first ─────────────────────
        # Sort by length descending so longer phrases match first
        sorted_aliases = sorted(ALIAS_MAP.keys(), key=len, reverse=True)
        remaining_text = text

        for phrase in sorted_aliases:
            if phrase in remaining_text:
                canonical = ALIAS_MAP[phrase]
                if canonical in self.canonical_set and canonical not in found:
                    found[canonical] = "alias"
                    # Remove matched phrase so it doesn't get double-matched
                    remaining_text = remaining_text.replace(phrase, " ", 1)

        # ── Step 3: Direct canonical name match ───────────────────────────
        # Check if any canonical name (with spaces) appears directly
        for readable, canonical in self.readable_map.items():
            if readable in remaining_text and canonical not in found:
                found[canonical] = "direct"
                remaining_text = remaining_text.replace(readable, " ", 1)

        # ── Step 4: Fuzzy match remaining words/bigrams/trigrams ──────────
        tokens = remaining_text.split()

        # Try single words, bigrams, trigrams
        ngrams = []
        for i in range(len(tokens)):
            ngrams.append(tokens[i])
            if i + 1 < len(tokens):
                ngrams.append(f"{tokens[i]} {tokens[i+1]}")
            if i + 2 < len(tokens):
                ngrams.append(f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}")

        for ngram in ngrams:
            if len(ngram) < 4:
                continue
            match = process.extractOne(
                ngram,
                list(self.readable_map.keys()),
                scorer=fuzz.token_sort_ratio,
                score_cutoff=self.FUZZY_THRESHOLD,
            )
            if match:
                canonical = self.readable_map[match[0]]
                if canonical not in found:
                    found[canonical] = f"fuzzy({match[1]:.0f}%)"

        # ── Step 5: spaCy entity extraction ───────────────────────────────
        if self._spacy_available:
            doc = self.nlp(text)
            for ent in doc.ents:
                ent_lower = ent.text.lower()
                if ent_lower in ALIAS_MAP:
                    canonical = ALIAS_MAP[ent_lower]
                    if canonical not in found:
                        found[canonical] = "spacy_ner"

        return NLPResult(
            original_text=original,
            extracted_symptoms=list(found.keys()),
            unmatched_phrases=[],
            match_method=found,
        )

    def normalize_list(self, items: list[str]) -> NLPResult:
        """
        Handles a mixed list of free-text strings and canonical names.
        e.g. ["I have a fever", "cough", "my back is hurting badly"]
        """
        all_found: dict[str, str] = {}

        for item in items:
            # Check if it's already a canonical name
            item_clean = item.strip().lower().replace(" ", "_")
            if item_clean in self.canonical_set:
                all_found[item_clean] = "exact"
                continue

            # Otherwise run full NLP pipeline
            result = self.normalize(item)
            all_found.update(result.match_method)

        return NLPResult(
            original_text=" | ".join(items),
            extracted_symptoms=list(all_found.keys()),
            unmatched_phrases=[],
            match_method=all_found,
        )