import pandas as pd
import json
import random

# -------- LOAD FILES --------
symptom_df = pd.read_csv("dataset.csv")
desc_df = pd.read_csv("symptom_Description.csv")
prec_df = pd.read_csv("symptom_precaution.csv")

# Build disease -> description map
disease_desc = dict(zip(desc_df["Disease"], desc_df["Description"]))

dataset = []

for _, row in symptom_df.iterrows():

    disease = row["Disease"]

    # Collect non-null symptoms
    symptoms = []
    for col in symptom_df.columns[1:]:
        if pd.notna(row[col]):
            symptoms.append(row[col])

    if len(symptoms) == 0:
        continue

    symptom_text = ", ".join(symptoms)

    description = disease_desc.get(disease, "")

    prompt = f"<s>[INST] Symptoms: {symptom_text} [/INST] "

    output = {
        "diseases": [disease],
        "primary_disease": disease,
        "confidence": "Medium",
        "explanation": description[:120]
    }

    dataset.append({
        "text": prompt + json.dumps(output)
    })

# Shuffle
random.shuffle(dataset)

with open("final_dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)

print("Dataset built successfully.")
print("Total samples:", len(dataset))