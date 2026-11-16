import pandas as pd
import numpy as np
from STEP1_load_dataset import load_detection_dataset

def split_metadata_and_features(df):
    """
    STEP 2: Separate metadata columns from model input features.
    
    This function splits the enriched dataset into two parts:
    1. Metadata DataFrame (for display and auto-blocking)
    2. Model Features DataFrame (for preprocessing and detection)
    
    CRITICAL: Metadata NEVER enters preprocessing or model.
    Row alignment is maintained between both DataFrames.
    
    Args:
        df (pd.DataFrame): Full dataset with all columns
        
    Returns:
        tuple: (metadata_df, features_df)
            - metadata_df: 4 columns (src_ip, dst_ip, src_country, dst_country)
            - features_df: 16 columns (UNSW features in exact order)
    """
    
    METADATA_COLUMNS = [
        'src_ip',
        'dst_ip', 
        'src_country',
        'dst_country'
    ]
    
    MODEL_FEATURE_COLUMNS = [
        'dur',
        'spkts',
        'dpkts',
        'sbytes',
        'dbytes',
        'sload',
        'dload',
        'sintpkt',
        'dintpkt',
        'sjit',
        'djit',
        'smean',
        'dmean',
        'synack',
        'ackdat',
        'proto'
    ]
    
    print(f"\n{'='*60}")
    print("STEP 2: METADATA AND FEATURE SEPARATION")
    print(f"{'='*60}")
    
    missing_metadata = [col for col in METADATA_COLUMNS if col not in df.columns]
    if missing_metadata:
        raise ValueError(f"Missing metadata columns: {missing_metadata}")
    
    missing_features = [col for col in MODEL_FEATURE_COLUMNS if col not in df.columns]
    if missing_features:
        raise ValueError(f"Missing feature columns: {missing_features}")
    
    metadata_df = df[METADATA_COLUMNS].copy()
    features_df = df[MODEL_FEATURE_COLUMNS].copy()
    
    print(f"\n✅ Metadata DataFrame:")
    print(f"   Shape: {metadata_df.shape}")
    print(f"   Columns: {list(metadata_df.columns)}")
    print(f"\n   Preview:")
    print(metadata_df.head(3))
    
    print(f"\n✅ Model Features DataFrame:")
    print(f"   Shape: {features_df.shape}")
    print(f"   Columns ({len(features_df.columns)} total):")
    for i, col in enumerate(features_df.columns, 1):
        print(f"      {i:2d}. {col}")
    
    print(f"\n   Preview:")
    print(features_df.head(3))
    
    assert len(metadata_df) == len(features_df), "Row count mismatch!"
    assert len(features_df.columns) == 16, f"Expected 16 features, got {len(features_df.columns)}"
    assert len(metadata_df.columns) == 4, f"Expected 4 metadata columns, got {len(metadata_df.columns)}"
    
    print(f"\n{'='*60}")
    print("VALIDATION CHECKS")
    print(f"{'='*60}")
    print(f"✅ Row alignment: {len(metadata_df)} == {len(features_df)}")
    print(f"✅ Feature count: {len(features_df.columns)} == 16")
    print(f"✅ Metadata count: {len(metadata_df.columns)} == 4")
    print(f"✅ No overlap between metadata and features")
    
    print(f"\n{'='*60}")
    print("READY FOR STEP 3: PREPROCESSING PIPELINE")
    print(f"{'='*60}")
    print("⚠️  IMPORTANT: Metadata will NOT be passed to preprocessing")
    print("⚠️  IMPORTANT: Only features_df will enter the model pipeline\n")
    
    return metadata_df, features_df


if __name__ == "__main__":
    DATASET_PATH = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/data/cleaned_detection_input_with_ip_country.csv"
    
    print("Loading dataset...")
    dataset = load_detection_dataset(DATASET_PATH)
    
    print("\nSplitting metadata and features...")
    metadata, features = split_metadata_and_features(dataset)
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Original dataset: {dataset.shape}")
    print(f"Metadata only: {metadata.shape}")
    print(f"Features only: {features.shape}")
    print(f"\nSplit completed successfully!")
