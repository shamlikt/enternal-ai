import json
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class QueryExecuteRequest(BaseModel):
    sql: str = Field(..., min_length=1)


class QueryExecuteResponse(BaseModel):
    history_id: int
    rows: list[dict[str, Any]]
    row_count: int
    execution_ms: int


class SavedQueryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sql: str = Field(..., min_length=1)


class SavedQueryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    sql: Optional[str] = Field(None, min_length=1)


class SavedQueryResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    sql: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QueryHistoryResponse(BaseModel):
    id: int
    user_id: int
    sql: str
    row_count: Optional[int]
    execution_ms: Optional[int]
    error: Optional[str]
    executed_at: datetime

    model_config = {"from_attributes": True}


class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: str
