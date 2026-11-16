"""
CONTINUOUS DETECTION MODE - TERMINAL ONLY

OBJECTIVE:
Run row-by-row detection continuously in terminal until user manually stops it (Ctrl + C)
with strict 7-second delay.

RULES:
✅ ONLY remove sample limit and run continuously
❌ Do NOT change preprocessing
❌ Do NOT change models
❌ Do NOT add backend / FastAPI
❌ Do NOT change thresholds
❌ Do NOT change output logic
❌ Do NOT change metadata handling
❌ Do NOT change KPI calculations

STOP MECHANISM: Ctrl + C only
"""

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
        """Add IP to blocked list."""
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
    
    def get_blocked_count(self):
        """Get total number of blocked IPs."""
        return len(self.blocked_ips)


def generate_detection_id(counter):
    """Generate system-generated detection ID."""
    return f"DET-{counter:06d}"


def display_auto_block(src_ip):
    """Display auto-block message immediately."""
    print(f"\n{'🚨'*35}")
    print(f"⛔ AUTO-BLOCKED IP: {src_ip}")
    print(f"📋 REASON: Attack detected")
    print(f"{'🚨'*35}\n")


def display_detection_output(detection_id, timestamp, metadata, detection_result, blocked=False):
    """Display detection output with optional block indicator."""
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


def continuous_detection(dataset_path, models_dir, delay_seconds=7):
    """
    CONTINUOUS DETECTION MODE - Run until Ctrl+C
    
    Runs row-by-row detection continuously with strict 7-second delay.
    Stops only when user presses Ctrl+C.
    
    Args:
        dataset_path (str): Path to detection CSV
        models_dir (str): Path to models directory
        delay_seconds (int): Delay between detections (default: 7, STRICT)
    """
    print(f"\n{'='*70}")
    print("CONTINUOUS DETECTION MODE - TERMINAL ONLY")
    print(f"{'='*70}")
    print(f"\n⚠️  Detection will run continuously until you press Ctrl+C")
    print(f"⚠️  Strict 7-second delay between each detection")
    print(f"⚠️  Press Ctrl+C to stop gracefully\n")
    
    print("[1/5] Loading dataset...")
    dataset = load_detection_dataset(dataset_path)
    
    print("\n[2/5] Splitting metadata and features...")
    metadata_df, features_df = split_metadata_and_features(dataset)
    total_rows = len(features_df)
    print(f"   Total rows available: {total_rows}")
    
    print("\n[3/5] Loading frozen preprocessing artifacts...")
    medians, encoder, scaler = load_frozen_artifacts(models_dir)
    
    print("\n[4/5] Loading frozen hybrid models...")
    load_models()
    print("   ✅ Hybrid models loaded (RF + IF)")
    
    print("\n[5/5] Initializing blocked IP manager...")
    blocked_ip_manager = BlockedIPManager()
    print("   ✅ Blocked IP manager ready")
    
    print(f"\n{'='*70}")
    print("STARTING CONTINUOUS DETECTION")
    print(f"{'='*70}")
    print(f"Press Ctrl+C to stop\n")
    
    row_index = 0
    detection_counter = 1
    
    normal_count = 0
    suspicious_count = 0
    attack_count = 0
    
    start_time = datetime.now()
    
    try:
        while True:
            if row_index >= total_rows:
                print(f"\n{'='*70}")
                print("DATASET END REACHED")
                print(f"{'='*70}")
                print(f"All {total_rows} rows processed. Stopping automatically.")
                break
            
            print(f"\n{'▼'*70}")
            print(f"PROCESSING ROW {row_index + 1}/{total_rows}")
            print(f"{'▼'*70}")
            
            detection_id = generate_detection_id(detection_counter)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            features_row = features_df.iloc[row_index:row_index+1]
            metadata_row = metadata_df.iloc[row_index]
            
            preprocessed = preprocess_detection_features(features_row, medians, encoder, scaler)
            
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
                attack_count += 1
            elif label == "Normal":
                normal_count += 1
            elif label == "Suspicious":
                suspicious_count += 1
            
            display_detection_output(detection_id, timestamp, metadata_row, detection_result, blocked)
            
            row_index += 1
            detection_counter += 1
            
            if row_index < total_rows:
                print(f"⏳ Waiting {delay_seconds} seconds before next detection...")
                time.sleep(delay_seconds)
    
    except KeyboardInterrupt:
        print(f"\n\n{'='*70}")
        print("⚠️  CTRL+C DETECTED - GRACEFUL SHUTDOWN")
        print(f"{'='*70}")
    
    end_time = datetime.now()
    total_elapsed = (end_time - start_time).total_seconds()
    total_detections = detection_counter - 1
    
    print(f"\n{'='*70}")
    print("FINAL SHUTDOWN STATISTICS")
    print(f"{'='*70}")
    print(f"Total detections processed: {total_detections}")
    print(f"Total elapsed time: {total_elapsed:.2f}s ({total_elapsed/60:.2f} minutes)")
    if total_detections > 0:
        print(f"Average time per detection: {total_elapsed/total_detections:.2f}s")
    
    print(f"\n{'='*70}")
    print("LABEL DISTRIBUTION")
    print(f"{'='*70}")
    print(f"Normal:      {normal_count}")
    print(f"Suspicious:  {suspicious_count}")
    print(f"Attack:      {attack_count}")
    
    print(f"\n{'='*70}")
    print("AUTO-BLOCK SUMMARY")
    print(f"{'='*70}")
    print(f"IPs blocked: {blocked_ip_manager.get_blocked_count()}")
    
    print(f"\n{'='*70}")
    print("SHUTDOWN COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    DATASET_PATH = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/data/cleaned_detection_input_with_ip_country.csv"
    MODELS_DIR = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/models"
    
    print("="*70)
    print("CONTINUOUS DETECTION - TERMINAL MODE")
    print("="*70)
    print("\n🎯 ONE-LINE SUMMARY:")
    print("   'Convert the detection loop to run continuously row-by-row")
    print("    with a 7-second delay until interrupted by Ctrl+C.")
    print("    Do not change any other logic.'\n")
    
    continuous_detection(
        dataset_path=DATASET_PATH,
        models_dir=MODELS_DIR,
        delay_seconds=7
    )
