# 🗄️ DATABASE MODULE - HISTORY & AUDIT STORAGE

SQLite-based storage for detection history and audit trails.

---

## 🔒 GLOBAL RULES (ENFORCED)

### ✅ What Database STORES

- ✅ Manual detection history (all)
- ✅ CSV attack detections
- ✅ CSV suspicious detections
- ✅ Blocked threats

### ❌ What Database DOES NOT STORE

- ❌ Normal CSV detections
- ❌ Raw features
- ❌ Scaled features
- ❌ Encoded features
- ❌ Model vectors

**Database is ONLY for history & audit, NOT for detection data.**

---

## 📁 FILES

### 1. `db_schema.py`
- Database schema definition
- Table creation
- Initialization logic
- Reset functionality
- Retention policy

### 2. `db_manager.py`
- Async write operations
- Background worker thread
- Queue-based writes (non-blocking)
- Read operations for history
- Thread-safe operations

### 3. `ids_history.db`
- SQLite database file (auto-created)
- Local file-based storage
- No external setup required

---

## 📊 DATABASE TABLES

### Table 1: `manual_detection_history`

Stores all manual detections.

**Columns:**
- `id` - Auto-increment primary key
- `timestamp` - Detection timestamp
- `detection_id` - System detection ID (optional)
- `label` - Attack / Suspicious / Normal
- `hybrid_confidence` - Confidence percentage (0-100)
- `risk_score` - Risk score (0-100)

**Write Policy:** ALWAYS insert

---

### Table 2: `threat_events`

Stores ONLY attack and suspicious detections from CSV monitoring.

**Columns:**
- `id` - Auto-increment primary key
- `timestamp` - Detection timestamp
- `detection_id` - System detection ID
- `src_ip` - Source IP address
- `src_country` - Source country
- `dst_ip` - Destination IP address
- `dst_country` - Destination country
- `label` - Attack / Suspicious
- `severity` - High / Medium / Low
- `hybrid_confidence` - Confidence percentage (0-100)
- `risk_score` - Risk score (0-100)

**Write Policy:** ONLY if label == "Attack" OR label == "Suspicious"

---

### Table 3: `blocked_threats`

Stores all blocked IP addresses.

**Columns:**
- `id` - Auto-increment primary key
- `timestamp` - Block timestamp
- `detection_id` - System detection ID
- `src_ip` - Blocked IP address
- `reason` - Block reason (e.g., "Attack detected")
- `severity` - Threat severity

**Write Policy:** ALWAYS insert when IP is blocked

---

## 🔄 ASYNC WRITE OPERATIONS

### Non-Blocking Writes

All database writes are **asynchronous** and **non-blocking**:

1. Detection completes
2. Write request queued
3. Background worker processes queue
4. Detection loop continues immediately

**Detection NEVER waits for database writes.**

### Background Worker

- Runs in separate daemon thread
- Processes write queue continuously
- Handles errors gracefully
- Stops cleanly on shutdown

---

## 📏 RETENTION POLICY

### Automatic Cleanup

**Rule:** Keep last **50,000 rows** per table

**Enforcement:**
- Applied separately to each table
- Deletes oldest rows when limit exceeded
- Runs periodically (can be triggered manually)

**Example:**
```python
from db_schema import apply_retention_policy

# Keep last 50,000 rows in each table
apply_retention_policy(max_rows=50000)
```

---

## 🔄 DEMO RESET

### Reset All History

For demo purposes, you can reset all history without restarting the backend.

**API Endpoint:**
```bash
POST /admin/reset-history
```

**What it does:**
1. Deletes all rows from all tables
2. Resets in-memory stats
3. Does NOT drop tables
4. Does NOT restart backend

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/admin/reset-history
```

**Response:**
```json
{
  "status": "success",
  "message": "All history reset successfully",
  "table_counts": {
    "manual_detection_history": 0,
    "threat_events": 0,
    "blocked_threats": 0
  }
}
```

---

## 📖 USAGE

### Initialize Database

Database is automatically initialized on backend startup:

```python
from db_schema import initialize_database

initialize_database()
```

### Start Database Manager

Database manager starts automatically with backend:

```python
from db_manager import db_manager

