from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ingestion.fhir_client import FHIR_RESOURCE_TYPES, FhirClient
from app.modules.ingestion.models import IngestionRun, Integration, Quarantine
from app.modules.ingestion.schemas import IntegrationCreate, IntegrationUpdate

logger = structlog.get_logger(__name__)


async def create_integration(
    db: AsyncSession, data: IntegrationCreate, user_id: int
) -> Integration:
    integration = Integration(
        name=data.name,
        type=data.type,
        config_json=data.config_json,
        created_by=user_id,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return integration


async def get_integration(db: AsyncSession, integration_id: int) -> Integration | None:
    result = await db.execute(select(Integration).where(Integration.id == integration_id))
    return result.scalar_one_or_none()


async def list_integrations(db: AsyncSession) -> list[Integration]:
    result = await db.execute(select(Integration).order_by(Integration.created_at.desc()))
    return list(result.scalars().all())


async def update_integration(
    db: AsyncSession, integration_id: int, data: IntegrationUpdate
) -> Integration | None:
    integration = await get_integration(db, integration_id)
    if not integration:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(integration, field, value)
    await db.commit()
    await db.refresh(integration)
    return integration


async def delete_integration(db: AsyncSession, integration_id: int) -> bool:
    integration = await get_integration(db, integration_id)
    if not integration:
        return False
    await db.delete(integration)
    await db.commit()
    return True


async def test_fhir_connection(config: dict) -> bool:
    client = FhirClient(
        server_url=config["server_url"],
        auth_type=config.get("auth_type", "none"),
        bearer_token=config.get("bearer_token"),
        username=config.get("username"),
        password=config.get("password"),
    )
    try:
        return await client.test_connection()
    finally:
        await client.close()


async def get_ingestion_run(db: AsyncSession, run_id: int) -> IngestionRun | None:
    result = await db.execute(select(IngestionRun).where(IngestionRun.id == run_id))
    return result.scalar_one_or_none()


async def list_ingestion_runs(db: AsyncSession, integration_id: int | None = None) -> list[IngestionRun]:
    query = select(IngestionRun).order_by(IngestionRun.started_at.desc())
    if integration_id:
        query = query.where(IngestionRun.integration_id == integration_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def run_fhir_ingestion(
    db: AsyncSession,
    integration: Integration,
    transformation_engine: Any,
) -> IngestionRun:
    config = integration.config_json

    # Retrieve the last successful run to determine the sync cursor
    last_run_result = await db.execute(
        select(IngestionRun)
        .where(
            IngestionRun.integration_id == integration.id,
            IngestionRun.status == "completed",
        )
        .order_by(IngestionRun.completed_at.desc())
        .limit(1)
    )
    last_run = last_run_result.scalar_one_or_none()
    last_cursor = last_run.last_cursor if last_run else None

    ingestion_run = IngestionRun(
        integration_id=integration.id,
        status="running",
    )
    db.add(ingestion_run)
    await db.commit()
    await db.refresh(ingestion_run)

    client = FhirClient(
        server_url=config["server_url"],
        auth_type=config.get("auth_type", "none"),
        bearer_token=config.get("bearer_token"),
        username=config.get("username"),
        password=config.get("password"),
    )

    records_processed = 0
    records_failed = 0
    sync_cursor = datetime.now(timezone.utc).isoformat()

    try:
        await client.connect()
        for resource_type in FHIR_RESOURCE_TYPES:
            async for resource in client.fetch_resources(resource_type, last_updated=last_cursor):
                try:
                    resource_dict = resource.serialize()
                    await transformation_engine.transform_fhir_resource(
                        db, resource_dict, ingestion_run.id
                    )
                    records_processed += 1
                except Exception as e:
                    records_failed += 1
                    quarantine_record = Quarantine(
                        ingestion_run_id=ingestion_run.id,
                        source_data=resource.serialize() if hasattr(resource, "serialize") else {},
                        error_message=str(e),
                        source_resource_type=resource_type,
                        source_resource_id=getattr(resource, "id", None),
                    )
                    db.add(quarantine_record)
                    await db.commit()
                    logger.warning(
                        "fhir_resource_transform_failed",
                        resource_type=resource_type,
                        error=str(e),
                    )

        ingestion_run.status = "completed"
        ingestion_run.last_cursor = sync_cursor
    except Exception as e:
        ingestion_run.status = "failed"
        ingestion_run.error_message = str(e)
        logger.error("fhir_ingestion_failed", integration_id=integration.id, error=str(e))
    finally:
        await client.close()
        ingestion_run.records_processed = records_processed
        ingestion_run.records_failed = records_failed
        ingestion_run.completed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(ingestion_run)

    return ingestion_run


async def list_quarantine_records(
    db: AsyncSession,
    run_id: int | None = None,
    resource_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Quarantine]:
    query = select(Quarantine).order_by(Quarantine.created_at.desc())
    if run_id:
        query = query.where(Quarantine.ingestion_run_id == run_id)
    if resource_type:
        query = query.where(Quarantine.source_resource_type == resource_type)
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_quarantine_stats(db: AsyncSession) -> dict:
    total_result = await db.execute(select(func.count(Quarantine.id)))
    total = total_result.scalar_one()

    by_type_result = await db.execute(
        select(Quarantine.source_resource_type, func.count(Quarantine.id))
        .group_by(Quarantine.source_resource_type)
    )
    by_resource_type = {row[0] or "unknown": row[1] for row in by_type_result.all()}

    recent_result = await db.execute(
        select(Quarantine.error_message)
        .order_by(Quarantine.created_at.desc())
        .limit(5)
    )
    recent_errors = [row[0] for row in recent_result.all()]

    return {
        "total": total,
        "by_resource_type": by_resource_type,
        "recent_errors": recent_errors,
    }
