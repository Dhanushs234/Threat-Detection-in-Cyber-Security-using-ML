"""
DETECTION WRAPPER - ORCHESTRATION ONLY

Wraps existing detection pipeline without modifying ML code.

RULES:
- Uses existing single_row_detection.py logic
- Uses existing STEP9_complete_pipeline.py for data loading
- NO modifications to preprocessing, models, or formulas
- Only orchestrates and formats results
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
from typing import Dict, Tuple

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))

sys.path.append(os.path.join(PROJECT_ROOT, 'src'))
sys.path.append(os.path.join(PROJECT_ROOT, 'detection'))

from hybrid_wrapper import predict_single, load_models
from hybrid_output_layer import compute_confidence_risk_severity
from STEP3_preprocessing import load_frozen_artifacts, preprocess_detection_features


MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
DATASET_PATH = os.path.join(PROJECT_ROOT, 'data', 'cleaned_detection_input_with_ip_country.csv')

REQUIRED_FEATURES = [
    'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 
    'sload', 'dload', 'sinpkt', 'dinpkt', 'sjit', 
    'djit', 'smean', 'dmean', 'synack', 'ackdat', 'proto'
]

METADATA_COLUMNS = ['src_ip', 'dst_ip', 'src_country', 'dst_country']

# Global artifacts (loaded once)
_artifacts_loaded = False
_medians = None
_encoder = None
_scaler = None


def load_artifacts_once():
    """Load frozen artifacts once and cache them"""
    global _artifacts_loaded, _medians, _encoder, _scaler
    
    if not _artifacts_loaded:
        _medians, _encoder, _scaler = load_frozen_artifacts(MODELS_DIR)
        load_models()
        _artifacts_loaded = True


def generate_detection_id(counter: int) -> str:
    """Generate system detection ID"""
    return f"DET-{counter:06d}"


def get_threat_color(label: str) -> str:
    """
    Get color for threat map based on label.
    
    FIXED RULES:
    - attack → red
    - suspicious → orange
    - normal → blue
    """
    label_lower = label.lower()
    if label_lower == 'attack':
        return 'red'
    elif label_lower == 'suspicious':
        return 'orange'
    else:
        return 'blue'


def detect_single_row_with_metadata(
    row_data: Dict,
    metadata: Dict,
    detection_id: str
) -> Dict:
    """
    Run detection on a single row with metadata.
    
    Args:
        row_data: 16 raw features
        metadata: src_ip, dst_ip, src_country, dst_country
        detection_id: System-generated detection ID
        
    Returns:
        dict: Complete detection result
    """
    load_artifacts_once()
    
    # Create DataFrame with 16 raw features
    features_df = pd.DataFrame([row_data])
    
    # Fix column naming if needed
    if 'sintpkt' in features_df.columns and 'sinpkt' not in features_df.columns:
        features_df = features_df.rename(columns={'sintpkt': 'sinpkt', 'dintpkt': 'dinpkt'})
    
    # Preprocess: 16 raw → 142 scaled features
    preprocessed = preprocess_detection_features(features_df, _medians, _encoder, _scaler)
    
    # Hybrid model inference
    X_scaled = preprocessed.values
    label, rf_prob, if_score = predict_single(X_scaled)
    
    # Output layer
    confidence, risk, severity = compute_confidence_risk_severity(label, rf_prob, if_score)
    
    # Build result
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        'timestamp': timestamp,
        'detection_id': detection_id,
        'src_ip': metadata['src_ip'],
        'src_country': metadata['src_country'],
        'dst_ip': metadata['dst_ip'],
        'dst_country': metadata['dst_country'],
        'label': label,
        'severity': severity,
        'hybrid_confidence': confidence,
        'risk_score': risk
    }


def detect_manual_input(user_input: Dict) -> Dict:
    """
    Run detection on manual user input (16 raw features only).
    
    Args:
        user_input: 16 raw features from user
        
    Returns:
        dict: Detection result (timestamp, label, severity, confidence, risk)
    """
    load_artifacts_once()
    
    # Validate input
    missing_fields = [field for field in REQUIRED_FEATURES if field not in user_input]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")
    
    # Create DataFrame
    features_df = pd.DataFrame([user_input])
    
    # Fix column naming if needed
    if 'sintpkt' in features_df.columns and 'sinpkt' not in features_df.columns:
        features_df = features_df.rename(columns={'sintpkt': 'sinpkt', 'dintpkt': 'dinpkt'})
    
    # Preprocess
    preprocessed = preprocess_detection_features(features_df, _medians, _encoder, _scaler)
    
    # Hybrid model inference
    X_scaled = preprocessed.values
    label, rf_prob, if_score = predict_single(X_scaled)
    
    # Output layer
    confidence, risk, severity = compute_confidence_risk_severity(label, rf_prob, if_score)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        'timestamp': timestamp,
        'label': label,
        'severity': severity,
        'hybrid_confidence': confidence,
        'risk_score': risk
    }


class DatasetIterator:
    """
    Iterator for dataset rows with metadata separation.
    
    RULES:
    - Metadata never enters preprocessing
    - Row-by-row iteration
    - Maintains alignment
    """
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.df = None
        self.current_index = 0
        self.total_rows = 0
        self._load_dataset()
    
    def _load_dataset(self):
        """Load dataset and separate metadata"""
        self.df = pd.read_csv(self.dataset_path)
        self.total_rows = len(self.df)
        
        # Verify columns
        for col in METADATA_COLUMNS:
            if col not in self.df.columns:
                raise ValueError(f"Missing metadata column: {col}")
        
        for col in REQUIRED_FEATURES:
            if col not in self.df.columns:
                # Check for naming mismatch
                if col == 'sinpkt' and 'sintpkt' in self.df.columns:
                    continue
                if col == 'dinpkt' and 'dintpkt' in self.df.columns:
                    continue
                raise ValueError(f"Missing feature column: {col}")
    
    def has_next(self) -> bool:
        """Check if more rows available"""
        return self.current_index < self.total_rows
    
    def get_next(self) -> Tuple[Dict, Dict]:
        """
        Get next row as (features, metadata).
        
        Returns:
            tuple: (feature_dict, metadata_dict)
        """
        if not self.has_next():
            raise StopIteration("No more rows")
        
        row = self.df.iloc[self.current_index]
        
        # Extract metadata
        metadata = {col: row[col] for col in METADATA_COLUMNS}
        
        # Extract features (handle naming mismatch)
        features = {}
        for col in REQUIRED_FEATURES:
            if col == 'sinpkt' and 'sintpkt' in self.df.columns:
                features[col] = row['sintpkt']
            elif col == 'dinpkt' and 'dintpkt' in self.df.columns:
                features[col] = row['dintpkt']
            else:
                features[col] = row[col]
        
        self.current_index += 1
        
        return features, metadata
    
    def reset(self):
        """Reset iterator to beginning"""
        self.current_index = 0
