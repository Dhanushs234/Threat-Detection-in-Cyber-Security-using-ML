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


class BlockedIPManager:
    """Manages the blocked IP list."""
    
    def __init__(self):
        self.blocked_ips = set()
        self.block_records = []
    
    def add_blocked_ip(self, src_ip, detection_id, timestamp, reason="Attack detected"):
        """
        Add IP to blocked list.
        
        Args:
            src_ip (str): Source IP address to block
            detection_id (str): Detection ID that triggered the block
            timestamp (str): When the block occurred
            reason (str): Reason for blocking
        """
        if src_ip not in self.blocked_ips:
            self.blocked_ips.add(src_ip)
            self.block_records.append({
                'blocked_ip': src_ip,
                'detection_id': detection_id,
                'timestamp': timestamp,
                'reason': reason
            })
            return True
        return False
    
    def is_blocked(self, src_ip):
        """Check if IP is already blocked."""
        return src_ip in self.blocked_ips
    
    def get_blocked_count(self):
        """Get total number of blocked IPs."""
        return len(self.blocked_ips)
    
    def get_block_records(self):
        """Get all block records as DataFrame."""
        return pd.DataFrame(self.block_records)


def generate_detection_id(counter):
    """Generate system-generated detection ID."""
    return f"DET-{counter:06d}"


def display_auto_block(src_ip):
    """
    Display auto-block message immediately.
    
    Args:
        src_ip (str): Source IP that was blocked
    """
    print(f"\n{'🚨'*35}")
    print(f"⛔ AUTO-BLOCKED IP: {src_ip}")
    print(f"📋 REASON: Attack detected")
    print(f"{'🚨'*35}\n")


def display_detection_output(detection_id, timestamp, metadata, detection_result, blocked=False):
    """
    Display detection output with optional block indicator.
    
    Args:
        detection_id (str): System-generated detection ID
        timestamp (str): Detection timestamp
        metadata (pd.Series): Metadata from metadata store
        detection_result (dict): Detection results
        blocked (bool): Whether IP was blocked
    """
    print(f"\n{'='*70}")
    print(f"🔍 DETECTION OUTPUT")
    print(f"{'='*70}")
    
    print(f"\n📅 Timestamp:              {timestamp}")
    print(f"🆔 Detection ID:           {detection_id}")
    
    print(f"\n📍 SOURCE INFORMATION:")
    print(f"   IP Address:             {metadata['src_ip']}")
    print(f"   Country:                {metadata['src_country']}")
    if blocked:
        print(f"   Status:                 ⛔ BLOCKED")
    
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


