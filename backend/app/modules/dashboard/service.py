import time
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dashboard.models import Dashboard, DashboardWidget
from app.modules.dashboard.schemas import (
    DashboardCreate,
    DashboardUpdate,
    TemplateDefinition,
    WidgetCreate,
    WidgetUpdate,
)
from app.modules.query.postgres_adapter import PostgresAdapter
from app.modules.query.service import _validate_select_only

# Pre-built dashboard templates
TEMPLATES: list[TemplateDefinition] = [
    TemplateDefinition(
        name="Patient Demographics",
        description="Overview of patient demographics including sex, race, and age distribution",
        widgets=[
            WidgetCreate(
                title="Sex Distribution",
                widget_type="pie",
                sql="SELECT SEX, COUNT(*) as count FROM DEMOGRAPHIC GROUP BY SEX ORDER BY count DESC",
                grid_x=0, grid_y=0, grid_w=6, grid_h=4,
            ),
            WidgetCreate(
                title="Race Distribution",
                widget_type="bar",
                sql="SELECT RACE, COUNT(*) as count FROM DEMOGRAPHIC GROUP BY RACE ORDER BY count DESC",
                grid_x=6, grid_y=0, grid_w=6, grid_h=4,
            ),
            WidgetCreate(
                title="Hispanic Origin",
                widget_type="donut",
                sql="SELECT HISPANIC, COUNT(*) as count FROM DEMOGRAPHIC GROUP BY HISPANIC",
                grid_x=0, grid_y=4, grid_w=6, grid_h=4,
            ),
            WidgetCreate(
                title="Total Patients",
                widget_type="kpi",
                sql="SELECT COUNT(*) as total_patients FROM DEMOGRAPHIC",
                grid_x=6, grid_y=4, grid_w=6, grid_h=2,
            ),
        ],
    ),
    TemplateDefinition(
        name="Encounter Trends",
        description="Encounter volume and type analysis over time",
        widgets=[
            WidgetCreate(
                title="Encounter Types",
                widget_type="bar",
                sql="SELECT ENC_TYPE, COUNT(*) as count FROM ENCOUNTER GROUP BY ENC_TYPE ORDER BY count DESC",
                grid_x=0, grid_y=0, grid_w=12, grid_h=4,
            ),
            WidgetCreate(
                title="Total Encounters",
                widget_type="kpi",
                sql="SELECT COUNT(*) as total_encounters FROM ENCOUNTER",
                grid_x=0, grid_y=4, grid_w=6, grid_h=2,
            ),
        ],
    ),
    TemplateDefinition(
        name="Diagnosis Distribution",
        description="Top diagnoses and ICD code distribution",
        widgets=[
            WidgetCreate(
                title="Top 20 Diagnoses",
                widget_type="table",
                sql="SELECT DX, DX_TYPE, COUNT(*) as count FROM DIAGNOSIS GROUP BY DX, DX_TYPE ORDER BY count DESC LIMIT 20",
                grid_x=0, grid_y=0, grid_w=12, grid_h=6,
            ),
            WidgetCreate(
                title="Diagnosis Source",
                widget_type="pie",
                sql="SELECT DX_SOURCE, COUNT(*) as count FROM DIAGNOSIS GROUP BY DX_SOURCE",
                grid_x=0, grid_y=6, grid_w=6, grid_h=4,
            ),
        ],
    ),
    TemplateDefinition(
        name="Lab Results Summary",
        description="Lab result trends and abnormal findings",
        widgets=[
            WidgetCreate(
                title="Top Lab Tests by LOINC",
                widget_type="bar",
                sql="SELECT LAB_LOINC, COUNT(*) as count FROM LAB_RESULT_CM WHERE LAB_LOINC IS NOT NULL GROUP BY LAB_LOINC ORDER BY count DESC LIMIT 15",
                grid_x=0, grid_y=0, grid_w=12, grid_h=4,
            ),
            WidgetCreate(
                title="Abnormal Results",
                widget_type="pie",
                sql="SELECT ABN_IND, COUNT(*) as count FROM LAB_RESULT_CM WHERE ABN_IND IS NOT NULL GROUP BY ABN_IND",
                grid_x=0, grid_y=4, grid_w=6, grid_h=4,
            ),
        ],
    ),
    TemplateDefinition(
        name="Prescription Analytics",
        description="Medication prescribing patterns",
        widgets=[
            WidgetCreate(
                title="Top Prescribed Medications (RxNorm)",
                widget_type="bar",
                sql="SELECT RXNORM_CUI, COUNT(*) as count FROM PRESCRIBING WHERE RXNORM_CUI IS NOT NULL GROUP BY RXNORM_CUI ORDER BY count DESC LIMIT 15",
                grid_x=0, grid_y=0, grid_w=12, grid_h=4,
            ),
            WidgetCreate(
                title="Total Prescriptions",
                widget_type="kpi",
                sql="SELECT COUNT(*) as total_prescriptions FROM PRESCRIBING",
                grid_x=0, grid_y=4, grid_w=6, grid_h=2,
            ),
        ],
    ),
]


