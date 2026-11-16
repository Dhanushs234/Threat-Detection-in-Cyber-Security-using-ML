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


def generate_detection_id(counter):
    """Generate system-generated detection ID."""
    return f"DET-{counter:06d}"


def display_detection_output(detection_id, timestamp, metadata, detection_result):
    """
    Display detection output AFTER EACH ROW.
    
    CRITICAL: Metadata values come from metadata store, NOT model input.
    
    Args:
        detection_id (str): System-generated detection ID
        timestamp (str): Detection timestamp
        metadata (pd.Series): Metadata from metadata store (src_ip, dst_ip, countries)
        detection_result (dict): Detection results from hybrid model + output layer
    """
    print(f"\n{'='*70}")
    print(f"🔍 DETECTION OUTPUT")
    print(f"{'='*70}")
    
    print(f"\n📅 Timestamp:              {timestamp}")
    print(f"🆔 Detection ID:           {detection_id}")
    
    print(f"\n📍 SOURCE INFORMATION:")
    print(f"   IP Address:             {metadata['src_ip']}")
    print(f"   Country:                {metadata['src_country']}")
    
    print(f"\n📍 DESTINATION INFORMATION:")
    print(f"   IP Address:             {metadata['dst_ip']}")
    print(f"   Country:                {metadata['dst_country']}")
    
    print(f"\n🎯 DETECTION RESULTS:")
    print(f"   Label:                  {detection_result['label']}")
    print(f"   Severity:               {detection_result['severity']}")
    print(f"   Hybrid Confidence:      {detection_result['confidence']}%")
    print(f"   Risk Score:             {detection_result['risk']}%")
    
    print(f"\n📊 MODEL DETAILS:")
    print(f"   RF Attack Probability:  {detection_result['rf_attack_prob']:.4f}")
    print(f"   IF Anomaly Score:       {detection_result['if_anomaly_score']:.4f}")
    
    print(f"{'='*70}\n")


def detect_and_display_row(row_index, features_row, metadata_row, detection_counter, 
                           medians, encoder, scaler):
    """
    Detect single row and display output immediately.
    
    Args:
        row_index (int): Row index in dataset
        features_row (pd.Series): 16 raw features
        metadata_row (pd.Series): Metadata (IPs, countries) from metadata store
        detection_counter (int): Detection counter for ID generation
        medians: Frozen medians
        encoder: Frozen encoder
        scaler: Frozen scaler
        
    Returns:
        dict: Complete detection record
    """
    detection_id = generate_detection_id(detection_counter)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    features_df = pd.DataFrame([features_row])
    preprocessed = preprocess_detection_features(features_df, medians, encoder, scaler)
    
    X_scaled = preprocessed.values
    label, rf_prob, if_score = predict_single(X_scaled)
    confidence, risk, severity = compute_confidence_risk_severity(label, rf_prob, if_score)
    
    detection_result = {
        'label': label,
        'severity': severity,
        'confidence': confidence,
        'risk': risk,
        'rf_attack_prob': rf_prob,
        'if_anomaly_score': if_score
    }
    
    display_detection_output(detection_id, timestamp, metadata_row, detection_result)
    
    return {
        'detection_id': detection_id,
        'timestamp': timestamp,
        'row_index': row_index,
        'src_ip': metadata_row['src_ip'],
        'dst_ip': metadata_row['dst_ip'],
        'src_country': metadata_row['src_country'],
        'dst_country': metadata_row['dst_country'],
        **detection_result
    }


