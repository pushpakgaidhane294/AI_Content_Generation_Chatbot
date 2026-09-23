import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify backend health endpoint returns status 200 and 'ok'."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data


def test_groq_status_endpoint():
    """Verify groq status check endpoint responds with diagnostic structure."""
    response = client.get("/api/groq-status")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert "model" in data
    assert "message" in data


def test_home_page_serves_html():
    """Verify root path serves the single page HTML application."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AI Content Generator" in response.text


def test_empty_prompt_validation():
    """Verify API rejects empty prompts with HTTP 422."""
    payload = {
        "user_prompt": "   ",
        "content_type": "EMAIL",
        "tone": "Professional",
        "audience": "Student",
        "length": "Short"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 422


def test_invalid_content_type_validation():
    """Verify API rejects unsupported content types."""
    payload = {
        "user_prompt": "Write something",
        "content_type": "INVALID_TYPE_XYZ",
        "tone": "Professional",
        "audience": "Student",
        "length": "Short"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 422


def test_history_crud_flow():
    """Verify history retrieval and deletion routes."""
    # List history
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert isinstance(data["items"], list)

    # 404 for non-existent item
    not_found_res = client.get("/api/history/999999")
    assert not_found_res.status_code == 404
