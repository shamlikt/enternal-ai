from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_role
from app.modules.auth.models import Role, User
from app.modules.query.schemas import (
    ColumnInfo,
    QueryExecuteRequest,
    QueryExecuteResponse,
    QueryHistoryResponse,
    SavedQueryCreate,
    SavedQueryResponse,
    SavedQueryUpdate,
)
from app.modules.query.service import (
    create_saved_query,
    delete_saved_query,
    execute_query,
    get_columns,
    get_query_history,
    get_saved_queries,
    get_saved_query_by_id,
    get_tables,
    update_saved_query,
)

router = APIRouter()


@router.post("/execute", response_model=QueryExecuteResponse)
async def run_query(
    request: QueryExecuteRequest,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    rows, history_id, elapsed_ms = await execute_query(db, current_user.id, request.sql)
    return QueryExecuteResponse(
        history_id=history_id,
        rows=rows,
        row_count=len(rows),
        execution_ms=elapsed_ms,
    )


@router.get("/history", response_model=list[QueryHistoryResponse])
async def list_history(
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    return await get_query_history(db, current_user.id)


@router.get("/saved", response_model=list[SavedQueryResponse])
async def list_saved(
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    return await get_saved_queries(db, current_user.id)


@router.post("/saved", response_model=SavedQueryResponse, status_code=status.HTTP_201_CREATED)
async def create_saved(
    data: SavedQueryCreate,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    return await create_saved_query(db, current_user.id, data)


@router.patch("/saved/{query_id}", response_model=SavedQueryResponse)
async def update_saved(
    query_id: int,
    data: SavedQueryUpdate,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    query = await get_saved_query_by_id(db, query_id, current_user.id)
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found")
    return await update_saved_query(db, query, data)


@router.delete("/saved/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved(
    query_id: int,
    current_user: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    query = await get_saved_query_by_id(db, query_id, current_user.id)
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found")
    await delete_saved_query(db, query)


schema_router = APIRouter()


@schema_router.get("/tables", response_model=list[str])
async def list_tables(
    _: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    return await get_tables(db)


@schema_router.get("/tables/{table_name}/columns", response_model=list[ColumnInfo])
async def list_columns(
    table_name: str,
    _: User = Depends(require_role(Role.ADMIN, Role.ANALYST)),
    db: AsyncSession = Depends(get_db),
):
    return await get_columns(db, table_name)
