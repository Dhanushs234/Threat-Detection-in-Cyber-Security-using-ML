# 🚀 BACKEND STARTUP GUIDE

Complete guide to start and use the Network Intrusion Detection Backend API.

---

## 📋 PREREQUISITES

1. **Python 3.8+** installed
2. **All ML artifacts** in place:
   - `/models/rf_model.pkl`
   - `/models/isolation_forest.pkl`
   - `/models/scaler.pkl`
   - `/models/medians.pkl`
   - `/models/encoder.pkl`
3. **Dataset** available:
   - `/data/cleaned_detection_input_with_ip_country.csv`

---

## 🔧 INSTALLATION

### Step 1: Navigate to Backend Directory

```bash
cd /Users/gauthamreddy/Documents/S\ copy/unsw_rf_project/backend
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scikit-learn` - ML models
- `joblib` - Model loading

---

## ▶️ START THE SERVER

### Method 1: Direct Python

```bash
python main.py
```

### Method 2: Uvicorn Command

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Server will start on:**
- URL: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## ✅ VERIFY SERVER IS RUNNING

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "Network Intrusion Detection API",
  "version": "1.0.0"
}
```

### Test 2: Root Endpoint

```bash
curl http://localhost:8000/
```

**Expected response:**
```json
{
  "message": "Network Intrusion Detection API",
  "endpoints": { ... }
}
```

---

## 🧪 RUN AUTOMATED TESTS

```bash
python test_backend.py
```

**Tests include:**
1. Health check
2. Root endpoint
3. Manual detection
4. Complete monitoring workflow
5. Invalid input handling

---

## 🎯 USAGE EXAMPLES

### Example 1: Manual Detection

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

### Example 2: Start Monitoring

```bash
curl -X POST http://localhost:8000/monitor/start
```

### Example 3: Get Real-Time Stats

```bash
curl http://localhost:8000/monitor/stats
```

### Example 4: Stop Monitoring

```bash
curl -X POST http://localhost:8000/monitor/stop
```

---

## 📊 MONITORING WORKFLOW

### 1. Start Monitoring
```bash
curl -X POST http://localhost:8000/monitor/start
```

### 2. Poll Stats (Every 2 seconds)
```bash
while true; do
  curl -s http://localhost:8000/monitor/stats | jq
  sleep 2
done
```

### 3. View Detection Logs
```bash
curl -s http://localhost:8000/monitor/logs | jq
```

### 4. View Blocked Threats
```bash
curl -s http://localhost:8000/monitor/blocked | jq
```

### 5. View Threat Map
```bash
curl -s http://localhost:8000/monitor/threat-map | jq
```

### 6. Stop Monitoring
```bash
curl -X POST http://localhost:8000/monitor/stop
```

---

## 🌐 INTERACTIVE API DOCUMENTATION

FastAPI provides automatic interactive documentation:

### Swagger UI
Open in browser: `http://localhost:8000/docs`

**Features:**
- Try out all endpoints
- See request/response schemas
- Test with sample data
- View validation errors

### ReDoc
Open in browser: `http://localhost:8000/redoc`

**Features:**
- Clean documentation layout
- Detailed schemas
- Code samples
- Download OpenAPI spec

---

## 🔍 PROTOCOL VALUES FOR MANUAL DETECTION

When using `/detect/manual`, the `proto` field accepts:

**Common protocols:**
- `tcp` - Transmission Control Protocol
- `udp` - User Datagram Protocol
- `icmp` - Internet Control Message Protocol
- `arp` - Address Resolution Protocol
- `igmp` - Internet Group Management Protocol

**Additional protocols in dataset:**
- `ipv6-icmp` - IPv6 ICMP
- `ospf` - Open Shortest Path First
- `rtp` - Real-time Transport Protocol
- `rtcp` - RTP Control Protocol

**Example:**
```json
{
  "proto": "tcp"
}
```

---

## 🐛 TROUBLESHOOTING

### Issue: "Cannot connect to backend server"

**Solution:**
1. Verify server is running: `curl http://localhost:8000/health`
2. Check port 8000 is not in use: `lsof -i :8000`
3. Restart server: `python main.py`

---

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Issue: "FileNotFoundError: models/rf_model.pkl"

**Solution:**
Verify all frozen artifacts exist:
```bash
ls -la /Users/gauthamreddy/Documents/S\ copy/unsw_rf_project/models/
```