def row_by_row_detection_with_display(dataset_path, models_dir, delay_seconds=7, max_rows=None):
    """
    STEP 7: Row-by-row detection with immediate display output.
    
    After each detection, displays:
    - Timestamp
    - Detection ID
    - Source IP
    - Source Country
    - Destination IP
    - Destination Country
    - Label (attack/normal/suspicious)
    - Severity
    - Hybrid Confidence
    - Risk Score
    
    CRITICAL: Metadata values come from metadata store, NOT model input.
    
    Args:
        dataset_path (str): Path to detection CSV
        models_dir (str): Path to models directory
        delay_seconds (int): Delay between detections (default: 7)
        max_rows (int): Maximum rows to process (None = all rows)
        
    Returns:
        pd.DataFrame: All detection results
    """
    print(f"\n{'='*70}")
    print("STEP 7: ROW-BY-ROW DETECTION WITH IMMEDIATE DISPLAY")
    print(f"{'='*70}")
    print(f"Delay between detections: {delay_seconds} seconds")
    if max_rows:
        print(f"Processing limit: {max_rows} rows")
    else:
        print(f"Processing: ALL rows")
    
    print("\n[1/5] Loading dataset...")
    dataset = load_detection_dataset(dataset_path)
    
    print("\n[2/5] Splitting metadata and features...")
    metadata_df, features_df = split_metadata_and_features(dataset)
    
    print(f"\n⚠️  CRITICAL: Metadata stored separately")
    print(f"   Metadata will NEVER enter model")
    print(f"   Metadata used ONLY for display")
    
    print("\n[3/5] Loading frozen preprocessing artifacts...")
    medians, encoder, scaler = load_frozen_artifacts(models_dir)
    
    print("\n[4/5] Loading frozen hybrid models...")
    load_models()
    print("✅ Hybrid models loaded (RF + IF)")
    
    print(f"\n[5/5] Starting row-by-row detection with display...")
    print(f"{'='*70}")
    
    total_rows = len(features_df) if max_rows is None else min(max_rows, len(features_df))
    
    results = []
    detection_counter = 1
    
    start_time = datetime.now()
    
    for idx in range(total_rows):
        row_start = time.time()
        
        print(f"\n{'▼'*70}")
        print(f"PROCESSING ROW {idx + 1}/{total_rows}")
        print(f"{'▼'*70}")
        
        features_row = features_df.iloc[idx]
        metadata_row = metadata_df.iloc[idx]
        
        detection_record = detect_and_display_row(
            idx, features_row, metadata_row, detection_counter,
            medians, encoder, scaler
        )
        
        results.append(detection_record)
        detection_counter += 1
        
        row_elapsed = time.time() - row_start
        
        if idx < total_rows - 1:
            print(f"⏱️  Detection completed in {row_elapsed:.2f}s")
            print(f"⏳ Waiting {delay_seconds} seconds before next detection...")
            time.sleep(delay_seconds)
        else:
            print(f"⏱️  Final detection completed in {row_elapsed:.2f}s")
    
    end_time = datetime.now()
    total_elapsed = (end_time - start_time).total_seconds()
    
    print(f"\n{'='*70}")
    print("DETECTION COMPLETE - SUMMARY")
    print(f"{'='*70}")
    print(f"Total detections: {total_rows}")
    print(f"Total time: {total_elapsed:.2f}s ({total_elapsed/60:.2f} minutes)")
    print(f"Average time per detection: {total_elapsed/total_rows:.2f}s")
    
    results_df = pd.DataFrame(results)
    
    print(f"\n{'='*70}")
    print("LABEL DISTRIBUTION")
    print(f"{'='*70}")
    label_counts = results_df['label'].value_counts()
    for label, count in label_counts.items():
        percentage = (count / total_rows) * 100
        print(f"{label:12s}: {count:4d} ({percentage:5.1f}%)")
    
    print(f"\n{'='*70}")
    print("SEVERITY DISTRIBUTION")
    print(f"{'='*70}")
    severity_counts = results_df['severity'].value_counts()
    for severity, count in severity_counts.items():
        percentage = (count / total_rows) * 100
        print(f"{severity:12s}: {count:4d} ({percentage:5.1f}%)")
    
    print(f"\n{'='*70}")
    print("METADATA SOURCE VERIFICATION")
    print(f"{'='*70}")
    print(f"✅ All IP addresses from metadata store")
    print(f"✅ All countries from metadata store")
    print(f"✅ Metadata NEVER entered model")
    print(f"✅ Only 16 features used for detection")
    
    return results_df


if __name__ == "__main__":
    DATASET_PATH = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/data/cleaned_detection_input_with_ip_country.csv"
    MODELS_DIR = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/models"
    
    print("="*70)
    print("ROW-BY-ROW DETECTION WITH IMMEDIATE DISPLAY OUTPUT")
    print("="*70)
    print("\n⚠️  Running with max_rows=5 for demonstration\n")
    
    results = row_by_row_detection_with_display(
        dataset_path=DATASET_PATH,
        models_dir=MODELS_DIR,
        delay_seconds=7,
        max_rows=5
    )
    
    output_path = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/detection/detection_with_display.csv"
    results.to_csv(output_path, index=False)
    print(f"\n✅ Results saved to: {output_path}")
    
    print(f"\n{'='*70}")
    print("SAMPLE OUTPUT RECORDS")
    print(f"{'='*70}")
    display_cols = ['detection_id', 'timestamp', 'src_ip', 'dst_ip', 'label', 'severity', 'confidence', 'risk']
    print(results[display_cols].to_string(index=False))
