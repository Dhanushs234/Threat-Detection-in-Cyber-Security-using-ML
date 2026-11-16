# STEP 6: Hybrid Model + Output Layer Integration

## Purpose
Send preprocessed rows to the hybrid model and pass model outputs to the output layer for final metrics computation. Uses existing implementations without re-implementing formulas.

## Critical Rule

⚠️ **DO NOT RE-IMPLEMENT FORMULAS**

- Uses existing `hybrid_wrapper.py` for model predictions
- Uses existing `hybrid_output_layer.py` for confidence/risk/severity
- No formula duplication
- No logic re-implementation

## Pipeline Flow

```
Preprocessed Row (142 features)
        ↓
┌─────────────────────────────────────┐
│   HYBRID MODEL (hybrid_wrapper.py)  │
│                                     │
│   1. Random Forest Model            │
│      → Attack probability [0, 1]    │
│                                     │
│   2. Isolation Forest Model         │
│      → Anomaly score                │
│                                     │
│   3. Hybrid Decision Logic          │
│      → Label: Attack/Suspicious/    │
│        Normal                       │
└─────────────────────────────────────┘
        ↓
Model Outputs:
- label (str)
- rf_attack_prob (float)
- if_anomaly_score (float)
        ↓
┌─────────────────────────────────────┐
│  OUTPUT LAYER (hybrid_output_layer) │
│                                     │
│   Computes:                         │
│   - Confidence % [0-100]            │
│   - Risk % [0-100]                  │
│   - Severity (Low/Medium/High)      │
└─────────────────────────────────────┘
        ↓
Final Output:
- label
- rf_attack_prob
- if_anomaly_score
- confidence
- risk
- severity
```

## Hybrid Model Logic (FROZEN)

### Random Forest (Supervised)
- **Input:** 142 preprocessed features
- **Output:** Attack probability [0, 1]
- **Threshold:** 0.40
- **Decision:** If prob ≥ 0.40 → Attack

### Isolation Forest (Unsupervised)
- **Input:** 142 preprocessed features
- **Output:** Anomaly score (lower = more anomalous)
- **Threshold:** 0.05
- **Decision:** If score < 0.05 → Suspicious

### Cascade Logic
1. **RF evaluated first**
2. **If RF predicts Attack** → Final = Attack
3. **If RF predicts Normal** → IF evaluated
4. **If IF detects anomaly** → Final = Suspicious
5. **Else** → Final = Normal

## Output Layer Computation

### Confidence Calculation

**Attack (RF decides):**
```
confidence = rf_attack_prob × 100
```

**Normal (RF decides):**
```
confidence = (1 - rf_attack_prob) × 100
```

**Suspicious (IF decides):**
```
confidence = min(100, ((IF_THRESHOLD - if_score) / |IF_THRESHOLD|) × 100)
```

### Risk Calculation

**Attack:**
```
risk = rf_attack_prob × 100
```

**Normal:**
```
risk = (1 - rf_attack_prob) × 10  # stays very low
```

**Suspicious:**
```
risk = 50 + 0.5 × confidence
```

### Severity Mapping

```
if risk < 30:
    severity = "Low"
elif risk < 70:
    severity = "Medium"
else:
    severity = "High"
```

## Output Fields

| Field | Type | Range/Values | Description |
|-------|------|--------------|-------------|
| `label` | str | Attack, Normal, Suspicious | Final detection label |
| `rf_attack_prob` | float | [0, 1] | Random Forest attack probability |
| `if_anomaly_score` | float | Real number | Isolation Forest anomaly score |
| `confidence` | int | [0, 100] | Detection confidence percentage |
| `risk` | int | [0, 100] | Risk percentage |
| `severity` | str | Low, Medium, High | Severity level |

## Sample Results (5 Detections)

| Source IP | Dest IP | Label | Confidence | Risk | Severity |
|-----------|---------|-------|------------|------|----------|
| 255.134.178.76 | 6.1.179.238 | Normal | 99% | 10% | Low |
| 135.235.202.105 | 86.81.7.139 | **Suspicious** | 41% | 70% | **High** |
| 96.104.12.25 | 190.50.30.146 | Normal | 99% | 10% | Low |
| 37.179.1.165 | 253.130.180.21 | Normal | 99% | 10% | Low |
| 51.157.250.242 | 104.181.46.64 | Normal | 100% | 10% | Low |

### Analysis
- **Normal:** 4 detections (80%) - Low risk, high confidence
- **Suspicious:** 1 detection (20%) - High risk, medium confidence
- **Attack:** 0 detections (0%)

