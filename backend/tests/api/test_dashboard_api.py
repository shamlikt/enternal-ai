"""
API contract tests for /api/v1/dashboards/* endpoints.

Tests focus on:
- RBAC: Analyst/Admin can create/edit; Viewer can only read
- 404 when dashboard not found
- Template listing and creation
- Widget CRUD within dashboard
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.auth.models import Role, User
from app.modules.auth.dependencies import get_current_user
from app.core.database import get_db
from app.modules.dashboard.models import Dashboard, DashboardWidget

from tests.api.conftest import _make_user, make_mock_db


def _make_dashboard(
    dashboard_id: int = 1,
    user_id: int = 1,
    name: str = "Test Dashboard",
) -> Dashboard:
    d = Dashboard()
    d.id = dashboard_id
    d.user_id = user_id
    d.name = name
    d.description = None
    d.is_public = False
    d.created_at = datetime.now(timezone.utc)
    d.updated_at = datetime.now(timezone.utc)
    return d


def _make_widget(widget_id: int = 1, dashboard_id: int = 1) -> DashboardWidget:
    w = DashboardWidget()
    w.id = widget_id
    w.dashboard_id = dashboard_id
    w.title = "Patient Count"
    w.widget_type = "kpi"
    w.sql = "SELECT COUNT(*) FROM DEMOGRAPHIC"
    w.grid_x = 0
    w.grid_y = 0
    w.grid_w = 6
    w.grid_h = 4
    w.created_at = datetime.now(timezone.utc)
    w.updated_at = datetime.now(timezone.utc)
    return w


# ---------------------------------------------------------------------------
# GET /api/v1/dashboards/templates
# ---------------------------------------------------------------------------


class TestTemplatesEndpoint:
    @pytest.mark.asyncio
    async def test_authenticated_user_can_list_templates(self):
        viewer = _make_user(role=Role.VIEWER)
        app.dependency_overrides[get_current_user] = lambda: viewer

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/dashboards/templates")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        templates = resp.json()
        assert isinstance(templates, list)
        assert len(templates) == 5
        names = {t["name"] for t in templates}
        assert "Patient Demographics" in names

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/dashboards/templates")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/dashboards/templates/{template_name}
# ---------------------------------------------------------------------------


class TestCreateFromTemplateEndpoint:
    @pytest.mark.asyncio
    async def test_analyst_can_create_from_template(self):
        analyst = _make_user(role=Role.ANALYST)
        dashboard = _make_dashboard(dashboard_id=10)

        with patch(
            "app.modules.dashboard.router.create_dashboard_from_template",
            return_value=dashboard,
        ):
            app.dependency_overrides[get_db] = lambda: make_mock_db()
            app.dependency_overrides[get_current_user] = lambda: analyst

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post("/api/v1/dashboards/templates/Patient Demographics")

            app.dependency_overrides.clear()

        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] == 10

    @pytest.mark.asyncio
    async def test_viewer_cannot_create_from_template(self):
        viewer = _make_user(role=Role.VIEWER)
        app.dependency_overrides[get_current_user] = lambda: viewer
        app.dependency_overrides[get_db] = lambda: make_mock_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/dashboards/templates/Patient Demographics")

        app.dependency_overrides.clear()
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_nonexistent_template_returns_404(self):
        analyst = _make_user(role=Role.ANALYST)

        app.dependency_overrides[get_db] = lambda: make_mock_db()
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/dashboards/templates/Nonexistent Template")

        app.dependency_overrides.clear()
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/dashboards/
# ---------------------------------------------------------------------------


class TestListDashboardsEndpoint:
    @pytest.mark.asyncio
    async def test_viewer_can_list_dashboards(self):
        viewer = _make_user(role=Role.VIEWER)
        d1 = _make_dashboard(dashboard_id=1, name="Overview")
        d2 = _make_dashboard(dashboard_id=2, name="Trends")

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [d1, d2]
        mock_db = AsyncMock()
        mock_db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: viewer

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/dashboards/")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self):
        app.dependency_overrides.clear()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/dashboards/")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/dashboards/
# ---------------------------------------------------------------------------


class TestCreateDashboardEndpoint:
    @pytest.mark.asyncio
    async def test_analyst_can_create_dashboard(self):
        analyst = _make_user(role=Role.ANALYST)
        new_dashboard = _make_dashboard(dashboard_id=5, name="New Dashboard")

        with patch(
            "app.modules.dashboard.router.create_dashboard",
            return_value=new_dashboard,
        ):
            app.dependency_overrides[get_db] = lambda: make_mock_db()
            app.dependency_overrides[get_current_user] = lambda: analyst

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/v1/dashboards/",
                    json={"name": "New Dashboard", "is_public": False},
                )

            app.dependency_overrides.clear()

        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "New Dashboard"

    @pytest.mark.asyncio
    async def test_viewer_cannot_create_dashboard(self):
        viewer = _make_user(role=Role.VIEWER)
        app.dependency_overrides[get_current_user] = lambda: viewer
        app.dependency_overrides[get_db] = lambda: make_mock_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/dashboards/",
                json={"name": "Test"},
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_missing_name_returns_422(self):
        analyst = _make_user(role=Role.ANALYST)
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/dashboards/", json={})

        app.dependency_overrides.clear()
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/dashboards/{dashboard_id}
# ---------------------------------------------------------------------------


class TestGetDashboardEndpoint:
    @pytest.mark.asyncio
    async def test_viewer_can_get_dashboard(self):
        viewer = _make_user(role=Role.VIEWER)
        dashboard = _make_dashboard(dashboard_id=3)
        widget = _make_widget(widget_id=1, dashboard_id=3)

        # First execute = get_dashboard_by_id, second = get_widgets
        result1 = MagicMock()
        result1.scalar_one_or_none.return_value = dashboard
        result2 = MagicMock()
        result2.scalars.return_value.all.return_value = [widget]
        mock_db = AsyncMock()
        mock_db.execute.side_effect = [result1, result2]

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: viewer

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/dashboards/3")

        app.dependency_overrides.clear()
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == 3
        assert "widgets" in body
        assert len(body["widgets"]) == 1

    @pytest.mark.asyncio
    async def test_not_found_returns_404(self):
        viewer = _make_user(role=Role.VIEWER)
        mock_db = make_mock_db(scalar_result=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: viewer

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/dashboards/9999")

        app.dependency_overrides.clear()
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /api/v1/dashboards/{dashboard_id}
# ---------------------------------------------------------------------------


class TestUpdateDashboardEndpoint:
    @pytest.mark.asyncio
    async def test_analyst_can_update_dashboard(self):
        analyst = _make_user(role=Role.ANALYST)
        dashboard = _make_dashboard(dashboard_id=1, name="Old Name")

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = dashboard
        mock_db = AsyncMock()
        mock_db.execute.return_value = result_mock
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.patch("/api/v1/dashboards/1", json={"name": "New Name"})

        app.dependency_overrides.clear()
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_update_nonexistent_dashboard_returns_404(self):
        analyst = _make_user(role=Role.ANALYST)
        mock_db = make_mock_db(scalar_result=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.patch("/api/v1/dashboards/9999", json={"name": "X"})

        app.dependency_overrides.clear()
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/dashboards/{dashboard_id}
# ---------------------------------------------------------------------------


class TestDeleteDashboardEndpoint:
    @pytest.mark.asyncio
    async def test_analyst_can_delete_dashboard(self):
        analyst = _make_user(role=Role.ANALYST)
        dashboard = _make_dashboard(dashboard_id=1)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = dashboard
        mock_db = AsyncMock()
        mock_db.execute.return_value = result_mock
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.delete("/api/v1/dashboards/1")

        app.dependency_overrides.clear()
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_nonexistent_dashboard_returns_404(self):
        analyst = _make_user(role=Role.ANALYST)
        mock_db = make_mock_db(scalar_result=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.delete("/api/v1/dashboards/9999")

        app.dependency_overrides.clear()
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Widget endpoints
# ---------------------------------------------------------------------------


class TestWidgetEndpoints:
    @pytest.mark.asyncio
    async def test_add_widget_to_nonexistent_dashboard_returns_404(self):
        analyst = _make_user(role=Role.ANALYST)
        mock_db = make_mock_db(scalar_result=None)

        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: analyst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/dashboards/9999/widgets",
                json={
                    "title": "Count",
                    "widget_type": "kpi",
                    "sql": "SELECT COUNT(*) FROM DEMOGRAPHIC",
                },
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_add_widget_with_invalid_type_returns_422(self):
        analyst = _make_user(role=Role.ANALYST)
        app.dependency_overrides[get_current_user] = lambda: analyst
        app.dependency_overrides[get_db] = lambda: make_mock_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/dashboards/1/widgets",
                json={
                    "title": "Count",
                    "widget_type": "scatter",  # invalid
                    "sql": "SELECT 1",
                },
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_viewer_cannot_add_widget(self):
        viewer = _make_user(role=Role.VIEWER)
        app.dependency_overrides[get_current_user] = lambda: viewer
        app.dependency_overrides[get_db] = lambda: make_mock_db()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/dashboards/1/widgets",
                json={
                    "title": "Count",
                    "widget_type": "kpi",
                    "sql": "SELECT COUNT(*) FROM DEMOGRAPHIC",
                },
            )

        app.dependency_overrides.clear()
        assert resp.status_code == 403
