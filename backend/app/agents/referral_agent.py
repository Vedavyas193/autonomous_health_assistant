class ReferralAgent:
    def __init__(self):
        # Maps diseases from your dataset to standard medical specialists
        self.specialist_map = {
            "Fungal infection": "Dermatologist",
            "Heart attack": "Cardiologist",
            "Diabetes ": "Endocrinologist",
            "Malaria": "Infectious Disease Specialist",
            "Dengue": "Infectious Disease Specialist",
            "Typhoid": "General Physician",
            "Migraine": "Neurologist",
            "Cervical spondylosis": "Orthopedist",
            "Jaundice": "Gastroenterologist"
        }
    
    def get_specialist(self, disease, risk_level):
        """Returns the specialist, escalating if critical."""
        key = disease.strip() if isinstance(disease, str) else disease
        specialist = self.specialist_map.get(key, "General Physician")
        
        if risk_level == "CRITICAL EMERGENCY":
            return f"{specialist} / Emergency Room (Immediate)"
        return specialist