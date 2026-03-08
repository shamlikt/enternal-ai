"""
API contract tests for /api/v1/health/* and /api/v1/audit/* endpoints.

Health: public endpoint returns 200; ingestion health is admin-only.
Audit: admin-only list endpoint with query params.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.auth.models import Role, User
from app.modules.auth.dependencies import get_current_user
from app.core.database import get_db

from tests.api.conftest import _make_user, make_mock_db


# ---------------------------------------------------------------------------
# GET /api/v1/health/
# ---------------------------------------------------------------------------


class TestSystemHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_endpoint_is_public(self):
        """Health endpoint requires no auth — any client can call it."""
        mock_db = make_mock_db()
        app.dependency_overrides[get_db] = lambda: mock_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/health/")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert "components" in body
        assert body["status"] in ["healthy", "degraded"]

    @pytest.mark.asyncio
    async def test_health_shows_healthy_when_db_ok(self):
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        app.dependency_overrides[get_db] = lambda: mock_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/health/")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_shows_degraded_when_db_fails(self):
        mock_db = AsyncMock()
        mock_db.execute.side_effect = Exception("Connection refused")
        app.dependency_overrides[get_db] = lambda: mock_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/health/")

        app.dependency_overrides.clear()
        # Still returns 200 (API is up) but status is degraded
        assert resp.status_code == 200
        assert resp.json()["status"] == "degraded"


# ---------------------------------------------------------------------------
# GET /api/v1/health/ingestion (admin only)
# ---------------------------------------------------------------------------


class TestIngestionHealthEndpoint:
    @pytest.mark.asyncio
    async def test_admin_can_get_ingestion_health(self):
        admin = _make_user(role=Role.ADMIN)

        result_mock = MagicMock()
        result_mock.fetchall.return_value = [("completed", 10), ("failed", 2)]
        mock_db = AsyncMock()
        mock_db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: admin

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/health/ingestion")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        body = resp.json()
        assert "ingestion_run_stats" in body

    @pytest.mark.asyncio
    async def test_analyst_cannot_get_ingestion_health(self):
        analyst = _make_user(role=Role.ANALYST)
        app.dependency_overrides[get_current_user] = lambda: analyst
        app.dependency_overrides[get_db] = lambda: make_mock_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/health/ingestion")

        app.dependency_overrides.clear()
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_get_ingestion_health(self):
        app.dependency_overrides.clear()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/health/ingestion")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/v1/audit/ (admin only)
# ---------------------------------------------------------------------------


def _make_audit_log_orm(log_id: int = 1, action: str = "login", user_id: int = 1):
    from app.modules.audit.models import AuditLog
    entry = AuditLog()
    entry.id = log_id
    entry.user_id = user_id
    entry.action = action
    entry.resource_type = None
    entry.resource_id = None
    entry.details = None
    entry.ip_address = "127.0.0.1"
    entry.timestamp = datetime.now(timezone.utc)
    return entry


class TestAuditEndpoint:
    @pytest.mark.asyncio
    async def test_admin_can_list_audit_logs(self):
        admin = _make_user(role=Role.ADMIN)
        log1 = _make_audit_log_orm(log_id=1, action="login")
        log2 = _make_audit_log_orm(log_id=2, action="query_executed")

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [log2, log1]
        mock_db = AsyncMock()
        mock_db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: admin

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/audit/")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        assert body[0]["action"] == "query_executed"

    @pytest.mark.asyncio
    async def test_analyst_cannot_access_audit_logs(self):
        analyst = _make_user(role=Role.ANALYST)
        app.dependency_overrides[get_current_user] = lambda: analyst
        app.dependency_overrides[get_db] = lambda: make_mock_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/audit/")

        app.dependency_overrides.clear()
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_access_audit_logs(self):
        app.dependency_overrides.clear()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/audit/")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_limit_query_param_is_validated(self):
        """limit must be between 1 and 500."""
        admin = _make_user(role=Role.ADMIN)
        app.dependency_overrides[get_current_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: make_mock_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/audit/?limit=0")

        app.dependency_overrides.clear()
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_logs(self):
        admin = _make_user(role=Role.ADMIN)
        mock_db = make_mock_db(scalars_result=[])

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: admin

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/audit/")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        assert resp.json() == []
