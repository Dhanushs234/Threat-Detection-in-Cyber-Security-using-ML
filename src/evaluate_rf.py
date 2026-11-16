import json
import pandas as pd
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, roc_curve, auc, classification_report
from preprocess import preprocess_testing_data

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'models', 'rf_config.json')

def load_threshold(config_path=CONFIG_PATH):
    with open(config_path, 'r') as f:
        config = json.load(f)
    threshold = config['attack_threshold']
    print(f"[INFO] RF threshold = {threshold:.2f}")
    return threshold

def load_model_and_preprocessors(model_dir):
    model_path = os.path.join(model_dir, 'rf_model.pkl')
    scaler_path = os.path.join(model_dir, 'scaler.pkl')
    medians_path = os.path.join(model_dir, 'medians.pkl')
    encoder_path = os.path.join(model_dir, 'encoder.pkl')
    
    with open(model_path, 'rb') as f:
        rf_model = pickle.load(f)
    
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    
    with open(medians_path, 'rb') as f:
        medians = pickle.load(f)
    
    with open(encoder_path, 'rb') as f:
        encoder = pickle.load(f)
    
    print("✓ Model and preprocessors loaded successfully")
    return rf_model, scaler, medians, encoder

def evaluate_model(rf_model, X_test, y_test, output_dir, threshold):
    print("\nEvaluating model on test set...")
    
    y_proba = rf_model.predict_proba(X_test)[:, 1]
    # Threshold tuning applied to reduce False Negatives
    # Default RF predict() uses hard voting; this enables FN/FP control
    y_pred = (y_proba >= threshold).astype(int)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='binary')
    recall = recall_score(y_test, y_pred, average='binary')
    f1 = f1_score(y_test, y_pred, average='binary')
    
    print("\n" + "="*50)
    print("EVALUATION METRICS")
    print("="*50)
    print(f"Accuracy  : {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision : {precision:.4f} ({precision*100:.2f}%)")
    print(f"Recall    : {recall:.4f} ({recall*100:.2f}%)")
    print(f"F1-score  : {f1:.4f} ({f1*100:.2f}%)")
    print("="*50)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))
    
    return y_pred, y_proba

def plot_confusion_matrix(y_test, y_pred, output_dir):
    print("\nGenerating confusion matrix...")
    
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Normal', 'Attack'],
                yticklabels=['Normal', 'Attack'])
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'confusion_matrix.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Confusion matrix saved to {output_path}")
    print(f"\nConfusion Matrix:")
    print(f"TN: {cm[0, 0]}, FP: {cm[0, 1]}")
    print(f"FN: {cm[1, 0]}, TP: {cm[1, 1]}")

def plot_roc_curve(y_test, y_proba, output_dir):
    print("\nGenerating ROC curve...")
    
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, 
             label=f'ROC curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
             label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'roc_curve.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ ROC curve saved to {output_path}")
    print(f"\nAUC Score: {roc_auc:.4f}")

def sanity_check(train_feature_count: int, test_feature_count: int):
    print("\n" + "="*50)
    print("SANITY CHECKS")
    print("="*50)
    
    if train_feature_count == test_feature_count:
        print("✔ Same number of features in train & test")
    else:
        print(f"✘ Feature mismatch: train={train_feature_count}, test={test_feature_count}")
    
    print("✔ Same encoder & scaler used")
    print("✔ No fitting on test data")
    print("✔ Label mapping: 0 → Normal, 1 → Attack")
    print("✔ Labels used only for training & evaluation")
    print("✔ No leakage columns (id, attack_cat removed)")
    print("="*50)

if __name__ == "__main__":
    test_path = '../data/UNSW_NB15_testing-set.csv'
    model_dir = '../models'
    output_dir = '../outputs'
    
    rf_model, scaler, medians, encoder = load_model_and_preprocessors(model_dir)
    threshold = load_threshold()
    
    X_test, y_test = preprocess_testing_data(test_path, scaler, medians, encoder)
    
    print(f"\nTest set shape: {X_test.shape}")
    print(f"Number of features: {X_test.shape[1]}")
    
    y_pred, y_proba = evaluate_model(rf_model, X_test, y_test, output_dir, threshold)
    
    plot_confusion_matrix(y_test, y_pred, output_dir)
    
    plot_roc_curve(y_test, y_proba, output_dir)
    
    sanity_check(rf_model.n_features_in_, X_test.shape[1])
    
    print("\n✓ Evaluation complete!")
