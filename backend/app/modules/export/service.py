import csv
import io
import json
from typing import Any

import openpyxl
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.query.models import QueryResult


async def get_result_rows(db: AsyncSession, result_id: int, user_id: int) -> list[dict[str, Any]]:
    result = await db.execute(
        select(QueryResult)
        .join(QueryResult.history_id == QueryResult.history_id)
        .where(QueryResult.id == result_id)
    )
    query_result = result.scalar_one_or_none()
    if not query_result or not query_result.result_json:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")
    return json.loads(query_result.result_json)


def rows_to_csv(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        return b""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def rows_to_xlsx(rows: list[dict[str, Any]]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    if not rows:
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()
    headers = list(rows[0].keys())
    ws.append(headers)
    for row in rows:
        ws.append([row.get(h) for h in headers])
    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()
