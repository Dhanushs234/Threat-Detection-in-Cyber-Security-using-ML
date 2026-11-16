"""
SINGLE-ROW DETECTION - USER INPUT MODE

INPUT: 16 raw features (user-typed)
OUTPUT: Timestamp, Label, Hybrid confidence, Risk score

RULES:
Input = 16 raw features (user-typed)
12 features are internal only (derived by preprocessing)
Same preprocessing reused
Output exactly as specified
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from hybrid_wrapper import predict_single, load_models
from hybrid_output_layer import compute_confidence_risk_severity
from STEP3_preprocessing import load_frozen_artifacts, preprocess_detection_features


REQUIRED_FEATURES = [
    'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 
    'sload', 'dload', 'sinpkt', 'dinpkt', 'sjit', 
    'djit', 'smean', 'dmean', 'synack', 'ackdat', 'proto'
]

NUMERIC_FEATURES = [
    'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes',
    'sload', 'dload', 'sinpkt', 'dinpkt', 'sjit',
    'djit', 'smean', 'dmean', 'synack', 'ackdat'
]


def validate_input(user_input):
    """
    Validate user input contains exactly 16 raw features.
    
    Args:
        user_input (dict): User-provided feature values
        
    Returns:
        tuple: (is_valid, error_message)
    """
    missing_fields = [field for field in REQUIRED_FEATURES if field not in user_input]
    if missing_fields:
        return False, f"Missing required fields: {missing_fields}"
    
    extra_fields = [field for field in user_input.keys() if field not in REQUIRED_FEATURES]
    if extra_fields:
        return False, f"Extra fields not allowed: {extra_fields}"
    
    for field in NUMERIC_FEATURES:
        try:
            float(user_input[field])
        except (ValueError, TypeError):
            return False, f"Field '{field}' must be numeric, got: {user_input[field]}"
    
    if not isinstance(user_input['proto'], str):
        return False, f"Field 'proto' must be a string, got: {type(user_input['proto'])}"
    
    return True, None


def detect_single_row(user_input, models_dir):
    """
    Perform detection on single user-entered row.
    
    PIPELINE:
    1. Accept user-typed input (16 raw features)
    2. Validate all 16 fields are provided
    3. Apply preprocessing (derives 12 features internally)
    4. Run hybrid model inference
    5. Pass to output layer
    6. Display: Timestamp, Label, Confidence, Risk
    
    Args:
        user_input (dict): 16 raw features from user
        models_dir (str): Path to models directory
        
    Returns:
        dict: Detection results
    """
    is_valid, error_msg = validate_input(user_input)
    if not is_valid:
        raise ValueError(f"Input validation failed: {error_msg}")
    
    print(f"\n{'='*70}")
    print("SINGLE-ROW DETECTION")
    print(f"{'='*70}")
    
    print("\n[1/4] Loading frozen preprocessing artifacts...")
    medians, encoder, scaler = load_frozen_artifacts(models_dir)
    
    print("\n[2/4] Loading frozen hybrid models...")
    load_models()
    
    print("\n[3/4] Preprocessing input (16 raw features -> 142 features)...")
    features_df = pd.DataFrame([user_input])
    
    if 'sintpkt' in features_df.columns and 'sinpkt' not in features_df.columns:
        features_df = features_df.rename(columns={'sintpkt': 'sinpkt', 'dintpkt': 'dinpkt'})
    
    preprocessed = preprocess_detection_features(features_df, medians, encoder, scaler)
    
    print("\n[4/4] Running hybrid model detection...")
    X_scaled = preprocessed.values
    label, rf_prob, if_score = predict_single(X_scaled)
    confidence, risk, severity = compute_confidence_risk_severity(label, rf_prob, if_score)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"\n{'='*70}")
    print("DETECTION OUTPUT")
    print(f"{'='*70}")
    print(f"Timestamp:         {timestamp}")
    print(f"Label:             {label}")
    print(f"Hybrid confidence: {confidence}%")
    print(f"Risk score:        {risk}%")
    print(f"{'='*70}\n")
    
    return {
        'timestamp': timestamp,
        'label': label,
        'confidence': confidence,
        'risk': risk
    }


def prompt_user_input():
    """Prompt the user to enter all 16 raw feature values."""
    user_input = {}
    print("Please enter values for the 16 required raw features:\n")
    for field in REQUIRED_FEATURES:
        while True:
            value = input(f"{field}: ").strip()
            if field in NUMERIC_FEATURES:
                try:
                    user_input[field] = float(value)
                    break
                except ValueError:
                    print(f"Invalid numeric value for '{field}'. Please try again.")
            else:
                if not value:
                    print(f"Field '{field}' cannot be empty. Please enter a protocol string.")
                else:
                    user_input[field] = value
                    break
    return user_input


if __name__ == "__main__":
    MODELS_DIR = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/models"
    
    print("="*70)
    print("SINGLE-ROW DETECTION - USER INPUT MODE")
    print("="*70)
    print("\nINPUT: 16 raw features (user-typed)")
    print("OUTPUT: Timestamp, Label, Hybrid confidence, Risk score\n")
    
    user_input = prompt_user_input()
    result = detect_single_row(user_input, MODELS_DIR)
    
    print("\nResult dictionary:")
    print(result)
