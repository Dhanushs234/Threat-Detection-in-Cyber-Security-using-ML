"""
HYBRID IDS – FINAL & FROZEN
-------------------------------------------------
Decision Logic:
1. Random Forest evaluated first
2. If RF predicts ATTACK → Final = ATTACK
3. If RF predicts NORMAL → Isolation Forest evaluated
4. If IF anomaly score < 0.05 → Final = SUSPICIOUS
5. Else → Final = NORMAL

Random Forest threshold   : 0.40
Isolation Forest threshold: 0.05
Features                  : 142

DO NOT MODIFY THIS FILE.
Any change requires full retraining & revalidation.
-------------------------------------------------
"""

import os
import pandas as pd
import joblib
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from preprocess import clean_data

# Global thresholds (loaded from config, validated at runtime)
RF_THRESHOLD = None
IF_THRESHOLD = None

def hybrid_decision(rf_probability, if_score):
    """
    FINAL FROZEN HYBRID DECISION LOGIC

    Rules:
    - RF first
    - IF only applied if RF says Normal
    
    Args:
        rf_probability: Random Forest attack probability [0, 1]
        if_score: Isolation Forest anomaly score (lower = more anomalous)
    
    Returns:
        str: "Attack", "Suspicious", or "Normal"
    """
    global RF_THRESHOLD, IF_THRESHOLD
    
    # Rule 1: Random Forest decides attack
    if rf_probability >= RF_THRESHOLD:
        return "Attack"
    
    # Rule 2: RF says Normal → Isolation Forest check
    if if_score < IF_THRESHOLD:
        return "Suspicious"
    
    # Rule 3: Both agree on Normal
    return "Normal"

