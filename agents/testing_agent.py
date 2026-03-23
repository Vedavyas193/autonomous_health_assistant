from __future__ import annotations
from dataclasses import dataclass


@dataclass
class TestRecommendation:
    test_name: str
    reason: str
    urgency: str   # IMMEDIATE | WITHIN_24H | WITHIN_WEEK | ROUTINE
    test_type: str # BLOOD | IMAGING | URINE | STOOL | SWAB | BIOPSY | ECG | OTHER


# Master map: disease → recommended diagnostic tests
DISEASE_TEST_MAP: dict[str, list[dict]] = {
    "Malaria": [
        {"test_name": "Malaria Rapid Diagnostic Test (RDT)", "reason": "Detects malaria antigens in blood", "urgency": "IMMEDIATE", "test_type": "BLOOD"},
        {"test_name": "Peripheral Blood Smear", "reason": "Identifies malaria parasite species and density", "urgency": "IMMEDIATE", "test_type": "BLOOD"},
        {"test_name": "Complete Blood Count (CBC)", "reason": "Checks for anaemia and thrombocytopenia common in malaria", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
    ],
    "Dengue": [
        {"test_name": "NS1 Antigen Test", "reason": "Detects dengue virus antigen in early infection", "urgency": "IMMEDIATE", "test_type": "BLOOD"},
        {"test_name": "Dengue IgM/IgG Serology", "reason": "Confirms dengue infection", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "Platelet Count", "reason": "Monitors platelet drop — key dengue complication indicator", "urgency": "IMMEDIATE", "test_type": "BLOOD"},
        {"test_name": "CBC with Differential", "reason": "Monitors leukopenia and haematocrit rise", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
    ],
    "Typhoid": [
        {"test_name": "Widal Test", "reason": "Detects antibodies against Salmonella typhi", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "Blood Culture", "reason": "Gold standard for typhoid — identifies Salmonella typhi", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "Stool Culture", "reason": "Detects Salmonella in stool during later stages", "urgency": "WITHIN_WEEK", "test_type": "STOOL"},
        {"test_name": "Urine Culture", "reason": "Identifies urinary shedding of Salmonella", "urgency": "WITHIN_WEEK", "test_type": "URINE"},
    ],
    "Tuberculosis": [
        {"test_name": "Sputum AFB Smear (× 3 samples)", "reason": "Detects acid-fast bacilli — frontline TB test", "urgency": "WITHIN_24H", "test_type": "SWAB"},
        {"test_name": "Chest X-Ray", "reason": "Identifies pulmonary infiltrates, cavities, lymphadenopathy", "urgency": "WITHIN_24H", "test_type": "IMAGING"},
        {"test_name": "Mantoux (TST) / IGRA Test", "reason": "Screens for TB infection (latent or active)", "urgency": "WITHIN_WEEK", "test_type": "OTHER"},
        {"test_name": "GeneXpert MTB/RIF", "reason": "Rapid molecular test — detects TB and rifampicin resistance", "urgency": "WITHIN_24H", "test_type": "SWAB"},
    ],
    "Pneumonia": [
        {"test_name": "Chest X-Ray", "reason": "Confirms consolidation or infiltrates in lung fields", "urgency": "IMMEDIATE", "test_type": "IMAGING"},
        {"test_name": "CBC with Differential", "reason": "Elevated WBC indicates bacterial infection", "urgency": "IMMEDIATE", "test_type": "BLOOD"},
        {"test_name": "Sputum Culture", "reason": "Identifies causative organism and antibiotic sensitivity", "urgency": "WITHIN_24H", "test_type": "SWAB"},
        {"test_name": "Blood Culture (× 2)", "reason": "Rules out bacteraemia", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "Pulse Oximetry", "reason": "Monitors oxygen saturation", "urgency": "IMMEDIATE", "test_type": "OTHER"},
    ],
    "Diabetes": [
        {"test_name": "Fasting Blood Glucose (FBG)", "reason": "Screens for hyperglycaemia", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "HbA1c", "reason": "Measures average blood glucose over 3 months", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "Oral Glucose Tolerance Test (OGTT)", "reason": "Confirms diabetes diagnosis", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "Urine Dipstick for Glucose/Ketones", "reason": "Quick bedside check for glycosuria and ketoacidosis", "urgency": "WITHIN_24H", "test_type": "URINE"},
    ],
    "Hepatitis A": [
        {"test_name": "Anti-HAV IgM Antibody", "reason": "Confirms acute Hepatitis A infection", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "Liver Function Tests (LFT)", "reason": "Measures ALT/AST elevation indicating liver damage", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "Bilirubin (Total/Direct)", "reason": "Assesses degree of jaundice", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
    ],
    "Hepatitis B": [
        {"test_name": "HBsAg (Hepatitis B Surface Antigen)", "reason": "Primary screening test for Hepatitis B", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "HBeAg and Anti-HBe", "reason": "Determines infectivity and disease phase", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "HBV DNA (PCR)", "reason": "Measures viral load", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "Liver Function Tests (LFT)", "reason": "Monitors liver damage", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "Abdominal Ultrasound", "reason": "Checks for liver enlargement or cirrhosis", "urgency": "WITHIN_WEEK", "test_type": "IMAGING"},
    ],
    "Hepatitis C": [
        {"test_name": "Anti-HCV Antibody", "reason": "Screening test for Hepatitis C exposure", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "HCV RNA (PCR)", "reason": "Confirms active HCV infection and viral load", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "Liver Function Tests (LFT)", "reason": "Monitors hepatic inflammation", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
    ],
    "Heart attack": [
        {"test_name": "12-Lead ECG", "reason": "Identifies ST elevation, Q waves, arrhythmias", "urgency": "IMMEDIATE", "test_type": "ECG"},
        {"test_name": "Troponin I / Troponin T", "reason": "Cardiac biomarker — elevated within 3-6h of MI", "urgency": "IMMEDIATE", "test_type": "BLOOD"},
        {"test_name": "CK-MB (Creatine Kinase-MB)", "reason": "Myocardial damage marker", "urgency": "IMMEDIATE", "test_type": "BLOOD"},
        {"test_name": "Chest X-Ray", "reason": "Rules out other causes of chest pain", "urgency": "IMMEDIATE", "test_type": "IMAGING"},
        {"test_name": "Echocardiogram", "reason": "Assesses cardiac wall motion and ejection fraction", "urgency": "WITHIN_24H", "test_type": "IMAGING"},
    ],
    "Hypertension": [
        {"test_name": "Serial Blood Pressure Monitoring", "reason": "Confirms sustained hypertension", "urgency": "WITHIN_24H", "test_type": "OTHER"},
        {"test_name": "Renal Function Test (RFT)", "reason": "Checks for hypertensive nephropathy", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "ECG", "reason": "Identifies left ventricular hypertrophy", "urgency": "WITHIN_WEEK", "test_type": "ECG"},
        {"test_name": "Fundoscopy", "reason": "Detects hypertensive retinopathy", "urgency": "WITHIN_WEEK", "test_type": "OTHER"},
        {"test_name": "Urine Dipstick for Protein", "reason": "Screens for proteinuria", "urgency": "WITHIN_WEEK", "test_type": "URINE"},
    ],
    "Urinary tract infection": [
        {"test_name": "Urine Routine & Microscopy", "reason": "Detects pus cells, bacteria, RBCs in urine", "urgency": "WITHIN_24H", "test_type": "URINE"},
        {"test_name": "Urine Culture & Sensitivity", "reason": "Identifies causative organism and antibiotic sensitivity", "urgency": "WITHIN_24H", "test_type": "URINE"},
        {"test_name": "Urine Dipstick (Nitrites/Leukocytes)", "reason": "Rapid bedside screening for UTI", "urgency": "IMMEDIATE", "test_type": "URINE"},
    ],
    "Hypothyroidism": [
        {"test_name": "TSH (Thyroid Stimulating Hormone)", "reason": "Primary screening test — elevated in hypothyroidism", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "Free T4 (FT4)", "reason": "Confirms thyroid hormone deficiency", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "Anti-TPO Antibodies", "reason": "Identifies autoimmune Hashimoto's thyroiditis", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "Thyroid Ultrasound", "reason": "Checks for goitre or structural abnormalities", "urgency": "ROUTINE", "test_type": "IMAGING"},
    ],
    "Hyperthyroidism": [
        {"test_name": "TSH (Thyroid Stimulating Hormone)", "reason": "Suppressed in hyperthyroidism", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "Free T3 / Free T4", "reason": "Elevated in hyperthyroid states", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "Thyroid Scan (Tc-99m)", "reason": "Identifies hot nodules or diffuse uptake (Graves')", "urgency": "WITHIN_WEEK", "test_type": "IMAGING"},
    ],
    "Jaundice": [
        {"test_name": "Serum Bilirubin (Total/Direct/Indirect)", "reason": "Quantifies jaundice and determines type", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "Liver Function Tests (LFT)", "reason": "Assesses hepatic damage", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "Abdominal Ultrasound", "reason": "Identifies biliary obstruction or liver disease", "urgency": "WITHIN_24H", "test_type": "IMAGING"},
        {"test_name": "Urine Bilirubin & Urobilinogen", "reason": "Differentiates hepatic from obstructive jaundice", "urgency": "WITHIN_24H", "test_type": "URINE"},
    ],
    "AIDS": [
        {"test_name": "HIV Rapid Test (4th Generation)", "reason": "Screens for HIV p24 antigen and antibodies", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "HIV RNA PCR (Viral Load)", "reason": "Confirms infection and measures viral burden", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "CD4 Count", "reason": "Assesses immune status and AIDS staging", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "CBC with Differential", "reason": "Checks for anaemia and lymphopenia", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
    ],
    "GERD": [
        {"test_name": "Upper GI Endoscopy (OGD)", "reason": "Visualises oesophageal inflammation, ulcers, Barrett's", "urgency": "WITHIN_WEEK", "test_type": "OTHER"},
        {"test_name": "24-Hour pH Monitoring", "reason": "Gold standard for acid reflux confirmation", "urgency": "ROUTINE", "test_type": "OTHER"},
        {"test_name": "H. pylori Breath Test / Stool Antigen", "reason": "Rules out H. pylori as contributing factor", "urgency": "WITHIN_WEEK", "test_type": "OTHER"},
    ],
    "Peptic ulcer disease": [
        {"test_name": "H. pylori Stool Antigen Test", "reason": "Detects H. pylori — primary cause of peptic ulcers", "urgency": "WITHIN_24H", "test_type": "STOOL"},
        {"test_name": "Upper GI Endoscopy", "reason": "Directly visualises ulcers", "urgency": "WITHIN_WEEK", "test_type": "OTHER"},
        {"test_name": "CBC", "reason": "Checks for anaemia from bleeding", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
    ],
    "Bronchial Asthma": [
        {"test_name": "Spirometry (FEV1/FVC)", "reason": "Confirms obstructive pattern — hallmark of asthma", "urgency": "WITHIN_WEEK", "test_type": "OTHER"},
        {"test_name": "Peak Expiratory Flow (PEF)", "reason": "Quick bedside test for airflow obstruction", "urgency": "WITHIN_24H", "test_type": "OTHER"},
        {"test_name": "Chest X-Ray", "reason": "Rules out other causes of breathlessness", "urgency": "WITHIN_24H", "test_type": "IMAGING"},
        {"test_name": "IgE Levels and Allergy Panel", "reason": "Identifies allergic triggers", "urgency": "ROUTINE", "test_type": "BLOOD"},
    ],
    "Paralysis (brain hemorrhage)": [
        {"test_name": "Non-Contrast CT Brain", "reason": "Immediately identifies intracranial haemorrhage", "urgency": "IMMEDIATE", "test_type": "IMAGING"},
        {"test_name": "MRI Brain", "reason": "Higher sensitivity for ischaemic stroke and bleed", "urgency": "IMMEDIATE", "test_type": "IMAGING"},
        {"test_name": "CBC, Coagulation Profile (PT/aPTT)", "reason": "Rules out coagulopathy", "urgency": "IMMEDIATE", "test_type": "BLOOD"},
        {"test_name": "Blood Pressure Monitoring", "reason": "Hypertension is primary risk factor", "urgency": "IMMEDIATE", "test_type": "OTHER"},
    ],
    "Chicken pox": [
        {"test_name": "Tzanck Smear from Vesicle Base", "reason": "Identifies multinucleated giant cells", "urgency": "WITHIN_24H", "test_type": "SWAB"},
        {"test_name": "Varicella-Zoster IgM/IgG", "reason": "Confirms VZV infection serologically", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
        {"test_name": "PCR of Vesicle Fluid", "reason": "Gold standard molecular confirmation", "urgency": "WITHIN_24H", "test_type": "SWAB"},
    ],
    "Fungal infection": [
        {"test_name": "KOH Mount of Skin Scraping", "reason": "Visualises fungal hyphae directly", "urgency": "WITHIN_24H", "test_type": "SWAB"},
        {"test_name": "Fungal Culture", "reason": "Identifies species for targeted antifungal therapy", "urgency": "WITHIN_WEEK", "test_type": "SWAB"},
    ],
    "Allergy": [
        {"test_name": "Skin Prick Test", "reason": "Identifies specific allergen triggers", "urgency": "ROUTINE", "test_type": "OTHER"},
        {"test_name": "Serum Total IgE", "reason": "Elevated in atopic conditions", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
        {"test_name": "Specific IgE (RAST) Panel", "reason": "Identifies specific allergen sensitisation", "urgency": "ROUTINE", "test_type": "BLOOD"},
        {"test_name": "CBC with Eosinophil Count", "reason": "Eosinophilia suggests allergic process", "urgency": "WITHIN_WEEK", "test_type": "BLOOD"},
    ],
    "Migraine": [
        {"test_name": "MRI Brain with Contrast", "reason": "Rules out secondary causes — tumour, AVM", "urgency": "WITHIN_WEEK", "test_type": "IMAGING"},
        {"test_name": "CT Brain", "reason": "Rules out acute intracranial pathology", "urgency": "WITHIN_24H", "test_type": "IMAGING"},
    ],
    "Gastroenteritis": [
        {"test_name": "Stool Routine & Microscopy", "reason": "Identifies ova, cysts, parasites, WBCs", "urgency": "WITHIN_24H", "test_type": "STOOL"},
        {"test_name": "Stool Culture", "reason": "Identifies bacterial pathogen", "urgency": "WITHIN_24H", "test_type": "STOOL"},
        {"test_name": "Electrolytes (Na, K, Cl)", "reason": "Monitors dehydration and electrolyte imbalance", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
    ],
    "Common Cold": [
        {"test_name": "Throat Swab Culture", "reason": "Rules out bacterial superinfection", "urgency": "WITHIN_24H", "test_type": "SWAB"},
        {"test_name": "Rapid Strep Test", "reason": "Rules out Group A Streptococcal pharyngitis", "urgency": "WITHIN_24H", "test_type": "SWAB"},
    ],
}

# Generic tests for diseases not in the specific map
GENERIC_UNCERTAIN_TESTS = [
    {"test_name": "Complete Blood Count (CBC)", "reason": "Broad screening — identifies infection, anaemia, inflammation", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
    {"test_name": "Erythrocyte Sedimentation Rate (ESR)", "reason": "Non-specific marker of inflammation or infection", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
    {"test_name": "C-Reactive Protein (CRP)", "reason": "Acute phase reactant — elevated in bacterial infection", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
    {"test_name": "Blood Glucose (Random)", "reason": "Quick metabolic screen", "urgency": "WITHIN_24H", "test_type": "BLOOD"},
    {"test_name": "Urine Routine & Microscopy", "reason": "Screens for urinary tract pathology", "urgency": "WITHIN_24H", "test_type": "URINE"},
]

TEST_TYPE_ICONS = {
    "BLOOD":   "B",
    "IMAGING": "I",
    "URINE":   "U",
    "STOOL":   "S",
    "SWAB":    "W",
    "BIOPSY":  "X",
    "ECG":     "E",
    "OTHER":   "O",
}

URGENCY_ORDER = {"IMMEDIATE": 0, "WITHIN_24H": 1, "WITHIN_WEEK": 2, "ROUTINE": 3}


@dataclass
class TestingResult:
    primary_disease: str
    confidence_level: str
    requires_testing: bool
    tests: list[TestRecommendation]
    differential_tests: list[dict]   # tests for runner-up diseases
    testing_rationale: str


class TestingAgent:
    """
    When the ML ensemble is uncertain (low confidence, few symptoms,
    or model disagreement), recommends specific diagnostic tests
    for the top candidate diseases.
    Called INSTEAD of just outputting a low-confidence diagnosis.
    """

    def recommend(
        self,
        top_k_diseases: list[dict],
        confidence_level: str,
        symptoms: list[str],
    ) -> TestingResult:
        top_disease  = top_k_diseases[0]["disease"] if top_k_diseases else "Unknown"
        votes        = top_k_diseases[0].get("votes", 0) if top_k_diseases else 0
        top_prob     = top_k_diseases[0].get("probability", 0) if top_k_diseases else 0

        requires_testing = (
            confidence_level == "low"
            or confidence_level == "medium"
            or votes < 3
            or top_prob < 0.70
            or len(symptoms) < 5
        )

        # Primary disease tests
        raw_tests = DISEASE_TEST_MAP.get(top_disease, GENERIC_UNCERTAIN_TESTS)
        tests = sorted(
            [TestRecommendation(**t) for t in raw_tests],
            key=lambda t: URGENCY_ORDER.get(t.urgency, 99)
        )

        # Differential tests — for runner-up diseases (rank 2-3)
        differential_tests = []
        for d in top_k_diseases[1:3]:
            disease_name = d["disease"]
            d_tests = DISEASE_TEST_MAP.get(disease_name, [])[:2]
            if d_tests:
                differential_tests.append({
                    "disease": disease_name,
                    "probability": d["probability"],
                    "tests": d_tests,
                })

        # Build rationale
        if votes < 3 and len(symptoms) < 5:
            rationale = (
                f"With {len(symptoms)} symptom(s) and {votes}/3 model agreement, "
                f"a definitive diagnosis of {top_disease} cannot be confirmed. "
                "The following tests will establish a clear diagnosis."
            )
        elif votes < 3:
            rationale = (
                f"The diagnostic models disagree ({votes}/3 agreement). "
                f"{top_disease} is the leading candidate at {top_prob:.0%} probability, "
                "but testing is required to confirm."
            )
        else:
            rationale = (
                f"{top_disease} is the most probable diagnosis ({top_prob:.0%}), "
                "but confirmatory testing is recommended before treatment."
            )

        return TestingResult(
            primary_disease=top_disease,
            confidence_level=confidence_level,
            requires_testing=requires_testing,
            tests=tests,
            differential_tests=differential_tests,
            testing_rationale=rationale,
        )