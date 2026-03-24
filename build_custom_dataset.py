"""
Builds a unified training dataset combining:
1. DDXPlus (49 diseases, 223 symptoms, realistic co-occurrence)
2. Augmented Kaggle dataset (cleaned, with noise injection)

Output: dataset/Training_v2.csv and dataset/Testing_v2.csv
"""

import json
import random
import numpy as np
import pandas as pd
from pathlib import Path

random.seed(42)
np.random.seed(42)

# ── 1. Full disease list (75 diseases) ────────────────────────────────────────

DISEASES = [
    # Infectious & Tropical
    "Malaria", "Dengue", "Typhoid", "Tuberculosis", "Pneumonia",
    "Influenza", "COVID-19", "Cholera", "Leptospirosis", "Chikungunya",
    "Meningitis", "Septicemia", "Measles", "Mumps", "Rubella",
    "Chickenpox", "Herpes Zoster", "Rabies", "Tetanus",
    # Gastrointestinal
    "GERD", "Peptic Ulcer Disease", "Gastroenteritis", "Appendicitis",
    "Irritable Bowel Syndrome", "Crohn's Disease", "Ulcerative Colitis",
    "Hepatitis A", "Hepatitis B", "Hepatitis C", "Alcoholic Hepatitis",
    "Liver Cirrhosis", "Pancreatitis", "Cholecystitis", "Jaundice",
    # Chronic & Metabolic
    "Type 2 Diabetes", "Type 1 Diabetes", "Hypoglycemia",
    "Hypertension", "Hypothyroidism", "Hyperthyroidism",
    "Obesity", "Anaemia", "Vitamin D Deficiency", "Iron Deficiency",
    # Cardiovascular
    "Heart Attack", "Heart Failure", "Angina", "Arrhythmia",
    "Deep Vein Thrombosis", "Varicose Veins",
    # Respiratory
    "Bronchial Asthma", "COPD", "Bronchitis", "Pleurisy",
    "Pulmonary Embolism", "Common Cold", "Sinusitis",
    # Neurological
    "Migraine", "Tension Headache", "Epilepsy", "Stroke",
    "Parkinson's Disease", "Vertigo", "Multiple Sclerosis",
    # Dermatological
    "Psoriasis", "Eczema", "Fungal Infection", "Acne",
    "Urticaria", "Cellulitis", "Impetigo",
    # Urological & Reproductive
    "Urinary Tract Infection", "Kidney Stones", "Prostatitis",
    "Polycystic Ovary Syndrome",
    # Musculoskeletal
    "Rheumatoid Arthritis", "Osteoarthritis", "Gout",
    "Cervical Spondylosis", "Fibromyalgia",
    # Other
    "AIDS", "Drug Reaction", "Allergy", "Anxiety Disorder", "Depression",
]

# ── 2. Symptom master list (180 symptoms) ────────────────────────────────────

