# 🔒 FROZEN ARTIFACTS - DO NOT MODIFY

This document lists all frozen artifacts that **MUST NOT be retrained, refitted, or modified** after initial training.

---

## ✅ MANDATORY FROZEN ARTIFACTS

### 1️⃣ Random Forest (Supervised Learning)

| Artifact | Path | Purpose | Status |
|----------|------|---------|--------|
| **RF Model** | `models/rf_model.pkl` | Learned attack patterns | ✅ FROZEN |
| **Feature Columns** | `models/feature_columns.pkl` | Feature order (142 features) | ✅ FROZEN |
| **Scaler** | `models/scaler.pkl` | StandardScaler for normalization | ✅ FROZEN |
| **Medians** | `models/medians.pkl` | Imputation values for missing data | ✅ FROZEN |
| **Encoder** | `models/encoder.pkl` | OneHotEncoder for categorical features | ✅ FROZEN |
| **RF Threshold** | `models/rf_config.json` | Attack probability threshold (0.40) | ✅ FROZEN |

### 2️⃣ Isolation Forest (Unsupervised Anomaly Detection)

| Artifact | Path | Purpose | Status |
|----------|------|---------|--------|
| **IF Model** | `models/isolation_forest.pkl` | Learned normal behavior | ✅ FROZEN |
| **IF Threshold** | `models/if_config.json` | Anomaly score threshold (0.05) | ✅ FROZEN |

---

## 🚨 CRITICAL RULES

### ❌ NEVER DO THIS:
- ❌ Retrain RF model
- ❌ Retrain Isolation Forest model
- ❌ Refit scaler on new data
- ❌ Recompute medians
- ❌ Refit encoder
- ❌ Change feature order
- ❌ Modify thresholds without updating config files
- ❌ Store thresholds inside `.pkl` files

### ✅ ALWAYS DO THIS:
- ✅ Load frozen artifacts for all predictions
- ✅ Transform new data using frozen scaler
- ✅ Use frozen feature order
- ✅ Load thresholds from config files
- ✅ Apply frozen preprocessing pipeline

---

## 📋 CONFIG FILE STRUCTURE

### `models/rf_config.json`
```json
{
  "attack_threshold": 0.40
}
```

### `models/if_config.json`
```json
{
  "anomaly_score_threshold": 0.05
}
```

---

## 🔍 HOW TO LOAD IN DETECTION SCRIPTS

### Random Forest Threshold
```python
import json

with open("models/rf_config.json") as f:
    RF_THRESHOLD = json.load(f)["attack_threshold"]
print(f"[INFO] RF threshold = {RF_THRESHOLD}")
```

### Isolation Forest Threshold
```python
import json

with open("models/if_config.json") as f:
    IF_THRESHOLD = json.load(f)["anomaly_score_threshold"]
print(f"[INFO] IF anomaly threshold = {IF_THRESHOLD}")
```

---

## 🧠 WHY FREEZING IS MANDATORY

| If You Don't Freeze | Consequence |
|---------------------|-------------|
| Scaler changes | Detection confidence collapses |
| Feature order changes | Silent misclassification |
| Threshold changes | Inconsistent results across runs |
| IF retrained | Anomaly detection logic breaks |
| Medians recomputed | Preprocessing mismatch |

**Freezing = Scientific Validity + Production Safety**

---

## 📊 ARTIFACT VERIFICATION

Run this to verify all frozen artifacts exist:

```bash
ls -lh models/rf_model.pkl
ls -lh models/isolation_forest.pkl
ls -lh models/feature_columns.pkl
ls -lh models/scaler.pkl
ls -lh models/medians.pkl
ls -lh models/encoder.pkl
ls -lh models/rf_config.json
ls -lh models/if_config.json
```

Expected output: All files present with non-zero size.

---

## 🔐 FREEZE DATE

**Frozen on:** December 23, 2025

**Training Data:**
- Dataset: UNSW-NB15
- Training samples: 82,332 (37,000 normal, 45,332 attack)
- Testing samples: Available in `data/UNSW_NB15_testing-set.csv`

**Model Performance:**
- RF Detection Rate: ~95% (with threshold=0.40)
- IF Detection Rate: 33.5% (with threshold=0.05)
- Combined system ready for hybrid ensemble

---

## ⚠️ WHAT CAN CHANGE

These are **NOT frozen** and can be modified:
- Training scripts (`src/train_rf.py`, `src/train_isolation_forest.py`)
- Evaluation scripts (`src/evaluate_rf.py`, `src/test_isolation_forest.py`)
- Visualization scripts
- Test subsets
- Output reports

---

## 🔒 FINAL WARNING

**DO NOT TOUCH FROZEN ARTIFACTS UNLESS:**
1. You have a new dataset and need to retrain from scratch
2. You are explicitly instructed to retrain
3. You discover a critical bug in preprocessing

In all cases, document the change and update this file.

---

*This freeze ensures reproducibility, consistency, and production readiness.*
