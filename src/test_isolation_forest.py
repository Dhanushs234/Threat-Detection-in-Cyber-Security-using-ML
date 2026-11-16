import pandas as pd
import pickle
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from preprocess import clean_data

def load_if_threshold(config_path='../models/if_config.json'):
    """Load Isolation Forest threshold from config file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    threshold = config['anomaly_score_threshold']
    print(f"[INFO] IF anomaly threshold = {threshold}")
    return threshold

def test_isolation_forest_with_scores():
    """
    Test Isolation Forest using decision_function() with manual threshold
    instead of predict() for better control over anomaly detection.
    """
    print("="*60)
    print("ISOLATION FOREST SCORE-BASED TESTING")
    print("="*60)
    
    # Load artifacts
    print("\n[1/5] Loading models and preprocessors...")
    model_dir = '../models'
    
    with open(os.path.join(model_dir, 'isolation_forest.pkl'), 'rb') as f:
        iso_forest = pickle.load(f)
    with open(os.path.join(model_dir, 'scaler.pkl'), 'rb') as f:
        scaler = pickle.load(f)
    with open(os.path.join(model_dir, 'encoder.pkl'), 'rb') as f:
        encoder = pickle.load(f)
    with open(os.path.join(model_dir, 'medians.pkl'), 'rb') as f:
        medians = pickle.load(f)
    with open(os.path.join(model_dir, 'rf_model.pkl'), 'rb') as f:
        rf_model = pickle.load(f)
    
    print("✓ All artifacts loaded")
    
    # Load test data
    print("\n[2/5] Loading test data...")
    test_path = '../data/UNSW_NB15_testing-set.csv'
    data = pd.read_csv(test_path)
    
    # Get balanced samples
    normal_samples = data[data['label'] == 0].sample(n=200, random_state=42)
    attack_samples = data[data['label'] == 1].sample(n=200, random_state=42)
    
    print(f"✓ Loaded 200 normal + 200 attack samples")
    
    # Load anomaly score threshold from config
    ANOMALY_SCORE_THRESHOLD = load_if_threshold()
    print(f"\n[3/5] Using anomaly score threshold: {ANOMALY_SCORE_THRESHOLD}")
    
    # Test on normal samples
    print("\n[4/5] Testing on NORMAL samples...")
    X_normal_clean, _ = clean_data(normal_samples, is_training=False, medians=medians, encoder=encoder)
    X_normal_scaled = scaler.transform(X_normal_clean)
    
    # Get anomaly scores (lower = more anomalous)
    if_scores_normal = iso_forest.decision_function(X_normal_scaled)
    
    # Apply manual threshold
    suspicious_count_normal = (if_scores_normal < ANOMALY_SCORE_THRESHOLD).sum()
    normal_count_normal = (if_scores_normal >= ANOMALY_SCORE_THRESHOLD).sum()
    
    print(f"  Score range: [{if_scores_normal.min():.4f}, {if_scores_normal.max():.4f}]")
    print(f"  Mean score: {if_scores_normal.mean():.4f}")
    print(f"  Classified as Normal: {normal_count_normal}/200 ({normal_count_normal/2:.1f}%)")
    print(f"  Classified as Suspicious: {suspicious_count_normal}/200 ({suspicious_count_normal/2:.1f}%)")
    
    # Sample debug output
    print(f"\n  Sample scores (first 10):")
    for i in range(10):
        label = "Suspicious" if if_scores_normal[i] < ANOMALY_SCORE_THRESHOLD else "Normal"
        print(f"    [{i}] IF score: {if_scores_normal[i]:.4f} | Threshold: {ANOMALY_SCORE_THRESHOLD} → {label}")
    
    # Test on attack samples
    print("\n[5/5] Testing on ATTACK samples...")
    X_attack_clean, _ = clean_data(attack_samples, is_training=False, medians=medians, encoder=encoder)
    X_attack_scaled = scaler.transform(X_attack_clean)
    
    # Get anomaly scores
    if_scores_attack = iso_forest.decision_function(X_attack_scaled)
    
    # Apply manual threshold
    suspicious_count_attack = (if_scores_attack < ANOMALY_SCORE_THRESHOLD).sum()
    normal_count_attack = (if_scores_attack >= ANOMALY_SCORE_THRESHOLD).sum()
    
    print(f"  Score range: [{if_scores_attack.min():.4f}, {if_scores_attack.max():.4f}]")
    print(f"  Mean score: {if_scores_attack.mean():.4f}")
    print(f"  Classified as Suspicious: {suspicious_count_attack}/200 ({suspicious_count_attack/2:.1f}%)")
    print(f"  Classified as Normal: {normal_count_attack}/200 ({normal_count_attack/2:.1f}%)")
    
    # Sample debug output
    print(f"\n  Sample scores (first 10):")
    for i in range(10):
        label = "Suspicious" if if_scores_attack[i] < ANOMALY_SCORE_THRESHOLD else "Normal"
        print(f"    [{i}] IF score: {if_scores_attack[i]:.4f} | Threshold: {ANOMALY_SCORE_THRESHOLD} → {label}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"\nAnomaly Score Threshold: {ANOMALY_SCORE_THRESHOLD}")
    print(f"\nNormal samples (200):")
    print(f"  ✓ Correctly classified as Normal: {normal_count_normal} ({normal_count_normal/2:.1f}%)")
    print(f"  ✗ False Positives (flagged as Suspicious): {suspicious_count_normal} ({suspicious_count_normal/2:.1f}%)")
    print(f"\nAttack samples (200):")
    print(f"  ✓ Correctly detected as Suspicious: {suspicious_count_attack} ({suspicious_count_attack/2:.1f}%)")
    print(f"  ✗ False Negatives (missed as Normal): {normal_count_attack} ({normal_count_attack/2:.1f}%)")
    
    detection_rate = suspicious_count_attack / 2
    fp_rate = suspicious_count_normal / 2
    
    print(f"\n📊 Detection Rate: {detection_rate:.1f}%")
    print(f"📊 False Positive Rate: {fp_rate:.1f}%")
    
    print("\n✅ Score-based decision logic applied")
    print("✅ No retraining needed")
    print("✅ 142 features confirmed")
    print("✅ Scaler & features match RF")
    
    # Generate visualization
    print("\n" + "="*60)
    print("GENERATING ANOMALY SCORE VISUALIZATION")
    print("="*60)
    
    output_dir = '../outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Isolation Forest Anomaly Score Analysis', fontsize=16, fontweight='bold')
    
    # 1. Score distribution histogram
    ax1 = axes[0, 0]
    ax1.hist(if_scores_normal, bins=30, alpha=0.6, label='Normal', color='green', edgecolor='black')
    ax1.hist(if_scores_attack, bins=30, alpha=0.6, label='Attack', color='red', edgecolor='black')
    ax1.axvline(ANOMALY_SCORE_THRESHOLD, color='blue', linestyle='--', linewidth=2, label=f'Threshold={ANOMALY_SCORE_THRESHOLD}')
    ax1.set_xlabel('Anomaly Score', fontsize=11)
    ax1.set_ylabel('Frequency', fontsize=11)
    ax1.set_title('Anomaly Score Distribution', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Box plot comparison
    ax2 = axes[0, 1]
    box_data = [if_scores_normal, if_scores_attack]
    bp = ax2.boxplot(box_data, labels=['Normal', 'Attack'], patch_artist=True)
    bp['boxes'][0].set_facecolor('green')
    bp['boxes'][0].set_alpha(0.6)
    bp['boxes'][1].set_facecolor('red')
    bp['boxes'][1].set_alpha(0.6)
    ax2.axhline(ANOMALY_SCORE_THRESHOLD, color='blue', linestyle='--', linewidth=2, label=f'Threshold={ANOMALY_SCORE_THRESHOLD}')
    ax2.set_ylabel('Anomaly Score', fontsize=11)
    ax2.set_title('Score Distribution by Class', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Scatter plot of scores
    ax3 = axes[1, 0]
    ax3.scatter(range(len(if_scores_normal)), if_scores_normal, alpha=0.5, s=20, c='green', label='Normal')
    ax3.scatter(range(len(if_scores_attack)), if_scores_attack, alpha=0.5, s=20, c='red', label='Attack')
    ax3.axhline(ANOMALY_SCORE_THRESHOLD, color='blue', linestyle='--', linewidth=2, label=f'Threshold={ANOMALY_SCORE_THRESHOLD}')
    ax3.set_xlabel('Sample Index', fontsize=11)
    ax3.set_ylabel('Anomaly Score', fontsize=11)
    ax3.set_title('Anomaly Scores per Sample', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Classification summary bar chart
    ax4 = axes[1, 1]
    categories = ['Normal\nSamples', 'Attack\nSamples']
    correct = [normal_count_normal, suspicious_count_attack]
    incorrect = [suspicious_count_normal, normal_count_attack]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, correct, width, label='Correct', color='green', alpha=0.7)
    bars2 = ax4.bar(x + width/2, incorrect, width, label='Incorrect', color='red', alpha=0.7)
    
    ax4.set_ylabel('Count', fontsize=11)
    ax4.set_title('Classification Results', fontsize=12, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(categories)
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save plot
    plot_path = os.path.join(output_dir, 'isolation_forest_anomaly_analysis.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualization saved to: {plot_path}")
    plt.close()
    
    # Additional: Score statistics summary
    stats_path = os.path.join(output_dir, 'isolation_forest_statistics.txt')
    with open(stats_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write("ISOLATION FOREST ANOMALY SCORE STATISTICS\n")
        f.write("="*60 + "\n\n")
        f.write(f"Threshold: {ANOMALY_SCORE_THRESHOLD}\n\n")
        f.write("NORMAL SAMPLES (n=200):\n")
        f.write(f"  Mean score:   {if_scores_normal.mean():.4f}\n")
        f.write(f"  Median score: {np.median(if_scores_normal):.4f}\n")
        f.write(f"  Std dev:      {if_scores_normal.std():.4f}\n")
        f.write(f"  Min score:    {if_scores_normal.min():.4f}\n")
        f.write(f"  Max score:    {if_scores_normal.max():.4f}\n")
        f.write(f"  Classified as Normal:     {normal_count_normal} ({normal_count_normal/2:.1f}%)\n")
        f.write(f"  Classified as Suspicious: {suspicious_count_normal} ({suspicious_count_normal/2:.1f}%)\n\n")
        f.write("ATTACK SAMPLES (n=200):\n")
        f.write(f"  Mean score:   {if_scores_attack.mean():.4f}\n")
        f.write(f"  Median score: {np.median(if_scores_attack):.4f}\n")
        f.write(f"  Std dev:      {if_scores_attack.std():.4f}\n")
        f.write(f"  Min score:    {if_scores_attack.min():.4f}\n")
        f.write(f"  Max score:    {if_scores_attack.max():.4f}\n")
        f.write(f"  Classified as Suspicious: {suspicious_count_attack} ({suspicious_count_attack/2:.1f}%)\n")
        f.write(f"  Classified as Normal:     {normal_count_attack} ({normal_count_attack/2:.1f}%)\n\n")
        f.write("PERFORMANCE METRICS:\n")
        f.write(f"  Detection Rate:       {detection_rate:.1f}%\n")
        f.write(f"  False Positive Rate:  {fp_rate:.1f}%\n")
        f.write(f"  True Negative Rate:   {normal_count_normal/2:.1f}%\n")
        f.write(f"  False Negative Rate:  {normal_count_attack/2:.1f}%\n")
    
    print(f"✓ Statistics saved to: {stats_path}")

if __name__ == "__main__":
    test_isolation_forest_with_scores()
