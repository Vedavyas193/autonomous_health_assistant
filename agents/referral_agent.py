from __future__ import annotations

from dataclasses import dataclass

SPECIALIST_MAP: dict[str, str] = {
    "Hepatitis A":       "Gastroenterologist",
    "Hepatitis B":       "Gastroenterologist",
    "Hepatitis C":       "Gastroenterologist",
    "Hepatitis D":       "Gastroenterologist",
    "Hepatitis E":       "Gastroenterologist",
    "Jaundice":          "Gastroenterologist",
    "Alcoholic hepatitis": "Gastroenterologist",
    "Chronic cholestasis": "Gastroenterologist",
    "Peptic ulcer disease": "Gastroenterologist",
    "GERD":              "Gastroenterologist",
    "Gastroenteritis":   "Gastroenterologist",
    "Dimorphic hemorrhoids (piles)": "Proctologist",
    "Heart attack":      "Cardiologist",
    "Hypertension":      "Cardiologist",
    "Varicose veins":    "Vascular Surgeon",
    "Diabetes":          "Endocrinologist",
    "Hypothyroidism":    "Endocrinologist",
    "Hyperthyroidism":   "Endocrinologist",
    "Hypoglycemia":      "Endocrinologist",
    "Tuberculosis":      "Pulmonologist",
    "Pneumonia":         "Pulmonologist",
    "Bronchial Asthma":  "Pulmonologist",
    "Migraine":          "Neurologist",
    "Paralysis (brain hemorrhage)": "Neurologist",
    "(vertigo) Paroxysmal Positional Vertigo": "ENT Specialist",
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
    "Chicken pox":       "General Physician",
    "Common Cold":       "General Physician",
    "Allergy":           "Allergist",
    "Drug Reaction":     "General Physician",
}

URGENCY_MAP: dict[str, str] = {
    "Heart attack":                  "IMMEDIATE",
    "Paralysis (brain hemorrhage)":  "IMMEDIATE",
    "AIDS":                          "URGENT",
    "Tuberculosis":                  "URGENT",
    "Pneumonia":                     "URGENT",
    "Dengue":                        "URGENT",
    "Typhoid":                       "URGENT",
    "Hepatitis E":                   "URGENT",
    "Hepatitis D":                   "URGENT",
    "Malaria":                       "URGENT",
    "Hypoglycemia":                  "URGENT",
}


@dataclass
class ReferralResult:
    disease:          str
    specialist:       str
    urgency:          str   # IMMEDIATE | URGENT | ROUTINE
    referral_note:    str
    contact_advice:   str


class ReferralAgent:
    """
    Maps a diagnosed disease to the appropriate specialist and urgency level.
    Called after Risk Assessment regardless of complexity level.
    """

    def refer(self, disease: str, is_emergency: bool) -> ReferralResult:
        specialist = SPECIALIST_MAP.get(disease, "General Physician")

        if is_emergency or URGENCY_MAP.get(disease) == "IMMEDIATE":
            urgency = "IMMEDIATE"
            note = (
                f"Patient requires IMMEDIATE transfer to {specialist}. "
                "Do not delay — activate emergency protocols now."
            )
            contact = "Call emergency services or transport to nearest hospital immediately."
        elif URGENCY_MAP.get(disease) == "URGENT":
            urgency = "URGENT"
            note = (
                f"Refer to {specialist} within 24-48 hours. "
                "Begin supportive treatment immediately while arranging referral."
            )
            contact = f"Schedule urgent appointment with {specialist} today."
        else:
            urgency = "ROUTINE"
            note = (
                f"Routine referral to {specialist} recommended. "
                "Patient can be managed at primary care level in the interim."
            )
            contact = f"Schedule appointment with {specialist} within the week."

        return ReferralResult(
            disease=disease,
            specialist=specialist,
            urgency=urgency,
            referral_note=note,
            contact_advice=contact,
        )