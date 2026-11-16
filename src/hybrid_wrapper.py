"""
HYBRID DETECTION WRAPPER
Provides single-sample prediction interface for manual detection.
Does NOT modify frozen hybrid_detector_final.py
"""

import joblib
import json
import numpy as np
import os

# Ensure paths work from any directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

RF_MODEL = None
IF_MODEL = None
RF_THRESHOLD = None
IF_THRESHOLD = None

def load_models():
    """Load frozen models and thresholds (once)"""
    global RF_MODEL, IF_MODEL, RF_THRESHOLD, IF_THRESHOLD
    
    if RF_MODEL is None:
        RF_MODEL = joblib.load(os.path.join(MODELS_DIR, "rf_model.pkl"))
        IF_MODEL = joblib.load(os.path.join(MODELS_DIR, "isolation_forest.pkl"))
        
        with open(os.path.join(MODELS_DIR, "rf_config.json")) as f:
            RF_THRESHOLD = json.load(f)["attack_threshold"]
        
        with open(os.path.join(MODELS_DIR, "if_config.json")) as f:
            IF_THRESHOLD = json.load(f)["anomaly_score_threshold"]
        
        assert RF_THRESHOLD == 0.40, "RF threshold mismatch"
        assert IF_THRESHOLD == 0.05, "IF threshold mismatch"

def hybrid_decision(rf_probability, if_score):
    """
    FROZEN HYBRID DECISION LOGIC (copied from hybrid_detector_final.py)
    
    Rules:
    - RF first
    - IF only applied if RF says Normal
    
    Args:
        rf_probability: Random Forest attack probability [0, 1]
        if_score: Isolation Forest anomaly score (lower = more anomalous)
    
    Returns:
        str: "Attack", "Suspicious", or "Normal"
    """
    if rf_probability >= RF_THRESHOLD:
        return "Attack"
    
    if if_score < IF_THRESHOLD:
        return "Suspicious"
    
    return "Normal"

def predict_single(X_scaled):
    """
    Run hybrid detection on single preprocessed sample
    
    Args:
        X_scaled: numpy array, shape (1, 142) - preprocessed & scaled features
    
    Returns:
        tuple: (label, p_attack, if_score)
    """
    load_models()
    
    rf_proba = RF_MODEL.predict_proba(X_scaled)[0, 1]
    if_score = IF_MODEL.decision_function(X_scaled)[0]
    
    label = hybrid_decision(rf_proba, if_score)
    
    return label, rf_proba, if_score
