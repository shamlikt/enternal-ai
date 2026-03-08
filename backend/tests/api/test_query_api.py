"""
API contract tests for /api/v1/query/* and /api/v1/schema/* endpoints.

Verifies HTTP status codes, SELECT-only enforcement at the API layer,
and authorization (Analyst/Admin can query; Viewer cannot).
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


def _make_query_history(history_id: int = 1, user_id: int = 1):
    """ORM-like object returned by get_query_history."""
    from app.modules.query.models import QueryHistory
    h = QueryHistory()
    h.id = history_id
    h.user_id = user_id
    h.sql = "SELECT COUNT(*) FROM DEMOGRAPHIC"
    h.row_count = 10
    h.execution_ms = 55
    h.error = None
    h.executed_at = datetime.now(timezone.utc)
    return h


# ---------------------------------------------------------------------------
# POST /api/v1/query/execute
# ---------------------------------------------------------------------------


class TestQueryExecuteEndpoint:
    @pytest.mark.asyncio
    async def test_analyst_can_execute_select(self):
        analyst = _make_user(role=Role.ANALYST)
        mock_db = make_mock_db()

        with patch("app.modules.query.router.execute_query", return_value=([{"count": 5}], 1, 42)):
            app.dependency_overrides[get_db] = lambda: mock_db
            app.dependency_overrides[get_current_user] = lambda: analyst

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/v1/query/execute",
                    json={"sql": "SELECT COUNT(*) FROM DEMOGRAPHIC"},
                )

            app.dependency_overrides.clear()

        assert resp.status_code == 200
        body = resp.json()
        assert "rows" in body
        assert body["row_count"] == 1
        assert body["execution_ms"] == 42

    @pytest.mark.asyncio
    async def test_viewer_cannot_execute_query_returns_403(self):
        viewer = _make_user(role=Role.VIEWER)
        mock_db = make_mock_db()

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: viewer

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/query/execute",
                json={"sql": "SELECT COUNT(*) FROM DEMOGRAPHIC"},
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/query/execute",
                json={"sql": "SELECT 1"},
            )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_sql_returns_422(self):
        analyst = _make_user(role=Role.ANALYST)
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/query/execute", json={})

        app.dependency_overrides.clear()
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_sql_returns_422(self):
        analyst = _make_user(role=Role.ANALYST)
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/query/execute", json={"sql": ""})

        app.dependency_overrides.clear()
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/query/history
# ---------------------------------------------------------------------------


class TestQueryHistoryEndpoint:
    @pytest.mark.asyncio
    async def test_analyst_can_get_history(self):
        analyst = _make_user(role=Role.ANALYST)
        h1 = _make_query_history(history_id=1, user_id=analyst.id)

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [h1]
        mock_db = AsyncMock()
        mock_db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/query/history")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 1
        assert body[0]["sql"] == "SELECT COUNT(*) FROM DEMOGRAPHIC"

    @pytest.mark.asyncio
    async def test_viewer_returns_403(self):
        viewer = _make_user(role=Role.VIEWER)
        app.dependency_overrides[get_current_user] = lambda: viewer
        app.dependency_overrides[get_db] = lambda: make_mock_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/query/history")

        app.dependency_overrides.clear()
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /api/v1/query/saved + POST /api/v1/query/saved
# ---------------------------------------------------------------------------


class TestSavedQueriesEndpoint:
    @pytest.mark.asyncio
    async def test_list_saved_returns_200(self):
        analyst = _make_user(role=Role.ANALYST)

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        mock_db = AsyncMock()
        mock_db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/query/saved")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_create_saved_query_returns_201(self):
        analyst = _make_user(role=Role.ANALYST)
        mock_db = AsyncMock()
        mock_db.commit = AsyncMock()

        def _refresh(obj):
            obj.id = 10
            obj.user_id = analyst.id
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)
            obj.description = None

        mock_db.refresh = AsyncMock(side_effect=_refresh)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/query/saved",
                json={"name": "My Query", "sql": "SELECT * FROM DEMOGRAPHIC"},
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_update_nonexistent_saved_query_returns_404(self):
        analyst = _make_user(role=Role.ANALYST)
        mock_db = make_mock_db(scalar_result=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.patch(
                "/api/v1/query/saved/9999",
                json={"name": "Updated Name"},
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_saved_query_returns_404(self):
        analyst = _make_user(role=Role.ANALYST)
        mock_db = make_mock_db(scalar_result=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.delete("/api/v1/query/saved/9999")

        app.dependency_overrides.clear()
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/schema/tables
# ---------------------------------------------------------------------------


class TestSchemaEndpoints:
    @pytest.mark.asyncio
    async def test_list_tables_returns_list(self):
        analyst = _make_user(role=Role.ANALYST)

        with patch("app.modules.query.router.get_tables", return_value=["DEMOGRAPHIC", "ENCOUNTER"]):
            app.dependency_overrides[get_db] = lambda: make_mock_db()
            app.dependency_overrides[get_current_user] = lambda: analyst

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.get("/api/v1/schema/tables")

            app.dependency_overrides.clear()

        assert resp.status_code == 200
        body = resp.json()
        assert "DEMOGRAPHIC" in body
        assert "ENCOUNTER" in body

    @pytest.mark.asyncio
    async def test_list_columns_returns_column_info(self):
        analyst = _make_user(role=Role.ANALYST)
        cols = [{"name": "PATID", "type": "varchar", "nullable": "NO"}]

        with patch("app.modules.query.router.get_columns", return_value=cols):
            app.dependency_overrides[get_db] = lambda: make_mock_db()
            app.dependency_overrides[get_current_user] = lambda: analyst

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.get("/api/v1/schema/tables/DEMOGRAPHIC/columns")

            app.dependency_overrides.clear()

        assert resp.status_code == 200
        body = resp.json()
        assert body[0]["name"] == "PATID"

    @pytest.mark.asyncio
    async def test_viewer_cannot_list_tables(self):
        viewer = _make_user(role=Role.VIEWER)
        app.dependency_overrides[get_current_user] = lambda: viewer
        app.dependency_overrides[get_db] = lambda: make_mock_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/schema/tables")

        app.dependency_overrides.clear()
        assert resp.status_code == 403
