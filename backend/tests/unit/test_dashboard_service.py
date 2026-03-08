"""
Unit tests for app.modules.dashboard.service and app.modules.dashboard.schemas.

Tests cover:
- Dashboard schema validation (widget types, field constraints)
- Template definitions (all 5 pre-built templates load correctly)
- Dashboard service CRUD with mocked AsyncSession
- Widget SELECT-only enforcement (dashboard re-uses the query guardrail)
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.modules.dashboard.schemas import (
    DashboardCreate,
    DashboardResponse,
    DashboardUpdate,
    DashboardWithWidgets,
    TemplateDefinition,
    WidgetCreate,
    WidgetDataResponse,
    WidgetResponse,
    WidgetUpdate,
)
from app.modules.dashboard.service import (
    TEMPLATES,
    create_dashboard,
    create_dashboard_from_template,
    delete_dashboard,
    update_dashboard,
)
from app.modules.dashboard.models import Dashboard, DashboardWidget


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestWidgetCreate:
    VALID_TYPES = ["bar", "line", "pie", "area", "donut", "kpi", "table", "funnel"]

    def test_valid_widget_all_types(self):
        for wtype in self.VALID_TYPES:
            w = WidgetCreate(
                title="Test Widget",
                widget_type=wtype,
                sql="SELECT COUNT(*) FROM DEMOGRAPHIC",
            )
            assert w.widget_type == wtype

    def test_invalid_widget_type_raises(self):
        with pytest.raises(ValidationError):
            WidgetCreate(title="Test", widget_type="scatter", sql="SELECT 1")

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError):
            WidgetCreate(title="", widget_type="bar", sql="SELECT 1")

    def test_title_too_long_raises(self):
        with pytest.raises(ValidationError):
            WidgetCreate(title="x" * 256, widget_type="bar", sql="SELECT 1")

    def test_empty_sql_raises(self):
        with pytest.raises(ValidationError):
            WidgetCreate(title="Test", widget_type="bar", sql="")

    def test_default_grid_values(self):
        w = WidgetCreate(title="Test", widget_type="kpi", sql="SELECT COUNT(*) FROM DEMOGRAPHIC")
        assert w.grid_x == 0
        assert w.grid_y == 0
        assert w.grid_w == 6
        assert w.grid_h == 4

    def test_custom_grid_values(self):
        w = WidgetCreate(
            title="Test",
            widget_type="bar",
            sql="SELECT 1",
            grid_x=3,
            grid_y=2,
            grid_w=9,
            grid_h=6,
        )
        assert w.grid_x == 3
        assert w.grid_w == 9


class TestWidgetUpdate:
    def test_all_optional(self):
        update = WidgetUpdate()
        assert update.title is None
        assert update.widget_type is None
        assert update.sql is None

    def test_partial_type_update(self):
        update = WidgetUpdate(widget_type="line")
        assert update.widget_type == "line"

    def test_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            WidgetUpdate(widget_type="histogram")

    def test_empty_sql_raises(self):
        with pytest.raises(ValidationError):
            WidgetUpdate(sql="")


class TestDashboardCreate:
    def test_valid_create(self):
        dc = DashboardCreate(name="Patient Overview")
        assert dc.name == "Patient Overview"
        assert dc.is_public is False

    def test_public_dashboard(self):
        dc = DashboardCreate(name="Shared Dashboard", is_public=True)
        assert dc.is_public is True

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            DashboardCreate(name="")

    def test_name_too_long_raises(self):
        with pytest.raises(ValidationError):
            DashboardCreate(name="x" * 256)

    def test_with_description(self):
        dc = DashboardCreate(name="Q1 Report", description="Q1 2024 analytics dashboard")
        assert dc.description == "Q1 2024 analytics dashboard"


class TestDashboardUpdate:
    def test_all_optional(self):
        update = DashboardUpdate()
        assert update.name is None
        assert update.description is None
        assert update.is_public is None

    def test_update_public_flag(self):
        update = DashboardUpdate(is_public=True)
        assert update.is_public is True


class TestDashboardResponse:
    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        resp = DashboardResponse(
            id=1,
            user_id=42,
            name="Patient Overview",
            description=None,
            is_public=False,
            created_at=now,
            updated_at=now,
        )
        assert resp.id == 1
        assert resp.is_public is False


class TestDashboardWithWidgets:
    def test_empty_widgets_by_default(self):
        now = datetime.now(timezone.utc)
        d = DashboardWithWidgets(
            id=1,
            user_id=1,
            name="Test",
            description=None,
            is_public=False,
            created_at=now,
            updated_at=now,
        )
        assert d.widgets == []


class TestWidgetDataResponse:
    def test_valid_widget_data(self):
        resp = WidgetDataResponse(
            widget_id=5,
            rows=[{"SEX": "M", "count": 150}, {"SEX": "F", "count": 180}],
            row_count=2,
            execution_ms=34,
        )
        assert resp.widget_id == 5
        assert resp.row_count == 2


# ---------------------------------------------------------------------------
# Template tests
# ---------------------------------------------------------------------------


class TestPrebuiltTemplates:
    def test_five_templates_exist(self):
        assert len(TEMPLATES) == 5

    def test_all_template_names_are_unique(self):
        names = [t.name for t in TEMPLATES]
        assert len(names) == len(set(names))

    def test_patient_demographics_template(self):
        template = next(t for t in TEMPLATES if t.name == "Patient Demographics")
        assert len(template.widgets) > 0
        for widget in template.widgets:
            assert widget.widget_type in ["bar", "pie", "donut", "kpi", "table", "funnel", "line", "area"]

    def test_encounter_trends_template(self):
        template = next(t for t in TEMPLATES if t.name == "Encounter Trends")
        assert len(template.widgets) > 0

    def test_diagnosis_distribution_template(self):
        template = next(t for t in TEMPLATES if t.name == "Diagnosis Distribution")
        assert len(template.widgets) > 0

    def test_lab_results_summary_template(self):
        template = next(t for t in TEMPLATES if t.name == "Lab Results Summary")
        assert len(template.widgets) > 0

    def test_prescription_analytics_template(self):
        template = next(t for t in TEMPLATES if t.name == "Prescription Analytics")
        assert len(template.widgets) > 0

    def test_all_template_widget_sqls_are_select(self):
        """All template widget SQLs must be SELECT statements."""
        from app.modules.query.service import _validate_select_only
        for template in TEMPLATES:
            for widget in template.widgets:
                # Should not raise for any template widget SQL
                _validate_select_only(widget.sql)

    def test_all_templates_have_description(self):
        for template in TEMPLATES:
            assert template.description
            assert len(template.description) > 0


# ---------------------------------------------------------------------------
# Service tests with mocked DB
# ---------------------------------------------------------------------------


def _make_dashboard(
    dashboard_id: int = 1,
    user_id: int = 1,
    name: str = "Test Dashboard",
    is_public: bool = False,
) -> Dashboard:
    d = Dashboard()
    d.id = dashboard_id
    d.user_id = user_id
    d.name = name
    d.description = None
    d.is_public = is_public
    d.created_at = datetime.now(timezone.utc)
    d.updated_at = datetime.now(timezone.utc)
    return d


class TestCreateDashboard:
    @pytest.mark.asyncio
    async def test_create_dashboard_adds_to_db(self):
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        data = DashboardCreate(name="My Dashboard", is_public=False)
        await create_dashboard(db, user_id=1, data=data)

        db.add.assert_called_once()
        added = db.add.call_args[0][0]
        assert added.name == "My Dashboard"
        assert added.user_id == 1
        assert added.is_public is False


class TestUpdateDashboard:
    @pytest.mark.asyncio
    async def test_update_name(self):
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        dashboard = _make_dashboard(name="Old Name")
        update = DashboardUpdate(name="New Name")
        await update_dashboard(db, dashboard, update)

        assert dashboard.name == "New Name"
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_public_flag(self):
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        dashboard = _make_dashboard(is_public=False)
        update = DashboardUpdate(is_public=True)
        await update_dashboard(db, dashboard, update)

        assert dashboard.is_public is True

    @pytest.mark.asyncio
    async def test_partial_update_leaves_other_fields(self):
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        dashboard = _make_dashboard(name="Keep Me", is_public=False)
        update = DashboardUpdate(description="New desc")
        await update_dashboard(db, dashboard, update)

        assert dashboard.name == "Keep Me"  # unchanged
        assert dashboard.is_public is False  # unchanged


class TestDeleteDashboard:
    @pytest.mark.asyncio
    async def test_delete_calls_db_delete(self):
        db = AsyncMock()
        db.commit = AsyncMock()
        db.delete = AsyncMock()

        dashboard = _make_dashboard()
        await delete_dashboard(db, dashboard)

        db.delete.assert_called_once_with(dashboard)
        db.commit.assert_called_once()


class TestCreateDashboardFromTemplate:
    @pytest.mark.asyncio
    async def test_template_not_found_raises_404(self):
        db = AsyncMock()
        with pytest.raises(HTTPException) as exc_info:
            await create_dashboard_from_template(db, user_id=1, template_name="Nonexistent Template")
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_valid_template_creates_dashboard(self):
        db = AsyncMock()
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        await create_dashboard_from_template(db, user_id=1, template_name="Patient Demographics")

        # db.add should have been called: once for the dashboard + N times for widgets
        assert db.add.call_count >= 1
        # Verify flush and commit were called
        db.flush.assert_called_once()
        db.commit.assert_called_once()
