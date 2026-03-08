from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.auth.models import Role, User
from app.modules.export.service import get_result_rows, rows_to_csv, rows_to_xlsx

router = APIRouter()


@router.get("/{result_id}/csv")
async def export_csv(
    result_id: int,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    rows = await get_result_rows(db, result_id, current_user.id)
    content = rows_to_csv(rows)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=result_{result_id}.csv"},
    )


@router.get("/{result_id}/xlsx")
async def export_xlsx(
    result_id: int,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    rows = await get_result_rows(db, result_id, current_user.id)
    content = rows_to_xlsx(rows)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=result_{result_id}.xlsx"},
    )
