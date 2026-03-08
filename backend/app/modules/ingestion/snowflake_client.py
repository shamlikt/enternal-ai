"""Snowflake connector wrapper for athenahealth DataView ingestion.

Uses snowflake-connector-python (synchronous) wrapped in asyncio executor
to avoid blocking the event loop.
"""
import asyncio
from typing import Any, Generator

import structlog

logger = structlog.get_logger(__name__)


class SnowflakeClient:
    def __init__(
        self,
        account: str,
        username: str,
        password: str,
        database: str,
        schema_name: str,
        warehouse: str,
        role: str | None = None,
    ):
        self.account = account
        self.username = username
        self.password = password
        self.database = database
        self.schema_name = schema_name
        self.warehouse = warehouse
        self.role = role
        self._conn = None

    def _connect_sync(self):
        import snowflake.connector

        kwargs = {
            "account": self.account,
            "user": self.username,
            "password": self.password,
            "database": self.database,
            "schema": self.schema_name,
            "warehouse": self.warehouse,
        }
        if self.role:
            kwargs["role"] = self.role

        return snowflake.connector.connect(**kwargs)

    async def connect(self) -> None:
        loop = asyncio.get_event_loop()
        self._conn = await loop.run_in_executor(None, self._connect_sync)
        logger.info(
            "snowflake_connected",
            account=self.account,
            database=self.database,
            schema=self.schema_name,
        )

    async def test_connection(self) -> bool:
        try:
            await self.connect()
            await self.execute_query("SELECT CURRENT_VERSION()")
            return True
        except Exception as e:
            logger.warning("snowflake_connection_test_failed", error=str(e))
            return False
        finally:
            await self.close()

    def _execute_sync(self, sql: str, params=None) -> list[dict[str, Any]]:
        cursor = self._conn.cursor(snowflake.connector.DictCursor)
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            cursor.close()

    async def execute_query(self, sql: str, params=None) -> list[dict[str, Any]]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._execute_sync, sql, params)

    def _get_tables_sync(self) -> list[str]:
        import snowflake.connector

        cursor = self._conn.cursor()
        try:
            cursor.execute(f"SHOW TABLES IN SCHEMA {self.database}.{self.schema_name}")
            rows = cursor.fetchall()
            return [row[1] for row in rows]  # column 1 is table name
        finally:
            cursor.close()

    async def get_tables(self) -> list[str]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_tables_sync)

    def _get_columns_sync(self, table_name: str) -> list[dict[str, str]]:
        cursor = self._conn.cursor()
        try:
            cursor.execute(
                f"DESCRIBE TABLE {self.database}.{self.schema_name}.{table_name}"
            )
            rows = cursor.fetchall()
            return [{"name": row[0], "type": row[1]} for row in rows]
        finally:
            cursor.close()

    async def get_columns(self, table_name: str) -> list[dict[str, str]]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_columns_sync, table_name)

    async def fetch_rows_paginated(
        self,
        table_name: str,
        last_updated_col: str | None = None,
        last_cursor: str | None = None,
        page_size: int = 1000,
    ) -> list[dict[str, Any]]:
        sql = f"SELECT * FROM {self.database}.{self.schema_name}.{table_name}"
        if last_updated_col and last_cursor:
            sql += f" WHERE {last_updated_col} > '{last_cursor}'"
        sql += f" LIMIT {page_size}"
        return await self.execute_query(sql)

    async def close(self) -> None:
        if self._conn:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._conn.close)
            self._conn = None