SYMPTOMS = [
    # Systemic / Fever
    "high_fever", "mild_fever", "low_grade_fever", "chills", "rigors",
    "night_sweats", "sweating", "fatigue", "malaise", "lethargy",
    "weakness", "weight_loss", "weight_gain", "loss_of_appetite",
    "increased_appetite", "excessive_thirst", "dehydration",
    # Pain
    "headache", "severe_headache", "chest_pain", "abdominal_pain",
    "stomach_pain", "back_pain", "neck_pain", "joint_pain", "muscle_pain",
    "bone_pain", "knee_pain", "hip_joint_pain", "throat_pain",
    "pain_behind_eyes", "ear_pain", "pelvic_pain",
    # Respiratory
    "cough", "dry_cough", "productive_cough", "breathlessness",
    "wheezing", "chest_tightness", "rapid_breathing", "noisy_breathing",
    "runny_nose", "nasal_congestion", "sneezing", "sore_throat",
    "hoarseness", "blood_in_sputum", "phlegm", "mucoid_sputum",
    # Gastrointestinal
    "nausea", "vomiting", "diarrhoea", "bloody_diarrhoea", "constipation",
    "bloating", "indigestion", "acidity", "heartburn", "regurgitation",
    "difficulty_swallowing", "loss_of_smell", "loss_of_taste",
    "stomach_bleeding", "black_tarry_stool", "bloody_stool",
    "mucus_in_stool", "abdominal_distension", "passage_of_gases",
    "jaundice", "yellowish_skin", "yellowing_of_eyes", "dark_urine",
    "pale_stool",
    # Cardiovascular
    "palpitations", "fast_heart_rate", "irregular_heartbeat",
    "chest_pressure", "ankle_swelling", "leg_swelling",
    "swollen_blood_vessels", "prominent_veins_on_calf", "cold_extremities",
    # Neurological
    "dizziness", "vertigo", "loss_of_balance", "fainting", "seizures",
    "confusion", "altered_consciousness", "memory_loss", "slurred_speech",
    "facial_drooping", "limb_weakness", "numbness", "tingling",
    "visual_disturbances", "double_vision", "blurred_vision",
    "sensitivity_to_light", "sensitivity_to_sound", "stiff_neck",
    "neck_rigidity",
    # Urinary
    "burning_urination", "frequent_urination", "painful_urination",
    "blood_in_urine", "cloudy_urine", "dark_urine_colour",
    "reduced_urine_output", "polyuria", "incontinence",
    # Skin
    "skin_rash", "itching", "hives", "blisters", "skin_peeling",
    "redness", "swelling", "nodules", "pustules", "dry_skin",
    "oily_skin", "hair_loss", "nail_changes", "bruising",
    "bleeding_tendency", "petechiae",
    # Eyes / ENT
    "red_eyes", "watery_eyes", "eye_discharge", "ear_discharge",
    "hearing_loss", "ringing_in_ears", "nasal_polyps", "mouth_ulcers",
    "swollen_lymph_nodes", "enlarged_tonsils",
    # Endocrine / Metabolic
    "excessive_hunger", "irregular_periods", "missed_period",
    "hot_flushes", "cold_intolerance", "heat_intolerance",
    "tremors", "enlarged_thyroid", "puffiness",
    # Psychological
    "anxiety", "depression_symptoms", "irritability", "mood_swings",
    "sleep_disturbance", "restlessness", "poor_concentration",
    # Other
    "muscle_cramps", "muscle_stiffness", "joint_stiffness",
    "reduced_mobility", "difficulty_walking", "falls",
]

SYMPTOM_INDEX = {sym: idx for idx, sym in enumerate(SYMPTOMS)}
N_SYMPTOMS = len(SYMPTOMS)

# ── 3. Disease-symptom profiles ───────────────────────────────────────────────
# Format: {disease: {"core": [...], "common": [...], "occasional": [...]}}
# core      = almost always present (prob 0.85-0.99)
# common    = frequently present   (prob 0.50-0.85)
# occasional= sometimes present    (prob 0.20-0.50)