db_manager.start()
```

### Queue Manual Detection

```python
db_manager.queue_manual_detection({
    'timestamp': '2024-12-25 22:00:00',
    'label': 'Normal',
    'hybrid_confidence': 85,
    'risk_score': 15
})
```

### Queue Threat Event (Attack/Suspicious Only)

```python
db_manager.queue_threat_event({
    'timestamp': '2024-12-25 22:00:00',
    'detection_id': 'DET-000001',
    'src_ip': '192.168.1.100',
    'src_country': 'United States',
    'dst_ip': '10.0.0.50',
    'dst_country': 'Germany',
    'label': 'Attack',
    'severity': 'High',
    'hybrid_confidence': 95,
    'risk_score': 95
})
```

### Queue Blocked Threat

```python
db_manager.queue_blocked_threat({
    'timestamp': '2024-12-25 22:00:00',
    'detection_id': 'DET-000001',
    'src_ip': '192.168.1.100',
    'reason': 'Attack detected',
    'severity': 'High'
})
```

### Read History

```python
# Get manual detection history
manual_history = db_manager.get_manual_detection_history(limit=100)

# Get threat events
threats = db_manager.get_threat_events(limit=100)

# Get blocked threats
blocked = db_manager.get_blocked_threats_history(limit=100)
```

---

## 🌐 API ENDPOINTS

### History Read Endpoints

**Get Manual Detection History:**
```bash
GET /history/manual?limit=100
```

**Get Threat Events:**
```bash
GET /history/threats?limit=100
```

**Get Blocked Threats:**
```bash
GET /history/blocked?limit=100
```

**Get Database Stats:**
```bash
GET /admin/db-stats
```

### Admin Endpoints

**Reset All History:**
```bash
POST /admin/reset-history
```

---

## 🧪 TESTING

### Test Database Initialization

```bash
cd Database
python db_schema.py
```

**Expected Output:**
```
✅ Database initialized: /path/to/ids_history.db

Table counts: {
  'manual_detection_history': 0,
  'threat_events': 0,
  'blocked_threats': 0
}
```

### Test Database Operations

```python
from db_manager import db_manager
from db_schema import initialize_database

# Initialize
initialize_database()
db_manager.start()

# Queue some data
db_manager.queue_manual_detection({
    'timestamp': '2024-12-25 22:00:00',
    'label': 'Normal',
    'hybrid_confidence': 85,
    'risk_score': 15
})

# Wait for write to complete
import time
time.sleep(1)

# Read history
history = db_manager.get_manual_detection_history(limit=10)
print(history)

# Stop manager
db_manager.stop()
```

---

## ⚠️ IMPORTANT NOTES

### What Database DOES

✅ Stores important outcomes only  
✅ Async writes (non-blocking)  
✅ Thread-safe operations  
✅ Automatic retention policy  
✅ Demo reset capability  
✅ Read-only history APIs  

### What Database DOES NOT DO

❌ Store every CSV row  
❌ Store normal traffic  
❌ Store raw features  
❌ Modify detection timing  
❌ Mix with ML logic  
❌ Block detection loop  

---

## 🔧 CONFIGURATION

### Database Path

```python
DB_PATH = Path(__file__).parent / "ids_history.db"
```

### Retention Limit

```python
retention_max_rows = 50000  # Per table
```

### Queue Settings

- Queue type: `Queue` (thread-safe)
- Worker timeout: 1 second
- Daemon thread: Yes

---

## 📈 PERFORMANCE

### Write Performance

- **Async writes:** No blocking
- **Queue-based:** Instant return
- **Background processing:** Separate thread

### Read Performance

- **Direct SQLite queries:** Fast
- **Indexed by ID:** Efficient
- **Limit parameter:** Prevents large reads

---

## 🛡️ SAFETY GUARANTEES

1. **Non-blocking:** Detection never waits for DB
2. **Thread-safe:** All operations protected
3. **Error handling:** Graceful failure (logs error, continues)
4. **Clean shutdown:** Worker stops cleanly
5. **Data integrity:** SQLite ACID properties

---

## 📝 STORAGE POLICY SUMMARY

| Detection Type | Store to DB? | Table |
|----------------|--------------|-------|
| Manual detection | ✅ YES | `manual_detection_history` |
| CSV Attack | ✅ YES | `threat_events` |
| CSV Suspicious | ✅ YES | `threat_events` |
| CSV Normal | ❌ NO | - |
| Blocked IP | ✅ YES | `blocked_threats` |
| Raw features | ❌ NO | - |
| Model vectors | ❌ NO | - |

---

**Database Status:** ✅ READY  
**ML Pipeline:** ✅ UNTOUCHED  
**Write Mode:** ✅ ASYNC (NON-BLOCKING)  
**Retention:** ✅ 50,000 ROWS PER TABLE  
**Demo Reset:** ✅ SUPPORTED
