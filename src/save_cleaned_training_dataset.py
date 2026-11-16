"""
Utility script to regenerate and persist the cleaned training dataset
exactly as consumed by the frozen Random Forest model.

The script:
1. Loads the original UNSW-NB15 training CSV.
2. Applies the frozen preprocessing artifacts (medians, encoder, scaler).
3. Saves the scaled feature matrix with the corresponding labels.
"""

import argparse
import pickle
from pathlib import Path

import pandas as pd

from preprocess import clean_data


BASE_DIR = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Save the cleaned + scaled training dataset using frozen preprocessing artifacts."
    )
    parser.add_argument(
        "--input-path",
        default=str(BASE_DIR / "data" / "UNSW_NB15_training-set.csv"),
        help="Path to the raw UNSW-NB15 training CSV.",
    )
    parser.add_argument(
        "--artifacts-dir",
        default=str(BASE_DIR / "models"),
        help="Directory containing the frozen scaler/encoder/medians artifacts.",
    )
    parser.add_argument(
        "--output-path",
        default=str(BASE_DIR / "outputs" / "cleaned_training_dataset.csv"),
        help="Destination path for the cleaned dataset CSV.",
    )
    return parser.parse_args()


def load_pickle(path: Path):
    with open(path, "rb") as file:
        return pickle.load(file)


def main():
    args = parse_args()

    input_path = Path(args.input_path)
    artifacts_dir = Path(args.artifacts_dir)
    output_path = Path(args.output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Training data not found: {input_path}")
    if not artifacts_dir.exists():
        raise FileNotFoundError(f"Artifacts directory not found: {artifacts_dir}")

    scaler = load_pickle(artifacts_dir / "scaler.pkl")
    medians = load_pickle(artifacts_dir / "medians.pkl")
    encoder = load_pickle(artifacts_dir / "encoder.pkl")

    feature_columns_path = artifacts_dir / "feature_columns.pkl"
    feature_columns = load_pickle(feature_columns_path) if feature_columns_path.exists() else None

    print(f"[INFO] Loading raw training data from {input_path}")
    train_df = pd.read_csv(input_path)
    print(f"[INFO] Raw shape: {train_df.shape}")

    print("[INFO] Cleaning training data with frozen medians/encoder...")
    X_clean, y = clean_data(train_df, is_training=False, medians=medians, encoder=encoder)

    if feature_columns is not None:
        missing = [col for col in feature_columns if col not in X_clean.columns]
        extra = [col for col in X_clean.columns if col not in feature_columns]
        if missing or extra:
            raise ValueError(
                "Feature mismatch detected when aligning with frozen feature order. "
                f"Missing: {missing}. Extra: {extra}."
            )
        X_clean = X_clean[feature_columns]

    print(f"[INFO] Applying frozen scaler to {X_clean.shape[0]} samples / {X_clean.shape[1]} features...")
    X_scaled = scaler.transform(X_clean)
    cleaned_df = pd.DataFrame(X_scaled, columns=X_clean.columns, index=train_df.index)
    cleaned_df["label"] = y.values

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(output_path, index=False)

    print(f"[SUCCESS] Cleaned training dataset saved to {output_path}")
    print(f"[SUCCESS] Final shape (features + label): {cleaned_df.shape}")


if __name__ == "__main__":
    main()