DISEASE_PROFILES: dict[str, dict] = {
    "Malaria": {
        "core":       ["high_fever", "chills", "rigors", "sweating"],
        "common":     ["headache", "malaise", "muscle_pain", "nausea", "vomiting", "fatigue"],
        "occasional": ["abdominal_pain", "diarrhoea", "jaundice", "loss_of_appetite"],
    },
    "Dengue": {
        "core":       ["high_fever", "severe_headache", "pain_behind_eyes", "joint_pain", "muscle_pain"],
        "common":     ["skin_rash", "nausea", "vomiting", "fatigue", "petechiae"],
        "occasional": ["bleeding_tendency", "bruising", "abdominal_pain", "sweating"],
    },
    "Typhoid": {
        "core":       ["high_fever", "headache", "malaise", "loss_of_appetite"],
        "common":     ["abdominal_pain", "constipation", "diarrhoea", "nausea", "fatigue"],
        "occasional": ["skin_rash", "cough", "vomiting", "confusion", "sweating"],
    },
    "Tuberculosis": {
        "core":       ["productive_cough", "night_sweats", "weight_loss", "fatigue"],
        "common":     ["mild_fever", "blood_in_sputum", "chest_pain", "loss_of_appetite"],
        "occasional": ["breathlessness", "malaise", "swollen_lymph_nodes", "hoarseness"],
    },
    "Pneumonia": {
        "core":       ["productive_cough", "high_fever", "breathlessness", "chest_pain"],
        "common":     ["chills", "fatigue", "rapid_breathing", "phlegm", "rigors"],
        "occasional": ["nausea", "vomiting", "confusion", "cyanosis", "sweating"],
    },
    "Influenza": {
        "core":       ["high_fever", "chills", "muscle_pain", "headache", "fatigue"],
        "common":     ["dry_cough", "sore_throat", "runny_nose", "malaise"],
        "occasional": ["vomiting", "diarrhoea", "loss_of_appetite", "sweating"],
    },
    "COVID-19": {
        "core":       ["high_fever", "dry_cough", "fatigue", "loss_of_taste", "loss_of_smell"],
        "common":     ["headache", "breathlessness", "muscle_pain", "sore_throat"],
        "occasional": ["diarrhoea", "nausea", "skin_rash", "chest_tightness", "confusion"],
    },
    "Meningitis": {
        "core":       ["severe_headache", "neck_rigidity", "high_fever", "sensitivity_to_light"],
        "common":     ["vomiting", "confusion", "altered_consciousness", "sensitivity_to_sound"],
        "occasional": ["seizures", "skin_rash", "petechiae", "facial_drooping"],
    },
    "Chickenpox": {
        "core":       ["skin_rash", "blisters", "itching", "mild_fever"],
        "common":     ["malaise", "fatigue", "loss_of_appetite", "headache"],
        "occasional": ["sore_throat", "dry_cough", "abdominal_pain"],
    },
    "Measles": {
        "core":       ["high_fever", "skin_rash", "red_eyes", "runny_nose"],
        "common":     ["cough", "malaise", "sensitivity_to_light", "mouth_ulcers"],
        "occasional": ["swollen_lymph_nodes", "loss_of_appetite", "diarrhoea"],
    },
    "Cholera": {
        "core":       ["watery_diarrhoea", "vomiting", "dehydration"],
        "common":     ["muscle_cramps", "weakness", "rapid_breathing", "sunken_eyes"],
        "occasional": ["low_grade_fever", "restlessness", "reduced_urine_output"],
    },
    "Chikungunya": {
        "core":       ["high_fever", "severe_joint_pain", "joint_stiffness", "skin_rash"],
        "common":     ["muscle_pain", "headache", "fatigue", "red_eyes"],
        "occasional": ["nausea", "vomiting", "mouth_ulcers", "swollen_lymph_nodes"],
    },
    "GERD": {
        "core":       ["heartburn", "regurgitation", "acidity"],
        "common":     ["chest_pain", "difficulty_swallowing", "indigestion", "bloating"],
        "occasional": ["dry_cough", "hoarseness", "nausea", "stomach_pain"],
    },
    "Peptic Ulcer Disease": {
        "core":       ["stomach_pain", "heartburn", "nausea", "indigestion"],
        "common":     ["loss_of_appetite", "bloating", "acidity", "vomiting"],
        "occasional": ["black_tarry_stool", "bloody_stool", "weight_loss", "fatigue"],
    },
    "Gastroenteritis": {
        "core":       ["diarrhoea", "vomiting", "nausea", "abdominal_pain"],
        "common":     ["mild_fever", "dehydration", "fatigue", "loss_of_appetite"],
        "occasional": ["chills", "muscle_pain", "headache", "bloating"],
    },
    "Appendicitis": {
        "core":       ["abdominal_pain", "nausea", "vomiting", "loss_of_appetite"],
        "common":     ["high_fever", "abdominal_distension", "constipation"],
        "occasional": ["diarrhoea", "bloating", "passage_of_gases", "rigors"],
    },
    "Irritable Bowel Syndrome": {
        "core":       ["abdominal_pain", "bloating", "constipation", "diarrhoea"],
        "common":     ["passage_of_gases", "mucus_in_stool", "indigestion"],
        "occasional": ["fatigue", "nausea", "anxiety", "depression_symptoms"],
    },
    "Hepatitis A": {
        "core":       ["jaundice", "yellowish_skin", "yellowing_of_eyes", "fatigue"],
        "common":     ["loss_of_appetite", "nausea", "abdominal_pain", "dark_urine"],
        "occasional": ["mild_fever", "vomiting", "joint_pain", "pale_stool"],
    },
    "Hepatitis B": {
        "core":       ["jaundice", "fatigue", "abdominal_pain", "dark_urine"],
        "common":     ["loss_of_appetite", "nausea", "vomiting", "joint_pain"],
        "occasional": ["skin_rash", "mild_fever", "pale_stool", "yellowing_of_eyes"],
    },
    "Hepatitis C": {
        "core":       ["fatigue", "jaundice", "abdominal_pain"],
        "common":     ["nausea", "loss_of_appetite", "dark_urine", "joint_pain"],
        "occasional": ["skin_rash", "itching", "depression_symptoms", "confusion"],
    },
    "Liver Cirrhosis": {
        "core":       ["jaundice", "abdominal_distension", "fatigue", "weight_loss"],
        "common":     ["loss_of_appetite", "nausea", "itching", "swollen_lymph_nodes"],
        "occasional": ["confusion", "bleeding_tendency", "muscle_cramps", "ankle_swelling"],
    },
    "Type 2 Diabetes": {
        "core":       ["excessive_thirst", "polyuria", "fatigue", "blurred_vision"],
        "common":     ["weight_loss", "increased_appetite", "slow_healing", "tingling"],
        "occasional": ["numbness", "frequent_urination", "skin_rash", "mood_swings"],
    },
    "Type 1 Diabetes": {
        "core":       ["excessive_thirst", "polyuria", "weight_loss", "fatigue"],
        "common":     ["blurred_vision", "increased_appetite", "nausea", "vomiting"],
        "occasional": ["abdominal_pain", "confusion", "fruity_breath", "rapid_breathing"],
    },
    "Hypoglycemia": {
        "core":       ["sweating", "tremors", "palpitations", "anxiety"],
        "common":     ["dizziness", "confusion", "headache", "weakness"],
        "occasional": ["fainting", "seizures", "altered_consciousness", "irritability"],
    },
    "Hypertension": {
        "core":       ["headache", "dizziness", "palpitations"],
        "common":     ["chest_pain", "blurred_vision", "fatigue", "nausea"],
        "occasional": ["breathlessness", "nosebleed", "anxiety", "chest_tightness"],
    },
    "Hypothyroidism": {
        "core":       ["fatigue", "weight_gain", "cold_intolerance", "dry_skin"],
        "common":     ["constipation", "depression_symptoms", "muscle_pain", "puffiness"],
        "occasional": ["hair_loss", "nail_changes", "memory_loss", "enlarged_thyroid"],
    },
    "Hyperthyroidism": {
        "core":       ["weight_loss", "heat_intolerance", "palpitations", "tremors"],
        "common":     ["increased_appetite", "sweating", "anxiety", "fast_heart_rate"],
        "occasional": ["diarrhoea", "fatigue", "red_eyes", "enlarged_thyroid"],
    },
    "Anaemia": {
        "core":       ["fatigue", "weakness", "pallor", "breathlessness"],
        "common":     ["dizziness", "headache", "cold_extremities", "palpitations"],
        "occasional": ["chest_pain", "hair_loss", "nail_changes", "loss_of_appetite"],
    },
    "Heart Attack": {
        "core":       ["chest_pain", "chest_pressure", "breathlessness", "sweating"],
        "common":     ["palpitations", "nausea", "vomiting", "pain_behind_eyes"],
        "occasional": ["jaw_pain", "arm_pain", "back_pain", "dizziness", "fainting"],
    },
    "Heart Failure": {
        "core":       ["breathlessness", "ankle_swelling", "fatigue", "leg_swelling"],
        "common":     ["fast_heart_rate", "chest_tightness", "reduced_mobility", "cough"],
        "occasional": ["weight_gain", "loss_of_appetite", "confusion", "palpitations"],
    },
    "Angina": {
        "core":       ["chest_pain", "chest_pressure", "breathlessness"],
        "common":     ["fatigue", "dizziness", "palpitations", "sweating"],
        "occasional": ["nausea", "back_pain", "jaw_pain", "cold_extremities"],
    },
    "Bronchial Asthma": {
        "core":       ["wheezing", "breathlessness", "chest_tightness", "dry_cough"],
        "common":     ["cough", "rapid_breathing", "fatigue", "noisy_breathing"],
        "occasional": ["sleep_disturbance", "anxiety", "phlegm", "sweating"],
    },
    "COPD": {
        "core":       ["productive_cough", "breathlessness", "wheezing", "chest_tightness"],
        "common":     ["fatigue", "phlegm", "cyanosis", "reduced_mobility"],
        "occasional": ["weight_loss", "ankle_swelling", "confusion", "rapid_breathing"],
    },
    "Common Cold": {
        "core":       ["runny_nose", "nasal_congestion", "sneezing", "sore_throat"],
        "common":     ["mild_fever", "cough", "headache", "malaise"],
        "occasional": ["watery_eyes", "fatigue", "muscle_pain", "ear_pain"],
    },
    "Sinusitis": {
        "core":       ["nasal_congestion", "facial_pain", "headache", "runny_nose"],
        "common":     ["sore_throat", "cough", "loss_of_smell", "mild_fever"],
        "occasional": ["fatigue", "ear_pain", "toothache", "bad_breath"],
    },
    "Migraine": {
        "core":       ["severe_headache", "nausea", "sensitivity_to_light", "sensitivity_to_sound"],
        "common":     ["vomiting", "visual_disturbances", "dizziness", "fatigue"],
        "occasional": ["neck_pain", "confusion", "numbness", "tingling"],
    },
    "Tension Headache": {
        "core":       ["headache", "neck_pain", "neck_rigidity"],
        "common":     ["fatigue", "sleep_disturbance", "irritability", "poor_concentration"],
        "occasional": ["sensitivity_to_light", "nausea", "dizziness", "muscle_stiffness"],
    },
    "Stroke": {
        "core":       ["facial_drooping", "limb_weakness", "slurred_speech", "confusion"],
        "common":     ["severe_headache", "loss_of_balance", "visual_disturbances", "altered_consciousness"],
        "occasional": ["seizures", "vomiting", "numbness", "double_vision"],
    },
    "Vertigo": {
        "core":       ["dizziness", "vertigo", "loss_of_balance", "nausea"],
        "common":     ["vomiting", "ear_pain", "ringing_in_ears", "hearing_loss"],
        "occasional": ["sweating", "palpitations", "headache", "difficulty_walking"],
    },
    "Epilepsy": {
        "core":       ["seizures", "altered_consciousness", "confusion"],
        "common":     ["fatigue", "memory_loss", "anxiety", "depression_symptoms"],
        "occasional": ["headache", "numbness", "tingling", "visual_disturbances"],
    },
    "Psoriasis": {
        "core":       ["skin_rash", "itching", "skin_peeling", "dry_skin"],
        "common":     ["redness", "joint_pain", "nail_changes", "blisters"],
        "occasional": ["joint_stiffness", "fatigue", "depression_symptoms", "swollen_lymph_nodes"],
    },
    "Eczema": {
        "core":       ["itching", "skin_rash", "dry_skin", "redness"],
        "common":     ["blisters", "skin_peeling", "sleep_disturbance", "swelling"],
        "occasional": ["skin_infection", "anxiety", "depression_symptoms", "fatigue"],
    },
    "Fungal Infection": {
        "core":       ["itching", "skin_rash", "redness", "skin_peeling"],
        "common":     ["blisters", "burning_sensation", "dry_skin", "nodules"],
        "occasional": ["nail_changes", "hair_loss", "swollen_lymph_nodes"],
    },
    "Urticaria": {
        "core":       ["hives", "itching", "skin_rash", "redness"],
        "common":     ["swelling", "burning_sensation", "anxiety", "breathlessness"],
        "occasional": ["abdominal_pain", "vomiting", "dizziness", "palpitations"],
    },
    "Urinary Tract Infection": {
        "core":       ["burning_urination", "frequent_urination", "painful_urination"],
        "common":     ["cloudy_urine", "blood_in_urine", "pelvic_pain", "mild_fever"],
        "occasional": ["back_pain", "nausea", "fatigue", "incontinence"],
    },
    "Kidney Stones": {
        "core":       ["severe_back_pain", "abdominal_pain", "blood_in_urine"],
        "common":     ["nausea", "vomiting", "painful_urination", "frequent_urination"],
        "occasional": ["high_fever", "chills", "cloudy_urine", "reduced_urine_output"],
    },
    "Rheumatoid Arthritis": {
        "core":       ["joint_pain", "joint_stiffness", "swelling", "reduced_mobility"],
        "common":     ["fatigue", "mild_fever", "weight_loss", "muscle_weakness"],
        "occasional": ["skin_rash", "dry_eyes", "chest_pain", "breathlessness"],
    },
    "Osteoarthritis": {
        "core":       ["joint_pain", "joint_stiffness", "reduced_mobility"],
        "common":     ["swelling", "muscle_weakness", "difficulty_walking", "knee_pain"],
        "occasional": ["bone_pain", "hip_joint_pain", "falls", "depression_symptoms"],
    },
    "Gout": {
        "core":       ["severe_joint_pain", "swelling", "redness", "joint_stiffness"],
        "common":     ["high_fever", "fatigue", "skin_peeling", "itching"],
        "occasional": ["kidney_stones", "reduced_mobility", "difficulty_walking"],
    },
    "Fibromyalgia": {
        "core":       ["muscle_pain", "fatigue", "sleep_disturbance", "poor_concentration"],
        "common":     ["joint_pain", "headache", "depression_symptoms", "anxiety"],
        "occasional": ["tingling", "numbness", "irritability", "bloating"],
    },
    "AIDS": {
        "core":       ["fatigue", "weight_loss", "night_sweats", "swollen_lymph_nodes"],
        "common":     ["high_fever", "diarrhoea", "cough", "skin_rash"],
        "occasional": ["mouth_ulcers", "visual_disturbances", "confusion", "headache"],
    },
    "Drug Reaction": {
        "core":       ["skin_rash", "itching", "hives", "redness"],
        "common":     ["nausea", "vomiting", "diarrhoea", "swelling"],
        "occasional": ["breathlessness", "palpitations", "fever", "joint_pain"],
    },
    "Allergy": {
        "core":       ["sneezing", "runny_nose", "itching", "watery_eyes"],
        "common":     ["skin_rash", "hives", "nasal_congestion", "red_eyes"],
        "occasional": ["breathlessness", "wheezing", "swelling", "fatigue"],
    },
    "Anxiety Disorder": {
        "core":       ["anxiety", "palpitations", "restlessness", "sleep_disturbance"],
        "common":     ["sweating", "tremors", "poor_concentration", "irritability"],
        "occasional": ["chest_tightness", "dizziness", "nausea", "fatigue"],
    },
    "Depression": {
        "core":       ["depression_symptoms", "fatigue", "sleep_disturbance", "poor_concentration"],
        "common":     ["loss_of_appetite", "weight_loss", "irritability", "mood_swings"],
        "occasional": ["headache", "back_pain", "muscle_pain", "anxiety"],
    },
    "Polycystic Ovary Syndrome": {
        "core":       ["irregular_periods", "weight_gain", "acne", "hair_loss"],
        "common":     ["excessive_hunger", "fatigue", "pelvic_pain", "mood_swings"],
        "occasional": ["depression_symptoms", "anxiety", "sleep_disturbance", "hot_flushes"],
    },
    "Pancreatitis": {
        "core":       ["severe_abdominal_pain", "nausea", "vomiting", "high_fever"],
        "common":     ["abdominal_distension", "loss_of_appetite", "jaundice", "chills"],
        "occasional": ["diarrhoea", "bloating", "back_pain", "weight_loss"],
    },
    "Leptospirosis": {
        "core":       ["high_fever", "severe_headache", "muscle_pain", "red_eyes"],
        "common":     ["chills", "vomiting", "abdominal_pain", "jaundice"],
        "occasional": ["skin_rash", "cough", "breathlessness", "confusion"],
    },
    "Herpes Zoster": {
        "core":       ["skin_rash", "blisters", "burning_sensation", "pain"],
        "common":     ["itching", "mild_fever", "fatigue", "sensitivity_to_light"],
        "occasional": ["headache", "muscle_pain", "swollen_lymph_nodes"],
    },
    "Cervical Spondylosis": {
        "core":       ["neck_pain", "neck_rigidity", "headache", "muscle_stiffness"],
        "common":     ["tingling", "numbness", "weakness", "reduced_mobility"],
        "occasional": ["dizziness", "vertigo", "back_pain", "difficulty_walking"],
    },
    "Vitamin D Deficiency": {
        "core":       ["bone_pain", "fatigue", "muscle_weakness", "depression_symptoms"],
        "common":     ["back_pain", "hair_loss", "poor_concentration", "mood_swings"],
        "occasional": ["muscle_cramps", "joint_pain", "sleep_disturbance", "anxiety"],
    },
    "Iron Deficiency": {
        "core":       ["fatigue", "weakness", "pallor", "breathlessness"],
        "common":     ["dizziness", "cold_extremities", "headache", "hair_loss"],
        "occasional": ["nail_changes", "mouth_ulcers", "restlessness", "palpitations"],
    },
    "Septicemia": {
        "core":       ["high_fever", "rigors", "confusion", "rapid_breathing"],
        "common":     ["fast_heart_rate", "low_blood_pressure", "altered_consciousness"],
        "occasional": ["skin_rash", "petechiae", "reduced_urine_output", "jaundice"],
    },
    "Deep Vein Thrombosis": {
        "core":       ["leg_swelling", "leg_pain", "redness", "warmth"],
        "common":     ["prominent_veins_on_calf", "difficulty_walking", "fatigue"],
        "occasional": ["breathlessness", "chest_pain", "palpitations"],
    },
    "Pulmonary Embolism": {
        "core":       ["breathlessness", "chest_pain", "palpitations", "rapid_breathing"],
        "common":     ["fainting", "sweating", "cough", "blood_in_sputum"],
        "occasional": ["leg_swelling", "anxiety", "confusion", "cyanosis"],
    },
    "Alcoholic Hepatitis": {
        "core":       ["jaundice", "abdominal_pain", "nausea", "vomiting"],
        "common":     ["fatigue", "loss_of_appetite", "weight_loss", "fever"],
        "occasional": ["confusion", "bleeding_tendency", "abdominal_distension"],
    },
    "Acne": {
        "core":       ["pustules", "nodules", "oily_skin", "redness"],
        "common":     ["skin_rash", "itching", "blackheads", "dry_skin"],
        "occasional": ["depression_symptoms", "anxiety", "poor_concentration"],
    },
    "Cellulitis": {
        "core":       ["redness", "swelling", "skin_warmth", "pain"],
        "common":     ["high_fever", "chills", "fatigue", "swollen_lymph_nodes"],
        "occasional": ["blisters", "skin_peeling", "rigors", "malaise"],
    },
    "Impetigo": {
        "core":       ["skin_rash", "blisters", "skin_peeling", "redness"],
        "common":     ["itching", "mild_fever", "swollen_lymph_nodes", "crusting"],
        "occasional": ["fatigue", "loss_of_appetite", "pain"],
    },
    "Prostatitis": {
        "core":       ["pelvic_pain", "painful_urination", "frequent_urination"],
        "common":     ["back_pain", "high_fever", "chills", "fatigue"],
        "occasional": ["nausea", "muscle_pain", "blood_in_urine", "reduced_urine_output"],
    },
    "Chronic Cholestasis": {
        "core":       ["jaundice", "itching", "dark_urine", "pale_stool"],
        "common":     ["fatigue", "abdominal_pain", "loss_of_appetite", "nausea"],
        "occasional": ["weight_loss", "xanthomas", "bone_pain", "vitamin_deficiency"],
    },
    "Parkinson's Disease": {
        "core":       ["tremors", "muscle_stiffness", "reduced_mobility", "balance_problems"],
        "common":     ["slurred_speech", "difficulty_walking", "fatigue", "depression_symptoms"],
        "occasional": ["sleep_disturbance", "constipation", "memory_loss", "anxiety"],
    },
    "Multiple Sclerosis": {
        "core":       ["limb_weakness", "tingling", "numbness", "visual_disturbances"],
        "common":     ["fatigue", "balance_problems", "slurred_speech", "reduced_mobility"],
        "occasional": ["depression_symptoms", "memory_loss", "bladder_issues", "seizures"],
    },
}


