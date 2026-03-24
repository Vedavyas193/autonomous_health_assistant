import json
import pickle
from pathlib import Path
from statistics import mode

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder


def load_and_clean(
    train_path: str = "dataset/Training.csv",
    test_path:  str = "dataset/Testing.csv",
):
    train_df = pd.read_csv(train_path)
    test_df  = pd.read_csv(test_path)

    train_df = train_df.dropna(axis=1, how="all")
    test_df  = test_df.dropna(axis=1, how="all")

    train_df.columns = train_df.columns.str.strip().str.lower().str.replace(' ', '_')
    test_df.columns  = test_df.columns.str.strip().str.lower().str.replace(' ', '_')

    train_df = train_df.loc[:, ~train_df.columns.duplicated()]
    test_df  = test_df.loc[:, ~test_df.columns.duplicated()]

    encoder = LabelEncoder()
    train_df["prognosis"] = encoder.fit_transform(train_df["prognosis"])
    test_df["prognosis"]  = encoder.transform(test_df["prognosis"])

    symptom_cols = [c for c in train_df.columns if c != "prognosis"]

    X_train = train_df[symptom_cols].values.astype(np.float32)
    y_train = train_df["prognosis"].values
    X_test  = test_df[symptom_cols].values.astype(np.float32)
    y_test  = test_df["prognosis"].values

    return X_train, y_train, X_test, y_test, encoder, symptom_cols


def train_ensemble(model_dir: str = "models/"):
    Path(model_dir).mkdir(parents=True, exist_ok=True)

    X_train, y_train, X_test, y_test, encoder, symptom_cols = load_and_clean()
    print(f"Training on {X_train.shape[0]} samples, {X_train.shape[1]} features.")
    print(f"Classes: {len(encoder.classes_)}")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_models = {
        "RandomForest":     RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1, class_weight="balanced"),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42),
        "NaiveBayes":       GaussianNB(),
    }
    for name, clf in cv_models.items():
        scores = cross_val_score(clf, X_train, y_train, cv=skf, scoring="accuracy", n_jobs=-1)
        print(f"[CV] {name:20s}  mean={scores.mean():.4f}  std={scores.std():.4f}")

    print("\nFitting final models...")
    final_rf = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1, class_weight="balanced")
    final_gb = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
    final_nb = GaussianNB()

    final_rf.fit(X_train, y_train)
    print("  RandomForest done")
    final_gb.fit(X_train, y_train)
    print("  GradientBoosting done")
    final_nb.fit(X_train, y_train)
    print("  NaiveBayes done")

    rf_preds = final_rf.predict(X_test)
    gb_preds = final_gb.predict(X_test)
    nb_preds = final_nb.predict(X_test)

    final_preds = [mode([r, g, n]) for r, g, n in zip(rf_preds, gb_preds, nb_preds)]
    acc = accuracy_score(y_test, final_preds)
    print(f"\n[TEST] Ensemble accuracy: {acc * 100:.2f}%")
    print(classification_report(y_test, final_preds, target_names=encoder.classes_, zero_division=0))

    artefacts = {
        "rf":           final_rf,
        "gb":           final_gb,
        "nb":           final_nb,
        "encoder":      encoder,
        "symptom_cols": symptom_cols,
    }
    with open(f"{model_dir}/ensemble.pkl", "wb") as f:
        pickle.dump(artefacts, f, protocol=pickle.HIGHEST_PROTOCOL)

    symptom_index = {sym: idx for idx, sym in enumerate(symptom_cols)}
    with open(f"{model_dir}/symptom_index.json", "w") as f:
        json.dump(symptom_index, f, indent=2)

    print(f"\n[SAVE] models/ensemble.pkl and models/symptom_index.json written.")


if __name__ == "__main__":
    train_ensemble()