def detect_and_auto_block(row_index, features_row, metadata_row, detection_counter,
                          medians, encoder, scaler, blocked_ip_manager):
    """
    Detect single row and auto-block if attack detected.
    
    CRITICAL RULES:
    - If label == "Attack" → Add src_ip to blocked list
    - Do NOT block "Normal"
    - Do NOT block "Suspicious"
    
    Args:
        row_index (int): Row index
        features_row (pd.Series): 16 raw features
        metadata_row (pd.Series): Metadata from metadata store
        detection_counter (int): Detection counter
        medians: Frozen medians
        encoder: Frozen encoder
        scaler: Frozen scaler
        blocked_ip_manager: BlockedIPManager instance
        
    Returns:
        dict: Complete detection record with block status
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
    
    blocked = False
    src_ip = metadata_row['src_ip']
    
    if label == "Attack":
        was_new_block = blocked_ip_manager.add_blocked_ip(src_ip, detection_id, timestamp)
        if was_new_block:
            display_auto_block(src_ip)
            blocked = True
        else:
            print(f"\n⚠️  IP {src_ip} already blocked (previous attack detection)")
            blocked = True
    
    display_detection_output(detection_id, timestamp, metadata_row, detection_result, blocked)
    
    return {
        'detection_id': detection_id,
        'timestamp': timestamp,
        'row_index': row_index,
        'src_ip': src_ip,
        'dst_ip': metadata_row['dst_ip'],
        'src_country': metadata_row['src_country'],
        'dst_country': metadata_row['dst_country'],
        **detection_result,
        'blocked': blocked
    }


def row_by_row_detection_with_auto_block(dataset_path, models_dir, delay_seconds=7, max_rows=None):
    """
    STEP 8: Row-by-row detection with auto-block logic.
    
    Auto-block rules:
    - If label == "Attack" → Add src_ip to blocked list
    - Display: AUTO-BLOCKED IP: <src_ip>, REASON: Attack detected
    - Do NOT block "Normal"
    - Do NOT block "Suspicious"
    
    Args:
        dataset_path (str): Path to detection CSV
        models_dir (str): Path to models directory
        delay_seconds (int): Delay between detections (default: 7)
        max_rows (int): Maximum rows to process (None = all rows)
        
    Returns:
        tuple: (results_df, blocked_ips_df)
    """
    print(f"\n{'='*70}")
    print("STEP 8: ROW-BY-ROW DETECTION WITH AUTO-BLOCK")
    print(f"{'='*70}")
    print(f"Auto-block rule: ONLY block if label == 'Attack'")
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
    
    print("\n[5/5] Initializing blocked IP manager...")
    blocked_ip_manager = BlockedIPManager()
    print("✅ Blocked IP manager ready")
    
    print(f"\n{'='*70}")
    print("STARTING DETECTION WITH AUTO-BLOCK")
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
        
        detection_record = detect_and_auto_block(
            idx, features_row, metadata_row, detection_counter,
            medians, encoder, scaler, blocked_ip_manager
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
    
    results_df = pd.DataFrame(results)
    
    print(f"\n{'='*70}")
    print("LABEL DISTRIBUTION")
    print(f"{'='*70}")
    label_counts = results_df['label'].value_counts()
    for label, count in label_counts.items():
        percentage = (count / total_rows) * 100
        print(f"{label:12s}: {count:4d} ({percentage:5.1f}%)")
    
    print(f"\n{'='*70}")
    print("AUTO-BLOCK SUMMARY")
    print(f"{'='*70}")
    print(f"Total IPs blocked: {blocked_ip_manager.get_blocked_count()}")
    print(f"Attack detections: {(results_df['label'] == 'Attack').sum()}")
    print(f"Normal detections: {(results_df['label'] == 'Normal').sum()} (NOT blocked)")
    print(f"Suspicious detections: {(results_df['label'] == 'Suspicious').sum()} (NOT blocked)")
    
    blocked_ips_df = blocked_ip_manager.get_block_records()
    
    if len(blocked_ips_df) > 0:
        print(f"\n{'='*70}")
        print("BLOCKED IPs LIST")
        print(f"{'='*70}")
        for _, record in blocked_ips_df.iterrows():
            print(f"⛔ {record['blocked_ip']:20s} | {record['detection_id']} | {record['timestamp']}")
    else:
        print(f"\n✅ No IPs blocked (no attacks detected)")
    
    print(f"\n{'='*70}")
    print("AUTO-BLOCK RULES VERIFICATION")
    print(f"{'='*70}")
    print(f"✅ Only 'Attack' label triggers blocking")
    print(f"✅ 'Normal' label does NOT trigger blocking")
    print(f"✅ 'Suspicious' label does NOT trigger blocking")
    
    return results_df, blocked_ips_df


if __name__ == "__main__":
    DATASET_PATH = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/data/cleaned_detection_input_with_ip_country.csv"
    MODELS_DIR = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/models"
    
    print("="*70)
    print("ROW-BY-ROW DETECTION WITH AUTO-BLOCK LOGIC")
    print("="*70)
    print("\n⚠️  Running with max_rows=5 for demonstration")
    print("⚠️  Note: Sample data may not contain attacks\n")
    
    results, blocked_ips = row_by_row_detection_with_auto_block(
        dataset_path=DATASET_PATH,
        models_dir=MODELS_DIR,
        delay_seconds=7,
        max_rows=5
    )
    
    output_path = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/detection/detection_with_auto_block.csv"
    results.to_csv(output_path, index=False)
    print(f"\n✅ Detection results saved to: {output_path}")
    
    if len(blocked_ips) > 0:
        blocked_path = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/detection/blocked_ips.csv"
        blocked_ips.to_csv(blocked_path, index=False)
        print(f"✅ Blocked IPs saved to: {blocked_path}")
    
    print(f"\n{'='*70}")
    print("SAMPLE RESULTS")
    print(f"{'='*70}")
    display_cols = ['detection_id', 'src_ip', 'label', 'severity', 'blocked']
    print(results[display_cols].to_string(index=False))
