import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"

@pytest.mark.asyncio
async def test_chat_stream_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/chat/stream",
            json={"prompt": "Test prompt for async streaming", "model": "llama-3.1-8b-instant", "temperature": 0.5}
        )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "data: " in response.text
    assert "[DONE]" in response.text

@pytest.mark.asyncio
async def test_invalid_prompt_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/chat/stream",
            json={"prompt": "", "temperature": 0.5} # Empty prompt triggers Pydantic validation error
        )
    assert response.status_code == 422
