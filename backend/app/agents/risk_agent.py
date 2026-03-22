# Create a new file: risk_agent.py
import pandas as pd

class RiskAssessmentAgent:
    def __init__(self, severity_csv_path="Symptom-severity.csv"):
        # Load the severity dataset dynamically
        try:
            df = pd.read_csv(severity_csv_path)
            # Clean column names (e.g., replace spaces with underscores to match input)
            df['Symptom'] = df['Symptom'].str.replace(' ', '_').str.lower()
            # Create a dictionary of {symptom: weight}
            self.severity_map = dict(zip(df['Symptom'], df['weight']))
        except Exception as e:
            print(f"Warning: Could not load {severity_csv_path}. Using default weights.")
            self.severity_map = {}

    def calculate_risk(self, symptoms):
        """Calculates risk based on the dataset's severity weights."""
        total_severity = 0
        max_single_severity = 0
        
        for sym in symptoms:
            clean_sym = sym.replace(' ', '_').lower()
            weight = self.severity_map.get(clean_sym, 1) # Default to 1 if unknown
            total_severity += weight
            if weight > max_single_severity:
                max_single_severity = weight
                
        # Define dynamic thresholds based on the dataset's scale
        # (Assuming typical Kaggle dataset weights range from 1 to 7)
        if max_single_severity >= 6 or total_severity > 15:
            return "CRITICAL EMERGENCY"
        elif max_single_severity >= 4 or total_severity > 10:
            return "MODERATE RISK"
        else:
            return "ROUTINE EVALUATION"

# Example usage inside your orchestrator:
# risk_agent = RiskAssessmentAgent()
# risk = risk_agent.calculate_risk(patient.symptoms)