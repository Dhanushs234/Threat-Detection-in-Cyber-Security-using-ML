import pandas as pd
import numpy as np
import pickle
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from preprocess import _select_stable_features, DERIVED_FEATURES

from STEP2_metadata_split import split_metadata_and_features
from STEP1_load_dataset import load_detection_dataset


def load_frozen_artifacts(models_dir):
    """
    Load all frozen preprocessing artifacts from training.
    
    CRITICAL: These artifacts are FROZEN and must NEVER be refitted.
    
    Args:
        models_dir (str): Path to models directory
        
    Returns:
        tuple: (medians, encoder, scaler)
    """
    print(f"\n{'='*60}")
    print("LOADING FROZEN PREPROCESSING ARTIFACTS")
    print(f"{'='*60}")
    
    medians_path = os.path.join(models_dir, 'medians.pkl')
    encoder_path = os.path.join(models_dir, 'encoder.pkl')
    scaler_path = os.path.join(models_dir, 'scaler.pkl')
    
    if not os.path.exists(medians_path):
        raise FileNotFoundError(f"Medians not found: {medians_path}")
    if not os.path.exists(encoder_path):
        raise FileNotFoundError(f"Encoder not found: {encoder_path}")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Scaler not found: {scaler_path}")
    
    with open(medians_path, 'rb') as f:
        medians = pickle.load(f)
    print(f"Loaded medians from: {medians_path}")
    print(f"   Median values for {len(medians)} features")
    
    with open(encoder_path, 'rb') as f:
        encoder = pickle.load(f)
    print(f"Loaded encoder from: {encoder_path}")
    print(f"   Encoder categories: {encoder.categories_}")
    
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    print(f"Loaded scaler from: {scaler_path}")
    print(f"   Scaler expects {len(scaler.mean_)} features")
    
    print(f"\n{'='*60}")
    print("CRITICAL: NO REFITTING WILL OCCUR")
    print(f"{'='*60}")
    print("- Medians will NOT be recomputed")
    print("- Encoder will NOT be refitted")
    print("- Scaler will NOT be refitted")
    print("Using EXACT same preprocessing as training\n")
    
    return medians, encoder, scaler


def preprocess_detection_features(features_df, medians, encoder, scaler):
    """
    Apply the SAME preprocessing pipeline used during training.
    
    Pipeline steps (EXACT ORDER):
    1. Feature derivation (12 derived features from 16 raw features)
    2. Median imputation (using FROZEN training medians)
    3. Protocol encoding (using FROZEN encoder)
    4. Scaling (using FROZEN scaler)
    
    CRITICAL: NO refitting occurs. All transformations use frozen artifacts.
    
    Args:
        features_df (pd.DataFrame): 16 raw UNSW features
        medians (pd.Series): FROZEN median values from training
        encoder (OneHotEncoder): FROZEN encoder from training
        scaler (StandardScaler): FROZEN scaler from training
        
    Returns:
        pd.DataFrame: Preprocessed features ready for model
    """
    print(f"\n{'='*60}")
    print("STEP 3: PREPROCESSING PIPELINE (SAME AS TRAINING)")
    print(f"{'='*60}")
    
    print(f"\nInput features shape: {features_df.shape}")
    print(f"Input columns: {list(features_df.columns)}")
    
    features_df = features_df.copy()
    if 'sintpkt' in features_df.columns and 'sinpkt' not in features_df.columns:
        features_df = features_df.rename(columns={'sintpkt': 'sinpkt', 'dintpkt': 'dinpkt'})
        print("Renamed sintpkt->sinpkt, dintpkt->dinpkt for compatibility")
    
    print(f"\n{'='*60}")
    print("STEP 3.1: FEATURE DERIVATION")
    print(f"{'='*60}")
    print("Deriving 12 features from 16 raw features...")
    
    X = _select_stable_features(features_df)
    
    print(f"Derived features shape: {X.shape}")
    print(f"Derived features: {list(X.columns)}")
    print(f"\nPreview:")
    print(X.head(3))
    
    print(f"\n{'='*60}")
    print("STEP 3.2: MEDIAN IMPUTATION (FROZEN MEDIANS)")
    print(f"{'='*60}")
    
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    
    missing_before = X[numeric_cols].isnull().sum().sum()
    print(f"Missing values before imputation: {missing_before}")
    
    X[numeric_cols] = X[numeric_cols].fillna(medians)
    
    missing_after = X[numeric_cols].isnull().sum().sum()
    print(f"Missing values after imputation: {missing_after}")
    print("Imputation complete using FROZEN training medians")
    
    X['Protocol'] = X['Protocol'].fillna('unknown').astype(str)
    
    print(f"\n{'='*60}")
    print("STEP 3.3: PROTOCOL ENCODING (FROZEN ENCODER)")
    print(f"{'='*60}")
    
    print(f"Unique protocols in detection data: {X['Protocol'].unique()}")
    
    protocol_encoded = encoder.transform(X[['Protocol']])
    
    protocol_feature_names = encoder.get_feature_names_out(['Protocol'])
    protocol_encoded_df = pd.DataFrame(
        protocol_encoded,
        columns=protocol_feature_names,
        index=X.index
    )
    
    print(f"Protocol encoded into {protocol_encoded_df.shape[1]} features")
    print(f"   Encoded columns: {list(protocol_encoded_df.columns)}")
    
    X = X.drop(columns=['Protocol'])
    X = pd.concat([X, protocol_encoded_df], axis=1)
    
    print(f"Features after encoding: {X.shape}")
    
    print(f"\n{'='*60}")
    print("STEP 3.4: SCALING (FROZEN SCALER)")
    print(f"{'='*60}")
    
    print(f"Features before scaling: {X.shape}")
    
    X_scaled = scaler.transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
    
    print(f"Features after scaling: {X_scaled.shape}")
    print(f"\nScaled features preview:")
    print(X_scaled.head(3))
    
    print(f"\n{'='*60}")
    print("PREPROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Final preprocessed shape: {X_scaled.shape}")
    print(f"Total features: {len(X_scaled.columns)}")
    print("Ready for model detection: YES")
    
    return X_scaled


if __name__ == "__main__":
    DATASET_PATH = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/data/cleaned_detection_input_with_ip_country.csv"
    MODELS_DIR = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/models"
    
    print("="*60)
    print("DETECTION PREPROCESSING PIPELINE")
    print("="*60)
    
    print("\n[1/4] Loading dataset...")
    dataset = load_detection_dataset(DATASET_PATH)
    
    print("\n[2/4] Splitting metadata and features...")
    metadata_df, features_df = split_metadata_and_features(dataset)
    
    print("\n[3/4] Loading frozen preprocessing artifacts...")
    medians, encoder, scaler = load_frozen_artifacts(MODELS_DIR)
    
    print("\n[4/4] Applying preprocessing pipeline...")
    preprocessed_features = preprocess_detection_features(
        features_df, 
        medians, 
        encoder, 
        scaler
    )
    
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Metadata (kept separate): {metadata_df.shape}")
    print(f"Preprocessed features: {preprocessed_features.shape}")
    print(f"Row alignment: {len(metadata_df)} == {len(preprocessed_features)}")
    print(f"\n✅ Ready for STEP 4: Row-by-row detection")
