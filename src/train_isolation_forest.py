import pandas as pd
import pickle
import os
from sklearn.ensemble import IsolationForest

def train_isolation_forest():
    print("="*60)
    print("ISOLATION FOREST TRAINING - NORMAL TRAFFIC ONLY")
    print("="*60)
    
    # Step 1: Verify RF artifacts exist
    print("\n[1/9] Verifying RF artifacts...")
    model_dir = '../models'
    required_files = ['rf_model.pkl', 'scaler.pkl', 'encoder.pkl', 'medians.pkl', 'rf_config.json']
    
    for file in required_files:
        path = os.path.join(model_dir, file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ Missing required file: {path}")
    print("✓ All RF artifacts found")
    
    # Step 2: Load training data (same as RF used)
    print("\n[2/9] Loading training data...")
    data_path = '../data/UNSW_NB15_training-set.csv'
    data = pd.read_csv(data_path)
    print(f"✓ Loaded {len(data)} total samples")
    print(f"  Label distribution:\n{data['label'].value_counts()}")
    
    # Step 3: Filter ONLY normal traffic
    print("\n[3/9] Filtering ONLY normal traffic (label=0)...")
    normal_data = data[data['label'] == 0].copy()
    print(f"✓ Filtered to {len(normal_data)} normal samples")
    
    if len(normal_data) == 0:
        raise ValueError("❌ No normal samples found! Check label mapping.")
    
    # Step 4: Remove label column (no label leakage)
    print("\n[4/9] Removing label column...")
    X_normal_raw = normal_data.drop(columns=['label'])
    print(f"✓ Features shape: {X_normal_raw.shape}")
    
    # Step 5: Load and apply same preprocessing as RF
    print("\n[5/9] Loading RF preprocessing artifacts...")
    with open(os.path.join(model_dir, 'scaler.pkl'), 'rb') as f:
        scaler = pickle.load(f)
    with open(os.path.join(model_dir, 'encoder.pkl'), 'rb') as f:
        encoder = pickle.load(f)
    with open(os.path.join(model_dir, 'medians.pkl'), 'rb') as f:
        medians = pickle.load(f)
    with open(os.path.join(model_dir, 'rf_model.pkl'), 'rb') as f:
        rf_model = pickle.load(f)
    
    # Get feature order from trained RF model
    if hasattr(rf_model, 'feature_names_in_'):
        feature_columns = rf_model.feature_names_in_.tolist()
        print(f"✓ Loaded {len(feature_columns)} feature columns from RF model")
    else:
        raise AttributeError("❌ RF model doesn't have feature_names_in_. Retrain RF with sklearn >= 1.0")
    
    # Step 6: Apply same preprocessing pipeline as RF
    print("\n[6/9] Applying RF preprocessing pipeline...")
    from preprocess import clean_data
    
    # Reconstruct the dataframe with label for clean_data function
    normal_data_with_label = normal_data.copy()
    X_normal_clean, _ = clean_data(normal_data_with_label, is_training=False, medians=medians, encoder=encoder)
    
    # Scale using RF scaler (DO NOT fit again)
    X_normal_scaled = scaler.transform(X_normal_clean)
    print(f"✓ Preprocessed and scaled: {X_normal_scaled.shape}")
    
    # Verify feature alignment
    if X_normal_scaled.shape[1] != len(feature_columns):
        raise ValueError(f"❌ Feature mismatch: {X_normal_scaled.shape[1]} vs {len(feature_columns)}")
    print(f"✓ Feature count matches RF: {len(feature_columns)}")
    
    # Step 7: Train Isolation Forest
    print("\n[7/9] Training Isolation Forest...")
    print("  Parameters:")
    print("    n_estimators=300")
    print("    max_samples=256")
    print("    contamination=0.10")
    print("    random_state=42")
    
    iso_forest = IsolationForest(
        n_estimators=300,
        max_samples=256,
        contamination=0.10,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    iso_forest.fit(X_normal_scaled)
    print("✓ Isolation Forest trained ONLY on NORMAL traffic")
    
    # Step 8: Save Isolation Forest model
    print("\n[8/9] Saving Isolation Forest model...")
    iso_path = os.path.join(model_dir, 'isolation_forest.pkl')
    with open(iso_path, 'wb') as f:
        pickle.dump(iso_forest, f)
    print(f"✓ Model saved to {iso_path}")
    
    # Save feature columns for consistency
    feature_columns_path = os.path.join(model_dir, 'feature_columns.pkl')
    with open(feature_columns_path, 'wb') as f:
        pickle.dump(feature_columns, f)
    print(f"✓ Feature columns saved to {feature_columns_path}")
    
    # Step 9: Mandatory sanity checks
    print("\n[9/9] Running sanity checks...")
    print("\n--- Check 1: Normal samples ---")
    preds_normal = iso_forest.predict(X_normal_scaled[:200])
    normal_inliers = (preds_normal == 1).sum()
    normal_outliers = (preds_normal == -1).sum()
    
    print(f"  Sample predictions (first 20): {preds_normal[:20]}")
    print(f"  Inliers (+1):  {normal_inliers}/200 ({normal_inliers/2:.1f}%)")
    print(f"  Outliers (-1): {normal_outliers}/200 ({normal_outliers/2:.1f}%)")
    
    if normal_outliers > 50:
        print("  ⚠️  WARNING: High outlier rate on normal data. Check contamination parameter.")
    else:
        print("  ✓ Normal outlier rate acceptable")
    
    # Optional but recommended: Test on attacks
    print("\n--- Check 2: Attack samples ---")
    attack_data = data[data['label'] == 1].copy()
    if len(attack_data) > 0:
        X_attack_clean, _ = clean_data(attack_data, is_training=False, medians=medians, encoder=encoder)
        X_attack_scaled = scaler.transform(X_attack_clean)
        
        attack_preds = iso_forest.predict(X_attack_scaled[:200])
        attack_outliers = (attack_preds == -1).sum()
        attack_inliers = (attack_preds == 1).sum()
        
        print(f"  Outliers (-1): {attack_outliers}/200 ({attack_outliers/2:.1f}%)")
        print(f"  Inliers (+1):  {attack_inliers}/200 ({attack_inliers/2:.1f}%)")
        
        if attack_outliers < 50:
            print("  ⚠️  WARNING: Low anomaly detection on attacks. Model may need tuning.")
        else:
            print("  ✓ Attack anomaly detection working")
    else:
        print("  ⚠️  No attack samples to test")
    
    print("\n" + "="*60)
    print("ISOLATION FOREST TRAINING COMPLETE")
    print("="*60)
    print("\n✅ Guarantees:")
    print("  ✓ Same features as RF")
    print("  ✓ Same scaler as RF")
    print("  ✓ No label leakage")
    print("  ✓ No data leakage")
    print("  ✓ Trained only on normal behavior")
    print("\n✅ Ready for ensemble integration")

if __name__ == "__main__":
    train_isolation_forest()
