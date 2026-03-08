from abc import ABC, abstractmethod
from typing import Any


class QueryAdapter(ABC):
    @abstractmethod
    async def execute_query(self, sql: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def get_tables(self) -> list[str]: ...

    @abstractmethod
    async def get_columns(self, table_name: str) -> list[dict[str, str]]: ...
