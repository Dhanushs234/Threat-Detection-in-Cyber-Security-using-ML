import asyncio
from typing import Optional

import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
_event_loop: Optional[asyncio.AbstractEventLoop] = None


def init_socketio(loop: asyncio.AbstractEventLoop) -> None:
    """Store the running event loop so background threads can emit safely."""
    global _event_loop
    _event_loop = loop


def emit_event(event: str, payload: dict) -> None:
    """Emit an event to all connected Socket.IO clients (thread-safe)."""
    if _event_loop is None:
        return
    asyncio.run_coroutine_threadsafe(sio.emit(event, payload), _event_loop)


