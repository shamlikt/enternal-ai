import json
import re
import time
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.query.models import QueryHistory, QueryResult, SavedQuery
from app.modules.query.postgres_adapter import PostgresAdapter
from app.modules.query.schemas import SavedQueryCreate, SavedQueryUpdate

# Patterns that indicate a non-SELECT statement
_FORBIDDEN_PATTERNS = re.compile(
    r"^\s*(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|MERGE|EXEC|EXECUTE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def _validate_select_only(sql: str) -> None:
    if _FORBIDDEN_PATTERNS.match(sql):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SELECT queries are allowed",
        )


async def execute_query(
    db: AsyncSession, user_id: int, sql: str
) -> tuple[list[dict[str, Any]], int, int]:
    _validate_select_only(sql)
    adapter = PostgresAdapter(db)
    start = time.monotonic()
    try:
        rows = await adapter.execute_query(sql)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        history = QueryHistory(
            user_id=user_id, sql=sql, row_count=len(rows), execution_ms=elapsed_ms
        )
        db.add(history)
        await db.flush()
        result = QueryResult(history_id=history.id, result_json=json.dumps(rows, default=str))
        db.add(result)
        await db.commit()
        await db.refresh(history)
        return rows, history.id, elapsed_ms
    except HTTPException:
        raise
    except Exception as exc:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        history = QueryHistory(
            user_id=user_id, sql=sql, execution_ms=elapsed_ms, error=str(exc)
        )
        db.add(history)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query execution failed: {exc}",
        )


async def get_query_history(db: AsyncSession, user_id: int) -> list[QueryHistory]:
    result = await db.execute(
        select(QueryHistory).where(QueryHistory.user_id == user_id).order_by(QueryHistory.executed_at.desc())
    )
    return list(result.scalars().all())


async def get_saved_queries(db: AsyncSession, user_id: int) -> list[SavedQuery]:
    result = await db.execute(
        select(SavedQuery).where(SavedQuery.user_id == user_id).order_by(SavedQuery.name)
    )
    return list(result.scalars().all())


async def create_saved_query(
    db: AsyncSession, user_id: int, data: SavedQueryCreate
) -> SavedQuery:
    query = SavedQuery(user_id=user_id, **data.model_dump())
    db.add(query)
    await db.commit()
    await db.refresh(query)
    return query


async def get_saved_query_by_id(db: AsyncSession, query_id: int, user_id: int):
    result = await db.execute(
        select(SavedQuery).where(SavedQuery.id == query_id, SavedQuery.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_saved_query(db: AsyncSession, query: SavedQuery, data: SavedQueryUpdate) -> SavedQuery:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(query, field, value)
    await db.commit()
    await db.refresh(query)
    return query


async def delete_saved_query(db: AsyncSession, query: SavedQuery) -> None:
    await db.delete(query)
    await db.commit()


async def get_tables(db: AsyncSession) -> list[str]:
    adapter = PostgresAdapter(db)
    return await adapter.get_tables()


async def get_columns(db: AsyncSession, table_name: str) -> list[dict]:
    adapter = PostgresAdapter(db)
    return await adapter.get_columns(table_name)
