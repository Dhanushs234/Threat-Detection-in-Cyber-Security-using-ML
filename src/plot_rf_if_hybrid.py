import os
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


RESULTS_PATH = "../outputs/hybrid_detection_results.csv"
OUTPUT_DIR = "../outputs"
OUTPUT_FIG = os.path.join(OUTPUT_DIR, "rf_if_hybrid_comparison.png")


def compute_metrics(pred_binary, true_binary):
    tp = ((pred_binary == 1) & (true_binary == 1)).sum()
    tn = ((pred_binary == 0) & (true_binary == 0)).sum()
    fp = ((pred_binary == 1) & (true_binary == 0)).sum()
    fn = ((pred_binary == 0) & (true_binary == 1)).sum()

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0

    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "fpr": fpr,
    }


def main():
    if not os.path.exists(RESULTS_PATH):
        raise FileNotFoundError(f"Hybrid results not found: {RESULTS_PATH}")

    df = pd.read_csv(RESULTS_PATH)
    required_cols = {"rf_prediction", "final_label", "true_label"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in results CSV: {missing}")

    # Binary ground truth (1 = attack)
    y_true = df["true_label"].to_numpy()

    # RF metrics (Attack = positive)
    rf_pred_binary = np.where(df["rf_prediction"] == "Attack", 1, 0)
    rf_metrics = compute_metrics(rf_pred_binary, y_true)

    # Hybrid metrics (Attack or Suspicious -> positive)
    hybrid_pred_binary = np.where(df["final_label"].isin(["Attack", "Suspicious"]), 1, 0)
    hybrid_metrics = compute_metrics(hybrid_pred_binary, y_true)

    # Isolation Forest performance on RF-normal subset
    rf_normal_mask = df["rf_prediction"] == "Normal"
    if_mask_count = int(rf_normal_mask.sum())
    if_sub_true = y_true[rf_normal_mask]
    if_sub_pred = np.where(df.loc[rf_normal_mask, "final_label"] == "Suspicious", 1, 0)
    if_metrics = compute_metrics(if_sub_pred, if_sub_true)

    # Recovery stats
    rf_fn_mask = (rf_pred_binary == 0) & (y_true == 1)
    recovered_mask = (rf_fn_mask) & (df["final_label"] == "Suspicious")
    recovered = int(recovered_mask.sum())
    remaining_fn = int(rf_fn_mask.sum() - recovered)

    print("RF metrics:", rf_metrics)
    print("Hybrid metrics:", hybrid_metrics)
    print("IF metrics (RF-normal subset):", if_metrics)
    print(f"RF false negatives: {int(rf_fn_mask.sum())}")
    print(f"Recovered by IF: {recovered}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Visualization
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("RF vs IF vs Hybrid Performance", fontsize=18, fontweight="bold")

    # Plot 1: Precision/Recall comparison
    metrics_names = ["Precision", "Recall", "FPR"]
    rf_values = [rf_metrics["precision"], rf_metrics["recall"], rf_metrics["fpr"]]
    hybrid_values = [hybrid_metrics["precision"], hybrid_metrics["recall"], hybrid_metrics["fpr"]]

    x = np.arange(len(metrics_names))
    width = 0.35

    axes[0].bar(x - width / 2, rf_values, width, label="RF", color="#0275d8")
    axes[0].bar(x + width / 2, hybrid_values, width, label="Hybrid", color="#5cb85c")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(metrics_names)
    axes[0].set_ylim(0, 1)
    axes[0].set_title("RF vs Hybrid (Global Metrics)", fontsize=14)
    axes[0].legend()

    for idx, val in enumerate(rf_values):
        axes[0].text(x[idx] - width / 2, val + 0.02, f"{val:.2f}", ha="center", fontsize=9)
    for idx, val in enumerate(hybrid_values):
        axes[0].text(x[idx] + width / 2, val + 0.02, f"{val:.2f}", ha="center", fontsize=9)

    # Plot 2: RF FN recovery breakdown
    axes[1].bar(["RF FN"], [rf_fn_mask.sum()], color="#d9534f", alpha=0.7, label="Remaining FN")
    axes[1].bar(["RF FN"], [recovered], color="#f0ad4e", label="Recovered by IF")
    axes[1].set_title("Isolation Forest Recovery of RF Misses", fontsize=14)
    axes[1].set_ylabel("Count")
    axes[1].legend()

    axes[1].text(0, recovered / 2, f"Recovered\n{recovered:,}", ha="center", va="center", color="black", fontsize=11)
    axes[1].text(0, (rf_fn_mask.sum() + recovered) / 2, f"Remaining\n{remaining_fn:,}", ha="center", va="center", color="white", fontsize=11)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(OUTPUT_FIG, dpi=300)
    plt.close()

    print(f"[OK] RF vs IF vs Hybrid comparison saved to {OUTPUT_FIG}")


if __name__ == "__main__":
    main()
