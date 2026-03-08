from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import require_role
from app.modules.auth.models import Role, User
from app.modules.audit.service import get_audit_logs
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    details: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime

    model_config = {"from_attributes": True}


router = APIRouter()


@router.get("/", response_model=list[AuditLogResponse])
async def list_audit_logs(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    _: User = Depends(require_role(Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    return await get_audit_logs(db, limit=limit, offset=offset, user_id=user_id, action=action)
