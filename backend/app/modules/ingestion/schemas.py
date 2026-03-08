from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class FhirIntegrationConfig(BaseModel):
    server_url: str
    auth_type: str = "none"  # none, basic, client_credentials, bearer
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    bearer_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    fhir_version: Optional[str] = None  # "R4" or "R5" — auto-detected if not set


class SnowflakeIntegrationConfig(BaseModel):
    account: str
    username: str
    password: str
    database: str
    schema_name: str
    warehouse: str
    role: Optional[str] = None


class IntegrationCreate(BaseModel):
    name: str
    type: str  # "fhir" or "snowflake"
    config_json: dict[str, Any]


class IntegrationUpdate(BaseModel):
    name: Optional[str] = None
    config_json: Optional[dict[str, Any]] = None
    status: Optional[str] = None


class IntegrationResponse(BaseModel):
    id: int
    name: str
    type: str
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IngestionRunResponse(BaseModel):
    id: int
    integration_id: int
    status: str
    records_processed: int
    records_failed: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_cursor: Optional[str] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class QuarantineResponse(BaseModel):
    id: int
    ingestion_run_id: int
    error_message: str
    source_resource_type: Optional[str] = None
    source_resource_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class QuarantineStatsResponse(BaseModel):
    total: int
    by_resource_type: dict[str, int]
    recent_errors: list[str]
