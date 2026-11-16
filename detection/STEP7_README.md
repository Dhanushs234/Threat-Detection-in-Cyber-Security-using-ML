# STEP 7: Display Output After Each Row

## Purpose
Display comprehensive detection output immediately after each row is processed. All metadata values come from the metadata store, NOT from model input.

## Critical Rule

⚠️ **METADATA VALUES MUST COME FROM METADATA STORE, NOT MODEL INPUT**

- Metadata (IPs, countries) stored separately in STEP 2
- Metadata NEVER enters preprocessing or model
- Metadata used ONLY for display purposes
- Only 16 features used for detection

## Display Output Format

After each detection (row), the following is displayed immediately:

```
======================================================================
🔍 DETECTION OUTPUT
======================================================================

📅 Timestamp:              2025-12-25 20:16:15
🆔 Detection ID:           DET-000001

📍 SOURCE INFORMATION:
   IP Address:             255.134.178.76
   Country:                Vietnam

📍 DESTINATION INFORMATION:
   IP Address:             6.1.179.238
   Country:                Netherlands

🎯 DETECTION RESULTS:
   Label:                  Normal
   Severity:               Low
   Hybrid Confidence:      99%
   Risk Score:             10%

📊 MODEL DETAILS:
   RF Attack Probability:  0.0053
   IF Anomaly Score:       0.0876
======================================================================
```

## Required Display Fields

### 1. Timestamp
- **Format:** YYYY-MM-DD HH:MM:SS
- **Source:** System-generated at detection time
- **Example:** 2025-12-25 20:16:15

### 2. Detection ID
- **Format:** DET-XXXXXX (6-digit counter)
- **Source:** System-generated (STEP 5)
- **Example:** DET-000001

### 3. Source IP
- **Source:** Metadata store (from STEP 2)
- **NOT from model input**
- **Example:** 255.134.178.76

### 4. Source Country
- **Source:** Metadata store (from STEP 2)
- **NOT from model input**
- **Example:** Vietnam

### 5. Destination IP
- **Source:** Metadata store (from STEP 2)
- **NOT from model input**
- **Example:** 6.1.179.238

### 6. Destination Country
- **Source:** Metadata store (from STEP 2)
- **NOT from model input**
- **Example:** Netherlands

### 7. Label
- **Values:** Attack, Normal, Suspicious
- **Source:** Hybrid model output (STEP 6)
- **Example:** Normal

### 8. Severity
- **Values:** Low, Medium, High
- **Source:** Output layer (STEP 6)
- **Example:** Low

### 9. Hybrid Confidence
- **Range:** 0-100%
- **Source:** Output layer (STEP 6)
- **Example:** 99%

### 10. Risk Score
- **Range:** 0-100%
- **Source:** Output layer (STEP 6)
- **Example:** 10%

## Sample Output (5 Detections)

### Detection 1
```
Timestamp:         2025-12-25 20:16:15
Detection ID:      DET-000001
Source IP:         255.134.178.76 (Vietnam)
Destination IP:    6.1.179.238 (Netherlands)
Label:             Normal
Severity:          Low
Confidence:        99%
Risk:              10%
```

### Detection 2
```
Timestamp:         2025-12-25 20:16:22
Detection ID:      DET-000002
Source IP:         135.235.202.105 (China)
Destination IP:    86.81.7.139 (United States)
Label:             Suspicious
Severity:          High
Confidence:        41%
Risk:              70%
```

### Detection 3
```
Timestamp:         2025-12-25 20:16:29
Detection ID:      DET-000003
Source IP:         96.104.12.25 (China)
Destination IP:    190.50.30.146 (Australia)
Label:             Normal
Severity:          Low
Confidence:        99%
Risk:              10%
```

### Detection 4
```
Timestamp:         2025-12-25 20:16:36
Detection ID:      DET-000004
Source IP:         37.179.1.165 (Ukraine)
Destination IP:    253.130.180.21 (Japan)
Label:             Normal
Severity:          Low
Confidence:        99%
Risk:              10%
```

### Detection 5
```
Timestamp:         2025-12-25 20:16:43
Detection ID:      DET-000005
Source IP:         51.157.250.242 (Brazil)
Destination IP:    104.181.46.64 (South Korea)
Label:             Normal
Severity:          Low
Confidence:        100%
Risk:              10%
```

## Detection Flow

```
For each row:
    1. Generate Detection ID (system-generated)
    2. Generate Timestamp (current time)
    3. Extract 16 features from features_df
    4. Extract metadata from metadata_df (IPs, countries)
    5. Preprocess 16 features → 142 features
    6. Send to hybrid model → label, rf_prob, if_score
    7. Send to output layer → confidence, risk, severity
    8. Display output immediately with all fields
    9. Save to results
    10. Wait 7 seconds
    11. Next row
```

## Metadata Source Verification

### Metadata Store (STEP 2)
- **Created in:** STEP 2 (metadata split)
- **Columns:** src_ip, dst_ip, src_country, dst_country
- **Shape:** (700,001, 4)
- **Usage:** Display only

### Model Input (STEP 3)
- **Created in:** STEP 3 (preprocessing)
- **Columns:** 142 preprocessed features
- **Shape:** (700,001, 142)
- **Usage:** Model detection only

