VALID_SPECIALISTS = [
    "Neurologist",
    "Cardiologist",
    "Endocrinologist",
    "Infectious Disease Specialist",
    "General Physician"
]

def validate_specialist(prediction):

    specialist = prediction.get("recommended_specialist", "")

    if specialist not in VALID_SPECIALISTS:
        prediction["recommended_specialist"] = "General Physician"

    return prediction