import torch
import json
from transformers import AutoTokenizer, AutoModelForCausalLM
from config import MODEL_PATH, MAX_TOKENS, TEMPERATURE, TOP_P

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH).to(device)

def build_prompt(symptoms):

    return f"""
You are an autonomous rural healthcare triage assistant.

Your job:
1. Identify possible diseases from symptoms.
2. Select the primary disease.
3. Assign confidence level: Low, Medium, or High.
4. Recommend the most appropriate medical specialist.

Respond ONLY in valid JSON format:

{{
  "diseases": [],
  "primary_disease": "",
  "confidence": "Low/Medium/High",
  "recommended_specialist": ""
}}

Examples:

Symptoms: headache, nausea, blurred vision

{{
  "diseases": ["Migraine"],
  "primary_disease": "Migraine",
  "confidence": "Medium",
  "recommended_specialist": "Neurologist"
}}

Symptoms: frequent urination, excessive thirst, weight loss

{{
  "diseases": ["Diabetes"],
  "primary_disease": "Diabetes",
  "confidence": "High",
  "recommended_specialist": "Endocrinologist"
}}

Now analyze the following symptoms:

Symptoms: {symptoms}
"""

def diagnose(symptoms):

    prompt = build_prompt(symptoms)

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        top_p=TOP_P
    )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract JSON safely
    start = decoded.find("{")
    end = decoded.rfind("}") + 1

    try:
        return json.loads(decoded[start:end])
    except:
        return {
            "diseases": [],
            "primary_disease": "Unknown",
            "confidence": "Low",
            "recommended_specialist": "General Physician"
        }