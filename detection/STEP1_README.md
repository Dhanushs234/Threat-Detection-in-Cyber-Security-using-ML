# STEP 1: Load Detection Dataset

## Purpose
Load the enriched CSV dataset that contains both model features and metadata columns without any modifications.

## Dataset Information

**Location:** `/Users/gauthamreddy/Documents/S copy/unsw_rf_project/data/cleaned_detection_input_with_ip_country.csv`

**Total Records:** 700,001 rows

**Total Columns:** 20

### Column Breakdown

#### Model Features (16 columns)
These are the raw UNSW features that will be used for detection:
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

#### Metadata Columns (4 columns)
These columns will be split out and NEVER enter the model:
17. `src_ip` - Source IP address
18. `dst_ip` - Destination IP address
19. `src_country` - Source country
20. `dst_country` - Destination country

## Data Quality

✅ **No missing values** detected  
✅ **No infinite values** detected  
✅ **Basic cleaning already done** (inf → NaN conversion)

## Data Types

- **Numeric features:** float64 and int64
- **Categorical features:** object (proto)
- **Metadata:** object (IP addresses and countries)

## Usage

```python
from STEP1_load_dataset import load_detection_dataset

# Load the dataset
dataset = load_detection_dataset(
    "/Users/gauthamreddy/Documents/S copy/unsw_rf_project/data/cleaned_detection_input_with_ip_country.csv"
)

# Dataset is now ready for STEP 2: Metadata Split
```

## Important Notes

⚠️ **DO NOT modify values at this stage**  
⚠️ **DO NOT derive features manually**  
⚠️ **DO NOT perform any preprocessing**  

The dataset is loaded as-is and will be processed in subsequent steps following the exact same pipeline used during training.

## Next Step

➡️ **STEP 2:** Split metadata columns from model features
