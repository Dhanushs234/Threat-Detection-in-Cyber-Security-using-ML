# STEP 2: Metadata and Feature Separation

## Purpose
Separate metadata columns from model input features while maintaining perfect row alignment. This ensures metadata NEVER enters the preprocessing pipeline or model.

## Critical Rule
⚠️ **METADATA MUST NEVER PASS INTO PREPROCESSING OR MODEL**

## Separation Logic

### Metadata Columns (4 columns - stored separately)
1. `src_ip` - Source IP address
2. `dst_ip` - Destination IP address  
3. `src_country` - Source country
4. `dst_country` - Destination country

**Purpose:** Display, logging, and auto-blocking decisions

### Model Feature Columns (16 columns - EXACTLY in this order)
1. `dur` - Duration
2. `spkts` - Source packets
3. `dpkts` - Destination packets
4. `sbytes` - Source bytes
5. `dbytes` - Destination bytes
6. `sload` - Source load
7. `dload` - Destination load
8. `sintpkt` - Source inter-packet time
9. `dintpkt` - Destination inter-packet time
10. `sjit` - Source jitter
11. `djit` - Destination jitter
12. `smean` - Source mean
13. `dmean` - Destination mean
14. `synack` - SYN-ACK time
15. `ackdat` - ACK-DATA time
16. `proto` - Protocol

**Purpose:** Preprocessing and model detection

## Validation Checks

The script performs the following validations:

✅ **Row alignment:** Both DataFrames have identical row counts (700,001)  
✅ **Feature count:** Exactly 16 model features  
✅ **Metadata count:** Exactly 4 metadata columns  
✅ **No overlap:** Zero columns shared between metadata and features  
✅ **All columns present:** No missing columns from original dataset

## Output

### Metadata DataFrame
- **Shape:** (700,001, 4)
- **Columns:** src_ip, dst_ip, src_country, dst_country
- **Usage:** Display and auto-blocking only

### Features DataFrame  
- **Shape:** (700,001, 16)
- **Columns:** All 16 UNSW features in exact order
- **Usage:** Enters preprocessing pipeline and model

## Usage

```python
from STEP2_metadata_split import split_metadata_and_features
from STEP1_load_dataset import load_detection_dataset

# Load dataset
dataset = load_detection_dataset("path/to/csv")

# Split into metadata and features
metadata_df, features_df = split_metadata_and_features(dataset)

# metadata_df: (700001, 4) - for display/blocking
# features_df: (700001, 16) - for model detection
```

## Row Alignment Guarantee

Both DataFrames maintain the same row indices, ensuring:
- Row 0 in metadata_df corresponds to Row 0 in features_df
- Row N in metadata_df corresponds to Row N in features_df

This alignment is critical for matching detection results back to their source IPs and countries.

## Next Step

➡️ **STEP 3:** Apply the same preprocessing pipeline used during training to `features_df` only
