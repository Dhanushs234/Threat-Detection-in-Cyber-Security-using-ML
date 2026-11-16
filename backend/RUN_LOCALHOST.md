# 🚀 RUN BACKEND ON LOCALHOST

**Simple instructions to run the FastAPI backend locally.**

---

## ✅ PREREQUISITES

1. **Dependencies installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **All ML artifacts present** in `/models/` directory
3. **Dataset present** at `/data/cleaned_detection_input_with_ip_country.csv`

---

## 🟢 RUN COMMAND (STANDARD)

```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

**Alternative (direct Python):**
```bash
python app.py
```

**Alternative (from main.py):**
```bash
python main.py
```

---

## 📍 BACKEND ACCESS

Once running, backend is available at:

**Base URL:** `http://127.0.0.1:8000`

**API Documentation:** `http://127.0.0.1:8000/docs`

**Alternative Docs:** `http://127.0.0.1:8000/redoc`

---

## 🔄 RUNTIME BEHAVIOR

### ✅ What Happens on Startup

- FastAPI app initializes
- All endpoints become available
- **NO detection starts automatically**
- Server waits for API calls

### ✅ Detection Control

**Start Detection:**
```bash
curl -X POST http://127.0.0.1:8000/monitor/start
```

**Stop Detection:**
```bash
curl -X POST http://127.0.0.1:8000/monitor/stop
```

**Check Status:**
```bash
curl http://127.0.0.1:8000/monitor/stats
```

### ✅ Stop Server

Press `Ctrl + C` in the terminal to stop the backend safely.

---

## 🧪 VERIFY RUNNING

### Test 1: Health Check
```bash
curl http://127.0.0.1:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "Network Intrusion Detection API",
  "version": "1.0.0"
}
```

### Test 2: Root Endpoint
```bash
curl http://127.0.0.1:8000/
```

**Expected:** API information with all endpoints listed

---

## 📊 AVAILABLE ENDPOINTS

### Monitoring
- `POST /monitor/start` - Start detection
- `POST /monitor/stop` - Stop detection
- `GET /monitor/stats` - Get KPI stats
- `GET /monitor/logs` - Get detection logs
- `GET /monitor/blocked` - Get blocked threats
- `GET /monitor/threat-map` - Get threat map
- `GET /monitor/latest` - Get latest detection

### Manual Detection
- `POST /detect/manual` - Single detection (16 raw features)

### Utility
- `GET /health` - Health check
- `GET /` - API info

---

## 🔒 LOCALHOST CONFIGURATION

**Host:** `127.0.0.1` (localhost only)  
**Port:** `8000`  
**No external services required**  
**No environment variables required**  
**No database required**  

Everything runs entirely on localhost.

---

## 🛑 STOP BACKEND

**Graceful Shutdown:**
1. Press `Ctrl + C` in terminal
2. Monitoring loop stops (if running)
3. Server shuts down cleanly

---

## ⚠️ TROUBLESHOOTING

### Issue: Port 8000 already in use

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app:app --host 127.0.0.1 --port 8001
```

### Issue: ModuleNotFoundError

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Cannot find models

**Solution:**
Verify models directory exists:
```bash
ls -la /Users/gauthamreddy/Documents/S\ copy/unsw_rf_project/models/
```

---

## ✅ CONFIRMATION CHECKLIST

- [ ] Dependencies installed
- [ ] ML artifacts present
- [ ] Dataset present
- [ ] Run command executed
- [ ] Backend accessible at `http://127.0.0.1:8000`
- [ ] Health check returns 200 OK
- [ ] Detection does NOT start automatically
- [ ] Detection starts only via `/monitor/start`

---

**Status:** ✅ READY TO RUN  
**Command:** `uvicorn app:app --host 127.0.0.1 --port 8000`  
**Access:** `http://127.0.0.1:8000`
