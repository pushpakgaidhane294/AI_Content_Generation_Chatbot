"""
API routes package initialization.
"""

from app.routes.health import router as health_router
from app.routes.chat import router as chat_router
from app.routes.history import router as history_router

__all__ = ["health_router", "chat_router", "history_router"]