async def get_dashboards(db: AsyncSession, user_id: int) -> list[Dashboard]:
    result = await db.execute(
        select(Dashboard).where(Dashboard.user_id == user_id).order_by(Dashboard.name)
    )
    return list(result.scalars().all())


async def get_dashboard_by_id(db: AsyncSession, dashboard_id: int, user_id: int) -> Optional[Dashboard]:
    result = await db.execute(
        select(Dashboard).where(Dashboard.id == dashboard_id, Dashboard.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_dashboard(db: AsyncSession, user_id: int, data: DashboardCreate) -> Dashboard:
    dashboard = Dashboard(user_id=user_id, **data.model_dump())
    db.add(dashboard)
    await db.commit()
    await db.refresh(dashboard)
    return dashboard


async def update_dashboard(db: AsyncSession, dashboard: Dashboard, data: DashboardUpdate) -> Dashboard:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(dashboard, field, value)
    await db.commit()
    await db.refresh(dashboard)
    return dashboard


async def delete_dashboard(db: AsyncSession, dashboard: Dashboard) -> None:
    await db.delete(dashboard)
    await db.commit()


async def get_widgets(db: AsyncSession, dashboard_id: int) -> list[DashboardWidget]:
    result = await db.execute(
        select(DashboardWidget).where(DashboardWidget.dashboard_id == dashboard_id)
        .order_by(DashboardWidget.grid_y, DashboardWidget.grid_x)
    )
    return list(result.scalars().all())


async def create_widget(db: AsyncSession, dashboard_id: int, data: WidgetCreate) -> DashboardWidget:
    _validate_select_only(data.sql)
    widget = DashboardWidget(dashboard_id=dashboard_id, **data.model_dump())
    db.add(widget)
    await db.commit()
    await db.refresh(widget)
    return widget


async def update_widget(db: AsyncSession, widget: DashboardWidget, data: WidgetUpdate) -> DashboardWidget:
    updates = data.model_dump(exclude_none=True)
    if "sql" in updates:
        _validate_select_only(updates["sql"])
    for field, value in updates.items():
        setattr(widget, field, value)
    await db.commit()
    await db.refresh(widget)
    return widget


async def delete_widget(db: AsyncSession, widget: DashboardWidget) -> None:
    await db.delete(widget)
    await db.commit()


async def get_widget_by_id(db: AsyncSession, widget_id: int, dashboard_id: int) -> Optional[DashboardWidget]:
    result = await db.execute(
        select(DashboardWidget).where(
            DashboardWidget.id == widget_id, DashboardWidget.dashboard_id == dashboard_id
        )
    )
    return result.scalar_one_or_none()


async def execute_widget_data(
    db: AsyncSession, widget: DashboardWidget
) -> tuple[list[dict[str, Any]], int]:
    adapter = PostgresAdapter(db)
    start = time.monotonic()
    rows = await adapter.execute_query(widget.sql)
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return rows, elapsed_ms


async def create_dashboard_from_template(
    db: AsyncSession, user_id: int, template_name: str
) -> Dashboard:
    template = next((t for t in TEMPLATES if t.name == template_name), None)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    dashboard = Dashboard(user_id=user_id, name=template.name, description=template.description)
    db.add(dashboard)
    await db.flush()
    for widget_data in template.widgets:
        widget = DashboardWidget(dashboard_id=dashboard.id, **widget_data.model_dump())
        db.add(widget)
    await db.commit()
    await db.refresh(dashboard)
    return dashboard
