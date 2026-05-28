import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_project_validation_duration():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/project/create",
            json={"genre": "cinematic emotional", "mood": "nostalgic", "prompt": "x", "duration": 30},
            headers={"Authorization": "Bearer dev:tester"},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_project_unauthorized():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/project/create",
            json={"genre": "cinematic emotional", "mood": "nostalgic", "prompt": "x", "duration": 120},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert body["success"] is False
        assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "ok"
