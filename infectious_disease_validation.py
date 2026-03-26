# infectious_disease_validation.py
"""
Validates the RF+GB+NB ensemble on:
1. Synthetic test split (our own held-out data)
2. Kaggle kaushil268 (disease-prediction-using-machine-learning)
3. Kaggle itachi9604 (disease-symptom-description-dataset)

All filtered to infectious & tropical diseases for IEEE paper reporting.
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from statistics import mode
from sklearn.metrics import (
    accuracy_score, top_k_accuracy_score,
    classification_report, f1_score
)

# ── Infectious disease filter ─────────────────────────────────────────────────

INFECTIOUS_DISEASES = [
    "Malaria", "Dengue", "Typhoid", "Tuberculosis", "Pneumonia",
    "Influenza", "COVID-19", "Cholera", "Leptospirosis", "Chikungunya",
    "Meningitis", "Septicemia", "Measles", "Chickenpox",
    "Hepatitis A", "Hepatitis B", "Hepatitis C",
    "Alcoholic hepatitis", "AIDS", "Urinary Tract Infection",
    "Common Cold", "Impetigo", "Chicken pox",
]

# ── Disease name mappings ─────────────────────────────────────────────────────

# Kaggle kaushil268 disease names → our model names
KAUSHIL_MAP = {
    "Malaria":                  "Malaria",
    "Dengue":                   "Dengue",
    "Typhoid":                  "Typhoid",
    "Tuberculosis":             "Tuberculosis",
    "Pneumonia":                "Pneumonia",
    "Common Cold":              "Common Cold",
    "Chicken pox":              "Chickenpox",
    "Chickenpox":               "Chickenpox",
    "hepatitis A":              "Hepatitis A",
    "Hepatitis B":              "Hepatitis B",
    "Hepatitis C":              "Hepatitis C",
    "Hepatitis D":              "Hepatitis C",
    "Hepatitis E":              "Hepatitis A",
    "Alcoholic hepatitis":      "Alcoholic hepatitis",
    "AIDS":                     "AIDS",
    "Urinary tract infection":  "Urinary Tract Infection",
    "Impetigo":                 "Impetigo",
}

# Kaggle itachi9604 disease names → our model names
ITACHI_MAP = {
    "Malaria":                  "Malaria",
    "Dengue":                   "Dengue",
    "Typhoid":                  "Typhoid",
    "Tuberculosis":             "Tuberculosis",
    "Pneumonia":                "Pneumonia",
    "Common Cold":              "Common Cold",
    "Chicken pox":              "Chickenpox",
    "hepatitis A":              "Hepatitis A",
    "Hepatitis B":              "Hepatitis B",
    "Hepatitis C":              "Hepatitis C",
    "Hepatitis D":              "Hepatitis C",
    "Hepatitis E":              "Hepatitis A",
    "Alcoholic hepatitis":      "Alcoholic hepatitis",
    "AIDS":                     "AIDS",
    "Urinary tract infection":  "Urinary Tract Infection",
    "Impetigo":                 "Impetigo",
}


# ── Load ensemble ─────────────────────────────────────────────────────────────

def load_ensemble(model_dir: str = "models/"):
    with open(f"{model_dir}/ensemble.pkl", "rb") as f:
        a = pickle.load(f)
    print(f"[LOADED] {len(a['encoder'].classes_)} diseases")
    print(f"[LOADED] {len(a['symptom_cols'])} symptoms")
    return a


# ── Core prediction helpers ───────────────────────────────────────────────────

def predict_batch(artefacts, X):
    rf = artefacts["rf"]
    gb = artefacts["gb"]
    nb = artefacts["nb"]

    rf_preds = rf.predict(X)
    gb_preds = gb.predict(X)
    nb_preds = nb.predict(X)

    ensemble = np.array([
        mode([r, g, n])
        for r, g, n in zip(rf_preds, gb_preds, nb_preds)
    ])

    rf_p  = rf.predict_proba(X)
    gb_p  = gb.predict_proba(X)
    nb_p  = nb.predict_proba(X)
    proba = (rf_p + gb_p + nb_p) / 3.0

    return ensemble, proba


def build_X_from_df(df, symptom_cols_in_df, our_symptoms):
    """
    Builds feature matrix from a dataframe where each symptom
    is a binary column. Maps to our symptom vocabulary.
    """
    overlap = [s for s in symptom_cols_in_df if s in our_symptoms]
    X = np.zeros((len(df), len(our_symptoms)), dtype=np.float32)
    for i, (_, row) in enumerate(df.iterrows()):
        for s in overlap:
            if row.get(s, 0) == 1:
                X[i, our_symptoms.index(s)] = 1.0
    return X, len(overlap)


def print_results(name, y_true, ensemble_preds, proba, encoder):
    top1 = accuracy_score(y_true, ensemble_preds)

    # Pass labels= so sklearn knows which columns correspond to which classes
    labels = list(range(proba.shape[1]))
    top3 = top_k_accuracy_score(y_true, proba, k=min(3, proba.shape[1]), labels=labels)
    top5 = top_k_accuracy_score(y_true, proba, k=min(5, proba.shape[1]), labels=labels)
    f1   = f1_score(y_true, ensemble_preds, average="weighted", zero_division=0)

    print(f"\n  Top-1 Accuracy   : {top1*100:.2f}%")
    print(f"  Top-3 Accuracy   : {top3*100:.2f}%")
    print(f"  Top-5 Accuracy   : {top5*100:.2f}%")
    print(f"  Weighted F1      : {f1:.4f}")
    print(f"  Samples tested   : {len(y_true)}")

    labels_present = sorted(set(y_true))
    label_names    = [encoder.classes_[i] for i in labels_present]
    print(f"\n  Per-disease report:")
    print(classification_report(
        y_true, ensemble_preds,
        labels=labels_present,
        target_names=label_names,
        zero_division=0,
    ))

    return {
        "top1": top1, "top3": top3,
        "top5": top5, "f1": f1,
        "n": len(y_true),
    }


# ── TEST 1: Synthetic test split ──────────────────────────────────────────────

def test_synthetic(artefacts, path="dataset/Testing.csv"):
    print("\n" + "="*60)
    print("TEST 1 — Synthetic Test Split (held-out 15%)")
    print("="*60)

    df = pd.read_csv(path)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(' ', '_')
    )
    df = df.dropna(axis=1, how='all')
    df = df.loc[:, ~df.columns.duplicated()]

    encoder      = artefacts["encoder"]
    our_symptoms = artefacts["symptom_cols"]
    our_diseases = list(encoder.classes_)
    symptom_cols = [c for c in df.columns if c != "prognosis"]

    # Filter to infectious diseases that our model knows
    df = df[df["prognosis"].isin(our_diseases)]

    # Further filter to infectious only
    infectious_in_data = [
        d for d in df["prognosis"].unique()
        if any(inf.lower() in d.lower() for inf in INFECTIOUS_DISEASES)
    ]
    df_inf = df[df["prognosis"].isin(infectious_in_data)]

    print(f"Total test samples      : {len(df)}")
    print(f"Infectious samples      : {len(df_inf)}")
    print(f"Infectious diseases     : {sorted(df_inf['prognosis'].unique())}")

    if len(df_inf) == 0:
        print("No infectious samples found.")
        return None

    X, overlap_count = build_X_from_df(df_inf, symptom_cols, our_symptoms)
    y_true = encoder.transform(df_inf["prognosis"].tolist())

    print(f"Symptom overlap         : {overlap_count}/{len(symptom_cols)}")

    ensemble_preds, proba = predict_batch(artefacts, X)
    result = print_results("Synthetic", y_true, ensemble_preds, proba, encoder)
    result["dataset"] = "Synthetic test split"
    return result


# ── TEST 2: Kaggle kaushil268 ─────────────────────────────────────────────────

def test_kaushil268(artefacts, path="dataset/Testing.csv"):
    """
    Uses the original Kaggle 41-disease test set.
    Maps disease names to our vocabulary and filters infectious only.
    Note: if you trained on this data, treat results as in-distribution reference.
    """
    print("\n" + "="*60)
    print("TEST 2 — Kaggle kaushil268 (41 diseases)")
    print("URL: kaggle.com/datasets/kaushil268/disease-prediction-using-machine-learning")
    print("="*60)

    if not Path(path).exists():
        print(f"File not found: {path}")
        print("Place Testing.csv in dataset/ folder")
        return None

    df = pd.read_csv(path)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(' ', '_')
    )
    df = df.dropna(axis=1, how='all')
    df = df.loc[:, ~df.columns.duplicated()]

    encoder      = artefacts["encoder"]
    our_symptoms = artefacts["symptom_cols"]
    symptom_cols = [c for c in df.columns if c != "prognosis"]

    # Map disease names
    df["mapped"] = df["prognosis"].map(
        {k.lower().replace(' ','_'): v for k, v in KAUSHIL_MAP.items()}
        | {k: v for k, v in KAUSHIL_MAP.items()}
    )

    # Filter mapped + infectious + known to our model
    df = df[df["mapped"].notna()]
    df = df[df["mapped"].isin(list(encoder.classes_))]
    df_inf = df[df["mapped"].isin(INFECTIOUS_DISEASES)]

    print(f"Total mapped samples    : {len(df)}")
    print(f"Infectious samples      : {len(df_inf)}")
    print(f"Infectious diseases     : {sorted(df_inf['mapped'].unique())}")

    if len(df_inf) == 0:
        print("No infectious samples after mapping.")
        return None

    X, overlap_count = build_X_from_df(df_inf, symptom_cols, our_symptoms)
    y_true = encoder.transform(df_inf["mapped"].tolist())

    print(f"Symptom overlap         : {overlap_count}/{len(symptom_cols)}")

    ensemble_preds, proba = predict_batch(artefacts, X)
    result = print_results("kaushil268", y_true, ensemble_preds, proba, encoder)
    result["dataset"] = "Kaggle kaushil268"
    return result


# ── TEST 3: Kaggle itachi9604 ─────────────────────────────────────────────────

def test_itachi9604(artefacts, path="real_datasets/itachi9604.csv"):
    """
    Tests on the itachi9604 Kaggle dataset.
    This dataset uses wide format: Disease, Symptom_1, Symptom_2, ...
    Each row has symptom names as values, not binary columns.
    """
    print("\n" + "="*60)
    print("TEST 3 — Kaggle itachi9604 (Disease-Symptom-Description)")
    print("URL: kaggle.com/datasets/itachi9604/disease-symptom-description-dataset")
    print("="*60)

    if not Path(path).exists():
        print(f"File not found: {path}")
        print(f"Download dataset.csv and place at: {path}")
        return None

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    print(f"Columns: {list(df.columns[:6])}...")
    print(f"Total rows: {len(df)}")

    encoder      = artefacts["encoder"]
    our_symptoms = artefacts["symptom_cols"]

    disease_col  = [c for c in df.columns if "disease" in c.lower()][0]
    symptom_cols = [c for c in df.columns if "symptom" in c.lower()]

    # Map disease names
    df["mapped"] = df[disease_col].str.strip().map(ITACHI_MAP)
    df = df[df["mapped"].notna()]
    df = df[df["mapped"].isin(list(encoder.classes_))]
    df_inf = df[df["mapped"].isin(INFECTIOUS_DISEASES)]

    print(f"Mapped samples          : {len(df)}")
    print(f"Infectious samples      : {len(df_inf)}")
    print(f"Infectious diseases     : {sorted(df_inf['mapped'].unique())}")

    if len(df_inf) == 0:
        print("No infectious samples after mapping.")
        return None

    # ✅ FIXED BLOCK (properly indented)
    X = np.zeros((len(df_inf), len(our_symptoms)), dtype=np.float32)
    matched_total = 0

    for i, (_, row) in enumerate(df_inf.iterrows()):
        for sc in symptom_cols:
            sym_raw = str(row.get(sc, "")).strip().lower()

            sym_clean = (
                sym_raw
                .replace(" ", "_")
                .replace("-", "_")
                .replace("(", "")
                .replace(")", "")
                .strip("_")
            )

            if sym_clean and sym_clean in our_symptoms:
                X[i, our_symptoms.index(sym_clean)] = 1.0
                matched_total += 1
            else:
                for our_sym in our_symptoms:
                    if sym_clean and (sym_clean in our_sym or our_sym in sym_clean):
                        X[i, our_symptoms.index(our_sym)] = 1.0
                        matched_total += 1
                        break

    avg_syms = matched_total / len(df_inf) if len(df_inf) > 0 else 0
    print(f"Avg symptoms matched    : {avg_syms:.1f} per sample")

    y_true = encoder.transform(df_inf["mapped"].tolist())

    ensemble_preds, proba = predict_batch(artefacts, X)
    result = print_results("itachi9604", y_true, ensemble_preds, proba, encoder)

    result["dataset"] = "Kaggle itachi9604"
    return result
# ── Summary table ─────────────────────────────────────────────────────────────

def print_summary(results):
    print("\n" + "="*70)
    print("VALIDATION SUMMARY — INFECTIOUS & TROPICAL DISEASES (IEEE TABLE)")
    print("="*70)
    print(f"{'Dataset':<30} {'Top-1':>8} {'Top-3':>8} {'Top-5':>8} {'F1':>8} {'N':>8}")
    print("-"*70)
    for r in results:
        if r is None:
            continue
        print(
            f"{r['dataset']:<30} "
            f"{r['top1']*100:>7.2f}% "
            f"{r['top3']*100:>7.2f}% "
            f"{r['top5']*100:>7.2f}% "
            f"{r['f1']:>8.4f} "
            f"{r['n']:>8}"
        )
    print("="*70)
    print("\nAll results filtered to infectious & tropical disease subset.")
    print("Accuracy variation across datasets reflects symptom vocabulary")
    print("differences — cross-dataset generalisation is expected to be lower")
    print("than within-distribution performance.")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    artefacts = load_ensemble("models/")

    results = [
        test_synthetic(artefacts),
        test_kaushil268(artefacts),
        test_itachi9604(artefacts),
    ]

    print_summary([r for r in results if r is not None])