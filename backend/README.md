# BACKEND API - NETWORK INTRUSION DETECTION SYSTEM

FastAPI backend that wraps the existing detection pipeline **WITHOUT modifying any ML code**.

---

## 🔒 GLOBAL RULES (ENFORCED)

✅ **NO modifications to:**
- Preprocessing pipeline
- Feature derivation
- Encoding / median / scaling
- Hybrid model
- Output layer formulas
- Thresholds or labels

✅ **Backend ONLY:**
- Orchestrates existing logic
- Exposes REST APIs
- Manages in-memory state
- Provides real-time monitoring

---

## 📁 FILE STRUCTURE

```
backend/
├── main.py                    # FastAPI app with all endpoints
├── state_manager.py           # In-memory state (KPIs, logs, blocked threats)
├── detection_wrapper.py       # Wraps existing detection logic
├── monitoring_service.py      # Background monitoring loop
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🚀 QUICK START

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python main.py
```

#### Windows (Command Prompt)

If the server exits immediately when run directly, launch it through `cmd /c` so the process stays alive:

```bat
cmd /c C:\Users\akash\AppData\Local\Programs\Python\Python311\python.exe main.py
```

> Adjust the Python path if your installation lives elsewhere.

Server runs on: `http://localhost:8000`

API docs: `http://localhost:8000/docs`

---

## 📡 API ENDPOINTS

### **A. CONTINUOUS MONITORING**

#### Start Monitoring
```http
POST /monitor/start
```

**Behavior:**
- Sets `is_monitoring = True`
- Starts background loop
- Processes rows with **7-second delay**
- Auto-blocks attacks only

**Response:**
```json
{
  "status": "success",
  "message": "Monitoring started"
}
```

---

#### Stop Monitoring
```http
POST /monitor/stop
```

**Behavior:**
- Sets `is_monitoring = False`
- Loop exits gracefully
- Stats remain available

**Response:**
```json
{
  "status": "success",
  "message": "Monitoring stopped"
}
```

---

#### Get KPI Stats
```http
GET /monitor/stats
```

**Response:**
```json
{
  "monitoring": true,
  "total_detections": 150,
  "normal_count": 100,
  "suspicious_count": 30,
  "attack_count": 20,
  "blocked_count": 20,
  "total_time": 1050.5,
  "avg_time_per_detection": 7.0
}
```

---

#### Get Detection Logs
```http
GET /monitor/logs
```

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-12-25 22:00:00",
      "detection_id": "DET-000001",
      "src_ip": "192.168.1.100",
      "src_country": "United States",
      "dst_ip": "10.0.0.50",
      "dst_country": "Germany",
      "label": "Attack",
      "severity": "High",
      "hybrid_confidence": 95,
      "risk_score": 95
    }
  ]
}
```

---

#### Get Blocked Threats
```http
GET /monitor/blocked
```

**Response:**
```json
{
  "blocked_threats": [
    {
      "timestamp": "2024-12-25 22:00:00",
      "detection_id": "DET-000001",
      "src_ip": "192.168.1.100",
      "reason": "Attack detected",
      "severity": "High"
    }
  ]
}
```

---

#### Get Threat Map
```http
GET /monitor/threat-map
```

**Response:**
```json
{
  "threat_map": [
    {
      "from_country": "United States",
      "to_country": "Germany",
      "label": "Attack",
      "severity": "High",
      "color": "red",
      "timestamp": "2024-12-25 22:00:00"
    }
  ]
}
```

**Color Rules:**
- `attack` → **red**
- `suspicious` → **orange**
- `normal` → **blue**

---

#### Get Latest Detection
```http
GET /monitor/latest
```

**Response:**
```json
{
  "latest_detection": {
    "timestamp": "2024-12-25 22:00:00",
    "detection_id": "DET-000001",
    "src_ip": "192.168.1.100",
    "src_country": "United States",
    "dst_ip": "10.0.0.50",
    "dst_country": "Germany",
    "label": "Attack",
    "severity": "High",
    "hybrid_confidence": 95,
    "risk_score": 95
  }
}
```

---

### **B. MANUAL DETECTION**

#### Manual Detection
```http
POST /detect/manual
```

**Request Body (16 raw features):**
```json
{
  "dur": 0.001055,
  "spkts": 2,
  "dpkts": 2,
  "sbytes": 132,
  "dbytes": 164,
  "sload": 500473.9375,
  "dload": 621800.9375,
  "sinpkt": 0.017,
  "dinpkt": 0.013,
  "sjit": 0.0,
  "djit": 0.0,
  "smean": 66,
  "dmean": 82,
  "synack": 0.0,
  "ackdat": 0.0,
  "proto": "udp"
}
```

**Response:**
```json
{
  "timestamp": "2024-12-25 22:00:00",
  "label": "Normal",
  "severity": "Low",
  "hybrid_confidence": 85,
  "risk_score": 15
}
```

**Rules:**
- No logs
- No metadata
- Single request only
- Same pipeline as monitoring

---

## 🔄 MONITORING LOOP BEHAVIOR

```python
while is_monitoring:
    # 1. Detect one row
    detect_single_row_with_metadata()
    
    # 2. Generate detection_id
    detection_id = generate_detection_id(counter)
    
    # 3. Update KPI counters
    monitoring_state.add_detection(detection)
    
    # 4. Append detection log
    detection_logs.append(detection)
    
    # 5. Auto-block if attack
    if label == "Attack":
        block_src_ip()
        append_blocked_threat()
    
    # 6. Append threat map event
    threat_map_events.append(event)
    
    # 7. STRICT 7-SECOND DELAY
    time.sleep(7)
