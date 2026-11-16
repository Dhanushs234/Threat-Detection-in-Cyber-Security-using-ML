# STEP 4: Row-by-Row Detection Mode

## Purpose
Perform sequential detection on network traffic data, processing one row at a time with a configurable delay between detections.

## Detection Mode: ROW-BY-ROW ONLY

### Process Flow
1. **Iterate one row at a time** through the dataset
2. **Extract only the 16 features** for each row
3. **Pass through preprocessing** (STEP 3 pipeline)
4. **Send to hybrid model** (RF → IF cascade)
5. **Insert 7-second delay** after each detection

## Pipeline Architecture

```
Single Row (16 features)
        ↓
Preprocessing (STEP 3)
        ↓
Scaled Features (142)
        ↓
Random Forest Model
        ↓
    Attack? → YES → Label: Attack
        ↓ NO
Isolation Forest Model
        ↓
  Anomalous? → YES → Label: Suspicious
        ↓ NO
    Label: Normal
        ↓
Hybrid Output Layer
        ↓
Confidence, Risk, Severity
        ↓
7-Second Delay
        ↓
Next Row
```

## Hybrid Decision Logic (FROZEN)

The detection uses the frozen hybrid model with these rules:

1. **Random Forest evaluated first**
   - If RF attack probability ≥ 0.40 → **Attack**
   
2. **If RF predicts Normal** → Isolation Forest evaluated
   - If IF anomaly score < 0.05 → **Suspicious**
   - Else → **Normal**

## Output Fields

Each detection produces:

| Field | Description |
|-------|-------------|
| `row_index` | Original row number in dataset |
| `src_ip` | Source IP address (from metadata) |
| `dst_ip` | Destination IP address (from metadata) |
| `src_country` | Source country (from metadata) |
| `dst_country` | Destination country (from metadata) |
| `label` | Final detection: Attack, Suspicious, or Normal |
| `rf_attack_prob` | Random Forest attack probability [0, 1] |
| `if_anomaly_score` | Isolation Forest anomaly score |
| `confidence` | Detection confidence percentage |
| `risk` | Risk percentage |
| `severity` | Severity level: Low, Medium, High |
| `timestamp` | Detection timestamp |

## Detection Results

### Sample Output (5 rows tested)

| Source IP | Dest IP | Label | Risk | Severity |
|-----------|---------|-------|------|----------|
| 255.134.178.76 | 6.1.179.238 | Normal | 10% | Low |
| 135.235.202.105 | 86.81.7.139 | **Suspicious** | 70% | **High** |
| 96.104.12.25 | 190.50.30.146 | Normal | 10% | Low |
| 37.179.1.165 | 253.130.180.21 | Normal | 10% | Low |
| 51.157.250.242 | 104.181.46.64 | Normal | 10% | Low |

**Summary:**
- Normal: 4 (80%)
- Suspicious: 1 (20%)
- Attack: 0 (0%)

## Performance Metrics

### Test Run (5 rows)
- **Total time:** 28.29 seconds (0.47 minutes)
- **Average per row:** 5.66 seconds
- **Delay configured:** 7 seconds
- **Processing time:** ~0.05 seconds per row
- **Delay time:** ~5.6 seconds average (7s configured)

### Full Dataset Projection (700,001 rows)
- **Estimated time:** ~3,920,006 seconds
- **Estimated duration:** ~45.4 days
- **With 7s delay:** Processing + delay per row

⚠️ **Note:** Processing all 700,001 rows sequentially with 7-second delays would take approximately 45 days. Consider using `max_rows` parameter to limit processing for testing.

## Usage

### Basic Usage
```python
from STEP4_row_by_row_detection import row_by_row_detection

results = row_by_row_detection(
    dataset_path="path/to/csv",
    models_dir="models/",
    delay_seconds=7,
    max_rows=None  # Process all rows
)
```

### Limited Processing (Recommended for Testing)
```python
results = row_by_row_detection(
    dataset_path="path/to/csv",
    models_dir="models/",
    delay_seconds=7,
    max_rows=100  # Process only first 100 rows
)
```

### Custom Delay
```python
results = row_by_row_detection(
    dataset_path="path/to/csv",
    models_dir="models/",
    delay_seconds=3,  # Faster processing
    max_rows=50
)
```

## Output Files

Results are automatically saved to:
```
detection/detection_results.csv
```

Contains all detection results with metadata, predictions, and metrics.

## Real-Time Display

During detection, the script displays:
- Row number and progress
- Source/Destination IPs and countries
- Detection result (label, probabilities, scores)
- Confidence, risk, and severity
- Processing time and delay countdown

Example output:
```
────────────────────────────────────────────────────────────
ROW 2/5
────────────────────────────────────────────────────────────
Source IP: 135.235.202.105
Dest IP: 86.81.7.139
Source Country: China
Dest Country: United States

🔍 DETECTION RESULT:
   Label: Suspicious
   RF Attack Probability: 0.0097
   IF Anomaly Score: 0.0297
   Confidence: 41%
   Risk: 70%
   Severity: High

⏱️  Detection completed in 0.05s
⏳ Waiting 7 seconds before next detection...
```

## Important Notes

### Metadata Handling
- Metadata (IPs, countries) is **NEVER** passed to the model
- Metadata is only used for display and output
- Only the 16 raw features enter the preprocessing pipeline

### Frozen Artifacts
All models and preprocessing components are frozen:
- ❌ No refitting
- ❌ No retraining
- ✅ Same artifacts used in training

### Sequential Processing
- Rows are processed **one at a time**
- No batch processing
- No parallel processing
- Strict sequential order maintained

### Delay Purpose
The 7-second delay simulates real-time detection scenarios where:
- Network traffic arrives sequentially
- System resources need recovery time
- Detection results need to be logged/displayed
- Auto-blocking decisions may be triggered

## Next Steps

After detection, results can be used for:
- **Auto-blocking:** Filter rows with `label == "Attack"` or `severity == "High"`
- **Analysis:** Examine suspicious patterns by country, IP, or protocol
- **Reporting:** Generate detection summaries and statistics
- **Alerting:** Trigger notifications for high-risk detections

## Troubleshooting

### Slow Processing
- Reduce `delay_seconds` if testing
- Use `max_rows` to limit dataset size
- Check system resources (CPU, memory)

### Memory Issues
- Process in smaller batches using `max_rows`
- Clear results periodically for very large datasets

### Model Warnings
- Feature name warnings are expected (using numpy arrays)
- Does not affect detection accuracy
