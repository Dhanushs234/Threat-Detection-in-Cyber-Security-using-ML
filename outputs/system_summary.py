def print_system_summary():
    print("\n" + "=" * 70)
    print("HYBRID INTRUSION DETECTION SYSTEM – FINAL SUMMARY")
    print("=" * 70)

    print("\n1. DATASET")
    print("   • Dataset           : UNSW-NB15")
    print("   • Total test samples: 175,341")
    print("   • Detection type    : Binary + Anomaly-assisted (Hybrid)")

    print("\n2. PREPROCESSING PIPELINE")
    print("   • Missing values    : Filled using median values (medians.pkl)")
    print("   • Categorical data  : One-hot encoded (encoder.pkl)")
    print("   • Feature alignment : Fixed feature order (feature_columns.pkl)")
    print("   • Final feature size: 142")

    print("\n3. SCALING")
    print("   • Scaler used       : StandardScaler")
    print("   • Scaler status     : Frozen (scaler.pkl)")
    print("   • Same scaler used for training and detection")

    print("\n4. MODELS USED")
    print("   • Supervised model  : Random Forest Classifier")
    print("   • Unsupervised model: Isolation Forest")
    print("   • Both models are frozen and NOT retrained during detection")

    print("\n5. THRESHOLDS (FROZEN)")
    print("   • Random Forest attack threshold      : 0.40")
    print("   • Isolation Forest anomaly threshold  : 0.05")
    print("   • Thresholds loaded from config files")
    print("     (rf_config.json, if_config.json)")

    print("\n6. HYBRID DECISION LOGIC (FROZEN)")
    print("   • Step 1: Random Forest evaluated first")
    print("   • Step 2: If RF predicts ATTACK → Final label = ATTACK")
    print("   • Step 3: If RF predicts NORMAL → Isolation Forest evaluated")
    print("   • Step 4: If IF score < 0.05 → Final label = SUSPICIOUS")
    print("   • Step 5: Else → Final label = NORMAL")

    print("\n7. FINAL LABELS")
    print("   • Attack      : Known malicious traffic")
    print("   • Suspicious  : RF-missed traffic flagged by IF")
    print("   • Normal      : Traffic agreed normal by both models")

    print("\n8. PERFORMANCE (FINAL EVALUATION)")
    print("   • Accuracy           : ~90.9%")
    print("   • Precision          : ~97.4%")
    print("   • Recall             : ~89.0%")
    print("   • RF FN recovery by IF: ~30% of RF-missed attacks")

    print("\n9. SYSTEM STATUS")
    print("   • Hybrid pipeline    : FROZEN")
    print("   • Models             : FROZEN")
    print("   • Preprocessing      : FROZEN")
    print("   • Thresholds         : FROZEN")

    print("\n10. OPERATIONAL MODE")
    print("   • Detection is performed ONLY via hybrid pipeline")
    print("   • No RF-only or IF-only detection paths exist")

    print("\n" + "=" * 70)
    print("END OF SYSTEM SUMMARY")
    print("=" * 70 + "\n")
