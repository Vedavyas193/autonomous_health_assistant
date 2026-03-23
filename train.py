import json
import pickle
from pathlib import Path
from statistics import mode

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC


def load_and_clean(
    train_path: str = "dataset/Training.csv",
    test_path: str = "dataset/Testing.csv",
):
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    train_df = train_df.dropna(axis=1, how="all")
    test_df = test_df.dropna(axis=1, how="all")

    encoder = LabelEncoder()
    train_df["prognosis"] = encoder.fit_transform(train_df["prognosis"])
    test_df["prognosis"] = encoder.transform(test_df["prognosis"])

    symptom_cols = [c for c in train_df.columns if c != "prognosis"]

    X_train = train_df[symptom_cols].values.astype(np.float32)
    y_train = train_df["prognosis"].values
    X_test = test_df[symptom_cols].values.astype(np.float32)
    y_test = test_df["prognosis"].values

    return X_train, y_train, X_test, y_test, encoder, symptom_cols


def train_ensemble(model_dir: str = "models/"):
    Path(model_dir).mkdir(parents=True, exist_ok=True)

    X_train, y_train, X_test, y_test, encoder, symptom_cols = load_and_clean()
    print(f"Training on {X_train.shape[0]} samples, {X_train.shape[1]} features.")
    print(f"Classes: {len(encoder.classes_)}")

    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    cv_models = {
        "SVM": SVC(probability=True, kernel="linear", random_state=42),
        "Naive Bayes": GaussianNB(),
        "RandomForest": RandomForestClassifier(
            n_estimators=100, random_state=18, n_jobs=-1
        ),
    }
    for name, clf in cv_models.items():
        scores = cross_val_score(clf, X_train, y_train, cv=skf, scoring="accuracy")
        print(f"[CV] {name:15s}  mean={scores.mean():.4f}  std={scores.std():.5f}")

    print("\nFitting final models on full training set...")
    final_svm = SVC(probability=True, kernel="linear", random_state=42)
    final_nb = GaussianNB()
    final_rf = RandomForestClassifier(n_estimators=100, random_state=18, n_jobs=-1)

    final_svm.fit(X_train, y_train)
    final_nb.fit(X_train, y_train)
    final_rf.fit(X_train, y_train)

    svm_preds = final_svm.predict(X_test)
    nb_preds = final_nb.predict(X_test)
    rf_preds = final_rf.predict(X_test)

    final_preds = [mode([s, n, r]) for s, n, r in zip(svm_preds, nb_preds, rf_preds)]
    test_acc = accuracy_score(y_test, final_preds)
    print(f"[TEST] Ensemble mode-vote accuracy: {test_acc * 100:.2f}%")

    artefacts = {
        "svm": final_svm,
        "nb": final_nb,
        "rf": final_rf,
        "encoder": encoder,
        "symptom_cols": symptom_cols,
    }
    with open(f"{model_dir}/ensemble.pkl", "wb") as f:
        pickle.dump(artefacts, f, protocol=pickle.HIGHEST_PROTOCOL)

    symptom_index = {sym: idx for idx, sym in enumerate(symptom_cols)}
    with open(f"{model_dir}/symptom_index.json", "w") as f:
        json.dump(symptom_index, f, indent=2)

    print(f"[SAVE] models/ensemble.pkl and models/symptom_index.json written.")


if __name__ == "__main__":
    train_ensemble()