def hybrid_detect():
    """
    Hybrid IDS using Random Forest + Isolation Forest
    
    Output labels:
    - Attack: RF detected as attack (probability >= 0.40)
    - Suspicious: RF says normal but IF flags as anomaly (score < 0.05)
    - Normal: Both RF and IF agree it's normal
    """
    
    print("="*60)
    print("HYBRID INTRUSION DETECTION SYSTEM")
    print("="*60)
    
    # STEP 1: Load all frozen artifacts
    print("\n[1/8] Loading frozen artifacts...")
    
    rf_model = joblib.load("../models/rf_model.pkl")
    iso_forest = joblib.load("../models/isolation_forest.pkl")
    scaler = joblib.load("../models/scaler.pkl")
    feature_columns = joblib.load("../models/feature_columns.pkl")
    medians = joblib.load("../models/medians.pkl")
    encoder = joblib.load("../models/encoder.pkl")
    
    print("✓ Models loaded")
    print("✓ Preprocessing artifacts loaded")
    
    # STEP 2: Load thresholds from config files
    print("\n[2/8] Loading thresholds from config...")
    
    global RF_THRESHOLD, IF_THRESHOLD
    
    with open("../models/rf_config.json") as f:
        RF_THRESHOLD = json.load(f)["attack_threshold"]
    
    with open("../models/if_config.json") as f:
        IF_THRESHOLD = json.load(f)["anomaly_score_threshold"]
    
    print(f"[INFO] RF threshold = {RF_THRESHOLD}")
    print(f"[INFO] IF anomaly threshold = {IF_THRESHOLD}")
    
    # CRITICAL: Assert frozen thresholds
    assert RF_THRESHOLD == 0.40, "RF threshold mismatch – hybrid is frozen"
    assert IF_THRESHOLD == 0.05, "IF threshold mismatch – hybrid is frozen"
    print("✓ Thresholds validated (frozen)")
    
    # STEP 3: Load test data
    print("\n[3/8] Loading test data...")
    
    data = pd.read_csv("../data/UNSW_NB15_testing-set.csv")
    y_true = data["label"].copy() if "label" in data else None
    
    print(f"✓ Loaded {len(data)} test samples")
    if y_true is not None:
        print(f"  True label distribution: {Counter(y_true)}")
    
    # STEP 4: Apply frozen preprocessing
    print("\n[4/8] Applying frozen preprocessing pipeline...")
    
    # Use clean_data with frozen artifacts (same as training)
    X_clean, _ = clean_data(data, is_training=False, medians=medians, encoder=encoder)
    
    # Scale using frozen scaler
    X_scaled = scaler.transform(X_clean)
    
    print(f"✓ Preprocessed shape: {X_scaled.shape}")
    print(f"✓ Feature count: {X_scaled.shape[1]}")
    
    # STEP 5: Random Forest decision (first line of defense)
    print("\n[5/8] Running Random Forest classification...")
    
    rf_proba = rf_model.predict_proba(X_scaled)[:, 1]
    rf_pred = np.where(rf_proba >= RF_THRESHOLD, "Attack", "Normal")
    
    rf_attack_count = (rf_pred == "Attack").sum()
    rf_normal_count = (rf_pred == "Normal").sum()
    
    print(f"✓ RF detected {rf_attack_count} attacks")
    print(f"✓ RF classified {rf_normal_count} as normal")
    
    # STEP 6: Isolation Forest (only on RF-Normal samples)
    print("\n[6/8] Running Isolation Forest on RF-Normal samples...")
    
    # Compute IF scores for all samples
    if_scores = iso_forest.decision_function(X_scaled)
    
    final_labels = []
    suspicious_count = 0
    
    for i in range(len(rf_pred)):
        # Use frozen hybrid_decision function (single source of truth)
        final_label = hybrid_decision(rf_proba[i], if_scores[i])
        final_labels.append(final_label)
        
        if final_label == "Suspicious":
            suspicious_count += 1
    
    print(f"✓ IF flagged {suspicious_count} samples as Suspicious")
    
    # STEP 7: Save results
    print("\n[7/8] Saving hybrid detection results...")
    
    output_dir = "../outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    results = pd.DataFrame({
        "rf_probability": rf_proba,
        "rf_prediction": rf_pred,
        "final_label": final_labels
    })
    
    if y_true is not None:
        results["true_label"] = y_true.values
    
    output_path = os.path.join(output_dir, "hybrid_detection_results.csv")
    results.to_csv(output_path, index=False)
    
    print(f"✓ Results saved to: {output_path}")
    
    # STEP 8: Evaluation summary
    print("\n[8/8] Hybrid detection summary...")
    print("\n" + "="*60)
    print("FINAL LABEL DISTRIBUTION")
    print("="*60)
    
    label_counts = Counter(final_labels)
    total = len(final_labels)
    
    for label in ["Attack", "Suspicious", "Normal"]:
        count = label_counts[label]
        pct = (count / total) * 100
        print(f"  {label:12s}: {count:6d} ({pct:5.1f}%)")
    
    suspicious_stats = None
    
    # If ground truth exists, compute confusion
    if y_true is not None:
        print("\n" + "="*60)
        print("PERFORMANCE ANALYSIS")
        print("="*60)
        
        # Map final labels to binary for comparison
        y_pred_binary = np.array([1 if label == "Attack" else 0 for label in final_labels])
        y_true_binary = y_true.values
        
        # Compute metrics
        tp = ((y_pred_binary == 1) & (y_true_binary == 1)).sum()
        tn = ((y_pred_binary == 0) & (y_true_binary == 0)).sum()
        fp = ((y_pred_binary == 1) & (y_true_binary == 0)).sum()
        fn = ((y_pred_binary == 0) & (y_true_binary == 1)).sum()
        
        print(f"\nRF-only Attack Detection:")
        print(f"  True Positives:  {tp}")
        print(f"  False Positives: {fp}")
        print(f"  False Negatives: {fn}")
        print(f"  True Negatives:  {tn}")
        
        # Analyze Suspicious samples
        suspicious_mask = np.array(final_labels) == "Suspicious"
        if suspicious_mask.sum() > 0:
            suspicious_true_attacks = (y_true_binary[suspicious_mask] == 1).sum()
            suspicious_true_normal = (y_true_binary[suspicious_mask] == 0).sum()
            
            suspicious_stats = {
                "total": int(suspicious_mask.sum()),
                "attacks": int(suspicious_true_attacks),
                "normal": int(suspicious_true_normal)
            }
            
            print(f"\nSuspicious Samples Analysis:")
            print(f"  Total Suspicious: {suspicious_mask.sum()}")
            print(f"  Actually attacks: {suspicious_true_attacks} ({suspicious_true_attacks/suspicious_mask.sum()*100:.1f}%)")
            print(f"  Actually normal:  {suspicious_true_normal} ({suspicious_true_normal/suspicious_mask.sum()*100:.1f}%)")
            
            print(f"\n✅ IF recovered {suspicious_true_attacks} RF-missed attacks")
        
        # Overall metrics
        accuracy = (tp + tn) / total
        if (tp + fp) > 0:
            precision = tp / (tp + fp)
        else:
            precision = 0
        if (tp + fn) > 0:
            recall = tp / (tp + fn)
        else:
            recall = 0
        
        print(f"\nOverall Metrics (Attack detection):")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
    
    # STEP 9: Visualization
    print("\n[9/9] Generating hybrid detection visualization...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Hybrid Detection Overview", fontsize=18, fontweight="bold")
    
    # Plot 1: Final label distribution
    ax1 = axes[0, 0]
    bars = ax1.bar(
        ["Attack", "Suspicious", "Normal"],
        [label_counts["Attack"], label_counts["Suspicious"], label_counts["Normal"]],
        color=["#d9534f", "#f0ad4e", "#5cb85c"],
        alpha=0.85,
    )
    ax1.set_title("Final Label Counts", fontsize=14)
    ax1.set_ylabel("Count")
    ax1.grid(axis="y", alpha=0.2)
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height, f"{height:,}", ha="center", va="bottom", fontsize=10)
    
    # Plot 2: RF probability distribution by final label
    ax2 = axes[0, 1]
    df_plot = pd.DataFrame({
        "rf_probability": rf_proba,
        "final_label": final_labels
    })
    sns.histplot(
        data=df_plot,
        x="rf_probability",
        hue="final_label",
        bins=40,
        stat="density",
        common_norm=False,
        palette={"Attack": "#d9534f", "Suspicious": "#f0ad4e", "Normal": "#5cb85c"},
        ax=ax2,
        alpha=0.35,
    )
    ax2.axvline(RF_THRESHOLD, color="#0275d8", linestyle="--", linewidth=2, label=f"RF Threshold ({RF_THRESHOLD:.2f})")
    ax2.set_title("RF Probability Distribution", fontsize=14)
    ax2.set_xlabel("RF Attack Probability")
    ax2.legend()
    ax2.grid(alpha=0.2)
    
    # Plot 3: Boxplot of RF probabilities per label
    ax3 = axes[1, 0]
    sns.boxplot(
        data=df_plot,
        x="final_label",
        y="rf_probability",
        order=["Attack", "Suspicious", "Normal"],
        palette={"Attack": "#d9534f", "Suspicious": "#f0ad4e", "Normal": "#5cb85c"},
        ax=ax3,
    )
    ax3.set_title("RF Probability by Final Label", fontsize=14)
    ax3.set_xlabel("Final Label")
    ax3.set_ylabel("RF Probability")
    ax3.grid(axis="y", alpha=0.2)
    
    # Plot 4: Suspicious breakdown (if labels exist)
    ax4 = axes[1, 1]
    if suspicious_stats:
        attack_pct = (suspicious_stats["attacks"] / suspicious_stats["total"]) * 100 if suspicious_stats["total"] else 0
        normal_pct = 100 - attack_pct
        wedges, texts, autotexts = ax4.pie(
            [suspicious_stats["attacks"], suspicious_stats["normal"]],
            labels=["Actual Attack", "Actual Normal"],
            autopct="%1.1f%%",
            colors=["#d9534f", "#5bc0de"],
            startangle=120,
            explode=(0.03, 0),
            textprops={"fontsize": 11},
        )
        ax4.set_title("Suspicious Sample Breakdown", fontsize=14)
    else:
        ax4.axis("off")
        ax4.text(0.5, 0.5, "No ground-truth labels available\nfor Suspicious breakdown.", ha="center", va="center", fontsize=12)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    hybrid_plot_path = os.path.join(output_dir, "hybrid_detection_overview.png")
    plt.savefig(hybrid_plot_path, dpi=300)
    plt.close()
    
    print(f"✓ Hybrid visualization saved to: {hybrid_plot_path}")
    
    print("\n" + "="*60)
    print("HYBRID DETECTION COMPLETE")
    print("="*60)
    print("\n✅ 3-label classification: Attack | Suspicious | Normal")
    print("✅ RF detects known attacks")
    print("✅ IF flags suspicious RF-misses")
    print("✅ Production-grade hybrid IDS ready")

if __name__ == "__main__":
    hybrid_detect()
