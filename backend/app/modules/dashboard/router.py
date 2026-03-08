from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.auth.models import Role, User
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
    create_widget,
    delete_dashboard,
    delete_widget,
    execute_widget_data,
    get_dashboard_by_id,
    get_dashboards,
    get_widget_by_id,
    get_widgets,
    update_dashboard,
    update_widget,
)

router = APIRouter()


@router.get("/templates", response_model=list[TemplateDefinition])
async def list_templates(_: User = Depends(get_current_user)):
    return TEMPLATES


@router.post("/templates/{template_name}", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
async def create_from_template(
    template_name: str,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    return await create_dashboard_from_template(db, current_user.id, template_name)


@router.get("/", response_model=list[DashboardResponse])
async def list_dashboards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_dashboards(db, current_user.id)


@router.post("/", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
async def create_new_dashboard(
    data: DashboardCreate,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    return await create_dashboard(db, current_user.id, data)


@router.get("/{dashboard_id}", response_model=DashboardWithWidgets)
async def get_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dashboard = await get_dashboard_by_id(db, dashboard_id, current_user.id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    widgets = await get_widgets(db, dashboard_id)
    return DashboardWithWidgets.model_validate(
        {**dashboard.__dict__, "widgets": widgets}
    )


@router.patch("/{dashboard_id}", response_model=DashboardResponse)
async def update_existing_dashboard(
    dashboard_id: int,
    data: DashboardUpdate,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    dashboard = await get_dashboard_by_id(db, dashboard_id, current_user.id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    return await update_dashboard(db, dashboard, data)


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_dashboard(
    dashboard_id: int,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    dashboard = await get_dashboard_by_id(db, dashboard_id, current_user.id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    await delete_dashboard(db, dashboard)


@router.get("/{dashboard_id}/data", response_model=list[WidgetDataResponse])
async def get_dashboard_data(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dashboard = await get_dashboard_by_id(db, dashboard_id, current_user.id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    widgets = await get_widgets(db, dashboard_id)
    results = []
    for widget in widgets:
        try:
            rows, elapsed_ms = await execute_widget_data(db, widget)
            results.append(WidgetDataResponse(
                widget_id=widget.id, rows=rows, row_count=len(rows), execution_ms=elapsed_ms
            ))
        except Exception:
            results.append(WidgetDataResponse(
                widget_id=widget.id, rows=[], row_count=0, execution_ms=0
            ))
    return results


@router.post("/{dashboard_id}/widgets", response_model=WidgetResponse, status_code=status.HTTP_201_CREATED)
async def add_widget(
    dashboard_id: int,
    data: WidgetCreate,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    dashboard = await get_dashboard_by_id(db, dashboard_id, current_user.id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    return await create_widget(db, dashboard_id, data)


@router.patch("/{dashboard_id}/widgets/{widget_id}", response_model=WidgetResponse)
async def update_existing_widget(
    dashboard_id: int,
    widget_id: int,
    data: WidgetUpdate,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    dashboard = await get_dashboard_by_id(db, dashboard_id, current_user.id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    widget = await get_widget_by_id(db, widget_id, dashboard_id)
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")
    return await update_widget(db, widget, data)


@router.delete("/{dashboard_id}/widgets/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_widget(
    dashboard_id: int,
    widget_id: int,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    dashboard = await get_dashboard_by_id(db, dashboard_id, current_user.id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    widget = await get_widget_by_id(db, widget_id, dashboard_id)
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")
    await delete_widget(db, widget)
