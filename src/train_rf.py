import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os
from preprocess import preprocess_training_data

def train_random_forest(X_train, y_train, model_path):
    print("\nTraining Random Forest classifier...")
    
    rf_model = RandomForestClassifier(
        n_estimators=300,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features="sqrt",
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
        verbose=1
    )
    
    rf_model.fit(X_train, y_train)
    
    print(f"\n✓ Training complete!")
    print(f"Number of trees: {rf_model.n_estimators}")
    print(f"Number of features: {rf_model.n_features_in_}")
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(rf_model, f)
    print(f"\nModel saved to {model_path}")
    
    return rf_model

if __name__ == "__main__":
    train_path = '../data/UNSW_NB15_training-set.csv'
    model_path = '../models/rf_model.pkl'
    output_dir = '../models'
    
    X_train, y_train, scaler, medians, encoder = preprocess_training_data(train_path, output_dir)
    
    rf_model = train_random_forest(X_train, y_train, model_path)
    
    train_accuracy = rf_model.score(X_train, y_train)
    print(f"\nTraining Accuracy: {train_accuracy:.4f}")
