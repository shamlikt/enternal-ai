import time
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_start_time = time.time()


async def get_system_health(db: AsyncSession) -> dict[str, Any]:
    # Database check with latency measurement
    try:
        t0 = time.time()
        await db.execute(text("SELECT 1"))
        latency_ms = round((time.time() - t0) * 1000, 1)
        db_status = "connected"
    except Exception:
        latency_ms = None
        db_status = "error"

    # Ingestion stats
    ingestion_info: dict[str, Any] = {"error_count_24h": 0}
    try:
        result = await db.execute(
            text(
                """
                SELECT status, started_at
                FROM ingestion_runs
                ORDER BY started_at DESC
                LIMIT 1
                """
            )
        )
        row = result.fetchone()
        if row:
            ingestion_info["status"] = row[0]
            ingestion_info["last_run"] = row[1].isoformat() if row[1] else None

        err_result = await db.execute(
            text(
                """
                SELECT COUNT(*)
                FROM ingestion_runs
                WHERE status = 'failed'
                  AND started_at >= NOW() - INTERVAL '24 hours'
                """
            )
        )
        err_row = err_result.fetchone()
        if err_row:
            ingestion_info["error_count_24h"] = err_row[0]
    except Exception:
        pass

    overall = "healthy" if db_status == "connected" else "degraded"

    return {
        "status": overall,
        "database": {
            "status": db_status,
            "latency_ms": latency_ms,
        },
        "ingestion": ingestion_info,
        "api": {
            "uptime_seconds": round(time.time() - _start_time),
            "version": "0.1.0",
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


async def get_application_logs(db: AsyncSession) -> list[dict[str, Any]]:
    """Return recent structured log entries from the audit_log table as application logs."""
    try:
        result = await db.execute(
            text(
                """
                SELECT timestamp, action, resource_type,
                       COALESCE(details::text, '') as details
                FROM audit_log
                ORDER BY timestamp DESC
                LIMIT 200
                """
            )
        )
        rows = result.fetchall()
        logs = []
        for row in rows:
            logs.append(
                {
                    "timestamp": row[0].isoformat() if row[0] else "",
                    "level": "INFO",
                    "logger": row[2] or "system",
                    "message": row[1] or "",
                    "event": row[1] or "",
                }
            )
        return logs
    except Exception:
        return []