Required files:
- `rf_model.pkl`
- `isolation_forest.pkl`
- `scaler.pkl`
- `medians.pkl`
- `encoder.pkl`

---

### Issue: "Monitoring already running"

**Solution:**
Stop existing monitoring first:
```bash
curl -X POST http://localhost:8000/monitor/stop
```

Then start again:
```bash
curl -X POST http://localhost:8000/monitor/start
```

---

### Issue: "Validation error for ManualDetectionRequest"

**Solution:**
Ensure all 16 features are provided:
- `dur`, `spkts`, `dpkts`, `sbytes`, `dbytes`
- `sload`, `dload`, `sinpkt`, `dinpkt`
- `sjit`, `djit`, `smean`, `dmean`
- `synack`, `ackdat`, `proto`

---

## 📈 PERFORMANCE NOTES

### Monitoring Performance
- **Detection rate:** 1 row every 7 seconds (strict delay)
- **Throughput:** ~8.5 detections per minute
- **Memory:** In-memory state only, no database overhead

### API Response Times
- **Manual detection:** ~100-200ms
- **Stats endpoint:** <10ms
- **Logs endpoint:** <50ms (depends on log count)

---

## 🔒 SECURITY NOTES

### Current Configuration
- **CORS:** Enabled for all origins (development mode)
- **Authentication:** None (add if deploying to production)
- **Rate limiting:** None (add if needed)

### Production Recommendations
1. Restrict CORS to specific frontend domains
2. Add API key authentication
3. Implement rate limiting
4. Use HTTPS
5. Add request logging

---

## 🛑 STOPPING THE SERVER

### Graceful Shutdown

Press `Ctrl+C` in the terminal running the server.

**What happens:**
1. Monitoring loop stops gracefully
2. Current detection completes
3. State is cleared (in-memory only)
4. Server shuts down

---

## 📝 LOGS AND OUTPUT

### Server Logs
Server logs appear in the terminal:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Detection Logs
Each detection prints to console:
```
======================================================================
Detection DET-000001 | 2024-12-25 22:00:00
======================================================================
Source:      192.168.1.100 (United States)
Destination: 10.0.0.50 (Germany)
Label:       Attack
Severity:    High
Confidence:  95%
Risk:        95%
======================================================================
```

### Blocked IP Logs
When an attack is blocked:
```
🚨 BLOCKED: 192.168.1.100 (Detection: DET-000001)
```

---

## 🎨 FRONTEND INTEGRATION

### Polling Example (JavaScript)

```javascript
// Start monitoring
await fetch('http://localhost:8000/monitor/start', {
  method: 'POST'
});

// Poll stats every 2 seconds
setInterval(async () => {
  const response = await fetch('http://localhost:8000/monitor/stats');
  const stats = await response.json();
  updateDashboard(stats);
}, 2000);

// Poll logs every 3 seconds
setInterval(async () => {
  const response = await fetch('http://localhost:8000/monitor/logs');
  const data = await response.json();
  updateTable(data.logs);
}, 3000);

// Stop monitoring
await fetch('http://localhost:8000/monitor/stop', {
  method: 'POST'
});
```

---

## ✅ VERIFICATION CHECKLIST

Before using the backend, verify:

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] All ML artifacts present in `/models/`
- [ ] Dataset present at `/data/cleaned_detection_input_with_ip_country.csv`
- [ ] Server starts without errors
- [ ] Health check returns 200 OK
- [ ] Manual detection works
- [ ] Monitoring starts successfully
- [ ] Stats update in real-time
- [ ] Monitoring stops gracefully

---

## 📞 SUPPORT

### Common Commands Reference

```bash
# Start server
python main.py

# Run tests
python test_backend.py

# Check health
curl http://localhost:8000/health

# Start monitoring
curl -X POST http://localhost:8000/monitor/start

# Get stats
curl http://localhost:8000/monitor/stats

# Stop monitoring
curl -X POST http://localhost:8000/monitor/stop

# Manual detection
curl -X POST http://localhost:8000/detect/manual \
  -H "Content-Type: application/json" \
  -d @sample_input.json
```

---

**Backend Status:** ✅ READY TO USE  
**Documentation:** ✅ COMPLETE  
**Tests:** ✅ AVAILABLE  
**ML Pipeline:** ✅ UNTOUCHED
