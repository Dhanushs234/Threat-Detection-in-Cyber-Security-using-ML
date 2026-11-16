import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from hybrid_wrapper import predict_single, load_models
from hybrid_output_layer import compute_confidence_risk_severity

from STEP3_preprocessing import load_frozen_artifacts, preprocess_detection_features
from STEP2_metadata_split import split_metadata_and_features
from STEP1_load_dataset import load_detection_dataset


def hybrid_detection_with_output_layer(preprocessed_row):
    """
    STEP 6: Send preprocessed row to hybrid model + output layer.
    
    Pipeline:
    1. Preprocessed row (142 features) → Hybrid Model
    2. Hybrid model outputs (label, rf_prob, if_score) → Output Layer
    3. Output layer returns: label, severity, confidence, risk
    
    DO NOT re-implement formulas - uses existing:
    - hybrid_wrapper.py for model predictions
    - hybrid_output_layer.py for confidence/risk/severity
    
    Args:
        preprocessed_row (pd.DataFrame): Single row with 142 preprocessed features
        
    Returns:
        dict: {
            'label': str (Attack, Normal, Suspicious),
            'rf_attack_prob': float,
            'if_anomaly_score': float,
            'confidence': int (0-100),
            'risk': int (0-100),
            'severity': str (Low, Medium, High)
        }
    """
    X_scaled = preprocessed_row.values
    
    label, rf_prob, if_score = predict_single(X_scaled)
    
    confidence, risk, severity = compute_confidence_risk_severity(label, rf_prob, if_score)
    
    return {
        'label': label,
        'rf_attack_prob': rf_prob,
        'if_anomaly_score': if_score,
        'confidence': confidence,
        'risk': risk,
        'severity': severity
    }


def demonstrate_hybrid_integration(dataset_path, models_dir, num_samples=5):
    """
    Demonstrate STEP 6: Hybrid model + output layer integration.
    
    Shows the complete flow:
    - Load data
    - Split metadata/features
    - Preprocess features
    - Send to hybrid model
    - Pass outputs to output layer
    - Display all results
    
    Args:
        dataset_path (str): Path to detection CSV
        models_dir (str): Path to models directory
        num_samples (int): Number of samples to process
        
    Returns:
        pd.DataFrame: Results with all output layer fields
    """
    print(f"\n{'='*60}")
    print("STEP 6: HYBRID MODEL + OUTPUT LAYER INTEGRATION")
    print(f"{'='*60}")
    
    print("\n[1/5] Loading dataset...")
    dataset = load_detection_dataset(dataset_path)
    
    print("\n[2/5] Splitting metadata and features...")
    metadata_df, features_df = split_metadata_and_features(dataset)
    
    print("\n[3/5] Loading frozen preprocessing artifacts...")
    medians, encoder, scaler = load_frozen_artifacts(models_dir)
    
    print("\n[4/5] Loading frozen hybrid models...")
    load_models()
    print("✅ Hybrid models loaded (RF + IF)")
    
    print(f"\n[5/5] Processing {num_samples} samples through hybrid pipeline...")
    print(f"{'='*60}")
    
    results = []
    
    for idx in range(num_samples):
        print(f"\n{'─'*60}")
        print(f"SAMPLE {idx + 1}/{num_samples}")
        print(f"{'─'*60}")
        
        row_features = features_df.iloc[idx:idx+1]
        row_metadata = metadata_df.iloc[idx]
        
        print(f"Source IP: {row_metadata['src_ip']}")
        print(f"Dest IP: {row_metadata['dst_ip']}")
        print(f"Source Country: {row_metadata['src_country']}")
        print(f"Dest Country: {row_metadata['dst_country']}")
        
        print(f"\n📊 STEP 6 PIPELINE:")
        print(f"   [1] Preprocessing: 16 features → 142 features")
        preprocessed = preprocess_detection_features(row_features, medians, encoder, scaler)
        print(f"       ✅ Preprocessed shape: {preprocessed.shape}")
        
        print(f"\n   [2] Hybrid Model: RF → IF cascade")
        print(f"       → Random Forest evaluates first")
        print(f"       → Isolation Forest if needed")
        
        print(f"\n   [3] Output Layer: Compute metrics")
        print(f"       → Confidence calculation")
        print(f"       → Risk calculation")
        print(f"       → Severity mapping")
        
        result = hybrid_detection_with_output_layer(preprocessed)
        
        print(f"\n🎯 HYBRID MODEL OUTPUT:")
        print(f"   Label: {result['label']}")
        print(f"   RF Attack Probability: {result['rf_attack_prob']:.4f}")
        print(f"   IF Anomaly Score: {result['if_anomaly_score']:.4f}")
        
        print(f"\n📈 OUTPUT LAYER RESULTS:")
        print(f"   Confidence: {result['confidence']}%")
        print(f"   Risk: {result['risk']}%")
        print(f"   Severity: {result['severity']}")
        
        results.append({
            'row_index': idx,
            'src_ip': row_metadata['src_ip'],
            'dst_ip': row_metadata['dst_ip'],
            'src_country': row_metadata['src_country'],
            'dst_country': row_metadata['dst_country'],
            **result
        })
    
    results_df = pd.DataFrame(results)
    
    print(f"\n{'='*60}")
    print("INTEGRATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total samples processed: {num_samples}")
    print(f"\nLabel Distribution:")
    print(results_df['label'].value_counts())
    print(f"\nSeverity Distribution:")
    print(results_df['severity'].value_counts())
    
    print(f"\n{'='*60}")
    print("OUTPUT LAYER FIELDS VERIFIED")
    print(f"{'='*60}")
    print(f"✅ Label: {results_df['label'].dtype}")
    print(f"✅ Severity: {results_df['severity'].dtype}")
    print(f"✅ Confidence: {results_df['confidence'].dtype}")
    print(f"✅ Risk: {results_df['risk'].dtype}")
    print(f"✅ RF Attack Prob: {results_df['rf_attack_prob'].dtype}")
    print(f"✅ IF Anomaly Score: {results_df['if_anomaly_score'].dtype}")
    
    return results_df


if __name__ == "__main__":
    DATASET_PATH = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/data/cleaned_detection_input_with_ip_country.csv"
    MODELS_DIR = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/models"
    
    print("="*60)
    print("HYBRID MODEL + OUTPUT LAYER INTEGRATION DEMO")
    print("="*60)
    
    results = demonstrate_hybrid_integration(
        dataset_path=DATASET_PATH,
        models_dir=MODELS_DIR,
        num_samples=5
    )
    
    output_path = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/detection/hybrid_integration_results.csv"
    results.to_csv(output_path, index=False)
    print(f"\n✅ Results saved to: {output_path}")
    
    print(f"\n{'='*60}")
    print("SAMPLE RESULTS")
    print(f"{'='*60}")
    print(results[['src_ip', 'dst_ip', 'label', 'confidence', 'risk', 'severity']].to_string(index=False))
    
    print(f"\n{'='*60}")
    print("KEY POINTS")
    print(f"{'='*60}")
    print("✅ Preprocessed rows sent to hybrid model")
    print("✅ Model outputs passed to output layer")
    print("✅ NO formulas re-implemented")
    print("✅ Output layer returns: label, severity, confidence, risk")
    print("✅ Uses existing hybrid_wrapper.py and hybrid_output_layer.py")