# ── 4. Dataset generation ─────────────────────────────────────────────────────

def generate_patient(disease: str, profile: dict) -> dict:
    """
    Generates a single realistic patient record with noise.
    Each patient is unique — symptoms are sampled probabilistically.
    """
    row = {sym: 0 for sym in SYMPTOMS}
    row["prognosis"] = disease

    core       = profile.get("core", [])
    common     = profile.get("common", [])
    occasional = profile.get("occasional", [])

    # Core symptoms — almost always present
    for sym in core:
        if sym in SYMPTOM_INDEX:
            row[sym] = 1 if random.random() < 0.92 else 0

    # Common symptoms — frequently present
    for sym in common:
        if sym in SYMPTOM_INDEX:
            row[sym] = 1 if random.random() < 0.65 else 0

    # Occasional symptoms — sometimes present
    for sym in occasional:
        if sym in SYMPTOM_INDEX:
            row[sym] = 1 if random.random() < 0.30 else 0

    # Add 1-3 random noise symptoms (realistic comorbidity simulation)
    noise_count = random.randint(0, 2)
    noise_syms  = random.sample(SYMPTOMS, noise_count)
    for sym in noise_syms:
        row[sym] = 1

    return row


def build_dataset(
    samples_per_disease: int = 200,
    test_ratio: float = 0.15,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    print(f"Building dataset: {len(DISEASE_PROFILES)} diseases × {samples_per_disease} samples")

    all_rows = []
    for disease, profile in DISEASE_PROFILES.items():
        for _ in range(samples_per_disease):
            all_rows.append(generate_patient(disease, profile))

    df = pd.DataFrame(all_rows)

    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Split
    test_size  = int(len(df) * test_ratio)
    test_df    = df.iloc[:test_size]
    train_df   = df.iloc[test_size:]

    print(f"Train: {len(train_df)} rows | Test: {len(test_df)} rows")
    print(f"Symptoms: {len(SYMPTOMS)} | Diseases: {len(DISEASE_PROFILES)}")

    return train_df, test_df


if __name__ == "__main__":
    Path("dataset").mkdir(exist_ok=True)

    train_df, test_df = build_dataset(samples_per_disease=200)

    train_df.to_csv("dataset/Training.csv", index=False)
    test_df.to_csv("dataset/Testing.csv", index=False)

    # Save symptom list for frontend
    Path("models").mkdir(exist_ok=True)
    with open("models/symptom_index.json", "w") as f:
        json.dump(SYMPTOM_INDEX, f, indent=2)

    print("Saved dataset/Training.csv and dataset/Testing.csv")
    print("Saved models/symptom_index.json")

    # Quick stats
    print("\nDisease distribution (train):")
    print(train_df["prognosis"].value_counts().to_string())