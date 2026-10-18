import csv
import json
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parent.parent / "model"

SMOKING_LABELS = {
    "No Info": "No information",
    "current": "Current smoker",
    "ever": "Ever smoked",
    "former": "Former smoker",
    "never": "Never smoked",
    "not current": "Not a current smoker",
}

FEATURE_LABELS = {
    "HbA1c_level": "HbA1c level",
    "blood_glucose_level": "Blood glucose level",
    "age": "Age",
    "bmi": "BMI",
    "smoking_history": "Smoking history",
    "hypertension": "Hypertension",
    "heart_disease": "Heart disease",
    "gender": "Gender",
}


@lru_cache(maxsize=1)
def get_metadata():
    with open(MODEL_DIR / "model_metadata.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def get_model():
    return joblib.load(MODEL_DIR / "diabetes_model.pkl")


def numeric_ranges():
    ranges = {}
    for key, bounds in get_metadata()["numeric_ranges"].items():
        low, high = bounds["min"], bounds["max"]
        if key == "age":
            low = max(low, 1.0)
        ranges[key] = (low, high)
    return ranges


def risk_level(probability):
    bands = get_metadata()["risk_bands"]
    if probability < bands["low_below"]:
        return "Low"
    if probability >= bands["high_from"]:
        return "High"
    return "Moderate"


def predict(values):
    meta = get_metadata()
    row = pd.DataFrame([values])[meta["feature_order"]]
    probability = float(get_model().predict_proba(row)[0, 1])
    return {
        "probability": probability,
        "risk_level": risk_level(probability),
        "predicted_class": int(probability >= meta["threshold"]),
    }


@lru_cache(maxsize=1)
def get_model_comparison():
    with open(MODEL_DIR / "model_comparison.csv", encoding="utf-8") as f:
        return [
            {
                "model": row["Model"],
                "accuracy": float(row["Accuracy"]),
                "precision": float(row["Precision"]),
                "recall": float(row["Recall"]),
                "f1": float(row["F1-score"]),
                "roc_auc": float(row["ROC-AUC"]),
            }
            for row in csv.DictReader(f)
        ]


@lru_cache(maxsize=1)
def get_feature_importance():
    with open(MODEL_DIR / "feature_importance.csv", encoding="utf-8") as f:
        rows = [
            {
                "feature": FEATURE_LABELS.get(row["Feature"], row["Feature"]),
                "importance": max(float(row["Importance"]), 0.0),
            }
            for row in csv.DictReader(f)
        ]
    top = max((r["importance"] for r in rows), default=0) or 1
    for r in rows:
        r["width"] = round(r["importance"] / top * 100, 1)
    return rows
