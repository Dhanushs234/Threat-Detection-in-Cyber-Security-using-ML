"""
FASTAPI BACKEND - NETWORK INTRUSION DETECTION SYSTEM

Exposes REST APIs for:
- Continuous monitoring (start/stop)
- KPI stats
- Detection logs
- Blocked threats
- Threat map
- Manual detection
- History storage (database)

RULES:
- NO modifications to ML pipeline
- Database for history/audit only
- In-memory state for real-time
- Polling-based (no WebSockets)
"""

import asyncio
import sys
import os

# Add Database directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Database'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from socketio import ASGIApp
from typing import Dict, List, Optional

from state_manager import monitoring_state
from monitoring_service import monitoring_service
from detection_wrapper import detect_manual_input, REQUIRED_FEATURES

# Database imports
from db_schema import initialize_database, reset_all_tables, get_table_counts
from db_manager import db_manager
from socket_manager import sio, init_socketio


app = FastAPI(
    title="Network Intrusion Detection API",
    description="Backend API for continuous monitoring and manual detection",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================

class ManualDetectionRequest(BaseModel):
    """Manual detection input - 16 raw features"""
    dur: float = Field(..., description="Flow duration")
    spkts: float = Field(..., description="Source packets")
    dpkts: float = Field(..., description="Destination packets")
    sbytes: float = Field(..., description="Source bytes")
    dbytes: float = Field(..., description="Destination bytes")
    sload: float = Field(..., description="Source load")
    dload: float = Field(..., description="Destination load")
    sinpkt: float = Field(..., description="Source inter-packet time")
    dinpkt: float = Field(..., description="Destination inter-packet time")
    sjit: float = Field(..., description="Source jitter")
    djit: float = Field(..., description="Destination jitter")
    smean: float = Field(..., description="Source mean packet length")
    dmean: float = Field(..., description="Destination mean packet length")
    synack: float = Field(..., description="SYN-ACK count")
    ackdat: float = Field(..., description="ACK-DAT count")
    proto: str = Field(..., description="Protocol (e.g., tcp, udp, arp)")


class ManualDetectionResponse(BaseModel):
    """Manual detection output"""
    timestamp: str
    label: str
    severity: str
    hybrid_confidence: int
    risk_score: int


class MonitoringStatusResponse(BaseModel):
    """Monitoring status response"""
    status: str
    message: str


class KPIStatsResponse(BaseModel):
    """KPI statistics response"""
    monitoring: bool
    total_detections: int
    normal_count: int
    suspicious_count: int
    attack_count: int
    blocked_count: int
    total_time: float
    avg_time_per_detection: float


# =====================================================
# MONITORING ENDPOINTS
# =====================================================

@app.post("/monitor/start", response_model=MonitoringStatusResponse)
async def start_monitoring():
    """
    Start continuous monitoring.
    
    Behavior:
    - Set is_monitoring = True
    - Start background loop
    - Process rows with 7-second delay
    """
    result = monitoring_service.start()
    return result


@app.post("/monitor/stop", response_model=MonitoringStatusResponse)
async def stop_monitoring():
    """
    Stop continuous monitoring.
    
    Behavior:
    - Set is_monitoring = False
    - Loop exits gracefully
    - Stats remain available
    """
    result = monitoring_service.stop()
    return result


@app.get("/monitor/stats", response_model=KPIStatsResponse)
async def get_monitoring_stats():
    """
    Get current KPI statistics.
    
    Returns:
    - monitoring: bool
    - total_detections: int
    - normal_count: int
    - suspicious_count: int
    - attack_count: int
    - blocked_count: int
    - total_time: float
    - avg_time_per_detection: float
    """
    stats = monitoring_state.get_kpi_stats()
    return stats


@app.get("/monitor/logs")
async def get_detection_logs():
    """
    Get all detection logs.
    
    Returns list of:
    - timestamp
    - detection_id
    - src_ip
    - src_country
    - dst_ip
    - dst_country
    - label
    - severity
    - hybrid_confidence
    - risk_score
    """
    logs = monitoring_state.get_detection_logs()
    return {"logs": logs}


@app.get("/monitor/blocked")
async def get_blocked_threats():
    """
    Get all blocked threats.
    
    Returns list of:
    - timestamp
    - detection_id
    - src_ip
    - reason
    - severity
    """
    blocked = monitoring_state.get_blocked_threats()
    return {"blocked_threats": blocked}


@app.get("/monitor/threat-map")
async def get_threat_map():
    """
    Get threat map events for visualization.
    
    Each event contains:
    - from_country
    - to_country
    - label
    - severity
    - color (red=attack, orange=suspicious, blue=normal)
    - timestamp
    
    NOTE: Read-only, no geo-IP calls, uses existing metadata
    """
    events = monitoring_state.get_threat_map_events()
    return {"threat_map": events}


@app.get("/monitor/latest")
async def get_latest_detection():
    """
    Get the most recent detection result.
    
    Returns:
    - Latest detection object or null
    """
    latest = monitoring_state.get_latest_detection()
    return {"latest_detection": latest}


@app.get("/monitor/detections-per-minute")
async def get_detections_per_minute(limit: int = 12):
    """Return total detections per minute for the recent window."""
    sanitized_limit = max(1, min(limit, 15))
    data = monitoring_state.get_detections_per_minute(max_minutes=sanitized_limit)
    return {"detections_per_minute": data}


# =====================================================
# MANUAL DETECTION ENDPOINT
# =====================================================

@app.post("/detect/manual", response_model=ManualDetectionResponse)
async def manual_detection(request: ManualDetectionRequest):
    """
    Perform manual detection on user-typed input.
    
    Input: 16 raw features
    - dur, spkts, dpkts, sbytes, dbytes
    - sload, dload, sinpkt, dinpkt
    - sjit, djit, smean, dmean
    - synack, ackdat, proto
    
    Output:
    - timestamp
    - label
    - severity
    - hybrid_confidence
    - risk_score
    
    RULES:
    - No logs
    - No metadata
    - Single request only
    - Stores to database (manual_detection_history)
    """
    try:
        # Convert request to dict
        user_input = request.dict()
        
        # Run detection
        result = detect_manual_input(user_input)
        
        # Store to database (async, non-blocking)
        db_manager.queue_manual_detection({
            'timestamp': result['timestamp'],
            'label': result['label'],
            'hybrid_confidence': result['hybrid_confidence'],
            'risk_score': result['risk_score']
        })
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Network Intrusion Detection API",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Network Intrusion Detection API",
        "endpoints": {
            "monitoring": {
                "start": "POST /monitor/start",
                "stop": "POST /monitor/stop",
                "stats": "GET /monitor/stats",
                "logs": "GET /monitor/logs",
                "blocked": "GET /monitor/blocked",
                "threat_map": "GET /monitor/threat-map",
                "latest": "GET /monitor/latest"
            },
            "detection": {
                "manual": "POST /detect/manual",
                "detections_per_minute": "GET /monitor/detections-per-minute"
            },
            "health": "GET /health"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database and start DB manager on startup"""
    initialize_database()
    db_manager.start()
    loop = asyncio.get_running_loop()
    init_socketio(loop)
    print("Backend startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop DB manager on shutdown"""
    db_manager.stop()
    print("Backend shutdown complete")


# =====================================================
# ADMIN ENDPOINTS (DEMO RESET)
# =====================================================

@app.post("/admin/reset-history")
async def reset_history():
    """
    Reset all database history for demo purposes.
    
    Deletes all rows from:
    - manual_detection_history
    - threat_events
    - blocked_threats
    
    Also resets in-memory stats.
    Does NOT restart backend.
    """
    try:
        # Reset database tables
        reset_all_tables()
        
        # Reset in-memory state
        monitoring_state.reset()
        
        # Get updated counts
        counts = get_table_counts()
        
        return {
            "status": "success",
            "message": "All history reset successfully",
            "table_counts": counts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


# =====================================================
# HISTORY ENDPOINTS (READ-ONLY)
# =====================================================

@app.get("/history/manual")
async def get_manual_history(limit: int = 100):
    """
    Get manual detection history from database.
    
    Args:
        limit: Maximum records to return (default: 100)
    
    Returns:
        List of manual detection records
    """
    try:
        history = db_manager.get_manual_detection_history(limit=limit)
        return {
            "count": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@app.get("/history/threats")
async def get_threats_history(limit: int = 100):
    """
    Get threat events history (attacks and suspicious) from database.
    
    Args:
        limit: Maximum records to return (default: 100)
    
    Returns:
        List of threat event records
    """
    try:
        threats = db_manager.get_threat_events(limit=limit)
        return {
            "count": len(threats),
            "threats": threats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch threats: {str(e)}")


@app.get("/history/blocked")
async def get_blocked_history(limit: int = 100):
    """
    Get blocked threats history from database.
    
    Args:
        limit: Maximum records to return (default: 100)
    
    Returns:
        List of blocked threat records
    """
    try:
        blocked = db_manager.get_blocked_threats_history(limit=limit)
        return {
            "count": len(blocked),
            "blocked": blocked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch blocked history: {str(e)}")


@app.get("/admin/db-stats")
async def get_database_stats():
    """
    Get database statistics (table row counts).
    
    Returns:
        Row counts for all tables
    """
    try:
        counts = get_table_counts()
        return {
            "status": "success",
            "table_counts": counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


socket_app = ASGIApp(sio, other_asgi_app=app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="127.0.0.1", port=8000)
