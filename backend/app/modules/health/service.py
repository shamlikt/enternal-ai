from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_system_health(db: AsyncSession) -> dict[str, Any]:
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "components": {
            "database": db_status,
            "api": "healthy",
        },
    }


async def get_ingestion_health(db: AsyncSession) -> dict[str, Any]:
    try:
        result = await db.execute(
            text(
                """
                SELECT status, COUNT(*) as count
                FROM ingestion_runs
                GROUP BY status
                ORDER BY status
                """
            )
        )
        rows = result.fetchall()
        stats = {row[0]: row[1] for row in rows}
    except Exception:
        stats = {}

    return {"ingestion_run_stats": stats}