### Critical Separation
```
Metadata DataFrame (4 columns)
    ↓
Display Output ONLY
    ✅ Source IP
    ✅ Destination IP
    ✅ Source Country
    ✅ Destination Country

Features DataFrame (16 → 142 columns)
    ↓
Model Detection ONLY
    ✅ Preprocessing
    ✅ Hybrid Model
    ✅ Output Layer
```

## Summary Statistics (5 Detections)

### Label Distribution
| Label | Count | Percentage |
|-------|-------|------------|
| Normal | 4 | 80.0% |
| Suspicious | 1 | 20.0% |
| Attack | 0 | 0.0% |

### Severity Distribution
| Severity | Count | Percentage |
|----------|-------|------------|
| Low | 4 | 80.0% |
| High | 1 | 20.0% |
| Medium | 0 | 0.0% |

### Performance
- **Total detections:** 5
- **Total time:** 28.30 seconds (0.47 minutes)
- **Average per detection:** 5.66 seconds
- **Delay configured:** 7 seconds

## Usage

### Basic Usage
```python
from STEP7_display_output import row_by_row_detection_with_display

results = row_by_row_detection_with_display(
    dataset_path="path/to/csv",
    models_dir="models/",
    delay_seconds=7,
    max_rows=None  # Process all rows
)
```

### Limited Processing
```python
results = row_by_row_detection_with_display(
    dataset_path="path/to/csv",
    models_dir="models/",
    delay_seconds=7,
    max_rows=100  # First 100 rows only
)
```

### Custom Delay
```python
results = row_by_row_detection_with_display(
    dataset_path="path/to/csv",
    models_dir="models/",
    delay_seconds=3,  # Faster processing
    max_rows=50
)
```

## Output Files

Results are saved to:
```
detection/detection_with_display.csv
```

CSV format includes all fields:
```csv
detection_id,timestamp,row_index,src_ip,dst_ip,src_country,dst_country,label,severity,confidence,risk,rf_attack_prob,if_anomaly_score
DET-000001,2025-12-25 20:16:15,0,255.134.178.76,6.1.179.238,Vietnam,Netherlands,Normal,Low,99,10,0.0053,0.0876
```

## Display Features

### Real-Time Output
- Output displayed immediately after each detection
- No buffering or batching
- Live progress tracking
- Row-by-row visibility

### Formatted Display
- Clear section headers
- Emoji indicators for readability
- Aligned columns
- Consistent formatting

### Information Hierarchy
1. **Timestamp & ID** - When and what
2. **Source Info** - Where from
3. **Destination Info** - Where to
4. **Detection Results** - What was detected
5. **Model Details** - How it was detected

## Integration with Previous Steps

### Complete Pipeline (STEP 1-7)

**STEP 1:** Load dataset  
**STEP 2:** Split metadata (stored separately) and features  
**STEP 3:** Preprocess features (frozen artifacts)  
**STEP 4:** Row-by-row detection (7s delay)  
**STEP 5:** Generate detection IDs (system-generated)  
**STEP 6:** Hybrid model + output layer  
**STEP 7:** Display output immediately ✅

### Data Flow
```
CSV Dataset
    ↓
STEP 1: Load
    ↓
STEP 2: Split
    ↓
Metadata Store          Features
(IPs, Countries)        (16 raw)
    ↓                       ↓
    |                   STEP 3: Preprocess
    |                       ↓
    |                   (142 features)
    |                       ↓
    |                   STEP 6: Hybrid Model
    |                       ↓
    |                   (label, confidence, risk, severity)
    |                       ↓
    └───────────────────────┘
                ↓
    STEP 7: Display Output
    (Metadata + Detection Results)
```

## Metadata Verification

### Test Results Verification ✅
- **All IP addresses:** From metadata store ✅
- **All countries:** From metadata store ✅
- **Metadata NEVER entered model:** Verified ✅
- **Only 16 features used for detection:** Verified ✅

### CSV Output Verification
All records contain:
- ✅ detection_id (system-generated)
- ✅ timestamp (system-generated)
- ✅ src_ip (from metadata store)
- ✅ dst_ip (from metadata store)
- ✅ src_country (from metadata store)
- ✅ dst_country (from metadata store)
- ✅ label (from hybrid model)
- ✅ severity (from output layer)
- ✅ confidence (from output layer)
- ✅ risk (from output layer)

## Important Notes

### Immediate Display
- Output shown after EACH row
- No waiting for batch completion
- Real-time monitoring capability
- Operator can see results as they happen

### Metadata Isolation
- Metadata stored separately in STEP 2
- Never mixed with features
- Never preprocessed
- Never sent to model
- Used ONLY for display

### Detection ID Tracking
- Each detection has unique ID
- IDs are sequential (DET-000001, DET-000002, ...)
- IDs used for logging and reference
- IDs NOT from dataset (system-generated)

## Next Steps

STEP 7 output can be used for:
- **Real-time monitoring:** Watch detections as they happen
- **Operator alerts:** Notify on high-risk detections
- **Auto-blocking:** Trigger blocks based on severity
- **Audit logging:** Record all detections with full context
- **Incident response:** Quick identification of threats
- **Reporting:** Generate detection reports with metadata
