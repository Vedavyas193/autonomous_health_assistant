import pandas as pd
import xgboost as xgb
import json
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder

def train_model():
    print("Loading dataset.csv...")
    df = pd.read_csv('dataset.csv')
    
    # Clean column names just in case
    df.columns = df.columns.str.strip()
    
    # 1. Extract Target (The Disease)
    y = df['Disease'].str.strip()
    
    # 2. Extract Features (The Symptoms)
    print("Extracting and mapping unique symptoms...")
    symptom_cols = [col for col in df.columns if col.startswith('Symptom')]
    
    # Gather a master list of all unique symptoms across all columns
    all_symptoms = set()
    for col in symptom_cols:
        unique_vals = df[col].dropna().unique()
        for val in unique_vals:
            # Clean text: remove spaces, make lowercase, replace spaces with underscores
            cleaned_val = str(val).strip().replace(' ', '_').lower()
            if cleaned_val:  
                all_symptoms.add(cleaned_val)
                
    symptom_list = sorted(list(all_symptoms))
    print(f"Found {len(symptom_list)} unique symptoms. Building binary matrix...")
    
    # 3. Create Multi-Hot Binary Matrix (0s and 1s)
    X_matrix = np.zeros((len(df), len(symptom_list)), dtype=int)
    
    for index, row in df.iterrows():
        for col in symptom_cols:
            val = row[col]
            if pd.notna(val):
                cleaned_val = str(val).strip().replace(' ', '_').lower()
                if cleaned_val in symptom_list:
                    idx = symptom_list.index(cleaned_val)
                    X_matrix[index, idx] = 1  # Mark 1 if symptom is present
                    
    # Convert back to a DataFrame so XGBoost can read it easily
    X = pd.DataFrame(X_matrix, columns=symptom_list)
    
    # 4. Encode target labels (Disease names to numbers)
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print("Training XGBoost Classifier...")
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
    model.fit(X, y_encoded)
    
    # 5. Save everything to disk
    model.save_model("disease_classifier.json")
    joblib.dump(label_encoder, "label_encoder.pkl")
    
    # Save the symptom list so our API knows the exact input order!
    with open("symptom_columns.json", "w") as f:
        json.dump(symptom_list, f)
        
    print("Training complete! Model and encoders successfully saved.")

if __name__ == "__main__":
    train_model()