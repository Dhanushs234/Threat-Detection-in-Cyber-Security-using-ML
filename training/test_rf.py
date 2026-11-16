import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
PREPROCESS_DIR = BASE_DIR / "preprocessing"

MODEL_PATH = MODEL_DIR / "rf_model.pkl"
SCALER_PATH = PREPROCESS_DIR / "scaler.pkl"
FEATURE_LIST_PATH = PREPROCESS_DIR / "feature_list.json"
LABEL_ENCODER_PATH = PREPROCESS_DIR / "label_encoder.pkl"
SCALER_FALLBACK = MODEL_DIR / "scaler.pkl"
FEATURE_LIST_FALLBACK = MODEL_DIR / "feature_list.json"
LABEL_ENCODER_FALLBACK = MODEL_DIR / "label_encoder.pkl"


SAMPLES: List[Dict[str, float]] = [
    {
        "Flow Duration": 120000,
        "Flow Packets/s": 30,
        "Flow Bytes/s": 4000,
        "Flow IAT Mean": 1500,
        "Flow IAT Std": 300,
        "Total Forward Bytes": 50000,
        "Total Backward Bytes": 45000,
        "Fwd Packet Length Mean": 900,
        "Bwd Packet Length Mean": 850,
        "SYN Flag Count": 2,
        "ACK Flag Count": 20,
        "Protocol": 6,
    },
    {
        "Flow Duration": 8000,
        "Flow Packets/s": 1500,
        "Flow Bytes/s": 200000,
        "Flow IAT Mean": 50,
        "Flow IAT Std": 10,
        "Total Forward Bytes": 300000,
        "Total Backward Bytes": 1000,
        "Fwd Packet Length Mean": 1200,
        "Bwd Packet Length Mean": 100,
        "SYN Flag Count": 15,
        "ACK Flag Count": 3,
        "Protocol": 6,
    },
    {
        "Flow Duration": 45000,
        "Flow Packets/s": 120,
        "Flow Bytes/s": 9000,
        "Flow IAT Mean": 400,
        "Flow IAT Std": 75,
        "Total Forward Bytes": 80000,
        "Total Backward Bytes": 60000,
        "Fwd Packet Length Mean": 700,
        "Bwd Packet Length Mean": 640,
        "SYN Flag Count": 4,
        "ACK Flag Count": 12,
        "Protocol": 17,
    },
]


def resolve_artifact(primary: Path, fallback: Optional[Path] = None) -> Path:
    if primary.exists():
        return primary
    if fallback and fallback.exists():
        return fallback
    raise FileNotFoundError(f"Required artifact missing: {primary} (no fallback)")


def load_pickle(path: Path):
    with open(path, "rb") as file:
        return pickle.load(file)


def load_feature_list(path: Path) -> List[str]:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if isinstance(data, dict) and "features" in data:
        return data["features"]
    if isinstance(data, list):
        return data
    raise ValueError("feature_list.json must contain a list or a {'features': [...]} structure")


def build_sample_dataframe(feature_names: List[str], samples: List[Dict[str, float]]) -> pd.DataFrame:
    rows = []
    for sample in samples:
        protocol_value = str(sample.get("Protocol", "0"))
        row = {}
        for feature in feature_names:
            if feature in sample:
                row[feature] = sample[feature]
            elif feature.startswith("Protocol_"):
                suffix = feature.split("Protocol_", 1)[1]
                row[feature] = 1.0 if suffix == protocol_value else 0.0
            else:
                row[feature] = 0.0
        rows.append(row)
    return pd.DataFrame(rows, columns=feature_names)


def main():
    rf_model = load_pickle(resolve_artifact(MODEL_PATH))
    scaler_path = resolve_artifact(SCALER_PATH, SCALER_FALLBACK)
    scaler = load_pickle(scaler_path)

    feature_list_path = None
    try:
        feature_list_path = resolve_artifact(FEATURE_LIST_PATH, FEATURE_LIST_FALLBACK)
        feature_names = load_feature_list(feature_list_path)
    except FileNotFoundError:
        if hasattr(rf_model, "feature_names_in_"):
            feature_names = rf_model.feature_names_in_.tolist()
        else:
            raise

    try:
        label_encoder_path = resolve_artifact(LABEL_ENCODER_PATH, LABEL_ENCODER_FALLBACK)
        label_encoder = load_pickle(label_encoder_path)
        label_decoder = lambda labels: label_encoder.inverse_transform(labels)
    except FileNotFoundError:
        label_decoder = lambda labels: ["Normal" if lbl == 0 else "Attack" for lbl in labels]

    sample_frame = build_sample_dataframe(feature_names, SAMPLES)
    scaled_samples = scaler.transform(sample_frame)

    predictions = rf_model.predict(scaled_samples)
    probabilities = rf_model.predict_proba(scaled_samples)
    decoded_labels = label_decoder(predictions)

    for idx, (label, probs) in enumerate(zip(decoded_labels, probabilities), start=1):
        confidence = float(max(probs))
        print(f"Sample {idx}")
        print(f"Predicted Label : {label}")
        print(f"Confidence      : {confidence:.2f}")
        if idx < len(SAMPLES):
            print()


if __name__ == "__main__":
    main()