## Usage

### Basic Integration
```python
from STEP6_hybrid_integration import hybrid_detection_with_output_layer

# preprocessed_row: pd.DataFrame with 142 features
result = hybrid_detection_with_output_layer(preprocessed_row)

# result = {
#     'label': 'Normal',
#     'rf_attack_prob': 0.0053,
#     'if_anomaly_score': 0.0876,
#     'confidence': 99,
#     'risk': 10,
#     'severity': 'Low'
# }
```

### Complete Pipeline
```python
from STEP6_hybrid_integration import demonstrate_hybrid_integration

results = demonstrate_hybrid_integration(
    dataset_path="path/to/csv",
    models_dir="models/",
    num_samples=10
)

# Results DataFrame with all fields:
# - row_index, src_ip, dst_ip, src_country, dst_country
# - label, rf_attack_prob, if_anomaly_score
# - confidence, risk, severity
```

## Integration with Previous Steps

### STEP 3 → STEP 6
```python
# STEP 3: Preprocessing
preprocessed = preprocess_detection_features(features_df, medians, encoder, scaler)

# STEP 6: Hybrid model + output layer
result = hybrid_detection_with_output_layer(preprocessed)
```

### Complete Flow (STEP 1-6)
```python
# STEP 1: Load dataset
dataset = load_detection_dataset(csv_path)

# STEP 2: Split metadata and features
metadata_df, features_df = split_metadata_and_features(dataset)

# STEP 3: Preprocess features
medians, encoder, scaler = load_frozen_artifacts(models_dir)
preprocessed = preprocess_detection_features(features_df, medians, encoder, scaler)

# STEP 6: Hybrid detection
result = hybrid_detection_with_output_layer(preprocessed)

# Result contains: label, confidence, risk, severity
```

## Verification Results

### Output Fields Verified ✅
- **Label:** object (string) ✅
- **Severity:** object (string) ✅
- **Confidence:** int64 (0-100) ✅
- **Risk:** int64 (0-100) ✅
- **RF Attack Prob:** float64 ✅
- **IF Anomaly Score:** float64 ✅

### Label Distribution (5 samples)
- Normal: 4
- Suspicious: 1
- Attack: 0

### Severity Distribution (5 samples)
- Low: 4
- High: 1
- Medium: 0

## Key Components Used

### 1. hybrid_wrapper.py
**Functions:**
- `load_models()` - Load RF and IF models
- `hybrid_decision()` - Apply cascade logic
- `predict_single()` - Run prediction on single sample

**Artifacts:**
- `models/rf_model.pkl` - Random Forest model
- `models/isolation_forest.pkl` - Isolation Forest model
- `models/rf_config.json` - RF threshold (0.40)
- `models/if_config.json` - IF threshold (0.05)

### 2. hybrid_output_layer.py
**Functions:**
- `compute_confidence_risk_severity()` - Compute all metrics

**Logic:**
- Confidence calculation (label-dependent)
- Risk calculation (label-dependent)
- Severity mapping (risk-driven)

## Important Notes

### No Formula Re-implementation
All calculations are performed by existing modules:
- ✅ Model predictions: `hybrid_wrapper.py`
- ✅ Metric computation: `hybrid_output_layer.py`
- ❌ No duplicate formulas in STEP 6
- ❌ No manual confidence/risk calculations

### Frozen Models
Both models are frozen and loaded from saved artifacts:
- RF model trained on 82,332 samples
- IF model trained on normal behavior
- Thresholds fixed at 0.40 (RF) and 0.05 (IF)
- No retraining or refitting

### Output Layer Independence
The output layer:
- Does NOT affect hybrid decision logic
- Only computes interpretive metrics
- Can be modified without retraining models
- Provides human-readable results

## Output Files

Results are saved to:
```
detection/hybrid_integration_results.csv
```

Format:
```csv
row_index,src_ip,dst_ip,src_country,dst_country,label,rf_attack_prob,if_anomaly_score,confidence,risk,severity
0,255.134.178.76,6.1.179.238,Vietnam,Netherlands,Normal,0.0053,0.0876,99,10,Low
```

## Next Steps

STEP 6 output can be used for:
- **Display:** Show results to operators with confidence/risk/severity
- **Auto-blocking:** Filter high-risk detections for blocking
- **Alerting:** Trigger alerts based on severity levels
- **Logging:** Record all detections with full metrics
- **Reporting:** Generate detection summaries and statistics
