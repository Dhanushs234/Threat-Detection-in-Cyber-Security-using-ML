import pandas as pd
from evaluate_rf import (
    load_model_and_preprocessors,
    evaluate_model,
    plot_confusion_matrix,
    plot_roc_curve,
    load_threshold,
)
from preprocess import preprocess_testing_data


def sample_balanced_subset(
    X: pd.DataFrame,
    y: pd.Series,
    normal_count: int = 200,
    attack_count: int = 200,
    random_state: int = 42,
):
    """
    Return a balanced subset with the requested number of normal (0) and attack (1) rows.
    """
    normal_mask = y == 0
    attack_mask = y == 1

    if normal_mask.sum() < normal_count:
        raise ValueError(
            f"Requested {normal_count} normal samples but only {normal_mask.sum()} available."
        )
    if attack_mask.sum() < attack_count:
        raise ValueError(
            f"Requested {attack_count} attack samples but only {attack_mask.sum()} available."
        )

    normal_idx = y[normal_mask].sample(n=normal_count, random_state=random_state).index
    attack_idx = y[attack_mask].sample(n=attack_count, random_state=random_state + 1).index

    subset_idx = pd.Index(normal_idx.tolist() + attack_idx.tolist())
    subset_idx = (
        subset_idx.to_series()
        .sample(frac=1.0, random_state=random_state + 2)
        .index
    )

    return X.loc[subset_idx], y.loc[subset_idx]


def main():
    test_path = "../data/UNSW_NB15_testing-set.csv"
    model_dir = "../models"
    output_dir = "../outputs"

    print("Loading model & preprocessors...")
    rf_model, scaler, medians, encoder = load_model_and_preprocessors(model_dir)
    threshold = load_threshold()

    print("\nPreprocessing testing data...")
    X_test, y_test = preprocess_testing_data(test_path, scaler, medians, encoder)
    print(f"Full test set size: {len(X_test)}")

    print("\nSampling 200 normal and 200 attack rows...")
    X_subset, y_subset = sample_balanced_subset(X_test, y_test, 200, 200)
    print(f"Subset size: {len(X_subset)}")
    print(f"Subset label counts:\n{y_subset.value_counts()}")

    y_pred, y_proba = evaluate_model(rf_model, X_subset, y_subset, output_dir, threshold)

    plot_confusion_matrix(y_subset, y_pred, output_dir)
    plot_roc_curve(y_subset, y_proba, output_dir)

    print("\n✓ Balanced subset evaluation complete!")


if __name__ == "__main__":
    main()