```

---

## 🧠 STATE MANAGEMENT

### In-Memory State (Thread-Safe)

```python
monitoring_state = {
    'is_monitoring': bool,
    'start_time': datetime,
    'detection_counter': int,
    'kpi_stats': {
        'total_detections': int,
        'normal_count': int,
        'suspicious_count': int,
        'attack_count': int,
        'blocked_count': int
    },
    'latest_detection': DetectionResult,
    'detection_logs': List[DetectionResult],
    'blocked_threats': List[BlockedThreat],
    'threat_map_events': List[ThreatMapEvent]
}
```

**Rules:**
- No database
- No persistence
- Reset on restart is OK
- Thread-safe with locks

---

## 🔐 AUTO-BLOCKING LOGIC

**STRICT RULE:** Only block if `label == "Attack"`

```python
if result['label'].lower() == 'attack':
    blocked = BlockedThreat(
        timestamp=timestamp,
        detection_id=detection_id,
        src_ip=src_ip,
        reason='Attack detected',
        severity=severity
    )
    monitoring_state.add_blocked_threat(blocked)
```

---

## 📊 DETECTION RESULT FORMAT

Every detection produces:

```python
{
    'timestamp': str,           # YYYY-MM-DD HH:MM:SS
    'detection_id': str,        # DET-XXXXXX
    'src_ip': str,              # Source IP
    'src_country': str,         # Source country
    'dst_ip': str,              # Destination IP
    'dst_country': str,         # Destination country
    'label': str,               # Attack / Suspicious / Normal
    'severity': str,            # High / Medium / Low
    'hybrid_confidence': int,   # 0-100
    'risk_score': int           # 0-100
}
```

---

## 🧪 TESTING

### Test Health Check
```bash
curl http://localhost:8000/health
```

### Test Manual Detection
```bash
curl -X POST http://localhost:8000/detect/manual \
  -H "Content-Type: application/json" \
  -d '{
    "dur": 0.001055,
    "spkts": 2,
    "dpkts": 2,
    "sbytes": 132,
    "dbytes": 164,
    "sload": 500473.9375,
    "dload": 621800.9375,
    "sinpkt": 0.017,
    "dinpkt": 0.013,
    "sjit": 0.0,
    "djit": 0.0,
    "smean": 66,
    "dmean": 82,
    "synack": 0.0,
    "ackdat": 0.0,
    "proto": "udp"
  }'
```

### Start Monitoring
```bash
curl -X POST http://localhost:8000/monitor/start
```

### Get Stats
```bash
curl http://localhost:8000/monitor/stats
```

### Stop Monitoring
```bash
curl -X POST http://localhost:8000/monitor/stop
```

---

## ⚠️ IMPORTANT NOTES

### What Backend DOES:
✅ Orchestrates existing detection logic  
✅ Exposes REST APIs  
✅ Manages in-memory state  
✅ Provides real-time monitoring  
✅ Auto-blocks attacks  

### What Backend DOES NOT DO:
❌ Modify preprocessing  
❌ Modify models  
❌ Modify formulas  
❌ Recompute medians  
❌ Batch predict  
❌ Use database  
❌ Use WebSockets (polling only)  

---

## 🎯 FRONTEND INTEGRATION

### Polling Strategy (Recommended)

```javascript
// Poll stats every 2 seconds
setInterval(async () => {
  const stats = await fetch('/monitor/stats').then(r => r.json());
  updateKPICards(stats);
}, 2000);

// Poll logs every 3 seconds
setInterval(async () => {
  const logs = await fetch('/monitor/logs').then(r => r.json());
  updateDetectionTable(logs.logs);
}, 3000);

// Poll blocked threats every 3 seconds
setInterval(async () => {
  const blocked = await fetch('/monitor/blocked').then(r => r.json());
  updateBlockedTable(blocked.blocked_threats);
}, 3000);

// Poll threat map every 5 seconds
setInterval(async () => {
  const map = await fetch('/monitor/threat-map').then(r => r.json());
  updateThreatMap(map.threat_map);
}, 5000);
```

---

## 📝 PROTOCOL VALUES

For manual detection, `proto` field accepts:

**Common protocols:**
- `tcp` - Transmission Control Protocol
- `udp` - User Datagram Protocol
- `icmp` - Internet Control Message Protocol
- `arp` - Address Resolution Protocol
- `igmp` - Internet Group Management Protocol

**Example values from dataset:**
```
udp, tcp, arp, icmp, igmp, ipv6-icmp, ospf, rtp, rtcp
```

---

## 🔧 TROUBLESHOOTING

### Issue: "Monitoring already running"
**Solution:** Call `/monitor/stop` first, then `/monitor/start`

### Issue: "Missing required fields"
**Solution:** Ensure all 16 features are provided in manual detection

### Issue: "Column name mismatch"
**Solution:** Backend automatically handles `sintpkt/sinpkt` and `dintpkt/dinpkt` naming

### Issue: "Models not loading"
**Solution:** Verify `MODELS_DIR` path in `detection_wrapper.py`

---

## 📄 LICENSE

This backend wraps the existing ML pipeline without modifications.  
All ML logic remains unchanged and follows the frozen artifact rules.

---

**Backend Status:** ✅ READY  
**ML Pipeline:** ✅ UNTOUCHED  
**Auto-Blocking:** ✅ ATTACK ONLY  
**Delay:** ✅ 7 SECONDS STRICT
