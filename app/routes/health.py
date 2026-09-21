from datetime import datetime, timezone, timedelta
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.schemas import HealthResponse, OllamaStatusResponse
from app.services.ai_provider import get_ai_service

router = APIRouter(prefix="/api", tags=["Health & Status"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Returns HTTP 200 with application health status.
    This endpoint is used by Render's health check system.
    It always returns 200 as long as the FastAPI process is alive.
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).isoformat()
    }


@router.get("/ollama-status", response_model=OllamaStatusResponse)
async def get_ollama_status():
    """
    Checks if the configured AI service is reachable.
    Returns a structured status object. Never throws 500 —
    a disconnected Ollama is a normal state on cloud deployments.
    """
    try:
        ai_service = get_ai_service()
        status_info = await ai_service.check_status()
    except Exception as exc:
        status_info = {
            "connected": False,
            "model": "unavailable",
            "available_models": [],
            "base_url": "N/A",
            "message": f"AI service not reachable: {str(exc)}"
        }
    return status_info
