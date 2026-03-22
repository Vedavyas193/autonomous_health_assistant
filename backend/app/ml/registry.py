DISEASE_REGISTRY = {

    # ---------------- CARDIOVASCULAR ----------------
    "heart_disease": {
        "category": "cardiovascular",
        "features": ["age", "heart_rate", "oxygen", "glucose"],
        "specialist": "Cardiologist",
        "risk_weight": 1.6,
        "emergency_threshold": 0.75
    },
    "hypertension": {
        "category": "cardiovascular",
        "features": ["age", "heart_rate"],
        "specialist": "Cardiologist",
        "risk_weight": 1.3,
        "emergency_threshold": 0.85
    },
    "stroke_risk": {
        "category": "cardiovascular",
        "features": ["age", "heart_rate"],
        "specialist": "Neurologist",
        "risk_weight": 1.8,
        "emergency_threshold": 0.70
    },

    # ---------------- METABOLIC ----------------
    "diabetes_type2": {
        "category": "metabolic",
        "features": ["age", "glucose"],
        "specialist": "Endocrinologist",
        "risk_weight": 1.4,
        "emergency_threshold": 0.80
    },
    "obesity_related_risk": {
        "category": "metabolic",
        "features": ["age", "glucose"],
        "specialist": "General Physician",
        "risk_weight": 1.2,
        "emergency_threshold": 0.85
    },

    # ---------------- RESPIRATORY ----------------
    "asthma": {
        "category": "respiratory",
        "features": ["age", "oxygen"],
        "specialist": "Pulmonologist",
        "risk_weight": 1.3,
        "emergency_threshold": 0.75
    },
    "pneumonia": {
        "category": "respiratory",
        "features": ["age", "oxygen"],
        "specialist": "Pulmonologist",
        "risk_weight": 1.5,
        "emergency_threshold": 0.70
    },
    "copd": {
        "category": "respiratory",
        "features": ["age", "oxygen"],
        "specialist": "Pulmonologist",
        "risk_weight": 1.4,
        "emergency_threshold": 0.72
    },

    # ---------------- INFECTIOUS ----------------
    "malaria": {
        "category": "infectious",
        "features": ["age"],
        "specialist": "Infectious Disease Specialist",
        "risk_weight": 1.6,
        "emergency_threshold": 0.70
    },
    "dengue": {
        "category": "infectious",
        "features": ["age"],
        "specialist": "Infectious Disease Specialist",
        "risk_weight": 1.7,
        "emergency_threshold": 0.65
    },
    "tuberculosis": {
        "category": "infectious",
        "features": ["age", "oxygen"],
        "specialist": "Pulmonologist",
        "risk_weight": 1.8,
        "emergency_threshold": 0.68
    },

    # ---------------- NUTRITIONAL ----------------
    "anemia": {
        "category": "nutritional",
        "features": ["age"],
        "specialist": "General Physician",
        "risk_weight": 1.2,
        "emergency_threshold": 0.90
    },

    # ---------------- GASTRO ----------------
    "gastritis": {
        "category": "gastrointestinal",
        "features": ["age"],
        "specialist": "General Physician",
        "risk_weight": 1.1,
        "emergency_threshold": 0.95
    },
    "dehydration": {
        "category": "gastrointestinal",
        "features": ["age"],
        "specialist": "General Physician",
        "risk_weight": 1.3,
        "emergency_threshold": 0.80
    },

    # ---------------- NEUROLOGICAL ----------------
    "migraine": {
        "category": "neurological",
        "features": ["age"],
        "specialist": "Neurologist",
        "risk_weight": 1.1,
        "emergency_threshold": 0.95
    },
    "epilepsy_risk": {
        "category": "neurological",
        "features": ["age"],
        "specialist": "Neurologist",
        "risk_weight": 1.6,
        "emergency_threshold": 0.60
    },

    # ---------------- GENERAL ACUTE ----------------
    "fever_unknown_origin": {
        "category": "general",
        "features": ["age"],
        "specialist": "General Physician",
        "risk_weight": 1.0,
        "emergency_threshold": 0.95
    }
}