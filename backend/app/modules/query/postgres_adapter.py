from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.query.adapter import QueryAdapter


class PostgresAdapter(QueryAdapter):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def execute_query(self, sql: str) -> list[dict[str, Any]]:
        result = await self._db.execute(text(sql))
        keys = list(result.keys())
        return [dict(zip(keys, row)) for row in result.fetchall()]

    async def get_tables(self) -> list[str]:
        sql = """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        result = await self._db.execute(text(sql))
        return [row[0] for row in result.fetchall()]

    async def get_columns(self, table_name: str) -> list[dict[str, str]]:
        sql = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = :table_name
            ORDER BY ordinal_position
        """
        result = await self._db.execute(text(sql), {"table_name": table_name})
        return [
            {"name": row[0], "type": row[1], "nullable": row[2]}
            for row in result.fetchall()
        ]
