import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_health(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/routes_test.db")
    import db as db_module
    from sqlmodel import create_engine, SQLModel
    new_engine = create_engine(f"sqlite:///{tmp_path}/routes_test.db")
    db_module.engine = new_engine
    SQLModel.metadata.create_all(new_engine)
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_start_debate_returns_session_id(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/routes_test2.db")
    import db as db_module
    from sqlmodel import create_engine, SQLModel
    new_engine = create_engine(f"sqlite:///{tmp_path}/routes_test2.db")
    db_module.engine = new_engine
    SQLModel.metadata.create_all(new_engine)
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/debate/start", json={"topic": "test topic"})
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0
