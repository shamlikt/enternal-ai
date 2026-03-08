from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class WidgetCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    widget_type: str = Field(..., pattern=r"^(bar|line|pie|area|donut|kpi|table|funnel)$")
    sql: str = Field(..., min_length=1)
    config_json: Optional[str] = None
    grid_x: int = 0
    grid_y: int = 0
    grid_w: int = 6
    grid_h: int = 4


class WidgetUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    widget_type: Optional[str] = Field(None, pattern=r"^(bar|line|pie|area|donut|kpi|table|funnel)$")
    sql: Optional[str] = Field(None, min_length=1)
    config_json: Optional[str] = None
    grid_x: Optional[int] = None
    grid_y: Optional[int] = None
    grid_w: Optional[int] = None
    grid_h: Optional[int] = None


class WidgetResponse(BaseModel):
    id: int
    dashboard_id: int
    title: str
    widget_type: str
    sql: str
    config_json: Optional[str]
    grid_x: int
    grid_y: int
    grid_w: int
    grid_h: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False


class DashboardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None


class DashboardResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DashboardWithWidgets(DashboardResponse):
    widgets: list[WidgetResponse] = []


class TemplateDefinition(BaseModel):
    name: str
    description: str
    widgets: list[WidgetCreate]


class WidgetDataResponse(BaseModel):
    widget_id: int
    rows: list[dict[str, Any]]
    row_count: int
    execution_ms: int
