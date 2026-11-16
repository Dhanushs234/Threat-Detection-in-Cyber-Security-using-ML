import pandas as pd
import numpy as np
import time
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from hybrid_wrapper import predict_single, load_models
from hybrid_output_layer import compute_confidence_risk_severity

from STEP3_preprocessing import load_frozen_artifacts, preprocess_detection_features
from STEP2_metadata_split import split_metadata_and_features
from STEP1_load_dataset import load_detection_dataset


def detect_single_row(row_features, medians, encoder, scaler):
    """
    Detect a single row through the complete pipeline.
    
    Args:
        row_features (pd.Series): Single row with 16 raw features
        medians: Frozen medians
        encoder: Frozen encoder
        scaler: Frozen scaler
        
    Returns:
        tuple: (label, p_attack, if_score, confidence, risk, severity)
    """
    row_df = pd.DataFrame([row_features])
    
    preprocessed = preprocess_detection_features(row_df, medians, encoder, scaler)
    
    X_scaled = preprocessed.values
    
    label, p_attack, if_score = predict_single(X_scaled)
    
    confidence, risk, severity = compute_confidence_risk_severity(label, p_attack, if_score)
    
    return label, p_attack, if_score, confidence, risk, severity


def row_by_row_detection(dataset_path, models_dir, delay_seconds=7, max_rows=None):
    """
    STEP 4: Row-by-row detection with delay.
    
    Detection mode: ROW-BY-ROW ONLY
    - Iterate one row at a time
    - Extract only the 16 features
    - Pass through preprocessing
    - Send to hybrid model
    - Insert delay after each detection
    
    Args:
        dataset_path (str): Path to detection CSV
        models_dir (str): Path to models directory
        delay_seconds (int): Delay between detections (default: 7)
        max_rows (int): Maximum rows to process (None = all rows)
        
    Returns:
        pd.DataFrame: Detection results with metadata
    """
    print(f"\n{'='*60}")
    print("STEP 4: ROW-BY-ROW DETECTION MODE")
    print(f"{'='*60}")
    print(f"Delay between detections: {delay_seconds} seconds")
    if max_rows:
        print(f"Processing limit: {max_rows} rows")
    else:
        print(f"Processing: ALL rows")
    
    print("\n[1/5] Loading dataset...")
    dataset = load_detection_dataset(dataset_path)
    
    print("\n[2/5] Splitting metadata and features...")
    metadata_df, features_df = split_metadata_and_features(dataset)
    
    print("\n[3/5] Loading frozen preprocessing artifacts...")
    medians, encoder, scaler = load_frozen_artifacts(models_dir)
    
    print("\n[4/5] Loading frozen hybrid models...")
    load_models()
    print("✅ Hybrid models loaded (RF + IF)")
    
    print(f"\n[5/5] Starting row-by-row detection...")
    print(f"{'='*60}")
    
    total_rows = len(features_df) if max_rows is None else min(max_rows, len(features_df))
    
    results = []
    
    start_time = datetime.now()
    
    for idx in range(total_rows):
        row_start = time.time()
        
        row_features = features_df.iloc[idx]
        row_metadata = metadata_df.iloc[idx]
        
        print(f"\n{'─'*60}")
        print(f"ROW {idx + 1}/{total_rows}")
        print(f"{'─'*60}")
        print(f"Source IP: {row_metadata['src_ip']}")
        print(f"Dest IP: {row_metadata['dst_ip']}")
        print(f"Source Country: {row_metadata['src_country']}")
        print(f"Dest Country: {row_metadata['dst_country']}")
        
        label, p_attack, if_score, confidence, risk, severity = detect_single_row(
            row_features, medians, encoder, scaler
        )
        
        print(f"\n🔍 DETECTION RESULT:")
        print(f"   Label: {label}")
        print(f"   RF Attack Probability: {p_attack:.4f}")
        print(f"   IF Anomaly Score: {if_score:.4f}")
        print(f"   Confidence: {confidence}%")
        print(f"   Risk: {risk}%")
        print(f"   Severity: {severity}")
        
        results.append({
            'row_index': idx,
            'src_ip': row_metadata['src_ip'],
            'dst_ip': row_metadata['dst_ip'],
            'src_country': row_metadata['src_country'],
            'dst_country': row_metadata['dst_country'],
            'label': label,
            'rf_attack_prob': p_attack,
            'if_anomaly_score': if_score,
            'confidence': confidence,
            'risk': risk,
            'severity': severity,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        row_elapsed = time.time() - row_start
        
        if idx < total_rows - 1:
            print(f"\n⏱️  Detection completed in {row_elapsed:.2f}s")
            print(f"⏳ Waiting {delay_seconds} seconds before next detection...")
            time.sleep(delay_seconds)
        else:
            print(f"\n⏱️  Final detection completed in {row_elapsed:.2f}s")
    
    end_time = datetime.now()
    total_elapsed = (end_time - start_time).total_seconds()
    
    print(f"\n{'='*60}")
    print("DETECTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total rows processed: {total_rows}")
    print(f"Total time: {total_elapsed:.2f}s ({total_elapsed/60:.2f} minutes)")
    print(f"Average time per row: {total_elapsed/total_rows:.2f}s")
    
    results_df = pd.DataFrame(results)
    
    print(f"\n{'='*60}")
    print("DETECTION SUMMARY")
    print(f"{'='*60}")
    print(results_df['label'].value_counts())
    
    print(f"\n{'='*60}")
    print("SEVERITY BREAKDOWN")
    print(f"{'='*60}")
    print(results_df['severity'].value_counts())
    
    return results_df


if __name__ == "__main__":
    DATASET_PATH = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/data/cleaned_detection_input_with_ip_country.csv"
    MODELS_DIR = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/models"
    
    print("="*60)
    print("ROW-BY-ROW DETECTION PIPELINE")
    print("="*60)
    print("\n⚠️  WARNING: Processing all 700,001 rows will take ~13.6 days")
    print("⚠️  Running with max_rows=5 for demonstration\n")
    
    results = row_by_row_detection(
        dataset_path=DATASET_PATH,
        models_dir=MODELS_DIR,
        delay_seconds=7,
        max_rows=5
    )
    
    output_path = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/detection/detection_results.csv"
    results.to_csv(output_path, index=False)
    print(f"\n✅ Results saved to: {output_path}")
    
    print(f"\n{'='*60}")
    print("SAMPLE RESULTS")
    print(f"{'='*60}")
    print(results[['src_ip', 'dst_ip', 'label', 'risk', 'severity']].head())
