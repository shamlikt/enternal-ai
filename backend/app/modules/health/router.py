from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import require_role
from app.modules.auth.models import Role, User
from app.modules.health.service import (
    get_application_logs,
    get_ingestion_health,
    get_system_health,
)

router = APIRouter()


@router.get("/", response_model=dict)
async def system_health(db: AsyncSession = Depends(get_db)):
    return await get_system_health(db)


@router.get("/ingestion", response_model=dict)
async def ingestion_health(
    _: User = Depends(require_role(Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    return await get_ingestion_health(db)


@router.get("/logs", response_model=list)
async def application_logs(
    _: User = Depends(require_role(Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    return await get_application_logs(db)
