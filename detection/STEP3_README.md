# STEP 3: Preprocessing Pipeline (SAME AS TRAINING)

## Purpose
Apply the **EXACT SAME** preprocessing pipeline used during training. All artifacts are FROZEN - no refitting occurs.

## Critical Rules

⚠️ **ABSOLUTELY NO REFITTING**
- ❌ NO recomputation of medians
- ❌ NO refitting of encoder
- ❌ NO refitting of scaler
- ✅ ONLY use frozen artifacts from training

## Frozen Artifacts Loaded

All preprocessing artifacts are loaded from `models/`:

| Artifact | File | Purpose |
|----------|------|---------|
| **Medians** | `medians.pkl` | Imputation values (11 numeric features) |
| **Encoder** | `encoder.pkl` | OneHotEncoder for protocol (131 categories) |
| **Scaler** | `scaler.pkl` | StandardScaler (expects 142 features) |

## Preprocessing Pipeline (4 Steps)

### Step 3.1: Feature Derivation
**Input:** 16 raw UNSW features  
**Output:** 12 derived features

Derives features using the same logic as training:
- Flow Duration
- Flow Packets/s
- Flow Bytes/s
- Flow IAT Mean
- Flow IAT Std
- Total Forward Bytes
- Total Backward Bytes
- Fwd Packet Length Mean
- Bwd Packet Length Mean
- SYN Flag Count
- ACK Flag Count
- Protocol (categorical)

**Note:** Column name mapping applied: `sintpkt`→`sinpkt`, `dintpkt`→`dinpkt` for compatibility with training preprocessing.

### Step 3.2: Median Imputation
**Input:** 12 derived features (with missing values)  
**Output:** 12 derived features (imputed)

- Uses **FROZEN medians** from training
- Fills NaN values in numeric columns
- Fills Protocol NaN with 'unknown'
- **Missing values handled:** 8,210 → 0

### Step 3.3: Protocol Encoding
**Input:** 12 features (1 categorical)  
**Output:** 142 features (all numeric)

- Uses **FROZEN OneHotEncoder** from training
- Encodes Protocol into 131 binary features
- Handles unknown protocols via `handle_unknown='ignore'`
- **Result:** 11 numeric + 131 encoded = 142 features

### Step 3.4: Scaling
**Input:** 142 features (unscaled)  
**Output:** 142 features (scaled)

- Uses **FROZEN StandardScaler** from training
- Applies same mean/std normalization as training
- **Final shape:** (700,001, 142)

## Validation Results

✅ **Feature derivation:** 16 → 12 features  
✅ **Missing values:** 8,210 imputed using frozen medians  
✅ **Protocol encoding:** 12 → 142 features  
✅ **Scaling:** Applied frozen scaler  
✅ **Final shape:** (700,001, 142) - ready for model  
✅ **Row alignment:** Metadata (700,001, 4) matches preprocessed (700,001, 142)

## Usage

```python
from STEP3_preprocessing import load_frozen_artifacts, preprocess_detection_features
from STEP2_metadata_split import split_metadata_and_features
from STEP1_load_dataset import load_detection_dataset

# Load dataset
dataset = load_detection_dataset("path/to/csv")

# Split metadata and features
metadata_df, features_df = split_metadata_and_features(dataset)

# Load frozen artifacts
medians, encoder, scaler = load_frozen_artifacts("models/")

# Apply preprocessing (NO refitting)
preprocessed_features = preprocess_detection_features(
    features_df, 
    medians, 
    encoder, 
    scaler
)

# preprocessed_features: (700001, 142) - ready for model
# metadata_df: (700001, 4) - kept separate
```

## Important Notes

### Column Name Compatibility
The detection CSV uses `sintpkt`/`dintpkt` while training used `sinpkt`/`dinpkt`. The script automatically renames these columns for compatibility.

### No Training Labels
Detection data has NO `label` column. The preprocessing pipeline is adapted to work without labels (unlike training preprocessing which required labels).

### Frozen Artifact Guarantee
All transformations use the exact same parameters learned during training:
- Same median values for imputation
- Same protocol categories for encoding
- Same mean/std for scaling

This ensures **preprocessing consistency** between training and detection.

## Next Step

➡️ **STEP 4:** Row-by-row detection with 7-second delay using the preprocessed features
