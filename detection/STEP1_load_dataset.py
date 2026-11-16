import pandas as pd
import numpy as np
import os

def load_detection_dataset(csv_path):
    """
    STEP 1: Load the enriched CSV dataset for detection.
    
    This CSV contains:
    - 16 raw UNSW features (dur, spkts, dpkts, sbytes, dbytes, sload, dload, 
      sintpkt, dintpkt, sjit, djit, smean, dmean, synack, ackdat, proto)
    - Metadata columns (src_ip, dst_ip, src_country, dst_country)
    
    NO modifications are made to the data at this stage.
    NO feature engineering is performed here.
    
    Args:
        csv_path (str): Path to the cleaned detection input CSV
        
    Returns:
        pd.DataFrame: Loaded dataset with all columns intact
    """
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at: {csv_path}")
    
    print(f"Loading detection dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"\n{'='*60}")
    print("DATASET LOADED SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"Total rows: {len(df):,}")
    print(f"Total columns: {len(df.columns)}")
    print(f"\nColumns present:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\n{'='*60}")
    print("DATA PREVIEW (First 5 rows)")
    print(f"{'='*60}")
    print(df.head())
    
    print(f"\n{'='*60}")
    print("DATA TYPES")
    print(f"{'='*60}")
    print(df.dtypes)
    
    print(f"\n{'='*60}")
    print("MISSING VALUES CHECK")
    print(f"{'='*60}")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("No missing values detected.")
    
    print(f"\n{'='*60}")
    print("INFINITE VALUES CHECK")
    print(f"{'='*60}")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    inf_check = {}
    for col in numeric_cols:
        inf_count = np.isinf(df[col]).sum()
        if inf_count > 0:
            inf_check[col] = inf_count
    
    if inf_check:
        print("WARNING: Infinite values found:")
        for col, count in inf_check.items():
            print(f"  {col}: {count}")
    else:
        print("No infinite values detected.")
    
    print(f"\n{'='*60}")
    print("READY FOR STEP 2: METADATA SPLIT")
    print(f"{'='*60}\n")
    
    return df


if __name__ == "__main__":
    DATASET_PATH = "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/data/cleaned_detection_input_with_ip_country.csv"
    
    dataset = load_detection_dataset(DATASET_PATH)
    
    print(f"\nDataset shape: {dataset.shape}")
    print(f"Dataset loaded and ready for next step.")
