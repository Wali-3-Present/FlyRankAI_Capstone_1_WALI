import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_cors_preflight_handling():
    """Probe 1: Verify OPTIONS CORS preflight returns correct cross-origin headers."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.options(
            "/api/submissions",
            headers={
                "Origin": "http://external-customer-domain.com",
                "Access-Control-Request-Method": "POST"
            }
        )
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == "*"

@pytest.mark.asyncio
async def test_invalid_widget_submission_boundary():
    """Probe 2: Verify bad payload returns 444/404 JSON error, never 500."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/submissions", json={"widget_id": "non-existent-uuid", "data": {}})
        assert res.status_code == 404
        assert "detail" in res.json()

@pytest.mark.asyncio
async def test_honeypot_spam_blocking():
    """Probe 6: Honeypot trap filled by bot triggers early mitigation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/submissions",
            json={
                "widget_id": "dummy",
                "data": {"email": "bot@spam.com"},
                "hp_field": "I am a spam bot"
            }
        )
        assert res.status_code == 200