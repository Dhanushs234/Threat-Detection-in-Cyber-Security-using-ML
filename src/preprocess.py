import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import pickle
import os

DERIVED_FEATURES = [
    'Flow Duration',
    'Flow Packets/s',
    'Flow Bytes/s',
    'Flow IAT Mean',
    'Flow IAT Std',
    'Total Forward Bytes',
    'Total Backward Bytes',
    'Fwd Packet Length Mean',
    'Bwd Packet Length Mean',
    'SYN Flag Count',
    'ACK Flag Count',
    'Protocol'
]

SOURCE_COLUMN_REQUIREMENTS = [
    'dur',
    'spkts',
    'dpkts',
    'sbytes',
    'dbytes',
    'sload',
    'dload',
    'sinpkt',
    'dinpkt',
    'sjit',
    'djit',
    'smean',
    'dmean',
    'synack',
    'ackdat',
    'proto'
]

def _select_stable_features(df: pd.DataFrame) -> pd.DataFrame:
    missing_sources = [col for col in SOURCE_COLUMN_REQUIREMENTS if col not in df.columns]
    if missing_sources:
        raise ValueError(f"Missing required base columns: {missing_sources}")
    
    duration = df['dur'].replace(0, np.nan)
    flow_packets_per_s = (df['spkts'] + df['dpkts']) / duration
    flow_bytes_per_s = (df['sbytes'] + df['dbytes']) / duration
    flow_iat_mean = (df['sinpkt'] + df['dinpkt']) / 2
    flow_iat_std = (df['sjit'] + df['djit']) / 2
    
    features = pd.DataFrame({
        'Flow Duration': df['dur'],
        'Flow Packets/s': flow_packets_per_s,
        'Flow Bytes/s': flow_bytes_per_s,
        'Flow IAT Mean': flow_iat_mean,
        'Flow IAT Std': flow_iat_std,
        'Total Forward Bytes': df['sbytes'],
        'Total Backward Bytes': df['dbytes'],
        'Fwd Packet Length Mean': df['smean'],
        'Bwd Packet Length Mean': df['dmean'],
        'SYN Flag Count': df['synack'],
        'ACK Flag Count': df['ackdat'],
        'Protocol': df['proto'].astype(str)
    }, index=df.index)
    
    features = features[DERIVED_FEATURES]
    features = features.replace([np.inf, -np.inf], np.nan)
    return features

def clean_data(df, is_training=True, medians=None, encoder=None):
    df = df.copy()
    
    columns_to_remove = ['id', 'attack_cat']
    existing_columns_to_remove = [col for col in columns_to_remove if col in df.columns]
    df = df.drop(columns=existing_columns_to_remove)
    
    if 'label' not in df.columns:
        raise ValueError("'label' column not found in dataset")
    
    y = df['label'].copy()
    X = _select_stable_features(df)
    
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    
    if is_training:
        medians = X[numeric_cols].median()
    elif medians is None:
        raise ValueError("Medians must be provided for test data cleaning")
    
    X[numeric_cols] = X[numeric_cols].fillna(medians)
    X['Protocol'] = X['Protocol'].fillna('unknown').astype(str)
    
    if is_training:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        protocol_encoded = encoder.fit_transform(X[['Protocol']])
    elif encoder is not None:
        protocol_encoded = encoder.transform(X[['Protocol']])
    else:
        raise ValueError("Encoder must be provided for test data cleaning")
    
    protocol_feature_names = encoder.get_feature_names_out(['Protocol'])
    protocol_encoded_df = pd.DataFrame(
        protocol_encoded,
        columns=protocol_feature_names,
        index=X.index
    )
    
    X = X.drop(columns=['Protocol'])
    X = pd.concat([X, protocol_encoded_df], axis=1)
    
    if is_training:
        return X, y, medians, encoder
    return X, y

def preprocess_training_data(train_path, output_dir):
    print("Loading training data...")
    train_df = pd.read_csv(train_path)
    
    print(f"Training data shape: {train_df.shape}")
    print(f"Training data columns: {train_df.columns.tolist()}")
    
    print("\nCleaning training data...")
    X_train_clean, y_train, medians, encoder = clean_data(train_df, is_training=True)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_clean)
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train_clean.columns, index=X_train_clean.index)
    
    print(f"Cleaned training features shape: {X_train_scaled.shape}")
    print(f"Training labels shape: {y_train.shape}")
    print(f"Label distribution:\n{y_train.value_counts()}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    scaler_path = os.path.join(output_dir, 'scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"\nScaler saved to {scaler_path}")
    
    medians_path = os.path.join(output_dir, 'medians.pkl')
    with open(medians_path, 'wb') as f:
        pickle.dump(medians, f)
    print(f"Medians saved to {medians_path}")
    
    encoder_path = os.path.join(output_dir, 'encoder.pkl')
    with open(encoder_path, 'wb') as f:
        pickle.dump(encoder, f)
    print(f"Encoder saved to {encoder_path}")
    
    return X_train_scaled, y_train, scaler, medians, encoder

def preprocess_testing_data(test_path, scaler, medians, encoder):
    print("\nLoading testing data...")
    test_df = pd.read_csv(test_path)
    
    print(f"Testing data shape: {test_df.shape}")
    
    print("Cleaning testing data...")
    X_test_clean, y_test = clean_data(test_df, is_training=False, medians=medians, encoder=encoder)
    
    X_test_scaled = scaler.transform(X_test_clean)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test_clean.columns, index=X_test_clean.index)
    
    print(f"Cleaned testing features shape: {X_test_scaled.shape}")
    print(f"Testing labels shape: {y_test.shape}")
    print(f"Label distribution:\n{y_test.value_counts()}")
    
    return X_test_scaled, y_test

if __name__ == "__main__":
    train_path = '../data/UNSW_NB15_training-set.csv'
    test_path = '../data/UNSW_NB15_testing-set.csv'
    output_dir = '../models'
    
    X_train, y_train, scaler, medians, encoder = preprocess_training_data(train_path, output_dir)
    X_test, y_test = preprocess_testing_data(test_path, scaler, medians, encoder)
    
    print("\n✓ Preprocessing complete!")
