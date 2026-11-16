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
    """
    Generate a unique detection ID (system-generated, NOT from CSV).
    
    Format: DET-XXXXXX (6-digit zero-padded counter)
    
    Args:
        counter (int): Sequential counter starting from 1
        
    Returns:
        str: Detection ID (e.g., "DET-000001", "DET-000042")
    """
    return f"DET-{counter:06d}"


def generate_timestamp_id():
    """
    Alternative: Generate timestamp-based unique ID.
    
    Format: DET-YYYYMMDD-HHMMSS-MICROSECONDS
    
    Returns:
        str: Timestamp-based detection ID
    """
    now = datetime.now()
    return f"DET-{now.strftime('%Y%m%d-%H%M%S')}-{now.microsecond:06d}"


def detect_single_row_with_id(row_features, detection_id, medians, encoder, scaler):
    """
    Detect a single row with system-generated detection ID.
    
    Args:
        row_features (pd.Series): Single row with 16 raw features
        detection_id (str): System-generated detection ID
        medians: Frozen medians
        encoder: Frozen encoder
        scaler: Frozen scaler
        
    Returns:
        tuple: (detection_id, label, p_attack, if_score, confidence, risk, severity)
    """
    row_df = pd.DataFrame([row_features])
    
    preprocessed = preprocess_detection_features(row_df, medians, encoder, scaler)
    
    X_scaled = preprocessed.values
    
    label, p_attack, if_score = predict_single(X_scaled)
    
    confidence, risk, severity = compute_confidence_risk_severity(label, p_attack, if_score)
    
    return detection_id, label, p_attack, if_score, confidence, risk, severity


def row_by_row_detection_with_id(dataset_path, models_dir, delay_seconds=7, max_rows=None, id_type='counter'):
    """
    STEP 5: Row-by-row detection with system-generated detection IDs.
    
    Detection ID is system-generated, NOT from CSV.
    Used only for logging and display.
    
    Args:
        dataset_path (str): Path to detection CSV
        models_dir (str): Path to models directory
        delay_seconds (int): Delay between detections (default: 7)
        max_rows (int): Maximum rows to process (None = all rows)
        id_type (str): ID generation type - 'counter' or 'timestamp'
        
    Returns:
        pd.DataFrame: Detection results with system-generated IDs and metadata
    """
    print(f"\n{'='*60}")
    print("STEP 5: ROW-BY-ROW DETECTION WITH SYSTEM-GENERATED IDs")
    print(f"{'='*60}")
    print(f"Detection ID Type: {id_type.upper()}")
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
    
    print(f"\n[5/5] Starting row-by-row detection with ID generation...")
    print(f"{'='*60}")
    
    total_rows = len(features_df) if max_rows is None else min(max_rows, len(features_df))
    
    results = []
    detection_counter = 1
    
    start_time = datetime.now()
    
    for idx in range(total_rows):
        row_start = time.time()
        
        if id_type == 'counter':
            detection_id = generate_detection_id(detection_counter)
        elif id_type == 'timestamp':
            detection_id = generate_timestamp_id()
        else:
            raise ValueError(f"Invalid id_type: {id_type}. Use 'counter' or 'timestamp'")
        
        row_features = features_df.iloc[idx]
        row_metadata = metadata_df.iloc[idx]
        
        print(f"\n{'─'*60}")
        print(f"DETECTION ID: {detection_id}")
        print(f"ROW {idx + 1}/{total_rows}")
        print(f"{'─'*60}")
        print(f"Source IP: {row_metadata['src_ip']}")
        print(f"Dest IP: {row_metadata['dst_ip']}")
        print(f"Source Country: {row_metadata['src_country']}")
        print(f"Dest Country: {row_metadata['dst_country']}")
        
        det_id, label, p_attack, if_score, confidence, risk, severity = detect_single_row_with_id(
            row_features, detection_id, medians, encoder, scaler
        )
        
        print(f"\n🔍 DETECTION RESULT:")
        print(f"   Detection ID: {det_id}")
        print(f"   Label: {label}")
        print(f"   RF Attack Probability: {p_attack:.4f}")
        print(f"   IF Anomaly Score: {if_score:.4f}")
        print(f"   Confidence: {confidence}%")
        print(f"   Risk: {risk}%")
        print(f"   Severity: {severity}")
        
        results.append({
            'detection_id': det_id,
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
        
        detection_counter += 1
        
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
    print(f"Total detections: {total_rows}")
    print(f"Detection IDs generated: {detection_counter - 1}")
    print(f"Total time: {total_elapsed:.2f}s ({total_elapsed/60:.2f} minutes)")
    print(f"Average time per detection: {total_elapsed/total_rows:.2f}s")
    
    results_df = pd.DataFrame(results)
    
    print(f"\n{'='*60}")
    print("DETECTION SUMMARY")
    print(f"{'='*60}")
    print(results_df['label'].value_counts())
    
    print(f"\n{'='*60}")
    print("SEVERITY BREAKDOWN")
    print(f"{'='*60}")
    print(results_df['severity'].value_counts())
    
    print(f"\n{'='*60}")
    print("SAMPLE DETECTION IDs")
    print(f"{'='*60}")
    print(f"First ID: {results_df['detection_id'].iloc[0]}")
    print(f"Last ID: {results_df['detection_id'].iloc[-1]}")
    
    return results_df


if __name__ == "__main__":
    DATASET_PATH = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/data/cleaned_detection_input_with_ip_country.csv"
    MODELS_DIR = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/models"
    
    print("="*60)
    print("ROW-BY-ROW DETECTION WITH SYSTEM-GENERATED IDs")
    print("="*60)
    print("\n⚠️  Running with max_rows=5 for demonstration\n")
    
    print("\n" + "="*60)
    print("OPTION 1: COUNTER-BASED IDs (DET-XXXXXX)")
    print("="*60)
    
    results_counter = row_by_row_detection_with_id(
        dataset_path=DATASET_PATH,
        models_dir=MODELS_DIR,
        delay_seconds=7,
        max_rows=5,
        id_type='counter'
    )
    
    output_path = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/detection/detection_results_with_id.csv"
    results_counter.to_csv(output_path, index=False)
    print(f"\n✅ Results saved to: {output_path}")
    
    print(f"\n{'='*60}")
    print("SAMPLE RESULTS WITH DETECTION IDs")
    print(f"{'='*60}")
    print(results_counter[['detection_id', 'src_ip', 'dst_ip', 'label', 'risk', 'severity']].to_string(index=False))
    
    print("\n\n" + "="*60)
    print("TIMESTAMP-BASED ID EXAMPLE")
    print("="*60)
    print(f"Example timestamp ID: {generate_timestamp_id()}")
    print(f"Format: DET-YYYYMMDD-HHMMSS-MICROSECONDS")
    print(f"Guarantees uniqueness even for simultaneous detections")
