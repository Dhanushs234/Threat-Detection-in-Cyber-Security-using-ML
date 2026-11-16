"""
BACKEND ENTRY POINT - LOCALHOST EXECUTION

FastAPI application entry point for localhost execution.

RULES:
- NO detection logic in global scope
- Detection starts ONLY via API calls
- Runs on 127.0.0.1:8000

RUN COMMAND:
    uvicorn app:app --host 127.0.0.1 --port 8000
"""

from socketio import ASGIApp

from main import app as fastapi_app
from socket_manager import sio

# Combined ASGI app (FastAPI + Socket.IO)
app = ASGIApp(sio, other_asgi_app=fastapi_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
